"""Display utilities for Fridge Chef — kitchen-themed visualization."""

import time
from typing import Optional

from fridge_chef.data import ChefState
from fridge_chef.game import KitchenWorld


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _render_pipeline(chef: ChefState) -> str:
    """Render the cooking pipeline progress."""
    steps = [
        ("Check Fridge", bool(chef.fridge_contents)),
        ("Find Recipes", bool(chef.possible_recipes)),
        ("Choose Recipe", bool(chef.chosen_recipe)),
        ("Check Ingredients", bool(chef.needed_ingredients)),
        ("Shopping List", chef.shopping_done or bool(chef.shopping_list)),
        ("Done", chef.is_complete),
    ]

    items = []
    for label, done in steps:
        if done:
            items.append(
                f'<span style="color:#16c79a;font-size:12px;">\u2705 {label}</span>'
            )
        else:
            items.append(
                f'<span style="color:#555;font-size:12px;">\u2b1c {label}</span>'
            )

    return (
        '<div style="display:flex;flex-wrap:wrap;gap:6px 14px;'
        'padding:8px 10px;background:#12122a;border-radius:8px;'
        'border:1px solid #2a2a3e;">'
        + "".join(items)
        + '</div>'
    )


def _render_fridge(chef: ChefState) -> str:
    """Render the fridge contents panel."""
    if not chef.fridge_contents:
        return '<div style="color:#666;font-style:italic;padding:8px;">Fridge not checked yet</div>'

    rows = []
    for item in chef.fridge_contents:
        rows.append(
            f'<div style="padding:3px 8px;font-size:12px;color:#e0e0e0;">'
            f'\U0001f7e2 {item}</div>'
        )
    return "".join(rows)


def _render_shopping_list(chef: ChefState) -> str:
    """Render the shopping list panel."""
    if not chef.shopping_list:
        return '<div style="color:#666;font-style:italic;padding:8px;font-size:12px;">Empty</div>'

    rows = []
    for item in chef.shopping_list:
        rows.append(
            f'<div style="padding:3px 8px;font-size:12px;color:#e9a045;">'
            f'\U0001f6d2 {item}</div>'
        )
    return "".join(rows)


def _render_turn_counter(turn: int, max_turns: int = 20) -> str:
    pct = min(100, int(turn / max_turns * 100))
    color = "#16c79a" if pct < 60 else "#e9a045" if pct < 80 else "#e94560"
    return (
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="font-size:14px;">\u23f1\ufe0f</span>'
        f'<div style="flex:1;background:#1a1a2e;border-radius:10px;height:14px;'
        f'border:1px solid #333;overflow:hidden;">'
        f'<div style="width:{pct}%;height:100%;background:{color};border-radius:10px;"></div>'
        f'</div>'
        f'<span style="color:{color};font-size:13px;min-width:70px;">Turn {turn}/{max_turns}</span>'
        f'</div>'
    )


def _action_icon(action: str) -> str:
    if "check_fridge" in action:
        return "\U0001f9ca"
    if "search_recipes" in action:
        return "\U0001f50d"
    if "get_ingredients" in action:
        return "\U0001f4cb"
    if "add_to_shopping_list" in action:
        return "\U0001f6d2"
    if "done" in action:
        return "\u2705"
    return "\U0001f373"


# ---------------------------------------------------------------------------
# Main display functions
# ---------------------------------------------------------------------------

