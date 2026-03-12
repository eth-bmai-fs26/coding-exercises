"""Game engine for The Support Desk — manages the simulation state."""

from dataclasses import dataclass, field
from typing import Optional
import copy

from support_desk.data import (
    Customer, Ticket, KBArticle, Template,
    TicketCategory, TicketPriority, TicketStatus, AccountTier, Team,
)
from support_desk.scenario import (
    CUSTOMERS, INITIAL_TICKETS, CHAIN_TICKETS, LATE_TICKETS,
    KNOWLEDGE_BASE, TEMPLATES,
)


# ---------------------------------------------------------------------------
# Agent State (equivalent to Hero)
# ---------------------------------------------------------------------------

@dataclass
class AgentState:
    """The support agent's current state — equivalent to Hero in Quest Hero."""
    escalation_tokens: int = 3
    MAX_TOKENS: int = 3
    resolved_count: int = 0
    csat_total: int = 0
    csat_interactions: int = 0
    WIN_RESOLVED: int = 15
    WIN_CSAT: float = 80.0
    notes: list[str] = field(default_factory=list)  # like hero.journal

    @property
    def csat_score(self) -> float:
        if self.csat_interactions == 0:
            return 100.0
        return (self.csat_total / self.csat_interactions) * 20  # scale to 0-100

    @property
    def is_alive(self) -> bool:
        return self.escalation_tokens > 0

    @property
    def has_won(self) -> bool:
        return (
            self.is_alive
            and self.resolved_count >= self.WIN_RESOLVED
            and self.csat_score >= self.WIN_CSAT
        )

    def status_text(self) -> str:
        return (
            f"Tokens: {self.escalation_tokens}/{self.MAX_TOKENS} | "
            f"Resolved: {self.resolved_count}/{self.WIN_RESOLVED} | "
            f"CSAT: {self.csat_score:.0f}%/{self.WIN_CSAT:.0f}% | "
            f"Interactions: {self.csat_interactions}"
        )


# ---------------------------------------------------------------------------
# Support World (equivalent to GameWorld)
# ---------------------------------------------------------------------------

class SupportWorld:
    """The support desk simulation — manages tickets, customers, KB."""

    def __init__(self):
        # Deep copy everything so each game is independent
        self.customers = {k: copy.deepcopy(v) for k, v in CUSTOMERS.items()}
        self.knowledge_base = [copy.deepcopy(a) for a in KNOWLEDGE_BASE]
        self.templates = {k: copy.deepcopy(v) for k, v in TEMPLATES.items()}

        # Ticket management
        self.queue: list[Ticket] = []           # tickets available to work on
        self.active_ticket: Optional[Ticket] = None  # currently open ticket
        self.resolved_tickets: list[Ticket] = []
        self.all_tickets: dict[str, Ticket] = {}

        # Chain tracking
        self._chain_tickets = {k: copy.deepcopy(v) for k, v in CHAIN_TICKETS.items()}
        self._late_tickets = [copy.deepcopy(t) for t in LATE_TICKETS]
        self._unlocked_chains: set[str] = set()

        # Load initial tickets
        for t in INITIAL_TICKETS:
            ticket = copy.deepcopy(t)
            self.queue.append(ticket)
            self.all_tickets[ticket.id] = ticket

        # Sort queue by priority
        self._sort_queue()

    def _sort_queue(self):
        """Sort queue: CRITICAL first, then HIGH, MEDIUM, LOW."""
        priority_order = {
            TicketPriority.CRITICAL: 0,
            TicketPriority.HIGH: 1,
            TicketPriority.MEDIUM: 2,
            TicketPriority.LOW: 3,
        }
        self.queue.sort(key=lambda t: priority_order.get(t.priority, 4))

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        return self.customers.get(customer_id)

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        return self.all_tickets.get(ticket_id)

    def search_kb(self, query: str) -> list[KBArticle]:
        """Search knowledge base by keyword matching."""
        query_lower = query.lower()
        results = []
        for article in self.knowledge_base:
            score = 0
            for keyword in article.keywords:
                if keyword.lower() in query_lower or query_lower in keyword.lower():
                    score += 1
            # Also check title
            if any(word in article.title.lower() for word in query_lower.split()):
                score += 1
            if score > 0:
                results.append((score, article))
        results.sort(key=lambda x: -x[0])
        return [article for _, article in results]

    def get_template(self, template_id: str) -> Optional[Template]:
        return self.templates.get(template_id)

    def add_late_tickets(self, current_turn: int):
        """Add time-gated tickets to the queue."""
        to_add = []
        remaining = []
        for ticket in self._late_tickets:
            if ticket.created_turn >= 0 and ticket.created_turn <= current_turn:
                ticket.created_turn = current_turn
                to_add.append(ticket)
            else:
                remaining.append(ticket)
        self._late_tickets = remaining
        for ticket in to_add:
            self.queue.append(ticket)
            self.all_tickets[ticket.id] = ticket
        if to_add:
            self._sort_queue()
        return to_add

    def unlock_chain(self, chain_id: str, current_turn: int) -> Optional[Ticket]:
        """Unlock a chain ticket after resolving its trigger."""
        if chain_id in self._unlocked_chains:
            return None
        if chain_id not in self._chain_tickets:
            return None

        self._unlocked_chains.add(chain_id)
        ticket = self._chain_tickets[chain_id]
        ticket.created_turn = current_turn + 2  # appears 2 turns later
        # Add to late tickets so it appears naturally
        self._late_tickets.append(ticket)
        return ticket

    def resolve_ticket(self, ticket: Ticket):
        """Move a ticket from active/queue to resolved."""
        ticket.status = TicketStatus.RESOLVED
        if ticket in self.queue:
            self.queue.remove(ticket)
        if self.active_ticket and self.active_ticket.id == ticket.id:
            self.active_ticket = None
        self.resolved_tickets.append(ticket)

    def queue_summary(self) -> str:
        """Summary of current queue state."""
        if not self.queue:
            return "Queue is empty."
        lines = [f"Queue: {len(self.queue)} tickets"]
        for t in self.queue[:10]:
            customer = self.customers.get(t.customer_id)
            name = customer.name if customer else "Unknown"
            read_mark = "" if not t.has_been_read else " [read]"
            lines.append(
                f"  {t.priority.emoji} {t.id}: {t.subject} "
                f"(from {name}, {t.priority.value}){read_mark}"
            )
        if len(self.queue) > 10:
            lines.append(f"  ... and {len(self.queue) - 10} more")
        return "\n".join(lines)
