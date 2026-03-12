"""Data models for The Support Desk — tickets, customers, knowledge base."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def emoji(self) -> str:
        return {
            TicketPriority.LOW: "\U0001f7e2",        # green
            TicketPriority.MEDIUM: "\U0001f7e1",     # yellow
            TicketPriority.HIGH: "\U0001f7e0",       # orange
            TicketPriority.CRITICAL: "\U0001f534",   # red
        }[self]

    @property
    def sla_turns(self) -> int:
        """Max turns before SLA breach."""
        return {
            TicketPriority.LOW: 50,
            TicketPriority.MEDIUM: 30,
            TicketPriority.HIGH: 15,
            TicketPriority.CRITICAL: 8,
        }[self]


class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"         # waiting for escalation response
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketCategory(Enum):
    PASSWORD = "password"
    BILLING = "billing"
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    ACCOUNT = "account"
    VIP = "vip"
    SPAM = "spam"
    GENERAL = "general"

    @property
    def emoji(self) -> str:
        return {
            TicketCategory.PASSWORD: "\U0001f511",
            TicketCategory.BILLING: "\U0001f4b3",
            TicketCategory.BUG: "\U0001f41b",
            TicketCategory.FEATURE_REQUEST: "\U0001f4a1",
            TicketCategory.ACCOUNT: "\U0001f464",
            TicketCategory.VIP: "\u2b50",
            TicketCategory.SPAM: "\U0001f6ab",
            TicketCategory.GENERAL: "\U0001f4e9",
        }[self]


class AccountTier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

    @property
    def emoji(self) -> str:
        return {
            AccountTier.FREE: "\u26aa",
            AccountTier.PRO: "\U0001f535",
            AccountTier.ENTERPRISE: "\U0001f49c",
        }[self]


class Team(Enum):
    BILLING = "billing"
    ENGINEERING = "engineering"
    ACCOUNT_MANAGEMENT = "account_management"
    LEGAL = "legal"
    SECURITY = "security"


# ---------------------------------------------------------------------------
# Customer
# ---------------------------------------------------------------------------

@dataclass
class Customer:
    id: str
    name: str
    email: str
    tier: AccountTier
    account_value: int          # annual $ value
    months_active: int
    prior_tickets: int          # how many past tickets
    sentiment: str              # "happy", "neutral", "frustrated", "angry"
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Ticket
# ---------------------------------------------------------------------------

@dataclass
class Ticket:
    id: str
    customer_id: str
    subject: str
    message: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus = TicketStatus.OPEN
    created_turn: int = 0

    # Resolution requirements
    requires_lookup: bool = False       # must lookup KB before resolving
    lookup_query: str = ""              # what to search for
    requires_action: str = ""           # action to apply (e.g. "reset_password")
    requires_escalation: str = ""       # team to escalate to (empty = don't escalate)
    correct_template: str = ""          # best template to use (empty = write custom)
    refund_amount: int = 0              # if refund needed

    # Resolution state
    has_been_read: bool = False
    lookup_done: bool = False
    action_applied: bool = False
    reply_sent: bool = False
    escalated_to: str = ""
    escalation_response: str = ""       # filled in after escalation
    escalation_turn: int = -1           # turn when escalated

    # Scoring
    csat_potential: int = 5             # max CSAT points if resolved perfectly
    csat_penalty_wrong_action: int = -3
    csat_penalty_no_lookup: int = -2
    csat_penalty_sla_breach: int = -2
    csat_penalty_wrong_escalation: int = -3
    csat_bonus_fast: int = 1            # bonus for resolving quickly

    # For multi-ticket chains
    chain_id: str = ""                  # tickets in same chain share this
    chain_order: int = 0                # order within chain
    unlocks_ticket: str = ""            # resolving this ticket adds another to queue
    requires_resolved: str = ""         # can't fully resolve until this ticket is done


# ---------------------------------------------------------------------------
# Knowledge Base Article
# ---------------------------------------------------------------------------

@dataclass
class KBArticle:
    id: str
    title: str
    content: str
    keywords: list[str]
    category: TicketCategory
    actionable: bool = True     # does this article have a fix?
    action_hint: str = ""       # what action to apply


# ---------------------------------------------------------------------------
# Response Template
# ---------------------------------------------------------------------------

@dataclass
class Template:
    id: str
    name: str
    category: TicketCategory
    message: str
    appropriate_for: list[str]  # list of ticket chain_ids or categories this works for
