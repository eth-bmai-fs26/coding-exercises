"""Agent loop for Fridge Chef."""

import json
import re
from datetime import datetime
from typing import Callable, Optional

from fridge_chef.data import ChefState
from fridge_chef.game import KitchenWorld
from fridge_chef.tools import KitchenTools, ToolResult


# ---------------------------------------------------------------------------
# Tool descriptions (provided to the LLM)
# ---------------------------------------------------------------------------

TOOLS_DESCRIPTION = """Available tools (use exactly one per turn):

ACTION: check_fridge()
  See what ingredients are currently in your fridge.

ACTION: search_recipes(ingredient="eggs")
  Search for recipes that use a specific ingredient from your fridge.

ACTION: get_ingredients(recipe="omelette")
  Get the full ingredient list for a recipe. This also sets it as your
  chosen recipe. Compare against your fridge to see what's missing.

ACTION: add_to_shopping_list(item="paprika")
  Add a missing ingredient to your shopping list. Only add items you
  don't already have in the fridge.

ACTION: done()
  Signal that you're finished — recipe chosen and shopping list ready.
  Make sure you've chosen a recipe with get_ingredients() first!"""


# ---------------------------------------------------------------------------
# Action parser
# ---------------------------------------------------------------------------

def parse_action(text: str) -> tuple[str, dict]:
    """Parse an agent response to extract an action call.

    Expected format: ACTION: tool_name(arg1="val1", arg2="val2")
    Falls back to check_fridge() if parsing fails.
    """
    match = re.search(r'ACTION:\s*(\w+)\((.*?)\)', text, re.DOTALL)
    if not match:
        simple = re.search(r'ACTION:\s*(\w+)', text)
        if simple:
            return simple.group(1), {}
        return "check_fridge", {}

    tool_name = match.group(1)
    args_str = match.group(2).strip()

    if not args_str:
        return tool_name, {}

    args = {}
    for kv_match in re.finditer(r'(\w+)\s*=\s*["\']([^"\']*)["\']', args_str):
        args[kv_match.group(1)] = kv_match.group(2)

    return tool_name, args


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

def run_agent(
    think_fn: Callable,
    chef: ChefState,
    world: KitchenWorld,
    tools: KitchenTools,
    max_turns: int = 20,
    display_fn: Optional[Callable] = None,
    user_request: str = "I want something comforting for a cold evening",
) -> dict:
    """Run the agent loop: perceive -> think -> act.

    Args:
        think_fn: Function(chef, world, history, user_request) -> str that returns an ACTION: call.
        chef: The chef state.
        world: The kitchen world.
        tools: The kitchen tools.
        max_turns: Maximum turns before timeout.
        display_fn: Optional display callback.
        user_request: What the user wants to cook.

    Returns:
        dict with keys: completed, turns, recipe, shopping_list, log_file.
    """
    history: list[dict[str, str]] = []
    game_log: list[dict] = []

    for turn in range(max_turns):
        # Check end condition
        if chef.is_complete:
            game_log.append({
                "turn": turn, "event": "COMPLETE",
                "reason": f"Recipe chosen: {chef.chosen_recipe}",
            })
            if display_fn:
                display_fn(world, chef, turn, "---",
                           f"COMPLETE: Ready to cook {chef.chosen_recipe}!")
            break

        # PERCEIVE: current state overview
        observation = f"User request: {user_request}\n{chef.status_text()}"
        history.append({"role": "observation", "content": observation})

        # THINK
        think_error = None
        try:
            action_text = think_fn(chef, world, history, user_request)
        except Exception as e:
            action_text = "ACTION: check_fridge()"
            think_error = str(e)
            history.append({"role": "error", "content": f"Think error: {e}"})

        # Parse
        tool_name, args = parse_action(action_text)

        # ACT
        result = tools.execute(tool_name, args)

        # Update history
        args_str = ", ".join(f'{k}="{v}"' for k, v in args.items())
        action_display = f"{tool_name}({args_str})"
        history.append({"role": "action", "content": action_display})
        history.append({
            "role": "result",
            "content": result.message,
            "success": result.success,
        })

        # Log
        log_entry = {
            "turn": turn,
            "recipe": chef.chosen_recipe,
            "shopping_list": list(chef.shopping_list),
            "action": action_display,
            "result": result.message,
            "success": result.success,
        }
        if think_error:
            log_entry["think_error"] = think_error
        game_log.append(log_entry)

        # Display
        if display_fn:
            display_fn(world, chef, turn, action_display, result.message)

    # Save log
    log_file = _save_game_log(game_log, chef, user_request)

    return {
        "completed": chef.is_complete,
        "turns": turn + 1 if 'turn' in dir() else 0,
        "recipe": chef.chosen_recipe,
        "shopping_list": list(chef.shopping_list),
        "log_file": log_file,
    }


def _save_game_log(game_log: list[dict], chef: ChefState, user_request: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outcome = "complete" if chef.is_complete else "timeout"
    log_file = f"kitchen_log_{outcome}_{timestamp}.json"

    log_data = {
        "outcome": outcome,
        "user_request": user_request,
        "final_recipe": chef.chosen_recipe,
        "final_shopping_list": list(chef.shopping_list),
        "notes": list(chef.notes),
        "turns": game_log,
    }

    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)

    return log_file


# ---------------------------------------------------------------------------
# Think function stubs (students implement these)
# ---------------------------------------------------------------------------

def think_rule_based(chef: ChefState, world: KitchenWorld, history: list[dict], user_request: str) -> str:
    """Decide the next action using rule-based logic.

    TODO: Implement this function.

    Args:
        chef: Current chef state (fridge contents, recipe, shopping list).
        world: The kitchen world (fridge, recipe DB, ingredients DB).
        history: List of dicts with observations, actions, results.
        user_request: What the user wants to cook.

    Returns:
        str: An ACTION: call string.
    """
    raise NotImplementedError("TODO: Implement think_rule_based")


def think_llm(chef: ChefState, world: KitchenWorld, history: list[dict], user_request: str) -> str:
    """Decide the next action using an LLM.

    TODO: Implement this function.

    Args:
        chef: Current chef state.
        world: The kitchen world.
        history: Conversation history.
        user_request: What the user wants to cook.

    Returns:
        str: An ACTION: call string.
    """
    raise NotImplementedError("TODO: Implement think_llm")
