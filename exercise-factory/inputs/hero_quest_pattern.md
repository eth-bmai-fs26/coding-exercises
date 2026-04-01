# The Hero Quest Pattern — Abstract Template for Agentic AI Exercises

This document captures the proven pattern from two successful exercises:
- **The Hero Quest** (fantasy RPG) — students navigate a grid, collect items, slay a dragon
- **The Support Desk** (customer support) — students process tickets, handle escalations, resolve a VIP crisis

Every new exercise should follow this same structural pattern, re-skinned for a different business domain.

---

## Core Architecture

### 1. Simulated Environment with State Machine

The game world has:
- **A queue/map of tasks** — things to process (tickets, deals, orders, stories, etc.)
- **Task state machine** — each task goes through phases: discover → investigate → act → respond → close
- **Global state** — agent stats tracked across all tasks (score, tokens, turn count)
- **Time pressure** — limited turns forces prioritization
- **Information sources** — a knowledge base the agent can query

### 2. Win Condition (Quantifiable)

- Resolve N+ tasks (e.g., 15 tickets)
- Maintain quality score >= X% (e.g., 80% CSAT)
- Don't lose all penalty tokens (e.g., 3 escalation tokens)
- All three conditions must be met simultaneously

### 3. Penalty Token System

- Start with 3 tokens
- **Wrong decisions** cost a token (wrong escalation, skipping required steps)
- **0 tokens = game over** (immediate loss)
- **`take_break()` action** recovers 1 token but costs 5 turns
- Creates risk/reward tension: rushing is dangerous, but being too slow means running out of turns

### 4. Task Types (Easy → Hard)

Design 5-7 distinct task categories with escalating complexity:

| Difficulty | Example (Support Desk) | Pattern |
|---|---|---|
| **Trivial** | Spam — just close it | 1 step, no lookup needed |
| **Easy** | Password reset | Lookup → action → template → resolve |
| **Medium** | Billing dispute | Lookup → verify → action → reply → resolve |
| **Hard** | Bug report with chain | Lookup → reply → wait for chain → action → reply → resolve |
| **Trap** | Looks like escalation but isn't | Tests if agent reads KB vs. blindly escalating |
| **Boss** | VIP briefing | Multi-task dependency resolution (see below) |

### 5. The Boss Fight (Multi-Step Planning Challenge)

The single most important design element. This is what separates a good exercise from a trivial one.

**Requirements:**
- The boss task is the **highest priority** in the queue (appears first)
- It **cannot be completed immediately** — it has prerequisites
- Prerequisites are **other tasks** that must be resolved first
- The agent must **leave the boss task** and go handle prerequisites
- After prerequisites are met, the agent must **perform a preparation step** (forge the weapon / prepare the briefing)
- Only then can the boss task be completed

**Why the LLM fails at this:**
1. The boss task has the highest priority → LLM opens it first
2. LLM tries to complete it immediately → gets bounced/rejected
3. LLM retries the same approach → wastes turns, loses tokens
4. LLM never figures out it needs to leave and handle other tasks first
5. Even if it reads the error message, switching away from a high-priority task requires planning that LLMs can't do

**What the deterministic planner does:**
1. Checks if the boss task has unmet prerequisites
2. **Skips it** in the queue (dependency resolution / topological sort)
3. Processes prerequisite tasks naturally
4. Comes back when prerequisites are met
5. Performs the preparation step
6. Completes the boss task

This is the **BFS equivalent** — instead of spatial pathfinding, it's dependency graph traversal.

### 6. Chain Tasks (Unlocked by Resolution)

Resolving certain tasks unlocks follow-up tasks:
- Resolving a billing dispute → customer asks "why did this happen?"
- Resolving an API bug → engineering sends a fix confirmation
- These add depth without front-loading complexity
- They test whether the agent can handle dynamic queue changes

### 7. Late/Time-Gated Tasks

New tasks arrive at specific turns:
- Creates the feeling of a real inbox/queue
- Forces re-prioritization
- Some late tasks are easy (keeps the agent busy while prerequisites resolve)
- Some late tasks are critical (forces trade-off decisions)

---

## The Three-Layer Solution Architecture

Every solution should demonstrate these three layers:

### Layer 1: Autopilot (Deterministic — No LLM)

Handle obvious cases with code:
- Spam → close immediately
- Password reset → lookup → action → template → resolve
- Known escalations → escalate to correct team

**Teaching point:** ~60-70% of tasks can be handled without any LLM at all.

### Layer 2: Planner (Algorithmic — No LLM)

Handle dependencies and prioritization with code:
- **Dependency resolution** — skip tasks with unmet prerequisites
- **Priority scoring** — deterministic formula, not LLM judgment
- **State tracking** — structured memory of what's been done
- **Guardrails** — block dangerous actions before they execute

**Teaching point:** The LLM can't plan, can't do graph traversal, can't track state reliably.

### Layer 3: LLM (Only for Ambiguous Decisions)

Use the LLM only when code can't decide:
- Crafting custom replies to unusual customer messages
- Interpreting ambiguous task descriptions
- Deciding between multiple valid approaches

**Teaching point:** The LLM is a tool, not the agent. The agent is the code that orchestrates everything.

---

## Implementation Structure

Every exercise should produce these files:

```
exercise_name/
├── exercise_name/               # Python package (the game engine)
│   ├── __init__.py              # Public exports
│   ├── data.py                  # Data models (enums, dataclasses)
│   ├── scenario.py              # Scenario data (tasks, KB, templates, characters)
│   ├── game.py                  # Game state (agent state, world state)
│   ├── tools.py                 # Tool implementations (all actions + guardrails)
│   ├── agent.py                 # Agent loop (perceive → think → act) + action parser
│   ├── display.py               # Rich HTML display for notebooks
│   ├── interactive.py           # Interactive play mode (ipywidgets)
│   └── main.py                  # Convenience runners (create_game, play_rule_based, play_with_llm)
├── exercise_name.ipynb          # Student notebook (TODOs)
└── exercise_name_solutions.ipynb # Solutions notebook (complete implementations)
```

### Key Design Rules

1. **The game engine must be fair** — all information needed to win is available through tools
2. **No contradictory guardrails** — if a guardrail blocks an action, there must be a valid alternative path
3. **The solution must win deterministically** — no randomness in the rule-based solution
4. **CSAT/score should be tight** — winning with exactly the minimum score is ideal (proves balance)
5. **The log must be diagnostic** — every turn records: action, result, success, score, token count
6. **Interactive mode first** — students must play manually before automating

---

## Scoring System

Each task has a `score_potential` (max points if handled perfectly).

Penalties for:
- Not replying/communicating before closing (-2)
- Not researching/looking up before acting (-2)
- Wrong action applied (-3)
- Wrong escalation (-3)
- Missing required steps (-2)

Score is capped at [0, 5] per task, then scaled to percentage.

---

## Gemini API Integration

The LLM solution uses:
- `google-genai` package
- `gemini-2.5-flash` model
- System prompt with tool descriptions, rules, and few-shot examples
- `max_output_tokens=500`, `temperature=0.2`
- Output format: `REASONING: ... \n ACTION: tool_name(args)`
- Regex parser: `ACTION:\s*(\w+)\((.*?)\)`
- API key via `google.colab.userdata` or `os.environ['GEMINI_API_KEY']`
