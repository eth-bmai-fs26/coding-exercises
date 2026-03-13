"""Scenario data for The Supply Line — entities, orders, KB, templates."""

from supply_line.data import (
    Entity, Order, KBArticle, Template,
    EntityTier, OrderCategory, OrderPriority, OrderStatus, Department,
)


# ---------------------------------------------------------------------------
# Entities (Clients, Suppliers, Internal, Regulator)
# ---------------------------------------------------------------------------

ENTITIES = {
    # Internal
    "E-001": Entity(
        id="E-001", name="Hans Richter", role="internal",
        tier=EntityTier.INTERNAL, industry="Logistics",
        notes=["CEO of NovaTrade", "Staked reputation on Project Aurora"],
    ),
    # Clients
    "E-010": Entity(
        id="E-010", name="Meridian Foods", role="client",
        tier=EntityTier.ENTERPRISE, industry="Food Manufacturing",
        notes=["Multiple active orders", "Sensitive to delays"],
    ),
    "E-011": Entity(
        id="E-011", name="Helvetica Pharma", role="client",
        tier=EntityTier.ENTERPRISE, industry="Pharmaceutical",
        notes=["Quality-critical", "Regulatory requirements"],
    ),
    "E-012": Entity(
        id="E-012", name="Apex Manufacturing", role="client",
        tier=EntityTier.STANDARD, industry="Industrial",
        notes=["Sends rush orders", "Threatens to switch suppliers"],
    ),
    "E-013": Entity(
        id="E-013", name="RUAG Electronics", role="client",
        tier=EntityTier.ENTERPRISE, industry="Defense/Aerospace",
        notes=["Customs-heavy orders", "Strict documentation requirements"],
    ),
    # Suppliers
    "E-020": Entity(
        id="E-020", name="SteelWorks GmbH", role="supplier",
        tier=EntityTier.STANDARD, industry="Industrial Parts",
        notes=["Reliable but pricing disputes"],
    ),
    "E-021": Entity(
        id="E-021", name="ChemPure AG", role="supplier",
        tier=EntityTier.STANDARD, industry="Chemical Coatings",
        notes=["Quality issues with recent batches"],
    ),
    "E-022": Entity(
        id="E-022", name="TechParts Shenzhen", role="supplier",
        tier=EntityTier.STANDARD, industry="Electronics",
        notes=["International supplier", "Customs-heavy"],
    ),
    "E-023": Entity(
        id="E-023", name="MechPro Engineering", role="supplier",
        tier=EntityTier.STANDARD, industry="Engineering Specs",
        notes=["Depends on coating specs for v2.1"],
    ),
    "E-024": Entity(
        id="E-024", name="QuickShip Ltd", role="supplier",
        tier=EntityTier.BLACKLISTED, industry="Logistics",
        notes=["BLACKLISTED — quality violations", "DO NOT ORDER"],
    ),
    "E-025": Entity(
        id="E-025", name="BargainParts Co", role="supplier",
        tier=EntityTier.BLACKLISTED, industry="Parts",
        notes=["BLACKLISTED — fraud", "DO NOT ORDER"],
    ),
    # Regulator
    "E-030": Entity(
        id="E-030", name="Dr. Muller", role="regulator",
        tier=EntityTier.REGULATOR, industry="Swiss Trade Authority",
        notes=["Inspector", "Demands compliance package"],
    ),
    # System
    "E-099": Entity(
        id="E-099", name="SpamBot3000", role="system",
        tier=EntityTier.SYSTEM, industry="Automated Monitoring",
    ),
}


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

