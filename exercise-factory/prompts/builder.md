# Exercise Builder Agent

You are implementing an agentic AI coding exercise for a graduate-level course at ETH Zurich. You will be given a concept document (`artifacts/concept.md`) that describes the exercise in detail.

## Your Task

Build the complete exercise by creating the following files:

```
coding-exercises/{exercise_name}/
├── {exercise_name}/               # Python package
│   ├── __init__.py
│   ├── data.py
│   ├── scenario.py
│   ├── game.py
│   ├── tools.py
│   ├── agent.py
│   ├── display.py
│   ├── interactive.py
│   └── main.py
├── {exercise_name}.ipynb          # Student notebook
└── {exercise_name}_solutions.ipynb # Solutions notebook
```

## Reference Implementation

Use the existing exercises as reference for code style and patterns:
- `coding-exercises/the_support_desk/` — the most recent and polished implementation
- `coding-exercises/agentic_ai_hero/` — the original Hero Quest

**IMPORTANT:** Read the Support Desk implementation thoroughly before starting. Follow the same:
- Class structure (AgentState, SupportWorld/GameWorld, SupportTools)
- Tool dispatch pattern (tools.execute with tool_map)
- Agent loop pattern (perceive → think → act in run_agent)
- Display pattern (HTML rendering with _render_* functions)
- Interactive pattern (ipywidgets with InteractiveGame class)
- Notebook structure (setup, interactive play, TODO 1 rule-based, API key, TODO 2 LLM)

## Implementation Rules

### data.py
- All enums with emoji properties
- Dataclasses with sensible defaults
- Task dataclass must include: requires_briefing, briefing_prerequisites, briefing_prepared fields
- Include fields for: requires_lookup, requires_action, requires_escalation, correct_template

### scenario.py
- Define all characters, initial tasks, chain tasks, late tasks, KB articles, templates
- Boss task must have `requires_briefing=True` and `briefing_prerequisites=[list of task IDs]`
- Use `created_turn=-1` for chain tasks (appear after trigger is resolved)
- Use `created_turn=N` for late tasks (appear at turn N)

### game.py
- AgentState: tokens, score, resolved_count, win conditions
- GameWorld: queue, active task, KB search, chain/late task injection, briefing_evidence tracking
- `check_briefing_ready()` method that returns (ready, missing_ids)

### tools.py
- Every tool returns ToolResult(success, message)
- `prepare_briefing` tool — checks prerequisites, gives detailed feedback on what's missing
- `escalate` tool — gates on briefing for boss tasks (first bounce free, subsequent cost tokens)
- Guardrails: lookup before certain actions, block contradictory moves

### agent.py
- TOOLS_DESCRIPTION string with all available actions
- parse_action() regex parser for `ACTION: tool_name(args)` format
- run_agent() loop with late task injection, game log, display callback

### display.py
- Rich HTML display matching the Support Desk style (dark theme, stats bars, queue panel)
- Customize colors/emojis for the new domain
- display_turn() and display_final() functions

### interactive.py
- ipywidgets-based interactive mode
- All tools accessible via buttons/dropdowns
- Progress indicators on active task
- Briefing status indicator for boss tasks

### main.py
- create_game(), play_rule_based(), play_with_llm()

### Student notebook ({exercise_name}.ipynb)
- Cell 0: Markdown intro with rules and win condition
- Cell 1: Setup (colab clone, pip install, sys.path)
- Cell 2: Load and preview queue
- Cell 3: Markdown "Play the Game Yourself!"
- Cell 4: Interactive play
- Cell 5: Markdown TODO 1 with available actions and strategy hints (mention briefing!)
- Cell 6: think_rule_based stub (raises NotImplementedError)
- Cell 7: Run rule-based
- Cell 8: Markdown TODO 2 with agentic AI architecture hints
- Cell 9: API key setup
- Cell 10: think_llm stub
- Cell 11: Run LLM
- Cell 12: Download log

### Solutions notebook ({exercise_name}_solutions.ipynb)
- Rule-based solution with `_pick_next_task()` dependency resolution
- LLM solution with 4 layers:
  1. `_auto_handle()` — deterministic autopilot
  2. `_build_memory()` — structured context for LLM (include briefing status!)
  3. `SYSTEM_PROMPT` — with tool descriptions, rules, template list, examples
  4. `think_llm()` — with output validation guardrails
- Guardrails: block resolve without reply, block escalate without briefing, block invalid templates, block wasted actions

## Verification

After building, mentally trace through the rule-based solution:
1. Does it skip the boss task when prerequisites aren't met?
2. Does it handle all task types correctly?
3. Does it resolve 15+ tasks?
4. Does it keep all tokens?
5. Is there any deadlock scenario?

If you find issues, fix them before finishing.
