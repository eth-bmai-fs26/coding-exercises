# Exercise Review — The Supply Line

## Verdict: NEEDS_WORK

## Critical Issues (must fix before shipping)

### Issue 1: LLM autopilot stuck loop on T-015 — wastes 30+ turns and loses 2 tokens
- **What:** After correctly escalating T-015 to finance (turn 67), the autopilot's `_auto_handle` falls through to the LLM because: (a) T-015 has no `correct_template`, so the "notify then close" auto-path is skipped; (b) the "escalated + notified → close" path fails because `notification_sent` is False; (c) no fallback path for "escalated, no template needed → close". The LLM loops calling `check_orders()` 20+ times and then re-escalates to procurement (WRONG — loses 1 token at turn 70, another at turn 77). From turn 78-99 the agent is completely stuck with 1 token, calling `check_orders()` forever.
- **Where:** Solutions notebook, `_auto_handle` function — missing close path for escalation-only orders with no required template.
- **Impact:** LLM solution resolves only 13/15 orders (loses), wastes 30+ turns, loses 2 tokens. Makes the exercise unwinnable for the LLM solution.
- **Fix:** In `_auto_handle`, add a path after the escalation check: if `order.escalated_to` matches `order.requires_escalation` and there's no `correct_template` (or notification already sent), auto-close the order. Also add: if escalation is done and `correct_template` exists but notification not sent, auto-notify.

## High Priority (should fix)

### Issue 2: No close-gate guardrail — LLM closes orders without required action
- **What:** T-018 (rush order, turn 50) and T-012 (MechPro spec, turn 58) both scored 0/5 because the LLM called `close_order` without ever calling `place_order`. The guardrails only check "don't close without notification" but never check "don't close without required action".
- **Where:** Solutions notebook, guardrails section of `think_llm`, and `_auto_handle` missing `place_order` autopilot for rush/reorder.
- **Impact:** 2 orders score 0/5, dropping quality from 100% to 87.2%. Combined with the stuck loop, this makes the LLM solution lose.
- **Fix:** (a) Add guardrail: if `close_order` and `order.requires_action` and not `order.action_applied`, block and return the correct action instead. (b) Add guardrail: if `notify_client` and `order.requires_action` and not `order.action_applied`, defer to action first.

### Issue 3: Rush/reorder place_order not in LLM autopilot
- **What:** The rule-based `think_rule_based` handles `place_order` for all categories (rush, reorder, quality). The LLM autopilot `_auto_handle` handles `reject_shipment`, `submit_documents`, `compile_records`, `update_timeline` but NOT `place_order` — it defers this to the LLM, which sometimes skips it.
- **Where:** Solutions notebook, `_auto_handle` function.
- **Impact:** The LLM must correctly decide supplier/SKU/quantity/expedited for every `place_order`, which it sometimes gets wrong or skips entirely.
- **Fix:** Add `place_order` handling in autopilot for rush orders (always expedited=true) and simple reorders (use the supplier from the order message).

## Medium Priority (nice to fix)

### Issue 4: Rule-based solution uses wrong SKU/supplier for T-021
- **What:** T-021 is a reorder for lab-grade containers (SKU-9901) from ChemPure AG. The rule-based solution places an order with `supplier="PureChem Basel", sku="replacement_coating"` — wrong supplier and SKU. It still scores correctly because the engine only checks `action_applied` flag, not argument accuracy.
- **Where:** Solutions notebook, `think_rule_based`, the `place_order` fallback branch.
- **Impact:** Cosmetic only — no score impact. But confusing if a student reads the game log.
- **Fix:** Improve the `place_order` routing in `think_rule_based` to use the supplier from the order message.

## Low Priority (polish)

### Issue 5: T-020 and T-001 show "Resolved without looking up info first (-2)" but still score 5/5
- **What:** The close_order result for T-020 (turn 45, rule-based) and T-001 (turn 64, rule-based) shows the penalty message but the score is still 5/5 because the score_potential is high enough to absorb it (7 and 8 respectively, capped at 5).
- **Where:** `tools.py:close_order` scoring logic
- **Impact:** Confusing feedback message — says there's a penalty but the score is perfect.
- **Fix:** Either suppress the penalty message when score still maxes at 5, or reduce score_potential so the penalty actually matters.

## What's Working Well
- Rule-based solution wins cleanly: 15 resolved, 100% quality, 3 tokens, 75 turns
- Boss fight dependency resolution works perfectly — both bosses require prerequisites
- Edge case tests pass: boss without prereqs BLOCKED, authorize without briefing BLOCKED, blacklisted supplier BLOCKED+PENALTY
- Chain tasks trigger correctly (T-008→T-012, T-003→T-015, T-006→T-016, T-009→T-017)
- KB search returns relevant articles for all query types
- The trap tasks (rush orders) work as designed — KB clearly explains expedited shipping
- Two-boss design creates good complexity with independent dependency chains
- Scoring system differentiates handling quality well
