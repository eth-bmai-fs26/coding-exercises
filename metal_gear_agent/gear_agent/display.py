"""Display utilities for Metal Gear Agent — military-style visualization."""

import time
from typing import Optional

from gear_agent.data import CellType
from gear_agent.scenario import FacilityWorld
from gear_agent.game import OperativeState


# ── Tile rendering ───────────────────────────────────────────────────────────

TILE_STYLES = {
    CellType.CORRIDOR:        {"bg": "#2a3a2a", "emoji": ""},
    CellType.SERVER_ROOM:     {"bg": "#1a2a3a", "emoji": "\U0001f4bb"},
    CellType.REINFORCED_WALL: {"bg": "#4a4a4a", "emoji": "\U0001f9f1"},
    CellType.INTEL_CACHE:     {"bg": "#2a3a2a", "emoji": "\U0001f4c1"},
    CellType.INFORMANT:       {"bg": "#2a3322", "emoji": "\U0001f575\ufe0f"},
    CellType.ARMORY:          {"bg": "#3a3020", "emoji": "\U0001f527"},
    CellType.SAFE_ROOM:       {"bg": "#1a2030", "emoji": "\U0001f4fb"},
    CellType.BOSS_ARENA:      {"bg": "#3a1a1a", "emoji": "\U0001f480"},
    CellType.ENTRY_POINT:     {"bg": "#2a2a3a", "emoji": "\U0001f6aa"},
}

FOG_TILE = {"bg": "#0a0a12", "emoji": "\u2591"}
OPERATIVE_EMOJI = "\U0001f575\ufe0f"


def _render_html_grid(world: FacilityWorld, operative: OperativeState, show_all: bool = False) -> str:
    """Render the game grid as an HTML table with colored tiles."""
    visible = set()
    if show_all:
        visible = {(r, c) for r in range(world.ROWS) for c in range(world.COLS)}
    else:
        for (vr, vc) in operative.visited:
            visible.add((vr, vc))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = vr + dr, vc + dc
                if 0 <= nr < world.ROWS and 0 <= nc < world.COLS:
                    visible.add((nr, nc))

    cell_size = 48
    rows_html = []
    for row in range(world.ROWS):
        cells_html = []
        for col in range(world.COLS):
            if (row, col) == operative.position:
                cell = world.get_cell(row, col)
                style = TILE_STYLES.get(cell.cell_type, TILE_STYLES[CellType.CORRIDOR])
                bg = style["bg"]
                cells_html.append(
                    f'<td style="width:{cell_size}px;height:{cell_size}px;'
                    f'background:{bg};text-align:center;font-size:24px;'
                    f'border:2px solid #00ff41;box-shadow:0 0 8px #00ff41 inset;">'
                    f'{OPERATIVE_EMOJI}</td>'
                )
            elif (row, col) in visible:
                cell = world.get_cell(row, col)
                style = TILE_STYLES.get(cell.cell_type, TILE_STYLES[CellType.CORRIDOR])
                bg = style["bg"]
                emoji = style["emoji"]
                if (row, col) in operative.visited and cell.cell_type == CellType.CORRIDOR:
                    bg = "#1e2e1e"
                cells_html.append(
                    f'<td style="width:{cell_size}px;height:{cell_size}px;'
                    f'background:{bg};text-align:center;font-size:20px;'
                    f'border:1px solid #1a1a22;">'
                    f'{emoji}</td>'
                )
            else:
                cells_html.append(
                    f'<td style="width:{cell_size}px;height:{cell_size}px;'
                    f'background:#070710;text-align:center;font-size:16px;'
                    f'color:#222;border:1px solid #0a0a12;">'
                    f'\u2591</td>'
                )
        rows_html.append("<tr>" + "".join(cells_html) + "</tr>")

    return (
        f'<table style="border-collapse:collapse;border:3px solid #1a2a1a;'
        f'border-radius:4px;box-shadow:0 0 20px rgba(0,40,0,0.5);">'
        + "".join(rows_html) +
        '</table>'
    )


def _render_health_bar(operative: OperativeState) -> str:
    """Render health as pixel-art style indicators."""
    full = '<span style="color:#00ff41;font-size:20px;text-shadow:0 0 4px #00ff41;">\u2764\ufe0f</span>'
    empty = '<span style="color:#333;font-size:20px;">\U0001f5a4</span>'
    return (full + " ") * operative.health + (empty + " ") * (operative.MAX_HEALTH - operative.health)


