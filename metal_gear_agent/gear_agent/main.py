"""Game runner for Metal Gear Agent — convenience functions to wire everything together."""

from typing import Callable, Optional

from gear_agent.scenario import FacilityWorld
from gear_agent.game import OperativeState
from gear_agent.tools import GameTools
from gear_agent.oracle import stub_oracle
from gear_agent.agent import run_agent
from gear_agent.display import display_turn, display_final


def create_game() -> tuple[OperativeState, FacilityWorld, GameTools]:
    """Create a fresh game instance.

    Returns:
        Tuple of (operative, world, tools) ready to play.
    """
    world = FacilityWorld()
    operative = OperativeState()
    tools = GameTools(operative, world)
    return operative, world, tools


def play_rule_based(
    think_fn: Callable,
    max_turns: int = 100,
    show_display: bool = True,
    delay: float = 0.0,
) -> dict:
    """Run a game using a rule-based think function (Phase 1).

    The stub oracle is used for NPC interactions.

    Args:
        think_fn: Your rule-based think function(operative, world, history) -> str.
        max_turns: Maximum number of turns.
        show_display: Whether to show the visual display.
        delay: Seconds to pause between turns (for visualization).

    Returns:
        dict with keys: won, turns, intel, health.
    """
    operative, world, tools = create_game()
    tools.set_oracle(stub_oracle)

    disp = None
    if show_display:
        disp = lambda w, o, t, a, r: display_turn(w, o, t, a, r, delay=delay)

    result = run_agent(think_fn, operative, world, tools, max_turns, display_fn=disp)

    if show_display:
        display_final(operative, result["turns"])

    return result


def play_with_llm(
    think_fn: Callable,
    oracle_fn: Callable,
    max_turns: int = 100,
    show_display: bool = True,
    delay: float = 0.0,
) -> dict:
    """Run a game using an LLM-powered think function (Phase 2).

    Args:
        think_fn: Your LLM think function(operative, world, history) -> str.
        oracle_fn: Your oracle function(npc, question, operative) -> str.
        max_turns: Maximum number of turns.
        show_display: Whether to show the visual display.
        delay: Seconds to pause between turns (for visualization).

    Returns:
        dict with keys: won, turns, intel, health.
    """
    operative, world, tools = create_game()
    tools.set_oracle(oracle_fn)

    disp = None
    if show_display:
        disp = lambda w, o, t, a, r: display_turn(w, o, t, a, r, delay=delay)

    result = run_agent(think_fn, operative, world, tools, max_turns, display_fn=disp)

    if show_display:
        display_final(operative, result["turns"])

    return result
