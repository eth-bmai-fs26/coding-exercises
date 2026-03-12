"""Display utilities for Quest Hero — retro RPG-style visualization."""

import time
from typing import Optional

from quest_hero.game_world import GameWorld, CellType
from quest_hero.hero import Hero


# ── Tile rendering ───────────────────────────────────────────────────────────

# Each cell type maps to an HTML tile with background color and emoji
TILE_STYLES = {
    CellType.OPEN:     {"bg": "#4a7c59", "emoji": ""},
    CellType.FOREST:   {"bg": "#2d5a27", "emoji": "\U0001f332"},
    CellType.MOUNTAIN: {"bg": "#6b6b6b", "emoji": "\u26f0\ufe0f"},
    CellType.TREASURE: {"bg": "#4a7c59", "emoji": "\U0001f48e"},
    CellType.NPC:      {"bg": "#4a6741", "emoji": "\U0001f9d9"},
    CellType.SHOP:     {"bg": "#7a6543", "emoji": "\U0001f3ea"},
    CellType.INN:      {"bg": "#6b5b3a", "emoji": "\U0001f3e0"},
    CellType.DRAGON:   {"bg": "#5c2a2a", "emoji": "\U0001f409"},
    CellType.CASTLE:   {"bg": "#5a5a7a", "emoji": "\U0001f3f0"},
}

FOG_TILE = {"bg": "#1a1a2e", "emoji": "\u2591"}
HERO_EMOJI = "\U0001f9b8"


def _render_html_grid(world: GameWorld, hero: Hero, show_all: bool = False) -> str:
    """Render the game grid as an HTML table with colored tiles."""
    visible = set()
    if show_all:
        visible = {(r, c) for r in range(world.ROWS) for c in range(world.COLS)}
    else:
        for (vr, vc) in hero.visited:
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
            if (row, col) == hero.position:
                cell = world.get_cell(row, col)
                style = TILE_STYLES.get(cell.cell_type, TILE_STYLES[CellType.OPEN])
                bg = style["bg"]
                cells_html.append(
                    f'<td style="width:{cell_size}px;height:{cell_size}px;'
                    f'background:{bg};text-align:center;font-size:24px;'
                    f'border:2px solid #ffd700;box-shadow:0 0 8px #ffd700 inset;">'
                    f'{HERO_EMOJI}</td>'
                )
            elif (row, col) in visible:
                cell = world.get_cell(row, col)
                style = TILE_STYLES.get(cell.cell_type, TILE_STYLES[CellType.OPEN])
                bg = style["bg"]
                emoji = style["emoji"]
                visited_mark = ""
                if (row, col) in hero.visited and cell.cell_type == CellType.OPEN:
                    bg = "#3d6b4e"
                cells_html.append(
                    f'<td style="width:{cell_size}px;height:{cell_size}px;'
                    f'background:{bg};text-align:center;font-size:20px;'
                    f'border:1px solid #2a2a3e;">'
                    f'{emoji}{visited_mark}</td>'
                )
            else:
                cells_html.append(
                    f'<td style="width:{cell_size}px;height:{cell_size}px;'
                    f'background:#111122;text-align:center;font-size:16px;'
                    f'color:#333;border:1px solid #1a1a2e;">'
                    f'\u2591</td>'
                )
        rows_html.append("<tr>" + "".join(cells_html) + "</tr>")

    return (
        f'<table style="border-collapse:collapse;border:3px solid #2a2a4e;'
        f'border-radius:4px;box-shadow:0 0 20px rgba(0,0,0,0.5);">'
        + "".join(rows_html) +
        '</table>'
    )


def _render_hearts_bar(hero: Hero) -> str:
    """Render hearts as pixel-art style hearts."""
    full = '<span style="color:#e94560;font-size:20px;text-shadow:0 0 4px #e94560;">\u2764\ufe0f</span>'
    empty = '<span style="color:#333;font-size:20px;">\U0001f5a4</span>'
    return (full + " ") * hero.hearts + (empty + " ") * (hero.MAX_HEARTS - hero.hearts)


