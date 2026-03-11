"""Agent loop and think function for Quest Hero.

Students implement:
- think_rule_based() in Phase 1
- think_llm() in Phase 2

Everything else is provided.
"""

import re
from typing import Callable, Optional

from quest_hero.hero import Hero
from quest_hero.game_world import GameWorld
from quest_hero.tools import GameTools, ToolResult


# ---------------------------------------------------------------------------
# Tool descriptions (provided to the LLM in Phase 2)
# ---------------------------------------------------------------------------

TOOLS_DESCRIPTION = """Available tools (use exactly one per turn):

TOOL: look()
  See the types of adjacent cells (north/south/east/west). Free action.

TOOL: move(direction="north|south|east|west")
  Move one step in a cardinal direction. Triggers cell events on arrival.
  Mountains are impassable. Moving into a forest may trigger a trap.

TOOL: talk(question="your question here")
  Talk to an NPC, innkeeper, or shopkeeper in your current cell.
  NPCs give hints and quest items. Innkeepers offer rest and errands.
  Shopkeepers tell you what they sell and craft.

TOOL: pick_up()
  Pick up items in your current cell (treasures, quest materials).

TOOL: buy(item="item name")
  Buy an item or craft a weapon at the current shop.
  Crafting requires the right materials + gold.

TOOL: use(item="item name")
  Use a consumable item: Bread (+1 heart), Health Potion (+2 hearts).

TOOL: fight()
  Fight the monster in your current cell. You need the right weapon
  or you'll lose 1 heart and retreat. With the right weapon, you win
  3 gold and Dragon Scales.

TOOL: rest()
  Rest at an inn. Costs 1 gold, restores 1 heart (max 3).

TOOL: status()
  Check your current hearts, gold, inventory, and position."""


# ---------------------------------------------------------------------------
# Tool call parser (provided complete)
# ---------------------------------------------------------------------------

def parse_tool_call(text: str) -> tuple[str, dict]:
    """Parse an LLM response to extract a tool call.

    Expected format: TOOL: tool_name(arg1="val1", arg2="val2")
    Falls back to look() if parsing fails.

    Args:
        text: The raw text from the think function.

    Returns:
        Tuple of (tool_name, args_dict).
    """
    # Try to find TOOL: pattern
    match = re.search(r'TOOL:\s*(\w+)\((.*?)\)', text, re.DOTALL)
    if not match:
        # Fallback: look for just a tool name
        simple = re.search(r'TOOL:\s*(\w+)', text)
        if simple:
            return simple.group(1), {}
        return "look", {}

    tool_name = match.group(1)
    args_str = match.group(2).strip()

    if not args_str:
        return tool_name, {}

    # Parse keyword arguments: key="value" or key='value'
    args = {}
    for kv_match in re.finditer(r'(\w+)\s*=\s*["\']([^"\']*)["\']', args_str):
        args[kv_match.group(1)] = kv_match.group(2)

    return tool_name, args


# ---------------------------------------------------------------------------
# Agent loop (provided complete)
# ---------------------------------------------------------------------------

def run_agent(
    think_fn: Callable,
    hero: Hero,
    world: GameWorld,
    tools: GameTools,
    max_turns: int = 100,
    display_fn: Optional[Callable] = None,
) -> dict:
    """Run the agent loop: perceive -> think -> act.

    Args:
        think_fn: Function(hero, world, history) -> str that returns a TOOL: call.
        hero: The hero instance.
        world: The game world.
        tools: The game tools.
        max_turns: Maximum turns before the game ends.
        display_fn: Optional function(world, hero, turn, action, result) for visualization.

    Returns:
        dict with keys: won (bool), turns (int), gold (int), hearts (int).
    """
    history: list[dict[str, str]] = []

    for turn in range(max_turns):
        # Check end conditions
        if not hero.is_alive:
            if display_fn:
                display_fn(world, hero, turn, "---", "GAME OVER: The hero has fallen.")
            break
        if hero.has_won:
            if display_fn:
                display_fn(world, hero, turn, "---", "VICTORY: The hero has collected enough gold!")
            break

        # PERCEIVE: auto-look each turn
        observation = tools.execute("look", {}).message

        # Build context for the think function
        history.append({"role": "observation", "content": observation})

        # THINK: agent decides an action
        try:
            action_text = think_fn(hero, world, history)
        except Exception as e:
            action_text = "TOOL: look()"
            history.append({"role": "error", "content": f"Think function error: {e}"})

        # Parse the action
        tool_name, args = parse_tool_call(action_text)

        # ACT: execute the chosen tool
        result = tools.execute(tool_name, args)

        # Update history
        history.append({"role": "action", "content": f"{tool_name}({args})"})
        history.append({"role": "result", "content": result.message})

        # Display
        if display_fn:
            display_fn(world, hero, turn, f"{tool_name}({args})", result.message)

    return {
        "won": hero.has_won,
        "turns": turn + 1 if 'turn' in dir() else 0,
        "gold": hero.gold,
        "hearts": hero.hearts,
    }


# ---------------------------------------------------------------------------
# Phase 1: Rule-based think function (students implement this)
# ---------------------------------------------------------------------------

def think_rule_based(hero: Hero, world: GameWorld, history: list[dict]) -> str:
    """Decide the next action using rule-based if/else logic.

    TODO (Phase 1): Implement this function.

    This function receives:
    - hero: current hero state (hearts, gold, inventory, position, visited, journal)
    - world: the game world (you can call world.get_cell(), world.get_adjacent(), etc.)
    - history: list of dicts with keys "role" and "content" tracking observations,
      actions, and results from previous turns.

    It must return a string in the format:
        TOOL: tool_name(arg="value")

    Examples:
        'TOOL: move(direction="north")'
        'TOOL: pick_up()'
        'TOOL: talk(question="What dangers lie ahead?")'
        'TOOL: buy(item="Sunblade")'
        'TOOL: fight()'
        'TOOL: status()'

    Strategy hints:
    - Use hero.position and hero.visited to navigate to unexplored cells.
    - Check the current cell type to decide: pick up treasures, talk to NPCs, etc.
    - Prioritize: pick_up on treasure > talk to NPCs > move to unexplored cells.
    - The world has mountains — you need to navigate around them.
    - You need 10 gold to win. Treasures give 1 gold each, quests give more.

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

def think_llm(hero: Hero, world: GameWorld, history: list[dict], client) -> str:
    """Decide the next action using an LLM.

    TODO (Phase 2): Implement this function.

    Steps:
    1. Build a system message that includes:
       - The agent's role (you are a hero in an RPG, goal is 10 gold)
       - The TOOLS_DESCRIPTION (so the LLM knows what tools are available)
       - Instructions to respond with exactly one TOOL: call

    2. Build a user message that includes:
       - Current hero status (use hero.status_text())
       - Recent history (last ~10 entries from the history list)
       - Current cell description
       - The hero's journal entries (key past NPC conversations)

    3. Call client.models.generate_content() with:
       - model="gemini-2.0-flash"
       - contents=<your user message>
       - config=genai.types.GenerateContentConfig(
             system_instruction=<your system message>,
             max_output_tokens=500,
         )

    4. Return response.text

    Args:
        hero: Current hero state.
        world: The game world.
        history: Conversation history from the game loop.
        client: A genai.Client() instance.

    Returns:
        str: The LLM's response containing a TOOL: call.
    """
    # ========================
    # YOUR CODE HERE (Phase 2)
    # ========================
    raise NotImplementedError("TODO: Implement think_llm for Phase 2")
