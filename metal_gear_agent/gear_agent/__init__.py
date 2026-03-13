"""Metal Gear Agent: A Stealth-Ops Agentic AI Exercise."""

from gear_agent.data import (
    CellType,
    Item,
    NPC,
    Cell,
    NPC_CATALOG,
    ARMORY_CATALOG,
    ITEM_CATALOG,
)
from gear_agent.game import OperativeState
from gear_agent.scenario import FacilityWorld
from gear_agent.tools import ToolResult, GameTools
from gear_agent.oracle import stub_oracle, llm_oracle, ORACLE_TEMPLATE
from gear_agent.agent import (
    TOOLS_DESCRIPTION,
    parse_tool_call,
    run_agent,
)
from gear_agent.display import render_grid, display_turn, display_final
from gear_agent.main import create_game, play_rule_based, play_with_llm
try:
    from gear_agent.interactive import play_interactive
except ImportError:
    pass
