"""Tool implementations for The Support Desk — the actions the agent can take."""

from dataclasses import dataclass
from typing import Callable, Optional

from support_desk.data import (
    TicketCategory, TicketPriority, TicketStatus, Team,
)
from support_desk.game import SupportWorld, AgentState


@dataclass
class ToolResult:
    success: bool
    message: str


class SupportTools:
    """All tools the support agent can use each turn."""

    def __init__(self, agent: AgentState, world: SupportWorld):
        self.agent = agent
        self.world = world

    # ------------------------------------------------------------------
    # Tool: check_queue
    # ------------------------------------------------------------------
    def check_queue(self) -> ToolResult:
        """See the current ticket queue (free action)."""
        return ToolResult(True, self.world.queue_summary())

    # ------------------------------------------------------------------
    # Tool: open_ticket
    # ------------------------------------------------------------------
    def open_ticket(self, ticket_id: str = "") -> ToolResult:
        """Open a ticket to read its details."""
        ticket_id = ticket_id.strip()

        if not ticket_id:
            # Open the highest priority unread ticket
            for t in self.world.queue:
                if not t.has_been_read:
                    ticket_id = t.id
                    break
            if not ticket_id and self.world.queue:
                ticket_id = self.world.queue[0].id
            if not ticket_id:
                return ToolResult(False, "No tickets in queue.")

        ticket = self.world.get_ticket(ticket_id)
        if not ticket:
            return ToolResult(False, f"Ticket {ticket_id} not found.")
        if ticket.status == TicketStatus.RESOLVED:
            return ToolResult(False, f"Ticket {ticket_id} is already resolved.")

        ticket.has_been_read = True
        ticket.status = TicketStatus.IN_PROGRESS
        self.world.active_ticket = ticket

        customer = self.world.get_customer(ticket.customer_id)
        customer_info = ""
        if customer:
            customer_info = (
                f"\nCustomer: {customer.name} ({customer.email}) | "
                f"Plan: {customer.tier.value} | "
                f"Account Value: ${customer.account_value:,}/yr | "
                f"Active: {customer.months_active} months | "
                f"Prior tickets: {customer.prior_tickets} | "
                f"Sentiment: {customer.sentiment}"
            )
            if customer.notes:
                customer_info += f"\nNotes: {'; '.join(customer.notes)}"

        sla_info = f"SLA: {ticket.priority.sla_turns} turns"

        return ToolResult(True,
            f"--- Ticket {ticket.id} ---\n"
            f"Subject: {ticket.subject}\n"
            f"Category: {ticket.category.value} | "
            f"Priority: {ticket.priority.value} | {sla_info}\n"
            f"{customer_info}\n\n"
            f"Message:\n{ticket.message}"
        )

    # ------------------------------------------------------------------
    # Tool: lookup
    # ------------------------------------------------------------------
    def lookup(self, query: str = "") -> ToolResult:
        """Search the knowledge base or CRM."""
        query = query.strip()
        if not query:
            return ToolResult(False, "Please provide a search query.")

        results = self.world.search_kb(query)
        if not results:
            return ToolResult(True,
                f"No knowledge base articles found for '{query}'. "
                "Consider escalating to a specialist team if this is outside your expertise."
            )

        # Mark lookup as done for active ticket
        if self.world.active_ticket:
            self.world.active_ticket.lookup_done = True

        articles = results[:3]  # top 3 results
        lines = [f"Knowledge Base results for '{query}':"]
        for article in articles:
            lines.append(
                f"\n--- {article.id}: {article.title} ---\n{article.content}"
            )
        return ToolResult(True, "\n".join(lines))

    # ------------------------------------------------------------------
    # Tool: reply
    # ------------------------------------------------------------------
    def reply(self, ticket_id: str = "", message: str = "") -> ToolResult:
        """Send a response to the customer."""
        ticket_id = ticket_id.strip()
        message = message.strip()

        if not ticket_id and self.world.active_ticket:
            ticket_id = self.world.active_ticket.id
        if not ticket_id:
            return ToolResult(False, "No ticket specified and no active ticket.")

        ticket = self.world.get_ticket(ticket_id)
        if not ticket:
            return ToolResult(False, f"Ticket {ticket_id} not found.")

        if not message:
            return ToolResult(False, "Cannot send an empty reply.")

        ticket.reply_sent = True
        customer = self.world.get_customer(ticket.customer_id)
        customer_name = customer.name if customer else "Customer"

        self.agent.notes.append(
            f"Replied to {ticket_id} ({customer_name}): {message[:80]}..."
        )

        return ToolResult(True,
            f"Reply sent to {customer_name} on ticket {ticket_id}."
        )

    # ------------------------------------------------------------------
    # Tool: apply_action
    # ------------------------------------------------------------------
    def apply_action(self, ticket_id: str = "", action: str = "") -> ToolResult:
        """Apply a specific action to resolve a ticket."""
        ticket_id = ticket_id.strip()
        action = action.strip().lower()

        if not ticket_id and self.world.active_ticket:
            ticket_id = self.world.active_ticket.id
        if not ticket_id:
            return ToolResult(False, "No ticket specified and no active ticket.")

        ticket = self.world.get_ticket(ticket_id)
        if not ticket:
            return ToolResult(False, f"Ticket {ticket_id} not found.")

        if not action:
            return ToolResult(False, "Please specify an action to apply.")

        customer = self.world.get_customer(ticket.customer_id)
        customer_name = customer.name if customer else "Customer"

        # --- Validate specific actions ---

        if action == "reset_password":
            ticket.action_applied = True
            return ToolResult(True,
                f"Password reset link sent to {customer_name}'s email. "
                "They should receive it within a few minutes."
            )

        if action == "issue_refund":
            # Guardrail: must lookup first
            if not ticket.lookup_done:
                self.agent.escalation_tokens -= 1
                return ToolResult(False,
                    "WARNING: You tried to issue a refund without verifying the charge first! "
                    "Always lookup billing history before issuing refunds. "
                    f"Lost 1 escalation token. Remaining: {self.agent.escalation_tokens}"
                )
            # Guardrail: refunds over $100 need approval
            if ticket.refund_amount > 100:
                return ToolResult(False,
                    f"Refund of ${ticket.refund_amount} exceeds the $100 limit. "
                    "Escalate to the billing team for manager approval."
                )
            ticket.action_applied = True
            return ToolResult(True,
                f"Refund of ${ticket.refund_amount} processed for {customer_name}. "
                "Will appear on their statement in 3-5 business days."
            )

        if action == "close_spam":
            ticket.action_applied = True
            self.world.resolve_ticket(ticket)
            self.agent.resolved_count += 1
            return ToolResult(True,
                f"Ticket {ticket_id} closed as spam. No reply sent."
            )

        if action == "adjust_rate_limit":
            ticket.action_applied = True
            return ToolResult(True,
                f"Rate limit for {customer_name} adjusted to match their plan tier."
            )

        if action == "update_billing_profile":
            ticket.action_applied = True
            return ToolResult(True,
                f"Billing profile updated for {customer_name}."
            )

        if action == "update_known_bugs":
            ticket.action_applied = True
            return ToolResult(True,
                "Known bugs knowledge base updated with latest engineering info."
            )

        if action == "reply_vip_confirmation":
            ticket.action_applied = True
            return ToolResult(True,
                "VIP confirmation reply drafted. Remember to send it with reply()."
            )

        if action == "confirm_rate_fix":
            ticket.action_applied = True
            return ToolResult(True,
                f"Rate limit fix confirmed for {customer_name}. "
                "Please notify the customer."
            )

        return ToolResult(False,
            f"Unknown action '{action}'. Available actions: reset_password, "
            "issue_refund, close_spam, adjust_rate_limit, update_billing_profile, "
            "update_known_bugs, reply_vip_confirmation, confirm_rate_fix"
        )

    # ------------------------------------------------------------------
    # Tool: escalate
    # ------------------------------------------------------------------
    def escalate(self, ticket_id: str = "", team: str = "") -> ToolResult:
        """Escalate a ticket to a specialist team."""
        ticket_id = ticket_id.strip()
        team = team.strip().lower()

        if not ticket_id and self.world.active_ticket:
            ticket_id = self.world.active_ticket.id
        if not ticket_id:
            return ToolResult(False, "No ticket specified and no active ticket.")

        ticket = self.world.get_ticket(ticket_id)
        if not ticket:
            return ToolResult(False, f"Ticket {ticket_id} not found.")

        if not team:
            return ToolResult(False,
                "Please specify a team: billing, engineering, account_management, "
                "legal, security"
            )

        valid_teams = {"billing", "engineering", "account_management", "legal", "security"}
        if team not in valid_teams:
            return ToolResult(False,
                f"Unknown team '{team}'. Available: {', '.join(sorted(valid_teams))}"
            )

        # Check if briefing is required but not prepared
        if ticket.requires_briefing and not ticket.briefing_prepared:
            bounce_key = f"briefing_bounce_{ticket_id}"
            bounce_count = sum(1 for n in self.agent.notes if n == bounce_key)
            self.agent.notes.append(bounce_key)

            if bounce_count == 0:
                # First bounce: free warning
                return ToolResult(False,
                    f"The {team} team reviewed the escalation for {ticket_id} and sent it back. "
                    "They need a VIP Account Briefing before they can take action on a VP-level contact. "
                    "Use prepare_briefing(ticket_id) to compile evidence from related resolved tickets. "
                    "Hint: check the knowledge base for 'VIP briefing protocol'."
                )
            else:
                # Repeated attempts: cost a token
                self.agent.escalation_tokens -= 1
                self.agent.notes.append(
                    f"Escalated {ticket_id} without briefing (REJECTED, token lost)"
                )
                return ToolResult(False,
                    f"The {team} team rejected the escalation AGAIN — no briefing prepared. "
                    f"Lost 1 escalation token. Remaining: {self.agent.escalation_tokens}. "
                    f"You MUST call prepare_briefing(ticket_id=\"{ticket_id}\") first. "
                    "Resolve prerequisite tickets, then prepare the briefing."
                )

        # Check if escalation is correct
        if ticket.requires_escalation:
            if team == ticket.requires_escalation:
                # Correct escalation
                ticket.escalated_to = team
                ticket.status = TicketStatus.WAITING
                self.agent.notes.append(
                    f"Escalated {ticket_id} to {team} (correct)"
                )
                return ToolResult(True,
                    f"Ticket {ticket_id} escalated to {team} team. "
                    "They will review and respond. You should acknowledge the customer "
                    "in the meantime."
                )
            else:
                # Wrong escalation — costs a token
                self.agent.escalation_tokens -= 1
                self.agent.notes.append(
                    f"Escalated {ticket_id} to {team} (WRONG — should be {ticket.requires_escalation})"
                )
                return ToolResult(False,
                    f"The {team} team reviewed the ticket and sent it back — "
                    f"this isn't their area. Lost 1 escalation token. "
                    f"Remaining: {self.agent.escalation_tokens}. "
                    "Re-read the ticket and KB to determine the correct team."
                )
        else:
            # Unnecessary escalation — costs a token
            self.agent.escalation_tokens -= 1
            self.agent.notes.append(
                f"Escalated {ticket_id} to {team} (UNNECESSARY — could handle directly)"
            )
            return ToolResult(False,
                f"The {team} team sent the ticket back — you can handle this yourself. "
                f"Unnecessary escalation. Lost 1 escalation token. "
                f"Remaining: {self.agent.escalation_tokens}"
            )

    # ------------------------------------------------------------------
    # Tool: use_template
    # ------------------------------------------------------------------
    def use_template(self, ticket_id: str = "", template: str = "") -> ToolResult:
        """Apply a canned response template to a ticket."""
        ticket_id = ticket_id.strip()
        template = template.strip()

        if not ticket_id and self.world.active_ticket:
            ticket_id = self.world.active_ticket.id
        if not ticket_id:
            return ToolResult(False, "No ticket specified and no active ticket.")

        ticket = self.world.get_ticket(ticket_id)
        if not ticket:
            return ToolResult(False, f"Ticket {ticket_id} not found.")

        if not template:
            available = ", ".join(self.world.templates.keys())
            return ToolResult(False,
                f"Please specify a template. Available: {available}"
            )

        tmpl = self.world.get_template(template)
        if not tmpl:
            available = ", ".join(self.world.templates.keys())
            return ToolResult(False,
                f"Template '{template}' not found. Available: {available}"
            )

        customer = self.world.get_customer(ticket.customer_id)
        customer_name = customer.name if customer else "Customer"
        customer_email = customer.email if customer else "customer@email.com"

        # Fill in template
        filled = tmpl.message.format(
            customer_name=customer_name,
            email=customer_email,
            amount=ticket.refund_amount if ticket.refund_amount else "N/A",
            team="the specialist",
            workaround="exporting in smaller batches (under 5,000 rows)",
        )

        ticket.reply_sent = True

        self.agent.notes.append(
            f"Used template '{template}' for {ticket_id} ({customer_name})"
        )

        return ToolResult(True,
            f"Template '{tmpl.name}' applied to ticket {ticket_id}.\n\n"
            f"Message sent:\n{filled}"
        )

    # ------------------------------------------------------------------
    # Tool: resolve_ticket
    # ------------------------------------------------------------------
    def resolve_ticket(self, ticket_id: str = "") -> ToolResult:
        """Mark a ticket as resolved and score it."""
        ticket_id = ticket_id.strip()

        if not ticket_id and self.world.active_ticket:
            ticket_id = self.world.active_ticket.id
        if not ticket_id:
            return ToolResult(False, "No ticket specified and no active ticket.")

        ticket = self.world.get_ticket(ticket_id)
        if not ticket:
            return ToolResult(False, f"Ticket {ticket_id} not found.")

        if ticket.status == TicketStatus.RESOLVED:
            return ToolResult(False, f"Ticket {ticket_id} is already resolved.")

        # --- Score the resolution ---
        csat = ticket.csat_potential
        feedback = []

        # Spam gets auto-scored
        if ticket.category == TicketCategory.SPAM:
            if ticket.action_applied:
                feedback.append("Spam handled correctly.")
            else:
                csat -= 1
                feedback.append("Spam ticket should be closed with close_spam action.")

        else:
            # Must have replied (except spam)
            if not ticket.reply_sent:
                csat -= 2
                feedback.append("No reply sent to customer! (-2 CSAT)")

            # Should have looked up KB if required
            if ticket.requires_lookup and not ticket.lookup_done:
                csat += ticket.csat_penalty_no_lookup
                feedback.append(
                    f"Resolved without looking up info first ({ticket.csat_penalty_no_lookup} CSAT)"
                )

            # Should have applied the right action if required
            if ticket.requires_action and not ticket.action_applied:
                csat += ticket.csat_penalty_wrong_action
                feedback.append(
                    f"Required action '{ticket.requires_action}' not applied ({ticket.csat_penalty_wrong_action} CSAT)"
                )

            # Should have escalated if required
            if ticket.requires_escalation and ticket.escalated_to != ticket.requires_escalation:
                csat += ticket.csat_penalty_wrong_escalation
                feedback.append(
                    f"Should have been escalated to {ticket.requires_escalation} ({ticket.csat_penalty_wrong_escalation} CSAT)"
                )

        csat = max(0, min(5, csat))

        # Update agent state
        self.world.resolve_ticket(ticket)
        self.agent.resolved_count += 1
        self.agent.csat_total += csat
        self.agent.csat_interactions += 1

        # Unlock chain tickets
        if ticket.chain_id:
            unlocked = self.world.unlock_chain(ticket.chain_id, 0)
            if unlocked:
                feedback.append(f"Follow-up ticket {unlocked.id} will appear soon.")

        customer = self.world.get_customer(ticket.customer_id)
        customer_name = customer.name if customer else "Customer"

        quality = "Excellent" if csat >= 4 else "Good" if csat >= 3 else "Needs improvement" if csat >= 2 else "Poor"

        return ToolResult(True,
            f"Ticket {ticket_id} resolved! CSAT: {csat}/5 ({quality})\n"
            + ("\n".join(f"  - {f}" for f in feedback) if feedback else "  Perfect handling!")
            + f"\n\nResolved: {self.agent.resolved_count}/{self.agent.WIN_RESOLVED} | "
            f"Overall CSAT: {self.agent.csat_score:.0f}%"
        )

    # ------------------------------------------------------------------
    # Tool: check_stats
    # ------------------------------------------------------------------
    def check_stats(self) -> ToolResult:
        """Check current agent performance stats (free action)."""
        return ToolResult(True, self.agent.status_text())

    # ------------------------------------------------------------------
    # Tool: prepare_briefing
    # ------------------------------------------------------------------
    def prepare_briefing(self, ticket_id: str = "") -> ToolResult:
        """Prepare a VIP account briefing by compiling evidence from resolved tickets."""
        ticket_id = ticket_id.strip()

        if not ticket_id and self.world.active_ticket:
            ticket_id = self.world.active_ticket.id
        if not ticket_id:
            return ToolResult(False, "No ticket specified and no active ticket.")

        ticket = self.world.get_ticket(ticket_id)
        if not ticket:
            return ToolResult(False, f"Ticket {ticket_id} not found.")

        if not ticket.requires_briefing:
            return ToolResult(False, f"Ticket {ticket_id} does not require a briefing.")

        if ticket.briefing_prepared:
            return ToolResult(True, f"Briefing for {ticket_id} is already prepared.")

        ready, missing = self.world.check_briefing_ready(ticket_id)
        if not ready:
            missing_details = []
            for mid in missing:
                mt = self.world.get_ticket(mid)
                if mt:
                    missing_details.append(f"{mid} ({mt.subject})")
                else:
                    missing_details.append(mid)
            return ToolResult(False,
                f"Cannot prepare briefing for {ticket_id} yet. "
                f"Missing evidence from unresolved tickets: {', '.join(missing_details)}. "
                "Resolve these tickets first to gather the required evidence."
            )

        # Success!
        ticket.briefing_prepared = True
        customer = self.world.get_customer(ticket.customer_id)
        customer_name = customer.name if customer else "Customer"
        self.agent.notes.append(f"Prepared VIP briefing for {ticket_id} ({customer_name})")

        return ToolResult(True,
            f"VIP Account Briefing prepared for {ticket_id} ({customer_name})!\n"
            "Compiled evidence:\n"
            "  - API reliability: Rate limit issue identified and resolved (T-008)\n"
            "  - Bug resolution: Export crash fix confirmed, v2.3 shipping next Tuesday (T-005)\n\n"
            "The Account Management team now has full context. "
            "You can proceed to escalate this ticket."
        )

    # ------------------------------------------------------------------
    # Tool: take_break
    # ------------------------------------------------------------------
    def take_break(self) -> ToolResult:
        """Take a break to recover one escalation token. Costs 5 turns."""
        if self.agent.escalation_tokens >= self.agent.MAX_TOKENS:
            return ToolResult(False, "You're already at full tokens. No break needed.")
        self.agent.escalation_tokens += 1
        return ToolResult(True,
            f"Break taken. Recovered 1 escalation token. "
            f"Tokens: {self.agent.escalation_tokens}/{self.agent.MAX_TOKENS}"
        )

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------
    def execute(self, tool_name: str, args: dict) -> ToolResult:
        """Execute a tool by name with given arguments."""
        tool_map = {
            "check_queue": lambda: self.check_queue(),
            "open_ticket": lambda: self.open_ticket(args.get("ticket_id", "")),
            "lookup": lambda: self.lookup(args.get("query", "")),
            "reply": lambda: self.reply(
                args.get("ticket_id", ""), args.get("message", "")
            ),
            "apply_action": lambda: self.apply_action(
                args.get("ticket_id", ""), args.get("action", "")
            ),
            "escalate": lambda: self.escalate(
                args.get("ticket_id", ""), args.get("team", "")
            ),
            "use_template": lambda: self.use_template(
                args.get("ticket_id", ""), args.get("template", "")
            ),
            "resolve_ticket": lambda: self.resolve_ticket(
                args.get("ticket_id", "")
            ),
            "check_stats": lambda: self.check_stats(),
            "prepare_briefing": lambda: self.prepare_briefing(
                args.get("ticket_id", "")
            ),
            "take_break": lambda: self.take_break(),
        }

        fn = tool_map.get(tool_name.lower().strip())
        if fn is None:
            return ToolResult(False,
                f"Unknown tool '{tool_name}'. Available: {', '.join(tool_map.keys())}"
            )

        return fn()