# Wave 1: Initial orders
INITIAL_ORDERS = [
    # --- Boss A: Project Aurora (CRITICAL, first in queue) ---
    Order(
        id="T-001", entity_id="E-001", category=OrderCategory.LAUNCH,
        priority=OrderPriority.CRITICAL, created_turn=0,
        subject="CRITICAL — Project Aurora launch coordination",
        message="CRITICAL — Project Aurora launch in 7 days. CEO Hans Richter has staked "
                "the company's reputation on this. Three critical components needed:\n"
                "(1) TechParts microcontrollers — STUCK AT CUSTOMS (see order T-005)\n"
                "(2) ChemPure specialty coating — FAILED QC (see order T-008)\n"
                "(3) Engineering spec v2.1 — waiting on MechPro confirmation (pending)\n\n"
                "Launch CANNOT proceed until all three are secured. "
                "Prepare launch readiness briefing and get authorization.",
        requires_lookup=True, lookup_query="aurora launch protocol",
        requires_briefing=True,
        briefing_prerequisites=["T-005", "T-008", "T-012"],
        briefing_type="launch",
        score_potential=8,
        chain_id="aurora",
    ),
    # --- Standard reorder (easy) ---
    Order(
        id="T-002", entity_id="E-020", category=OrderCategory.REORDER,
        priority=OrderPriority.LOW, created_turn=0,
        subject="Reorder: SKU-4421 industrial bearings below threshold",
        message="SKU-4421 (industrial bearings) inventory at 12 units, reorder point is 50. "
                "Supplier: SteelWorks GmbH. Standard lead time: 5 days. Please reorder.",
        requires_lookup=True, lookup_query="reorder procedures",
        requires_action="place_order",
        correct_template="reorder_confirmation",
        score_potential=3,
    ),
    # --- Standard reorder (triggers chain) ---
    Order(
        id="T-003", entity_id="E-020", category=OrderCategory.REORDER,
        priority=OrderPriority.MEDIUM, created_turn=0,
        subject="Reorder: SKU-7712 precision gears — SteelWorks",
        message="SKU-7712 (precision gears) inventory at 8 units, reorder point is 30. "
                "Supplier: SteelWorks GmbH. Regular order. Please process.",
        requires_lookup=True, lookup_query="reorder procedures",
        requires_action="place_order",
        correct_template="reorder_confirmation",
        score_potential=3,
        chain_id="steelworks_bulk",
    ),
    # --- System alert (spam) ---
    Order(
        id="T-004", entity_id="E-099", category=OrderCategory.SYSTEM_ALERT,
        priority=OrderPriority.LOW, created_turn=0,
        subject="AUTOMATED: Warehouse B3 temperature sensor — normal",
        message="AUTOMATED ALERT: Warehouse B3 temperature sensor reading 18.2°C. "
                "Within acceptable range (15-25°C). Daily check passed. No action required.",
        requires_action="acknowledge_alert",
        score_potential=1,
    ),
    # --- Boss A prerequisite: Customs hold (TechParts → RUAG) ---
    Order(
        id="T-005", entity_id="E-022", category=OrderCategory.CUSTOMS,
        priority=OrderPriority.HIGH, created_turn=0,
        subject="Customs hold: Shipment #SH-1190 from TechParts Shenzhen",
        message="Shipment #SH-1190 from TechParts Shenzhen held at Zurich customs. "
                "Missing Form 47-B (certificate of origin). "
                "Client: RUAG Electronics. Deadline: 5 days.\n\n"
                "NOTE: These microcontrollers are also needed for Project Aurora.",
        requires_lookup=True, lookup_query="customs documentation",
        requires_action="submit_documents",
        correct_template="customs_update",
        score_potential=4,
    ),
    # --- Boss B prerequisite: Customs hold (TechParts → Meridian) ---
    Order(
        id="T-006", entity_id="E-022", category=OrderCategory.CUSTOMS,
        priority=OrderPriority.MEDIUM, created_turn=0,
        subject="Customs hold: Shipment #SH-2201 from TechParts — Meridian Foods",
        message="Shipment #SH-2201 from TechParts Shenzhen held at Basel customs. "
                "Missing commercial invoice and packing list. "
                "Client: Meridian Foods. Standard processing.",
        requires_lookup=True, lookup_query="customs documentation",
        requires_action="submit_documents",
        correct_template="customs_update",
        score_potential=4,
        chain_id="meridian_customs",
    ),
    # --- Shipping delay ---
    Order(
        id="T-007", entity_id="E-010", category=OrderCategory.DELAY,
        priority=OrderPriority.HIGH, created_turn=0,
        subject="Shipping delay: Meridian Foods shipment #SH-2287",
        message="Client Meridian Foods reports their shipment #SH-2287 hasn't arrived. "
                "Original ETA was 3 days ago. Carrier: FastFreight. "
                "This is a temperature-sensitive food ingredients shipment.",
        requires_lookup=True, lookup_query="shipping delay resolution",
        requires_action="update_timeline",
        correct_template="delay_notification",
        score_potential=4,
    ),
    # --- Boss A prerequisite: Quality rejection (ChemPure → Helvetica) ---
    Order(
        id="T-008", entity_id="E-021", category=OrderCategory.QUALITY,
        priority=OrderPriority.HIGH, created_turn=0,
        subject="QC rejection: Shipment #SH-3301 from ChemPure AG",
        message="QC inspection FAILED for shipment #SH-3301 from ChemPure AG. "
                "Contamination found in batch B-7744. 200 units of specialty coating affected. "
                "Client: Helvetica Pharma (pharma-grade required).\n\n"
                "NOTE: This coating is also a critical component for Project Aurora.",
        requires_lookup=True, lookup_query="quality control rejection",
        requires_action="reject_shipment",
        requires_claim=True,
        correct_template="quality_issue",
        score_potential=5,
        chain_id="chempure_quality",
    ),
    # --- Boss B prerequisite: Supplier dispute ---
    Order(
        id="T-009", entity_id="E-020", category=OrderCategory.DISPUTE,
        priority=OrderPriority.MEDIUM, created_turn=0,
        subject="Pricing dispute: SteelWorks GmbH invoice #PO-8812",
        message="Invoice from SteelWorks GmbH shows EUR 47,200 for order #PO-8812. "
                "Contract rate is EUR 38/unit x 1000 = EUR 38,000. "
                "Overcharge of EUR 9,200 (24% above contract). Payment due in 3 days.",
        requires_lookup=True, lookup_query="supplier dispute pricing",
        requires_escalation="procurement",
        correct_template="dispute_resolution",
        score_potential=5,
        chain_id="steelworks_dispute",
    ),
    # --- Rush order (TRAP — do NOT escalate) ---
    Order(
        id="T-010", entity_id="E-012", category=OrderCategory.RUSH,
        priority=OrderPriority.HIGH, created_turn=0,
        subject="URGENT: Rush order from Apex Manufacturing",
        message="URGENT from client Apex Manufacturing: Need 500 units of SKU-7890 "
                "by Friday. Regular lead time is 2 weeks. "
                "They're threatening to switch suppliers if we can't deliver.",
        requires_lookup=True, lookup_query="expedited shipping policy",
        requires_action="place_order",
        correct_template="rush_confirmation",
        score_potential=3,
        order_value=15000,
    ),
    # --- System alert (spam) ---
    Order(
        id="T-011", entity_id="E-099", category=OrderCategory.SYSTEM_ALERT,
        priority=OrderPriority.LOW, created_turn=0,
        subject="AUTOMATED: Warehouse A1 stock count — routine",
        message="AUTOMATED ALERT: Warehouse A1 daily stock count complete. "
                "All SKUs within expected ranges. No discrepancies found.",
        requires_action="acknowledge_alert",
        score_potential=1,
    ),
    # --- Boss B: Regulatory shutdown threat ---
    Order(
        id="T-020", entity_id="E-030", category=OrderCategory.REGULATORY,
        priority=OrderPriority.HIGH, created_turn=0,
        subject="URGENT — STA regulatory compliance review",
        message="Swiss Trade Authority (STA) has flagged NovaTrade for import compliance "
                "review after recent customs irregularities. Inspector Dr. Muller demands "
                "a comprehensive compliance package within the review period or NovaTrade's "
                "import license will be SUSPENDED.\n\n"
                "Package must include:\n"
                "(1) Proof of proper customs handling (see Meridian customs case T-006)\n"
                "(2) Supplier procurement audit trail (see SteelWorks dispute T-009)\n"
                "(3) Compiled import records for past 30 days (pending internal audit)\n\n"
                "Prepare compliance package and submit to STA.",
        requires_lookup=True, lookup_query="regulatory compliance STA",
        requires_briefing=True,
        briefing_prerequisites=["T-006", "T-009", "T-016"],
        briefing_type="compliance",
        score_potential=7,
        chain_id="regulatory",
    ),
]