def _render_gold_bar(hero: Hero) -> str:
    """Render gold progress as a bar."""
    pct = min(100, int(hero.gold / hero.WIN_GOLD * 100))
    glow = "box-shadow:0 0 10px #ffd700;" if pct >= 100 else ""
    return (
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="font-size:18px;">\U0001fa99</span>'
        f'<div style="flex:1;background:#1a1a2e;border-radius:10px;height:20px;border:1px solid #333;overflow:hidden;">'
        f'<div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#b8860b,#ffd700);'
        f'border-radius:10px;transition:width 0.5s;{glow}"></div>'
        f'</div>'
        f'<span style="color:#ffd700;font-weight:bold;min-width:60px;">{hero.gold}/{hero.WIN_GOLD}</span>'
        f'</div>'
    )


def _render_inventory(hero: Hero) -> str:
    """Render inventory as item slots."""
    if not hero.inventory:
        return '<span style="color:#666;font-style:italic;">Empty</span>'

    item_icons = {
        "Letter": "\u2709\ufe0f",
        "Herbal Tea": "\U0001fad6",
        "Ghostcaps": "\U0001f344",
        "Medicine": "\U0001f9ea",
        "Moonstone": "\U0001f311",
        "Ember Ore": "\U0001f525",
        "Sunblade": "\u2694\ufe0f",
        "Moonstone Lantern": "\U0001f506",
        "Dragon Scales": "\U0001f49a",
        "Bread": "\U0001f35e",
        "Health Potion": "\U0001f9cb",
    }

    slots = []
    for item in hero.inventory:
        icon = item_icons.get(item, "\U0001f4e6")
        slots.append(
            f'<div style="display:inline-block;background:#2a2a3e;border:1px solid #444;'
            f'border-radius:6px;padding:4px 8px;margin:2px;font-size:12px;">'
            f'{icon} {item}</div>'
        )
    return "".join(slots)


