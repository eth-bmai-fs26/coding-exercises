"""Scenario data for The Support Desk — customers, tickets, KB, templates."""

from support_desk.data import (
    Customer, Ticket, KBArticle, Template,
    AccountTier, TicketCategory, TicketPriority, TicketStatus, Team,
)


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

CUSTOMERS = {
    "C-100": Customer(
        id="C-100", name="Alice Park", email="alice@startup.io",
        tier=AccountTier.PRO, account_value=1200, months_active=8,
        prior_tickets=2, sentiment="neutral",
        notes=["Upgraded from Free 3 months ago"],
    ),
    "C-101": Customer(
        id="C-101", name="Bob Martinez", email="bob@megacorp.com",
        tier=AccountTier.ENTERPRISE, account_value=120000, months_active=36,
        prior_tickets=15, sentiment="frustrated",
        notes=["Key account — 50 seats", "Had billing issue last quarter"],
    ),
    "C-102": Customer(
        id="C-102", name="Carla Jensen", email="carla@freelance.me",
        tier=AccountTier.FREE, account_value=0, months_active=2,
        prior_tickets=0, sentiment="happy",
    ),
    "C-103": Customer(
        id="C-103", name="David Liu", email="david@techfirm.co",
        tier=AccountTier.PRO, account_value=3600, months_active=14,
        prior_tickets=5, sentiment="neutral",
        notes=["Power user, very technical"],
    ),
    "C-104": Customer(
        id="C-104", name="Elena Rossi", email="elena@globalbank.com",
        tier=AccountTier.ENTERPRISE, account_value=500000, months_active=48,
        prior_tickets=8, sentiment="angry",
        notes=["VP of Operations", "Threatened to switch to competitor last month",
               "Account managed by Sarah (AM team)"],
    ),
    "C-105": Customer(
        id="C-105", name="Frank Okafor", email="frank@designstudio.co",
        tier=AccountTier.PRO, account_value=2400, months_active=6,
        prior_tickets=1, sentiment="happy",
    ),
    "C-106": Customer(
        id="C-106", name="Grace Kim", email="grace@university.edu",
        tier=AccountTier.FREE, account_value=0, months_active=1,
        prior_tickets=0, sentiment="neutral",
    ),
    "C-107": Customer(
        id="C-107", name="Hassan Al-Rashid", email="hassan@logistics.ae",
        tier=AccountTier.ENTERPRISE, account_value=85000, months_active=24,
        prior_tickets=12, sentiment="neutral",
        notes=["Uses API heavily", "30 seats"],
    ),
    "C-108": Customer(
        id="C-108", name="Isla Chen", email="isla@retailchain.com",
        tier=AccountTier.PRO, account_value=4800, months_active=18,
        prior_tickets=3, sentiment="frustrated",
        notes=["Reported export bug twice before — still not fixed"],
    ),
    "C-109": Customer(
        id="C-109", name="spam_bot_42", email="definitelynotspam@freemail.xyz",
        tier=AccountTier.FREE, account_value=0, months_active=0,
        prior_tickets=0, sentiment="neutral",
    ),
}


# ---------------------------------------------------------------------------
# Tickets — designed to create quest chains and teach agentic patterns
# ---------------------------------------------------------------------------

