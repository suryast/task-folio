# TaskFolio — Project Overview

**Repository:** [https://github.com/suryast/task-folio](https://github.com/suryast/task-folio)

**Launch Target:** 8 weeks from Sprint 0 start

**Domain:** taskfolio.com.au (to register)

---

## Mission

Build the first task-level AI exposure analysis tool for the Australian job market, helping 14.4M Australian workers understand which specific parts of their job AI will affect—and when.

## Problem

Existing tools (karpathy/jobs, ychua/jobs):

- Show occupation-level AI exposure ("Software Developer: 9/10")
- No actionable breakdown
- Static, browse-only experience
- No customization for individual roles

**Gap:** Workers need to know:

- Which specific tasks in their job are changing?
- How soon will each task be affected?
- How reliable is AI for each task?
- What should they learn/automate/delegate?

## Core Value Proposition

> "See exactly which parts of your job AI will affect—task by task, with timeframes and success rates backed by 1M real conversations."

## Key Features (V1)

- **Treemap landing page** — 361 ANZSCO occupations (familiar UX)
- **Task breakdown** — Click occupation → see 8-15 specific tasks
- **Economic primitives** — Show success rates, time savings, education required
- **Custom job analysis** — Enter any job title → get AI decomposition
- **Australian context** — Market-specific adjustments and timeframes

## Competitive Comparison

| Dimension | karpathy/ychua | TaskFolio |
|---|---|---|
| Granularity | Occupation-level | Task-level (8-15 per job) |
| Data source | LLM guess | Anthropic Economic Index (1M conversations) |
| Customization | Fixed 342/361 jobs | Any job title + description |
| Metrics | AI exposure score (0-10) | Exposure + success rate + speedup + timeframe |
| Market | US/AU browse only | Australia-first, personalized |
| Validation | None | Research-backed (Anthropic) |

**Moat:** Task-level granularity + economic primitives + Australian localization + custom job input

## Why Australia, Why Now

- **Zero competition** — No one doing task-level analysis in AU
- **Data pipeline exists** — ychua built it, we fork it
- **Smaller market** — 14.4M workers vs. 143M (US) = faster validation
- **Government data** — JSA/ABS comprehensive and free
- **ANZSCO mapping ready** — Infrastructure exists in codebase
- **English-speaking** — Easier user research, content, marketing
- **University partnerships** — AU unis love local tools

## Free Resources

- **Anthropic Economic Index** — FREE, CC-BY license, research-backed
- **ychua's pipeline** — Proven, production-ready, OSS
- **Cloudflare** — Zero cost at scale, no DevOps
- **O*NET tasks** — 20,000 pre-classified tasks

## Success Criteria (V1 Launch)

- Traffic: 1,000 unique visitors
- Engagement: 100+ custom job analyses, 3+ min avg. time on site
- Distribution: HN front page, 50+ social shares, 1 media mention
- Validation: 20 user interviews, >70% "would recommend"

## Economic Primitives

Not just exposure scores—show real-world usage patterns:

- **Task success rate:** 67% (Claude.ai), 49% (API)
- **Time savings:** 3.3 hours → 15 min (13x speedup)
- **Education required:** 13.8 years (college degree)
- **Collaboration pattern:** 60% automation, 40% augmentation
- **AI autonomy:** 3/5 (medium oversight)

### Australian Context Adjustments

- JSA employment + earnings data (AUD)
- 5-year growth projections
- Regulatory context (e.g., medical AI restrictions)
- Market maturity adjustments (-15% success for tech roles)

### Example: "Software Developer"

| Task | Exposure | Timeframe | Success Rate |
|---|---|---|---|
| Write production code | 85/100 | 0-2 years | 61% |
| Debug complex systems | 70/100 | 0-2 years | 65% |
| Design system architecture | 60/100 | 2-5 years | 55% |
| Mentor junior developers | 30/100 | 10+ years | 40% |

## Post-V1 Roadmap

- User accounts (magic link)
- Save analysis history
- PDF export
- Email sharing
- US market launch
- B2B employer dashboard
- API access
- Task validation voting

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Next.js 16 (App Router, TypeScript) |
| Styling | Tailwind CSS |
| Visualization | D3.js (ychua's treemap) |
| ORM | Drizzle |
| Database | PostgreSQL (Neon) |
| AI | Anthropic Claude Haiku 4.5 |

## Data Sources

- **Tasks:** Anthropic Economic Index (HuggingFace)
- **Occupations:** ychua/jobs (JSA + ABS)
- **Mapping:** O*NET (via Anthropic)

## Budget

| Item | Cost | Notes |
|---|---|---|
| Domain (.com.au) | $20/year | taskfolio.com.au |
| Cloudflare | $0/month | Free tier covers V1 |
| Anthropic API | ~$50 | One-time task scoring |
| **Total** | **~$70** | Zero monthly recurring |

## Attribution

Required by CC-BY license:

> Task data sourced from the Anthropic Economic Index (CC-BY)

**Citations:**
- Appel, R., Massenkoff, M., & McCrory, P. (2026). "Anthropic Economic Index report: Economic primitives" https://www.anthropic.com/research/anthropic-economic-index-january-2026-report
- Handa et al. (2025). "Which Economic Tasks are Performed with AI?" ArXiv: 2503.04761

Employment and wage data from Jobs and Skills Australia (JSA).

## Risks

### Technical

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| D1 performance | High | Medium | Indexes, caching, query optimization |
| Anthropic rate limits | High | Low | Cache results, batch requests |
| ANZSCO mapping quality | Medium | Medium | Manual validation, confidence >0.7 |
| Deployment issues | High | Low | Staging environment, gradual rollout |

### Market

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Low initial traffic | Medium | Medium | Strong HN/Reddit launch |
| Negative feedback | Low | Low | Clear methodology page |
| Legal/IP issues | High | Very Low | Proper attribution, T&C |

## Team

Solo founder:
- Data engineering (Sprint 1)
- Backend development (Sprint 2)
- Frontend development (Sprint 3)
- Product + launch (Sprint 4)

**Estimated time:**
- Full-time (40 hrs/week): 8 weeks
- Part-time (20 hrs/week): 16 weeks
