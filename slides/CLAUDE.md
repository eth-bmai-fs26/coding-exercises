# Slides — Agentic AI for CAS BMAI FS26

## What's Here

`agentic_ai_slides.html` — A reveal.js slide deck (18 slides) for the Agentic AI lecture in the Building ML & AI Applications course (ETH Zurich, CAS BMAI FS26).

## Slide Deck Structure

1. **Title**: Agentic AI — From Language Models to Autonomous Agents
2. **What is Agentic AI?**: Definition, chatbot vs agent comparison
3. **The Agent Loop**: Perceive → Think → Act cycle diagram
4. **Anatomy of an Agent**: LLM brain, tools, memory, environment
5. **Why Agentic AI?**: Real-world applications, why now
6. **From Chatbot to Agent**: Comparison table
7. **The Hidden Layer** (transition): Spy-themed exercise intro
8. **Mission Overview**: Objective (10 dossiers), constraints (health, turns)
9. **The Game World**: Full 8x8 grid map with legend
10. **Agent Tools**: move, talk, collect, fabricate (+ auto scan)
11. **Tool Call Format**: `TOOL: name(args)` + regex parser
12. **System Architecture**: Full SVG diagram (environment, agent loop, LLM, display)
13. **Quest Chains**: Three quest chain diagrams (USB, Cryo-Sentinel, Medical Trade)
14. **Three Mission Tiers**: Micro (3x3) → Training (5x5) → Full (8x8)
15. **Your Task**: `think_llm()` function signature and requirements
16. **Building the Prompt** (3 slides): System message → User message → API call
17. **Iterative Prompt Improvement** (transition): Using ChatGPT as coach
18. **The Improvement Cycle**: Run → Observe → Debrief → Coach → Improve (SVG cycle)
19. **The Debrief System**: How to generate paste blocks and use coaching
20. **ChatGPT as Coach**: Diagnose → Guide → Hint → Implement Together
21. **Common Failures & Fixes**: Table of symptoms, root causes, prompt fixes
22. **Prompt Engineering Tips**: System prompt and user message best practices
23. **Your Workflow**: Step-by-step guide for the exercise
24. **Time to Code**: Call to action with workflow diagram

## Tech Stack

- **reveal.js 5.1.0** via CDN (no local deps)
- **Syntax highlighting** via reveal.js highlight plugin (monokai theme)
- **SVG diagrams** for architecture, quest chains, and the improvement cycle (all inline)
- **Custom CSS** with ETH-inspired dark theme (eth-blue: #1F407A, eth-teal: #0D9999)
- **Spy theme accents**: terminal green (#00ff41), red alerts (#e94560)

## How to Present

Open `agentic_ai_slides.html` in a browser. Arrow keys or space to navigate. Press `S` for speaker notes (none added yet). Press `F` for fullscreen.

## How to Edit

- All slides are in a single HTML file — search for `<section>` tags
- SVG diagrams are inline — edit coordinates directly
- CSS variables at the top control the color scheme
- Code blocks use reveal.js highlight plugin with `language-python` class
- The game grid on the map slide uses a CSS grid with emoji cells

## Relationship to Exercise

The slides reference:
- `agentic_ai_spy/hidden_layer/` — the game engine (agent.py, tools.py, game_world.py, etc.)
- `agentic_ai_spy/the_hidden_layer_micro_mission.ipynb` — the first student notebook
- The debrief system built into each notebook
- `TOOLS_DESCRIPTION` and `MISSION_BRIEFING` constants from `agent.py`

## Future Improvements

- Add speaker notes to each slide
- Add a live demo slide (screenshot or embedded Colab output)
- Add NPC portrait images from `agentic_ai_spy/assets/`
- Add animation fragments for progressive reveal of diagrams
- Consider adding a slide about the solution architecture (BFS + LLM hybrid)
