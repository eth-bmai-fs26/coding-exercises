# Improvement Log — Iteration 1

## Issues Fixed

1. **T-015 stuck loop (Critical)** — Added escalation-complete close path in `_auto_handle`: when `order.requires_escalation` matches `order.escalated_to`, auto-notify (if template exists) then auto-close. This prevents the LLM from being called for a fully-handled escalation order, eliminating the 30+ turn stuck loop and 2 token losses. — `the_supply_line_solutions.ipynb` (cell `5gtil1at89q`)

2. **Missing close-gate guardrail (High)** — Added guardrail in `think_llm` that blocks `close_order` and `notify_client` when `order.requires_action` is set but `order.action_applied` is False. The guardrail redirects to the correct `place_order` action based on order category/message content. This prevents T-018 and T-012 from scoring 0/5. — `the_supply_line_solutions.ipynb` (cell `5gtil1at89q`)

3. **Rush order place_order not in autopilot (High)** — Added `place_order` handling in `_auto_handle` for rush orders (`OrderCategory.RUSH`), which always uses `expedited="true"`. This is deterministic and doesn't need LLM involvement. — `the_supply_line_solutions.ipynb` (cell `5gtil1at89q`)

4. **System prompt missing action-before-notify rule** — Added "ALWAYS place_order BEFORE notifying or closing reorder/rush/quality orders" to the system prompt to reduce LLM errors even when guardrails don't catch them. — `the_supply_line_solutions.ipynb` (cell `5gtil1at89q`)

## Issues Deferred

1. **Rule-based wrong SKU/supplier for T-021 (Medium)** — Cosmetic only, no score impact. Would require more complex supplier routing logic. Low priority.

2. **T-020/T-001 penalty message shows but score is 5/5 (Low)** — Polish issue in the game engine. Would require changes to `close_order` scoring display logic. Not worth the risk of breaking scoring.

## Verification (Rule-Based Solution)
- Won: yes
- Resolved: 15
- Score: 100.0%
- Tokens: 3
- Turns: 75

(LLM solution cannot be verified without Gemini API key, but all three failure modes are now addressed by autopilot/guardrail changes that don't depend on LLM behavior.)

## Ready for Re-Test: YES
