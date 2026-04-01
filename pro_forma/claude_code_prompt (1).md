# Claude Code Prompt: Business Case Builder Prototype

## Context — Read This First

You're joining a conversation already in progress. Here's everything you need to know about why we're building this, who it's for, and the thinking that got us here.

### The Problem We're Solving

We identified four pain points that managers and entrepreneurs hit when they try to use AI (specifically Claude via chat) to build financial models and projections:

1. **Specification difficulty**: People don't know what they want until they see a first draft. They can't give a complete brief upfront, so they end up in 8-10 rounds of back-and-forth with a chatbot, discovering their requirements as they go.

2. **Context re-establishment**: In long conversations, the AI loses track of earlier constraints. The user keeps having to remind it of things like "remember, we're targeting the German market" or "like I said, we only have three employees."

3. **Granularity mismatch**: The user wants to change one number in a 2,000-word document, but in chat they have to describe which number and what to change, then the AI regenerates everything. They need direct manipulation, not description-mediated editing.

4. **Output format friction**: They want a spreadsheet or PDF, but the chat interface means everything passes through text first and needs to be converted.

We looked at what exists in the market. Enterprise FP&A tools (Anaplan, Planful, Datarails) are powerful but overkill and expensive. Startup-focused tools (Sturppy, Finmark, FinModelBuilder) use rigid templates that break for non-standard business models. And chatbot-based approaches (Claude, ChatGPT) are maximally flexible but suffer from all four pain points above.

The gap is: **an adaptive, AI-powered tool that asks the right questions for YOUR specific business, shows a live preview as you answer, and lets you directly manipulate the output.** Not a fixed template, not a blank chat box — something in between that solves all four pain points.

### Who This Is For

This is a prototype to demonstrate to participants of a CAS (Certificate of Advanced Studies) program in AI Strategy at a Swiss university. We analyzed their profiles:

- **37 participants**, heavily concentrated in finance (UBS, Julius Baer, Raiffeisen, Swiss Re, Schaffhauser Kantonalbank), consulting (Deloitte, Bain, EY, Accenture), and corporate innovation (Novartis, Nestlé, Ringier, Vattenfall, Samsung)
- **Management level**: 8 senior (COOs, CEOs, Directors), 12 middle management, 13 lower/professional
- **Average experience**: ~14 years
- **Typical need**: They're NOT scrappy first-time founders. They're senior professionals who need to build business cases for internal ventures, AI transformation projects, new product lines, or innovation initiatives within their organizations. Some are running their own smaller companies.

So the framing is NOT "build your startup pitch deck." It's **"build the business case for your next big initiative in 5 minutes."**

### The Approach

We decided to focus on the simplest useful financial model: a **revenue-cost-runway projection**. Mathematically, this is just:

- A starting budget (cash on hand)
- An income function over time (revenue or cost savings or churn reduction)
- An expense function over time (fixed costs + variable costs)
- Finding the break-even crossover point and computing runway

It's a discrete time series over 24 months. The "business vocabulary" is just naming the components — the underlying math is simple arithmetic, geometric sequences for growth, and cumulative sums.

### What the Product Should Feel Like

The person who built this prompt (the course instructor) is a mathematician, not a business person. The prototype needs to make financial modeling feel intuitive and non-intimidating, while being rigorous enough that finance professionals (who WILL check the math) take it seriously.

The "wow moment" is: you type one sentence about your idea, answer 7 quick questions, and watch a professional financial dashboard build itself in real time. Then you can click and tweak any number directly. Three to five minutes, total.

### The Feedback Loop

This prototype serves double duty — it's both a demo product AND a research instrument. It includes a session tracking system that logs how users interact with it (which questions cause hesitation, which defaults get overridden, which assumptions get edited after the fact). This data gets exported as JSON and brought back for analysis, so we can identify remaining pain points and improve the next version.

---

Now here's what to build:

## What to Build

Build a single-page React application called **"CaseForge"** — an AI-powered business case builder that helps managers and executives go from a rough initiative idea to a credible financial projection in under 5 minutes.

This is a prototype for demonstration to senior managers (avg 14 years experience) at Swiss companies like UBS, Novartis, Ringier, Deloitte, and Samsung. It needs to feel polished and executive-grade, not like a hackathon project.

