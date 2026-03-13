# Exercise Concept: The Supply Line

## 1. Theme & Setting

**Pitch:** You are the Operations Coordinator at NovaTrade Logistics, managing a stream of supply chain disruptions — delayed shipments, quality failures, customs holds, and supplier disputes — while racing to coordinate a critical product launch that depends on resolving three separate crises first.

**Role:** Operations Coordinator responsible for order fulfillment, supplier management, and logistics coordination.

**Why it matters:** Over 60% of the audience works in industries with complex supply chains — pharma (Novartis, Roche), food (Nestlé), finance (UBS, Swiss Re), industrial (Samsung), retail, defense (RUAG), energy (Vattenfall). Even those in consulting (Deloitte, Bain, EY, Accenture) regularly advise on supply chain optimization. The exercise makes the abstract concept of "agentic AI" concrete through a domain every manager touches.

---

## 2. Win Condition

- **Fulfill 15+ orders** (out of ~22 total)
- **Maintain ≥ 80% fulfillment quality score** (weighted average of per-order scores)
- **Keep ≥ 1 operations token** (start with 3)
- **Within 100 turns**

All three conditions must be met simultaneously.

---

## 3. Task Types

### 3.1 System Alert (🔔 `system_alert`) — Trivial
- **Example:** "AUTOMATED: Warehouse B3 temperature sensor reading normal. Daily check passed."
- **Steps:** `acknowledge_alert` → `close_order`
- **Score potential:** 1
- **Count:** 3 initial
- **Trap?** No — but wastes turns if agent over-investigates

### 3.2 Standard Reorder (📦 `reorder`) — Easy
- **Example:** "SKU-4421 (industrial bearings) inventory at 12 units, reorder point is 50. Supplier: SteelWorks GmbH. Please reorder."
- **Steps:** `check_inventory` → `lookup_kb("reorder procedures")` → `place_order(supplier, sku, quantity)` → `notify_client(template="reorder_confirmation")` → `close_order`
- **Score potential:** 3
- **Count:** 4 initial + 2 chain
- **Trap?** No

### 3.3 Shipping Delay (🚚 `delay`) — Medium
- **Example:** "Client Meridian Foods reports their shipment #SH-2287 hasn't arrived. Original ETA was 3 days ago. Carrier: FastFreight."
- **Steps:** `lookup_shipment(id)` → `check_alternatives` → `update_timeline(order_id, new_eta)` → `notify_client(template="delay_notification")` → `close_order`
- **Score potential:** 4
- **Count:** 3 initial + 1 late (turn 25)
- **Trap?** No

### 3.4 Quality Rejection (⚠️ `quality`) — Medium-Hard
- **Example:** "QC inspection failed for shipment #SH-3301 from ChemPure AG. Contamination found in batch B-7744. 200 units affected. Client: Helvetica Pharma."
- **Steps:** `lookup_shipment(id)` → `reject_shipment(id, reason)` → `file_claim(supplier, amount)` → `place_order(alt_supplier, sku, quantity)` → `notify_client(template="quality_issue")` → `close_order`
- **Score potential:** 5
- **Count:** 2 initial (T-008 is boss prerequisite)
- **Trap?** No

### 3.5 Customs Hold (🛃 `customs`) — Medium-Hard
- **Example:** "Shipment #SH-1190 from TechParts Shenzhen held at Zurich customs. Missing Form 47-B (certificate of origin). Client: RUAG Electronics. Deadline: 5 days."
- **Steps:** `lookup_shipment(id)` → `check_documentation(shipment_id)` → `submit_documents(shipment_id, doc_type)` → `notify_client(template="customs_update")` → `close_order`
- **Score potential:** 4
- **Count:** 2 initial (T-005 is boss prerequisite)
- **Trap?** No

### 3.6 Rush Order (⚡ `rush`) — Trap
- **Example:** "URGENT from client Apex Manufacturing: Need 500 units of SKU-7890 by Friday. Regular lead time is 2 weeks. They're threatening to switch suppliers."
- **Steps:** `lookup_kb("expedited shipping")` → `check_alternatives` → `place_order(supplier, sku, quantity, expedited=True)` → `notify_client(template="rush_confirmation")` → `close_order`
- **Score potential:** 3
- **Count:** 2 initial + 1 late (turn 40)
- **Trap?** YES — looks like it needs management escalation, but KB says expedited shipping is available for orders under 1000 units. Escalating wastes a token.