# Wave 1: Initial queue (tickets 1-8)
INITIAL_TICKETS = [
    # --- Simple: Password Reset (= treasure pickup) ---
    Ticket(
        id="T-001", customer_id="C-100", category=TicketCategory.PASSWORD,
        priority=TicketPriority.MEDIUM, created_turn=0,
        subject="Can't log in to my account",
        message="Hi, I've been trying to log in all morning but it says my password is wrong. "
                "I'm sure I'm using the right one. Can you help?",
        requires_lookup=True, lookup_query="account locked",
        requires_action="reset_password",
        correct_template="password_reset",
        csat_potential=3,
    ),
    # --- Simple: General question (= open path) ---
    Ticket(
        id="T-002", customer_id="C-106", category=TicketCategory.GENERAL,
        priority=TicketPriority.LOW, created_turn=0,
        subject="How do I export my data?",
        message="Hello, I'm new to the platform. How do I export my project data to CSV? "
                "I looked in settings but couldn't find it.",
        requires_lookup=True, lookup_query="export csv",
        correct_template="export_guide",
        csat_potential=2,
    ),
    # --- Medium: Billing Dispute (= letter delivery chain) ---
    Ticket(
        id="T-003", customer_id="C-100", category=TicketCategory.BILLING,
        priority=TicketPriority.HIGH, created_turn=0,
        subject="Charged twice this month!",
        message="I just checked my credit card statement and I see TWO charges of $29.99 from "
                "you this month. I should only be charged once. Please refund the duplicate!",
        requires_lookup=True, lookup_query="billing C-100",
        requires_action="issue_refund",
        refund_amount=30,
        csat_potential=5,
        chain_id="billing_alice",
    ),
    # --- Spam (= trap) ---
    Ticket(
        id="T-004", customer_id="C-109", category=TicketCategory.SPAM,
        priority=TicketPriority.LOW, created_turn=0,
        subject="URGENT: You have won $1,000,000!!!",
        message="Congratulations! You have been selected for our exclusive promotion. "
                "Click here to claim your prize. Act now before it expires!!! "
                "Send your bank details to claim.",
        requires_action="close_spam",
        csat_potential=0,
    ),
    # --- Bug Report — Known Bug (= NPC with known info) ---
    Ticket(
        id="T-005", customer_id="C-108", category=TicketCategory.BUG,
        priority=TicketPriority.HIGH, created_turn=0,
        subject="Export crashes AGAIN",
        message="The CSV export is crashing AGAIN. This is the THIRD time I've reported this. "
                "It happens every time I try to export more than 10,000 rows. "
                "Last time you said it would be fixed in v2.3. When is that shipping?!",
        requires_lookup=True, lookup_query="export crash bug",
        correct_template="known_bug_eta",
        csat_potential=4,
        chain_id="export_bug",
    ),
    # --- Feature Request (= exploration, low value) ---
    Ticket(
        id="T-006", customer_id="C-105", category=TicketCategory.FEATURE_REQUEST,
        priority=TicketPriority.LOW, created_turn=0,
        subject="Dark mode please!",
        message="Love the product! Any chance you're working on a dark mode? "
                "My eyes would really appreciate it for late-night sessions.",
        correct_template="feature_request_logged",
        csat_potential=2,
    ),
    # --- VIP Escalation (= dragon fight!) ---
    Ticket(
        id="T-007", customer_id="C-104", category=TicketCategory.VIP,
        priority=TicketPriority.CRITICAL, created_turn=0,
        subject="Considering switching to competitor",
        message="This is Elena Rossi, VP of Operations at GlobalBank. We've been customers "
                "for 4 years and I'm frankly disappointed with the level of service. "
                "Our API has been unreliable, our last 3 support tickets took over a week "
                "to resolve, and I've had a meeting with your competitor yesterday. "
                "I need to speak with someone senior about our contract renewal.",
        requires_lookup=True, lookup_query="account C-104",
        requires_escalation="account_management",
        csat_potential=8,
        chain_id="vip_elena",
    ),
    # --- Account Issue — Needs investigation (= NPC quest trigger) ---
    Ticket(
        id="T-008", customer_id="C-103", category=TicketCategory.ACCOUNT,
        priority=TicketPriority.MEDIUM, created_turn=0,
        subject="API rate limits too low",
        message="We're hitting API rate limits way too often. We're on the Pro plan and the "
                "docs say we should get 10,000 requests/hour, but we're getting throttled "
                "at around 5,000. Can you check our account settings?",
        requires_lookup=True, lookup_query="rate limits C-103",
        requires_action="adjust_rate_limit",
        csat_potential=4,
        chain_id="api_limits",
    ),
]