def display_turn(
    world: KitchenWorld,
    chef: ChefState,
    turn: int,
    action: str,
    result: str,
    delay: float = 0.0,
) -> None:
    """Display a single turn with kitchen-themed UI."""
    try:
        from IPython.display import clear_output, display, HTML

        clear_output(wait=True)

        pipeline_html = _render_pipeline(chef)
        turn_html = _render_turn_counter(turn + 1)
        fridge_html = _render_fridge(chef)
        shopping_html = _render_shopping_list(chef)
        icon = _action_icon(action)

        if any(w in result.lower() for w in ["done", "added", "recipes using", "you need", "contains", "complete"]):
            result_color = "#16c79a"
            result_border = "#16c79a"
        elif any(w in result.lower() for w in ["not found", "already", "please", "unknown", "error"]):
            result_color = "#e94560"
            result_border = "#e94560"
        else:
            result_color = "#b0b0b0"
            result_border = "#444"

        # Recipe info
        recipe_html = ""
        if chef.chosen_recipe:
            recipe_html = (
                f'<div style="background:#12122a;border-radius:8px;padding:8px 10px;'
                f'border:1px solid #2a2a3e;">'
                f'<div style="color:#888;font-size:11px;text-transform:uppercase;'
                f'letter-spacing:1px;margin-bottom:4px;">\U0001f373 Chosen Recipe</div>'
                f'<div style="font-size:14px;color:#ffd700;font-weight:bold;">'
                f'{chef.chosen_recipe.title()}</div>'
                f'</div>'
            )
        else:
            recipe_html = (
                '<div style="background:#12122a;border-radius:8px;padding:8px 10px;'
                'border:1px solid #2a2a3e;">'
                '<div style="color:#666;font-size:12px;font-style:italic;">'
                'No recipe chosen yet</div></div>'
            )

        html = f"""
<div style="font-family:'Courier New',monospace;background:linear-gradient(180deg,#0d0d1a 0%,#1a1a2e 100%);
  color:#e0e0e0;padding:0;border-radius:12px;max-width:750px;border:2px solid #2a2a4e;
  box-shadow:0 4px 24px rgba(0,0,0,0.6);overflow:hidden;">

  <!-- Title bar -->
  <div style="background:linear-gradient(90deg,#1e3a1e,#2d5a2d);padding:8px 16px;
    display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #2d5a2d;">
    <span style="color:#e0e0e0;font-weight:bold;font-size:16px;letter-spacing:2px;">
      \U0001f9d1\u200d\U0001f373 FRIDGE CHEF</span>
    <span style="color:#666;font-size:12px;">Meal planning in progress</span>
  </div>

  <!-- Pipeline progress -->
  <div style="padding:10px 16px 0;">
    {pipeline_html}
  </div>

  <!-- Main content -->
  <div style="display:flex;gap:0;">

    <!-- Left: Fridge -->
    <div style="padding:12px;width:220px;flex-shrink:0;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
        \U0001f9ca Fridge ({len(chef.fridge_contents)} items)</div>
      <div style="background:#0d0d18;border-radius:8px;padding:4px;border:1px solid #2a2a3e;
        max-height:200px;overflow-y:auto;">
        {fridge_html}
      </div>

      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;
        margin-top:10px;margin-bottom:6px;">
        \U0001f6d2 Shopping List ({len(chef.shopping_list)})</div>
      <div style="background:#0d0d18;border-radius:8px;padding:4px;border:1px solid #2a2a3e;
        max-height:120px;overflow-y:auto;">
        {shopping_html}
      </div>
    </div>

    <!-- Right: Stats panel -->
    <div style="padding:12px 12px 12px 0;flex:1;min-width:200px;display:flex;flex-direction:column;gap:10px;">
      {turn_html}
      {recipe_html}
    </div>
  </div>

  <!-- Action log -->
  <div style="border-top:1px solid #2a2a3e;padding:10px 16px;background:#0d0d18;">
    <div style="color:#2d5a2d;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Action</div>
    <div style="color:#16c79a;font-size:13px;margin-top:2px;">{icon} {action}</div>
    <div style="margin-top:6px;padding:8px 10px;background:#12122a;border-radius:6px;
      border-left:3px solid {result_border};font-size:12px;color:{result_color};
      max-height:120px;overflow-y:auto;white-space:pre-wrap;">
{result[:500]}</div>
  </div>
</div>
"""
        display(HTML(html))

    except ImportError:
        print(f"\n{'='*60}")
        print(f"Turn {turn + 1} | {chef.status_text()}")
        print(f"Action: {action}")
        print(f"Result: {result[:300]}")
        print(f"{'='*60}")

    if delay > 0:
        time.sleep(delay)


def display_final(chef: ChefState, turns: int) -> None:
    """Display the final kitchen result."""
    if chef.is_complete:
        title = f"\U0001f373 READY TO COOK: {chef.chosen_recipe.upper()} \U0001f373"
        color = "#ffd700"
        bg = "linear-gradient(180deg,#1a3a1a,#0d0d1a)"
        glow = "text-shadow:0 0 20px #ffd700,0 0 40px #ffd700;"
    else:
        title = "\u23f0 TIME'S UP — COULDN'T DECIDE"
        color = "#e9a045"
        bg = "linear-gradient(180deg,#2a2010,#0d0d1a)"
        glow = "text-shadow:0 0 20px #e9a045;"

    shopping_items = ", ".join(chef.shopping_list) if chef.shopping_list else "Nothing needed!"

    try:
        from IPython.display import display, HTML

        html = f"""
<div style="font-family:'Courier New',monospace;background:{bg};
  color:#e0e0e0;padding:0;border-radius:12px;max-width:680px;border:2px solid {color};
  box-shadow:0 0 30px {color}40;overflow:hidden;">

  <div style="text-align:center;padding:30px 20px 10px;">
    <div style="font-size:24px;font-weight:bold;color:{color};{glow}letter-spacing:3px;">
      {title}</div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:20px;margin:10px 20px;
    background:#0d0d18;border-radius:8px;border:1px solid #2a2a3e;">

    <div style="text-align:center;padding:10px;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;">Recipe</div>
      <div style="font-size:22px;margin-top:4px;color:#ffd700;">
        {chef.chosen_recipe.title() if chef.chosen_recipe else "None"}</div>
    </div>

    <div style="text-align:center;padding:10px;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;">Turns Used</div>
      <div style="font-size:22px;margin-top:4px;color:#7b68ee;">{turns}</div>
    </div>
  </div>

  <div style="padding:0 20px 20px;">
    <div style="background:#0d0d18;border-radius:8px;padding:12px;border:1px solid #2a2a3e;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
        \U0001f6d2 Shopping List</div>
      <div style="font-size:13px;color:#e9a045;">
        {shopping_items}</div>
    </div>
  </div>

  <div style="padding:0 20px 20px;">
    <div style="background:#0d0d18;border-radius:8px;padding:12px;border:1px solid #2a2a3e;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
        Agent Notes</div>
      <div style="font-size:12px;color:#b0b0b0;max-height:120px;overflow-y:auto;">
        {"<br>".join(f"- {n}" for n in chef.notes[-10:]) if chef.notes else "<em>No notes recorded.</em>"}
      </div>
    </div>
  </div>
</div>
"""
        display(HTML(html))

    except ImportError:
        print(f"\n{'#'*60}")
        print(f"  {title}")
        print(f"  Recipe: {chef.chosen_recipe or 'None'}")
        print(f"  Shopping: {shopping_items}")
        print(f"  Turns: {turns}")
        print(f"{'#'*60}")