### 3.7 Supplier Dispute (💰 `dispute`) — Hard
- **Example:** "Invoice from SteelWorks GmbH shows €47,200 for order #PO-8812. Contract rate is €38/unit × 1000 = €38,000. Overcharge of €9,200. Payment due in 3 days."
- **Steps:** `lookup_contract(supplier)` → `verify_pricing(order_id)` → `escalate(department="procurement", reason="pricing_discrepancy")` → `close_order`
- **Score potential:** 5
- **Count:** 1 initial + 1 chain
- **Trap?** No — this one genuinely requires escalation

### 3.8 Boss A: Product Launch Coordination (🚀 `launch`) — Boss Fight
- **Example:** "CRITICAL — Project Aurora launch in 7 days. CEO Hans Richter has staked company reputation on this. Three critical components needed: (1) TechParts microcontrollers — STUCK AT CUSTOMS (see order O-1190), (2) ChemPure specialty coating — FAILED QC (see order O-3301), (3) Engineering spec v2.1 — waiting on supplier confirmation from MechPro (see order O-5501). Launch CANNOT proceed until all three are secured. Prepare launch readiness briefing and get authorization."
- **Steps:** resolve T-005 (customs) → resolve T-008 (quality) → resolve T-012 (spec confirmation, chain task) → `prepare_launch_briefing` → `authorize_launch(order_id)` → `close_order`
- **Score potential:** 8
- **Count:** 1 (always T-001, highest priority)
- **Prerequisites:** T-005, T-008, T-012

### 3.9 Boss B: Regulatory Shutdown Threat (⚖️ `regulatory`) — Boss Fight
- **Example:** "URGENT — Swiss Trade Authority (STA) has flagged NovaTrade for import compliance review after customs irregularities. Inspector Dr. Müller demands a comprehensive compliance package within the review period or NovaTrade's import license will be SUSPENDED. Package must include: (1) proof of proper customs handling (see order O-1190b for the Meridian customs case), (2) supplier procurement audit trail (see the SteelWorks dispute), (3) compiled import records for the past 30 days (pending internal audit). Prepare compliance package and submit to STA."
- **Steps:** resolve T-006 (customs for Meridian) → resolve T-009 (supplier dispute) → resolve T-016 (compliance audit, chain task from T-006) → `prepare_compliance_package` → `submit_compliance(order_id)` → `close_order`
- **Score potential:** 7
- **Count:** 1 (T-020, HIGH priority — appears second after Aurora)
- **Prerequisites:** T-006, T-009, T-016

---

## 4. The Boss Fights

### 4A. Project Aurora (🚀 launch) — "The Frost Wyrm"

### What it is
The company's new product launch (Project Aurora) depends on three supply chain crises being resolved first. It's the highest-priority order in the queue, but attempting to authorize launch without all components secured gets rejected.

### Prerequisites
1. **T-005** — Customs clearance for TechParts microcontrollers (customs hold)
2. **T-008** — Quality replacement for ChemPure specialty coating (quality rejection)
3. **T-012** — Engineering spec confirmation from MechPro (chain task, unlocked after T-008 resolves — MechPro needs to know the replacement coating specs)

### The Preparation Step
`prepare_launch_briefing` — compiles evidence from all three resolved orders into a launch readiness report. Returns detailed status of each component. Only succeeds when all prerequisites are resolved.

### Why the LLM Fails
1. T-001 (Aurora) is CRITICAL priority → LLM opens it first
2. LLM reads "prepare launch readiness briefing" → tries `prepare_launch_briefing` immediately
3. Gets bounced: "Cannot prepare briefing — missing: customs clearance (O-1190), QC replacement (O-3301), spec confirmation (O-5501)"
4. LLM retries or tries `authorize_launch` directly → bounced again, first bounce free
5. Subsequent unauthorized launch attempts cost operations tokens
6. LLM can't figure out it needs to *leave* the highest-priority order and go handle three other orders first
7. Even if it does, T-012 doesn't exist yet (chain task) — it only appears after T-008 is resolved

### What the Deterministic Planner Does
```python
def _pick_next_order(world):
    for order in world.queue:
        if order.requires_briefing and not order.briefing_prepared:
            ready, missing = world.check_briefing_ready(order.id)
            if not ready:
                continue  # skip — prerequisites not met
        return order
    return world.queue[0] if world.queue else None
```

### 4B. Regulatory Shutdown (⚖️ regulatory) — "The Shadow Beast"

