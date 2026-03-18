"""Agent loop for The Supply Line."""

import json
import re
from datetime import datetime
from typing import Callable, Optional

from supply_line.game import AgentState, SupplyWorld
from supply_line.tools import SupplyTools, ToolResult


# ---------------------------------------------------------------------------
# Tool descriptions (provided to the LLM)
# ---------------------------------------------------------------------------

TOOLS_DESCRIPTION = """Available tools (use exactly one per turn):

ACTION: check_orders()
  See the current order queue with priorities. Free action.

ACTION: read_order(order_id="T-001")
  Open a specific order to read its details. If no ID given, opens the
  highest priority unread order.

ACTION: lookup_kb(query="reorder procedures")
  Search the knowledge base for procedures and policies. ALWAYS do this
  before handling unfamiliar order types.

ACTION: check_inventory(sku="SKU-4421")
  Check current inventory levels for a SKU.

ACTION: lookup_shipment(shipment_id="SH-1190")
  Get shipment status and tracking information.

ACTION: lookup_contract(supplier="SteelWorks")
  Get contract terms and pricing for a supplier.

ACTION: check_documentation(shipment_id="SH-1190")
  Check what customs documents are on file for a shipment.

ACTION: check_alternatives()
  Find alternative suppliers or carriers.

ACTION: place_order(supplier="SteelWorks GmbH", sku="SKU-4421", quantity="50", expedited="false")
  Place a purchase order. Set expedited="true" for rush orders.
  WARNING: Ordering from blacklisted suppliers costs tokens!

ACTION: reject_shipment(shipment_id="SH-3301", reason="QC failure")
  Reject a shipment that failed quality control.

ACTION: file_claim(supplier="ChemPure AG", amount="25000")
  File a monetary claim against a supplier.

ACTION: submit_documents(shipment_id="SH-1190", doc_type="certificate_of_origin")
  Submit customs documentation for a held shipment.

ACTION: update_timeline(order_id="T-007", new_eta="5 business days")
  Update the delivery timeline for a delayed shipment.

ACTION: verify_pricing(order_id="PO-8812")
  Verify pricing against contract terms.

ACTION: compile_records(period="30_days")
  Compile import records for compliance audit.

ACTION: acknowledge_alert(alert_id="T-004")
  Acknowledge and close a system alert.

ACTION: notify_client(template="reorder_confirmation")
  Send notification using a template. Available: reorder_confirmation,
  delay_notification, quality_issue, customs_update, rush_confirmation,
  launch_status, compliance_status, dispute_resolution, general_update.

ACTION: escalate(department="procurement", reason="pricing discrepancy")
  Escalate to a department: procurement, finance, logistics, engineering,
  compliance. WARNING: Wrong or unnecessary escalations cost tokens!

ACTION: prepare_launch_briefing()
  Compile the Project Aurora launch readiness briefing. Requires all
  prerequisite orders (T-005, T-008, T-012) to be resolved first.

ACTION: authorize_launch(order_id="T-001")
  Authorize the Project Aurora launch. Requires briefing to be prepared first.

ACTION: prepare_compliance_package()
  Compile the STA regulatory compliance package. Requires prerequisite
  orders (T-006, T-009, T-016) to be resolved first.

ACTION: submit_compliance(order_id="T-020")
  Submit compliance package to Swiss Trade Authority. Requires package
  to be prepared first.

ACTION: close_order(order_id="T-001")
  Mark an order as fulfilled. Scores your handling quality.
  Make sure you've done everything needed BEFORE closing!

ACTION: check_stats()
  Check your performance stats. Free action.

ACTION: take_break()
  Recover 1 operations token. Costs 5 turns."""


# ---------------------------------------------------------------------------
# Action parser
# ---------------------------------------------------------------------------

def parse_action(text: str) -> tuple[str, dict]:
    """Parse an agent response to extract an action call."""
    match = re.search(r'ACTION:\s*(\w+)\((.*?)\)', text, re.DOTALL)
    if not match:
        simple = re.search(r'ACTION:\s*(\w+)', text)
        if simple:
            return simple.group(1), {}
        return "check_orders", {}

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
    agent: AgentState,
    world: SupplyWorld,
    tools: SupplyTools,
    max_turns: int = 100,
    display_fn: Optional[Callable] = None,
) -> dict:
    """Run the agent loop: perceive -> think -> act."""
    history: list[dict[str, str]] = []
    game_log: list[dict] = []

    for turn in range(max_turns):
        if not agent.is_alive:
            game_log.append({
                "turn": turn, "event": "GAME OVER",
                "reason": "Out of operations tokens.",
            })
            if display_fn:
                display_fn(world, agent, turn, "---",
                           "GAME OVER: Too many violations. Management has stepped in.")
            break

        if agent.has_won:
            game_log.append({
                "turn": turn, "event": "VICTORY",
                "reason": "Met all targets!",
            })
            if display_fn:
                display_fn(world, agent, turn, "---",
                           "VICTORY: All fulfillment targets met!")
            break

        # Add time-gated orders
        new_orders = world.add_late_orders(turn)
        if new_orders:
            names = ", ".join(o.id for o in new_orders)
            history.append({
                "role": "system",
                "content": f"New orders arrived: {names}"
            })

        # PERCEIVE
        observation = tools.check_orders().message
        if world.active_order:
            observation += f"\n\nActive order: {world.active_order.id} — {world.active_order.subject}"
        history.append({"role": "observation", "content": observation})

        # THINK
        think_error = None
        try:
            action_text = think_fn(agent, world, history)
        except Exception as e:
            action_text = "ACTION: check_orders()"
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
            "tokens": agent.operations_tokens,
            "resolved": agent.resolved_count,
            "quality": round(agent.quality_score, 1),
            "queue_size": len(world.queue),
            "action": action_display,
            "result": result.message,
            "success": result.success,
        }
        if think_error:
            log_entry["think_error"] = think_error
        game_log.append(log_entry)

        # Display
        if display_fn:
            display_fn(world, agent, turn, action_display, result.message)

    # Save log
    log_file = _save_game_log(game_log, agent)

    return {
        "won": agent.has_won,
        "turns": turn + 1 if 'turn' in dir() else 0,
        "resolved": agent.resolved_count,
        "quality": round(agent.quality_score, 1),
        "tokens": agent.operations_tokens,
        "log_file": log_file,
    }


def _save_game_log(game_log: list[dict], agent: AgentState) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outcome = "victory" if agent.has_won else "defeat"
    log_file = f"supply_log_{outcome}_{timestamp}.json"

    log_data = {
        "outcome": outcome,
        "final_resolved": agent.resolved_count,
        "final_quality": round(agent.quality_score, 1),
        "final_tokens": agent.operations_tokens,
        "notes": list(agent.notes),
        "turns": game_log,
    }

    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)

    return log_file


# ---------------------------------------------------------------------------
# Think function stubs
# ---------------------------------------------------------------------------

def think_llm(agent: AgentState, world: SupplyWorld, history: list[dict]) -> str:
    """Decide the next action using an LLM.

    TODO: Implement this function.
    """
    raise NotImplementedError("TODO: Implement think_llm")
