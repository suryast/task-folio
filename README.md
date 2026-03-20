# TaskFolio 📋

**See exactly which parts of your job AI will affect — task by task, with timeframes and success rates backed by 1M real conversations.**

TaskFolio is the first task-level AI exposure analysis tool for the Australian job market, helping 14.4M workers understand which specific parts of their job AI will affect — and when.

## The Problem

Existing tools show occupation-level AI exposure ("Software Developer: 9/10") with no actionable breakdown. Workers need to know:

- **Which specific tasks** in their job are changing
- **How soon** each task will be affected (0-2 years, 2-5 years, 10+ years)
- **How reliable** AI is for each task (success rates from real usage)
- **What to do** — learn, automate, or delegate

## How It Works

1. **Browse** 361 ANZSCO occupations on the treemap, or **enter any job title**
2. **TaskFolio decomposes** the role into 8–15 core tasks using O\*NET data + AI
3. **Each task gets scored** with economic primitives: exposure, success rate, speedup, timeframe
4. **See your exposure profile** — which tasks are safe, which are changing, and when

## Example: "Software Developer"

| Task | Exposure | Timeframe | Success Rate |
|---|---|---|---|
| Write production code | 85/100 | 0-2 years | 61% |
| Debug complex systems | 70/100 | 0-2 years | 65% |
| Design system architecture | 60/100 | 2-5 years | 55% |
| Mentor junior developers | 30/100 | 10+ years | 40% |

## Features

- ✅ O\*NET integration — 101 occupations with validated task breakdowns
- ✅ ANZSCO mapping for Australian job titles
- ✅ AI-powered decomposition for any role (Claude Haiku 4.5)
- ✅ Per-task AI exposure scoring with reasoning and timeframes
- ✅ Frequency-weighted job-level exposure score
- ✅ Task validation by users (agree/disagree/edit)
- 🔜 Anthropic Economic Index integration (1M real conversations)
- 🔜 361 ANZSCO occupations (treemap landing page)
- 🔜 Economic primitives (success rate, speedup, autonomy)
- 🔜 Shareable task portfolio links
- 🔜 SEO pages for top 50 job titles
- 🔜 Employer dashboard (B2B)

## Sprint Plan

| Sprint | Focus | Status |
|---|---|---|
| **S1** | Core engine — O\*NET, decomposition, scoring, API | ✅ Done |
| **S2** | Data expansion — Anthropic Economic Index, 361 occupations | ⏳ Next |
| **S3** | Frontend — Treemap, task breakdown UI, mobile, dark mode | Not started |
| **S4** | Launch — SEO, analytics, legal, go live | Not started |

## Tech Stack

| Layer | Choice |
|-------|--------|
| Frontend | Next.js 16 (App Router, TypeScript) |
| Styling | Tailwind CSS |
| Visualization | D3.js (treemap) |
| ORM | Drizzle |
| Database | PostgreSQL (Neon) |
| LLM | Anthropic Claude Haiku 4.5 |

## Data Sources

- [Anthropic Economic Index](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report) (CC-BY) — 1M real AI conversations classified by economic task
- [Jobs and Skills Australia](https://www.jobsandskills.gov.au/) — Employment and wage data
- [O\*NET](https://www.onetonline.org/) — 20,000 pre-classified occupational tasks
- [ychua/jobs](https://github.com/ychua/jobs) — ANZSCO occupation pipeline (OSS)

## API Endpoints

```
POST /api/analyze              — Decompose job + score AI exposure
GET  /api/occupations/search   — Search O*NET occupations
GET  /api/occupations/[code]   — Get occupation details + tasks
```

## Development

```bash
pnpm install
pnpm dev       # Start dev server at localhost:3000
pnpm test      # Run tests (25 tests)
pnpm build     # Production build
```

Requires `ANTHROPIC_API_KEY` in `.env` for LLM features. Copy `.env.example` to `.env.local`.

## Documentation

- [Project Overview](docs/PROJECT_OVERVIEW.md) — Full spec, competitive analysis, budget, risks
- [Sprint Plan](docs/SPRINT_PLAN.md) — Sprint execution with stories, acceptance criteria, scripts
- [Architecture](docs/ARCHITECTURE.md) — System design, API routes, Cloudflare stack, cost analysis, ADRs

## Attribution

Task data sourced from the [Anthropic Economic Index](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report) (CC-BY). Employment and wage data from [Jobs and Skills Australia](https://www.jobsandskills.gov.au/).

## Research Basis

Built on the "jobs as bundles of tasks" framework (Autor, Zweig). O\*NET provides the occupational taxonomy. AI exposure scoring uses the Anthropic Economic Index as the baseline.

## License

MIT
