# Build Debrief — ProForma v1

## 1. Architectural Decisions & Tradeoffs

**Vite 5 instead of Vite 7**: The host machine runs Node 18. Vite 7 requires Node 20+, so I pinned Vite to v5 and @vitejs/plugin-react to v4 for compatibility. This is transparent to the user experience.

**Tailwind v3 (not v4)**: Same Node 18 constraint. Tailwind v4 requires Node 20+. Used the classic PostCSS pipeline with `tailwind.config.js`.

**Single useReducer vs. Context**: I kept all state in a single `useReducer` at the App level and passed props down. For a prototype with ~6 components, this is simpler than adding React Context. If the app grows beyond 10+ components, extracting a `ProFormaContext` provider would be the right next step.

**Express proxy as separate process**: The Vite dev server proxies `/api/*` to Express on port 3001. In production you'd want a single server, but for a prototype this separation is cleaner and the `concurrently` setup makes it invisible to the user.

**Fallback question flows are hardcoded per revenue model type**: Three complete flows (new_revenue, churn_reduction, cost_savings) with Swiss-market benchmarks. The keyword detection is simple regex matching — good enough for a prototype but a real version should use the AI to classify.

## 2. Financial Model Observations

**Edge cases handled**:
- Growth rate capped at -99% to prevent NaN from `Math.pow`
- Launch month clamped to 1-24 range
- Savings percentage clamped to 0-100%
- Break-even uses linear interpolation between months for fractional precision

**Potential issues a finance professional might notice**:
- Growth is compound (geometric), which can produce unrealistically large numbers at high growth rates over 24 months. A 15% monthly growth rate means 28x in 24 months. Consider adding a saturation/S-curve model.
- Variable costs are a flat percentage of impact. Real variable costs often have step functions (hire a new person every X customers).
- No discounting/NPV calculation. Finance professionals expect to see time-value-of-money adjustments. Adding a discount rate parameter would be straightforward.
- No tax consideration. For an internal business case at a Swiss company, this matters.

**Suggestions for v2**:
- Add NPV and IRR calculations
- Add sensitivity analysis (tornado chart showing which parameter has the most impact)
- Support S-curve growth models alongside exponential
- Allow multiple revenue streams

## 3. AI Integration Insights

**System prompt design**: The prompt asks for structured JSON output. In practice, Claude sometimes wraps responses in markdown code fences (```json ... ```). The `claude.js` module strips these before parsing, which handles the most common failure mode.

**Structured output reliability**: Claude Sonnet is very good at producing valid JSON with this prompt structure. The main risk is when the conversation context gets long (many previous answers) — the model may start including explanatory text. The "ONLY valid JSON" instruction in the system prompt mitigates this.

**Fallback vs AI comparison**: The fallback flow is deterministic and fast — questions appear instantly with no loading state. The AI flow adds 1-3 seconds per question but produces genuinely adaptive questions (e.g., if you say "media company," it'll ask about subscriber metrics; if you say "bank," it'll ask about AUM). The fallback can only route between three pre-built flows based on keyword detection.

**Improvement for v2**: Use Claude's tool_use/function_calling feature instead of asking for raw JSON. This gives you schema validation for free and eliminates parsing issues.

## 4. UX & Design Observations

**What works well**:
- The progressive dashboard reveal is compelling — seeing numbers appear as you answer creates a strong feedback loop
- Dark Bloomberg-style aesthetic looks professional and appropriate for the audience
- The fallback mode ensures the demo never fails, even without internet

**What feels awkward**:
- The left panel (interview) and right panel (dashboard) don't have a clear visual connection. Adding animated connectors or highlighting which dashboard element just updated would strengthen the progressive-build experience.
- After the interview, the left panel switches to an assumptions editor — this transition could be smoother. A brief "Summary" state between interview and editing would help.
- The session insights panel is discoverable only by a small icon in the bottom-right. For a research tool, it should be more prominent.

**Where users might get stuck**:
- Number inputs don't have clear validation feedback. If you type a negative number for customers, it silently produces weird results.
- The scenario tabs don't show the actual numbers, just labels. Adding sparkline previews would help.
- No undo functionality. If you change an assumption and want to go back, you can't.

## 5. Things I'd Do Differently

**If building from scratch with no constraints**:
- Use Next.js or Remix instead of Vite + Express. Server-side API calls would be built-in, no separate proxy needed.
- Use Zustand instead of useReducer — better developer experience for reactive state with computed values.
- Use D3.js instead of Recharts for the chart. Recharts is faster to implement but D3 gives full control over the Bloomberg-terminal aesthetic (custom axes, crosshairs, annotations).
- Add a proper form library (React Hook Form) for the assumptions panel to handle validation, dirty state, and undo.

**Libraries to consider for v2**:
- `jspdf` + `jspdf-autotable` for real PDF export
- `xlsx` for proper Excel export with formulas
- `framer-motion` for smoother animations
- `@tanstack/react-table` if the assumptions panel grows into a spreadsheet-like editor

## 6. Ideas We Didn't Think Of

- **Comparison mode**: Let users save multiple scenarios side-by-side (not just conservative/base/optimistic, but entirely different initiative ideas).
- **Collaborative editing**: Share a URL with a colleague, they see the same dashboard and can suggest parameter changes.
- **AI "sanity check"**: After the user finishes editing assumptions, send the final parameters back to Claude and ask "Does this business case make sense? What are the biggest risks?" Display the response as a brief advisory note.
- **Benchmark overlay**: Show industry-average curves on the same chart (anonymized from previous sessions) so users can see if their projections are in the right ballpark.
- **"What would it take?" mode**: Instead of forward-projecting from assumptions, let users set a target (e.g., "break even in 12 months") and have the model back-calculate what growth rate or cost structure would be needed.
- **The session tracking data is gold**: With 37 participants each running 3-5 sessions, you'll have ~150 sessions. Analyze which questions cause the most hesitation, which defaults get changed most, and which parameters get edited after the interview. This tells you exactly where the fallback question flows need improvement and which industry benchmarks are wrong.
