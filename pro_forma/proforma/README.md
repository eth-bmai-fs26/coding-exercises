# ProForma -- AI-Powered Business Case Builder

Build a credible 24-month financial projection for your next big initiative in under 5 minutes.

## Quick Start

```bash
cd proforma
npm install
cp .env.example .env
# Edit .env to add your ANTHROPIC_API_KEY (optional -- app works without it)
npm start
# Opens browser to http://localhost:3000
```

## API Key Setup (Optional)

The app uses the Anthropic API for adaptive interview questions. Without a key, it falls back to a built-in question flow that works offline.

1. Go to https://console.anthropic.com and create an account
2. Add $10-20 of API credits under Billing
3. Create a new API key under API Keys
4. Add it to your `.env` file: `ANTHROPIC_API_KEY=sk-ant-your-key-here`

**Cost**: ~$0.07 per session (~15K input + ~2K output tokens using Claude Sonnet)

## Architecture

```
Browser (React/Vite on :3000)  ->  /api/ask  ->  Express proxy (:3001)  ->  api.anthropic.com
                                                      |
                                              reads ANTHROPIC_API_KEY
                                              from .env
```

- **Frontend**: React + Vite + Recharts + Tailwind CSS
- **Backend**: Minimal Express server (API key proxy)
- **Financial Engine**: Pure JavaScript, no external dependencies

## Features

- Smart adaptive interview (AI-powered or fallback)
- Live 24-month financial dashboard with break-even analysis
- Three scenarios: Conservative / Base / Optimistic
- Direct manipulation of all assumptions
- Session tracking for UX research
- CSV export of financial model
