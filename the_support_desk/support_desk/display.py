"""Display utilities for The Support Desk — office-themed visualization."""

import time
from typing import Optional

from support_desk.data import TicketPriority, TicketStatus, TicketCategory
from support_desk.game import AgentState, SupportWorld


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _render_tokens_bar(agent: AgentState) -> str:
    full = '<span style="color:#16c79a;font-size:20px;">\U0001f4aa</span>'
    empty = '<span style="color:#333;font-size:20px;">\U0001f4aa</span>'
    return (full + " ") * agent.escalation_tokens + (empty + " ") * (agent.MAX_TOKENS - agent.escalation_tokens)


def _render_csat_bar(agent: AgentState) -> str:
    score = agent.csat_score
    pct = min(100, int(score))
    color = "#16c79a" if score >= 80 else "#e9a045" if score >= 60 else "#e94560"
    glow = "box-shadow:0 0 10px #16c79a;" if score >= 80 else ""
    return (
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="font-size:16px;">\u2b50</span>'
        f'<div style="flex:1;background:#1a1a2e;border-radius:10px;height:20px;border:1px solid #333;overflow:hidden;">'
        f'<div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#e94560,{color});'
        f'border-radius:10px;transition:width 0.5s;{glow}"></div>'
        f'</div>'
        f'<span style="color:{color};font-weight:bold;min-width:50px;">{score:.0f}%</span>'
        f'</div>'
    )


def _render_resolved_bar(agent: AgentState) -> str:
    pct = min(100, int(agent.resolved_count / agent.WIN_RESOLVED * 100))
    glow = "box-shadow:0 0 10px #16c79a;" if pct >= 100 else ""
    return (
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="font-size:16px;">\u2705</span>'
        f'<div style="flex:1;background:#1a1a2e;border-radius:10px;height:20px;border:1px solid #333;overflow:hidden;">'
        f'<div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#0f3460,#16c79a);'
        f'border-radius:10px;transition:width 0.5s;{glow}"></div>'
        f'</div>'
        f'<span style="color:#16c79a;font-weight:bold;min-width:60px;">{agent.resolved_count}/{agent.WIN_RESOLVED}</span>'
        f'</div>'
    )


def _render_turn_counter(turn: int, max_turns: int = 100) -> str:
    pct = min(100, int(turn / max_turns * 100))
    color = "#16c79a" if pct < 60 else "#e9a045" if pct < 80 else "#e94560"
    return (
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="font-size:14px;">\u23f1\ufe0f</span>'
        f'<div style="flex:1;background:#1a1a2e;border-radius:10px;height:14px;border:1px solid #333;overflow:hidden;">'
        f'<div style="width:{pct}%;height:100%;background:{color};border-radius:10px;"></div>'
        f'</div>'
        f'<span style="color:{color};font-size:13px;min-width:70px;">Turn {turn}/{max_turns}</span>'
        f'</div>'
    )


def _render_queue(world: SupportWorld) -> str:
    if not world.queue:
        return '<div style="color:#666;font-style:italic;padding:8px;">Queue empty</div>'

    rows = []
    for t in world.queue[:8]:
        customer = world.get_customer(t.customer_id)
        name = customer.name if customer else "Unknown"
        is_active = world.active_ticket and world.active_ticket.id == t.id
        bg = "#1a2a3e" if is_active else "#12122a"
        border = "border-left:3px solid #e94560;" if is_active else "border-left:3px solid transparent;"
        read_style = "color:#888;" if t.has_been_read else "color:#e0e0e0;font-weight:bold;"

        rows.append(
            f'<div style="padding:6px 8px;{border}background:{bg};margin:2px 0;border-radius:0 4px 4px 0;{read_style}font-size:12px;">'
            f'{t.priority.emoji} {t.category.emoji} '
            f'<span style="color:#7b68ee;">{t.id}</span> '
            f'{t.subject[:30]}{"..." if len(t.subject) > 30 else ""} '
            f'<span style="color:#666;">— {name}</span>'
            f'</div>'
        )

    if len(world.queue) > 8:
        rows.append(f'<div style="color:#666;font-size:11px;padding:4px 8px;">... +{len(world.queue) - 8} more</div>')

    return "".join(rows)


