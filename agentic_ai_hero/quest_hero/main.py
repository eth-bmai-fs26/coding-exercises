"""Game runner for Quest Hero — convenience functions to wire everything together."""

from typing import Callable, Optional

from quest_hero.game_world import GameWorld
from quest_hero.hero import Hero
from quest_hero.tools import GameTools
from quest_hero.oracle import stub_oracle
from quest_hero.agent import run_agent
from quest_hero.display import display_turn, display_final


def create_game() -> tuple[Hero, GameWorld, GameTools]:
    """Create a fresh game instance.

    Returns:
        Tuple of (hero, world, tools) ready to play.
    """
    world = GameWorld()
    hero = Hero()
    tools = GameTools(hero, world)
    return hero, world, tools


def play_rule_based(
    think_fn: Callable,
    max_turns: int = 100,
    show_display: bool = True,
    delay: float = 0.0,
) -> dict:
    """Run a game using a rule-based think function (Phase 1).

    The stub oracle is used for NPC interactions.

    Args:
        think_fn: Your rule-based think function(hero, world, history) -> str.
        max_turns: Maximum number of turns.
        show_display: Whether to show the visual display.
        delay: Seconds to pause between turns (for visualization).

    Returns:
        dict with keys: won, turns, gold, hearts.
    """
    hero, world, tools = create_game()
    tools.set_oracle(stub_oracle)

    disp = None
    if show_display:
        disp = lambda w, h, t, a, r: display_turn(w, h, t, a, r, delay=delay)

    result = run_agent(think_fn, hero, world, tools, max_turns, display_fn=disp)

    if show_display:
        display_final(hero, result["turns"])

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
        think_fn: Your LLM think function(hero, world, history) -> str.
        oracle_fn: Your oracle function(npc, question, hero) -> str.
        max_turns: Maximum number of turns.
        show_display: Whether to show the visual display.
        delay: Seconds to pause between turns (for visualization).

    Returns:
        dict with keys: won, turns, gold, hearts.
    """
    hero, world, tools = create_game()
    tools.set_oracle(oracle_fn)

    disp = None
    if show_display:
        disp = lambda w, h, t, a, r: display_turn(w, h, t, a, r, delay=delay)

    result = run_agent(think_fn, hero, world, tools, max_turns, display_fn=disp)

    if show_display:
        display_final(hero, result["turns"])

    return result
