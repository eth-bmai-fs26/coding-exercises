"""Interactive play mode for Quest Hero — play the game yourself in a notebook."""

import time
from typing import Optional

from IPython.display import display, clear_output, HTML
import ipywidgets as widgets

from quest_hero.game_world import GameWorld, CellType, SHOP_CATALOG, INN_CATALOG
from quest_hero.hero import Hero
from quest_hero.tools import GameTools
from quest_hero.oracle import stub_oracle
from quest_hero.display import (
    _render_html_grid,
    _render_hearts_bar,
    _render_gold_bar,
    _render_inventory,
    _render_turn_counter,
    _action_icon,
)


class InteractiveGame:
    """Interactive game UI using ipywidgets."""

    def __init__(self, oracle_fn=None):
        self.hero, self.world, self.tools = self._create_game()
        self.tools.set_oracle(oracle_fn or stub_oracle)
        self.turn = 0
        self.max_turns = 100
        self.last_action = ""
        self.last_result = "Your quest begins! Explore the world and collect 10 gold."
        self.game_over = False

        # -- Widgets --
        # Display area
        self._game_display = widgets.Output()

        # Direction buttons (cross layout)
        btn_style = widgets.Layout(width="64px", height="40px")
        self._btn_north = widgets.Button(description="\u2b06 N", layout=btn_style,
                                         button_style="primary")
        self._btn_south = widgets.Button(description="\u2b07 S", layout=btn_style,
                                         button_style="primary")
        self._btn_east = widgets.Button(description="\u27a1 E", layout=btn_style,
                                        button_style="primary")
        self._btn_west = widgets.Button(description="\u2b05 W", layout=btn_style,
                                        button_style="primary")
        self._btn_north.on_click(lambda _: self._do_action("move", {"direction": "north"}))
        self._btn_south.on_click(lambda _: self._do_action("move", {"direction": "south"}))
        self._btn_east.on_click(lambda _: self._do_action("move", {"direction": "east"}))
        self._btn_west.on_click(lambda _: self._do_action("move", {"direction": "west"}))

        dpad = widgets.GridBox(
            children=[
                widgets.Label(""),       self._btn_north, widgets.Label(""),
                self._btn_west,          widgets.Label(""),  self._btn_east,
                widgets.Label(""),       self._btn_south, widgets.Label(""),
            ],
            layout=widgets.Layout(
                grid_template_columns="64px 64px 64px",
                grid_template_rows="40px 40px 40px",
                grid_gap="2px",
                justify_items="center",
                align_items="center",
            ),
        )

        # Action buttons
        act_style = widgets.Layout(width="auto", height="36px")
        self._btn_pickup = widgets.Button(description="\u270b Pick Up", layout=act_style,
                                          button_style="success")
        self._btn_fight = widgets.Button(description="\u2694 Fight", layout=act_style,
                                         button_style="danger")
        self._btn_rest = widgets.Button(description="\U0001f634 Rest", layout=act_style,
                                        button_style="warning")
        self._btn_look = widgets.Button(description="\U0001f441 Look", layout=act_style,
                                        button_style="info")
        self._btn_status = widgets.Button(description="\U0001f4cb Status", layout=act_style,
                                          button_style="info")
        self._btn_pickup.on_click(lambda _: self._do_action("pick_up", {}))
        self._btn_fight.on_click(lambda _: self._do_action("fight", {}))
        self._btn_rest.on_click(lambda _: self._do_action("rest", {}))
        self._btn_look.on_click(lambda _: self._do_action("look", {}))
        self._btn_status.on_click(lambda _: self._do_action("status", {}))

        quick_actions = widgets.HBox(
            [self._btn_pickup, self._btn_fight, self._btn_rest,
             self._btn_look, self._btn_status],
            layout=widgets.Layout(gap="4px"),
        )

        # Talk input
        self._talk_input = widgets.Text(
            placeholder='Ask a question... (e.g. "Do you have a job for me?")',
            layout=widgets.Layout(flex="1"),
        )
        self._btn_talk = widgets.Button(description="\U0001f4ac Talk", layout=act_style,
                                        button_style="success")
        self._btn_talk.on_click(lambda _: self._do_talk())
        self._talk_input.on_submit(lambda _: self._do_talk())
        talk_row = widgets.HBox(
            [self._talk_input, self._btn_talk],
            layout=widgets.Layout(gap="4px"),
        )

        # Buy/Use input
        self._item_input = widgets.Text(
            placeholder='Item name... (e.g. "Sunblade", "Bread")',
            layout=widgets.Layout(flex="1"),
        )
        self._btn_buy = widgets.Button(description="\U0001f4b0 Buy/Craft", layout=act_style,
                                       button_style="warning")
        self._btn_use = widgets.Button(description="\u2728 Use", layout=act_style,
                                       button_style="info")
        self._btn_buy.on_click(lambda _: self._do_buy())
        self._btn_use.on_click(lambda _: self._do_use())
        self._item_input.on_submit(lambda _: self._do_buy())
        item_row = widgets.HBox(
            [self._item_input, self._btn_buy, self._btn_use],
            layout=widgets.Layout(gap="4px"),
        )

        # Assemble controls panel
        controls_title = widgets.HTML(
            '<div style="font-family:Courier New,monospace;color:#e94560;'
            'font-weight:bold;font-size:13px;letter-spacing:1px;'
            'padding:4px 0;">CONTROLS</div>'
        )
        move_label = widgets.HTML(
            '<div style="font-family:Courier New,monospace;color:#888;'
            'font-size:11px;margin-top:6px;">MOVE</div>'
        )
        action_label = widgets.HTML(
            '<div style="font-family:Courier New,monospace;color:#888;'
            'font-size:11px;margin-top:8px;">QUICK ACTIONS</div>'
        )
        talk_label = widgets.HTML(
            '<div style="font-family:Courier New,monospace;color:#888;'
            'font-size:11px;margin-top:8px;">TALK TO NPC / INNKEEPER</div>'
        )
        item_label = widgets.HTML(
            '<div style="font-family:Courier New,monospace;color:#888;'
            'font-size:11px;margin-top:8px;">BUY / CRAFT / USE ITEM</div>'
        )

        controls = widgets.VBox(
            [controls_title, move_label, dpad, action_label, quick_actions,
             talk_label, talk_row, item_label, item_row],
            layout=widgets.Layout(padding="8px"),
        )

        # Main layout: game display on top, controls below
        self._main = widgets.VBox(
            [self._game_display, controls],
            layout=widgets.Layout(max_width="700px"),
        )

    def _create_game(self):
        world = GameWorld()
        hero = Hero()
        tools = GameTools(hero, world)
        return hero, world, tools

    def _do_action(self, tool_name: str, args: dict):
        if self.game_over:
            return
        result = self.tools.execute(tool_name, args)
        args_str = ", ".join(f'{k}="{v}"' for k, v in args.items())
        self.last_action = f"{tool_name}({args_str})"
        self.last_result = result.message
        if tool_name not in ("look", "status"):
            self.turn += 1
        self._check_game_state()
        self._render()

    def _do_talk(self):
        question = self._talk_input.value.strip()
        if not question:
            question = "Hello!"
        self._talk_input.value = ""
        self._do_action("talk", {"question": question})

    def _do_buy(self):
        item = self._item_input.value.strip()
        if not item:
            return
        self._item_input.value = ""
        self._do_action("buy", {"item": item})

    def _do_use(self):
        item = self._item_input.value.strip()
        if not item:
            return
        self._item_input.value = ""
        self._do_action("use", {"item": item})

    def _check_game_state(self):
        if not self.hero.is_alive:
            self.game_over = True
            self.last_result += " \U0001f480 GAME OVER — The hero has fallen!"
        elif self.hero.has_won:
            self.game_over = True
            self.last_result += " \U0001f3c6 VICTORY — You collected enough gold!"
        elif self.turn >= self.max_turns:
            self.game_over = True
            self.last_result += " \u23f0 TIME'S UP — Ran out of turns!"

    def _render(self):
        grid_html = _render_html_grid(self.world, self.hero)
        hearts_html = _render_hearts_bar(self.hero)
        gold_html = _render_gold_bar(self.hero)
        inventory_html = _render_inventory(self.hero)
        turn_html = _render_turn_counter(self.turn, self.max_turns)
        icon = _action_icon(self.last_action)

        if any(w in self.last_result.lower() for w in
               ["gold", "victory", "reward", "found", "picked up", "crafted", "defeated"]):
            result_color = "#16c79a"
            result_border = "#16c79a"
        elif any(w in self.last_result.lower() for w in
                 ["damage", "hurt", "fail", "cannot", "nothing", "retreat", "game over"]):
            result_color = "#e94560"
            result_border = "#e94560"
        else:
            result_color = "#b0b0b0"
            result_border = "#444"

        # Cell context hints
        row, col = self.hero.position
        cell = self.world.get_cell(row, col)
        hints = self._get_cell_hints(cell)

        game_over_banner = ""
        if self.game_over:
            if self.hero.has_won:
                game_over_banner = (
                    '<div style="text-align:center;padding:12px;background:#1a3a1a;'
                    'border:2px solid #ffd700;border-radius:8px;margin-top:8px;">'
                    '<span style="font-size:24px;color:#ffd700;text-shadow:0 0 10px #ffd700;'
                    f'font-weight:bold;">VICTORY! {self.hero.gold} gold in {self.turn} turns</span></div>'
                )
            elif not self.hero.is_alive:
                game_over_banner = (
                    '<div style="text-align:center;padding:12px;background:#3a1a1a;'
                    'border:2px solid #e94560;border-radius:8px;margin-top:8px;">'
                    '<span style="font-size:24px;color:#e94560;text-shadow:0 0 10px #e94560;'
                    f'font-weight:bold;">GAME OVER after {self.turn} turns</span></div>'
                )
            else:
                game_over_banner = (
                    '<div style="text-align:center;padding:12px;background:#2a2a10;'
                    'border:2px solid #e9a045;border-radius:8px;margin-top:8px;">'
                    '<span style="font-size:24px;color:#e9a045;'
                    f'font-weight:bold;">TIME\'S UP! {self.hero.gold}/10 gold</span></div>'
                )

        html = f"""
<div style="font-family:'Courier New',monospace;background:linear-gradient(180deg,#0d0d1a 0%,#1a1a2e 100%);
  color:#e0e0e0;padding:0;border-radius:12px;max-width:680px;border:2px solid #2a2a4e;
  box-shadow:0 4px 24px rgba(0,0,0,0.6);overflow:hidden;">

  <!-- Title bar -->
  <div style="background:linear-gradient(90deg,#16213e,#0f3460);padding:8px 16px;
    display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #e94560;">
    <span style="color:#e94560;font-weight:bold;font-size:16px;letter-spacing:2px;">
      \u2694\ufe0f QUEST HERO</span>
    <span style="color:#ffd700;font-size:13px;font-weight:bold;">INTERACTIVE MODE</span>
    <span style="color:#666;font-size:12px;">({row}, {col})</span>
  </div>

  <!-- Main content -->
  <div style="display:flex;gap:0;">
    <!-- Left: Map -->
    <div style="padding:12px;flex-shrink:0;">
      {grid_html}
    </div>

    <!-- Right: Stats panel -->
    <div style="padding:12px 12px 12px 0;flex:1;min-width:200px;display:flex;flex-direction:column;gap:10px;">
      {turn_html}
      <div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Health</div>
        {hearts_html}
      </div>
      <div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Gold</div>
        {gold_html}
      </div>
      <div style="background:#12122a;border-radius:8px;padding:8px 10px;border:1px solid #2a2a3e;flex:1;">
        <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">
          \U0001f392 Inventory</div>
        <div style="font-size:12px;">{inventory_html}</div>
      </div>
    </div>
  </div>

  <!-- Cell info + hints -->
  <div style="padding:6px 16px;background:#0d0d15;border-top:1px solid #2a2a3e;">
    <div style="color:#7b68ee;font-size:12px;">
      <strong>Location:</strong> {cell.description or cell.cell_type.label}
      {hints}
    </div>
  </div>

  <!-- Action log -->
  <div style="border-top:1px solid #2a2a3e;padding:10px 16px;background:#0d0d18;">
    <div style="color:#e94560;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Last Action</div>
    <div style="color:#16c79a;font-size:13px;margin-top:2px;">{icon} {self.last_action or '(none yet)'}</div>
    <div style="margin-top:6px;padding:8px 10px;background:#12122a;border-radius:6px;
      border-left:3px solid {result_border};font-size:12px;color:{result_color};
      max-height:80px;overflow-y:auto;">
      {self.last_result}
    </div>
    {game_over_banner}
  </div>
</div>
"""
        with self._game_display:
            clear_output(wait=True)
            display(HTML(html))

    def _get_cell_hints(self, cell) -> str:
        """Generate contextual hints about what actions are available."""
        hints = []
        if cell.items:
            hints.append('\U0001f4a1 <span style="color:#16c79a;">Items here! Use Pick Up</span>')
        if cell.cell_type == CellType.NPC and cell.npc:
            hints.append(f'\U0001f4a1 <span style="color:#16c79a;">Talk to {cell.npc.name}</span>')
        if cell.cell_type == CellType.DRAGON:
            alive = True
            if cell.dragon_name == "Frost Wyrm":
                alive = self.world.frost_wyrm_alive
            elif cell.dragon_name == "Shadow Beast":
                alive = self.world.shadow_beast_alive
            if alive:
                hints.append(f'\U0001f4a1 <span style="color:#e94560;">{cell.dragon_name} here! Fight if you have the right weapon</span>')
            else:
                hints.append('<span style="color:#666;">The creature has been slain.</span>')
        if cell.cell_type == CellType.SHOP:
            shop = SHOP_CATALOG.get(cell.shop_pos)
            if shop:
                items = list(shop.sells.keys()) + list(shop.crafts.keys())
                hints.append(f'\U0001f4a1 <span style="color:#e9a045;">Shop: {", ".join(items)}</span>')
        if cell.cell_type == CellType.INN:
            hints.append('\U0001f4a1 <span style="color:#e9a045;">Inn: Talk to innkeeper or Rest (1 gold)</span>')

        if hints:
            return '<br>' + '<br>'.join(hints)
        return ''

    def play(self):
        """Start the interactive game. Call this in a notebook cell."""
        self._render()
        display(self._main)


def play_interactive(oracle_fn=None):
    """Launch an interactive game session.

    Usage in a notebook cell:
        from quest_hero.interactive import play_interactive
        play_interactive()

    Or with an LLM oracle:
        play_interactive(oracle_fn=lambda npc, q, h: llm_oracle(npc, q, h, client))
    """
    game = InteractiveGame(oracle_fn=oracle_fn)
    game.play()
    return game