# Wave 2: Tickets unlocked by resolving wave 1 (chain continuations)
CHAIN_TICKETS = {
    # Resolving the billing dispute for Alice unlocks a follow-up
    "billing_alice": Ticket(
        id="T-009", customer_id="C-100", category=TicketCategory.BILLING,
        priority=TicketPriority.MEDIUM, created_turn=-1,
        subject="Re: Charged twice — got the refund, but why did it happen?",
        message="Thanks for the refund! But I'm worried — why was I charged twice? "
                "Is this going to happen again next month? I need to know it's fixed.",
        requires_lookup=True, lookup_query="billing duplicate cause",
        csat_potential=3,
        chain_id="billing_alice_followup",
    ),
    # VIP Elena escalation triggers AM response
    "vip_elena": Ticket(
        id="T-010", customer_id="C-104", category=TicketCategory.VIP,
        priority=TicketPriority.CRITICAL, created_turn=-1,
        subject="Re: Contract renewal — AM team follow-up",
        message="[INTERNAL — from Account Management]\n"
                "Thanks for escalating Elena's ticket. We've scheduled a call with her "
                "for Thursday. Please reply to her confirming that our AM team will be "
                "in touch within 24 hours, and that we're prioritizing her API reliability "
                "concerns. DO NOT promise any discounts or contract changes.",
        requires_action="reply_vip_confirmation",
        csat_potential=6,
        chain_id="vip_elena_followup",
    ),
    # Export bug chain — after acknowledging, engineering responds
    "export_bug": Ticket(
        id="T-011", customer_id="C-108", category=TicketCategory.BUG,
        priority=TicketPriority.HIGH, created_turn=-1,
        subject="Re: Export crash — Engineering update",
        message="[INTERNAL — from Engineering]\n"
                "The export crash bug (ENG-4521) has been fixed in v2.3 which ships next "
                "Tuesday. The root cause was a memory overflow when row count > 8000. "
                "Customer can use the workaround of exporting in batches of 5000 rows until then. "
                "Please update the customer and add this to the known bugs KB.",
        requires_action="update_known_bugs",
        csat_potential=5,
        chain_id="export_bug_resolved",
        unlocks_ticket="T-014",
    ),
    # API rate limits — after investigation
    "api_limits": Ticket(
        id="T-012", customer_id="C-103", category=TicketCategory.ACCOUNT,
        priority=TicketPriority.MEDIUM, created_turn=-1,
        subject="Re: API rate limits — investigation results",
        message="[INTERNAL — from Engineering]\n"
                "Checked C-103's account. Their rate limit was incorrectly set to 5000/hr "
                "due to a migration bug. Should be 10000/hr on Pro plan. "
                "I've fixed it on our end. Please confirm with the customer.",
        requires_action="confirm_rate_fix",
        csat_potential=4,
    ),
}


