# Build Prompt: Metal Gear Agent — Agentic AI Exercise

You are building a new agentic AI coding exercise called **"Metal Gear Agent"** (directory: `metal_gear_agent/`, package: `gear_agent/`). It is a stealth-ops grid world game inspired by Metal Gear Solid, where the student controls an AI "agent" (the pun: secret agent AND AI agent) infiltrating a military facility.

## CRITICAL: Read the Reference Exercise First

Before writing ANY code, read the **entire** existing exercise at:
```
coding-exercises/agentic_ai_hero/
```

Read ALL of these files completely — they are your blueprint:
- `quest_hero/game_world.py` — grid world, cells, NPCs, items, shops
- `quest_hero/hero.py` — hero state (hearts, gold, inventory)
- `quest_hero/tools.py` — 9 tool implementations
- `quest_hero/agent.py` — agent loop, parse function, TOOLS_DESCRIPTION
- `quest_hero/oracle.py` — NPC oracle (stub + LLM versions)
- `quest_hero/display.py` — HTML grid rendering
- `quest_hero/main.py` — game runners
- `quest_hero/interactive.py` — ipywidgets interactive play
- `quest_hero/__init__.py` — public exports
- `quest_hero_solutions.ipynb` — **READ THIS ENTIRE FILE** — it contains the three-layer LLM solution architecture
- `quest_hero_student.ipynb` — student notebook with TODOs

You must follow the **exact same architecture, patterns, and file structure**. The game engine structure, agent loop, tool parser, display system, interactive mode, and notebook structure should mirror the hero quest. Re-skin, don't reinvent.

## Theme: Metal Gear Solid

The game is a **stealth infiltration mission**. The "agent" (operative) must infiltrate a facility, gather intel, disable security systems, rescue a hostage, and escape — all while avoiding detection.

### Flavor Guidelines
- **Codec calls** = talking to NPCs / contacts (like Colonel Campbell, Mei Ling, Otacon)
- **"!" alert** = getting caught / penalty (losing stealth tokens)
- **Cardboard box** = hiding / safe rooms
- **Boss fights** = multi-step operations requiring prerequisite items/intel
- **Keycards / equipment** = quest items enabling progress
- **The pun**: the player is building an AI "agent" to control a secret "agent"

Do NOT require Metal Gear knowledge to play. The game should be self-contained and fun for anyone. Use the aesthetic, not the lore.

## World Design: 8x8 Military Facility Grid

Design an 8x8 grid representing a military facility. The operative starts at the **entry point** (e.g., bottom-left) and must work through the facility.

### Cell Types (map to hero quest equivalents)
| Metal Gear | Hero Quest | Emoji | Description |
|---|---|---|---|
| Corridor | Open | `·` | Empty passable corridor |
| Server Room / Lab | Forest | `💻` or `🧪` | Contains items (intel, equipment) |
| Reinforced Wall | Mountain | `🧱` | Impassable |
| Intel Cache | Treasure | `📁` | Contains intel points (= gold) |
| Boss Arena | Dragon | `💀` | Boss encounter |
| Informant / Contact | NPC | `🕵️` | NPC who gives missions/hints |
| Armory / Supply | Shop | `🔧` | Craft/buy equipment |
| Safe Room | Inn | `📻` | Rest, codec calls, receive missions |
| Entry Point | Castle | `🚪` | Starting area |

### Key Locations (design these)
- **Entry Point** (7,0) — where the operative starts
- **3 Intel Caches** — each gives 1 intel point (= treasure → gold)
- **2 Boss Arenas** — one requiring an EMP device, one requiring C4 explosives
- **3 Informants/Contacts** — each with personality and quest-gating keywords
- **2 Safe Rooms** — give missions, heal, receive quest items
- **2 Armory/Supply points** — craft equipment from components
- **3-4 Server Rooms/Labs** — contain components (circuit boards, detonators, etc.)
- **3-4 Reinforced Walls** — create routing bottlenecks

### NPCs (3 informants, map to Hermit/Merchant/Witch)

Design 3 NPCs with distinct personalities inspired by Metal Gear codec contacts:

1. **The Colonel** (veteran commander type) — gives strategic intel, knows about Boss A (security system), hints about EMP weapons, gives a "decode this intercepted transmission" errand
2. **The Engineer** (nervous tech specialist, Otacon-like) — knows about electronics, where to find circuit boards, can analyze captured tech, hints about Boss B (armored vehicle)
3. **The Informant** (mysterious double agent inside the facility) — knows guard patrol patterns, has a package to deliver, hints about secret passages and item locations

Each NPC must:
- Have a distinct speaking style (terse military, nervous techno-babble, cryptic whisper)
- Gate quest items behind specific keywords (just like the hero quest)
- Provide hints about bosses, items, and locations using in-world language
- NEVER give grid coordinates directly — always use descriptions ("the server room in the northeast wing")

### Quest Chains (map to hero quest structure)

Design quest chains that mirror the hero quest's structure:

**Chain A: EMP Device (→ Boss A: Security Mainframe)**
1. Pick up Circuit Board at a server room
2. Bring to Armory → craft EMP Device (costs 1 intel point)
3. Use EMP Device to fight Boss A (Security Mainframe) → +3 intel + Access Codes

**Chain B: C4 Explosives (→ Boss B: Armored Mech)**
1. Pick up Detonator Components at a lab
2. Get Plastic Explosives from informant quest
3. Bring both to Armory → craft C4 Package (costs 1 intel point)
4. Use C4 to fight Boss B (Armored Mech) → +3 intel + Hostage Location Data

**Errands (= letter delivery, herbal tea):**
- Colonel gives encrypted message → deliver to Engineer → +2 intel
- Safe Room operator gives medical supplies → deliver to other Safe Room → +2 intel

**Win condition: 10 intel points** (same structure as 10 gold)

### Boss Fights (2 bosses, map to Frost Wyrm / Shadow Beast)

1. **Security Mainframe** — requires EMP Device to disable. Without it, you trigger alarms (lose 1 health, get pushed back). With EMP → +3 intel + Access Codes.
2. **Armored Mech** — requires C4 Package to destroy. Without it, you can't damage it (lose 1 health, retreat). With C4 → +3 intel + Hostage Location Data.

### Items (map to hero quest items)
| Metal Gear Item | Hero Quest Equivalent | Purpose |
|---|---|---|
| Circuit Board | Ember Ore | Component for EMP Device |
| Detonator Components | Ghostcaps | Component for C4 (via quest chain) |
| Plastic Explosives | Medicine | Quest reward, component for C4 |
| EMP Device | Sunblade | Weapon for Boss A |
| C4 Package | Moonstone Lantern | Weapon for Boss B |
| Encrypted Message | Letter | Errand delivery item |
| Medical Supplies | Herbal Tea | Errand delivery item |
| Access Codes | Dragon Scales | Sellable loot from Boss A |
| Hostage Data | Dragon Scales | Sellable loot from Boss B |
| Ration | Bread | Consumable: +1 health |
| Medkit | Health Potion | Consumable: +2 health |

### Operative State (map to Hero)
- **Health**: 3 (like hearts) — 0 = mission failed
- **Intel Points**: 0 → 10 to win (like gold)
- **Inventory**: quest items, equipment, consumables
- **Position**: (row, col) on 8x8 grid
- **Visited**: set of visited cells (fog of war)
- **Briefing Log**: list of codec conversations (like journal)

## Tools (9 tools, map to hero quest)

| Metal Gear Tool | Hero Quest Tool | Description |
|---|---|---|
| `scan()` | `look()` | See current + adjacent cells. **Free action but wastes a turn.** |
| `move(direction)` | `move(direction)` | Move one cell in cardinal direction |
| `codec(question)` | `talk(question)` | Contact NPC / informant with a question |
| `collect()` | `pick_up()` | Collect items on current cell |
| `equip(item)` | `buy(item)` | Craft/equip at armory, or "sell" intel items |
| `use(item)` | `use(item)` | Use consumable (Ration, Medkit) |
| `engage()` | `fight()` | Engage boss at boss arena cell |
| `hide()` | `rest()` | Rest at safe room, costs 1 intel, restores 1 health |
| `sitrep()` | `status()` | Check operative status. **Free action but wastes a turn.** |

## CRITICAL LESSONS FROM HERO QUEST (DO NOT IGNORE)

These are hard-won lessons from building the hero quest. Violating any of these will break the exercise:

