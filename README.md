# TaskFolio 📋

**See your job as AI sees it.**

TaskFolio decomposes any knowledge worker role into its component tasks and scores each one for AI automation exposure. Understand which parts of your job are most (and least) vulnerable to AI — and what to do about it.

## The Problem

AI is reshaping knowledge work, but workers have no tools to understand their personal exposure. "Will AI take my job?" is the wrong question — the right question is **"Which of my tasks will AI change?"**

## How It Works

1. **Enter your job title** or paste a job description
2. **TaskFolio decomposes** the role into 8–15 core tasks using O\*NET data + AI
3. **Each task gets scored** 0–100 for AI automation potential
4. **See your exposure profile** — which tasks are safe, which are changing, and when

## Features

- ✅ O\*NET integration — 101 occupations with validated task breakdowns
- ✅ ANZSCO mapping for Australian job titles
- ✅ AI-powered decomposition for any role (Claude Haiku 4.5)
- ✅ Per-task AI exposure scoring with reasoning and timeframes
- ✅ Frequency-weighted job-level exposure score
- ✅ Task validation by users (agree/disagree/edit)
- 🔜 Shareable task portfolio links
- 🔜 Adjacent role suggestions
- 🔜 SEO pages for top 50 job titles
- 🔜 Employer dashboard (B2B)

## Tech Stack

| Layer | Choice |
|-------|--------|
| Frontend | Next.js 14 (App Router, TypeScript) |
| Styling | Tailwind CSS |
| ORM | Drizzle |
| Database | PostgreSQL (Neon) |
| LLM | Anthropic Claude Haiku 4.5 |
| Auth | Magic link (S2) |

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

## Project Status

- [x] **S1** — Core engine (O\*NET data, task decomposition, AI scoring, API routes)
- [ ] **S2** — UI (landing page, input flow, results view, sharing)
- [ ] **S3** — Validation loop (task voting, user refinement, aggregate scores)
- [ ] **S4** — Distribution (SEO pages, social sharing, waitlist)

## Research Basis

Built on the "jobs as bundles of tasks" framework (Autor, Zweig). O\*NET provides the occupational taxonomy. AI exposure scoring uses current LLM capabilities as the baseline.

## License

Proprietary. All rights reserved.
