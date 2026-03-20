# Fridge Chef

An agentic AI exercise built around a kitchen assistant. The agent checks the
fridge, interprets a natural-language request, picks a recipe, and builds a
shopping list by calling tools in a loop.

This folder now has two notebooks:

- `fridge_chef_Exercise.ipynb` — the student version with TODOs
- `fridge_chef_secondTask_sol.ipynb` — the filled solution version

The Python package in `fridge_chef/` is the shared infrastructure both
notebooks use.

---

## Notebook Structure

The exercise is split into three phases:

- **Phase 1 — Rule-Based Agent**
  Students implement `think_rule_based(...)`. The agent follows a fixed
  pipeline: check the fridge, search recipes, choose a recipe, add missing
  ingredients, then finish. It works for direct requests such as
  `"I want something with eggs"`, but breaks on natural-language intent because
  it can fall back to the first fridge ingredient.

- **Phase 2 — LLM-Powered Agent**
  Students build a two-step LLM controller:
  - a **Thinker** proposes the next action from the current kitchen context
  - a **Validator** approves or revises that action before execution

  This phase introduces prompt design, helper functions such as
  `build_context(...)`, `call_llm(...)`, `build_action_string(...)`, and the
  full `think_llm(...)` wiring. The LLM is not only used for ingredient
  selection; it can influence recipe choice and later decisions through the
  action it proposes.

- **Phase 3 — Bonus: Classifier Distillation**
  Students start from a baseline classifier that learns the workflow from
  LLM-generated examples. The main goal is to show distillation: use phase 2 to
  generate training data, then train a smaller model to imitate the LLM's
  tool-selection behavior. This phase is intentionally open-ended and works best
  as an extension or bonus task.

---

## What Students Are Expected To Do

In the exercise notebook, students mainly:

- complete the rule-based `think` function
- write prompts for the Thinker and Validator
- implement `build_action_string(...)`
- implement `think_llm(...)`
- inspect the LLM pipeline and compare it against the rule-based version
- optionally experiment with the phase-3 classifier baseline

The solution notebook keeps the same progression but fills in the missing code.

---

## How The Agent Works

The core loop is:

1. observe the current state
2. call a `think` function to choose the next action
3. parse that action
4. execute one tool
5. update the state
6. repeat until `done()`

The available tools are:

- `check_fridge()`
- `search_recipes(ingredient="...")`
- `get_ingredients(recipe="...")`
- `add_to_shopping_list(item="...")`
- `done()`

The loop itself lives in the package code, not in the notebook.

---

## Package Files (`fridge_chef/`)

| File | What it does |
|------|--------------|
| `data.py` | Defines `ChefState`, which stores fridge contents, possible recipes, chosen recipe, needed ingredients, shopping list, and completion state |
| `scenario.py` | Defines the recipe and ingredient databases used by the game |
| `game.py` | Defines `KitchenWorld`, the environment that serves fridge contents and recipe lookups |
| `tools.py` | Implements the tool actions and updates the agent state |
| `agent.py` | Defines `parse_action(...)`, `run_agent(...)`, and the tool descriptions shared with the LLM |
| `main.py` | Provides `create_game()`, `play_rule_based()`, and `play_with_llm()` |
| `display.py` | Renders the notebook UI panels |
| `interactive.py` | Provides the manual interactive play mode |
| `__init__.py` | Re-exports the package API for `from fridge_chef import *` |

---

## Notes

- Each new run creates a fresh game state, so repeated runs can produce
  different outcomes.
- The notebooks are designed for Colab or Jupyter-style execution.
- Phase 3 is deliberately a baseline, not a final production-ready classifier.