# Wave 2: Chain orders (unlocked by resolving wave 1)
CHAIN_ORDERS = {
    # T-008 (quality) → T-012 (spec confirmation) — Boss A prerequisite
    "chempure_quality": Order(
        id="T-012", entity_id="E-023", category=OrderCategory.REORDER,
        priority=OrderPriority.MEDIUM, created_turn=-1,
        subject="MechPro spec confirmation needed — replacement coating",
        message="MechPro Engineering needs the replacement coating specs to finalize "
                "the v2.1 engineering spec sheet for Project Aurora.\n\n"
                "Please confirm the replacement supplier and batch number from the "
                "ChemPure quality rejection resolution. "
                "Use place_order to confirm the spec with MechPro.",
        requires_action="place_order",
        correct_template="reorder_confirmation",
        score_potential=3,
    ),
    # T-003 (reorder gears) → T-015 (bulk discount offer)
    "steelworks_bulk": Order(
        id="T-015", entity_id="E-020", category=OrderCategory.DISPUTE,
        priority=OrderPriority.MEDIUM, created_turn=-1,
        subject="SteelWorks bulk discount offer — procurement approval needed",
        message="SteelWorks GmbH is offering a 15% bulk discount on next quarter's "
                "precision gear order if committed by end of week. "
                "Total value: EUR 62,000. Exceeds coordinator authority (EUR 50,000). "
                "Need procurement/finance approval.",
        requires_lookup=True, lookup_query="budget authority",
        requires_escalation="finance",
        score_potential=3,
        order_value=62000,
    ),
    # T-006 (customs Meridian) → T-016 (compliance audit) — Boss B prerequisite
    "meridian_customs": Order(
        id="T-016", entity_id="E-030", category=OrderCategory.CUSTOMS,
        priority=OrderPriority.HIGH, created_turn=-1,
        subject="Compliance audit: Compile import records for STA review",
        message="Following the resolution of the Meridian customs case, Swiss customs "
                "authority has flagged NovaTrade for a documentation audit.\n\n"
                "Compile all import documentation from the past 30 days using "
                "compile_records. Submit within 48 hours.",
        requires_lookup=True, lookup_query="compliance audit procedures",
        requires_action="compile_records",
        correct_template="compliance_status",
        score_potential=4,
    ),
    # T-009 (dispute) → T-017 (contract renewal)
    "steelworks_dispute": Order(
        id="T-017", entity_id="E-020", category=OrderCategory.DISPUTE,
        priority=OrderPriority.MEDIUM, created_turn=-1,
        subject="SteelWorks contract renewal — renegotiate terms",
        message="SteelWorks GmbH contract expires next month. Given the recent pricing "
                "dispute, we need to either renegotiate terms or find an alternative "
                "supplier for industrial parts.\n\n"
                "Escalate to procurement for contract renewal negotiation.",
        requires_escalation="procurement",
        correct_template="dispute_resolution",
        score_potential=4,
    ),
}


