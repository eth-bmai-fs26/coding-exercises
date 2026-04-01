"""Agent loop and think function for Metal Gear Agent.

Students implement:
- think_rule_based() in Phase 1
- think_llm() in Phase 2

Everything else is provided.
"""

import json
import re
from datetime import datetime
from typing import Callable, Optional

from gear_agent.game import OperativeState
from gear_agent.scenario import FacilityWorld
from gear_agent.tools import GameTools, ToolResult


# ---------------------------------------------------------------------------
# Tool descriptions (provided to the LLM in Phase 2)
# ---------------------------------------------------------------------------

TOOLS_DESCRIPTION = """Available tools (use exactly one per turn):

TOOL: scan()
  See the types of adjacent cells (north/south/east/west). Free action.

TOOL: move(direction="north|south|east|west")
  Move one step in a cardinal direction. Triggers cell events on arrival.
  Reinforced walls are impassable. Moving into a server room may trigger a trap.

TOOL: codec(question="your question here")
  Contact an NPC, safe room operator, or armory technician in your current cell.
  NPCs give hints and quest items. Safe room operators offer rest and errands.
  Armory technicians tell you what they can fabricate and supply.

TOOL: collect()
  Collect items in your current cell (intel caches, quest materials).

TOOL: equip(item="item name")
  Acquire an item or fabricate equipment at the current armory.
  Fabrication requires the right materials + intel.

TOOL: use(item="item name")
  Use a consumable item: Ration (+1 health), Medkit (+2 health).

TOOL: engage()
  Engage the boss in your current cell. You need the right equipment
  or you'll lose 1 health and retreat. With the right equipment, you
  earn 3 intel and valuable loot.

TOOL: hide()
  Rest at a safe room. Costs 1 intel, restores 1 health (max 3).

TOOL: sitrep()
  Check your current health, intel, inventory, and position."""


# ---------------------------------------------------------------------------
# Tool call parser (provided complete)
# ---------------------------------------------------------------------------

def parse_tool_call(text: str) -> tuple[str, dict]:
    """Parse an LLM response to extract a tool call.

    Expected format: TOOL: tool_name(arg1="val1", arg2="val2")
    Falls back to scan() if parsing fails.

    Args:
        text: The raw text from the think function.

    Returns:
        Tuple of (tool_name, args_dict).
    """
    match = re.search(r'TOOL:\s*(\w+)\((.*?)\)', text, re.DOTALL)
    if not match:
        simple = re.search(r'TOOL:\s*(\w+)', text)
        if simple:
            return simple.group(1), {}
        return "scan", {}

    tool_name = match.group(1)
    args_str = match.group(2).strip()

    if not args_str:
        return tool_name, {}

    args = {}
    for kv_match in re.finditer(r'(\w+)\s*=\s*["\']([^"\']*)["\']', args_str):
        args[kv_match.group(1)] = kv_match.group(2)

    return tool_name, args


# ---------------------------------------------------------------------------
# Agent loop (provided complete)
# ---------------------------------------------------------------------------

def run_agent(
    think_fn: Callable,
    operative: OperativeState,
    world: FacilityWorld,
    tools: GameTools,
    max_turns: int = 100,
    display_fn: Optional[Callable] = None,
) -> dict:
    """Run the agent loop: perceive -> think -> act.

    Args:
        think_fn: Function(operative, world, history) -> str that returns a TOOL: call.
        operative: The operative instance.
        world: The facility world.
        tools: The game tools.
        max_turns: Maximum turns before the mission ends.
        display_fn: Optional function(world, operative, turn, action, result) for visualization.

    Returns:
        dict with keys: won, turns, intel, health, log_file.
    """
    history: list[dict[str, str]] = []
    game_log: list[dict] = []

    for turn in range(max_turns):
        if not operative.is_alive:
            game_log.append({
                "turn": turn, "event": "MISSION FAILED", "reason": "The operative has been eliminated.",
                "position": list(operative.position), "health": operative.health, "intel": operative.intel,
                "inventory": list(operative.inventory),
            })
            if display_fn:
                display_fn(world, operative, turn, "---", "MISSION FAILED: The operative has been eliminated.")
            break
        if operative.has_won:
            game_log.append({
                "turn": turn, "event": "MISSION COMPLETE", "reason": "Gathered enough intel!",
                "position": list(operative.position), "health": operative.health, "intel": operative.intel,
                "inventory": list(operative.inventory),
            })
            if display_fn:
                display_fn(world, operative, turn, "---", "MISSION COMPLETE: Intel objective achieved!")
            break

        # PERCEIVE: auto-scan each turn
        observation = tools.execute("scan", {}).message

        history.append({"role": "observation", "content": observation})

        # THINK: agent decides an action
        think_error = None
        try:
            action_text = think_fn(operative, world, history)
        except Exception as e:
            action_text = "TOOL: scan()"
            think_error = str(e)
            history.append({"role": "error", "content": f"Think function error: {e}"})

        # Parse the action
        tool_name, args = parse_tool_call(action_text)

        # ACT: execute the chosen tool
        result = tools.execute(tool_name, args)

        # Update history
        history.append({"role": "action", "content": f"{tool_name}({args})"})
        history.append({"role": "result", "content": result.message})

        # Log this turn
        log_entry = {
            "turn": turn,
            "position": list(operative.position),
            "health": operative.health,
            "intel": operative.intel,
            "inventory": list(operative.inventory),
            "observation": observation,
            "action": f"{tool_name}({args})",
            "result": result.message,
            "success": result.success,
        }
        if think_error:
            log_entry["think_error"] = think_error
        game_log.append(log_entry)

        if display_fn:
            display_fn(world, operative, turn, f"{tool_name}({args})", result.message)

    log_file = _save_game_log(game_log, operative)

    return {
        "won": operative.has_won,
        "turns": turn + 1 if 'turn' in dir() else 0,
        "intel": operative.intel,
        "health": operative.health,
        "log_file": log_file,
    }


