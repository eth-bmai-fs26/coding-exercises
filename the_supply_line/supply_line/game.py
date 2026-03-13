"""Game engine for The Supply Line — manages the simulation state."""

from dataclasses import dataclass, field
from typing import Optional
import copy

from supply_line.data import (
    Entity, Order, KBArticle, Template,
    OrderCategory, OrderPriority, OrderStatus, EntityTier, Department,
)
from supply_line.scenario import (
    ENTITIES, INITIAL_ORDERS, CHAIN_ORDERS, LATE_ORDERS,
    KNOWLEDGE_BASE, TEMPLATES,
)


# ---------------------------------------------------------------------------
# Agent State
# ---------------------------------------------------------------------------

@dataclass
class AgentState:
    """The operations coordinator's current state."""
    operations_tokens: int = 3
    MAX_TOKENS: int = 3
    resolved_count: int = 0
    score_total: int = 0
    score_max_total: int = 0       # sum of max possible per scored order
    score_interactions: int = 0
    WIN_RESOLVED: int = 15
    WIN_SCORE: float = 80.0
    notes: list[str] = field(default_factory=list)

    @property
    def quality_score(self) -> float:
        if self.score_max_total == 0:
            return 100.0
        return (self.score_total / self.score_max_total) * 100

    @property
    def is_alive(self) -> bool:
        return self.operations_tokens > 0

    @property
    def has_won(self) -> bool:
        return (
            self.is_alive
            and self.resolved_count >= self.WIN_RESOLVED
            and self.quality_score >= self.WIN_SCORE
        )

    def status_text(self) -> str:
        return (
            f"Tokens: {self.operations_tokens}/{self.MAX_TOKENS} | "
            f"Fulfilled: {self.resolved_count}/{self.WIN_RESOLVED} | "
            f"Quality: {self.quality_score:.0f}%/{self.WIN_SCORE:.0f}% | "
            f"Orders scored: {self.score_interactions}"
        )


# ---------------------------------------------------------------------------
# Supply World
# ---------------------------------------------------------------------------

class SupplyWorld:
    """The supply line simulation — manages orders, entities, KB."""

    def __init__(self):
        self.entities = {k: copy.deepcopy(v) for k, v in ENTITIES.items()}
        self.knowledge_base = [copy.deepcopy(a) for a in KNOWLEDGE_BASE]
        self.templates = {k: copy.deepcopy(v) for k, v in TEMPLATES.items()}

        # Order management
        self.queue: list[Order] = []
        self.active_order: Optional[Order] = None
        self.resolved_orders: list[Order] = []
        self.all_orders: dict[str, Order] = {}

        # Chain tracking
        self._chain_orders = {k: copy.deepcopy(v) for k, v in CHAIN_ORDERS.items()}
        self._late_orders = [copy.deepcopy(o) for o in LATE_ORDERS]
        self._unlocked_chains: set[str] = set()

        # Briefing evidence tracking
        self.briefing_evidence: set[str] = set()

        # Load initial orders
        for o in INITIAL_ORDERS:
            order = copy.deepcopy(o)
            self.queue.append(order)
            self.all_orders[order.id] = order

        self._sort_queue()

    def _sort_queue(self):
        priority_order = {
            OrderPriority.CRITICAL: 0,
            OrderPriority.HIGH: 1,
            OrderPriority.MEDIUM: 2,
            OrderPriority.LOW: 3,
        }
        self.queue.sort(key=lambda o: priority_order.get(o.priority, 4))

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)

    def get_order(self, order_id: str) -> Optional[Order]:
        return self.all_orders.get(order_id)

    def search_kb(self, query: str) -> list[KBArticle]:
        query_lower = query.lower()
        results = []
        for article in self.knowledge_base:
            score = 0
            for keyword in article.keywords:
                if keyword.lower() in query_lower or query_lower in keyword.lower():
                    score += 1
            if any(word in article.title.lower() for word in query_lower.split()):
                score += 1
            if score > 0:
                results.append((score, article))
        results.sort(key=lambda x: -x[0])
        return [article for _, article in results]

    def get_template(self, template_id: str) -> Optional[Template]:
        return self.templates.get(template_id)

    def add_late_orders(self, current_turn: int):
        to_add = []
        remaining = []
        for order in self._late_orders:
            if order.created_turn >= 0 and order.created_turn <= current_turn:
                order.created_turn = current_turn
                to_add.append(order)
            else:
                remaining.append(order)
        self._late_orders = remaining
        for order in to_add:
            self.queue.append(order)
            self.all_orders[order.id] = order
        if to_add:
            self._sort_queue()
        return to_add

    def unlock_chain(self, chain_id: str, current_turn: int) -> Optional[Order]:
        if chain_id in self._unlocked_chains:
            return None
        if chain_id not in self._chain_orders:
            return None

        self._unlocked_chains.add(chain_id)
        order = self._chain_orders[chain_id]
        order.created_turn = current_turn + 2
        self._late_orders.append(order)
        return order

    def resolve_order(self, order: Order):
        order.status = OrderStatus.RESOLVED
        if order in self.queue:
            self.queue.remove(order)
        if self.active_order and self.active_order.id == order.id:
            self.active_order = None
        self.resolved_orders.append(order)
        self.briefing_evidence.add(order.id)

    def check_briefing_ready(self, order_id: str) -> tuple[bool, list[str]]:
        order = self.get_order(order_id)
        if not order or not order.requires_briefing:
            return False, []
        missing = [oid for oid in order.briefing_prerequisites
                   if oid not in self.briefing_evidence]
        return len(missing) == 0, missing

    def queue_summary(self) -> str:
        if not self.queue:
            return "Order queue is empty."
        lines = [f"Order Queue: {len(self.queue)} orders"]
        for o in self.queue[:10]:
            entity = self.entities.get(o.entity_id)
            name = entity.name if entity else "Unknown"
            read_mark = "" if not o.has_been_read else " [read]"
            lines.append(
                f"  {o.priority.emoji} {o.category.emoji} "
                f"{o.id}: {o.subject[:50]}{'...' if len(o.subject) > 50 else ''} "
                f"({name}, {o.priority.value}){read_mark}"
            )
        if len(self.queue) > 10:
            lines.append(f"  ... and {len(self.queue) - 10} more")
        return "\n".join(lines)