def _render_intel_bar(operative: OperativeState) -> str:
    """Render intel progress as a bar."""
    pct = min(100, int(operative.intel / operative.WIN_INTEL * 100))
    glow = "box-shadow:0 0 10px #00ff41;" if pct >= 100 else ""
    return (
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="font-size:18px;">\U0001f4c1</span>'
        f'<div style="flex:1;background:#0a0a12;border-radius:10px;height:20px;border:1px solid #1a3a1a;overflow:hidden;">'
        f'<div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#005500,#00ff41);'
        f'border-radius:10px;transition:width 0.5s;{glow}"></div>'
        f'</div>'
        f'<span style="color:#00ff41;font-weight:bold;min-width:60px;">{operative.intel}/{operative.WIN_INTEL}</span>'
        f'</div>'
    )


def _render_inventory(operative: OperativeState) -> str:
    """Render inventory as item slots."""
    if not operative.inventory:
        return '<span style="color:#555;font-style:italic;">Empty</span>'

    item_icons = {
        "Encrypted Message": "\u2709\ufe0f",
        "Medical Supplies": "\U0001fa79",
        "Detonator Components": "\U0001f4a3",
        "Plastic Explosives": "\U0001f9e8",
        "C4 Compound": "\U0001f4a5",
        "Circuit Board": "\U0001f4df",
        "EMP Device": "\u26a1",
        "C4 Package": "\U0001f4a3",
        "Access Codes": "\U0001f510",
        "Hostage Data": "\U0001f4be",
        "Ration": "\U0001f35e",
        "Medkit": "\U0001fa79",
    }

    slots = []
    for item in operative.inventory:
        icon = item_icons.get(item, "\U0001f4e6")
        slots.append(
            f'<div style="display:inline-block;background:#1a2a1a;border:1px solid #2a3a2a;'
            f'border-radius:6px;padding:4px 8px;margin:2px;font-size:12px;">'
            f'{icon} {item}</div>'
        )
    return "".join(slots)


def _render_turn_counter(turn: int, max_turns: int = 100) -> str:
    """Render turn counter as a progress indicator."""
    pct = min(100, int(turn / max_turns * 100))
    color = "#00ff41" if pct < 60 else "#e9a045" if pct < 80 else "#e94560"
    return (
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="font-size:14px;">\u23f1\ufe0f</span>'
        f'<div style="flex:1;background:#0a0a12;border-radius:10px;height:14px;border:1px solid #1a3a1a;overflow:hidden;">'
        f'<div style="width:{pct}%;height:100%;background:{color};'
        f'border-radius:10px;transition:width 0.5s;"></div>'
        f'</div>'
        f'<span style="color:{color};font-size:13px;min-width:70px;">Turn {turn}/{max_turns}</span>'
        f'</div>'
    )


def _action_icon(action: str) -> str:
    """Get an icon for the action type."""
    if "move" in action:
        return "\U0001f9ed"
    if "codec" in action:
        return "\U0001f4fb"
    if "collect" in action:
        return "\u270b"
    if "engage" in action:
        return "\U0001f4a5"
    if "equip" in action:
        return "\U0001f527"
    if "hide" in action:
        return "\U0001f4e6"
    if "use" in action:
        return "\u2728"
    if "scan" in action:
        return "\U0001f441\ufe0f"
    if "sitrep" in action:
        return "\U0001f4cb"
    return "\u2753"


# ── Plain-text rendering (fallback) ─────────────────────────────────────────

def render_grid(world: FacilityWorld, operative: OperativeState, show_all: bool = False) -> str:
    """Render the game grid as a string (plain-text fallback)."""
    visible = set()
    if show_all:
        visible = {(r, c) for r in range(world.ROWS) for c in range(world.COLS)}
    else:
        for (vr, vc) in operative.visited:
            visible.add((vr, vc))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = vr + dr, vc + dc
                if 0 <= nr < world.ROWS and 0 <= nc < world.COLS:
                    visible.add((nr, nc))

    lines = []
    lines.append("    " + "  ".join(f" {c} " for c in range(world.COLS)))
    lines.append("   " + "----" * world.COLS + "-")

    for row in range(world.ROWS):
        row_str = f"{row}  |"
        for col in range(world.COLS):
            if (row, col) == operative.position:
                row_str += " \U0001f575\ufe0f|"
            elif (row, col) in visible:
                cell = world.get_cell(row, col)
                emoji = cell.cell_type.emoji
                row_str += f" {emoji}  |" if len(emoji) == 1 else f" {emoji} |"
            else:
                row_str += " \u2591\u2591 |"
        lines.append(row_str)
        lines.append("   " + "----" * world.COLS + "-")

    return "\n".join(lines)


