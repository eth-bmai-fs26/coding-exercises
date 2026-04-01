#!/bin/bash
# ============================================================================
# Exercise Factory Pipeline
#
# Automates the design → build → test → critique → improve loop for creating
# agentic AI coding exercises.
#
# Usage:
#   ./run_pipeline.sh                    # Full pipeline (design + build + iterate)
#   ./run_pipeline.sh --skip-design      # Skip design, use existing concept.md
#   ./run_pipeline.sh --iterate-only     # Only run test → critique → improve loop
#   ./run_pipeline.sh --max-iterations 3 # Limit improvement iterations (default: 5)
#
# Prerequisites:
#   - claude CLI installed and authenticated
#   - inputs/domain_choice.txt exists with the chosen domain
#   - inputs/audience.xlsx exists with participant profiles
#   - inputs/hero_quest_pattern.md exists with the exercise pattern
# ============================================================================

set -euo pipefail

FACTORY_DIR="$(cd "$(dirname "$0")" && pwd)"
EXERCISES_DIR="$(dirname "$FACTORY_DIR")"
PROMPTS_DIR="$FACTORY_DIR/prompts"
INPUTS_DIR="$FACTORY_DIR/inputs"
ARTIFACTS_DIR="$FACTORY_DIR/artifacts"
MAX_ITERATIONS=5
SKIP_DESIGN=false
ITERATE_ONLY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-design) SKIP_DESIGN=true; shift ;;
        --iterate-only) ITERATE_ONLY=true; shift ;;
        --max-iterations) MAX_ITERATIONS="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_step() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}\n"; }
log_ok()   { echo -e "${GREEN}✓ $1${NC}"; }
log_warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
log_err()  { echo -e "${RED}✗ $1${NC}"; }

# ── Preflight checks ──────────────────────────────────────────────────────

if ! command -v claude &> /dev/null; then
    log_err "claude CLI not found. Install it first."
    exit 1
fi

if [ ! -f "$INPUTS_DIR/domain_choice.txt" ]; then
    log_err "Missing inputs/domain_choice.txt"
    echo "Create this file with your chosen domain, e.g.:"
    echo '  echo "supply chain management" > inputs/domain_choice.txt'
    exit 1
fi

DOMAIN=$(cat "$INPUTS_DIR/domain_choice.txt")
log_step "Exercise Factory — Domain: $DOMAIN"

# ── Step 1: Design ────────────────────────────────────────────────────────

if [ "$SKIP_DESIGN" = false ] && [ "$ITERATE_ONLY" = false ]; then
    log_step "Step 1: DESIGN — Creating exercise concept"

    claude --print \
        "$(cat "$PROMPTS_DIR/designer.md")

DOMAIN CHOICE: $DOMAIN

