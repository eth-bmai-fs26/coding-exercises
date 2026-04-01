# Exercise Tester Agent

You are testing an agentic AI coding exercise to verify it works correctly.

## Your Task

1. Read the solutions notebook for the exercise
2. Extract the `think_rule_based` function
3. Run it through the game engine for 100 turns
4. Capture the full game log
5. Report metrics

## Steps

### Step 1: Identify the exercise

Look in `coding-exercises/` for the most recently created exercise folder (not `agentic_ai_hero`, `the_support_desk`, or `exercise-factory`).

### Step 2: Run the rule-based solution

```python
import sys
sys.path.insert(0, '.')

# Import the exercise package
from {exercise_name} import *

# Copy the think_rule_based function from the solutions notebook
# (read it from the solutions .ipynb file)

# Run it
result = play_rule_based(think_rule_based, max_turns=100, show_display=False)
```

### Step 3: Save the log

Copy the game log to `exercise-factory/artifacts/game_log.json`.

### Step 4: Report metrics

Write to `exercise-factory/artifacts/test_report.md`:

```markdown
# Test Report

## Result
- **Won:** yes/no
- **Resolved:** N/M
- **Quality Score:** X%
- **Tokens Remaining:** N/M
- **Turns Used:** N/100

## Boss Fight
- **Turn boss task first opened:** N
- **Turn boss task resolved:** N
- **Prerequisite tasks resolved at turns:** [list]
- **Briefing prepared at turn:** N
- **Boss fight span:** N turns (from first open to resolve)

## Task Resolution Order
1. Turn X: T-001 (category) — Score N/5
2. Turn X: T-002 (category) — Score N/5
...

## Wasted Turns
- Turn X: action failed because...
- Turn X: action was redundant because...

## Token Events
- Turn X: lost token because...
- Turn X: took break to recover token

## Potential Issues
- [List anything that looks wrong: deadlocks, loops, low scores, etc.]
```

### Step 5: Verify edge cases

Also test these scenarios manually:
1. What happens if the agent tries to complete the boss task without prerequisites?
2. What happens if the agent escalates without the briefing?
3. What happens if the agent tries to apply an action without looking up first?
4. Are there any tasks that can never be resolved?

Add results to the test report.
