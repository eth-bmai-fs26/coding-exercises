"""Interactive play mode for Fridge Chef — play the game yourself in a notebook."""

from IPython.display import display, clear_output, HTML
import ipywidgets as widgets

from fridge_chef.data import ChefState
from fridge_chef.game import KitchenWorld
from fridge_chef.tools import KitchenTools
from fridge_chef.display import (
    _render_pipeline, _render_fridge, _render_shopping_list,
    _render_turn_counter, _action_icon,
)


class InteractiveGame:
    """Interactive kitchen game using ipywidgets."""

    def __init__(self):
        self.chef, self.world, self.tools = self._create_game()
        self.turn = 0
        self.max_turns = 20
        self.last_action = ""
        self.last_result = "Welcome to Fridge Chef! Check your fridge and find something to cook."
        self.game_over = False

        # -- Widgets --
        self._game_display = widgets.Output()

        btn_layout = widgets.Layout(width="auto", height="36px")

        # Check fridge button
        self._btn_check_fridge = widgets.Button(
            description="\U0001f9ca Check Fridge", layout=btn_layout, button_style="info")
        self._btn_check_fridge.on_click(lambda _: self._do_action("check_fridge", {}))

        # Search recipes
        self._search_input = widgets.Text(
            placeholder='Ingredient (e.g. "eggs")',
            layout=widgets.Layout(flex="1"),
        )
        self._btn_search = widgets.Button(
            description="\U0001f50d Search Recipes", layout=btn_layout, button_style="success")
        self._btn_search.on_click(lambda _: self._do_search())
        self._search_input.on_submit(lambda _: self._do_search())
        search_row = widgets.HBox(
            [self._search_input, self._btn_search],
            layout=widgets.Layout(gap="4px"),
        )

        # Get ingredients
        self._recipe_input = widgets.Text(
            placeholder='Recipe name (e.g. "omelette")',
            layout=widgets.Layout(flex="1"),
        )
        self._btn_ingredients = widgets.Button(
            description="\U0001f4cb Get Ingredients", layout=btn_layout, button_style="success")
        self._btn_ingredients.on_click(lambda _: self._do_get_ingredients())
        self._recipe_input.on_submit(lambda _: self._do_get_ingredients())
        recipe_row = widgets.HBox(
            [self._recipe_input, self._btn_ingredients],
            layout=widgets.Layout(gap="4px"),
        )

        # Add to shopping list
        self._shopping_input = widgets.Text(
            placeholder='Item to add (e.g. "paprika")',
            layout=widgets.Layout(flex="1"),
        )
        self._btn_add = widgets.Button(
            description="\U0001f6d2 Add to List", layout=btn_layout, button_style="warning")
        self._btn_add.on_click(lambda _: self._do_add_shopping())
        self._shopping_input.on_submit(lambda _: self._do_add_shopping())
        shopping_row = widgets.HBox(
            [self._shopping_input, self._btn_add],
            layout=widgets.Layout(gap="4px"),
        )

        # Done button
        self._btn_done = widgets.Button(
            description="\u2705 Done!", layout=btn_layout, button_style="success")
        self._btn_done.on_click(lambda _: self._do_action("done", {}))

        # Labels
        def _label(text):
            return widgets.HTML(
                f'<div style="font-family:Courier New,monospace;color:#888;'
                f'font-size:11px;margin-top:6px;">{text}</div>'
            )

        controls_title = widgets.HTML(
            '<div style="font-family:Courier New,monospace;color:#2d5a2d;'
            'font-weight:bold;font-size:13px;letter-spacing:1px;'
            'padding:4px 0;">CONTROLS</div>'
        )

        controls = widgets.VBox([
            controls_title,
            _label("FRIDGE"), self._btn_check_fridge,
            _label("SEARCH RECIPES BY INGREDIENT"), search_row,
            _label("GET RECIPE INGREDIENTS"), recipe_row,
            _label("ADD TO SHOPPING LIST"), shopping_row,
            _label(""), self._btn_done,
        ], layout=widgets.Layout(padding="8px"))

        self._main = widgets.VBox(
            [self._game_display, controls],
            layout=widgets.Layout(max_width="780px"),
        )

    def _create_game(self):
        world = KitchenWorld()
        chef = ChefState()
        tools = KitchenTools(chef, world)
        return chef, world, tools

    def _do_action(self, tool_name, args):
        """Execute a tool action."""
        if self.game_over:
            return
        result = self.tools.execute(tool_name, args)
        args_str = ", ".join(f'{k}="{v}"' for k, v in args.items())
        self.last_action = f"{tool_name}({args_str})"
        self.last_result = result.message
        self.turn += 1
        self._check_game_state()
        self._render()

    def _do_search(self):
        ingredient = self._search_input.value.strip()
        if not ingredient:
            return
        self._search_input.value = ""
        self._do_action("search_recipes", {"ingredient": ingredient})

    def _do_get_ingredients(self):
        recipe = self._recipe_input.value.strip()
        if not recipe:
            return
        self._recipe_input.value = ""
        self._do_action("get_ingredients", {"recipe": recipe})

    def _do_add_shopping(self):
        item = self._shopping_input.value.strip()
        if not item:
            return
        self._shopping_input.value = ""
        self._do_action("add_to_shopping_list", {"item": item})

    def _check_game_state(self):
        if self.chef.is_complete:
            self.game_over = True
            self.last_result += f"\n\U0001f373 Ready to cook {self.chef.chosen_recipe}!"
        elif self.turn >= self.max_turns:
            self.game_over = True
            self.last_result += "\n\u23f0 Time's up! Ran out of turns."

    def _render(self):
        pipeline_html = _render_pipeline(self.chef)
        turn_html = _render_turn_counter(self.turn, self.max_turns)
        fridge_html = _render_fridge(self.chef)
        shopping_html = _render_shopping_list(self.chef)
        icon = _action_icon(self.last_action)

        # Avoid showing the full fridge list in the result area — it's already in the panel
        if self.last_action.startswith("check_fridge"):
            display_result = f"\u2713 {len(self.chef.fridge_contents)} items loaded — see panel on the left."
        else:
            display_result = self.last_result

        if any(w in self.last_result.lower() for w in
               ["done", "added", "recipes using", "you need", "contains", "complete", "ready"]):
            result_color = "#16c79a"
            result_border = "#16c79a"
        elif any(w in self.last_result.lower() for w in
                 ["not found", "already", "please", "unknown", "error"]):
            result_color = "#e94560"
            result_border = "#e94560"
        else:
            result_color = "#b0b0b0"
            result_border = "#444"

        # Recipe info
        recipe_html = ""
        if self.chef.chosen_recipe:
            recipe_html = (
                f'<div style="background:#12122a;border-radius:8px;padding:8px 10px;'
                f'border:1px solid #2a2a3e;margin-top:8px;">'
                f'<div style="color:#888;font-size:11px;text-transform:uppercase;'
                f'letter-spacing:1px;margin-bottom:4px;">\U0001f373 Chosen Recipe</div>'
                f'<div style="font-size:16px;color:#ffd700;font-weight:bold;">'
                f'{self.chef.chosen_recipe.title()}</div>'
                f'</div>'
            )

        game_over_banner = ""
        if self.game_over:
            if self.chef.is_complete:
                game_over_banner = (
                    '<div style="text-align:center;padding:12px;background:#1a3a1a;'
                    'border:2px solid #ffd700;border-radius:8px;margin-top:8px;">'
                    f'<span style="font-size:20px;color:#ffd700;text-shadow:0 0 10px #ffd700;'
                    f'font-weight:bold;">READY TO COOK: {self.chef.chosen_recipe.upper()}</span></div>'
                )
            else:
                game_over_banner = (
                    '<div style="text-align:center;padding:12px;background:#2a2a10;'
                    'border:2px solid #e9a045;border-radius:8px;margin-top:8px;">'
                    '<span style="font-size:20px;color:#e9a045;font-weight:bold;">'
                    'TIME\'S UP</span></div>'
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
    <span style="color:#ffd700;font-size:13px;font-weight:bold;">INTERACTIVE MODE</span>
  </div>

  <!-- Pipeline -->
  <div style="padding:10px 16px 0;">
    {pipeline_html}
  </div>

  <!-- Main content -->
  <div style="display:flex;gap:0;">
    <!-- Left: Fridge + Shopping -->
    <div style="padding:12px;width:220px;flex-shrink:0;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
        \U0001f9ca Fridge ({len(self.chef.fridge_contents)})</div>
      <div style="background:#0d0d18;border-radius:8px;padding:4px;border:1px solid #2a2a3e;
        max-height:180px;overflow-y:auto;">
        {fridge_html}
      </div>

      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;
        margin-top:10px;margin-bottom:6px;">
        \U0001f6d2 Shopping ({len(self.chef.shopping_list)})</div>
      <div style="background:#0d0d18;border-radius:8px;padding:4px;border:1px solid #2a2a3e;
        max-height:100px;overflow-y:auto;">
        {shopping_html}
      </div>
    </div>

    <!-- Right: Stats -->
    <div style="padding:12px 12px 12px 0;flex:1;min-width:200px;display:flex;flex-direction:column;gap:8px;">
      {turn_html}
      {recipe_html}
    </div>
  </div>

  <!-- Action log -->
  <div style="border-top:1px solid #2a2a3e;padding:10px 16px;background:#0d0d18;margin-top:8px;">
    <div style="color:#2d5a2d;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Last Action</div>
    <div style="color:#16c79a;font-size:13px;margin-top:2px;">{icon} {self.last_action or "(none yet)"}</div>
    <div style="margin-top:6px;padding:8px 10px;background:#12122a;border-radius:6px;
      border-left:3px solid {result_border};font-size:12px;color:{result_color};
      max-height:120px;overflow-y:auto;white-space:pre-wrap;">{display_result}</div>
    {game_over_banner}
  </div>
</div>
"""
        with self._game_display:
            clear_output(wait=True)
            display(HTML(html))

    def play(self):
        """Start the interactive game."""
        self._render()
        display(self._main)


def play_interactive():
    """Launch an interactive Fridge Chef session.

    Usage:
        from fridge_chef.interactive import play_interactive
        play_interactive()
    """
    game = InteractiveGame()
    game.play()
    return game