AUDIENCE DATA (summary):
$(python3 -c "
import openpyxl
wb = openpyxl.load_workbook('$INPUTS_DIR/audience.xlsx')
ws = wb.active
for i, row in enumerate(ws.iter_rows(values_only=True)):
    if i == 0: continue  # header row
    if i == 1:  # column headers
        print('Columns:', [str(c) for c in row if c])
        continue
    vals = [str(c)[:60] if c else '' for c in row[:10]]
    if any(v for v in vals[1:]):
        print('  '.join(vals))
    if i > 40: break
" 2>/dev/null || echo "(Could not read xlsx — install openpyxl)")

PATTERN REFERENCE:
$(cat "$INPUTS_DIR/hero_quest_pattern.md")

EXISTING EXERCISES FOR REFERENCE:
- The Support Desk (customer support) — in coding-exercises/the_support_desk/
- The Hero Quest (fantasy RPG) — in coding-exercises/agentic_ai_hero/

Write the complete concept.md content." \
    > "$ARTIFACTS_DIR/concept.md"

    log_ok "Concept written to artifacts/concept.md"

    # ── Human checkpoint ──
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  REVIEW: artifacts/concept.md"
    echo "  Does this concept look good for your audience?"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    read -p "Approve concept? (y/n/edit): " approval

    if [ "$approval" = "n" ]; then
        log_warn "Concept rejected. Edit inputs/domain_choice.txt or artifacts/concept.md and re-run."
        exit 0
    elif [ "$approval" = "edit" ]; then
        ${EDITOR:-nano} "$ARTIFACTS_DIR/concept.md"
        log_ok "Concept edited. Continuing..."
    fi
fi

# ── Step 2: Build ─────────────────────────────────────────────────────────

if [ "$ITERATE_ONLY" = false ]; then
    log_step "Step 2: BUILD — Implementing the exercise"

    if [ ! -f "$ARTIFACTS_DIR/concept.md" ]; then
        log_err "No concept.md found. Run without --skip-design first."
        exit 1
    fi

    claude \
        --print \
        -p "$(cat "$PROMPTS_DIR/builder.md")

CONCEPT:
$(cat "$ARTIFACTS_DIR/concept.md")

REFERENCE CODE — Read these files for implementation patterns:
- coding-exercises/the_support_desk/support_desk/data.py
- coding-exercises/the_support_desk/support_desk/scenario.py
- coding-exercises/the_support_desk/support_desk/game.py
- coding-exercises/the_support_desk/support_desk/tools.py
- coding-exercises/the_support_desk/support_desk/agent.py
- coding-exercises/the_support_desk/support_desk/main.py
- coding-exercises/the_support_desk/support_desk/display.py
- coding-exercises/the_support_desk/support_desk/interactive.py
- coding-exercises/the_support_desk/the_support_desk.ipynb
- coding-exercises/the_support_desk/the_support_desk_solutions.ipynb

Working directory: $EXERCISES_DIR

Build the complete exercise. Create all files. Then run the rule-based solution
to verify it wins. Report the result."

    log_ok "Exercise built"
fi

# ── Step 3-6: Test → Critique → Improve loop ──────────────────────────────

for iteration in $(seq 1 "$MAX_ITERATIONS"); do
    log_step "Iteration $iteration/$MAX_ITERATIONS: TEST → CRITIQUE → IMPROVE"

    # ── Test ──
    log_step "Step 3: TEST — Running the solution"

    claude \
        --print \
        -p "$(cat "$PROMPTS_DIR/tester.md")

Working directory: $EXERCISES_DIR

Find the most recently created exercise (not agentic_ai_hero, the_support_desk,
or exercise-factory). Read its solutions notebook, extract the think_rule_based
function, run it through the game engine, and write the test report.

Save the game log to: $ARTIFACTS_DIR/game_log.json
Save the test report to: $ARTIFACTS_DIR/test_report.md"

    if [ ! -f "$ARTIFACTS_DIR/test_report.md" ]; then
        log_err "Test report not generated"
        continue
    fi
    log_ok "Test complete — report at artifacts/test_report.md"

    # ── Critique ──
    log_step "Step 4: CRITIQUE — Analyzing results"

    claude \
        --print \
        -p "$(cat "$PROMPTS_DIR/critic.md")

Working directory: $EXERCISES_DIR

Analyze these artifacts:
- Test report: $ARTIFACTS_DIR/test_report.md
- Game log: $ARTIFACTS_DIR/game_log.json
$([ -f "$ARTIFACTS_DIR/concept.md" ] && echo "- Concept: $ARTIFACTS_DIR/concept.md")

Write your review to: $ARTIFACTS_DIR/issues.md"

    if [ ! -f "$ARTIFACTS_DIR/issues.md" ]; then
        log_err "Issues file not generated"
        continue
    fi

    # Check if we're done
    if grep -q "NO_ISSUES" "$ARTIFACTS_DIR/issues.md" 2>/dev/null; then
        log_ok "No issues found! Exercise is ready."
        break
    fi

    if grep -q "Verdict: PASS" "$ARTIFACTS_DIR/issues.md" 2>/dev/null; then
        log_ok "Exercise passes review!"

        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  The critic says PASS. Continue improving?"
        echo "  Review: artifacts/issues.md"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        read -p "Continue iterating? (y/n): " cont
        if [ "$cont" = "n" ]; then
            break
        fi
    fi

    log_warn "Issues found — implementing fixes"

    # ── Improve ──
    log_step "Step 5: IMPROVE — Fixing issues (iteration $iteration)"

    claude \
        --print \
        -p "$(cat "$PROMPTS_DIR/improver.md")

Working directory: $EXERCISES_DIR

Issues to fix: $ARTIFACTS_DIR/issues.md

Implement the fixes, then run the rule-based solution to verify it still wins.
Write the improvement log to: $ARTIFACTS_DIR/improvement_log_iter${iteration}.md"

    log_ok "Improvements applied — see artifacts/improvement_log_iter${iteration}.md"
done

# ── Summary ───────────────────────────────────────────────────────────────

log_step "Pipeline Complete"

echo "Artifacts:"
ls -la "$ARTIFACTS_DIR/"

echo ""
echo "Exercise location:"
ls -d "$EXERCISES_DIR"/*/ 2>/dev/null | grep -v -E "(agentic_ai_hero|the_support_desk|exercise-factory|interpretability|notes_rag|pro_forma)" || echo "  (no new exercise found)"

echo ""
echo "Next steps:"
echo "  1. Open the student notebook in Colab"
echo "  2. Play it yourself interactively"
echo "  3. Try implementing the solution without looking at the solutions notebook"
echo "  4. If it feels right, ship it!"