def _action_icon(action: str) -> str:
    if "open_ticket" in action:
        return "\U0001f4e8"
    if "reply" in action:
        return "\U0001f4ac"
    if "lookup" in action:
        return "\U0001f50d"
    if "apply_action" in action:
        return "\u2699\ufe0f"
    if "escalate" in action:
        return "\u26a0\ufe0f"
    if "use_template" in action:
        return "\U0001f4dd"
    if "resolve" in action:
        return "\u2705"
    if "check_queue" in action:
        return "\U0001f4cb"
    if "check_stats" in action:
        return "\U0001f4ca"
    if "take_break" in action:
        return "\u2615"
    return "\u2753"


# ---------------------------------------------------------------------------
# Main display functions
# ---------------------------------------------------------------------------

def display_turn(
    world: SupportWorld,
    agent: AgentState,
    turn: int,
    action: str,
    result: str,
    delay: float = 0.0,
) -> None:
    """Display a single turn with support-desk-themed UI."""
    try:
        from IPython.display import clear_output, display, HTML

        clear_output(wait=True)

        tokens_html = _render_tokens_bar(agent)
        csat_html = _render_csat_bar(agent)
        resolved_html = _render_resolved_bar(agent)
        turn_html = _render_turn_counter(turn + 1)
        queue_html = _render_queue(world)
        icon = _action_icon(action)

        if any(w in result.lower() for w in ["resolved", "sent", "processed", "applied", "updated", "victory"]):
            result_color = "#16c79a"
            result_border = "#16c79a"
        elif any(w in result.lower() for w in ["warning", "lost", "wrong", "fail", "cannot", "game over", "unnecessary"]):
            result_color = "#e94560"
            result_border = "#e94560"
        else:
            result_color = "#b0b0b0"
            result_border = "#444"

        # Active ticket info
        active_html = ""
        if world.active_ticket:
            t = world.active_ticket
            customer = world.get_customer(t.customer_id)
            cname = customer.name if customer else "Unknown"
            active_html = (
                f'<div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;">'
                f'<div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">'
                f'\U0001f4e8 Active Ticket</div>'
                f'<div style="font-size:13px;color:#e0e0e0;">'
                f'{t.priority.emoji} <span style="color:#7b68ee;">{t.id}</span> — {t.subject[:35]}</div>'
                f'<div style="font-size:11px;color:#888;margin-top:2px;">'
                f'{cname} | {t.category.value} | {t.priority.value}</div>'
                f'</div>'
            )
        else:
            active_html = (
                '<div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;">'
                '<div style="color:#666;font-size:12px;font-style:italic;">No active ticket — use open_ticket()</div>'
                '</div>'
            )

        html = f"""
<div style="font-family:'Courier New',monospace;background:linear-gradient(180deg,#0d0d1a 0%,#1a1a2e 100%);
  color:#e0e0e0;padding:0;border-radius:12px;max-width:750px;border:2px solid #2a2a4e;
  box-shadow:0 4px 24px rgba(0,0,0,0.6);overflow:hidden;">

  <!-- Title bar -->
  <div style="background:linear-gradient(90deg,#16213e,#0f3460);padding:8px 16px;
    display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #0f3460;">
    <span style="color:#e0e0e0;font-weight:bold;font-size:16px;letter-spacing:2px;">
      \U0001f4e7 THE SUPPORT DESK</span>
    <span style="color:#666;font-size:12px;">Shift in progress</span>
  </div>

  <!-- Main content -->
  <div style="display:flex;gap:0;">

    <!-- Left: Ticket Queue -->
    <div style="padding:12px;width:320px;flex-shrink:0;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
        \U0001f4e5 Ticket Queue ({len(world.queue)})</div>
      <div style="background:#0d0d18;border-radius:8px;padding:4px;border:1px solid #2a2a3e;
        max-height:300px;overflow-y:auto;">
        {queue_html}
      </div>
    </div>

    <!-- Right: Stats panel -->
    <div style="padding:12px 12px 12px 0;flex:1;min-width:200px;display:flex;flex-direction:column;gap:10px;">
      {turn_html}

      <div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Escalation Tokens</div>
        {tokens_html}
      </div>

      <div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">CSAT Score</div>
        {csat_html}
      </div>

      <div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Tickets Resolved</div>
        {resolved_html}
      </div>

      {active_html}
    </div>
  </div>

  <!-- Action log -->
  <div style="border-top:1px solid #2a2a3e;padding:10px 16px;background:#0d0d18;">
    <div style="color:#0f3460;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Action</div>
    <div style="color:#16c79a;font-size:13px;margin-top:2px;">{icon} {action}</div>
    <div style="margin-top:6px;padding:8px 10px;background:#12122a;border-radius:6px;
      border-left:3px solid {result_border};font-size:12px;color:{result_color};
      max-height:100px;overflow-y:auto;white-space:pre-wrap;">
{result[:500]}</div>
  </div>
</div>
"""
        display(HTML(html))

    except ImportError:
        print(f"\n{'='*60}")
        print(f"Turn {turn + 1} | {agent.status_text()}")
        print(f"Queue: {len(world.queue)} tickets")
        print(f"Action: {action}")
        print(f"Result: {result[:300]}")
        print(f"{'='*60}")

    if delay > 0:
        time.sleep(delay)


