"""Display utilities for Quest Hero — notebook-friendly visualization."""

import time
from typing import Optional

from quest_hero.game_world import GameWorld, CellType
from quest_hero.hero import Hero


def render_grid(world: GameWorld, hero: Hero, show_all: bool = False) -> str:
    """Render the game grid as a string.

    By default, only visited cells and their neighbors are revealed.
    If show_all is True, the full map is shown (for debugging or solutions).

    Args:
        world: The game world.
        hero: The hero (for position and visited set).
        show_all: If True, reveal the entire map.

    Returns:
        str: Multi-line string representation of the grid.
    """
    # Determine which cells are visible (visited + adjacent to visited)
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
                row_str += " \U0001f9b8 |"  # 🦸
            elif (row, col) in visible:
                cell = world.get_cell(row, col)
                emoji = cell.cell_type.emoji
                # Pad emoji display
                row_str += f" {emoji}  |" if len(emoji) == 1 else f" {emoji} |"
            else:
                row_str += " \u2591\u2591 |"  # ░░ fog
        lines.append(row_str)
        lines.append("   " + "----" * world.COLS + "-")

    return "\n".join(lines)


def render_stats(hero: Hero) -> str:
    """Render the hero stats bar."""
    hearts_display = "\u2764\ufe0f " * hero.hearts + "\U0001f5a4 " * (hero.MAX_HEARTS - hero.hearts)
    inv = ", ".join(hero.inventory) if hero.inventory else "empty"
    return (
        f"Hearts: {hearts_display.strip()} | "
        f"Gold: {hero.gold} | "
        f"Position: {hero.position} | "
        f"Inventory: [{inv}]"
    )


def display_turn(
    world: GameWorld,
    hero: Hero,
    turn: int,
    action: str,
    result: str,
    delay: float = 0.0,
) -> None:
    """Display a single turn in the notebook.

    Uses IPython.display if available, otherwise falls back to print.
    """
    try:
        from IPython.display import clear_output, display, HTML

        clear_output(wait=True)

        grid = render_grid(world, hero)
        stats = render_stats(hero)

        html = f"""
<div style="font-family: monospace; background: #1a1a2e; color: #e0e0e0; padding: 15px; border-radius: 8px; max-width: 800px;">
  <h3 style="color: #e94560; margin-top: 0;">Quest Hero - Turn {turn + 1}</h3>
  <div style="color: #0f3460; background: #e0e0e0; padding: 8px; border-radius: 4px; margin-bottom: 10px;">
    {stats}
  </div>
  <pre style="font-size: 14px; line-height: 1.4;">{grid}</pre>
  <div style="margin-top: 10px;">
    <strong style="color: #e94560;">Action:</strong> <span style="color: #16c79a;">{action}</span>
  </div>
  <div style="margin-top: 5px;">
    <strong style="color: #e94560;">Result:</strong> {result[:300]}
  </div>
</div>
"""
        display(HTML(html))

    except ImportError:
        # Fallback for non-notebook environments
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
    """Display the final game result."""
    if hero.has_won:
        title = "VICTORY!"
        color = "#16c79a"
        msg = f"The hero collected {hero.gold} gold in {turns} turns with {hero.hearts} hearts remaining!"
    elif not hero.is_alive:
        title = "GAME OVER"
        color = "#e94560"
        msg = f"The hero fell after {turns} turns with {hero.gold} gold collected."
    else:
        title = "TIME'S UP"
        color = "#e9a045"
        msg = f"Ran out of turns! Collected {hero.gold}/{hero.WIN_GOLD} gold in {turns} turns."

    try:
        from IPython.display import display, HTML

        html = f"""
<div style="font-family: monospace; background: #1a1a2e; color: #e0e0e0; padding: 20px; border-radius: 8px; max-width: 800px; text-align: center;">
  <h1 style="color: {color}; font-size: 36px;">{title}</h1>
  <p style="font-size: 18px;">{msg}</p>
  <div style="margin-top: 15px; text-align: left; padding: 10px;">
    <strong>Final Stats:</strong><br>
    Hearts: {hero.hearts}/{hero.MAX_HEARTS}<br>
    Gold: {hero.gold}<br>
    Inventory: {', '.join(hero.inventory) if hero.inventory else 'empty'}<br>
    Cells visited: {len(hero.visited)}<br>
    Turns used: {turns}
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
        print(f"  Inventory: {', '.join(hero.inventory) if hero.inventory else 'empty'}")
        print(f"  Cells visited: {len(hero.visited)}")
        print(f"  Turns used: {turns}")
        print(f"{'#'*60}")
