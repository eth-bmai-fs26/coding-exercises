# Fridge Chef

An agentic AI coding exercise. A kitchen assistant agent checks the fridge,
interprets a natural language request, picks a recipe, and builds a shopping list —
using tools in a loop.

**Students only ever open `fridge_chef.ipynb`.** Everything else is infrastructure.

---

## How it works

The agent runs a loop: perceive → think → act. Each turn it observes the current
state (what's in the fridge, which recipe was chosen, what's on the shopping list),
calls a `think` function to decide the next action, and executes one of five tools.
The loop ends when the agent calls `done()`.

The exercise has three phases, all in the notebook:

- **Phase 1** — implement `think_rule_based`: keyword-match the user's request to
  an ingredient, follow a fixed pipeline. Works for explicit requests (`"cook eggs"`),
  breaks on natural language (`"something comforting for a cold evening"`).
- **Phase 2** — implement `think_llm`: same pipeline, but use Gemini to interpret
  the request and pick the right ingredient. The LLM's only real job is that one
  translation step — everything else stays autopilot.
- **Phase 3** — skeleton for `think_classifier`: distill the LLM into a small
  sklearn classifier trained on logged game data. <-- This is a bad idea... Its better to provide a syntetic dataset and let them train a classier on that, synt dataset is created using the think from phase 2

---

## Package files (`fridge_chef/`)

| File | What it does | Notes |
|------|-------------|-------|
| `data.py` | `ChefState` dataclass — tracks fridge contents, chosen recipe, shopping list, completion flag | Core state |
| `scenario.py` | `FRIDGE_CONTENTS`, `RECIPE_DB` (ingredient → recipes), `INGREDIENTS_DB` (recipe → ingredients) | Just data |
| `game.py` | `KitchenWorld` — wraps the databases, exposes lookup methods | Thin wrapper |
| `tools.py` | The 5 tools the agent can call + dispatcher. **This is where the agent's action space is defined.** | Core logic |
| `agent.py` | `run_agent()` loop, `parse_action()`, `TOOLS_DESCRIPTION`. **This is the agent loop.** | Core logic |
| `main.py` | `create_game()`, `play_rule_based()`, `play_with_llm()` — convenience wrappers called from the notebook | Glue |
| `display.py` | Kitchen-themed HTML panel rendered in Jupyter. Dark theme, pipeline progress bar, fridge/shopping panels | HTML only |
| `interactive.py` | ipywidgets UI for manually playing the game in the notebook | HTML only |
| `__init__.py` | Re-exports everything so the notebook can do `from fridge_chef import *` | Glue |