### What it is
The Swiss Trade Authority is threatening to suspend NovaTrade's import license. The agent must compile a compliance package proving proper customs handling, procurement controls, and complete import records. Like Aurora, it appears as a high-priority order but can't be resolved until its own set of prerequisites are met.

### Prerequisites
1. **T-006** — Customs clearance for Meridian Foods shipment (proves proper customs handling)
2. **T-009** — SteelWorks pricing dispute resolved (proves procurement controls)
3. **T-016** — Compliance audit records compiled (chain task, unlocked after T-006 resolves)

### The Preparation Step
`prepare_compliance_package` — compiles evidence from resolved customs, procurement, and audit records into a regulatory submission. Only succeeds when all three prerequisites are resolved.

### Why the LLM Fails (Same Pattern, Different Prereqs)
1. T-020 is HIGH priority → LLM opens it early (right after or instead of Aurora)
2. LLM tries `prepare_compliance_package` or `submit_compliance` immediately → bounced
3. Now the LLM has TWO blocked boss tasks and can't figure out which regular orders to prioritize
4. The two bosses have **different prerequisite sets** — the LLM must track two independent dependency chains
5. T-016 is a chain task that doesn't exist yet — it only appears after T-006 is resolved
6. This is the equivalent of needing both the Sunblade AND the Moonstone Lantern

### What the Deterministic Planner Handles
The same `_pick_next_order` function handles both bosses — it skips any order with `requires_briefing=True` whose prerequisites aren't met. The planner naturally processes T-005, T-006, T-008, T-009 (all non-boss orders), which unlocks T-012 and T-016 (chain tasks), which then unblocks both bosses.

---

## 5. Chain Tasks

### Chain 1: T-008 (Quality) → T-012 (Spec Confirmation)
- **Trigger:** Resolving T-008 (replacing ChemPure coating)
- **Unlocks:** T-012 — "MechPro Engineering needs coating specs for the replacement batch to finalize v2.1 spec sheet. Please confirm replacement supplier and batch number."
- **Connection to boss:** T-012 is a boss prerequisite
- **created_turn:** -1 (appears when T-008 resolves)

### Chain 2: T-003 (Reorder bearings) → T-015 (Bulk Discount Offer)
- **Trigger:** Resolving T-003 (SteelWorks reorder)
- **Unlocks:** T-015 — "SteelWorks is offering a 15% bulk discount on next quarter's order if committed by end of week. Need procurement approval."
- **Connection to boss:** None (side quest)
- **created_turn:** -1

### Chain 3: T-006 (Customs docs) → T-016 (Compliance Audit)
- **Trigger:** Resolving T-006 (second customs hold)
- **Unlocks:** T-016 — "Swiss customs authority flagged NovaTrade for audit. Need to compile all import documentation from past 30 days."
- **Connection to boss:** T-016 is a PREREQUISITE for Boss B (Regulatory Shutdown)
- **created_turn:** -1

### Chain 4: T-009 (Supplier dispute) → T-017 (Contract Renewal)
- **Trigger:** Resolving T-009 (SteelWorks dispute)
- **Unlocks:** T-017 — "SteelWorks contract expires next month. Given the recent pricing dispute, renegotiate terms or find alternative supplier."
- **Connection to boss:** None (medium difficulty side quest)
- **created_turn:** -1

---

## 6. Knowledge Base (14 articles)

