# Exercise Ideas

Pick one and write its name into `domain_choice.txt` to run the pipeline.

```bash
# Example:
echo "supply chain coordinator" > inputs/domain_choice.txt
./run_pipeline.sh
```

---

## 1. Sales Pipeline Assistant

**Domain:** `sales pipeline assistant`

An agent processing inbound leads: qualify, schedule demos, send follow-ups, update CRM. The "game" is converting as many leads as possible in a simulated week.

- **Autopilot:** enterprise domains auto-escalate to senior reps
- **Guardrails:** never discount below floor price, never commit delivery dates
- **LLM limitation:** can't check real calendar availability — needs a tool
- **Memory:** must remember prior conversations with returning leads
- **Boss fight:** enterprise deal requiring multi-step approval chain (legal review, pricing committee, VP sign-off) before closing
- **Audience fit:** sales managers, revenue ops, GTM teams

---

## 2. Supply Chain Coordinator

**Domain:** `supply chain coordinator`

An agent managing a simplified supply chain: orders come in, inventory must be checked, suppliers contacted, shipping arranged, delays communicated. The "game" is fulfilling all orders within budget and time constraints.

- **Autopilot:** standard orders with stock available get auto-fulfilled
- **Guardrails:** never order from blacklisted suppliers, never exceed budget
- **LLM limitation:** can't do inventory math — needs deterministic checks (like BFS)
- **Memory:** must track pending orders, supplier lead times, backorders
- **Boss fight:** backorder cascade requiring dependency resolution across multiple suppliers (supplier A needs part from supplier B who is delayed by supplier C)
- **Audience fit:** ops managers, procurement, logistics

---

## 3. HR Onboarding Coordinator

**Domain:** `hr onboarding coordinator`

An agent onboarding new hires: assign equipment, schedule training, send welcome emails, set up accounts, check compliance. The "game" is onboarding 10 employees with no missed steps.

- **Autopilot:** standard equipment packages per role are deterministic
- **Guardrails:** never skip compliance checks, never grant admin access without approval
- **LLM limitation:** can't actually provision accounts — needs tool calls
- **Memory:** must track which steps are done per employee
- **Boss fight:** executive hire requiring cross-department coordination (IT, legal, finance, facilities must all sign off before day-one)
- **Audience fit:** HR managers, people ops, hiring managers

---

## 4. Executive Email / Calendar Assistant

**Domain:** `executive email assistant`

An agent triaging an executive's inbox: prioritize emails, draft responses, schedule meetings, flag urgent items. The "game" is processing 40 emails with a limited action budget.

- **Autopilot:** recurring meeting acceptances, newsletter archival
- **Guardrails:** never send without approval, never share confidential info, never double-book
- **LLM limitation:** can't check real calendar conflicts — needs a tool
- **Memory:** must track email threads, prior commitments, VIP contacts
- **Boss fight:** board meeting prep requiring information synthesis from multiple email threads and calendar constraints
- **Audience fit:** every executive and their EA / chief of staff

---

## 5. Financial Report Analyst

**Domain:** `financial report analyst`

An agent processing quarterly reports: extract KPIs, compare to targets, flag anomalies, draft board summaries. The "game" is analyzing 10 department reports and producing an accurate executive summary.

- **Autopilot:** standard KPI extraction from known report templates
- **Guardrails:** never fabricate numbers, always cite the source document
- **LLM limitation:** can't do arithmetic reliably — needs a calculator tool
- **Memory:** must track cross-department dependencies and year-over-year trends
- **Boss fight:** cross-department discrepancy requiring reconciliation (marketing says revenue is X, finance says Y — agent must trace the difference through three intermediate reports)
- **Audience fit:** CFOs, FP&A, controllers, board members
