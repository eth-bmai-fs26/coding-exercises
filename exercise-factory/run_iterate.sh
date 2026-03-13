#!/bin/bash
# ============================================================================
# Exercise Factory — Iterate Loop (Test → Critique → Improve)
#
# Fully automated: no interactive prompts, no Gemini API key needed.
# Uses claude CLI for the critic+improver step (one LLM call per iteration).
# The test step is pure Python — no LLM needed.
#
# Usage:
#   ./run_iterate.sh                         # Auto-detect exercise
#   ./run_iterate.sh the_supply_line         # Specify exercise name
#   ./run_iterate.sh the_supply_line 3       # Specify max iterations
#
# Prerequisites:
#   - claude CLI installed and authenticated
#   - Exercise already built (package + solutions notebook exist)
# ============================================================================

set -euo pipefail

FACTORY_DIR="$(cd "$(dirname "$0")" && pwd)"
EXERCISES_DIR="$(dirname "$FACTORY_DIR")"
ARTIFACTS_DIR="$FACTORY_DIR/artifacts"
PROMPTS_DIR="$FACTORY_DIR/prompts"

# Parse arguments
EXERCISE_NAME="${1:-}"
MAX_ITERATIONS="${2:-5}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_step() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}\n"; }
log_ok()   { echo -e "${GREEN}✓ $1${NC}"; }
log_warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
log_err()  { echo -e "${RED}✗ $1${NC}"; }

# ── Auto-detect exercise ─────────────────────────────────────────────────