def display_final(agent: AgentState, turns: int) -> None:
    """Display the final shift result."""
    if agent.has_won:
        title = "\U0001f3c6 SHIFT COMPLETE — ALL TARGETS MET \U0001f3c6"
        color = "#ffd700"
        bg = "linear-gradient(180deg,#1a3a1a,#0d0d1a)"
        glow = "text-shadow:0 0 20px #ffd700,0 0 40px #ffd700;"
    elif not agent.is_alive:
        title = "\U0001f6a8 SHIFT TERMINATED \U0001f6a8"
        color = "#e94560"
        bg = "linear-gradient(180deg,#2a1010,#0d0d1a)"
        glow = "text-shadow:0 0 20px #e94560;"
    else:
        title = "\u23f0 SHIFT ENDED — TARGETS NOT MET"
        color = "#e9a045"
        bg = "linear-gradient(180deg,#2a2010,#0d0d1a)"
        glow = "text-shadow:0 0 20px #e9a045;"

    try:
        from IPython.display import display, HTML

        html = f"""
<div style="font-family:'Courier New',monospace;background:{bg};
  color:#e0e0e0;padding:0;border-radius:12px;max-width:680px;border:2px solid {color};
  box-shadow:0 0 30px {color}40;overflow:hidden;">

  <div style="text-align:center;padding:30px 20px 10px;">
    <div style="font-size:28px;font-weight:bold;color:{color};{glow}letter-spacing:3px;">
      {title}</div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:20px;margin:10px 20px;
    background:#0d0d18;border-radius:8px;border:1px solid #2a2a3e;">

    <div style="text-align:center;padding:10px;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;">Tickets Resolved</div>
      <div style="font-size:28px;margin-top:4px;color:#16c79a;">{agent.resolved_count}/{agent.WIN_RESOLVED}</div>
    </div>

    <div style="text-align:center;padding:10px;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;">CSAT Score</div>
      <div style="font-size:28px;margin-top:4px;color:{'#16c79a' if agent.csat_score >= 80 else '#e9a045' if agent.csat_score >= 60 else '#e94560'};">{agent.csat_score:.0f}%</div>
    </div>

    <div style="text-align:center;padding:10px;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;">Turns Used</div>
      <div style="font-size:28px;margin-top:4px;color:#7b68ee;">{turns}</div>
    </div>

    <div style="text-align:center;padding:10px;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;">Tokens Remaining</div>
      <div style="font-size:28px;margin-top:4px;color:{'#16c79a' if agent.escalation_tokens >= 2 else '#e94560'};">{agent.escalation_tokens}/{agent.MAX_TOKENS}</div>
    </div>
  </div>

  <div style="padding:0 20px 20px;">
    <div style="background:#0d0d18;border-radius:8px;padding:12px;border:1px solid #2a2a3e;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
        Agent Notes</div>
      <div style="font-size:12px;color:#b0b0b0;max-height:120px;overflow-y:auto;">
        {"<br>".join(f"- {n}" for n in agent.notes[-10:]) if agent.notes else "<em>No notes recorded.</em>"}
      </div>
    </div>
  </div>
</div>
"""
        display(HTML(html))

    except ImportError:
        print(f"\n{'#'*60}")
        print(f"  {title}")
        print(f"  Resolved: {agent.resolved_count}/{agent.WIN_RESOLVED}")
        print(f"  CSAT: {agent.csat_score:.0f}%")
        print(f"  Tokens: {agent.escalation_tokens}/{agent.MAX_TOKENS}")
        print(f"  Turns: {turns}")
        print(f"{'#'*60}")