## The Core Experience

The app has three phases that flow seamlessly on one screen:

### Phase 1: Smart Interview (Left Panel)

The user starts by describing their initiative in a text field. Example: "I want to build an AI content recommendation engine for our media platforms to increase subscriber retention."

The app then sends this to the Anthropic API (Claude) which returns a structured set of 6-8 adaptive follow-up questions, one at a time. Each question should:
- Be specific to what the user described (not generic)
- Offer clickable options where possible (single select or slider)
- Include helpful context (e.g., "Media subscription services in Europe typically see 4-8% monthly churn")
- Have sensible defaults pre-filled

The questions should cover:
1. **Revenue model type**: Is this about new revenue, cost savings, or reducing churn?
2. **Scale parameters**: How big is the current base? (subscribers, customers, transactions)
3. **Impact estimate**: What improvement is realistic? (with industry benchmarks)
4. **Cost structure**: Build in-house vs outsource? Team size? Key cost items?
5. **Timeline**: When does it launch? How long to build?
6. **Initial investment**: Any upfront costs (licenses, infrastructure)?
7. **Starting cash / budget**: What budget is available?

### Phase 2: Live Dashboard (Right Panel)

As the user answers each question, the right panel progressively builds a 24-month financial projection. This is the "wow moment" — the dashboard comes alive as they answer.

The dashboard shows:
- **Summary bar**: Total investment, monthly run cost, projected annual impact, months to break-even
- **Timeline chart**: 24-month projection with costs (bars below zero line) and revenue/impact (curve above), break-even point highlighted
- **Assumptions panel**: Every input listed, each one directly editable (click to change)
- **Scenario tabs**: Conservative / Base / Optimistic (auto-generated by varying key assumptions ±20-30%)

### Phase 3: Direct Manipulation

After the interview, users can:
- Click any number in the assumptions panel and change it — the entire model recalculates instantly
- Use sliders for key parameters (growth rate, team size, timeline)
- Add or remove cost lines with a "+" button
- Toggle between scenarios
- All charts and summary numbers update in real time

### Export (Bottom Bar)

Three export buttons (can be mock/placeholder in prototype):
- "Executive Summary PDF"
- "Detailed Excel Model"  
- "Presentation Slide"

## The Financial Model (Math)

The underlying model is simple arithmetic. Here's the logic:

```
For each month t (1 to 24):

  // Revenue impact (depends on model type)
  If type == "new_revenue":
    impact[t] = base_customers * growth_rate^t * revenue_per_customer
  If type == "churn_reduction":  
    impact[t] = subscriber_base * (old_churn - new_churn) * avg_revenue_per_user
  If type == "cost_savings":
    impact[t] = current_monthly_cost * savings_percentage
  
  // Impact only starts after launch
  if t < launch_month: impact[t] = 0
  
  // Costs
  // Pre-launch: development costs (team salaries + infrastructure)
  // Post-launch: ongoing run costs (reduced team + maintenance + infrastructure)
  fixed_costs[t] = sum of all fixed monthly cost items
  variable_costs[t] = variable_rate * impact[t]
  total_costs[t] = fixed_costs[t] + variable_costs[t] + (upfront_costs if t==1 else 0)
  
  // Net
  net[t] = impact[t] - total_costs[t]
  cumulative[t] = cumulative[t-1] + net[t]
  
  // Break-even is when cumulative crosses zero
  // Runway is when starting_budget + cumulative crosses zero (if net is negative)
```

For scenarios:
- **Conservative**: reduce impact by 30%, increase costs by 20%, delay launch by 2 months
- **Base**: as entered
- **Optimistic**: increase impact by 25%, reduce costs by 10%, accelerate launch by 1 month

## Anthropic API Integration

Use the Anthropic API to power the smart interview. The API call structure:

```javascript
const response = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1000,
    system: `You are a financial modeling assistant helping executives build business cases.
    
Given the user's initiative description and their answers so far, generate the next question to ask.

