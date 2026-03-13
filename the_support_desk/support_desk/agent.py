"""Agent loop for The Support Desk."""

import json
import re
from datetime import datetime
from typing import Callable, Optional

from support_desk.game import AgentState, SupportWorld
from support_desk.tools import SupportTools, ToolResult


# ---------------------------------------------------------------------------
# Tool descriptions (provided to the LLM)
# ---------------------------------------------------------------------------

TOOLS_DESCRIPTION = """Available tools (use exactly one per turn):

ACTION: check_queue()
  See the current ticket queue with priorities and subjects. Free action.

ACTION: open_ticket(ticket_id="T-001")
  Open a specific ticket to read its details. If no ID given, opens the
  highest priority unread ticket.

ACTION: lookup(query="billing duplicate charge")
  Search the knowledge base and CRM for information. ALWAYS do this before
  resolving billing issues, technical problems, or unfamiliar topics.

ACTION: reply(ticket_id="T-001", message="Your message here")
  Send a response to the customer. If no ticket_id, uses the active ticket.

ACTION: apply_action(ticket_id="T-001", action="reset_password")
  Apply a specific fix. Available actions: reset_password, issue_refund,
  close_spam, adjust_rate_limit, update_billing_profile, update_known_bugs,
  reply_vip_confirmation, confirm_rate_fix.

ACTION: escalate(ticket_id="T-001", team="engineering")
  Escalate to a specialist team: billing, engineering, account_management,
  legal, security. WARNING: Wrong or unnecessary escalations cost tokens!

ACTION: use_template(ticket_id="T-001", template="password_reset")
  Apply a canned response template. Available: password_reset, export_guide,
  known_bug_eta, feature_request_logged, sso_guide, escalation_ack,
  refund_confirmation, spam_close.

ACTION: prepare_briefing(ticket_id="T-007")
  Prepare a VIP Account Briefing for high-value escalation tickets. Compiles
  evidence from related resolved tickets. Required before escalating VIP
  retention cases. Will fail if prerequisite tickets haven't been resolved yet.

ACTION: resolve_ticket(ticket_id="T-001")
  Mark a ticket as resolved. Scores your handling quality (CSAT).
  Make sure you've done everything needed BEFORE resolving!

ACTION: check_stats()
  Check your performance stats. Free action.

ACTION: take_break()
  Recover 1 escalation token. Costs 5 turns of shift time."""


# ---------------------------------------------------------------------------
# Action parser
# ---------------------------------------------------------------------------

def parse_action(text: str) -> tuple[str, dict]:
    """Parse an agent response to extract an action call.

    Expected format: ACTION: tool_name(arg1="val1", arg2="val2")
    Falls back to check_queue() if parsing fails.
    """
    match = re.search(r'ACTION:\s*(\w+)\((.*?)\)', text, re.DOTALL)
    if not match:
        simple = re.search(r'ACTION:\s*(\w+)', text)
        if simple:
            return simple.group(1), {}
        return "check_queue", {}

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
    world: SupportWorld,
    tools: SupportTools,
    max_turns: int = 100,
    display_fn: Optional[Callable] = None,
) -> dict:
    """Run the agent loop: perceive -> think -> act.

    Args:
        think_fn: Function(agent, world, history) -> str that returns an ACTION: call.
        agent: The agent state.
        world: The support world.
        tools: The support tools.
        max_turns: Maximum turns before shift ends.
        display_fn: Optional display callback.

    Returns:
        dict with keys: won, turns, resolved, csat, tokens, log_file.
    """
    history: list[dict[str, str]] = []
    game_log: list[dict] = []

    for turn in range(max_turns):
        # Check end conditions
        if not agent.is_alive:
            game_log.append({
                "turn": turn, "event": "GAME OVER",
                "reason": "Out of escalation tokens.",
            })
            if display_fn:
                display_fn(world, agent, turn, "---",
                           "GAME OVER: Too many bad escalations. Manager has stepped in.")
            break

        if agent.has_won:
            game_log.append({
                "turn": turn, "event": "VICTORY",
                "reason": "Met all targets!",
            })
            if display_fn:
                display_fn(world, agent, turn, "---",
                           "VICTORY: Shift complete with all targets met!")
            break

        # Add time-gated tickets
        new_tickets = world.add_late_tickets(turn)
        if new_tickets:
            names = ", ".join(t.id for t in new_tickets)
            history.append({
                "role": "system",
                "content": f"New tickets arrived: {names}"
            })

        # PERCEIVE: queue overview
        observation = tools.check_queue().message
        if world.active_ticket:
            observation += f"\n\nActive ticket: {world.active_ticket.id} — {world.active_ticket.subject}"
        history.append({"role": "observation", "content": observation})

        # THINK
        think_error = None
        try:
            action_text = think_fn(agent, world, history)
        except Exception as e:
            action_text = "ACTION: check_queue()"
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
            "tokens": agent.escalation_tokens,
            "resolved": agent.resolved_count,
            "csat": round(agent.csat_score, 1),
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
        "csat": round(agent.csat_score, 1),
        "tokens": agent.escalation_tokens,
        "log_file": log_file,
    }


def _save_game_log(game_log: list[dict], agent: AgentState) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outcome = "victory" if agent.has_won else "defeat"
    log_file = f"support_log_{outcome}_{timestamp}.json"

    log_data = {
        "outcome": outcome,
        "final_resolved": agent.resolved_count,
        "final_csat": round(agent.csat_score, 1),
        "final_tokens": agent.escalation_tokens,
        "notes": list(agent.notes),
        "turns": game_log,
    }

    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)

    return log_file


# ---------------------------------------------------------------------------
# Think function stubs (students implement these)
# ---------------------------------------------------------------------------

def think_rule_based(agent: AgentState, world: SupportWorld, history: list[dict]) -> str:
    """Decide the next action using rule-based logic.

    TODO: Implement this function.

    Args:
        agent: Current agent state (tokens, resolved count, CSAT).
        world: The support world (queue, tickets, KB, customers).
        history: List of dicts with observations, actions, results.

    Returns:
        str: An ACTION: call string.
    """
    raise NotImplementedError("TODO: Implement think_rule_based")


def think_llm(agent: AgentState, world: SupportWorld, history: list[dict]) -> str:
    """Decide the next action using an LLM.

    TODO: Implement this function.

    Args:
        agent: Current agent state.
        world: The support world.
        history: Conversation history.

    Returns:
        str: An ACTION: call string.
    """
    raise NotImplementedError("TODO: Implement think_llm")
