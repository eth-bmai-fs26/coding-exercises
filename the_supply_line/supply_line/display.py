"""Display utilities for The Supply Line — logistics-themed visualization."""

import time
from typing import Optional

from supply_line.data import OrderPriority, OrderStatus, OrderCategory
from supply_line.game import AgentState, SupplyWorld


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _render_tokens_bar(agent: AgentState) -> str:
    full = '<span style="color:#16c79a;font-size:20px;">\u2699\ufe0f</span>'
    empty = '<span style="color:#333;font-size:20px;">\u2699\ufe0f</span>'
    return (full + " ") * agent.operations_tokens + (empty + " ") * (agent.MAX_TOKENS - agent.operations_tokens)


def _render_quality_bar(agent: AgentState) -> str:
    score = agent.quality_score
    pct = min(100, int(score))
    color = "#16c79a" if score >= 80 else "#e9a045" if score >= 60 else "#e94560"
    glow = "box-shadow:0 0 10px #16c79a;" if score >= 80 else ""
    return (
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="font-size:16px;">\U0001f4ca</span>'
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


def _render_queue(world: SupplyWorld) -> str:
    if not world.queue:
        return '<div style="color:#666;font-style:italic;padding:8px;">Queue empty</div>'

    rows = []
    for o in world.queue[:8]:
        entity = world.get_entity(o.entity_id)
        name = entity.name if entity else "Unknown"
        is_active = world.active_order and world.active_order.id == o.id
        bg = "#1a2a3e" if is_active else "#12122a"
        border = "border-left:3px solid #e94560;" if is_active else "border-left:3px solid transparent;"
        read_style = "color:#888;" if o.has_been_read else "color:#e0e0e0;font-weight:bold;"

        rows.append(
            f'<div style="padding:6px 8px;{border}background:{bg};margin:2px 0;border-radius:0 4px 4px 0;{read_style}font-size:12px;">'
            f'{o.priority.emoji} {o.category.emoji} '
            f'<span style="color:#7b68ee;">{o.id}</span> '
            f'{o.subject[:30]}{"..." if len(o.subject) > 30 else ""} '
            f'<span style="color:#666;">\u2014 {name}</span>'
            f'</div>'
        )

    if len(world.queue) > 8:
        rows.append(f'<div style="color:#666;font-size:11px;padding:4px 8px;">... +{len(world.queue) - 8} more</div>')

    return "".join(rows)


def _action_icon(action: str) -> str:
    if "read_order" in action:
        return "\U0001f4e8"
    if "notify" in action:
        return "\U0001f4ac"
    if "lookup" in action:
        return "\U0001f50d"
    if "place_order" in action:
        return "\U0001f4e6"
    if "escalate" in action:
        return "\u26a0\ufe0f"
    if "close_order" in action:
        return "\u2705"
    if "check_orders" in action:
        return "\U0001f4cb"
    if "check_stats" in action:
        return "\U0001f4ca"
    if "take_break" in action:
        return "\u2615"
    if "reject" in action:
        return "\u274c"
    if "submit" in action:
        return "\U0001f4e4"
    if "prepare" in action:
        return "\U0001f4dd"
    if "authorize" in action or "launch" in action:
        return "\U0001f680"
    if "acknowledge" in action:
        return "\U0001f514"
    if "file_claim" in action:
        return "\U0001f4b0"
    if "check_inventory" in action:
        return "\U0001f4e6"
    if "update_timeline" in action:
        return "\U0001f552"
    if "verify" in action:
        return "\U0001f9ee"
    if "compile" in action:
        return "\U0001f4c1"
    if "check_alternatives" in action:
        return "\U0001f504"
    if "check_documentation" in action:
        return "\U0001f4c4"
    return "\u2753"


# ---------------------------------------------------------------------------
# Main display functions
# ---------------------------------------------------------------------------

def display_turn(
    world: SupplyWorld,
    agent: AgentState,
    turn: int,
    action: str,
    result: str,
    delay: float = 0.0,
) -> None:
    """Display a single turn with logistics-themed UI."""
    try:
        from IPython.display import clear_output, display, HTML

        clear_output(wait=True)

        tokens_html = _render_tokens_bar(agent)
        quality_html = _render_quality_bar(agent)
        resolved_html = _render_resolved_bar(agent)
        turn_html = _render_turn_counter(turn + 1)
        queue_html = _render_queue(world)
        icon = _action_icon(action)

        if any(w in result.lower() for w in ["fulfilled", "sent", "processed", "placed", "submitted", "victory", "authorized", "prepared", "acknowledged"]):
            result_color = "#16c79a"
            result_border = "#16c79a"
        elif any(w in result.lower() for w in ["warning", "lost", "wrong", "fail", "cannot", "game over", "violation", "rejected", "blacklisted"]):
            result_color = "#e94560"
            result_border = "#e94560"
        else:
            result_color = "#b0b0b0"
            result_border = "#444"

        active_html = ""
        if world.active_order:
            o = world.active_order
            entity = world.get_entity(o.entity_id)
            ename = entity.name if entity else "Unknown"
            active_html = (
                f'<div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;">'
                f'<div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">'
                f'\U0001f4e6 Active Order</div>'
                f'<div style="font-size:13px;color:#e0e0e0;">'
                f'{o.priority.emoji} <span style="color:#7b68ee;">{o.id}</span> \u2014 {o.subject[:35]}</div>'
                f'<div style="font-size:11px;color:#888;margin-top:2px;">'
                f'{ename} | {o.category.value} | {o.priority.value}</div>'
                f'</div>'
            )
        else:
            active_html = (
                '<div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;">'
                '<div style="color:#666;font-size:12px;font-style:italic;">No active order \u2014 use read_order()</div>'
                '</div>'
            )

        html = f"""
<div style="font-family:'Courier New',monospace;background:linear-gradient(180deg,#0d0d1a 0%,#1a1a2e 100%);
  color:#e0e0e0;padding:0;border-radius:12px;max-width:750px;border:2px solid #2a4a2e;
  box-shadow:0 4px 24px rgba(0,0,0,0.6);overflow:hidden;">

  <div style="background:linear-gradient(90deg,#1a3e16,#0f4630);padding:8px 16px;
    display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #0f4630;">
    <span style="color:#e0e0e0;font-weight:bold;font-size:16px;letter-spacing:2px;">
      \U0001f69a THE SUPPLY LINE</span>
    <span style="color:#666;font-size:12px;">Operations in progress</span>
  </div>

  <div style="display:flex;gap:0;">
    <div style="padding:12px;width:320px;flex-shrink:0;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
        \U0001f4e5 Order Queue ({len(world.queue)})</div>
      <div style="background:#0d0d18;border-radius:8px;padding:4px;border:1px solid #2a2a3e;
        max-height:300px;overflow-y:auto;">
        {queue_html}
      </div>
    </div>

    <div style="padding:12px 12px 12px 0;flex:1;min-width:200px;display:flex;flex-direction:column;gap:10px;">
      {turn_html}

      <div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Operations Tokens</div>
        {tokens_html}
      </div>

      <div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Fulfillment Quality</div>
        {quality_html}
      </div>

      <div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Orders Fulfilled</div>
        {resolved_html}
      </div>

      {active_html}
    </div>
  </div>

  <div style="border-top:1px solid #2a2a3e;padding:10px 16px;background:#0d0d18;">
    <div style="color:#0f4630;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Action</div>
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
        print(f"Queue: {len(world.queue)} orders")
        print(f"Action: {action}")
        print(f"Result: {result[:300]}")
        print(f"{'='*60}")

    if delay > 0:
        time.sleep(delay)


def display_final(agent: AgentState, turns: int) -> None:
    """Display the final result."""
    if agent.has_won:
        title = "\U0001f3c6 OPERATIONS COMPLETE \u2014 ALL TARGETS MET \U0001f3c6"
        color = "#ffd700"
        bg = "linear-gradient(180deg,#1a3a1a,#0d0d1a)"
        glow = "text-shadow:0 0 20px #ffd700,0 0 40px #ffd700;"
    elif not agent.is_alive:
        title = "\U0001f6a8 OPERATIONS TERMINATED \U0001f6a8"
        color = "#e94560"
        bg = "linear-gradient(180deg,#2a1010,#0d0d1a)"
        glow = "text-shadow:0 0 20px #e94560;"
    else:
        title = "\u23f0 SHIFT ENDED \u2014 TARGETS NOT MET"
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
      <div style="color:#888;font-size:11px;text-transform:uppercase;">Orders Fulfilled</div>
      <div style="font-size:28px;margin-top:4px;color:#16c79a;">{agent.resolved_count}/{agent.WIN_RESOLVED}</div>
    </div>

    <div style="text-align:center;padding:10px;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;">Quality Score</div>
      <div style="font-size:28px;margin-top:4px;color:{'#16c79a' if agent.quality_score >= 80 else '#e9a045' if agent.quality_score >= 60 else '#e94560'};">{agent.quality_score:.0f}%</div>
    </div>

    <div style="text-align:center;padding:10px;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;">Turns Used</div>
      <div style="font-size:28px;margin-top:4px;color:#7b68ee;">{turns}</div>
    </div>

    <div style="text-align:center;padding:10px;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;">Tokens Remaining</div>
      <div style="font-size:28px;margin-top:4px;color:{'#16c79a' if agent.operations_tokens >= 2 else '#e94560'};">{agent.operations_tokens}/{agent.MAX_TOKENS}</div>
    </div>
  </div>

  <div style="padding:0 20px 20px;">
    <div style="background:#0d0d18;border-radius:8px;padding:12px;border:1px solid #2a2a3e;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
        Operations Log</div>
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
        print(f"  Fulfilled: {agent.resolved_count}/{agent.WIN_RESOLVED}")
        print(f"  Quality: {agent.quality_score:.0f}%")
        print(f"  Tokens: {agent.operations_tokens}/{agent.MAX_TOKENS}")
        print(f"  Turns: {turns}")
        print(f"{'#'*60}")