def _save_game_log(game_log: list[dict], operative: OperativeState) -> str:
    """Save the game log to a JSON file and return the file path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outcome = "mission_complete" if operative.has_won else "mission_failed"
    log_file = f"game_log_{outcome}_{timestamp}.json"

    log_data = {
        "outcome": outcome,
        "final_intel": operative.intel,
        "final_health": operative.health,
        "final_inventory": list(operative.inventory),
        "total_turns": len([e for e in game_log if "action" in e]),
        "briefing_log": list(operative.briefing_log),
        "turns": game_log,
    }

    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)

    return log_file


# ---------------------------------------------------------------------------
# Phase 1: Rule-based think function (students implement this)
# ---------------------------------------------------------------------------

def think_rule_based(operative: OperativeState, world: FacilityWorld, history: list[dict]) -> str:
    """Decide the next action using rule-based if/else logic.

    TODO (Phase 1): Implement this function.

    This function receives:
    - operative: current state (health, intel, inventory, position, visited, briefing_log)
    - world: the facility world (you can call world.get_cell(), world.get_adjacent(), etc.)
    - history: list of dicts with keys "role" and "content" tracking observations,
      actions, and results from previous turns.

    It must return a string in the format:
        TOOL: tool_name(arg="value")

    Examples:
        'TOOL: move(direction="north")'
        'TOOL: collect()'
        'TOOL: codec(question="What dangers lie ahead?")'
        'TOOL: equip(item="EMP Device")'
        'TOOL: engage()'
        'TOOL: sitrep()'

    Strategy hints:
    - Use operative.position and operative.visited to navigate to unexplored cells.
    - Check the current cell type to decide: collect intel, contact NPCs, etc.
    - Prioritize: collect on intel cache > codec NPCs > move to unexplored cells.
    - The world has reinforced walls — you need to navigate around them.
    - You need 10 intel to win. Intel caches give 1 each, quests give more.

    Returns:
        str: A TOOL: call string.
    """
    # ========================
    # YOUR CODE HERE (Phase 1)
    # ========================
    raise NotImplementedError("TODO: Implement think_rule_based for Phase 1")


# ---------------------------------------------------------------------------
# Phase 2: LLM-powered think function (students implement this)
# ---------------------------------------------------------------------------

def think_llm(operative: OperativeState, world: FacilityWorld, history: list[dict], client) -> str:
    """Decide the next action using an LLM.

    TODO (Phase 2): Implement this function.

    Steps:
    1. Build a system message that includes:
       - The agent's role (you are an operative infiltrating a facility, goal is 10 intel)
       - The TOOLS_DESCRIPTION (so the LLM knows what tools are available)
       - Instructions to respond with exactly one TOOL: call

    2. Build a user message that includes:
       - Current operative status (use operative.status_text())
       - Recent history (last ~10 entries from the history list)
       - Current cell description
       - The operative's briefing log entries (key past codec conversations)

    3. Call client.models.generate_content() with:
       - model="gemini-2.5-flash"
       - contents=<your user message>
       - config=genai.types.GenerateContentConfig(
             system_instruction=<your system message>,
             max_output_tokens=500,
         )

    4. Return response.text

    Args:
        operative: Current operative state.
        world: The facility world.
        history: Conversation history from the game loop.
        client: A genai.Client() instance.

    Returns:
        str: The LLM's response containing a TOOL: call.
    """
    # ========================
    # YOUR CODE HERE (Phase 2)
    # ========================
    raise NotImplementedError("TODO: Implement think_llm for Phase 2")