# Wave 3: Late orders (arrive mid-game)
LATE_ORDERS = [
    # Shipping delay (turn 15)
    Order(
        id="T-013", entity_id="E-010", category=OrderCategory.DELAY,
        priority=OrderPriority.MEDIUM, created_turn=15,
        subject="Shipping delay: Meridian Foods — second shipment #SH-2350",
        message="Meridian Foods reports a second shipment #SH-2350 is delayed. "
                "Carrier: EuroFreight. Original ETA was 2 days ago. "
                "Contains refrigerated dairy ingredients.",
        requires_lookup=True, lookup_query="shipping delay resolution",
        requires_action="update_timeline",
        correct_template="delay_notification",
        score_potential=4,
    ),
    # Standard reorder (turn 25)
    Order(
        id="T-014", entity_id="E-020", category=OrderCategory.REORDER,
        priority=OrderPriority.LOW, created_turn=25,
        subject="Reorder: SKU-3308 rubber seals — routine",
        message="SKU-3308 (rubber seals) inventory at 20 units, reorder point is 40. "
                "Supplier: SteelWorks GmbH. Standard order, low urgency.",
        requires_lookup=True, lookup_query="reorder procedures",
        requires_action="place_order",
        correct_template="reorder_confirmation",
        score_potential=3,
    ),
    # Rush order — TRAP (turn 40)
    Order(
        id="T-018", entity_id="E-012", category=OrderCategory.RUSH,
        priority=OrderPriority.HIGH, created_turn=40,
        subject="URGENT: Apex Manufacturing — second rush order",
        message="URGENT from Apex Manufacturing AGAIN: Need 800 units of SKU-4455 "
                "immediately. Says they'll go to our competitor by Monday. "
                "Standard lead time is 10 days.",
        requires_lookup=True, lookup_query="expedited shipping policy",
        requires_action="place_order",
        correct_template="rush_confirmation",
        score_potential=3,
        order_value=24000,
    ),
    # System alert (turn 55)
    Order(
        id="T-019", entity_id="E-099", category=OrderCategory.SYSTEM_ALERT,
        priority=OrderPriority.LOW, created_turn=55,
        subject="AUTOMATED: Warehouse C2 humidity check — normal",
        message="AUTOMATED ALERT: Warehouse C2 humidity at 42%. "
                "Within acceptable range (30-60%). All clear.",
        requires_action="acknowledge_alert",
        score_potential=1,
    ),
    # Another reorder (turn 30)
    Order(
        id="T-021", entity_id="E-011", category=OrderCategory.REORDER,
        priority=OrderPriority.MEDIUM, created_turn=30,
        subject="Reorder: SKU-9901 lab-grade containers — Helvetica Pharma",
        message="SKU-9901 (lab-grade containers) inventory low. Helvetica Pharma "
                "needs these for next batch. Supplier: ChemPure AG (different product line, "
                "not affected by the coating quality issue). Standard reorder.",
        requires_lookup=True, lookup_query="reorder procedures",
        requires_action="place_order",
        correct_template="reorder_confirmation",
        score_potential=3,
    ),
    # Quality issue (turn 45) — second quality case
    Order(
        id="T-022", entity_id="E-020", category=OrderCategory.QUALITY,
        priority=OrderPriority.MEDIUM, created_turn=45,
        subject="QC warning: SteelWorks batch B-9021 — minor defects",
        message="QC inspection found minor surface defects in SteelWorks batch B-9021. "
                "15 of 500 units affected (3%). Below rejection threshold (5%) but "
                "client RUAG Electronics has strict tolerances.\n\n"
                "Recommend: file claim for affected units and notify client.",
        requires_lookup=True, lookup_query="quality control rejection",
        requires_action="file_claim",
        requires_claim=True,
        correct_template="quality_issue",
        score_potential=4,
    ),
]