### 1. LLMs Cannot Do Spatial Reasoning
The LLM WILL fail at grid navigation. The solution MUST use BFS for all movement. Never ask the LLM to output `move(direction)`. The system prompt must say "NEVER call move() — navigation is handled automatically."

### 2. Three-Layer Architecture is Mandatory
```
Layer 1: Autopilot (_auto_interact)
  → Handles obvious actions: collect items, codec NPCs with right keywords,
    equip at armory, engage bosses with right equipment
  → Fires BEFORE the LLM is called
  → Only when agent is ALREADY on the right cell

Layer 2: BFS Navigation (_bfs_navigate)
  → Deterministic pathfinding toward quest targets
  → Quest targets derived from inventory state
  → Falls back to nearest unvisited cell, then any passable direction

Layer 3: LLM Decision
  → Only called when no autopilot action AND no quest target
  → Decides what to explore, which NPC to revisit, strategy
  → Output validated: scan/sitrep/move → redirected to BFS
```

### 3. Memory Must Be Structured, Not Raw
Build memory sections:
- **ACTIVE MISSIONS** (top, most visible) — what to do next, with exact tool syntax
- **COMPLETED** — what's been accomplished
- **FAILURES** — what went wrong (teach the LLM)
- **UNDISCOVERED** — what opportunities remain
- **URGENCY** — turns remaining, intel needed

### 4. Quest Items Gate Behind Keywords
NPC interactions must require specific keywords to trigger item exchange:
- Colonel: mention "message", "transmission", or "decode" to get Encrypted Message
- Engineer: mention "circuit", "analyze", or "tech" to trigger analysis
- Informant: mention "package", "explosives", or "supplies" to get items
The autopilot must know these keywords. The LLM oracle must hint at them without giving them away.

