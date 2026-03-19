# CLAUDE.md — Coding Exercises for CAS BMAI FS26

## What This Repo Is

University coding exercises for the **CAS Business Management & AI** course (ETH Zurich, FS26). Each subdirectory is an independent exercise. Most use **Google Colab** notebooks with the **Gemini API**.

## Repository Structure

```
coding-exercises/
├── agentic_ai_spy/      # "The Hidden Layer" — spy-themed agentic AI (PRIMARY EXERCISE)
├── agentic_ai_hero/     # RPG-themed agentic AI (same engine pattern)
├── metal_gear_agent/    # Tactical espionage agent (same engine pattern)
├── fridge_chef/         # Kitchen assistant agent (3 phases: rules → LLM → distillation)
├── the_supply_line/     # Supply chain logistics agent
├── the_support_desk/    # Customer service agent
├── rag_exercise/        # RAG fundamentals
├── notes_rag/           # RAG with HNSW / Louvain variants
├── RAG TA CX/           # CityLens restaurant recommender (RAG)
├── clustering-exercises/# Clustering algorithms
├── interpretability/    # Neural network interpretability (multi-language)
├── pictogram_attention_game/ # HTML5 visual attention game
├── pro_forma/           # AI-powered business case builder (JS + Claude API)
└── exercise-factory/    # Meta-tooling: multi-agent pipeline to generate exercises
```

## Agentic AI Exercise Pattern

The 6 agent exercises (`agentic_ai_spy`, `agentic_ai_hero`, `metal_gear_agent`, `fridge_chef`, `the_supply_line`, `the_support_desk`) share a common architecture:

```
exercise_dir/
├── *_student.ipynb          # Student notebook (has TODO stubs)
├── *_solutions.ipynb        # Solutions notebook
└── package_name/            # Python game engine (students do NOT modify)
    ├── agent.py             # Agent loop + think_llm() stub
    ├── tools.py             # Tool implementations (move, talk, collect, etc.)
    ├── game_world.py        # Map, cells, NPCs, items
    ├── oracle.py            # NPC dialogue (stub + LLM-powered)
    ├── display.py           # Notebook HTML visualization
    └── interactive.py       # Manual play mode (ipywidgets)
```

**Student task**: Implement `think_llm()` — build a system prompt, format game history, call `client.models.generate_content()` (Gemini), return a `TOOL: name(args)` string.

**Agent loop**: `run_agent()` in `agent.py` runs perceive → think → act. Auto-scans each turn. Parses LLM output via `parse_tool_call()`.

## The Hidden Layer (agentic_ai_spy/) — Detailed

This is the primary/most developed exercise. Three progressive notebooks:

| Notebook | Grid | Dossiers | Turns | Difficulty |
|----------|------|----------|-------|------------|
| `the_hidden_layer_micro_mission.ipynb` | 3×3 | 3 | 30 | Intro |
| `the_hidden_layer_training_mission.ipynb` | 5×5 | 5 | 50 | Medium |
| `the_hidden_layer_full_mission.ipynb` | 8×8 | 10 | 100 | Full |

Each notebook has: setup → interactive play → API key → think_llm TODO → sanity check → run → debrief.

**Engine files** (`hidden_layer/`):
- `operative.py` — Player state: health (3), dossiers, inventory, position, visited, journal
- `game_world.py` — CellType enum, NPC/Item/ForgeInfo dataclasses, GameWorld 8×8 grid builder
- `tools.py` — GameTools with move/talk/collect/fabricate + quest flag logic
- `oracle.py` — `stub_oracle` (keyword-matched), `llm_oracle` (Gemini), `gemini_call_with_retry` (backoff wrapper)
- `agent.py` — `run_agent()` loop, `MISSION_BRIEFING`, `TOOLS_DESCRIPTION`, `parse_tool_call()`
- `display.py` — Rich HTML rendering for Colab (grid, health bar, dossier bar, etc.)
- `interactive.py` — `InteractiveGame` with ipywidgets for manual play
- `main.py` — `create_game()` and `play_with_llm()` convenience wrappers

**Micro/Training notebooks** define their own smaller game worlds (MicroGameWorld, MiniGameWorld) as subclasses of GameWorld, with patched tools (MicroGameTools, MiniGameTools) and stub oracles inline in the notebook cells.

**Debrief system**: Each notebook has a debrief cell that analyzes the game log JSON, generates a paste block for ChatGPT/Gemini, and instructs the external LLM to act as a **coach** (diagnose → guide → hint → implement together). The LLM is told to NEVER return a complete drop-in function.

**Solution architecture** (in solutions notebooks): BFS handles navigation (LLM outputs `NAVIGATE: (row, col)` or `EXPLORE`), auto-collect is deterministic, LLM decides everything else (what to say, craft, fight).

## Key Conventions

- **Notebooks run on Google Colab** — setup cells clone repo, install deps, configure path
- **Gemini API** via `google-genai` package — students get free API keys from AI Studio
- **All notebooks clone from branch `no-bfs`** (setup cells use `git clone -b no-bfs`)
- **Game logs** are JSON files written to CWD (gitignored via `*_log_*.json`)
- **NPC portraits** stored in `assets/` as JPG/PNG, embedded as base64 in notebook HTML
- **`@title` comments** in code cells make them collapsible in Colab

## When Editing Notebooks

- Each notebook has student + solutions versions — keep them in sync
- Micro/Training notebooks define custom GameWorld subclasses inline — changes to the engine may need mirroring in these cells
- The `_STATIC_CONTEXT` string in debrief helpers cells contains game-specific info sent to external LLMs — update it when game mechanics change
- `NOTEBOOK_VERSION` in setup cells tracks versions (currently v2.1 for micro, v1.5 for training/full)

## Common Gotchas

- `hide()` tool is referenced in brochure/docs but NOT implemented in tools.py
- `has_won` checks `dossiers >= 10` only — does NOT require returning to position (0,0)
- Micro mission robot gives +3 dossiers (engine default) despite docs saying +1
- Full mission solutions notebook's `think_llm` takes 3 args (closes over `client`) unlike the 4-arg signature in student notebooks
