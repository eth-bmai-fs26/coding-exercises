"""Interactive play mode for Metal Gear Agent — play the game yourself in a notebook."""

import time
from typing import Optional

from IPython.display import display, clear_output, HTML
import ipywidgets as widgets

from gear_agent.data import CellType, ARMORY_CATALOG, SAFE_ROOM_CATALOG
from gear_agent.scenario import FacilityWorld
from gear_agent.game import OperativeState
from gear_agent.tools import GameTools
from gear_agent.oracle import stub_oracle
from gear_agent.display import (
    _render_html_grid,
    _render_health_bar,
    _render_intel_bar,
    _render_inventory,
    _render_turn_counter,
    _action_icon,
)


class InteractiveGame:
    """Interactive game UI using ipywidgets."""

    def __init__(self, oracle_fn=None):
        self.operative, self.world, self.tools = self._create_game()
        self.tools.set_oracle(oracle_fn or stub_oracle)
        self.turn = 0
        self.max_turns = 100
        self.last_action = ""
        self.last_result = "Mission briefing: Infiltrate the facility and gather 10 intel points. Good luck, operative."
        self.game_over = False

        # -- Widgets --
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
        self._btn_collect = widgets.Button(description="\u270b Collect", layout=act_style,
                                           button_style="success")
        self._btn_engage = widgets.Button(description="\U0001f4a5 Engage", layout=act_style,
                                          button_style="danger")
        self._btn_hide = widgets.Button(description="\U0001f4e6 Hide", layout=act_style,
                                        button_style="warning")
        self._btn_scan = widgets.Button(description="\U0001f441 Scan", layout=act_style,
                                        button_style="info")
        self._btn_sitrep = widgets.Button(description="\U0001f4cb Sitrep", layout=act_style,
                                          button_style="info")
        self._btn_collect.on_click(lambda _: self._do_action("collect", {}))
        self._btn_engage.on_click(lambda _: self._do_action("engage", {}))
        self._btn_hide.on_click(lambda _: self._do_action("hide", {}))
        self._btn_scan.on_click(lambda _: self._do_action("scan", {}))
        self._btn_sitrep.on_click(lambda _: self._do_action("sitrep", {}))

        quick_actions = widgets.HBox(
            [self._btn_collect, self._btn_engage, self._btn_hide,
             self._btn_scan, self._btn_sitrep],
            layout=widgets.Layout(gap="4px"),
        )

        # Codec input
        self._codec_input = widgets.Text(
            placeholder='Ask a question... (e.g. "Do you have a mission for me?")',
            layout=widgets.Layout(flex="1"),
        )
        self._btn_codec = widgets.Button(description="\U0001f4fb Codec", layout=act_style,
                                         button_style="success")
        self._btn_codec.on_click(lambda _: self._do_codec())
        self._codec_input.on_submit(lambda _: self._do_codec())
        codec_row = widgets.HBox(
            [self._codec_input, self._btn_codec],
            layout=widgets.Layout(gap="4px"),
        )

        # Equip/Use input
        self._item_input = widgets.Text(
            placeholder='Item name... (e.g. "EMP Device", "Ration")',
            layout=widgets.Layout(flex="1"),
        )
        self._btn_equip = widgets.Button(description="\U0001f527 Equip", layout=act_style,
                                          button_style="warning")
        self._btn_use = widgets.Button(description="\u2728 Use", layout=act_style,
                                       button_style="info")
        self._btn_equip.on_click(lambda _: self._do_equip())
        self._btn_use.on_click(lambda _: self._do_use())
        self._item_input.on_submit(lambda _: self._do_equip())
        item_row = widgets.HBox(
            [self._item_input, self._btn_equip, self._btn_use],
            layout=widgets.Layout(gap="4px"),
        )

        # Assemble controls panel
        controls_title = widgets.HTML(
            '<div style="font-family:Courier New,monospace;color:#00ff41;'
            'font-weight:bold;font-size:13px;letter-spacing:1px;'
            'padding:4px 0;">CONTROLS</div>'
        )
        move_label = widgets.HTML(
            '<div style="font-family:Courier New,monospace;color:#666;'
            'font-size:11px;margin-top:6px;">MOVE</div>'
        )
        action_label = widgets.HTML(
            '<div style="font-family:Courier New,monospace;color:#666;'
            'font-size:11px;margin-top:8px;">QUICK ACTIONS</div>'
        )
        codec_label = widgets.HTML(
            '<div style="font-family:Courier New,monospace;color:#666;'
            'font-size:11px;margin-top:8px;">CODEC / CONTACT NPC</div>'
        )
        item_label = widgets.HTML(
            '<div style="font-family:Courier New,monospace;color:#666;'
            'font-size:11px;margin-top:8px;">EQUIP / FABRICATE / USE ITEM</div>'
        )

        controls = widgets.VBox(
            [controls_title, move_label, dpad, action_label, quick_actions,
             codec_label, codec_row, item_label, item_row],
            layout=widgets.Layout(padding="8px"),
        )

        self._main = widgets.VBox(
            [self._game_display, controls],
            layout=widgets.Layout(max_width="700px"),
        )

    def _create_game(self):
        world = FacilityWorld()
        operative = OperativeState()
        tools = GameTools(operative, world)
        return operative, world, tools

    def _do_action(self, tool_name: str, args: dict):
        if self.game_over:
            return
        result = self.tools.execute(tool_name, args)
        args_str = ", ".join(f'{k}="{v}"' for k, v in args.items())
        self.last_action = f"{tool_name}({args_str})"
        self.last_result = result.message
        if tool_name not in ("scan", "sitrep"):
            self.turn += 1
        self._check_game_state()
        self._render()

    def _do_codec(self):
        question = self._codec_input.value.strip()
        if not question:
            question = "Report."
        self._codec_input.value = ""
        self._do_action("codec", {"question": question})

    def _do_equip(self):
        item = self._item_input.value.strip()
        if not item:
            return
        self._item_input.value = ""
        self._do_action("equip", {"item": item})

    def _do_use(self):
        item = self._item_input.value.strip()
        if not item:
            return
        self._item_input.value = ""
        self._do_action("use", {"item": item})

    def _check_game_state(self):
        if not self.operative.is_alive:
            self.game_over = True
            self.last_result += " \U0001f480 MISSION FAILED — The operative has been eliminated!"
        elif self.operative.has_won:
            self.game_over = True
            self.last_result += " \U0001f3c6 MISSION COMPLETE — Intel objective achieved!"
        elif self.turn >= self.max_turns:
            self.game_over = True
            self.last_result += " \u23f0 TIME'S UP — Mission window has closed!"

    def _render(self):
        grid_html = _render_html_grid(self.world, self.operative)
        health_html = _render_health_bar(self.operative)
        intel_html = _render_intel_bar(self.operative)
        inventory_html = _render_inventory(self.operative)
        turn_html = _render_turn_counter(self.turn, self.max_turns)
        icon = _action_icon(self.last_action)

        if any(w in self.last_result.lower() for w in
               ["intel", "mission success", "mission complete", "reward", "collected", "fabricated", "earned"]):
            result_color = "#00ff41"
            result_border = "#00ff41"
        elif any(w in self.last_result.lower() for w in
                 ["alert", "damage", "fail", "cannot", "nothing", "retreat", "mission failed"]):
            result_color = "#e94560"
            result_border = "#e94560"
        else:
            result_color = "#8a8a8a"
            result_border = "#333"

        row, col = self.operative.position
        cell = self.world.get_cell(row, col)
        hints = self._get_cell_hints(cell)

        game_over_banner = ""
        if self.game_over:
            if self.operative.has_won:
                game_over_banner = (
                    '<div style="text-align:center;padding:12px;background:#0a1a0a;'
                    'border:2px solid #00ff41;border-radius:8px;margin-top:8px;">'
                    '<span style="font-size:24px;color:#00ff41;text-shadow:0 0 10px #00ff41;'
                    f'font-weight:bold;">MISSION COMPLETE! {self.operative.intel} intel in {self.turn} turns</span></div>'
                )
            elif not self.operative.is_alive:
                game_over_banner = (
                    '<div style="text-align:center;padding:12px;background:#1a0808;'
                    'border:2px solid #e94560;border-radius:8px;margin-top:8px;">'
                    '<span style="font-size:24px;color:#e94560;text-shadow:0 0 10px #e94560;'
                    f'font-weight:bold;">MISSION FAILED after {self.turn} turns</span></div>'
                )
            else:
                game_over_banner = (
                    '<div style="text-align:center;padding:12px;background:#1a1808;'
                    'border:2px solid #e9a045;border-radius:8px;margin-top:8px;">'
                    '<span style="font-size:24px;color:#e9a045;'
                    f'font-weight:bold;">TIME\'S UP! {self.operative.intel}/10 intel</span></div>'
                )

        html = f"""
<div style="font-family:'Courier New',monospace;background:linear-gradient(180deg,#080810 0%,#0a1a0a 100%);
  color:#c0c0c0;padding:0;border-radius:12px;max-width:680px;border:2px solid #1a3a1a;
  box-shadow:0 4px 24px rgba(0,20,0,0.6);overflow:hidden;">

  <!-- Title bar -->
  <div style="background:linear-gradient(90deg,#0a1a0a,#1a2a1a);padding:8px 16px;
    display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #00ff41;">
    <span style="color:#00ff41;font-weight:bold;font-size:16px;letter-spacing:2px;">
      \U0001f575\ufe0f METAL GEAR AGENT</span>
    <span style="color:#00ff41;font-size:13px;font-weight:bold;">INTERACTIVE MODE</span>
    <span style="color:#555;font-size:12px;">({row}, {col})</span>
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
      <div style="background:#0a0a12;border-radius:8px;padding:8px 10px;border:1px solid #1a2a1a;">
        <div style="color:#666;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Health</div>
        {health_html}
      </div>
      <div style="background:#0a0a12;border-radius:8px;padding:8px 10px;border:1px solid #1a2a1a;">
        <div style="color:#666;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Intel</div>
        {intel_html}
      </div>
      <div style="background:#0a0a12;border-radius:8px;padding:8px 10px;border:1px solid #1a2a1a;flex:1;">
        <div style="color:#666;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">
          \U0001f4e6 Equipment</div>
        <div style="font-size:12px;">{inventory_html}</div>
      </div>
    </div>
  </div>

  <!-- Cell info + hints -->
  <div style="padding:6px 16px;background:#060610;border-top:1px solid #1a2a1a;">
    <div style="color:#7b68ee;font-size:12px;">
      <strong>Location:</strong> {cell.description or cell.cell_type.label}
      {hints}
    </div>
  </div>

  <!-- Action log -->
  <div style="border-top:1px solid #1a2a1a;padding:10px 16px;background:#060610;">
    <div style="color:#00ff41;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Last Action</div>
    <div style="color:#00cc33;font-size:13px;margin-top:2px;">{icon} {self.last_action or '(none yet)'}</div>
    <div style="margin-top:6px;padding:8px 10px;background:#0a0a12;border-radius:6px;
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
            hints.append('\U0001f4a1 <span style="color:#00ff41;">Items here! Use Collect</span>')
        if cell.cell_type == CellType.INFORMANT and cell.npc:
            hints.append(f'\U0001f4a1 <span style="color:#00ff41;">Contact: {cell.npc.name} — use Codec</span>')
        if cell.cell_type == CellType.BOSS_ARENA:
            active = True
            if cell.boss_name == "Security Mainframe":
                active = self.world.mainframe_active
            elif cell.boss_name == "Armored Mech":
                active = self.world.mech_active
            if active:
                hints.append(f'\U0001f4a1 <span style="color:#e94560;">{cell.boss_name} here! Engage if you have the right equipment</span>')
            else:
                hints.append('<span style="color:#555;">Target neutralized.</span>')
        if cell.cell_type == CellType.ARMORY:
            armory = ARMORY_CATALOG.get(cell.armory_pos)
            if armory:
                items = list(armory.sells.keys()) + list(armory.crafts.keys())
                hints.append(f'\U0001f4a1 <span style="color:#e9a045;">Armory: {", ".join(items)}</span>')
        if cell.cell_type == CellType.SAFE_ROOM:
            hints.append('\U0001f4a1 <span style="color:#e9a045;">Safe Room: Contact operator or Hide (1 intel)</span>')

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
        from gear_agent.interactive import play_interactive
        play_interactive()

    Or with an LLM oracle:
        play_interactive(oracle_fn=lambda npc, q, o: llm_oracle(npc, q, o, client))
    """
    game = InteractiveGame(oracle_fn=oracle_fn)
    game.play()
    return game