# Wave 3: Late-game tickets (appear mid-shift)
LATE_TICKETS = [
    # Another VIP — but this one should NOT be escalated
    Ticket(
        id="T-013", customer_id="C-101", category=TicketCategory.BILLING,
        priority=TicketPriority.HIGH, created_turn=40,
        subject="Invoice format change request",
        message="Hi, we need our invoices to include a PO number field. Our finance team "
                "requires this for internal processing. Can you update our billing profile "
                "to include PO number MB-2024-0891?",
        requires_lookup=True, lookup_query="invoice po number",
        requires_action="update_billing_profile",
        csat_potential=4,
    ),
    # Follow-up from export bug resolution — customer confirms
    Ticket(
        id="T-014", customer_id="C-108", category=TicketCategory.BUG,
        priority=TicketPriority.MEDIUM, created_turn=-1,
        subject="Re: Export crash — workaround works!",
        message="Thanks! The batch export workaround is working for now. "
                "Looking forward to v2.3 next week. You can close this ticket. "
                "One more thing — can you also check if the PDF export has the same issue?",
        requires_lookup=True, lookup_query="pdf export bug",
        csat_potential=3,
    ),
    # Security concern — must escalate to security
    Ticket(
        id="T-015", customer_id="C-107", category=TicketCategory.ACCOUNT,
        priority=TicketPriority.CRITICAL, created_turn=50,
        subject="Suspicious login activity on our account",
        message="We noticed login attempts from an IP address in a country where we have "
                "no employees. Three failed attempts followed by one successful login at "
                "3 AM our time. We've changed our password but need you to investigate "
                "if any data was accessed.",
        requires_lookup=True, lookup_query="security suspicious login",
        requires_escalation="security",
        csat_potential=6,
    ),
    # Simple password reset — tests autopilot (should be auto-handled)
    Ticket(
        id="T-016", customer_id="C-102", category=TicketCategory.PASSWORD,
        priority=TicketPriority.LOW, created_turn=30,
        subject="Forgot my password",
        message="Hi, I forgot my password and the reset email isn't arriving. "
                "Can you reset it manually? My email is carla@freelance.me.",
        requires_lookup=True, lookup_query="account locked",
        requires_action="reset_password",
        correct_template="password_reset",
        csat_potential=2,
    ),
    # Another billing — small refund (tests guardrail: amount is fine)
    Ticket(
        id="T-017", customer_id="C-105", category=TicketCategory.BILLING,
        priority=TicketPriority.MEDIUM, created_turn=35,
        subject="Accidental upgrade charge",
        message="I accidentally clicked 'upgrade to annual' and was charged $199. "
                "I wanted to stay on monthly. Can I get a refund? It just happened today.",
        requires_lookup=True, lookup_query="billing C-105",
        requires_action="issue_refund",
        refund_amount=199,
        csat_potential=4,
    ),
    # Enterprise feature question — tests lookup
    Ticket(
        id="T-018", customer_id="C-107", category=TicketCategory.GENERAL,
        priority=TicketPriority.LOW, created_turn=55,
        subject="SSO setup documentation",
        message="We're setting up SSO for our team. Where can I find the documentation "
                "for SAML integration? Our IT team needs the metadata URL and certificate.",
        requires_lookup=True, lookup_query="sso saml setup",
        correct_template="sso_guide",
        csat_potential=3,
    ),
    # Angry customer — previously unresolved bug
    Ticket(
        id="T-019", customer_id="C-108", category=TicketCategory.ACCOUNT,
        priority=TicketPriority.HIGH, created_turn=60,
        subject="I want to cancel my subscription",
        message="I've had it. The export bug took forever to fix, the PDF export "
                "is still broken, and I just lost an hour of work because your "
                "auto-save failed. I want to cancel my Pro subscription immediately.",
        requires_lookup=True, lookup_query="cancellation C-108",
        requires_escalation="account_management",
        csat_potential=6,
        chain_id="cancel_isla",
    ),
    # Spam wave 2
    Ticket(
        id="T-020", customer_id="C-109", category=TicketCategory.SPAM,
        priority=TicketPriority.LOW, created_turn=45,
        subject="FINAL WARNING: Your account will be suspended",
        message="Your account will be suspended unless you verify your identity NOW. "
                "Click the link below and enter your login credentials to avoid suspension.",
        requires_action="close_spam",
        csat_potential=0,
    ),
]


# ---------------------------------------------------------------------------
# Knowledge Base
# ---------------------------------------------------------------------------