# ---------------------------------------------------------------------------
# Knowledge Base
# ---------------------------------------------------------------------------

KNOWLEDGE_BASE = [
    KBArticle(
        id="KB-001", title="Reorder Procedures",
        category=OrderCategory.REORDER,
        keywords=["reorder", "inventory", "threshold", "sku", "stock", "order"],
        content="Standard reorder process:\n"
                "1. Verify inventory levels with check_inventory(sku)\n"
                "2. Confirm supplier is approved (check KB-007)\n"
                "3. Place order with place_order(supplier, sku, quantity)\n"
                "4. Notify client with reorder_confirmation template\n"
                "5. Close the order.\n\n"
                "Standard lead times: 3-5 days domestic, 7-14 days international.",
        actionable=True, action_hint="place_order",
    ),
    KBArticle(
        id="KB-002", title="Expedited Shipping Policy",
        category=OrderCategory.RUSH,
        keywords=["rush", "urgent", "expedited", "fast", "express", "shipping"],
        content="EXPEDITED SHIPPING POLICY:\n"
                "- Orders under 1000 units: expedited shipping available at +30% cost. "
                "NO management approval needed. Use place_order with expedited=True.\n"
                "- Orders over 1000 units: requires VP approval — escalate to logistics.\n\n"
                "DO NOT escalate rush orders under 1000 units to management. "
                "This wastes an operations token. Just use expedited shipping.",
        actionable=True, action_hint="place_order with expedited=True",
    ),
    KBArticle(
        id="KB-003", title="Quality Control Rejection Process",
        category=OrderCategory.QUALITY,
        keywords=["qc", "quality", "rejection", "contamination", "defect", "batch"],
        content="When a shipment fails QC:\n"
                "1. Reject shipment: reject_shipment(shipment_id, reason)\n"
                "2. File claim: file_claim(supplier, amount)\n"
                "3. Reorder from alternative approved supplier: place_order(...)\n"
                "4. Notify client with quality_issue template\n"
                "5. Close the order.\n\n"
                "Claims must include batch number and inspection report reference.\n"
                "Alternative approved coating suppliers: PureChem Basel, CoatTech Munich.",
        actionable=True, action_hint="reject_shipment then file_claim then place_order",
    ),
    KBArticle(
        id="KB-004", title="Customs Documentation Guide",
        category=OrderCategory.CUSTOMS,
        keywords=["customs", "hold", "import", "form", "certificate", "documentation", "47-B"],
        content="Required customs documents:\n"
                "- Certificate of origin (Form 47-B)\n"
                "- Commercial invoice\n"
                "- Packing list\n\n"
                "Process:\n"
                "1. check_documentation(shipment_id) — see what's missing\n"
                "2. submit_documents(shipment_id, doc_type) — submit the missing docs\n"
                "3. Notify client with customs_update template\n\n"
                "Processing time: 2-3 business days after submission.",
        actionable=True, action_hint="check_documentation then submit_documents",
    ),
    KBArticle(
        id="KB-005", title="Supplier Escalation Policy",
        category=OrderCategory.DISPUTE,
        keywords=["dispute", "pricing", "overcharge", "contract", "supplier", "escalation"],
        content="Pricing discrepancy handling:\n"
                "- Discrepancy > 5% of contract value: MUST escalate to procurement.\n"
                "- Discrepancy <= 5%: can resolve directly with supplier.\n\n"
                "Process:\n"
                "1. lookup_contract(supplier) to verify contract terms\n"
                "2. verify_pricing(order_id) to confirm discrepancy\n"
                "3. If > 5%: escalate(department='procurement', reason='pricing_discrepancy')\n"
                "4. Notify with dispute_resolution template.",
        actionable=True, action_hint="escalate to procurement",
    ),
    KBArticle(
        id="KB-006", title="Project Aurora Launch Protocol",
        category=OrderCategory.LAUNCH,
        keywords=["aurora", "launch", "product", "briefing", "authorization", "critical"],
        content="CRITICAL — Project Aurora Launch Protocol:\n\n"
                "Launch requires ALL THREE critical components confirmed:\n"
                "1. TechParts microcontrollers (customs clearance)\n"
                "2. ChemPure specialty coating (quality replacement)\n"
                "3. MechPro engineering spec v2.1 (supplier confirmation)\n\n"
                "Process:\n"
                "1. Resolve all three prerequisite orders\n"
                "2. Call prepare_launch_briefing() to compile evidence\n"
                "3. Call authorize_launch(order_id='T-001') to authorize\n"
                "4. Notify with launch_status template\n\n"
                "WARNING: Attempting to authorize without briefing will be rejected. "
                "First attempt is a free warning. Subsequent attempts cost tokens.",
        actionable=True, action_hint="prepare_launch_briefing then authorize_launch",
    ),
    KBArticle(
        id="KB-007", title="Approved Supplier Directory",
        category=OrderCategory.REORDER,
        keywords=["supplier", "approved", "blacklist", "alternative", "quickship", "bargainparts"],
        content="APPROVED SUPPLIERS:\n"
                "- SteelWorks GmbH: industrial parts, gears, bearings\n"
                "- ChemPure AG: chemical coatings, lab supplies\n"
                "- TechParts Shenzhen: electronics, microcontrollers\n"
                "- MechPro Engineering: engineering specs, technical docs\n"
                "- PureChem Basel: alternative coating supplier\n"
                "- CoatTech Munich: alternative coating supplier\n\n"
                "BLACKLISTED (DO NOT ORDER):\n"
                "- QuickShip Ltd: quality violations\n"
                "- BargainParts Co: fraud investigation\n\n"
                "Using a blacklisted supplier = IMMEDIATE operations token loss.",
        actionable=False,
    ),
    KBArticle(
        id="KB-008", title="Client Communication Templates",
        category=OrderCategory.REORDER,
        keywords=["template", "notification", "reply", "update", "communication"],
        content="Available templates:\n"
                "- reorder_confirmation: after placing standard reorder\n"
                "- delay_notification: after updating shipping timeline\n"
                "- quality_issue: after quality rejection and replacement\n"
                "- customs_update: after submitting customs docs\n"
                "- rush_confirmation: after placing expedited order\n"
                "- launch_status: after Aurora launch authorization\n"
                "- compliance_status: after regulatory compliance submission\n"
                "- dispute_resolution: after escalating pricing dispute\n"
                "- general_update: fallback for any other communication",
        actionable=False,
    ),
    KBArticle(
        id="KB-009", title="Budget Authority Matrix",
        category=OrderCategory.DISPUTE,
        keywords=["budget", "approval", "authorization", "limit", "finance", "EUR 50000"],
        content="Budget authority levels:\n"
                "- Coordinators: can approve orders up to EUR 50,000\n"
                "- Above EUR 50,000: MUST escalate to Finance\n"
                "- Expedited shipping surcharges do NOT count toward the limit\n\n"
                "If an order exceeds EUR 50,000, escalate to finance before proceeding.",
        actionable=False,
    ),
    KBArticle(
        id="KB-010", title="Shipping Delay Resolution",
        category=OrderCategory.DELAY,
        keywords=["delay", "carrier", "alternative", "reroute", "shipping", "late"],
        content="Delay resolution process:\n"
                "1. lookup_shipment(shipment_id) — get current status\n"
                "2. If delay > 5 days: check_alternatives() for alt carriers\n"
                "3. If delay > 10 days: escalate to logistics management\n"
                "4. update_timeline(order_id, new_eta) — set new delivery date\n"
                "5. Notify client with delay_notification template.",
        actionable=True, action_hint="lookup_shipment then update_timeline",
    ),
    KBArticle(
        id="KB-011", title="Inventory Management Alerts",
        category=OrderCategory.SYSTEM_ALERT,
        keywords=["alert", "system", "automated", "sensor", "temperature", "humidity", "routine"],
        content="System alerts (temperature, humidity, stock count) are INFORMATIONAL ONLY.\n\n"
                "Process: acknowledge_alert(alert_id) then close_order(order_id).\n"
                "Do NOT investigate further. Do NOT escalate.\n"
                "These are routine automated checks.",
        actionable=True, action_hint="acknowledge_alert",
    ),
    KBArticle(
        id="KB-012", title="Operations Token Policy",
        category=OrderCategory.REORDER,
        keywords=["token", "penalty", "violation", "break", "operations"],
        content="Operations tokens (you start with 3):\n\n"
                "COSTS A TOKEN:\n"
                "- Ordering from blacklisted supplier\n"
                "- Unauthorized launch/compliance attempt (after first warning)\n"
                "- Escalating when not needed (e.g., rush orders under 1000 units)\n"
                "- Wrong escalation department\n\n"
                "RECOVER: take_break() restores 1 token but costs 5 turns.\n"
                "AT 0 TOKENS: Game over — management steps in.",
        actionable=False,
    ),
    KBArticle(
        id="KB-013", title="MechPro Engineering Coordination",
        category=OrderCategory.REORDER,
        keywords=["mechpro", "engineering", "specs", "v2.1", "coating", "aurora"],
        content="MechPro Engineering requires final coating specs before releasing "
                "the v2.1 engineering spec sheet.\n\n"
                "Contact MechPro ONLY after the replacement coating supplier is confirmed "
                "(i.e., after the ChemPure quality rejection T-008 is resolved).\n\n"
                "The spec confirmation order (T-012) will appear after T-008 is resolved.",
        actionable=False,
    ),
    KBArticle(
        id="KB-014", title="Compliance and Audit Procedures",
        category=OrderCategory.CUSTOMS,
        keywords=["audit", "compliance", "customs", "documentation", "records", "compile"],
        content="Compliance audit process:\n"
                "1. compile_records(period='30_days') — gather all import records\n"
                "2. Submit compiled records\n"
                "3. Close the audit order\n\n"
                "Must be completed within 48 hours of audit notification.",
        actionable=True, action_hint="compile_records",
    ),
    KBArticle(
        id="KB-015", title="STA Regulatory Review Protocol",
        category=OrderCategory.REGULATORY,
        keywords=["STA", "regulatory", "shutdown", "compliance", "package", "import", "license", "muller"],
        content="CRITICAL — Swiss Trade Authority (STA) Review Protocol:\n\n"
                "Compliance package must include THREE evidence items:\n"
                "1. Proof of proper customs handling (resolve customs cases first)\n"
                "2. Supplier procurement audit trail (resolve pricing disputes first)\n"
                "3. Compiled import records (complete internal audit first)\n\n"
                "Process:\n"
                "1. Resolve prerequisite orders: T-006, T-009, and T-016 (audit)\n"
                "2. Call prepare_compliance_package() to compile evidence\n"
                "3. Call submit_compliance(order_id='T-020') to submit to STA\n\n"
                "WARNING: Submitting without package will be rejected. "
                "First attempt is a free warning. Subsequent attempts cost tokens.",
        actionable=True, action_hint="prepare_compliance_package then submit_compliance",
    ),
]


