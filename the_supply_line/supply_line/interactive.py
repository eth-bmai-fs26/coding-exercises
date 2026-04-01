"""Interactive play mode for The Supply Line — play the game yourself in a notebook."""

from IPython.display import display, clear_output, HTML
import ipywidgets as widgets

from supply_line.data import OrderStatus
from supply_line.game import AgentState, SupplyWorld
from supply_line.tools import SupplyTools
from supply_line.display import (
    _render_tokens_bar, _render_quality_bar, _render_resolved_bar,
    _render_turn_counter, _render_queue, _action_icon,
)


class InteractiveGame:
    """Interactive supply line game using ipywidgets."""

    def __init__(self):
        self.agent, self.world, self.tools = self._create_game()
        self.turn = 0
        self.max_turns = 100
        self.last_action = ""
        self.last_result = "Operations begin! Check the order queue and start fulfilling orders."
        self.game_over = False

        btn_layout = widgets.Layout(width="auto", height="36px")

        self._game_display = widgets.Output()

        # Quick actions
        self._btn_check_orders = widgets.Button(
            description="\U0001f4cb Orders", layout=btn_layout, button_style="info")
        self._btn_check_stats = widgets.Button(
            description="\U0001f4ca Stats", layout=btn_layout, button_style="info")
        self._btn_take_break = widgets.Button(
            description="\u2615 Break", layout=btn_layout, button_style="warning")
        self._btn_alternatives = widgets.Button(
            description="\U0001f504 Alternatives", layout=btn_layout, button_style="info")

        self._btn_check_orders.on_click(lambda _: self._do_free("check_orders", {}))
        self._btn_check_stats.on_click(lambda _: self._do_free("check_stats", {}))
        self._btn_take_break.on_click(lambda _: self._do_action("take_break", {}))
        self._btn_alternatives.on_click(lambda _: self._do_action("check_alternatives", {}))

        quick_row = widgets.HBox(
            [self._btn_check_orders, self._btn_check_stats, self._btn_take_break, self._btn_alternatives],
            layout=widgets.Layout(gap="4px"),
        )

        # Read order
        self._order_id_input = widgets.Text(
            placeholder="Order ID (e.g. T-001) or leave blank for next",
            layout=widgets.Layout(flex="1"),
        )
        self._btn_read = widgets.Button(
            description="\U0001f4e8 Read Order", layout=btn_layout, button_style="primary")
        self._btn_read.on_click(lambda _: self._do_read())
        self._order_id_input.on_submit(lambda _: self._do_read())
        read_row = widgets.HBox([self._order_id_input, self._btn_read], layout=widgets.Layout(gap="4px"))

        # Lookup KB
        self._lookup_input = widgets.Text(
            placeholder='Search query (e.g. "reorder procedures")',
            layout=widgets.Layout(flex="1"),
        )
        self._btn_lookup = widgets.Button(
            description="\U0001f50d Lookup KB", layout=btn_layout, button_style="success")
        self._btn_lookup.on_click(lambda _: self._do_lookup())
        self._lookup_input.on_submit(lambda _: self._do_lookup())
        lookup_row = widgets.HBox([self._lookup_input, self._btn_lookup], layout=widgets.Layout(gap="4px"))

        # Check inventory
        self._sku_input = widgets.Text(
            placeholder='SKU (e.g. "SKU-4421")', layout=widgets.Layout(flex="1"))
        self._btn_inventory = widgets.Button(
            description="\U0001f4e6 Inventory", layout=btn_layout, button_style="info")
        self._btn_inventory.on_click(lambda _: self._do_inventory())
        inventory_row = widgets.HBox([self._sku_input, self._btn_inventory], layout=widgets.Layout(gap="4px"))

        # Lookup shipment / Check docs
        self._shipment_input = widgets.Text(
            placeholder='Shipment ID (e.g. "SH-1190")', layout=widgets.Layout(flex="1"))
        self._btn_shipment = widgets.Button(
            description="\U0001f69a Shipment", layout=btn_layout, button_style="info")
        self._btn_docs = widgets.Button(
            description="\U0001f4c4 Docs", layout=btn_layout, button_style="info")
        self._btn_shipment.on_click(lambda _: self._do_shipment())
        self._btn_docs.on_click(lambda _: self._do_docs())
        shipment_row = widgets.HBox(
            [self._shipment_input, self._btn_shipment, self._btn_docs],
            layout=widgets.Layout(gap="4px"))

        # Place order
        self._supplier_input = widgets.Text(
            placeholder='Supplier name', layout=widgets.Layout(flex="1"))
        self._btn_place_order = widgets.Button(
            description="\U0001f4e6 Place Order", layout=btn_layout, button_style="warning")
        self._expedited_check = widgets.Checkbox(value=False, description="Expedited", indent=False)
        self._btn_place_order.on_click(lambda _: self._do_place_order())
        order_row = widgets.HBox(
            [self._supplier_input, self._expedited_check, self._btn_place_order],
            layout=widgets.Layout(gap="4px"))

        # Actions row
        self._action_dropdown = widgets.Dropdown(
            options=[
                ("Select action...", ""),
                ("\u274c Reject Shipment", "reject_shipment"),
                ("\U0001f4b0 File Claim", "file_claim"),
                ("\U0001f4e4 Submit Documents", "submit_documents"),
                ("\U0001f552 Update Timeline", "update_timeline"),
                ("\U0001f9ee Verify Pricing", "verify_pricing"),
                ("\U0001f4c1 Compile Records", "compile_records"),
                ("\U0001f514 Acknowledge Alert", "acknowledge_alert"),
            ],
            layout=widgets.Layout(flex="1"),
        )
        self._btn_apply = widgets.Button(
            description="\u2699 Apply", layout=btn_layout, button_style="warning")
        self._btn_apply.on_click(lambda _: self._do_apply())
        action_row = widgets.HBox([self._action_dropdown, self._btn_apply], layout=widgets.Layout(gap="4px"))

        # Notify client
        self._template_dropdown = widgets.Dropdown(
            options=[
                ("Select template...", ""),
                ("\U0001f4e6 Reorder Confirmation", "reorder_confirmation"),
                ("\U0001f69a Delay Notification", "delay_notification"),
                ("\u26a0 Quality Issue", "quality_issue"),
                ("\U0001f6c3 Customs Update", "customs_update"),
                ("\u26a1 Rush Confirmation", "rush_confirmation"),
                ("\U0001f680 Launch Status", "launch_status"),
                ("\u2696 Compliance Status", "compliance_status"),
                ("\U0001f4b0 Dispute Resolution", "dispute_resolution"),
                ("\U0001f4ac General Update", "general_update"),
            ],
            layout=widgets.Layout(flex="1"),
        )
        self._btn_notify = widgets.Button(
            description="\U0001f4ac Notify", layout=btn_layout, button_style="success")
        self._btn_notify.on_click(lambda _: self._do_notify())
        notify_row = widgets.HBox([self._template_dropdown, self._btn_notify], layout=widgets.Layout(gap="4px"))

        # Escalate
        self._escalate_dropdown = widgets.Dropdown(
            options=[
                ("Select department...", ""),
                ("\U0001f4b0 Procurement", "procurement"),
                ("\U0001f4b3 Finance", "finance"),
                ("\U0001f69a Logistics", "logistics"),
                ("\U0001f527 Engineering", "engineering"),
                ("\u2696 Compliance", "compliance"),
            ],
            layout=widgets.Layout(flex="1"),
        )
        self._btn_escalate = widgets.Button(
            description="\u26a0 Escalate", layout=btn_layout, button_style="danger")
        self._btn_escalate.on_click(lambda _: self._do_escalate())
        escalate_row = widgets.HBox([self._escalate_dropdown, self._btn_escalate], layout=widgets.Layout(gap="4px"))

        # Boss fight buttons
        self._btn_launch_briefing = widgets.Button(
            description="\U0001f680 Launch Briefing", layout=btn_layout, button_style="warning")
        self._btn_authorize = widgets.Button(
            description="\U0001f680 Authorize Launch", layout=btn_layout, button_style="danger")
        self._btn_compliance_pkg = widgets.Button(
            description="\u2696 Compliance Package", layout=btn_layout, button_style="warning")
        self._btn_submit_compliance = widgets.Button(
            description="\u2696 Submit Compliance", layout=btn_layout, button_style="danger")

        self._btn_launch_briefing.on_click(lambda _: self._do_action("prepare_launch_briefing", {}))
        self._btn_authorize.on_click(lambda _: self._do_action("authorize_launch", {"order_id": "T-001"}))
        self._btn_compliance_pkg.on_click(lambda _: self._do_action("prepare_compliance_package", {}))
        self._btn_submit_compliance.on_click(lambda _: self._do_action("submit_compliance", {"order_id": "T-020"}))

        boss_row = widgets.HBox(
            [self._btn_launch_briefing, self._btn_authorize,
             self._btn_compliance_pkg, self._btn_submit_compliance],
            layout=widgets.Layout(gap="4px"))

        # Close order
        self._btn_close = widgets.Button(
            description="\u2705 Close Order", layout=btn_layout, button_style="success")
        self._btn_close.on_click(lambda _: self._do_close())

        def _label(text):
            return widgets.HTML(
                f'<div style="font-family:Courier New,monospace;color:#888;'
                f'font-size:11px;margin-top:6px;">{text}</div>')

        controls = widgets.VBox([
            widgets.HTML('<div style="font-family:Courier New,monospace;color:#0f4630;'
                        'font-weight:bold;font-size:13px;letter-spacing:1px;padding:4px 0;">CONTROLS</div>'),
            _label("QUICK ACTIONS"), quick_row,
            _label("READ ORDER"), read_row,
            _label("SEARCH KNOWLEDGE BASE"), lookup_row,
            _label("CHECK INVENTORY"), inventory_row,
            _label("SHIPMENT / DOCUMENTATION"), shipment_row,
            _label("PLACE ORDER"), order_row,
            _label("APPLY ACTION"), action_row,
            _label("NOTIFY CLIENT"), notify_row,
            _label("ESCALATE"), escalate_row,
            _label("BOSS FIGHT"), boss_row,
            _label(""), self._btn_close,
        ], layout=widgets.Layout(padding="8px"))

        self._main = widgets.VBox(
            [self._game_display, controls],
            layout=widgets.Layout(max_width="780px"),
        )

    def _create_game(self):
        world = SupplyWorld()
        agent = AgentState()
        tools = SupplyTools(agent, world)
        return agent, world, tools

    def _do_free(self, tool_name, args):
        if self.game_over:
            return
        result = self.tools.execute(tool_name, args)
        self.last_action = f"{tool_name}()"
        self.last_result = result.message
        self._render()

    def _do_action(self, tool_name, args):
        if self.game_over:
            return
        result = self.tools.execute(tool_name, args)
        args_str = ", ".join(f'{k}="{v}"' for k, v in args.items())
        self.last_action = f"{tool_name}({args_str})"
        self.last_result = result.message
        self.turn += 1
        self.world.add_late_orders(self.turn)
        self._check_game_state()
        self._render()

    def _do_read(self):
        oid = self._order_id_input.value.strip()
        self._order_id_input.value = ""
        self._do_action("read_order", {"order_id": oid})

    def _do_lookup(self):
        query = self._lookup_input.value.strip()
        if not query:
            return
        self._lookup_input.value = ""
        self._do_action("lookup_kb", {"query": query})

    def _do_inventory(self):
        sku = self._sku_input.value.strip()
        if not sku:
            return
        self._sku_input.value = ""
        self._do_action("check_inventory", {"sku": sku})

    def _do_shipment(self):
        sid = self._shipment_input.value.strip()
        if not sid:
            return
        self._do_action("lookup_shipment", {"shipment_id": sid})

    def _do_docs(self):
        sid = self._shipment_input.value.strip()
        if not sid:
            return
        self._shipment_input.value = ""
        self._do_action("check_documentation", {"shipment_id": sid})

    def _do_place_order(self):
        supplier = self._supplier_input.value.strip()
        if not supplier:
            return
        self._supplier_input.value = ""
        exp = "true" if self._expedited_check.value else "false"
        self._expedited_check.value = False
        self._do_action("place_order", {"supplier": supplier, "expedited": exp})

    def _do_apply(self):
        action = self._action_dropdown.value
        if not action:
            return
        self._action_dropdown.value = ""
        oid = self.world.active_order.id if self.world.active_order else ""
        if action == "reject_shipment":
            sid = self._shipment_input.value.strip() or "active"
            self._do_action("reject_shipment", {"shipment_id": sid, "reason": "QC failure"})
        elif action == "file_claim":
            self._do_action("file_claim", {"supplier": "as specified", "amount": "pending"})
        elif action == "submit_documents":
            sid = self._shipment_input.value.strip() or "active"
            self._do_action("submit_documents", {"shipment_id": sid})
        elif action == "update_timeline":
            self._do_action("update_timeline", {"order_id": oid, "new_eta": "recalculated"})
        elif action == "verify_pricing":
            self._do_action("verify_pricing", {"order_id": oid})
        elif action == "compile_records":
            self._do_action("compile_records", {"period": "30_days"})
        elif action == "acknowledge_alert":
            self._do_action("acknowledge_alert", {"alert_id": oid})

    def _do_notify(self):
        template = self._template_dropdown.value
        if not template:
            return
        self._template_dropdown.value = ""
        self._do_action("notify_client", {"template": template})

    def _do_escalate(self):
        dept = self._escalate_dropdown.value
        if not dept:
            return
        self._escalate_dropdown.value = ""
        self._do_action("escalate", {"department": dept, "reason": "as described"})

    def _do_close(self):
        oid = self.world.active_order.id if self.world.active_order else ""
        self._do_action("close_order", {"order_id": oid})

    def _check_game_state(self):
        if not self.agent.is_alive:
            self.game_over = True
            self.last_result += "\n\U0001f6a8 GAME OVER — Too many violations!"
        elif self.agent.has_won:
            self.game_over = True
            self.last_result += "\n\U0001f3c6 VICTORY — All targets met!"
        elif self.turn >= self.max_turns:
            self.game_over = True
            self.last_result += "\n\u23f0 SHIFT ENDED — Ran out of turns!"

    def _render(self):
        tokens_html = _render_tokens_bar(self.agent)
        quality_html = _render_quality_bar(self.agent)
        resolved_html = _render_resolved_bar(self.agent)
        turn_html = _render_turn_counter(self.turn, self.max_turns)
        queue_html = _render_queue(self.world)
        icon = _action_icon(self.last_action)

        if any(w in self.last_result.lower() for w in
               ["fulfilled", "sent", "processed", "placed", "submitted", "victory",
                "authorized", "prepared", "acknowledged", "notification"]):
            result_color = "#16c79a"
            result_border = "#16c79a"
        elif any(w in self.last_result.lower() for w in
                 ["warning", "lost", "wrong", "fail", "cannot", "game over",
                  "violation", "rejected", "blacklisted"]):
            result_color = "#e94560"
            result_border = "#e94560"
        else:
            result_color = "#b0b0b0"
            result_border = "#444"

        # Active order detail
        active_html = ""
        if self.world.active_order:
            o = self.world.active_order
            entity = self.world.get_entity(o.entity_id)
            ename = entity.name if entity else "Unknown"

            steps = []
            if o.has_been_read:
                steps.append('<span style="color:#16c79a;">\u2705 Read</span>')
            if o.lookup_done:
                steps.append('<span style="color:#16c79a;">\u2705 Lookup</span>')
            elif o.requires_lookup:
                steps.append('<span style="color:#666;">\u2b1c Lookup</span>')
            if o.requires_briefing:
                if o.briefing_prepared:
                    steps.append('<span style="color:#16c79a;">\u2705 Briefing</span>')
                else:
                    steps.append('<span style="color:#e9a045;">\u2b1c Briefing</span>')
            if o.action_applied:
                steps.append('<span style="color:#16c79a;">\u2705 Action</span>')
            elif o.requires_action:
                steps.append('<span style="color:#666;">\u2b1c Action</span>')
            if o.notification_sent:
                steps.append('<span style="color:#16c79a;">\u2705 Notified</span>')
            elif o.correct_template:
                steps.append('<span style="color:#666;">\u2b1c Notify</span>')
            if o.escalated_to:
                steps.append(f'<span style="color:#e9a045;">\u26a0 Escalated to {o.escalated_to}</span>')
            progress = " ".join(steps)

            active_html = (
                f'<div style="background:#12122a;border-radius:8px;padding:10px;'
                f'border:1px solid #2a2a3e;margin-top:8px;">'
                f'<div style="color:#888;font-size:11px;text-transform:uppercase;'
                f'letter-spacing:1px;margin-bottom:6px;">\U0001f4e6 Active Order</div>'
                f'<div style="font-size:14px;color:#e0e0e0;font-weight:bold;">'
                f'{o.priority.emoji} {o.category.emoji} '
                f'<span style="color:#7b68ee;">{o.id}</span> \u2014 {o.subject[:50]}</div>'
                f'<div style="font-size:12px;color:#888;margin-top:4px;">'
                f'{ename} | {o.category.value} | {o.priority.value}</div>'
                f'<div style="font-size:12px;color:#e0e0e0;margin-top:8px;padding:8px;'
                f'background:#0d0d18;border-radius:4px;white-space:pre-wrap;max-height:100px;'
                f'overflow-y:auto;">{o.message}</div>'
                f'<div style="margin-top:6px;font-size:11px;">{progress}</div>'
                f'</div>'
            )
        else:
            active_html = (
                '<div style="background:#12122a;border-radius:8px;padding:10px;'
                'border:1px solid #2a2a3e;margin-top:8px;">'
                '<div style="color:#666;font-size:12px;font-style:italic;text-align:center;'
                'padding:16px;">No active order. Use Read Order to get started.</div></div>'
            )

        game_over_banner = ""
        if self.game_over:
            if self.agent.has_won:
                game_over_banner = (
                    '<div style="text-align:center;padding:12px;background:#1a3a1a;'
                    'border:2px solid #ffd700;border-radius:8px;margin-top:8px;">'
                    '<span style="font-size:24px;color:#ffd700;text-shadow:0 0 10px #ffd700;'
                    f'font-weight:bold;">OPERATIONS COMPLETE! {self.agent.resolved_count} orders, '
                    f'{self.agent.quality_score:.0f}% quality</span></div>'
                )
            elif not self.agent.is_alive:
                game_over_banner = (
                    '<div style="text-align:center;padding:12px;background:#3a1a1a;'
                    'border:2px solid #e94560;border-radius:8px;margin-top:8px;">'
                    '<span style="font-size:24px;color:#e94560;text-shadow:0 0 10px #e94560;'
                    f'font-weight:bold;">TERMINATED after {self.turn} turns</span></div>'
                )
            else:
                game_over_banner = (
                    '<div style="text-align:center;padding:12px;background:#2a2a10;'
                    'border:2px solid #e9a045;border-radius:8px;margin-top:8px;">'
                    '<span style="font-size:24px;color:#e9a045;font-weight:bold;">'
                    f'SHIFT ENDED \u2014 {self.agent.resolved_count}/{self.agent.WIN_RESOLVED} fulfilled</span></div>'
                )

        html = f"""
<div style="font-family:'Courier New',monospace;background:linear-gradient(180deg,#0d0d1a 0%,#1a1a2e 100%);
  color:#e0e0e0;padding:0;border-radius:12px;max-width:750px;border:2px solid #2a4a2e;
  box-shadow:0 4px 24px rgba(0,0,0,0.6);overflow:hidden;">

  <div style="background:linear-gradient(90deg,#1a3e16,#0f4630);padding:8px 16px;
    display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #0f4630;">
    <span style="color:#e0e0e0;font-weight:bold;font-size:16px;letter-spacing:2px;">
      \U0001f69a THE SUPPLY LINE</span>
    <span style="color:#ffd700;font-size:13px;font-weight:bold;">INTERACTIVE MODE</span>
  </div>

  <div style="display:flex;gap:0;">
    <div style="padding:12px;width:280px;flex-shrink:0;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
        \U0001f4e5 Order Queue ({len(self.world.queue)})</div>
      <div style="background:#0d0d18;border-radius:8px;padding:4px;border:1px solid #2a2a3e;
        max-height:200px;overflow-y:auto;">
        {queue_html}
      </div>
    </div>

    <div style="padding:12px 12px 12px 0;flex:1;min-width:200px;display:flex;flex-direction:column;gap:8px;">
      {turn_html}
      <div style="background:#12122a;border-radius:8px;padding:6px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-bottom:2px;">Operations Tokens</div>
        {tokens_html}
      </div>
      <div style="background:#12122a;border-radius:8px;padding:6px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-bottom:2px;">Fulfillment Quality</div>
        {quality_html}
      </div>
      <div style="background:#12122a;border-radius:8px;padding:6px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-bottom:2px;">Orders Fulfilled</div>
        {resolved_html}
      </div>
    </div>
  </div>

  <div style="padding:0 12px;">
    {active_html}
  </div>

  <div style="border-top:1px solid #2a2a3e;padding:10px 16px;background:#0d0d18;margin-top:8px;">
    <div style="color:#0f4630;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Last Action</div>
    <div style="color:#16c79a;font-size:13px;margin-top:2px;">{icon} {self.last_action or "(none yet)"}</div>
    <div style="margin-top:6px;padding:8px 10px;background:#12122a;border-radius:6px;
      border-left:3px solid {result_border};font-size:12px;color:{result_color};
      max-height:100px;overflow-y:auto;white-space:pre-wrap;">{self.last_result}</div>
    {game_over_banner}
  </div>
</div>
"""
        with self._game_display:
            clear_output(wait=True)
            display(HTML(html))

    def play(self):
        self._render()
        display(self._main)


def play_interactive():
    game = InteractiveGame()
    game.play()
    return game