def _render_turn_counter(turn: int, max_turns: int = 100) -> str:
    """Render turn counter as a progress indicator."""
    pct = min(100, int(turn / max_turns * 100))
    color = "#16c79a" if pct < 60 else "#e9a045" if pct < 80 else "#e94560"
    return (
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="font-size:14px;">\u23f1\ufe0f</span>'
        f'<div style="flex:1;background:#1a1a2e;border-radius:10px;height:14px;border:1px solid #333;overflow:hidden;">'
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
    if "talk" in action:
        return "\U0001f4ac"
    if "pick_up" in action:
        return "\u270b"
    if "fight" in action:
        return "\u2694\ufe0f"
    if "buy" in action:
        return "\U0001f4b0"
    if "rest" in action:
        return "\U0001f634"
    if "use" in action:
        return "\u2728"
    if "look" in action:
        return "\U0001f441\ufe0f"
    if "status" in action:
        return "\U0001f4cb"
    return "\u2753"


# ── Plain-text rendering (fallback) ─────────────────────────────────────────

def render_grid(world: GameWorld, hero: Hero, show_all: bool = False) -> str:
    """Render the game grid as a string (plain-text fallback)."""
    visible = set()
    if show_all:
        visible = {(r, c) for r in range(world.ROWS) for c in range(world.COLS)}
    else:
        for (vr, vc) in hero.visited:
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
            if (row, col) == hero.position:
                row_str += " \U0001f9b8 |"
            elif (row, col) in visible:
                cell = world.get_cell(row, col)
                emoji = cell.cell_type.emoji
                row_str += f" {emoji}  |" if len(emoji) == 1 else f" {emoji} |"
            else:
                row_str += " \u2591\u2591 |"
        lines.append(row_str)
        lines.append("   " + "----" * world.COLS + "-")

    return "\n".join(lines)


def render_stats(hero: Hero) -> str:
    """Render the hero stats bar (plain-text fallback)."""
    hearts_display = "\u2764\ufe0f " * hero.hearts + "\U0001f5a4 " * (hero.MAX_HEARTS - hero.hearts)
    inv = ", ".join(hero.inventory) if hero.inventory else "empty"
    return (
        f"Hearts: {hearts_display.strip()} | "
        f"Gold: {hero.gold} | "
        f"Position: {hero.position} | "
        f"Inventory: [{inv}]"
    )


# ── Rich HTML display ───────────────────────────────────────────────────────

def display_turn(
    world: GameWorld,
    hero: Hero,
    turn: int,
    action: str,
    result: str,
    delay: float = 0.0,
) -> None:
    """Display a single turn with rich RPG-style UI."""
    try:
        from IPython.display import clear_output, display, HTML

        clear_output(wait=True)

        grid_html = _render_html_grid(world, hero)
        hearts_html = _render_hearts_bar(hero)
        gold_html = _render_gold_bar(hero)
        inventory_html = _render_inventory(hero)
        turn_html = _render_turn_counter(turn + 1)
        icon = _action_icon(action)

        # Determine result style
        if any(w in result.lower() for w in ["gold", "victory", "reward", "found", "picked up", "crafted", "defeated"]):
            result_color = "#16c79a"
            result_border = "#16c79a"
        elif any(w in result.lower() for w in ["damage", "hurt", "fail", "cannot", "nothing", "retreat"]):
            result_color = "#e94560"
            result_border = "#e94560"
        else:
            result_color = "#b0b0b0"
            result_border = "#444"

        html = f"""
<div style="font-family:'Courier New',monospace;background:linear-gradient(180deg,#0d0d1a 0%,#1a1a2e 100%);
  color:#e0e0e0;padding:0;border-radius:12px;max-width:680px;border:2px solid #2a2a4e;
  box-shadow:0 4px 24px rgba(0,0,0,0.6);overflow:hidden;">

  <!-- Title bar -->
  <div style="background:linear-gradient(90deg,#16213e,#0f3460);padding:8px 16px;
    display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #e94560;">
    <span style="color:#e94560;font-weight:bold;font-size:16px;letter-spacing:2px;">
      \u2694\ufe0f QUEST HERO</span>
    <span style="color:#666;font-size:12px;">({hero.position[0]}, {hero.position[1]})</span>
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

      <!-- Hearts -->
      <div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Health</div>
        {hearts_html}
      </div>

      <!-- Gold -->
      <div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Gold</div>
        {gold_html}
      </div>

      <!-- Inventory -->
      <div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;flex:1;">
        <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">
          \U0001f392 Inventory</div>
        <div style="font-size:12px;">{inventory_html}</div>
      </div>
    </div>
  </div>

  <!-- Action log -->
  <div style="border-top:1px solid #2a2a3e;padding:10px 16px;background:#0d0d18;">
    <div style="display:flex;gap:12px;align-items:flex-start;">
      <div style="flex:1;">
        <div style="color:#e94560;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Action</div>
        <div style="color:#16c79a;font-size:13px;margin-top:2px;">{icon} {action}</div>
      </div>
    </div>
    <div style="margin-top:8px;padding:8px 10px;background:#12122a;border-radius:6px;
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
        print(render_stats(hero))
        print(render_grid(world, hero))
        print(f"Action: {action}")
        print(f"Result: {result[:300]}")
        print(f"{'='*60}")

    if delay > 0:
        time.sleep(delay)


def display_final(hero: Hero, turns: int) -> None:
    """Display the final game result with RPG victory/defeat screen."""
    if hero.has_won:
        title = "\u2694\ufe0f VICTORY \u2694\ufe0f"
        subtitle = "The quest is complete!"
        color = "#ffd700"
        bg_accent = "linear-gradient(180deg,#1a3a1a,#0d0d1a)"
        glow = "text-shadow:0 0 20px #ffd700,0 0 40px #ffd700;"
        msg = f"Collected <span style='color:#ffd700;font-weight:bold;'>{hero.gold} gold</span> in <span style='color:#16c79a;'>{turns} turns</span> with <span style='color:#e94560;'>{hero.hearts} hearts</span> remaining."
    elif not hero.is_alive:
        title = "\U0001f480 GAME OVER \U0001f480"
        subtitle = "The hero has fallen..."
        color = "#e94560"
        bg_accent = "linear-gradient(180deg,#2a1010,#0d0d1a)"
        glow = "text-shadow:0 0 20px #e94560,0 0 40px #e94560;"
        msg = f"Fell after <span style='color:#e9a045;'>{turns} turns</span> with <span style='color:#ffd700;'>{hero.gold} gold</span> collected."
    else:
        title = "\u23f0 TIME'S UP \u23f0"
        subtitle = "The sands of time have run out..."
        color = "#e9a045"
        bg_accent = "linear-gradient(180deg,#2a2010,#0d0d1a)"
        glow = "text-shadow:0 0 20px #e9a045;"
        msg = f"Collected <span style='color:#ffd700;'>{hero.gold}/{hero.WIN_GOLD} gold</span> in <span style='color:#e9a045;'>{turns} turns</span>."

    inv_text = ", ".join(hero.inventory) if hero.inventory else "empty"
    hearts_display = "\u2764\ufe0f " * hero.hearts + "\U0001f5a4 " * (hero.MAX_HEARTS - hero.hearts)

    try:
        from IPython.display import display, HTML

        html = f"""
<div style="font-family:'Courier New',monospace;background:{bg_accent};
  color:#e0e0e0;padding:0;border-radius:12px;max-width:680px;border:2px solid {color};
  box-shadow:0 0 30px {color}40;overflow:hidden;">

  <!-- Header -->
  <div style="text-align:center;padding:30px 20px 10px;">
    <div style="font-size:36px;font-weight:bold;color:{color};{glow}letter-spacing:4px;">
      {title}
    </div>
    <div style="color:#888;font-size:14px;margin-top:4px;font-style:italic;">{subtitle}</div>
    <div style="margin-top:16px;font-size:15px;line-height:1.6;">{msg}</div>
  </div>

  <!-- Stats grid -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:20px;margin:10px 20px;
    background:#0d0d18;border-radius:8px;border:1px solid #2a2a3e;">

    <div style="text-align:center;padding:10px;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Health</div>
      <div style="font-size:22px;margin-top:4px;">{hearts_display}</div>
    </div>

    <div style="text-align:center;padding:10px;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Gold</div>
      <div style="font-size:22px;margin-top:4px;color:#ffd700;">\U0001fa99 {hero.gold}</div>
    </div>

    <div style="text-align:center;padding:10px;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Turns Used</div>
      <div style="font-size:22px;margin-top:4px;color:#16c79a;">{turns}</div>
    </div>

    <div style="text-align:center;padding:10px;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Cells Explored</div>
      <div style="font-size:22px;margin-top:4px;color:#7b68ee;">{len(hero.visited)}</div>
    </div>
  </div>

  <!-- Inventory -->
  <div style="padding:0 20px 20px;">
    <div style="background:#0d0d18;border-radius:8px;padding:12px;border:1px solid #2a2a3e;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
        \U0001f392 Final Inventory</div>
      <div style="font-size:13px;">{_render_inventory(hero)}</div>
    </div>
  </div>
</div>
"""
        display(HTML(html))

    except ImportError:
        print(f"\n{'#'*60}")
        print(f"  {title}")
        print(f"  {msg}")
        print(f"  Hearts: {hero.hearts}/{hero.MAX_HEARTS}")
        print(f"  Gold: {hero.gold}")
        print(f"  Inventory: {inv_text}")
        print(f"  Cells visited: {len(hero.visited)}")
        print(f"  Turns used: {turns}")
        print(f"{'#'*60}")
