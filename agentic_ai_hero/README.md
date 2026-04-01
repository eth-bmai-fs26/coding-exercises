# Quest Hero: An RPG-Based Agentic AI Exercise

Build an LLM-powered agent that navigates an RPG grid world, interprets cryptic NPC dialogue, manages resources, and completes quests.

## Setup

```bash
pip install anthropic
```

Set your API key:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Open `quest_hero_student.ipynb` and follow the instructions.

## Structure

```
agentic_ai_hero/
├── quest_hero/                    # Game engine (provided)
│   ├── game_world.py              # Map, cells, NPCs, items
│   ├── hero.py                    # Hero state
│   ├── tools.py                   # 9 tool implementations
│   ├── oracle.py                  # NPC oracle (stub + TODOs)
│   ├── agent.py                   # Agent loop + think functions (TODOs)
│   ├── display.py                 # Visualization
│   └── main.py                    # Game runner
├── quest_hero_student.ipynb       # Student notebook
└── quest_hero_solutions.ipynb     # Solutions
```

## TODOs

| # | Phase | File | Function | Description |
|---|-------|------|----------|-------------|
| 1 | 1 | `agent.py` | `think_rule_based()` | Rule-based if/else decision logic |
| 2 | 2 | `oracle.py` | `build_npc_system_prompt()` + `ask_npc()` | LLM-powered NPC oracle |
| 3 | 2 | `agent.py` | `think_llm()` | LLM-powered agent decision function |

## The Game

- **8x8 grid** with NPCs, shops, inns, dragons, forests, and treasures
- **Win condition**: Collect 10 gold and survive (hearts > 0)
- **15 total gold** available — multiple winning strategies exist
- **Limited visibility**: Hero can only see adjacent cells