def render_stats(operative: OperativeState) -> str:
    """Render the operative stats bar (plain-text fallback)."""
    health_display = "\u2764\ufe0f " * operative.health + "\U0001f5a4 " * (operative.MAX_HEALTH - operative.health)
    inv = ", ".join(operative.inventory) if operative.inventory else "empty"
    return (
        f"Health: {health_display.strip()} | "
        f"Intel: {operative.intel} | "
        f"Position: {operative.position} | "
        f"Inventory: [{inv}]"
    )


# ── Rich HTML display ───────────────────────────────────────────────────────

def display_turn(
    world: FacilityWorld,
    operative: OperativeState,
    turn: int,
    action: str,
    result: str,
    delay: float = 0.0,
) -> None:
    """Display a single turn with military-style UI."""
    try:
        from IPython.display import clear_output, display, HTML

        clear_output(wait=True)

        grid_html = _render_html_grid(world, operative)
        health_html = _render_health_bar(operative)
        intel_html = _render_intel_bar(operative)
        inventory_html = _render_inventory(operative)
        turn_html = _render_turn_counter(turn + 1)
        icon = _action_icon(action)

        if any(w in result.lower() for w in ["intel", "mission success", "reward", "collected", "fabricated", "earned"]):
            result_color = "#00ff41"
            result_border = "#00ff41"
        elif any(w in result.lower() for w in ["alert", "damage", "fail", "cannot", "nothing", "retreat", "lost"]):
            result_color = "#e94560"
            result_border = "#e94560"
        else:
            result_color = "#8a8a8a"
            result_border = "#333"

        html = f"""
<div style="font-family:'Courier New',monospace;background:linear-gradient(180deg,#080810 0%,#0a1a0a 100%);
  color:#c0c0c0;padding:0;border-radius:12px;max-width:680px;border:2px solid #1a3a1a;
  box-shadow:0 4px 24px rgba(0,20,0,0.6);overflow:hidden;">

  <!-- Title bar -->
  <div style="background:linear-gradient(90deg,#0a1a0a,#1a2a1a);padding:8px 16px;
    display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #00ff41;">
    <span style="color:#00ff41;font-weight:bold;font-size:16px;letter-spacing:2px;">
      \U0001f575\ufe0f METAL GEAR AGENT</span>
    <span style="color:#555;font-size:12px;">({operative.position[0]}, {operative.position[1]})</span>
  </div>

  <!-- Main content -->
  <div style="display:flex;gap:0;">

    <!-- Left: Map -->
    <div style="padding:12px;flex-shrink:0;">
      {grid_html}
    </div>

    <!-- Right: Stats panel -->
    <div style="padding:12px 12px 12px 0;flex:1;min-width:200px;display:flex;flex-direction:column;gap:10px;">

      <!-- Turn counter -->
      {turn_html}

      <!-- Health -->
      <div style="background:#0a0a12;border-radius:8px;padding:8px 10px;border:1px solid #1a2a1a;">
        <div style="color:#666;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Health</div>
        {health_html}
      </div>

      <!-- Intel -->
      <div style="background:#0a0a12;border-radius:8px;padding:8px 10px;border:1px solid #1a2a1a;">
        <div style="color:#666;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Intel</div>
        {intel_html}
      </div>

      <!-- Inventory -->
      <div style="background:#0a0a12;border-radius:8px;padding:8px 10px;border:1px solid #1a2a1a;flex:1;">
        <div style="color:#666;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">
          \U0001f4e6 Equipment</div>
        <div style="font-size:12px;">{inventory_html}</div>
      </div>
    </div>
  </div>

  <!-- Action log -->
  <div style="border-top:1px solid #1a2a1a;padding:10px 16px;background:#060610;">
    <div style="display:flex;gap:12px;align-items:flex-start;">
      <div style="flex:1;">
        <div style="color:#00ff41;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Action</div>
        <div style="color:#00cc33;font-size:13px;margin-top:2px;">{icon} {action}</div>
      </div>
    </div>
    <div style="margin-top:8px;padding:8px 10px;background:#0a0a12;border-radius:6px;
      border-left:3px solid {result_border};font-size:12px;color:{result_color};
      max-height:60px;overflow-y:auto;">
      {result[:400]}
    </div>
  </div>
</div>
"""
        display(HTML(html))

    except ImportError:
        print(f"\n{'='*60}")
        print(f"Turn {turn + 1}")
        print(f"{'='*60}")
        print(render_stats(operative))
        print(render_grid(world, operative))
        print(f"Action: {action}")
        print(f"Result: {result[:300]}")
        print(f"{'='*60}")

    if delay > 0:
        time.sleep(delay)