| ID | Title | Keywords | Summary | Action Hint |
|---|---|---|---|---|
| KB-001 | Reorder Procedures | reorder, inventory, threshold, SKU | Standard reorder process: verify inventory, select approved supplier, place order, confirm with client | Use `place_order` after checking inventory |
| KB-002 | Expedited Shipping Policy | rush, urgent, expedited, fast | Orders under 1000 units can use expedited shipping (+30% cost). No management approval needed. Over 1000 units requires VP approval. | Use `place_order` with `expedited=True` — do NOT escalate for small rush orders |
| KB-003 | Quality Control Rejection Process | QC, quality, rejection, contamination | Reject shipment, file supplier claim, reorder from alternative supplier. Claims must include batch number and inspection report. | `reject_shipment` → `file_claim` → `place_order` with alt supplier |
| KB-004 | Customs Documentation Guide | customs, hold, import, Form 47-B, certificate | Required docs: certificate of origin, commercial invoice, packing list. Submit via `submit_documents`. Processing time: 2-3 days. | `check_documentation` → `submit_documents` |
| KB-005 | Supplier Escalation Policy | dispute, pricing, overcharge, contract | Pricing discrepancies >5% must be escalated to procurement. Under 5% can be resolved directly with supplier. | Verify discrepancy amount before escalating |
| KB-006 | Project Aurora Launch Protocol | aurora, launch, product, briefing, authorization | Launch requires: (1) all three critical components confirmed, (2) launch readiness briefing prepared, (3) authorization from operations. Briefing must compile evidence from each component resolution. | `prepare_launch_briefing` only after all components secured |
| KB-007 | Approved Supplier Directory | supplier, approved, blacklist, alternative | Lists approved suppliers by category. BLACKLISTED: QuickShip Ltd (quality violations), BargainParts Co (fraud). Using blacklisted supplier = immediate operations token loss. | Always verify supplier against approved list |
| KB-008 | Client Communication Templates | template, notification, reply, update | Lists all available templates: reorder_confirmation, delay_notification, quality_issue, customs_update, rush_confirmation, launch_status, dispute_resolution, general_update | Use correct template per situation |
| KB-009 | Budget Authority Matrix | budget, approval, authorization, limit | Coordinators can approve orders up to €50,000. Above €50,000 requires escalation to Finance. Expedited shipping surcharges don't count toward the limit. | Check order value before placing |
| KB-010 | Shipping Delay Resolution | delay, carrier, alternative, reroute | Check carrier status first. If delay >5 days, check alternative carriers. If delay >10 days, escalate to logistics management. | `lookup_shipment` → `check_alternatives` → `update_timeline` |
| KB-011 | Inventory Management Alerts | alert, system, automated, sensor | System alerts (temperature, stock level daily checks) are informational only. Acknowledge and close. Do NOT investigate further. | `acknowledge_alert` → `close_order` |
| KB-012 | Operations Token Policy | token, penalty, violation, break | Tokens lost for: blacklisted supplier, unauthorized launch attempt, wrong escalation. Recover via `take_break` (costs 5 turns). | Avoid violations; take break if at 1 token |
| KB-013 | MechPro Engineering Coordination | mechpro, engineering, specs, v2.1 | MechPro requires final coating specs before releasing v2.1 engineering spec. Contact only after replacement coating supplier is confirmed. | Only appears relevant after T-008 resolved |
| KB-014 | Compliance and Audit Procedures | audit, compliance, customs, documentation | Compile import records using `compile_records`. Submit within 48 hours of audit notification. | `compile_records` → `submit_documents` |
| KB-015 | STA Regulatory Review Protocol | STA, regulatory, shutdown, compliance package, import license | Swiss Trade Authority reviews require: (1) proof of proper customs handling, (2) supplier procurement audit trail, (3) compiled import records. All three must be included in compliance package. Package must be prepared via `prepare_compliance_package` before `submit_compliance`. | `prepare_compliance_package` only after all three evidence items secured |

---

## 7. Templates (8)

| Name | Category | Template Text | When to Use |
|---|---|---|---|
| `reorder_confirmation` | reorder | "Your reorder for {sku} has been placed with {supplier}. Expected delivery: {eta}. Order reference: {order_ref}." | After placing standard reorder |
| `delay_notification` | delay | "We're aware of the delay on shipment {shipment_id}. New estimated arrival: {new_eta}. We apologize for the inconvenience." | After updating timeline for delayed shipment |
| `quality_issue` | quality | "A quality issue was detected in your recent shipment. We've initiated a replacement order with {alt_supplier}. Expected delivery: {eta}." | After quality rejection and reorder |
| `customs_update` | customs | "Your shipment {shipment_id} is being processed through customs. Required documentation has been submitted. Expected clearance: {eta}." | After submitting customs documents |
| `rush_confirmation` | rush | "Your expedited order has been placed. {quantity} units of {sku} via express shipping. Delivery by {eta}." | After placing rush order with expedited flag |
| `launch_status` | launch | "Project Aurora update: All critical components secured. Launch readiness briefing prepared. Authorization pending." | After preparing launch briefing |
| `dispute_resolution` | dispute | "The pricing discrepancy on order {order_id} has been escalated to our procurement team. Expected resolution: {eta}." | After escalating supplier dispute |
| `general_update` | general | "Update on your order {order_id}: {status_message}" | Fallback for any other communication |
| `compliance_status` | regulatory | "NovaTrade compliance update: All required documentation compiled and submitted to Swiss Trade Authority. Reference: {ref_id}." | After preparing compliance package |

---

## 8. Characters/Entities