Respond ONLY in JSON with this structure:
{
  "question_id": "q1",
  "question_text": "The question to display",
  "help_text": "Helpful context or industry benchmarks",
  "input_type": "select" | "number" | "slider" | "text",
  "options": ["Option A", "Option B", "Option C"],  // for select type
  "default_value": 50,  // suggested default
  "min": 0, "max": 100, "step": 1,  // for slider/number
  "unit": "CHF" | "%" | "months" | "people",
  "parameter_key": "subscriber_base",  // maps to model parameter
  "inferred_parameters": {  // any parameters the AI can already infer
    "revenue_model": "churn_reduction",
    "industry": "media"
  }
}

When you have enough information (6-8 questions answered), respond with:
{
  "complete": true,
  "summary": "Brief summary of the business case",
  "final_parameters": { ... all model parameters ... }
}`,
    messages: [
      { role: "user", content: conversationContext }
    ]
  })
});
```

## Feedback Loop System

**IMPORTANT**: Build a feedback/insights panel that helps us learn from usage.

Add a collapsible "Session Insights" panel (accessible via a small icon in the bottom-right corner) that tracks and displays:

1. **Interaction Log**: Timestamped record of every user action
   - Questions answered (with time spent on each)
   - Which defaults were accepted vs changed
   - Which assumptions were manually edited after the interview
   - Which scenarios were viewed
   - What was exported

2. **Pain Point Indicators**: Auto-detected friction moments
   - Questions where user hesitated (>30 seconds)
   - Questions where user changed their answer
   - Assumptions edited multiple times
   - Parameters where user deviated significantly from defaults

3. **Export Session Report**: A button that generates a JSON file containing:
   - Full interaction timeline
   - All parameter values (initial from AI vs final after edits)
   - Pain point flags
   - Session duration
   - Free-text feedback field (prompt user: "What was confusing? What's missing?")

This session report is what gets brought back to Claude.ai for analysis. The user copies the JSON or uploads the file, and we analyze patterns across sessions to improve the product.

## Design Direction

Target aesthetic: **Swiss executive minimalism meets Bloomberg terminal**

- Dark mode by default (these are finance people, they live in dark UIs)
- Clean typography — use something like "DM Sans" for body and "Fraunces" or "Playfair Display" for headings
- Accent color: a sharp teal or electric blue against dark backgrounds
- Charts should feel like Bloomberg/Reuters — dense with information but clean
- Smooth animations as dashboard elements appear (staggered reveal as questions are answered)
- The progressive build of the dashboard should feel almost magical — like watching a photograph develop

## Technical Stack

- React (single file, all-in-one)
- Recharts for charts
- Tailwind CSS for styling
- Anthropic API for the smart interview
- No localStorage needed — all state in React useState/useReducer
- The app should work as a standalone HTML file that can be opened in a browser

## What Success Looks Like

A senior manager at UBS or Ringier opens this, types a one-sentence description of their AI initiative, answers 7 quick questions, and 3 minutes later is looking at a professional 24-month financial projection that they can tweak with sliders and export to show their CFO. They think: "I need this."

## Important Notes

- The prototype should be fully functional — not a mockup
- The AI questions should genuinely adapt based on previous answers
- The financial math must be correct — these are finance people, they will check
- Pre-fill with a demo scenario so the prototype isn't empty on first load (use: "AI-powered client risk assessment tool for a Swiss private bank" as the default example)
- Include a "Reset / New Case" button to start fresh
- Mobile responsiveness is NOT needed for the prototype — this is for laptop/desktop demo

## API Key Setup

The prototype uses the Anthropic API for the adaptive interview questions. The cost is minimal — about $0.07 per user session (~15K input tokens + ~2K output tokens using Sonnet). For a class of 37 participants each running it a few times, total cost is under $10.

### How to set up:
1. Go to https://console.anthropic.com and create a free account (or log in if you already have one)
2. Go to Billing and add $10-20 of API credits
3. Go to API Keys and create a new key
4. Set it as an environment variable before running the app:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-your-key-here"
   ```

### How the app should handle the API key:
- The app should read the API key from an environment variable `ANTHROPIC_API_KEY`
- On startup, if no API key is found, show a clear, friendly message explaining how to set one up (with the steps above)
- **IMPORTANT**: The API key should NEVER be hardcoded in the source code or committed to any repository
- Pass the key via a simple backend proxy or build the app with a minimal Express/Node server that handles API calls server-side so the key isn't exposed in the browser. The server can be extremely simple — just one POST endpoint that forwards requests to the Anthropic API with the key attached.

### Architecture for API key security:
```
Browser (React app) → localhost:3000/api/ask → Node server → api.anthropic.com/v1/messages
                                                  ↑
                                          reads ANTHROPIC_API_KEY
                                          from environment