KNOWLEDGE_BASE = [
    KBArticle(
        id="KB-001", title="Account Locked / Password Reset",
        category=TicketCategory.PASSWORD,
        keywords=["password", "locked", "login", "can't log in", "reset", "account locked"],
        content="If a customer's account is locked due to failed login attempts, "
                "verify their identity via email, then use apply_action('reset_password'). "
                "The system will send a reset link to their registered email. "
                "Account locks trigger after 5 failed attempts.",
        actionable=True, action_hint="reset_password",
    ),
    KBArticle(
        id="KB-002", title="CSV Export Guide",
        category=TicketCategory.GENERAL,
        keywords=["export", "csv", "download", "data export"],
        content="To export data to CSV: Go to Project > Settings > Export > Choose CSV format. "
                "Free plan: up to 1,000 rows. Pro plan: up to 50,000 rows. "
                "Enterprise: unlimited. Export is available under the 'Data' tab in settings.",
        actionable=False, action_hint="",
    ),
    KBArticle(
        id="KB-003", title="Billing Duplicate Charge Investigation",
        category=TicketCategory.BILLING,
        keywords=["billing", "charge", "duplicate", "double charge", "refund", "charged twice"],
        content="To investigate duplicate charges: Check the billing history for the customer. "
                "If a duplicate is confirmed, issue a refund via apply_action('issue_refund'). "
                "Refunds under $100 can be processed immediately. "
                "Refunds over $100 require manager approval — escalate to billing team. "
                "Always verify the duplicate in billing history BEFORE issuing refund.",
        actionable=True, action_hint="issue_refund",
    ),
    KBArticle(
        id="KB-004", title="Billing — Duplicate Charge Root Cause",
        category=TicketCategory.BILLING,
        keywords=["billing", "duplicate", "cause", "why", "charged twice", "recurring"],
        content="Duplicate charges are typically caused by: (1) Payment gateway timeout causing "
                "retry, (2) User clicking 'pay' twice, (3) Plan change during billing cycle. "
                "The billing team deployed a fix for gateway retries in v2.2. If the customer "
                "asks why it happened, explain it was a gateway timeout (most common cause) "
                "and that safeguards are now in place to prevent recurrence.",
        actionable=False,
    ),
    KBArticle(
        id="KB-005", title="Export Crash Bug (ENG-4521)",
        category=TicketCategory.BUG,
        keywords=["export", "crash", "bug", "csv", "10000", "rows", "memory", "ENG-4521"],
        content="KNOWN BUG: CSV export crashes when exporting more than 8,000 rows. "
                "Root cause: memory overflow in the export service. "
                "Status: Fix scheduled for v2.3 (shipping next Tuesday). "
                "WORKAROUND: Export in batches of 5,000 rows or fewer. "
                "This bug does NOT affect PDF exports.",
        actionable=False, action_hint="",
    ),
    KBArticle(
        id="KB-006", title="Feature Request Handling",
        category=TicketCategory.FEATURE_REQUEST,
        keywords=["feature", "request", "suggestion", "dark mode", "new feature"],
        content="Log all feature requests in the product feedback system. "
                "Thank the customer for their suggestion. Do NOT promise timelines or "
                "commit to building any feature. Say: 'We've logged your request and our "
                "product team reviews all suggestions during sprint planning.'",
        actionable=False,
    ),
    KBArticle(
        id="KB-007", title="VIP / Enterprise Escalation Protocol",
        category=TicketCategory.VIP,
        keywords=["vip", "enterprise", "churn", "cancel", "competitor", "escalat", "account"],
        content="CRITICAL: Enterprise accounts mentioning competitors, cancellation, or "
                "contract renewal MUST be escalated to Account Management immediately. "
                "DO NOT attempt to handle retention yourself. "
                "DO NOT promise discounts, contract changes, or feature timelines. "
                "Reply acknowledging their concerns and confirm AM will follow up within 24h. "
                "Escalation team: account_management.",
        actionable=False, action_hint="",
    ),
    KBArticle(
        id="KB-008", title="API Rate Limits by Plan",
        category=TicketCategory.ACCOUNT,
        keywords=["api", "rate limit", "throttl", "requests", "hour", "quota"],
        content="API rate limits by plan: Free: 1,000 req/hr. Pro: 10,000 req/hr. "
                "Enterprise: 100,000 req/hr. If a customer reports being throttled below "
                "their plan limit, escalate to engineering to check their account config. "
                "Common cause: migration bugs can set wrong limits.",
        actionable=False,
    ),
    KBArticle(
        id="KB-009", title="Invoice / PO Number Updates",
        category=TicketCategory.BILLING,
        keywords=["invoice", "po number", "purchase order", "billing profile"],
        content="To add a PO number to a customer's invoice: Use "
                "apply_action('update_billing_profile'). Enterprise and Pro customers can "
                "have custom invoice fields. Free plan does not support custom invoices.",
        actionable=True, action_hint="update_billing_profile",
    ),
    KBArticle(
        id="KB-010", title="SSO / SAML Setup Guide",
        category=TicketCategory.GENERAL,
        keywords=["sso", "saml", "single sign-on", "metadata", "certificate", "identity"],
        content="SSO setup documentation is at docs.ourproduct.com/sso. "
                "SAML metadata URL: auth.ourproduct.com/saml/metadata. "
                "Supported providers: Okta, Azure AD, Google Workspace, OneLogin. "
                "SSO is available on Enterprise plan only. "
                "Setup requires admin access and takes about 30 minutes.",
        actionable=False,
    ),
    KBArticle(
        id="KB-011", title="Security — Suspicious Login Investigation",
        category=TicketCategory.ACCOUNT,
        keywords=["security", "suspicious", "login", "unauthorized", "breach", "hack", "ip"],
        content="CRITICAL: Any report of suspicious login activity MUST be escalated to the "
                "Security team immediately. DO NOT attempt to investigate yourself. "
                "Advise the customer to: (1) Change their password immediately, "
                "(2) Enable 2FA if not already active, (3) Review their recent activity log. "
                "Escalation team: security.",
        actionable=False,
    ),
    KBArticle(
        id="KB-012", title="Cancellation Handling",
        category=TicketCategory.ACCOUNT,
        keywords=["cancel", "cancellation", "unsubscribe", "close account", "leave"],
        content="Cancellation requests from paying customers should be escalated to "
                "Account Management for retention attempt. DO NOT process cancellation directly. "
                "Acknowledge the customer's frustration, apologize for their experience, "
                "and confirm that a senior team member will reach out within 24 hours. "
                "Escalation team: account_management.",
        actionable=False,
    ),
    KBArticle(
        id="KB-013", title="PDF Export",
        category=TicketCategory.BUG,
        keywords=["pdf", "export", "pdf export"],
        content="PDF export is working normally. No known bugs. "
                "The CSV export crash (ENG-4521) does NOT affect PDF exports. "
                "If a customer reports PDF export issues, ask for browser and OS details "
                "and escalate to engineering with reproduction steps.",
        actionable=False,
    ),
    KBArticle(
        id="KB-014", title="Spam / Phishing Ticket Handling",
        category=TicketCategory.SPAM,
        keywords=["spam", "phishing", "scam", "won", "prize", "suspend", "verify"],
        content="Tickets identified as spam or phishing should be closed immediately "
                "using apply_action('close_spam'). Do NOT reply to spam tickets. "
                "Do NOT click any links in spam messages.",
        actionable=True, action_hint="close_spam",
    ),
    KBArticle(
        id="KB-015", title="Billing History Lookup",
        category=TicketCategory.BILLING,
        keywords=["billing", "history", "charges", "payments", "C-100", "C-105"],
        content="Billing history results:\n"
                "- C-100 (Alice Park): Charged $29.99 on Mar 1 and $29.99 on Mar 3. "
                "CONFIRMED DUPLICATE — gateway timeout caused retry.\n"
                "- C-105 (Frank Okafor): Charged $199.00 on Mar 10 for annual upgrade. "
                "Single charge, legitimate — but customer says it was accidental.",
        actionable=False,
    ),
]


