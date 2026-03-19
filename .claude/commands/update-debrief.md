Update the debrief _STATIC_CONTEXT across all notebooks for a given exercise when game mechanics change.

When the game world, tools, quest structure, or map layout changes, the debrief _STATIC_CONTEXT strings sent to external LLMs (ChatGPT/Gemini) must be updated to match. This command:

1. Reads the current game state (map, tools, quest structure) from the engine files
2. Compares it against the _STATIC_CONTEXT in each notebook's debrief helpers cell
3. Reports any mismatches (e.g., wrong grid size, missing tools, outdated quest info)
4. If asked, updates the _STATIC_CONTEXT strings to match the current game state

Important: The _STATIC_CONTEXT must use the coaching format (DIAGNOSE → GUIDE → HINT → IMPLEMENT TOGETHER). Never revert to code-generator mode.

Usage: /update-debrief agentic_ai_spy