def display_final(operative: OperativeState, turns: int) -> None:
    """Display the final game result with military victory/defeat screen."""
    if operative.has_won:
        title = "\U0001f575\ufe0f MISSION COMPLETE \U0001f575\ufe0f"
        subtitle = "Intel objective achieved. Extraction confirmed."
        color = "#00ff41"
        bg_accent = "linear-gradient(180deg,#0a1a0a,#080810)"
        glow = "text-shadow:0 0 20px #00ff41,0 0 40px #00ff41;"
        msg = f"Gathered <span style='color:#00ff41;font-weight:bold;'>{operative.intel} intel</span> in <span style='color:#00cc33;'>{turns} turns</span> with <span style='color:#e94560;'>{operative.health} health</span> remaining."
    elif not operative.is_alive:
        title = "\U0001f480 MISSION FAILED \U0001f480"
        subtitle = "The operative has been eliminated."
        color = "#e94560"
        bg_accent = "linear-gradient(180deg,#1a0808,#080810)"
        glow = "text-shadow:0 0 20px #e94560,0 0 40px #e94560;"
        msg = f"Eliminated after <span style='color:#e9a045;'>{turns} turns</span> with <span style='color:#00ff41;'>{operative.intel} intel</span> gathered."
    else:
        title = "\u23f0 TIME'S UP \u23f0"
        subtitle = "Mission window has closed. Abort."
        color = "#e9a045"
        bg_accent = "linear-gradient(180deg,#1a1808,#080810)"
        glow = "text-shadow:0 0 20px #e9a045;"
        msg = f"Gathered <span style='color:#00ff41;'>{operative.intel}/{operative.WIN_INTEL} intel</span> in <span style='color:#e9a045;'>{turns} turns</span>."

    inv_text = ", ".join(operative.inventory) if operative.inventory else "empty"
    health_display = "\u2764\ufe0f " * operative.health + "\U0001f5a4 " * (operative.MAX_HEALTH - operative.health)

    try:
        from IPython.display import display, HTML

        html = f"""
<div style="font-family:'Courier New',monospace;background:{bg_accent};
  color:#c0c0c0;padding:0;border-radius:12px;max-width:680px;border:2px solid {color};
  box-shadow:0 0 30px {color}40;overflow:hidden;">

  <!-- Header -->
  <div style="text-align:center;padding:30px 20px 10px;">
    <div style="font-size:36px;font-weight:bold;color:{color};{glow}letter-spacing:4px;">
      {title}
    </div>
    <div style="color:#666;font-size:14px;margin-top:4px;font-style:italic;">{subtitle}</div>
    <div style="margin-top:16px;font-size:15px;line-height:1.6;">{msg}</div>
  </div>

  <!-- Stats grid -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:20px;margin:10px 20px;
    background:#060610;border-radius:8px;border:1px solid #1a2a1a;">

    <div style="text-align:center;padding:10px;">
      <div style="color:#666;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Health</div>
      <div style="font-size:22px;margin-top:4px;">{health_display}</div>
    </div>

    <div style="text-align:center;padding:10px;">
      <div style="color:#666;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Intel</div>
      <div style="font-size:22px;margin-top:4px;color:#00ff41;">\U0001f4c1 {operative.intel}</div>
    </div>

    <div style="text-align:center;padding:10px;">
      <div style="color:#666;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Turns Used</div>
      <div style="font-size:22px;margin-top:4px;color:#00cc33;">{turns}</div>
    </div>

    <div style="text-align:center;padding:10px;">
      <div style="color:#666;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Sectors Explored</div>
      <div style="font-size:22px;margin-top:4px;color:#7b68ee;">{len(operative.visited)}</div>
    </div>
  </div>

  <!-- Inventory -->
  <div style="padding:0 20px 20px;">
    <div style="background:#060610;border-radius:8px;padding:12px;border:1px solid #1a2a1a;">
      <div style="color:#666;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
        \U0001f4e6 Final Equipment</div>
      <div style="font-size:13px;">{_render_inventory(operative)}</div>
    </div>
  </div>
</div>
"""
        display(HTML(html))

    except ImportError:
        print(f"\n{'#'*60}")
        print(f"  {title}")
        print(f"  {msg}")
        print(f"  Health: {operative.health}/{operative.MAX_HEALTH}")
        print(f"  Intel: {operative.intel}")
        print(f"  Inventory: {inv_text}")
        print(f"  Cells visited: {len(operative.visited)}")
        print(f"  Turns used: {turns}")
        print(f"{'#'*60}")