| Name | Role/Company | Tier | Key Attributes |
|---|---|---|---|
| **Hans Richter** | CEO, NovaTrade | Internal VIP | Staked reputation on Aurora launch. Connected to boss fight. |
| **Meridian Foods** | Client — food manufacturer | Enterprise | Multiple active orders, sensitive to delays |
| **Helvetica Pharma** | Client — pharmaceutical | Enterprise | Quality-critical, regulatory requirements |
| **Apex Manufacturing** | Client — industrial | Standard | Sends rush orders, threatens to switch suppliers |
| **RUAG Electronics** | Client — defense/aerospace | Enterprise | Customs-heavy orders, strict documentation |
| **SteelWorks GmbH** | Supplier — industrial parts | Approved | Reliable but has pricing disputes |
| **ChemPure AG** | Supplier — chemical coatings | Approved | Quality issues with recent batches |
| **TechParts Shenzhen** | Supplier — electronics | Approved | International, customs-heavy |
| **MechPro Engineering** | Supplier — engineering specs | Approved | Depends on coating specs for v2.1 |
| **QuickShip Ltd** | Supplier — logistics | BLACKLISTED | Quality violations — ordering costs a token |
| **Dr. Müller** | Inspector, Swiss Trade Authority | Regulator | Demands compliance package. Connected to boss fight B. |
| **SpamBot3000** | Automated system | System | Generates warehouse sensor alerts (spam) |

---

## 9. Penalty Token Scenarios

### Costs a token:
- Ordering from blacklisted supplier (QuickShip Ltd, BargainParts Co)
- Attempting `authorize_launch` without completed briefing (after first free bounce)
- Attempting `submit_compliance` without completed compliance package (after first free bounce)
- Escalating a rush order that doesn't need escalation (under 1000 units)
- Approving an order >€50,000 without escalating to Finance
- Shipping without required quality check on quality-flagged orders

### Free on first attempt:
- First `authorize_launch` without briefing → helpful error message explaining what's missing
- First `prepare_launch_briefing` with missing prerequisites → lists what's still needed
- First `submit_compliance` without package → helpful error message
- First `prepare_compliance_package` with missing prerequisites → lists what's still needed

### Deadlock Test:
- ✅ Rush orders: KB-002 clearly says <1000 units = use expedited, no escalation needed
- ✅ Quality issues: reject → file_claim → reorder from alternative (KB-003 + KB-007 list alternatives)
- ✅ Customs: documentation guide (KB-004) has clear steps
- ✅ Boss fight: prerequisites are all achievable independently, T-012 chain unlocks after T-008
- ✅ Budget: all standard orders are under €50,000; only the bulk discount chain (T-015) might exceed, and it correctly requires escalation
- ✅ Boss B prerequisites achievable independently: T-006 and T-009 have no prerequisites, T-016 chain unlocks after T-006
- ✅ No circular dependencies: Boss A: T-001 → {T-005, T-008} → T-012. Boss B: T-020 → {T-006, T-009} → T-016. No overlap between boss prerequisite sets.
- ✅ No shared prerequisites between bosses — they can be resolved in any order

---

## 10. Mapping Table

| Hero Quest | Support Desk | The Supply Line |
|---|---|---|
| Grid map (7×7) | Ticket queue | Order queue |
| BFS pathfinding | Dependency resolution (_pick_next_ticket) | Dependency resolution (_pick_next_order) |
| Items to collect | Evidence to gather | Components to secure |
| Frost Wyrm (dragon 1) | VIP Elena | Project Aurora launch (Boss A) |
| Shadow Beast (dragon 2) | — (only 1 boss) | Regulatory Shutdown (Boss B) |
| Sunblade (weapon 1) | Account briefing | Launch readiness briefing (prepare_launch_briefing) |
| Moonstone Lantern (weapon 2) | — | Compliance package (prepare_compliance_package) |
| Health points (3) | Escalation tokens (3) | Operations tokens (3) |
| Gold / score | CSAT score | Fulfillment quality score |
| NPCs (innkeeper, merchant) | Customers (Elena, David) | Clients (Meridian, Helvetica, Apex) |
| Spam (empty cells) | Spam tickets | System alerts |
| Treasure chests | High-CSAT tickets | Bonus orders (chain tasks) |
| Forest Witch (quest chain) | Chain tickets | Chain orders (T-008 → T-012) |
| look() / talk() | check_queue / read_ticket | check_orders / read_order |
| pick_up() / fight() | apply_action / escalate | place_order / authorize_launch |
| status() | check_stats | check_stats |
| take_break() | take_break() | take_break() |