if [ -z "$EXERCISE_NAME" ]; then
    SKIP_DIRS="agentic_ai_hero|the_support_desk|exercise-factory|interpretability|notes_rag|pro_forma"
    EXERCISE_NAME=$(ls -dt "$EXERCISES_DIR"/*/ 2>/dev/null \
        | grep -v -E "($SKIP_DIRS)" \
        | head -1 \
        | xargs basename 2>/dev/null || echo "")

    if [ -z "$EXERCISE_NAME" ]; then
        log_err "No exercise found. Pass the exercise name as first argument."
        exit 1
    fi
fi

EXERCISE_DIR="$EXERCISES_DIR/$EXERCISE_NAME"
# The Python package name may differ from directory name (e.g. the_supply_line -> supply_line)
# Auto-detect: find the Python package inside the exercise directory
PKG_NAME=$(echo "$EXERCISE_NAME" | tr '-' '_')

if [ ! -d "$EXERCISE_DIR/$PKG_NAME" ]; then
    # Try without "the_" prefix
    PKG_NAME_ALT=$(echo "$PKG_NAME" | sed 's/^the_//')
    if [ -d "$EXERCISE_DIR/$PKG_NAME_ALT" ]; then
        PKG_NAME="$PKG_NAME_ALT"
    else
        # Last resort: find any Python package (directory with __init__.py)
        PKG_NAME=$(find "$EXERCISE_DIR" -maxdepth 2 -name "__init__.py" -exec dirname {} \; | head -1 | xargs basename 2>/dev/null || echo "")
        if [ -z "$PKG_NAME" ] || [ ! -d "$EXERCISE_DIR/$PKG_NAME" ]; then
            log_err "Exercise package not found in $EXERCISE_DIR"
            exit 1
        fi
    fi
fi

SOLUTIONS_NB="$EXERCISE_DIR/${EXERCISE_NAME}_solutions.ipynb"
if [ ! -f "$SOLUTIONS_NB" ]; then
    log_err "Solutions notebook not found at $SOLUTIONS_NB"
    exit 1
fi

log_step "Iterate Loop — Exercise: $EXERCISE_NAME (max $MAX_ITERATIONS iterations)"

# ── Preflight: check claude CLI ──────────────────────────────────────────

if ! command -v claude &> /dev/null; then
    log_err "claude CLI not found. Install it first."
    exit 1
fi

# Cannot run nested claude sessions
if [ -n "${CLAUDECODE:-}" ]; then
    log_err "Cannot run inside a Claude Code session (nested sessions crash)."
    log_err "Run this script from a regular terminal."
    exit 1
fi

# ── Load .env if it exists (for GEMINI_API_KEY) ─────────────────────────

ENV_FILE="$EXERCISES_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    set -a  # auto-export all variables
    source "$ENV_FILE"
    set +a
    log_ok "Loaded .env (GEMINI_API_KEY=${GEMINI_API_KEY:+set}${GEMINI_API_KEY:-NOT SET})"
else
    log_warn "No .env file found at $ENV_FILE"
    log_warn "LLM solution test will be skipped unless GEMINI_API_KEY is set"
fi

if [ -z "${GEMINI_API_KEY:-}" ]; then
    log_warn "GEMINI_API_KEY not set — LLM solution will NOT be tested"
    TEST_LLM=false
else
    TEST_LLM=true
fi

mkdir -p "$ARTIFACTS_DIR"

# ============================================================================
# Step 1: TESTER — Pure Python, no LLM needed
# ============================================================================

run_test() {
    log_step "TEST — Running rule-based solution"

    cd "$EXERCISE_DIR"

    python3 << 'PYTEST'
import sys, json, os, importlib, re

sys.path.insert(0, '.')

exercise_dir = os.environ.get('EXERCISE_DIR', '.')
exercise_name = os.environ.get('EXERCISE_NAME', '')
pkg_name = os.environ.get('PKG_NAME', '')
artifacts_dir = os.environ.get('ARTIFACTS_DIR', '.')
solutions_nb = os.environ.get('SOLUTIONS_NB', '')

# ── Import the exercise package ──
pkg = importlib.import_module(pkg_name)
create_game = getattr(pkg, 'create_game')
run_agent = getattr(pkg, 'run_agent', None)
parse_action = getattr(pkg, 'parse_action', None)

# ── Extract think_rule_based from solutions notebook ──
with open(solutions_nb) as f:
    nb = json.load(f)

# Find the cell with think_rule_based definition
rb_code = None
for cell in nb['cells']:
    if cell['cell_type'] != 'code':
        continue
    source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
    if 'def think_rule_based(' in source and 'NotImplementedError' not in source:
        rb_code = source
        break

if not rb_code:
    print("ERROR: Could not find think_rule_based in solutions notebook")
    sys.exit(1)

# Execute it to define the function
exec_globals = {}
# Import everything the function might need
exec(f"from {pkg_name} import *", exec_globals)
exec(f"from {pkg_name}.game import *", exec_globals)
exec(f"from {pkg_name}.data import *", exec_globals)
exec(f"from {pkg_name}.agent import *", exec_globals)
exec(rb_code, exec_globals)

think_fn = exec_globals['think_rule_based']

# ── Run the game ──
agent, world, tools = create_game()
if run_agent:
    result = run_agent(think_fn, agent, world, tools, max_turns=100)
else:
    # Fallback: use play_rule_based
    play_rb = getattr(pkg, 'play_rule_based')
    result = play_rb(think_fn, max_turns=100, show_display=False)

# ── Read and copy game log ──
import glob, shutil

game_log_data = None
log_file = result.get('log_file', '')
# log_file is a relative path; resolve it against cwd (which is exercise_dir)
if log_file and os.path.exists(log_file):
    with open(log_file) as f:
        game_log_data = json.load(f)
    shutil.copy2(log_file, os.path.join(artifacts_dir, 'game_log.json'))
    os.remove(log_file)

# ── Generate test report ──
report = []
report.append("# Test Report\n")
report.append("## Result")
report.append(f"- **Won:** {'yes' if result.get('won') else 'no'}")
report.append(f"- **Resolved:** {result.get('resolved', '?')}")

# Handle different score field names
quality = result.get('quality', result.get('csat', '?'))
report.append(f"- **Quality Score:** {quality}%")
report.append(f"- **Tokens Remaining:** {result.get('tokens', '?')}")
report.append(f"- **Turns Used:** {result.get('turns', '?')}/100")
report.append("")

# Task resolution order from game log
if game_log_data and 'turns' in game_log_data:
    report.append("## Task Resolution Order")
    for i, turn in enumerate(game_log_data['turns']):
        action = turn.get('action', '')
        if 'close_order' in action or 'resolve_ticket' in action or 'acknowledge_alert' in action:
            if turn.get('success', False):
                report.append(f"- Turn {turn['turn']}: {action} | resolved={turn.get('resolved','?')} quality={turn.get('quality','?')}%")
    report.append("")

    # Boss fight milestones
    report.append("## Boss Fight Milestones")
    boss_keywords = ['prepare_launch', 'authorize_launch', 'prepare_compliance',
                     'submit_compliance', 'prepare_briefing']
    for turn in game_log_data['turns']:
        action = turn.get('action', '')
        if any(kw in action for kw in boss_keywords):
            status = "OK" if turn.get('success') else "FAIL"
            report.append(f"- Turn {turn['turn']}: {action} → {status}")
    report.append("")

    # Wasted turns / failures
    report.append("## Failed Actions")
    for turn in game_log_data['turns']:
        if not turn.get('success', True) and 'event' not in turn:
            report.append(f"- Turn {turn['turn']}: {turn.get('action','')} → {turn.get('result','')[:100]}")
    report.append("")

    # Token events
    report.append("## Token Events")
    prev_tokens = 3
    for turn in game_log_data['turns']:
        tokens = turn.get('tokens', prev_tokens)
        if tokens != prev_tokens:
            report.append(f"- Turn {turn['turn']}: tokens {prev_tokens} → {tokens} ({turn.get('action','')})")
            prev_tokens = tokens
    if prev_tokens == 3:
        report.append("- No token changes (all 3 retained)")
    report.append("")

    # Think errors
    report.append("## Think Errors")
    errors = [t for t in game_log_data['turns'] if 'think_error' in t]
    if errors:
        for t in errors:
            report.append(f"- Turn {t['turn']}: {t['think_error']}")
    else:
        report.append("- None")
    report.append("")

# Edge case tests
report.append("## Edge Case Tests")
report.append("(Automated — checking game engine guardrails)")

# Test: boss without prerequisites
agent2, world2, tools2 = create_game()
from io import StringIO
# Try to prepare launch briefing immediately
r = tools2.execute('prepare_launch_briefing', {})
report.append(f"- Boss without prereqs: {'BLOCKED (correct)' if not r.success else 'ALLOWED (BUG!)'}")

# Try to authorize launch without briefing
r = tools2.execute('authorize_launch', {'order_id': 'T-001'})
report.append(f"- Authorize without briefing: {'BLOCKED (correct)' if not r.success else 'ALLOWED (BUG!)'}")

# Try blacklisted supplier
r = tools2.execute('place_order', {'supplier': 'QuickShip Ltd'})
report.append(f"- Blacklisted supplier: {'BLOCKED+PENALTY (correct)' if not r.success else 'ALLOWED (BUG!)'}")

report.append("")

# ── LLM solution test (if GEMINI_API_KEY is available) ──
gemini_key = os.environ.get('GEMINI_API_KEY', '')
if gemini_key and gemini_key != 'paste-your-key-here':
    report.append("## LLM Solution Test")
    try:
        # Ensure google-genai is installed
        try:
            from google import genai
        except ImportError:
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'google-genai', '--quiet'])
            from google import genai
        # Extract think_llm and all its helpers from solutions notebook
        llm_code_cells = []
        for cell in nb['cells']:
            if cell['cell_type'] != 'code':
                continue
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            # Skip setup cells, interactive cells, and run cells
            if 'pip install' in source or 'play_interactive' in source:
                continue
            if 'play_with_llm(' in source or 'play_rule_based(' in source:
                continue
            if 'files.download' in source:
                continue
            # Include cells that define LLM-related functions
            if any(kw in source for kw in ['def think_llm', 'def _auto_handle',
                    'def _build_memory', 'def _pick_next_order_llm',
                    'def _switch_away_from', 'SYSTEM_PROMPT', 'VALID_TEMPLATES',
                    'genai.Client', 'client = genai']):
                llm_code_cells.append(source)

        if not llm_code_cells:
            report.append("- Could not extract think_llm from solutions notebook")
        else:
            # Build execution environment
            llm_globals = {}
            exec(f"from {pkg_name} import *", llm_globals)
            exec(f"from {pkg_name}.game import *", llm_globals)
            exec(f"from {pkg_name}.data import *", llm_globals)
            exec(f"from {pkg_name}.agent import *", llm_globals)
            exec("import os", llm_globals)
            llm_globals['os'] = os

            # Execute all LLM cells in order
            for cell_code in llm_code_cells:
                exec(cell_code, llm_globals)

            think_llm_fn = llm_globals.get('think_llm')
            if not think_llm_fn:
                report.append("- think_llm function not found after executing cells")
            else:
                # Run the LLM game with progress output
                print("Running LLM solution (up to 100 turns with Gemini API calls)...")
                agent3, world3, tools3 = create_game()

                # Wrap think_llm to show progress every 10 turns
                _llm_turn_count = [0]
                _original_think = think_llm_fn
                def _think_with_progress(a, w, h):
                    _llm_turn_count[0] += 1
                    t = _llm_turn_count[0]
                    if t % 10 == 0 or t == 1:
                        print(f"  Turn {t}/100 | Resolved: {a.resolved_count} | Quality: {a.quality_score:.0f}% | Tokens: {a.operations_tokens}", flush=True)
                    return _original_think(a, w, h)

                llm_result = run_agent(_think_with_progress, agent3, world3, tools3, max_turns=100)
                print(f"  Done! Won: {llm_result.get('won')} | Resolved: {llm_result.get('resolved')} | Quality: {llm_result.get('quality')}%")

                # Save LLM game log
                llm_log_file = llm_result.get('log_file', '')
                if llm_log_file and os.path.exists(llm_log_file):
                    shutil.copy2(llm_log_file, os.path.join(artifacts_dir, 'game_log_llm.json'))
                    os.remove(llm_log_file)

                report.append(f"- **Won:** {'yes' if llm_result.get('won') else 'no'}")
                llm_quality = llm_result.get('quality', llm_result.get('csat', '?'))
                report.append(f"- **Resolved:** {llm_result.get('resolved', '?')}")
                report.append(f"- **Quality Score:** {llm_quality}%")
                report.append(f"- **Tokens Remaining:** {llm_result.get('tokens', '?')}")
                report.append(f"- **Turns Used:** {llm_result.get('turns', '?')}/100")

                # ── Deep LLM analysis (always, not just on failure) ──
                report.append("")
                report.append("### LLM Detailed Analysis")

                # Load the LLM game log for analysis
                llm_log_path = os.path.join(artifacts_dir, 'game_log_llm.json')
                llm_log_data = None
                if os.path.exists(llm_log_path):
                    with open(llm_log_path) as f:
                        llm_log_data = json.load(f)

                if llm_log_data and 'turns' in llm_log_data:
                    turns = llm_log_data['turns']

                    # 1. Token loss events (with context)
                    report.append("")
                    report.append("#### Token Loss Events")
                    prev_tokens = 3
                    token_losses = []
                    for t in turns:
                        tokens = t.get('tokens', prev_tokens)
                        if tokens < prev_tokens:
                            token_losses.append(t)
                            report.append(f"- **Turn {t['turn']}**: {prev_tokens} → {tokens} tokens")
                            report.append(f"  - Action: `{t.get('action', '')}`")
                            report.append(f"  - Result: {t.get('result', '')[:200]}")
                            # Show 2 turns before for context
                            turn_num = t['turn']
                            context_turns = [ct for ct in turns if turn_num - 3 <= ct.get('turn', -1) < turn_num]
                            if context_turns:
                                report.append(f"  - Context (preceding turns):")
                                for ct in context_turns:
                                    report.append(f"    - Turn {ct['turn']}: `{ct.get('action', '')[:80]}`")
                        prev_tokens = tokens
                    if not token_losses:
                        report.append("- No tokens lost")

                    # 2. Repeated/stuck action detection
                    report.append("")
                    report.append("#### Stuck/Loop Detection")
                    action_runs = []
                    for t in turns:
                        action_runs.append(t.get('action', ''))

                    # Find runs of the same action
                    streak_action = None
                    streak_start = 0
                    streak_len = 0
                    worst_streaks = []
                    for i, a in enumerate(action_runs):
                        # Normalize: treat check_orders() and check_stats() as "idle"
                        norm = 'IDLE' if a in ('check_orders()', 'check_stats()') else a
                        if norm == streak_action:
                            streak_len += 1
                        else:
                            if streak_len >= 3:
                                worst_streaks.append((streak_action, streak_start, streak_len))
                            streak_action = norm
                            streak_start = i
                            streak_len = 1
                    if streak_len >= 3:
                        worst_streaks.append((streak_action, streak_start, streak_len))

                    if worst_streaks:
                        for action, start, length in worst_streaks:
                            report.append(f"- **STUCK**: `{action}` repeated {length} times (turns {start}-{start+length-1})")
                            report.append(f"  - This wasted {length} turns. The autopilot or guardrails should intercept this pattern.")
                    else:
                        report.append("- No stuck loops detected")

                    # 3. Escalation analysis
                    report.append("")
                    report.append("#### Escalation Analysis")
                    if llm_log_data.get('notes'):
                        for note in llm_log_data['notes']:
                            if 'WRONG' in note or 'UNNECESSARY' in note:
                                report.append(f"- **BAD ESCALATION**: {note}")
                                report.append(f"  - Fix: The autopilot should handle this order's escalation deterministically, not defer to the LLM.")
                            elif 'correct' in note.lower():
                                report.append(f"- OK: {note}")
                    else:
                        report.append("- No escalation events")

                    # 4. Unresolved orders analysis
                    report.append("")
                    report.append("#### Unresolved Orders")
                    resolved_ids = set()
                    for t in turns:
                        action = t.get('action', '')
                        if ('close_order' in action or 'acknowledge_alert' in action) and t.get('success'):
                            m = re.search(r'(?:order_id|alert_id)="(T-\d+)"', action)
                            if m:
                                resolved_ids.add(m.group(1))

                    all_seen = set()
                    for t in turns:
                        for m in re.finditer(r'T-\d+', t.get('action', '') + ' ' + t.get('result', '')):
                            all_seen.add(m.group())

                    unresolved = sorted(all_seen - resolved_ids)
                    if unresolved:
                        report.append(f"- Resolved: {sorted(resolved_ids)}")
                        report.append(f"- **NOT resolved**: {unresolved}")
                        report.append(f"  - The LLM solution must resolve at least 15 orders to win.")
                        report.append(f"  - Check if these orders were ever opened (read_order called).")

                        # Check which unresolved orders were actually opened
                        for oid in unresolved:
                            opened = any(f'order_id="{oid}"' in t.get('action', '') and 'read_order' in t.get('action', '') for t in turns)
                            if not opened:
                                report.append(f"  - **{oid} was NEVER opened** — the autopilot/LLM never called read_order for it")
                            else:
                                # Find what happened after opening
                                actions_on = [t for t in turns if oid in t.get('action', '')]
                                report.append(f"  - {oid} was opened but not closed. Actions taken: {[t.get('action','')[:60] for t in actions_on[:5]]}")
                    else:
                        report.append("- All orders resolved")

                    # 5. Turn efficiency
                    report.append("")
                    report.append("#### Turn Efficiency")
                    idle_turns = sum(1 for a in action_runs if a in ('check_orders()', 'check_stats()'))
                    failed_turns = sum(1 for t in turns if not t.get('success', True) and 'event' not in t)
                    useful_turns = len(turns) - idle_turns - failed_turns
                    report.append(f"- Total turns: {len(turns)}")
                    report.append(f"- Useful turns: {useful_turns}")
                    report.append(f"- Idle turns (check_orders/check_stats): {idle_turns}")
                    report.append(f"- Failed turns: {failed_turns}")
                    if idle_turns > 10:
                        report.append(f"  - **{idle_turns} idle turns is excessive.** The guardrail should force read_order when check_orders is called with orders in queue.")

                # Summary for the critic
                if not llm_result.get('won'):
                    report.append("")
                    report.append("### LLM Fix Priority")
                    if llm_result.get('tokens', 3) <= 0:
                        report.append("1. **CRITICAL**: Lost all tokens. Guardrails must block the bad escalations/actions that caused token loss.")
                    elif llm_result.get('tokens', 3) < 3:
                        report.append(f"1. **HIGH**: Lost {3 - llm_result.get('tokens', 3)} token(s). Add autopilot handling for the orders that caused wrong escalations.")
                    resolved = llm_result.get('resolved', 0)
                    if resolved < 15:
                        report.append(f"2. **HIGH**: Only {resolved}/15 resolved. Orders not being opened or getting stuck. Fix autopilot to handle more order types deterministically.")
                    if idle_turns > 10:
                        report.append(f"3. **HIGH**: {idle_turns} idle turns. Add guardrail: if LLM outputs check_orders/check_stats and queue is non-empty, force read_order on next unread order.")

    except Exception as e:
        report.append(f"- LLM test error: {e}")

    report.append("")
else:
    report.append("## LLM Solution Test")
    report.append("- SKIPPED (GEMINI_API_KEY not set)")
    report.append("")

report_text = '\n'.join(report)
with open(os.path.join(artifacts_dir, 'test_report.md'), 'w') as f:
    f.write(report_text)

print(report_text)
print(f"\nTest report saved to {artifacts_dir}/test_report.md")
PYTEST
}

# ============================================================================
# Step 2: CRITIC + IMPROVER — Single claude call per iteration
# ============================================================================

run_critique_and_improve() {
    local iteration=$1
    log_step "CRITIQUE + IMPROVE (iteration $iteration)"

    # Combine critic and improver into one prompt
    # Build the prompt
    CRITIC_PROMPT=$(cat "$PROMPTS_DIR/critic.md")
    IMPROVER_PROMPT=$(cat "$PROMPTS_DIR/improver.md")
    CONCEPT_LINE=""
    if [ -f "$ARTIFACTS_DIR/concept.md" ]; then
        CONCEPT_LINE="- Concept: $ARTIFACTS_DIR/concept.md"
    fi

    cat > "$ARTIFACTS_DIR/_iterate_prompt.txt" << PROMPT_EOF
You are reviewing and improving an agentic AI coding exercise.

## Phase 1: CRITIQUE

Read ALL of these files carefully — especially the full raw game logs:

- Test report (summary): $ARTIFACTS_DIR/test_report.md
- **FULL game log (rule-based)**: $ARTIFACTS_DIR/game_log.json — Read this entire file. Every turn matters.
$([ -f "$ARTIFACTS_DIR/game_log_llm.json" ] && echo "- **FULL game log (LLM)**: $ARTIFACTS_DIR/game_log_llm.json — Read this ENTIRE file turn by turn. This is the most important file. Trace through every turn to understand exactly where and why the LLM agent fails. Look for: wrong escalations, stuck loops, orders never opened, wasted turns, token losses.")
$CONCEPT_LINE

CRITICAL: The LLM solution is the one students will build as their final solution.
If it fails, you MUST understand exactly why by reading the raw log turn by turn.
Don't just look at the summary — read the actual sequence of actions and results.

For every problem you find, trace it back to the root cause in the code:
- Is it a missing autopilot case? (order type not handled deterministically)
- Is it a missing guardrail? (LLM outputs a bad action that should be intercepted)
- Is it a prompt issue? (LLM doesn't have enough info to make the right decision)
- Is it a game engine bug? (scoring, ordering, or gating logic is wrong)

Analyze using this framework:

$CRITIC_PROMPT

## Phase 2: IMPROVE (if needed)

If there are Critical or High priority issues, fix them:

$IMPROVER_PROMPT

The exercise is at: $EXERCISE_DIR
The Python package is: $EXERCISE_DIR/$PKG_NAME/
The solutions notebook is: $SOLUTIONS_NB
The student notebook is: $EXERCISE_DIR/${EXERCISE_NAME}.ipynb

## Instructions

1. Read the test report AND the full raw game logs (both rule-based and LLM)
2. For the LLM log: trace through every turn. Identify the exact turns where things go wrong.
3. Read the exercise source files (especially tools.py and the solutions notebook)
4. Write your review to $ARTIFACTS_DIR/issues.md — include specific turn numbers and root causes
5. If there are Critical/High issues: implement the fixes in the source code
6. After fixing, verify the rule-based solution still wins by running:
   cd $EXERCISE_DIR && python3 -c "import sys; sys.path.insert(0, '.'); from ${PKG_NAME} import *; from ${PKG_NAME}.data import *; result = play_rule_based(lambda a,w,h: 'ACTION: check_orders()', max_turns=1, show_display=False); print('engine OK')"
   Then read the solutions notebook, extract the think_rule_based, and run it.
7. Write improvement log to $ARTIFACTS_DIR/improvement_log_iter${iteration}.md
8. If no issues found: write 'Verdict: PASS' and 'NO_ISSUES' in issues.md
PROMPT_EOF

    claude -p "$(cat "$ARTIFACTS_DIR/_iterate_prompt.txt")" \
        --allowedTools "Read,Write,Edit,Bash,Glob,Grep" \
        --permission-mode "bypassPermissions" \
        --add-dir "$EXERCISES_DIR" \
        2>&1 | tail -30

    rm -f "$ARTIFACTS_DIR/_iterate_prompt.txt"

    log_ok "Critique + improve complete for iteration $iteration"
}

# ============================================================================
# Main Loop
# ============================================================================

export EXERCISE_DIR EXERCISE_NAME PKG_NAME ARTIFACTS_DIR SOLUTIONS_NB GEMINI_API_KEY TEST_LLM

for iteration in $(seq 1 "$MAX_ITERATIONS"); do
    log_step "Iteration $iteration/$MAX_ITERATIONS"

    # ── Test ──
    run_test

    if [ ! -f "$ARTIFACTS_DIR/test_report.md" ]; then
        log_err "Test report not generated — aborting"
        exit 1
    fi

    # Check if test already passes perfectly
    if grep -q "Won:.*yes" "$ARTIFACTS_DIR/test_report.md" 2>/dev/null; then
        # Extract metrics (macOS-compatible — no grep -P)
        QUALITY=$(python3 -c "
import re
text = open('$ARTIFACTS_DIR/test_report.md').read()
m = re.search(r'Quality Score.*?([\d.]+)%', text)
print(m.group(1) if m else '0')
")
        TOKENS=$(python3 -c "
import re
text = open('$ARTIFACTS_DIR/test_report.md').read()
m = re.search(r'Tokens Remaining.*?(\d+)', text)
print(m.group(1) if m else '0')
")

        log_ok "Rule-based solution wins! Quality: ${QUALITY}%, Tokens: ${TOKENS}"

        if [ "$iteration" -eq 1 ]; then
            log_ok "Passing on first iteration — running critic once for polish feedback"
        fi
    fi

    # ── Critique + Improve ──
    run_critique_and_improve "$iteration"

    if [ ! -f "$ARTIFACTS_DIR/issues.md" ]; then
        log_warn "Issues file not generated — skipping to next iteration"
        continue
    fi

    # Check if we're done
    if grep -q "NO_ISSUES" "$ARTIFACTS_DIR/issues.md" 2>/dev/null; then
        log_ok "No issues found! Exercise is ready."
        break
    fi

    if grep -q "Verdict: PASS" "$ARTIFACTS_DIR/issues.md" 2>/dev/null; then
        log_ok "Exercise passes review!"
        # In automated mode, we stop when critic says PASS
        break
    fi

    log_warn "Issues found — will re-test in next iteration"
done

# ── Summary ──────────────────────────────────────────────────────────────

log_step "Pipeline Complete"

echo "Artifacts:"
ls -la "$ARTIFACTS_DIR/" 2>/dev/null

echo ""
echo "Exercise: $EXERCISE_DIR"
echo ""
echo "Next steps:"
echo "  1. Review artifacts/issues.md for any remaining suggestions"
echo "  2. Open the student notebook in Colab and play it"
echo "  3. Try implementing the solution without looking at solutions"
echo "  4. If it feels right, ship it!"