### 5. Output Validation is Essential
After the LLM generates an action, validate:
- `scan`/`sitrep` → redirect to BFS (waste of turn)
- `move` → redirect to BFS (LLM can't navigate)
- `codec` to NPC with no new business → redirect to BFS
- `engage` without correct equipment → redirect to BFS (don't let agent die)

### 6. NPC Oracle Must Stay In Character
Each NPC has a personality template. The oracle:
- Uses in-world language (not "go to cell (2,5)")
- Gives hints, not solutions
- Has a stub version (keyword matching) for Phase 1
- Has an LLM version (Gemini API) for Phase 2

### 7. The Agent Loop is Provided — Students Only Write `think()`
The `agent.py` file provides:
- `run_agent()` — the perceive-think-act loop (students don't touch this)
- `parse_tool_call()` — regex parser for `TOOL: name(args)` format
- `TOOLS_DESCRIPTION` — tool documentation string
- `think_rule_based()` stub — students implement Phase 1
- `think_llm()` stub — students implement Phase 2

### 8. Interactive Mode Comes First
Students must play manually before automating. The interactive mode (`interactive.py`) uses ipywidgets: direction buttons, action buttons, text input for codec questions.

### 9. The Game Must Be Winnable and Balanced
- Rule-based solution: wins in 70-90 turns, 10 intel, 3 health
- LLM solution: wins in 60-85 turns, 10 intel, 2-3 health
- Total available intel: ~15 (enough margin but not too easy)
- 3 intel caches (3) + 2 boss fights (6) + 2 errands (4) + selling loot (2) = 15 max

### 10. Index Errors in History Access
When building action history from the `history` list, be careful with index arithmetic. The hero quest had a bug where `history[i+1]` caused IndexError when history was short. Always bounds-check:
```python
global_i = history_offset + i
if global_i + 1 < len(history) and history[global_i + 1]["role"] == "result":
    result_text = history[global_i + 1]["content"][:120]
```

### 11. BFS Must Navigate Around Walls
BFS pathfinding must check `world.is_passable(nr, nc)` — walls (reinforced walls) are impassable. The map MUST have bottlenecks that force interesting routing but NO deadlocks.

### 12. Gemini API Integration
- Use `google-genai` package, model `gemini-2.5-flash`
- System prompt with tool descriptions + rules + few-shot examples
- `max_output_tokens=300`, `temperature=0.3` for LLM decisions
- `max_output_tokens=300`, `temperature=0.7` for NPC oracle (more personality)
- API key via `google.colab.userdata` or `os.environ['GEMINI_API_KEY']`
- Always wrap API calls in try/except with BFS fallback

## File Structure to Create

```
coding-exercises/metal_gear_agent/
├── gear_agent/
│   ├── __init__.py          # Exports: create_game, play_rule_based, play_with_llm, parse_tool_call, run_agent, TOOLS_DESCRIPTION
│   ├── data.py              # Enums (CellType), dataclasses (Item, NPC), catalogs
│   ├── scenario.py          # The 8x8 map layout, NPC definitions, item catalog, quest triggers
│   ├── game.py              # OperativeState (= Hero) + FacilityWorld (= GameWorld)
│   ├── tools.py             # 9 tool implementations + ToolResult
│   ├── agent.py             # Agent loop + parse_tool_call + TOOLS_DESCRIPTION + think stubs
│   ├── oracle.py            # NPC oracle: stub_oracle + llm_oracle + ORACLE_TEMPLATE
│   ├── display.py           # HTML grid rendering (copy pattern from hero quest, re-skin colors)
│   ├── interactive.py       # ipywidgets interactive play mode
│   └── main.py              # create_game(), play_rule_based(), play_with_llm()
├── metal_gear_agent.ipynb           # Student notebook with TODOs
├── metal_gear_agent_solutions.ipynb # Solutions notebook
└── requirements.txt                 # google-genai>=1.0.0
```

## Notebook Structure

### Student Notebook (`metal_gear_agent.ipynb`)
1. Setup (pip install, imports, API key)
2. Explore the facility (interactive play)
3. Tool call format explanation
4. **TODO 1**: `think_rule_based()` — hints on BFS, inventory tracking, quest priorities
5. Run and test Phase 1
6. **TODO 2**: `think_llm()` — API setup, prompt engineering hints
7. Run and test Phase 2
8. Reflection: compare approaches

### Solutions Notebook (`metal_gear_agent_solutions.ipynb`)
1. Setup
2. Interactive play
3. **Rule-based solution** — complete `think_rule_based()` with BFS
4. Run rule-based
5. **LLM solution** — complete three-layer `think_llm()`:
   - `_auto_interact()` — autopilot
   - `_bfs_navigate()` — BFS navigation with quest targets
   - `_build_memory_summary()` — structured memory
   - `SYSTEM_PROMPT_TEMPLATE` — with tools, rules, few-shot examples
   - `think_llm()` — orchestrator with output validation
6. Run LLM solution
7. Download log

## Verification Steps

After building everything:

1. **Run the rule-based solution** — must win (10 intel, health > 0, < 100 turns)
2. **Check the map** — all locations reachable, no deadlocks, bottlenecks exist
3. **Check quest chains** — all items obtainable, all bosses beatable
4. **Check NPC keywords** — all quest items gated properly
5. **Check BFS** — navigates around walls correctly
6. **Print the grid** — verify visual layout makes sense

Run verification:
```python
from gear_agent import *
hero, world, tools = create_game()
# Print the full map
from gear_agent.display import render_grid
print(render_grid(world, hero, show_all=True))
# Run rule-based
result = play_rule_based(think_rule_based_from_solutions, max_turns=100, delay=0.05)
print(f"Won: {result['won']} | Intel: {result['intel']} | Health: {result['health']} | Turns: {result['turns']}")
```

## Style Notes

- Keep the Metal Gear flavor fun but not cringe. Professional military tone with subtle humor.
- The "!" alert reference should appear in penalty messages ("! ALERT: Wrong equipment triggered alarm!")
- Codec conversations should feel like real briefings, not info dumps.
- Boss encounters should have dramatic flavor text.
- The display should use dark/military colors (dark grays, greens, reds for alerts).

## What NOT To Do

- Do NOT invent new architectural patterns — follow the hero quest exactly
- Do NOT skip the interactive mode
- Do NOT let the LLM handle navigation
- Do NOT hardcode quest solutions in the autopilot (autopilot only handles interactions on the CURRENT cell)
- Do NOT make the map trivially small — 8x8 with bottlenecks
- Do NOT forget the NPC oracle (both stub and LLM versions)
- Do NOT skip output validation in think_llm
- Do NOT use any LLM API other than Gemini (google-genai)
