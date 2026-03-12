"""Interactive play mode for The Support Desk — play the game yourself in a notebook."""

from IPython.display import display, clear_output, HTML
import ipywidgets as widgets

from support_desk.data import TicketStatus
from support_desk.game import AgentState, SupportWorld
from support_desk.tools import SupportTools
from support_desk.display import (
    _render_tokens_bar, _render_csat_bar, _render_resolved_bar,
    _render_turn_counter, _render_queue, _action_icon,
)


class InteractiveGame:
    """Interactive support desk game using ipywidgets."""

    def __init__(self):
        self.agent, self.world, self.tools = self._create_game()
        self.turn = 0
        self.max_turns = 100
        self.last_action = ""
        self.last_result = "Your shift begins! Open tickets from the queue and start resolving them."
        self.game_over = False

        # -- Widgets --
        self._game_display = widgets.Output()

        btn_layout = widgets.Layout(width="auto", height="36px")

        # Queue buttons
        self._btn_check_queue = widgets.Button(
            description="\U0001f4cb Queue", layout=btn_layout, button_style="info")
        self._btn_check_stats = widgets.Button(
            description="\U0001f4ca Stats", layout=btn_layout, button_style="info")
        self._btn_take_break = widgets.Button(
            description="\u2615 Break", layout=btn_layout, button_style="warning")

        self._btn_check_queue.on_click(lambda _: self._do_free("check_queue", {}))
        self._btn_check_stats.on_click(lambda _: self._do_free("check_stats", {}))
        self._btn_take_break.on_click(lambda _: self._do_action("take_break", {}))

        quick_row = widgets.HBox(
            [self._btn_check_queue, self._btn_check_stats, self._btn_take_break],
            layout=widgets.Layout(gap="4px"),
        )

        # Open ticket
        self._ticket_id_input = widgets.Text(
            placeholder="Ticket ID (e.g. T-001) or leave blank for next",
            layout=widgets.Layout(flex="1"),
        )
        self._btn_open = widgets.Button(
            description="\U0001f4e8 Open Ticket", layout=btn_layout, button_style="primary")
        self._btn_open.on_click(lambda _: self._do_open())
        self._ticket_id_input.on_submit(lambda _: self._do_open())
        open_row = widgets.HBox(
            [self._ticket_id_input, self._btn_open],
            layout=widgets.Layout(gap="4px"),
        )

        # Lookup
        self._lookup_input = widgets.Text(
            placeholder='Search query (e.g. "billing duplicate charge")',
            layout=widgets.Layout(flex="1"),
        )
        self._btn_lookup = widgets.Button(
            description="\U0001f50d Lookup", layout=btn_layout, button_style="success")
        self._btn_lookup.on_click(lambda _: self._do_lookup())
        self._lookup_input.on_submit(lambda _: self._do_lookup())
        lookup_row = widgets.HBox(
            [self._lookup_input, self._btn_lookup],
            layout=widgets.Layout(gap="4px"),
        )

        # Reply
        self._reply_input = widgets.Textarea(
            placeholder="Type your reply to the customer...",
            layout=widgets.Layout(flex="1", height="60px"),
        )
        self._btn_reply = widgets.Button(
            description="\U0001f4ac Reply", layout=btn_layout, button_style="success")
        self._btn_reply.on_click(lambda _: self._do_reply())
        reply_row = widgets.HBox(
            [self._reply_input, self._btn_reply],
            layout=widgets.Layout(gap="4px"),
        )

        # Apply action
        self._action_dropdown = widgets.Dropdown(
            options=[
                ("Select an action...", ""),
                ("\U0001f511 Reset Password", "reset_password"),
                ("\U0001f4b3 Issue Refund", "issue_refund"),
                ("\U0001f6ab Close Spam", "close_spam"),
                ("\u2699 Adjust Rate Limit", "adjust_rate_limit"),
                ("\U0001f4dd Update Billing Profile", "update_billing_profile"),
                ("\U0001f41b Update Known Bugs", "update_known_bugs"),
                ("\u2b50 Reply VIP Confirmation", "reply_vip_confirmation"),
                ("\u2705 Confirm Rate Fix", "confirm_rate_fix"),
            ],
            layout=widgets.Layout(flex="1"),
        )
        self._btn_apply = widgets.Button(
            description="\u2699 Apply", layout=btn_layout, button_style="warning")
        self._btn_apply.on_click(lambda _: self._do_apply())
        action_row = widgets.HBox(
            [self._action_dropdown, self._btn_apply],
            layout=widgets.Layout(gap="4px"),
        )

        # Escalate
        self._escalate_dropdown = widgets.Dropdown(
            options=[
                ("Select a team...", ""),
                ("\U0001f4b3 Billing", "billing"),
                ("\U0001f527 Engineering", "engineering"),
                ("\u2b50 Account Management", "account_management"),
                ("\u2696 Legal", "legal"),
                ("\U0001f512 Security", "security"),
            ],
            layout=widgets.Layout(flex="1"),
        )
        self._btn_escalate = widgets.Button(
            description="\u26a0 Escalate", layout=btn_layout, button_style="danger")
        self._btn_escalate.on_click(lambda _: self._do_escalate())
        escalate_row = widgets.HBox(
            [self._escalate_dropdown, self._btn_escalate],
            layout=widgets.Layout(gap="4px"),
        )

        # Use template
        self._template_dropdown = widgets.Dropdown(
            options=[
                ("Select a template...", ""),
                ("\U0001f511 Password Reset", "password_reset"),
                ("\U0001f4e4 Export Guide", "export_guide"),
                ("\U0001f41b Known Bug ETA", "known_bug_eta"),
                ("\U0001f4a1 Feature Request Logged", "feature_request_logged"),
                ("\U0001f510 SSO Guide", "sso_guide"),
                ("\u26a0 Escalation Ack", "escalation_ack"),
                ("\U0001f4b3 Refund Confirmation", "refund_confirmation"),
                ("\U0001f6ab Spam Close", "spam_close"),
            ],
            layout=widgets.Layout(flex="1"),
        )
        self._btn_template = widgets.Button(
            description="\U0001f4dd Template", layout=btn_layout, button_style="success")
        self._btn_template.on_click(lambda _: self._do_template())
        template_row = widgets.HBox(
            [self._template_dropdown, self._btn_template],
            layout=widgets.Layout(gap="4px"),
        )

        # Resolve
        self._btn_resolve = widgets.Button(
            description="\u2705 Resolve Ticket", layout=btn_layout, button_style="success")
        self._btn_resolve.on_click(lambda _: self._do_resolve())

        # Labels
        def _label(text):
            return widgets.HTML(
                f'<div style="font-family:Courier New,monospace;color:#888;'
                f'font-size:11px;margin-top:6px;">{text}</div>'
            )

        controls_title = widgets.HTML(
            '<div style="font-family:Courier New,monospace;color:#0f3460;'
            'font-weight:bold;font-size:13px;letter-spacing:1px;'
            'padding:4px 0;">CONTROLS</div>'
        )

        controls = widgets.VBox([
            controls_title,
            _label("QUICK ACTIONS"), quick_row,
            _label("OPEN TICKET"), open_row,
            _label("SEARCH KNOWLEDGE BASE"), lookup_row,
            _label("REPLY TO CUSTOMER"), reply_row,
            _label("APPLY ACTION"), action_row,
            _label("USE TEMPLATE"), template_row,
            _label("ESCALATE TO TEAM"), escalate_row,
            _label(""), self._btn_resolve,
        ], layout=widgets.Layout(padding="8px"))

        self._main = widgets.VBox(
            [self._game_display, controls],
            layout=widgets.Layout(max_width="780px"),
        )

    def _create_game(self):
        world = SupportWorld()
        agent = AgentState()
        tools = SupportTools(agent, world)
        return agent, world, tools

    def _do_free(self, tool_name, args):
        """Free actions (don't cost a turn)."""
        if self.game_over:
            return
        result = self.tools.execute(tool_name, args)
        self.last_action = f"{tool_name}()"
        self.last_result = result.message
        self._render()

    def _do_action(self, tool_name, args):
        """Actions that cost a turn."""
        if self.game_over:
            return
        result = self.tools.execute(tool_name, args)
        args_str = ", ".join(f'{k}="{v}"' for k, v in args.items())
        self.last_action = f"{tool_name}({args_str})"
        self.last_result = result.message
        self.turn += 1
        self.world.add_late_tickets(self.turn)
        self._check_game_state()
        self._render()

    def _do_open(self):
        tid = self._ticket_id_input.value.strip()
        self._ticket_id_input.value = ""
        self._do_action("open_ticket", {"ticket_id": tid})

    def _do_lookup(self):
        query = self._lookup_input.value.strip()
        if not query:
            return
        self._lookup_input.value = ""
        self._do_action("lookup", {"query": query})

    def _do_reply(self):
        message = self._reply_input.value.strip()
        if not message:
            return
        self._reply_input.value = ""
        tid = self.world.active_ticket.id if self.world.active_ticket else ""
        self._do_action("reply", {"ticket_id": tid, "message": message})

    def _do_apply(self):
        action = self._action_dropdown.value
        if not action:
            return
        self._action_dropdown.value = ""
        tid = self.world.active_ticket.id if self.world.active_ticket else ""
        self._do_action("apply_action", {"ticket_id": tid, "action": action})

    def _do_escalate(self):
        team = self._escalate_dropdown.value
        if not team:
            return
        self._escalate_dropdown.value = ""
        tid = self.world.active_ticket.id if self.world.active_ticket else ""
        self._do_action("escalate", {"ticket_id": tid, "team": team})

    def _do_template(self):
        template = self._template_dropdown.value
        if not template:
            return
        self._template_dropdown.value = ""
        tid = self.world.active_ticket.id if self.world.active_ticket else ""
        self._do_action("use_template", {"ticket_id": tid, "template": template})

    def _do_resolve(self):
        tid = self.world.active_ticket.id if self.world.active_ticket else ""
        self._do_action("resolve_ticket", {"ticket_id": tid})

    def _check_game_state(self):
        if not self.agent.is_alive:
            self.game_over = True
            self.last_result += "\n\U0001f6a8 GAME OVER — Too many bad escalations!"
        elif self.agent.has_won:
            self.game_over = True
            self.last_result += "\n\U0001f3c6 VICTORY — All targets met!"
        elif self.turn >= self.max_turns:
            self.game_over = True
            self.last_result += "\n\u23f0 SHIFT ENDED — Ran out of turns!"

    def _render(self):
        tokens_html = _render_tokens_bar(self.agent)
        csat_html = _render_csat_bar(self.agent)
        resolved_html = _render_resolved_bar(self.agent)
        turn_html = _render_turn_counter(self.turn, self.max_turns)
        queue_html = _render_queue(self.world)
        icon = _action_icon(self.last_action)

        if any(w in self.last_result.lower() for w in
               ["resolved", "sent", "processed", "applied", "updated", "victory", "template"]):
            result_color = "#16c79a"
            result_border = "#16c79a"
        elif any(w in self.last_result.lower() for w in
                 ["warning", "lost", "wrong", "fail", "cannot", "game over", "unnecessary"]):
            result_color = "#e94560"
            result_border = "#e94560"
        else:
            result_color = "#b0b0b0"
            result_border = "#444"

        # Active ticket detail
        active_html = ""
        if self.world.active_ticket:
            t = self.world.active_ticket
            customer = self.world.get_customer(t.customer_id)
            cname = customer.name if customer else "Unknown"
            cemail = customer.email if customer else ""
            ctier = customer.tier.value if customer else ""
            cval = f"${customer.account_value:,}/yr" if customer else ""
            csentiment = customer.sentiment if customer else ""

            # Progress indicators
            steps = []
            if t.has_been_read:
                steps.append('<span style="color:#16c79a;">\u2705 Read</span>')
            if t.lookup_done:
                steps.append('<span style="color:#16c79a;">\u2705 Lookup</span>')
            else:
                steps.append('<span style="color:#666;">\u2b1c Lookup</span>')
            if t.action_applied:
                steps.append('<span style="color:#16c79a;">\u2705 Action</span>')
            else:
                steps.append('<span style="color:#666;">\u2b1c Action</span>')
            if t.reply_sent:
                steps.append('<span style="color:#16c79a;">\u2705 Reply</span>')
            else:
                steps.append('<span style="color:#666;">\u2b1c Reply</span>')
            if t.escalated_to:
                steps.append(f'<span style="color:#e9a045;">\u26a0 Escalated to {t.escalated_to}</span>')
            progress = " ".join(steps)

            active_html = (
                f'<div style="background:#12122a;border-radius:8px;padding:10px;'
                f'border:1px solid #2a2a3e;margin-top:8px;">'
                f'<div style="color:#888;font-size:11px;text-transform:uppercase;'
                f'letter-spacing:1px;margin-bottom:6px;">\U0001f4e8 Active Ticket</div>'
                f'<div style="font-size:14px;color:#e0e0e0;font-weight:bold;">'
                f'{t.priority.emoji} {t.category.emoji} '
                f'<span style="color:#7b68ee;">{t.id}</span> — {t.subject}</div>'
                f'<div style="font-size:12px;color:#888;margin-top:4px;">'
                f'{cname} ({cemail}) | {ctier} | {cval} | Mood: {csentiment}</div>'
                f'<div style="font-size:12px;color:#e0e0e0;margin-top:8px;padding:8px;'
                f'background:#0d0d18;border-radius:4px;white-space:pre-wrap;max-height:100px;'
                f'overflow-y:auto;">{t.message}</div>'
                f'<div style="margin-top:6px;font-size:11px;">{progress}</div>'
                f'</div>'
            )
        else:
            active_html = (
                '<div style="background:#12122a;border-radius:8px;padding:10px;'
                'border:1px solid #2a2a3e;margin-top:8px;">'
                '<div style="color:#666;font-size:12px;font-style:italic;text-align:center;'
                'padding:16px;">No active ticket. Use Open Ticket to get started.</div></div>'
            )

        game_over_banner = ""
        if self.game_over:
            if self.agent.has_won:
                game_over_banner = (
                    '<div style="text-align:center;padding:12px;background:#1a3a1a;'
                    'border:2px solid #ffd700;border-radius:8px;margin-top:8px;">'
                    '<span style="font-size:24px;color:#ffd700;text-shadow:0 0 10px #ffd700;'
                    f'font-weight:bold;">SHIFT COMPLETE! {self.agent.resolved_count} tickets, '
                    f'{self.agent.csat_score:.0f}% CSAT</span></div>'
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
                    f'SHIFT ENDED — {self.agent.resolved_count}/{self.agent.WIN_RESOLVED} resolved</span></div>'
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
    <span style="color:#ffd700;font-size:13px;font-weight:bold;">INTERACTIVE MODE</span>
  </div>

  <!-- Main content -->
  <div style="display:flex;gap:0;">
    <!-- Left: Queue -->
    <div style="padding:12px;width:280px;flex-shrink:0;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
        \U0001f4e5 Ticket Queue ({len(self.world.queue)})</div>
      <div style="background:#0d0d18;border-radius:8px;padding:4px;border:1px solid #2a2a3e;
        max-height:200px;overflow-y:auto;">
        {queue_html}
      </div>
    </div>

    <!-- Right: Stats -->
    <div style="padding:12px 12px 12px 0;flex:1;min-width:200px;display:flex;flex-direction:column;gap:8px;">
      {turn_html}
      <div style="background:#12122a;border-radius:8px;padding:6px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-bottom:2px;">Escalation Tokens</div>
        {tokens_html}
      </div>
      <div style="background:#12122a;border-radius:8px;padding:6px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-bottom:2px;">CSAT Score</div>
        {csat_html}
      </div>
      <div style="background:#12122a;border-radius:8px;padding:6px 10px;border:1px solid #2a2a3e;">
        <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-bottom:2px;">Tickets Resolved</div>
        {resolved_html}
      </div>
    </div>
  </div>

  <!-- Active ticket -->
  <div style="padding:0 12px;">
    {active_html}
  </div>

  <!-- Action log -->
  <div style="border-top:1px solid #2a2a3e;padding:10px 16px;background:#0d0d18;margin-top:8px;">
    <div style="color:#0f3460;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Last Action</div>
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
        """Start the interactive game."""
        self._render()
        display(self._main)


def play_interactive():
    """Launch an interactive support desk session.

    Usage:
        from support_desk.interactive import play_interactive
        play_interactive()
    """
    game = InteractiveGame()
    game.play()
    return game
