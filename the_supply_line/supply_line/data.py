"""Data models for The Supply Line — orders, clients, knowledge base."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class OrderPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def emoji(self) -> str:
        return {
            OrderPriority.LOW: "\U0001f7e2",        # green
            OrderPriority.MEDIUM: "\U0001f7e1",     # yellow
            OrderPriority.HIGH: "\U0001f7e0",       # orange
            OrderPriority.CRITICAL: "\U0001f534",   # red
        }[self]

    @property
    def sla_turns(self) -> int:
        return {
            OrderPriority.LOW: 50,
            OrderPriority.MEDIUM: 30,
            OrderPriority.HIGH: 15,
            OrderPriority.CRITICAL: 8,
        }[self]


class OrderStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    RESOLVED = "resolved"
    CLOSED = "closed"


class OrderCategory(Enum):
    REORDER = "reorder"
    DELAY = "delay"
    QUALITY = "quality"
    CUSTOMS = "customs"
    RUSH = "rush"
    DISPUTE = "dispute"
    LAUNCH = "launch"
    REGULATORY = "regulatory"
    SYSTEM_ALERT = "system_alert"

    @property
    def emoji(self) -> str:
        return {
            OrderCategory.REORDER: "\U0001f4e6",        # package
            OrderCategory.DELAY: "\U0001f69a",           # truck
            OrderCategory.QUALITY: "\u26a0\ufe0f",       # warning
            OrderCategory.CUSTOMS: "\U0001f6c3",         # customs
            OrderCategory.RUSH: "\u26a1",                # lightning
            OrderCategory.DISPUTE: "\U0001f4b0",         # money bag
            OrderCategory.LAUNCH: "\U0001f680",          # rocket
            OrderCategory.REGULATORY: "\u2696\ufe0f",    # scales
            OrderCategory.SYSTEM_ALERT: "\U0001f514",    # bell
        }[self]


class EntityTier(Enum):
    STANDARD = "standard"
    ENTERPRISE = "enterprise"
    INTERNAL = "internal"
    BLACKLISTED = "blacklisted"
    SYSTEM = "system"
    REGULATOR = "regulator"

    @property
    def emoji(self) -> str:
        return {
            EntityTier.STANDARD: "\u26aa",
            EntityTier.ENTERPRISE: "\U0001f49c",
            EntityTier.INTERNAL: "\U0001f535",
            EntityTier.BLACKLISTED: "\U0001f534",
            EntityTier.SYSTEM: "\u2699\ufe0f",
            EntityTier.REGULATOR: "\u2696\ufe0f",
        }[self]


class Department(Enum):
    PROCUREMENT = "procurement"
    FINANCE = "finance"
    LOGISTICS = "logistics"
    ENGINEERING = "engineering"
    COMPLIANCE = "compliance"


# ---------------------------------------------------------------------------
# Client / Supplier
# ---------------------------------------------------------------------------

@dataclass
class Entity:
    id: str
    name: str
    role: str               # "client", "supplier", "internal", "regulator", "system"
    tier: EntityTier
    industry: str = ""
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------

@dataclass
class Order:
    id: str
    entity_id: str
    subject: str
    message: str
    category: OrderCategory
    priority: OrderPriority
    status: OrderStatus = OrderStatus.OPEN
    created_turn: int = 0

    # Resolution requirements
    requires_lookup: bool = False
    lookup_query: str = ""
    requires_action: str = ""           # e.g. "place_order", "reject_shipment"
    requires_claim: bool = False        # quality orders: must file_claim
    requires_escalation: str = ""       # department to escalate to
    correct_template: str = ""
    order_value: int = 0                # EUR value

    # Resolution state
    has_been_read: bool = False
    lookup_done: bool = False
    action_applied: bool = False
    notification_sent: bool = False
    escalated_to: str = ""
    escalation_response: str = ""
    escalation_turn: int = -1
    claim_filed: bool = False

    # Scoring
    score_potential: int = 5
    penalty_wrong_action: int = -3
    penalty_no_lookup: int = -2
    penalty_sla_breach: int = -2
    penalty_wrong_escalation: int = -3
    bonus_fast: int = 1

    # Chain tasks
    chain_id: str = ""
    chain_order: int = 0
    unlocks_order: str = ""
    requires_resolved: str = ""

    # Boss fight (briefing mechanic)
    requires_briefing: bool = False
    briefing_prerequisites: list[str] = field(default_factory=list)
    briefing_prepared: bool = False
    # Which briefing type: "launch" or "compliance"
    briefing_type: str = ""


# ---------------------------------------------------------------------------
# Knowledge Base Article
# ---------------------------------------------------------------------------

@dataclass
class KBArticle:
    id: str
    title: str
    content: str
    keywords: list[str]
    category: OrderCategory
    actionable: bool = True
    action_hint: str = ""


# ---------------------------------------------------------------------------
# Notification Template
# ---------------------------------------------------------------------------

@dataclass
class Template:
    id: str
    name: str
    category: OrderCategory
    message: str
    appropriate_for: list[str]
