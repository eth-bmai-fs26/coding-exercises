"""The Supply Line: An Agentic AI Exercise for Business Professionals."""

from supply_line.data import (
    Entity, Order, KBArticle, Template,
    OrderCategory, OrderPriority, OrderStatus, EntityTier, Department,
)
from supply_line.game import AgentState, SupplyWorld
from supply_line.tools import SupplyTools, ToolResult
from supply_line.agent import (
    TOOLS_DESCRIPTION, parse_action, run_agent,
)
from supply_line.display import display_turn, display_final
from supply_line.main import create_game, play_with_llm

def play_interactive():
    """Launch an interactive supply line session (requires IPython/Colab)."""
    from supply_line.interactive import play_interactive as _play
    return _play()
