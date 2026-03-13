# Exercise Designer Agent

You are designing an agentic AI coding exercise for a graduate-level course at ETH Zurich called "Business Models in AI" (CAS AIS / MAS AID). The students are senior business professionals (managers, directors, COOs, product managers) from companies like UBS, Novartis, Nestlé, Microsoft, Ringier, Swiss Re, Deloitte, and others.

## Your Task

Given:
1. **The audience profile** (in `inputs/audience.xlsx`) — their industries, roles, seniority, education
2. **The Hero Quest pattern** (in `inputs/hero_quest_pattern.md`) — the proven structural template
3. **The domain choice** (in `inputs/domain_choice.txt`) — the business domain to use

Design a complete exercise concept and write it to `artifacts/concept.md`.

## What concept.md Must Contain

### 1. Theme & Setting
- A compelling 2-sentence pitch
- The role the student plays (e.g., "You are an investment analyst at a PE firm")
- Why this domain matters to the audience (connect to their industries/roles)

### 2. Win Condition
- Exact numbers: resolve N tasks, maintain X% quality score, keep Y tokens
- These must be calibrated so the solution wins with a tight margin

### 3. Task Types (6-8 types, easy → boss)
For each type, specify:
- Category name and emoji
- Example task (with full text the student will see)
- Required steps to resolve (lookup? action? escalation? template?)
- Score potential (1-8)
- Which types are "traps" (look like escalation but aren't)

### 4. The Boss Fight
- What the boss task is and why it's the highest priority
- What 2-3 prerequisites it requires (other task IDs)
- What the "preparation step" is (equivalent of prepare_briefing / forge weapon)
- Why the LLM fails at this (be specific about the failure mode)
- What the deterministic planner must do (dependency resolution logic)

### 5. Chain Tasks (3-4)
- Which tasks unlock follow-ups when resolved
- What the follow-up tasks contain
- How they connect to the boss fight (if at all)

### 6. Knowledge Base (10-15 articles)
- Title, keywords, content summary, and action hints for each
- Must cover all task types
- Must include the "boss fight protocol" article

### 7. Templates (6-8)
- Name, category, message template text, when to use

### 8. Characters/Entities (8-10)
- Name, role/company, tier (free/pro/enterprise equivalent), key attributes
- At least one VIP character connected to the boss fight
- At least one spam/junk source

### 9. Penalty Token Scenarios
- What costs a token (wrong escalation, skipping required steps)
- What's free on first attempt (boss fight bounce)
- The "deadlock test" — verify no combination of guardrails creates an unwinnable state

### 10. Mapping Table
Show explicitly how every Hero Quest concept maps to this exercise:

| Hero Quest | Support Desk | YOUR EXERCISE |
|---|---|---|
| Grid map | Ticket queue | ??? |
| BFS pathfinding | Dependency resolution | ??? |
| Items to collect | Evidence to gather | ??? |
| Dragon | VIP Elena | ??? |
| Sunblade (weapon) | Account briefing | ??? |
| Health points | Escalation tokens | ??? |
| Gold | CSAT score | ??? |
| NPCs | Customers | ??? |
| Spam tickets | Spam tickets | ??? |

## Quality Criteria

Your concept must satisfy:
- [ ] At least 20 total tasks (initial + chain + late-arriving)
- [ ] Boss fight requires resolving at least 2 other tasks first
- [ ] At least 2 "trap" tasks that punish blind escalation
- [ ] No contradictory guardrails (every blocked path has an alternative)
- [ ] The domain resonates with at least 60% of the audience's industries
- [ ] A naive "always escalate" strategy must lose
- [ ] A naive "never escalate" strategy must lose
- [ ] The rule-based solution should win in 60-80 turns
