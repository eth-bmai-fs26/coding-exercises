"""Game runner for Fridge Chef."""

from typing import Callable, Optional

from fridge_chef.data import ChefState
from fridge_chef.game import KitchenWorld
from fridge_chef.tools import KitchenTools
from fridge_chef.agent import run_agent
from fridge_chef.display import display_turn, display_final


def create_game() -> tuple[ChefState, KitchenWorld, KitchenTools]:
    """Create a fresh game instance."""
    world = KitchenWorld()
    chef = ChefState()
    tools = KitchenTools(chef, world)
    return chef, world, tools


def play_rule_based(
    think_fn: Callable,
    user_request: str = "I want something comforting for a cold evening",
    max_turns: int = 20,
    show_display: bool = True,
    delay: float = 0.0,
) -> dict:
    """Run a game using a rule-based think function."""
    chef, world, tools = create_game()

    disp = None
    if show_display:
        disp = lambda w, c, t, act, res: display_turn(w, c, t, act, res, delay=delay)

    result = run_agent(think_fn, chef, world, tools, max_turns,
                       display_fn=disp, user_request=user_request)

    if show_display:
        display_final(chef, result["turns"])

    return result


def play_with_llm(
    think_fn: Callable,
    user_request: str = "I want something comforting for a cold evening",
    max_turns: int = 20,
    show_display: bool = True,
    delay: float = 0.0,
) -> dict:
    """Run a game using an LLM-powered think function."""
    chef, world, tools = create_game()

    disp = None
    if show_display:
        disp = lambda w, c, t, act, res: display_turn(w, c, t, act, res, delay=delay)

    result = run_agent(think_fn, chef, world, tools, max_turns,
                       display_fn=disp, user_request=user_request)

    if show_display:
        display_final(chef, result["turns"])

    return result
