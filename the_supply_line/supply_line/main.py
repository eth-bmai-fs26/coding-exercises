"""Game runner for The Supply Line."""

from typing import Callable, Optional

from supply_line.game import AgentState, SupplyWorld
from supply_line.tools import SupplyTools
from supply_line.agent import run_agent
from supply_line.display import display_turn, display_final


def create_game() -> tuple[AgentState, SupplyWorld, SupplyTools]:
    """Create a fresh game instance."""
    world = SupplyWorld()
    agent = AgentState()
    tools = SupplyTools(agent, world)
    return agent, world, tools


def play_rule_based(
    think_fn: Callable,
    max_turns: int = 100,
    show_display: bool = True,
    delay: float = 0.0,
) -> dict:
    """Run a game using a rule-based think function."""
    agent, world, tools = create_game()

    disp = None
    if show_display:
        disp = lambda w, a, t, act, res: display_turn(w, a, t, act, res, delay=delay)

    result = run_agent(think_fn, agent, world, tools, max_turns, display_fn=disp)

    if show_display:
        display_final(agent, result["turns"])

    return result


def play_with_llm(
    think_fn: Callable,
    max_turns: int = 100,
    show_display: bool = True,
    delay: float = 0.0,
) -> dict:
    """Run a game using an LLM-powered think function."""
    agent, world, tools = create_game()

    disp = None
    if show_display:
        disp = lambda w, a, t, act, res: display_turn(w, a, t, act, res, delay=delay)

    result = run_agent(think_fn, agent, world, tools, max_turns, display_fn=disp)

    if show_display:
        display_final(agent, result["turns"])

    return result