# ---------------------------------------------------------------------------
# Notification Templates
# ---------------------------------------------------------------------------

TEMPLATES = {
    "reorder_confirmation": Template(
        id="reorder_confirmation", name="Reorder Confirmation",
        category=OrderCategory.REORDER,
        message="Your reorder for {sku} has been placed with {supplier}. "
                "Expected delivery: {eta}. Order reference: {order_ref}.",
        appropriate_for=["reorder"],
    ),
    "delay_notification": Template(
        id="delay_notification", name="Delay Notification",
        category=OrderCategory.DELAY,
        message="We're aware of the delay on shipment {shipment_id}. "
                "New estimated arrival: {new_eta}. We apologize for the inconvenience "
                "and are monitoring the situation closely.",
        appropriate_for=["delay"],
    ),
    "quality_issue": Template(
        id="quality_issue", name="Quality Issue Notification",
        category=OrderCategory.QUALITY,
        message="A quality issue was detected in your recent shipment. "
                "We've rejected the affected batch and initiated a replacement order "
                "with {alt_supplier}. Expected delivery: {eta}.",
        appropriate_for=["quality"],
    ),
    "customs_update": Template(
        id="customs_update", name="Customs Update",
        category=OrderCategory.CUSTOMS,
        message="Your shipment {shipment_id} is being processed through customs. "
                "Required documentation has been submitted. "
                "Expected clearance: {eta}.",
        appropriate_for=["customs"],
    ),
    "rush_confirmation": Template(
        id="rush_confirmation", name="Rush Order Confirmation",
        category=OrderCategory.RUSH,
        message="Your expedited order has been placed. "
                "{quantity} units of {sku} via express shipping. "
                "Delivery by {eta}.",
        appropriate_for=["rush"],
    ),
    "launch_status": Template(
        id="launch_status", name="Launch Status Update",
        category=OrderCategory.LAUNCH,
        message="Project Aurora update: All critical components secured. "
                "Launch readiness briefing prepared. Authorization confirmed.",
        appropriate_for=["launch"],
    ),
    "compliance_status": Template(
        id="compliance_status", name="Compliance Status Update",
        category=OrderCategory.REGULATORY,
        message="NovaTrade compliance update: All required documentation compiled "
                "and submitted to Swiss Trade Authority. Reference: {ref_id}.",
        appropriate_for=["regulatory", "compliance"],
    ),
    "dispute_resolution": Template(
        id="dispute_resolution", name="Dispute Resolution Notice",
        category=OrderCategory.DISPUTE,
        message="The pricing discrepancy on order {order_id} has been escalated "
                "to our procurement team. Expected resolution: {eta}.",
        appropriate_for=["dispute"],
    ),
    "general_update": Template(
        id="general_update", name="General Update",
        category=OrderCategory.REORDER,
        message="Update on your order {order_id}: {status_message}",
        appropriate_for=["general"],
    ),
}