# ---------------------------------------------------------------------------
# Response Templates
# ---------------------------------------------------------------------------

TEMPLATES = {
    "password_reset": Template(
        id="password_reset", name="Password Reset Confirmation",
        category=TicketCategory.PASSWORD,
        message="Hi {customer_name},\n\n"
                "I've reset your password. You should receive a reset link at {email} "
                "within the next few minutes. If you don't see it, please check your spam folder.\n\n"
                "For security, the link expires in 24 hours.\n\n"
                "Best regards,\nSupport Team",
        appropriate_for=["password"],
    ),
    "export_guide": Template(
        id="export_guide", name="Export Data Guide",
        category=TicketCategory.GENERAL,
        message="Hi {customer_name},\n\n"
                "To export your data to CSV:\n"
                "1. Go to your Project\n"
                "2. Click Settings > Export\n"
                "3. Choose CSV format\n"
                "4. Click Download\n\n"
                "You'll find the Export option under the 'Data' tab in your project settings.\n\n"
                "Let me know if you need anything else!\n\n"
                "Best regards,\nSupport Team",
        appropriate_for=["general", "export"],
    ),
    "known_bug_eta": Template(
        id="known_bug_eta", name="Known Bug with ETA",
        category=TicketCategory.BUG,
        message="Hi {customer_name},\n\n"
                "Thank you for reporting this. This is a known issue that our engineering "
                "team is actively working on. The fix is scheduled for our next release.\n\n"
                "In the meantime, you can work around this by {workaround}.\n\n"
                "I understand this is frustrating, especially as a returning issue. "
                "I apologize for the inconvenience.\n\n"
                "Best regards,\nSupport Team",
        appropriate_for=["bug", "export_bug"],
    ),
    "feature_request_logged": Template(
        id="feature_request_logged", name="Feature Request Acknowledged",
        category=TicketCategory.FEATURE_REQUEST,
        message="Hi {customer_name},\n\n"
                "Thank you for the suggestion! We've logged your feature request and our "
                "product team reviews all feedback during sprint planning.\n\n"
                "While I can't promise a timeline, know that your input helps shape "
                "our roadmap.\n\n"
                "Best regards,\nSupport Team",
        appropriate_for=["feature_request"],
    ),
    "sso_guide": Template(
        id="sso_guide", name="SSO Setup Guide",
        category=TicketCategory.GENERAL,
        message="Hi {customer_name},\n\n"
                "Here are the SSO/SAML setup details:\n\n"
                "- Documentation: docs.ourproduct.com/sso\n"
                "- SAML Metadata URL: auth.ourproduct.com/saml/metadata\n"
                "- Supported providers: Okta, Azure AD, Google Workspace, OneLogin\n\n"
                "Setup requires admin access and typically takes about 30 minutes. "
                "The docs include step-by-step instructions for each provider.\n\n"
                "Let me know if your IT team runs into any issues!\n\n"
                "Best regards,\nSupport Team",
        appropriate_for=["general", "sso"],
    ),
    "escalation_ack": Template(
        id="escalation_ack", name="Escalation Acknowledgment",
        category=TicketCategory.VIP,
        message="Hi {customer_name},\n\n"
                "Thank you for reaching out. I understand your concerns and I want you "
                "to know we take them very seriously.\n\n"
                "I've escalated your case to our {team} team, and a senior team member "
                "will be in touch with you within 24 hours.\n\n"
                "Best regards,\nSupport Team",
        appropriate_for=["vip", "escalation"],
    ),
    "refund_confirmation": Template(
        id="refund_confirmation", name="Refund Processed",
        category=TicketCategory.BILLING,
        message="Hi {customer_name},\n\n"
                "I've processed a refund of ${amount} to your original payment method. "
                "It should appear on your statement within 3-5 business days.\n\n"
                "I apologize for the inconvenience. If you have any other questions, "
                "don't hesitate to reach out.\n\n"
                "Best regards,\nSupport Team",
        appropriate_for=["billing", "refund"],
    ),
    "spam_close": Template(
        id="spam_close", name="Spam Ticket Closed",
        category=TicketCategory.SPAM,
        message="[INTERNAL] Ticket closed as spam/phishing. No customer reply sent.",
        appropriate_for=["spam"],
    ),
}
