"""The Support Desk: An Agentic AI Exercise for Business Professionals."""

from support_desk.data import (
    Customer, Ticket, KBArticle, Template,
    TicketCategory, TicketPriority, TicketStatus, AccountTier, Team,
)
from support_desk.game import AgentState, SupportWorld
from support_desk.tools import SupportTools, ToolResult
from support_desk.agent import (
    TOOLS_DESCRIPTION, parse_action, run_agent,
)
from support_desk.display import display_turn, display_final
from support_desk.main import create_game, play_rule_based, play_with_llm

def play_interactive():
    """Launch an interactive support desk session (requires IPython/Colab)."""
    from support_desk.interactive import play_interactive as _play
    return _play()