```

This way the API key stays server-side and never reaches the browser. The Node server is maybe 30 lines of code — just an Express app with one route that proxies to the Anthropic API.

## Fallback Mode

If for any reason the API is unreachable or the key isn't set, the app should gracefully fall back to a **hardcoded smart question flow**. This flow should:
- Detect keywords in the initial description (e.g., "SaaS", "subscription", "AI", "cost savings", "internal tool", "platform")
- Route to an appropriate pre-built question sequence based on the detected business model type
- Still produce a working financial model at the end

This way the prototype always works, even without internet or API access — useful for demo situations where connectivity might be unreliable.

## Project Structure

Set up the project as follows:
```
caseforge/
├── server.js          # Minimal Express server (~30 lines, proxies API calls)
├── package.json       # Dependencies: express, cors, react, recharts, etc.
├── .env.example       # Template showing ANTHROPIC_API_KEY=sk-ant-...
├── public/
│   └── index.html     # Entry point
├── src/
│   ├── App.jsx        # Main application component
│   ├── components/
│   │   ├── Interview.jsx      # Smart interview panel (left side)
│   │   ├── Dashboard.jsx      # Live financial dashboard (right side)
│   │   ├── Assumptions.jsx    # Editable assumptions panel
│   │   ├── ScenarioTabs.jsx   # Conservative/Base/Optimistic toggle
│   │   ├── ExportBar.jsx      # PDF/Excel/Slide export buttons
│   │   └── SessionInsights.jsx # Feedback tracking panel
│   ├── engine/
│   │   ├── financialModel.js  # Pure math — the calculation engine
│   │   └── scenarios.js       # Scenario generation logic
│   ├── api/
│   │   ├── claude.js          # API integration for smart interview
│   │   └── fallback.js        # Hardcoded question flow fallback
│   └── utils/
│       ├── sessionTracker.js  # Interaction logging for feedback loop
│       └── exportHelpers.js   # PDF/Excel generation utilities
└── README.md          # Setup instructions, architecture overview
```

## Running the App

After Claude Code builds it, the user should be able to:
```bash
cd caseforge
npm install
cp .env.example .env
# Edit .env to add your ANTHROPIC_API_KEY
npm start
# Opens browser to localhost:3000
```

That's it. Three commands and they're running.

## After You're Done Building: Debrief

Once the prototype is complete and working, please write a **BUILD_DEBRIEF.md** file in the project root. This is important — you're part of a three-way collaboration between yourself, the course instructor (a mathematician, not a business person), and another Claude instance (running in claude.ai) who designed the product spec with the instructor. Your debrief helps us all get smarter for the next iteration.

In BUILD_DEBRIEF.md, please cover:

### 1. Architectural Decisions & Tradeoffs
- What design choices did you make that weren't specified in the prompt?
- Where did you have to interpret ambiguous requirements?
- What tradeoffs did you make (e.g., simplicity vs. flexibility, performance vs. features)?

### 2. Financial Model Observations
- Are there edge cases in the math that could produce misleading results? (e.g., zero growth rate, negative values, very short or very long timelines)
- Did you find the model logic sufficient, or are there obvious gaps that a finance professional would notice?
- Any suggestions for making the model more robust?

### 3. AI Integration Insights
- How well does the system prompt work for generating adaptive questions? Any improvements you'd suggest?
- Did you encounter issues with getting consistent structured JSON output from the API?
- How does the fallback question flow compare to the AI-generated one? Where does it fall short?

### 4. UX & Design Observations
- What felt awkward or forced in the user flow?
- Where might users get confused or stuck?
- What would you prioritize improving in version 2?

### 5. Things You'd Do Differently
- If you were building this from scratch again with no constraints, what would you change?
- Any libraries, patterns, or approaches you'd recommend for the next version?

### 6. Ideas We Didn't Think Of
- Any features or improvements that occurred to you during the build that weren't in the spec?
- Anything that surprised you about the problem space?

Be honest and specific. Criticism is welcome — it makes the next version better. This debrief will be brought back to the claude.ai conversation for analysis and planning of v2.