---

## Task List (23 total)

### Initial Orders (13)
| ID | Category | Priority | Score | Client/Supplier | Boss Prereq? |
|---|---|---|---|---|---|
| T-001 | 🚀 launch | CRITICAL | 8 | Hans Richter (Aurora) | IS Boss A |
| T-002 | 📦 reorder | LOW | 3 | Internal warehouse | No |
| T-003 | 📦 reorder | MEDIUM | 3 | SteelWorks → internal | No |
| T-004 | 🔔 system_alert | LOW | 1 | SpamBot3000 | No |
| T-005 | 🛃 customs | HIGH | 4 | TechParts → RUAG | Boss A prereq |
| T-006 | 🛃 customs | MEDIUM | 4 | TechParts → Meridian | Boss B prereq |
| T-007 | 🚚 delay | HIGH | 4 | FastFreight → Meridian | No |
| T-008 | ⚠️ quality | HIGH | 5 | ChemPure → Helvetica | Boss A prereq |
| T-009 | 💰 dispute | MEDIUM | 5 | SteelWorks | Boss B prereq |
| T-010 | ⚡ rush (TRAP) | HIGH | 3 | Apex Manufacturing | No |
| T-011 | 🔔 system_alert | LOW | 1 | SpamBot3000 | No |
| T-012_placeholder | — | — | — | (chain from T-008) | Boss A prereq |
| T-020 | ⚖️ regulatory | HIGH | 7 | Dr. Müller / STA | IS Boss B |

### Chain Orders (4, created_turn=-1)
| ID | Trigger | Category | Score |
|---|---|---|---|
| T-012 | T-008 resolved | 📦 reorder (spec confirmation) | 3 |
| T-015 | T-003 resolved | 💰 dispute (bulk discount) | 3 |
| T-016 | T-006 resolved | 🛃 customs (compliance audit) | 4 |
| T-017 | T-009 resolved | 💰 dispute (contract renewal) | 4 |

### Late Orders (4, arrive at specific turns)
| ID | Turn | Category | Score |
|---|---|---|---|
| T-013 | 15 | 🚚 delay | 4 |
| T-014 | 25 | 📦 reorder | 3 |
| T-018 | 40 | ⚡ rush (TRAP) | 3 |
| T-019 | 55 | 🔔 system_alert | 1 |

### Score Budget
- Total possible: ~73 points across 23 orders
- Win requires 15 orders at 80%: need ~50 points from top 15 = feasible
- Rule-based solution targets: 18-20 orders, ~85% score, 0 tokens lost, ~75 turns

---

## Available Tools

| Tool | Args | Description |
|---|---|---|
| `check_orders` | — | View current order queue with priorities |
| `read_order` | `order_id` | Open/read a specific order's details |
| `lookup_kb` | `query` | Search knowledge base for procedures |
| `check_inventory` | `sku` | Check current inventory levels |
| `lookup_shipment` | `shipment_id` | Get shipment status and tracking |
| `lookup_contract` | `supplier` | Get contract terms and pricing |
| `check_documentation` | `shipment_id` | Check what customs docs are on file |
| `check_alternatives` | — | Find alternative suppliers/carriers |
| `place_order` | `supplier, sku, quantity, expedited` | Place a purchase order |
| `reject_shipment` | `shipment_id, reason` | Reject a failed QC shipment |
| `file_claim` | `supplier, amount` | File a claim against supplier |
| `submit_documents` | `shipment_id, doc_type` | Submit customs documentation |
| `update_timeline` | `order_id, new_eta` | Update delivery timeline |
| `verify_pricing` | `order_id` | Verify pricing against contract |
| `compile_records` | `period` | Compile import records for audit |
| `acknowledge_alert` | `alert_id` | Acknowledge system alert |
| `notify_client` | `template, **kwargs` | Send notification using template |
| `escalate` | `department, reason` | Escalate to department (procurement/finance/logistics) |
| `prepare_launch_briefing` | — | Compile launch readiness briefing (Boss A) |
| `authorize_launch` | `order_id` | Authorize product launch (Boss A) |
| `prepare_compliance_package` | — | Compile regulatory compliance package (Boss B) |
| `submit_compliance` | `order_id` | Submit compliance package to STA (Boss B) |
| `close_order` | `order_id` | Close/resolve an order |
| `check_stats` | — | View current score, tokens, progress |
| `take_break` | — | Rest to recover 1 operations token (costs 5 turns) |
