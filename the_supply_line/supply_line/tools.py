"""Tool implementations for The Supply Line — the actions the agent can take."""

from dataclasses import dataclass
from typing import Optional

from supply_line.data import (
    OrderCategory, OrderPriority, OrderStatus, Department,
)
from supply_line.game import SupplyWorld, AgentState


@dataclass
class ToolResult:
    success: bool
    message: str


# Blacklisted supplier names (case-insensitive match)
BLACKLISTED_SUPPLIERS = {"quickship", "quickship ltd", "bargainparts", "bargainparts co"}


class SupplyTools:
    """All tools the operations coordinator can use each turn."""

    def __init__(self, agent: AgentState, world: SupplyWorld):
        self.agent = agent
        self.world = world

    # ------------------------------------------------------------------
    # Tool: check_orders
    # ------------------------------------------------------------------
    def check_orders(self) -> ToolResult:
        """See the current order queue (free action)."""
        return ToolResult(True, self.world.queue_summary())

    # ------------------------------------------------------------------
    # Tool: read_order
    # ------------------------------------------------------------------
    def read_order(self, order_id: str = "") -> ToolResult:
        """Read an order's details."""
        order_id = order_id.strip()

        if not order_id:
            for o in self.world.queue:
                if not o.has_been_read:
                    order_id = o.id
                    break
            if not order_id and self.world.queue:
                order_id = self.world.queue[0].id
            if not order_id:
                return ToolResult(False, "No orders in queue.")

        order = self.world.get_order(order_id)
        if not order:
            return ToolResult(False, f"Order {order_id} not found.")
        if order.status == OrderStatus.RESOLVED:
            return ToolResult(False, f"Order {order_id} is already resolved.")

        order.has_been_read = True
        order.status = OrderStatus.IN_PROGRESS
        self.world.active_order = order

        entity = self.world.get_entity(order.entity_id)
        entity_info = ""
        if entity:
            entity_info = (
                f"\nEntity: {entity.name} ({entity.role}) | "
                f"Tier: {entity.tier.value} | "
                f"Industry: {entity.industry}"
            )
            if entity.notes:
                entity_info += f"\nNotes: {'; '.join(entity.notes)}"

        sla_info = f"SLA: {order.priority.sla_turns} turns"
        value_info = f" | Value: EUR {order.order_value:,}" if order.order_value else ""

        return ToolResult(True,
            f"--- Order {order.id} ---\n"
            f"Subject: {order.subject}\n"
            f"Category: {order.category.value} | "
            f"Priority: {order.priority.value} | {sla_info}{value_info}\n"
            f"{entity_info}\n\n"
            f"Details:\n{order.message}"
        )

    # ------------------------------------------------------------------
    # Tool: lookup_kb
    # ------------------------------------------------------------------
    def lookup_kb(self, query: str = "") -> ToolResult:
        """Search the knowledge base."""
        query = query.strip()
        if not query:
            return ToolResult(False, "Please provide a search query.")

        results = self.world.search_kb(query)
        if not results:
            return ToolResult(True,
                f"No knowledge base articles found for '{query}'. "
                "Consider escalating if this is outside standard procedures."
            )

        if self.world.active_order:
            self.world.active_order.lookup_done = True

        articles = results[:3]
        lines = [f"Knowledge Base results for '{query}':"]
        for article in articles:
            lines.append(f"\n--- {article.id}: {article.title} ---\n{article.content}")
        return ToolResult(True, "\n".join(lines))

    # ------------------------------------------------------------------
    # Tool: check_inventory
    # ------------------------------------------------------------------
    def check_inventory(self, sku: str = "") -> ToolResult:
        """Check inventory levels for a SKU."""
        sku = sku.strip()
        if not sku:
            return ToolResult(False, "Please specify a SKU.")

        # Simulated inventory data
        inventory = {
            "SKU-4421": ("industrial bearings", 12, 50),
            "SKU-7712": ("precision gears", 8, 30),
            "SKU-7890": ("electronic modules", 45, 100),
            "SKU-4455": ("control valves", 30, 80),
            "SKU-3308": ("rubber seals", 20, 40),
            "SKU-9901": ("lab-grade containers", 5, 25),
        }

        if sku.upper() in inventory or sku in inventory:
            key = sku.upper() if sku.upper() in inventory else sku
            name, current, reorder_point = inventory[key]
            status = "BELOW REORDER POINT" if current < reorder_point else "OK"
            return ToolResult(True,
                f"Inventory for {key} ({name}):\n"
                f"  Current stock: {current} units\n"
                f"  Reorder point: {reorder_point} units\n"
                f"  Status: {status}"
            )

        return ToolResult(True, f"SKU {sku} not found in inventory system.")

    # ------------------------------------------------------------------
    # Tool: lookup_shipment
    # ------------------------------------------------------------------
    def lookup_shipment(self, shipment_id: str = "") -> ToolResult:
        """Get shipment status and tracking."""
        shipment_id = shipment_id.strip()
        if not shipment_id:
            return ToolResult(False, "Please specify a shipment ID.")

        shipments = {
            "SH-1190": ("TechParts Shenzhen → RUAG Electronics", "HELD AT CUSTOMS",
                        "Zurich customs. Missing Form 47-B."),
            "SH-2201": ("TechParts Shenzhen → Meridian Foods", "HELD AT CUSTOMS",
                        "Basel customs. Missing commercial invoice and packing list."),
            "SH-2287": ("FastFreight → Meridian Foods", "DELAYED",
                        "Last scan: Stuttgart hub, 3 days ago. Carrier delay."),
            "SH-2350": ("EuroFreight → Meridian Foods", "DELAYED",
                        "Last scan: Milan depot, 2 days ago. Refrigeration issue."),
            "SH-3301": ("ChemPure AG → Helvetica Pharma", "QC REJECTED",
                        "Contamination in batch B-7744. 200 units affected."),
        }

        if shipment_id in shipments:
            route, status, details = shipments[shipment_id]
            return ToolResult(True,
                f"Shipment {shipment_id}:\n"
                f"  Route: {route}\n"
                f"  Status: {status}\n"
                f"  Details: {details}"
            )

        return ToolResult(True, f"Shipment {shipment_id} not found in tracking system.")

    # ------------------------------------------------------------------
    # Tool: lookup_contract
    # ------------------------------------------------------------------
    def lookup_contract(self, supplier: str = "") -> ToolResult:
        """Get contract terms for a supplier."""
        supplier = supplier.strip().lower()
        if not supplier:
            return ToolResult(False, "Please specify a supplier name.")

        contracts = {
            "steelworks": (
                "SteelWorks GmbH", "Active", "EUR 38/unit for industrial parts",
                "1000 unit minimum order", "Payment NET 30"
            ),
            "chempure": (
                "ChemPure AG", "Active", "EUR 125/unit for specialty coatings",
                "50 unit minimum order", "Payment NET 15"
            ),
            "techparts": (
                "TechParts Shenzhen", "Active", "EUR 22/unit for microcontrollers",
                "500 unit minimum order", "Payment NET 45"
            ),
        }

        for key, (name, status, rate, minimum, payment) in contracts.items():
            if key in supplier:
                return ToolResult(True,
                    f"Contract — {name}:\n"
                    f"  Status: {status}\n"
                    f"  Rate: {rate}\n"
                    f"  Minimum: {minimum}\n"
                    f"  Terms: {payment}"
                )

        return ToolResult(True, f"No contract found for '{supplier}'.")

    # ------------------------------------------------------------------
    # Tool: check_documentation
    # ------------------------------------------------------------------
    def check_documentation(self, shipment_id: str = "") -> ToolResult:
        """Check what customs documents are on file."""
        shipment_id = shipment_id.strip()
        if not shipment_id:
            return ToolResult(False, "Please specify a shipment ID.")

        docs = {
            "SH-1190": {"on_file": ["Commercial invoice", "Packing list"],
                        "missing": ["Certificate of origin (Form 47-B)"]},
            "SH-2201": {"on_file": ["Certificate of origin"],
                        "missing": ["Commercial invoice", "Packing list"]},
        }

        if shipment_id in docs:
            d = docs[shipment_id]
            return ToolResult(True,
                f"Documentation for {shipment_id}:\n"
                f"  On file: {', '.join(d['on_file'])}\n"
                f"  MISSING: {', '.join(d['missing'])}"
            )

        return ToolResult(True, f"No customs records for shipment {shipment_id}.")

    # ------------------------------------------------------------------
    # Tool: check_alternatives
    # ------------------------------------------------------------------
    def check_alternatives(self) -> ToolResult:
        """Find alternative suppliers or carriers."""
        return ToolResult(True,
            "Alternative options available:\n"
            "  Carriers: ExpressLogistics (2-day), SwiftCargo (3-day), RailFreight (5-day)\n"
            "  Coating suppliers: PureChem Basel, CoatTech Munich\n"
            "  Parts suppliers: MetalPro Stuttgart (bearings/gears)\n\n"
            "Use place_order with the alternative supplier name."
        )

    # ------------------------------------------------------------------
    # Tool: place_order
    # ------------------------------------------------------------------
    def place_order(self, supplier: str = "", sku: str = "",
                    quantity: str = "", expedited: str = "") -> ToolResult:
        """Place a purchase order."""
        supplier = supplier.strip()
        if not supplier:
            return ToolResult(False, "Please specify a supplier.")

        # Guardrail: blacklisted supplier
        if supplier.lower().replace(" ", "").replace(".", "") in {
            s.replace(" ", "") for s in BLACKLISTED_SUPPLIERS
        } or any(b in supplier.lower() for b in ["quickship", "bargainparts"]):
            self.agent.operations_tokens -= 1
            self.agent.notes.append(f"VIOLATION: Attempted order from blacklisted supplier {supplier}")
            return ToolResult(False,
                f"VIOLATION: {supplier} is a BLACKLISTED supplier! "
                f"Lost 1 operations token. Remaining: {self.agent.operations_tokens}. "
                "Check KB-007 for approved suppliers."
            )

        if self.world.active_order:
            self.world.active_order.action_applied = True

        is_expedited = expedited.lower() in ("true", "yes", "1") if expedited else False
        exp_text = " (EXPEDITED)" if is_expedited else ""

        return ToolResult(True,
            f"Order placed with {supplier}{exp_text}. "
            f"SKU: {sku or 'as specified'}, Qty: {quantity or 'as needed'}. "
            f"Confirmation pending."
        )

    # ------------------------------------------------------------------
    # Tool: reject_shipment
    # ------------------------------------------------------------------
    def reject_shipment(self, shipment_id: str = "", reason: str = "") -> ToolResult:
        """Reject a failed QC shipment."""
        shipment_id = shipment_id.strip()
        if not shipment_id:
            return ToolResult(False, "Please specify a shipment ID.")

        if self.world.active_order:
            self.world.active_order.action_applied = True

        return ToolResult(True,
            f"Shipment {shipment_id} rejected. Reason: {reason or 'QC failure'}. "
            "Supplier has been notified. File a claim for reimbursement."
        )

    # ------------------------------------------------------------------
    # Tool: file_claim
    # ------------------------------------------------------------------
    def file_claim(self, supplier: str = "", amount: str = "") -> ToolResult:
        """File a claim against a supplier."""
        supplier = supplier.strip()
        if not supplier:
            return ToolResult(False, "Please specify the supplier.")

        if self.world.active_order:
            self.world.active_order.action_applied = True
            self.world.active_order.claim_filed = True

        return ToolResult(True,
            f"Claim filed against {supplier} for EUR {amount or 'pending assessment'}. "
            "Processing time: 5-10 business days."
        )

    # ------------------------------------------------------------------
    # Tool: submit_documents
    # ------------------------------------------------------------------
    def submit_documents(self, shipment_id: str = "", doc_type: str = "") -> ToolResult:
        """Submit customs documentation."""
        shipment_id = shipment_id.strip()
        if not shipment_id:
            return ToolResult(False, "Please specify a shipment ID.")

        if self.world.active_order:
            self.world.active_order.action_applied = True

        return ToolResult(True,
            f"Documents submitted for shipment {shipment_id}. "
            f"Type: {doc_type or 'all required documents'}. "
            "Expected customs clearance: 2-3 business days."
        )

    # ------------------------------------------------------------------
    # Tool: update_timeline
    # ------------------------------------------------------------------
    def update_timeline(self, order_id: str = "", new_eta: str = "") -> ToolResult:
        """Update delivery timeline."""
        order_id = order_id.strip()
        if not order_id and self.world.active_order:
            order_id = self.world.active_order.id

        if self.world.active_order:
            self.world.active_order.action_applied = True

        return ToolResult(True,
            f"Timeline updated for {order_id}. "
            f"New ETA: {new_eta or 'recalculated based on current status'}."
        )

    # ------------------------------------------------------------------
    # Tool: verify_pricing
    # ------------------------------------------------------------------
    def verify_pricing(self, order_id: str = "") -> ToolResult:
        """Verify pricing against contract."""
        order_id = order_id.strip()
        if not order_id:
            return ToolResult(False, "Please specify an order ID.")

        if self.world.active_order:
            self.world.active_order.action_applied = True

        # SteelWorks dispute case
        if order_id in ("PO-8812", "T-009"):
            return ToolResult(True,
                "Pricing verification for PO-8812:\n"
                "  Contract rate: EUR 38/unit\n"
                "  Invoiced: EUR 47.20/unit\n"
                "  Quantity: 1000 units\n"
                "  Discrepancy: EUR 9,200 (24.2% above contract)\n"
                "  Threshold: >5% → MUST escalate to procurement."
            )

        return ToolResult(True, f"Pricing verified for {order_id}. No discrepancies found.")

    # ------------------------------------------------------------------
    # Tool: compile_records
    # ------------------------------------------------------------------
    def compile_records(self, period: str = "") -> ToolResult:
        """Compile import records for audit."""
        if self.world.active_order:
            self.world.active_order.action_applied = True

        return ToolResult(True,
            f"Import records compiled for period: {period or 'past 30 days'}.\n"
            "Records include: 47 import shipments, 12 customs clearances, "
            "3 rejected shipments, all supplier invoices.\n"
            "Ready for submission."
        )

    # ------------------------------------------------------------------
    # Tool: acknowledge_alert
    # ------------------------------------------------------------------
    def acknowledge_alert(self, alert_id: str = "") -> ToolResult:
        """Acknowledge a system alert."""
        if self.world.active_order:
            self.world.active_order.action_applied = True

        order = self.world.active_order
        if order and order.category == OrderCategory.SYSTEM_ALERT:
            self.world.resolve_order(order)
            self.agent.resolved_count += 1
            # System alerts don't affect quality score (like spam in Support Desk)
            return ToolResult(True,
                f"Alert acknowledged and closed."
            )

        return ToolResult(True, "Alert acknowledged.")

    # ------------------------------------------------------------------
    # Tool: notify_client
    # ------------------------------------------------------------------
    def notify_client(self, template: str = "", **kwargs) -> ToolResult:
        """Send a notification using a template."""
        template = template.strip()

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

        if self.world.active_order:
            self.world.active_order.notification_sent = True

        return ToolResult(True,
            f"Notification sent using template '{tmpl.name}'."
        )

    # ------------------------------------------------------------------
    # Tool: escalate
    # ------------------------------------------------------------------
    def escalate(self, department: str = "", reason: str = "") -> ToolResult:
        """Escalate to a department."""
        department = department.strip().lower()

        if not department:
            return ToolResult(False,
                "Please specify a department: procurement, finance, logistics, "
                "engineering, compliance"
            )

        valid_depts = {"procurement", "finance", "logistics", "engineering", "compliance"}
        if department not in valid_depts:
            return ToolResult(False,
                f"Unknown department '{department}'. "
                f"Available: {', '.join(sorted(valid_depts))}"
            )

        order = self.world.active_order
        if not order:
            return ToolResult(False, "No active order to escalate.")

        # Check if this is a boss order needing briefing
        if order.requires_briefing and not order.briefing_prepared:
            bounce_key = f"briefing_bounce_{order.id}"
            bounce_count = sum(1 for n in self.agent.notes if n == bounce_key)
            self.agent.notes.append(bounce_key)

            if bounce_count == 0:
                btype = "launch readiness briefing" if order.briefing_type == "launch" else "compliance package"
                return ToolResult(False,
                    f"Cannot process — a {btype} must be prepared first. "
                    f"Resolve prerequisite orders and then use "
                    f"{'prepare_launch_briefing' if order.briefing_type == 'launch' else 'prepare_compliance_package'}(). "
                    f"Check the knowledge base for the protocol."
                )
            else:
                self.agent.operations_tokens -= 1
                self.agent.notes.append(f"Attempted action on {order.id} without briefing (REJECTED, token lost)")
                return ToolResult(False,
                    f"Rejected AGAIN — no briefing prepared. "
                    f"Lost 1 operations token. Remaining: {self.agent.operations_tokens}. "
                    f"You MUST prepare the briefing first."
                )

        # Check if escalation is correct
        if order.requires_escalation:
            if department == order.requires_escalation:
                order.escalated_to = department
                order.status = OrderStatus.WAITING
                self.agent.notes.append(f"Escalated {order.id} to {department} (correct)")
                return ToolResult(True,
                    f"Order {order.id} escalated to {department}. "
                    "They will review and respond."
                )
            else:
                self.agent.operations_tokens -= 1
                self.agent.notes.append(
                    f"Escalated {order.id} to {department} "
                    f"(WRONG — should be {order.requires_escalation})"
                )
                return ToolResult(False,
                    f"The {department} team sent it back — wrong department. "
                    f"Lost 1 operations token. Remaining: {self.agent.operations_tokens}."
                )
        else:
            # Unnecessary escalation
            self.agent.operations_tokens -= 1
            self.agent.notes.append(
                f"Escalated {order.id} to {department} (UNNECESSARY)"
            )
            return ToolResult(False,
                f"The {department} team sent it back — you can handle this yourself. "
                f"Lost 1 operations token. Remaining: {self.agent.operations_tokens}."
            )

    # ------------------------------------------------------------------
    # Tool: prepare_launch_briefing (Boss A)
    # ------------------------------------------------------------------
    def prepare_launch_briefing(self) -> ToolResult:
        """Prepare the Project Aurora launch readiness briefing."""
        order = self.world.get_order("T-001")
        if not order:
            return ToolResult(False, "Project Aurora order (T-001) not found.")

        if order.briefing_prepared:
            return ToolResult(True, "Launch briefing is already prepared.")

        ready, missing = self.world.check_briefing_ready("T-001")
        if not ready:
            missing_details = []
            for mid in missing:
                mo = self.world.get_order(mid)
                if mo:
                    missing_details.append(f"{mid} ({mo.subject[:40]})")
                else:
                    missing_details.append(f"{mid} (not yet available)")
            return ToolResult(False,
                "Cannot prepare launch briefing yet. "
                f"Missing evidence from: {', '.join(missing_details)}. "
                "Resolve these orders first."
            )

        order.briefing_prepared = True
        self.agent.notes.append("Prepared Project Aurora launch briefing")

        return ToolResult(True,
            "Launch readiness briefing prepared for Project Aurora!\n"
            "Compiled evidence:\n"
            "  - Customs: TechParts microcontrollers cleared (T-005)\n"
            "  - Quality: Replacement coating secured from alternative supplier (T-008)\n"
            "  - Engineering: MechPro v2.1 spec confirmed with new coating specs (T-012)\n\n"
            "You can now authorize the launch with authorize_launch(order_id='T-001')."
        )

    # ------------------------------------------------------------------
    # Tool: authorize_launch (Boss A)
    # ------------------------------------------------------------------
    def authorize_launch(self, order_id: str = "") -> ToolResult:
        """Authorize the Project Aurora launch."""
        order = self.world.get_order("T-001")
        if not order:
            return ToolResult(False, "Project Aurora order (T-001) not found.")

        if not order.briefing_prepared:
            bounce_key = "launch_auth_bounce"
            bounce_count = sum(1 for n in self.agent.notes if n == bounce_key)
            self.agent.notes.append(bounce_key)

            if bounce_count == 0:
                return ToolResult(False,
                    "Cannot authorize launch — launch readiness briefing not prepared. "
                    "Use prepare_launch_briefing() first. "
                    "All prerequisite orders must be resolved before preparing the briefing."
                )
            else:
                self.agent.operations_tokens -= 1
                return ToolResult(False,
                    "Launch authorization REJECTED again. No briefing prepared. "
                    f"Lost 1 operations token. Remaining: {self.agent.operations_tokens}."
                )

        order.action_applied = True
        return ToolResult(True,
            "Project Aurora AUTHORIZED! Launch sequence initiated.\n"
            "All three critical components confirmed and briefing reviewed.\n"
            "CEO Hans Richter has been notified. Notify stakeholders and close the order."
        )

    # ------------------------------------------------------------------
    # Tool: prepare_compliance_package (Boss B)
    # ------------------------------------------------------------------
    def prepare_compliance_package(self) -> ToolResult:
        """Prepare the STA regulatory compliance package."""
        order = self.world.get_order("T-020")
        if not order:
            return ToolResult(False, "Regulatory order (T-020) not found.")

        if order.briefing_prepared:
            return ToolResult(True, "Compliance package is already prepared.")

        ready, missing = self.world.check_briefing_ready("T-020")
        if not ready:
            missing_details = []
            for mid in missing:
                mo = self.world.get_order(mid)
                if mo:
                    missing_details.append(f"{mid} ({mo.subject[:40]})")
                else:
                    missing_details.append(f"{mid} (not yet available)")
            return ToolResult(False,
                "Cannot prepare compliance package yet. "
                f"Missing evidence from: {', '.join(missing_details)}. "
                "Resolve these orders first."
            )

        order.briefing_prepared = True
        self.agent.notes.append("Prepared STA compliance package")

        return ToolResult(True,
            "Compliance package prepared for STA review!\n"
            "Compiled evidence:\n"
            "  - Customs handling: Meridian Foods case resolved properly (T-006)\n"
            "  - Procurement audit: SteelWorks dispute escalated correctly (T-009)\n"
            "  - Import records: 30-day audit compiled (T-016)\n\n"
            "You can now submit with submit_compliance(order_id='T-020')."
        )

    # ------------------------------------------------------------------
    # Tool: submit_compliance (Boss B)
    # ------------------------------------------------------------------
    def submit_compliance(self, order_id: str = "") -> ToolResult:
        """Submit compliance package to STA."""
        order = self.world.get_order("T-020")
        if not order:
            return ToolResult(False, "Regulatory order (T-020) not found.")

        if not order.briefing_prepared:
            bounce_key = "compliance_submit_bounce"
            bounce_count = sum(1 for n in self.agent.notes if n == bounce_key)
            self.agent.notes.append(bounce_key)

            if bounce_count == 0:
                return ToolResult(False,
                    "Cannot submit — compliance package not prepared. "
                    "Use prepare_compliance_package() first. "
                    "All prerequisite orders must be resolved before preparing."
                )
            else:
                self.agent.operations_tokens -= 1
                return ToolResult(False,
                    "Submission REJECTED again. No compliance package prepared. "
                    f"Lost 1 operations token. Remaining: {self.agent.operations_tokens}."
                )

        order.action_applied = True
        return ToolResult(True,
            "Compliance package SUBMITTED to Swiss Trade Authority!\n"
            "Dr. Muller has confirmed receipt. Import license review cleared.\n"
            "Notify stakeholders and close the order."
        )

    # ------------------------------------------------------------------
    # Tool: close_order
    # ------------------------------------------------------------------
    def close_order(self, order_id: str = "") -> ToolResult:
        """Mark an order as resolved and score it."""
        order_id = order_id.strip()

        if not order_id and self.world.active_order:
            order_id = self.world.active_order.id
        if not order_id:
            return ToolResult(False, "No order specified and no active order.")

        order = self.world.get_order(order_id)
        if not order:
            return ToolResult(False, f"Order {order_id} not found.")
        if order.status == OrderStatus.RESOLVED:
            return ToolResult(False, f"Order {order_id} is already resolved.")

        # --- Score the resolution ---
        score = order.score_potential
        feedback = []

        if order.category == OrderCategory.SYSTEM_ALERT:
            if order.action_applied:
                feedback.append("System alert handled correctly.")
            else:
                score -= 1
                feedback.append("Alert should be acknowledged before closing.")

        else:
            # Must have notified client (except system alerts)
            if not order.notification_sent and order.correct_template:
                score -= 2
                feedback.append("No client notification sent! (-2)")

            # Should have looked up KB if required
            if order.requires_lookup and not order.lookup_done:
                score += order.penalty_no_lookup
                feedback.append(f"Resolved without looking up info first ({order.penalty_no_lookup})")

            # Should have applied the right action
            if order.requires_action and not order.action_applied:
                score += order.penalty_wrong_action
                feedback.append(
                    f"Required action '{order.requires_action}' not applied ({order.penalty_wrong_action})"
                )

            # Should have filed a claim if required (quality orders)
            if order.requires_claim and not order.claim_filed:
                score -= 2
                feedback.append("Quality issue requires filing a claim against supplier (-2)")

            # Should have escalated if required
            if order.requires_escalation and order.escalated_to != order.requires_escalation:
                score += order.penalty_wrong_escalation
                feedback.append(
                    f"Should have been escalated to {order.requires_escalation} ({order.penalty_wrong_escalation})"
                )

        score = max(0, min(5, score))

        # Update agent state
        max_score = min(5, order.score_potential)
        self.world.resolve_order(order)
        self.agent.resolved_count += 1
        self.agent.score_total += score
        self.agent.score_max_total += max_score
        self.agent.score_interactions += 1

        # Unlock chain orders
        if order.chain_id:
            unlocked = self.world.unlock_chain(order.chain_id, 0)
            if unlocked:
                feedback.append(f"Follow-up order {unlocked.id} will appear soon.")

        entity = self.world.get_entity(order.entity_id)
        entity_name = entity.name if entity else "Unknown"

        quality = "Excellent" if score >= 4 else "Good" if score >= 3 else "Needs improvement" if score >= 2 else "Poor"

        return ToolResult(True,
            f"Order {order_id} fulfilled! Score: {score}/5 ({quality})\n"
            + ("\n".join(f"  - {f}" for f in feedback) if feedback else "  Perfect handling!")
            + f"\n\nFulfilled: {self.agent.resolved_count}/{self.agent.WIN_RESOLVED} | "
            f"Quality: {self.agent.quality_score:.0f}%"
        )

    # ------------------------------------------------------------------
    # Tool: check_stats
    # ------------------------------------------------------------------
    def check_stats(self) -> ToolResult:
        """Check current performance stats (free action)."""
        return ToolResult(True, self.agent.status_text())

    # ------------------------------------------------------------------
    # Tool: take_break
    # ------------------------------------------------------------------
    def take_break(self) -> ToolResult:
        """Take a break to recover one operations token. Costs 5 turns."""
        if self.agent.operations_tokens >= self.agent.MAX_TOKENS:
            return ToolResult(False, "Already at full tokens. No break needed.")
        self.agent.operations_tokens += 1
        return ToolResult(True,
            f"Break taken. Recovered 1 operations token. "
            f"Tokens: {self.agent.operations_tokens}/{self.agent.MAX_TOKENS}"
        )

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------
    def execute(self, tool_name: str, args: dict) -> ToolResult:
        tool_map = {
            "check_orders": lambda: self.check_orders(),
            "read_order": lambda: self.read_order(args.get("order_id", "")),
            "lookup_kb": lambda: self.lookup_kb(args.get("query", "")),
            "check_inventory": lambda: self.check_inventory(args.get("sku", "")),
            "lookup_shipment": lambda: self.lookup_shipment(args.get("shipment_id", "")),
            "lookup_contract": lambda: self.lookup_contract(args.get("supplier", "")),
            "check_documentation": lambda: self.check_documentation(args.get("shipment_id", "")),
            "check_alternatives": lambda: self.check_alternatives(),
            "place_order": lambda: self.place_order(
                args.get("supplier", ""), args.get("sku", ""),
                args.get("quantity", ""), args.get("expedited", "")
            ),
            "reject_shipment": lambda: self.reject_shipment(
                args.get("shipment_id", ""), args.get("reason", "")
            ),
            "file_claim": lambda: self.file_claim(
                args.get("supplier", ""), args.get("amount", "")
            ),
            "submit_documents": lambda: self.submit_documents(
                args.get("shipment_id", ""), args.get("doc_type", "")
            ),
            "update_timeline": lambda: self.update_timeline(
                args.get("order_id", ""), args.get("new_eta", "")
            ),
            "verify_pricing": lambda: self.verify_pricing(args.get("order_id", "")),
            "compile_records": lambda: self.compile_records(args.get("period", "")),
            "acknowledge_alert": lambda: self.acknowledge_alert(args.get("alert_id", "")),
            "notify_client": lambda: self.notify_client(args.get("template", "")),
            "escalate": lambda: self.escalate(
                args.get("department", ""), args.get("reason", "")
            ),
            "prepare_launch_briefing": lambda: self.prepare_launch_briefing(),
            "authorize_launch": lambda: self.authorize_launch(args.get("order_id", "")),
            "prepare_compliance_package": lambda: self.prepare_compliance_package(),
            "submit_compliance": lambda: self.submit_compliance(args.get("order_id", "")),
            "close_order": lambda: self.close_order(args.get("order_id", "")),
            "check_stats": lambda: self.check_stats(),
            "take_break": lambda: self.take_break(),
        }

        fn = tool_map.get(tool_name.lower().strip())
        if fn is None:
            return ToolResult(False,
                f"Unknown tool '{tool_name}'. Available: {', '.join(tool_map.keys())}"
            )

        return fn()
