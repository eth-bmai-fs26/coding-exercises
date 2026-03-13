"""Fridge Chef: An Agentic AI Exercise for Business Professionals."""

from fridge_chef.data import ChefState
from fridge_chef.game import KitchenWorld
from fridge_chef.tools import KitchenTools, ToolResult
from fridge_chef.agent import (
    TOOLS_DESCRIPTION, parse_action, run_agent,
)
from fridge_chef.display import display_turn, display_final
from fridge_chef.main import create_game, play_rule_based, play_with_llm


def play_interactive():
    """Launch an interactive Fridge Chef session (requires IPython/Colab)."""
    from fridge_chef.interactive import play_interactive as _play
    return _play()
