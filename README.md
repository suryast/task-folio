# TaskFolio 📋

**See exactly which parts of your job AI will affect — task by task, with timeframes backed by 1M real conversations.**

Task-level AI exposure analysis for 361 Australian occupations. Built with Cloudflare D1, Anthropic Economic Index, and Claude Sonnet 4.5.

🌐 **Live:** Coming soon (Sprint 4)  
🔗 **API:** `taskfolio-au-api.hello-bb8.workers.dev`  
📊 **Data:** 361 ANZSCO occupations • 6,690 tasks • 100% timeframe coverage

---

## What It Does

**Problem:** Existing AI job impact tools show occupation-level scores ("Software Developer: 9/10") with no actionable breakdown.

**Solution:** TaskFolio breaks jobs into 8-20 specific tasks and scores each one:
- **Which tasks** AI will affect
- **When** (now, 1-2y, 3-5y, 5-10y, 10y+)
- **How much** (automation %, augmentation %, speedup)
- **Economic primitives** from Anthropic's 1M real AI conversations

---

## Example: Software Developer (ANZSCO 2613)

| Task | Timeframe | Auto | Aug | Source |
|---|---|---|---|---|
| Write production code | now | 73% | 27% | Anthropic |
| Debug systems | 1-2y | 68% | 32% | Anthropic |
| Code review | 1-2y | 0% | 100% | Anthropic |
| Mentor juniors | 10y+ | 5% | 45% | Anthropic |
| System architecture | 3-5y | 0% | 85% | Anthropic |

_12 more tasks..._

---

## Data Pipeline

### Sprint 2: Data Expansion ✅ Complete

Built a two-tier pipeline to map 361 Australian (ANZSCO) occupations to economic primitives:

**Tier 1 — High Confidence Matches (147 occupations)**
- ANZSCO → O*NET fuzzy matching (confidence >0.7)
- Merged Anthropic Economic Index (6 CSV datasets, 1M conversations)
- **3,074 research-backed tasks** with automation %, success rate, speedup

**Tier 2 — Unmapped Occupations (214 occupations)**
- Generated tasks with Claude Sonnet 4.5 (13 parallel subagent batches, 4 min)
- Australian-specific context (regulations, SME adoption, geography)
- **3,616 AI-generated tasks** with timeframe predictions

**Final Dataset:**
- **361 ANZSCO occupations** (100% Australian labour market coverage)
- **6,690 tasks** with economic primitives
- **100% timeframe coverage** (now: 23.5%, 1-2y: 31%, 3-5y: 31.4%, 5-10y: 10.9%, 10y+: 3.3%)
- **1.6MB D1 database** (Sydney region)

### Why Two Tiers?

Fuzzy matching `difflib.SequenceMatcher` produced garbage for 214 occupations:
- "Chefs" → "Chemists" (0.62 confidence) ❌
- "Police" → "Producers" (0.53) ❌
- "Kitchenhands" → "Mapping Technicians" (0.52) ❌

**Trade-off:** Claude-generated tasks are templates (not research-backed), but they're **occupation-specific** and **Australian-context-aware** — better than wrong O*NET data.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Cloudflare Pages (Next.js 16)                 │
│  • D3.js treemap (361 occupations)             │
│  • Task breakdown detail pages                 │
│  • Responsive, dark mode                       │
└──────────────────┬──────────────────────────────┘
                   │ REST API
┌──────────────────▼──────────────────────────────┐
│  Cloudflare Workers (Hono)                     │
│  • /api/occupations → list all                 │
│  • /api/tasks/{code} → task breakdown          │
│  • /api/analyze → custom job input (future)    │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Cloudflare D1 (SQLite, Sydney region)         │
│  • occupations (361 rows, 50KB)                │
│  • tasks (6,690 rows, 1.5MB)                   │
│  • KV cache (24h TTL)                          │
└─────────────────────────────────────────────────┘
```

**Tech Stack:**
- Frontend: Next.js 16, React 19, Tailwind, D3.js
- API: Hono (Cloudflare Workers)
- Database: Cloudflare D1 (SQLite)
- Cache: Cloudflare KV
- LLM: Claude Sonnet 4.5 (for task generation)

---

## Sprint Status

| Sprint | Goal | Status | Deliverable |
|---|---|---|---|
| **S1** | Core Engine | ✅ Complete | O*NET integration, decomposition API, 25 tests |
| **S2** | Data Expansion | ✅ Complete | 361 occupations, 6,690 tasks, D1 database |
| **S3** | Frontend UI | ⏳ 60% | Treemap + detail pages deployed, needs adapter config |
| **S4** | Launch | Not started | SEO, analytics, legal, go live |

### Sprint 2 Details (Complete)

**Delivered:**
- ✅ S2.1: ANZSCO → O*NET fuzzy mapping (147 high-confidence matches)
- ✅ S2.2: Anthropic Economic Index integration (3,074 tasks)
- ✅ S2.3: Claude-generated tasks for 214 unmapped occupations (3,616 tasks)
- ✅ S2.4: Cloudflare D1 database setup (1.6MB, Sydney region)
- ✅ S2.5: 100% timeframe coverage (13 subagent batches, 4 min)

**Methodology doc:** [Data Pipeline](docs/SPRINT_PLAN.md#sprint-2-anthropic-economic-index--data-expansion)

### Sprint 3 Details (In Progress)

**Delivered:**
- ✅ S3.1: Interactive D3 treemap landing page (361 occupations)
- ✅ S3.2: Task breakdown detail pages (grouped by timeframe)
- ✅ Worker API deployed: `taskfolio-au-api.hello-bb8.workers.dev`
- ⚠️ Pages deployed: `taskfolio-au.pages.dev` (needs `@cloudflare/next-on-pages` adapter)

**Remaining:**
- S3.3: Configure Cloudflare Pages adapter for Next.js
- S3.4: Custom job input form (optional)

---

## Deployment

### Current Status

| Component | URL | Status |
|---|---|---|
| **Worker API** | `taskfolio-au-api.hello-bb8.workers.dev` | ✅ Live |
| **D1 Database** | `taskfolio-au` (OC/Sydney) | ✅ Live (6,690 tasks) |
| **KV Cache** | `CACHE` namespace | ✅ Configured |
| **Pages (Next.js)** | `taskfolio-au.pages.dev` | ⚠️ Needs adapter |

### Test API

```bash
# List all occupations
curl https://taskfolio-au-api.hello-bb8.workers.dev/api/occupations

# Get tasks for Software Developer (ANZSCO 2613)
curl https://taskfolio-au-api.hello-bb8.workers.dev/api/tasks/2613
```

### Known Issues

1. **Pages deployment broken** — Raw `.next` output deployed without `@cloudflare/next-on-pages` adapter
2. **Custom domain** — Not configured yet (recommend `taskfolio.au`)
3. **Analytics** — Not set up yet (use Cloudflare Web Analytics in S4)

---

## Development

```bash
# Install dependencies
pnpm install

# Start Worker API (local)
cd api && pnpm dev
# → http://localhost:8787

# Start Next.js frontend (local)
pnpm dev
# → http://localhost:3000

# Build for production
pnpm build

# Deploy Worker
cd api && wrangler deploy

# Deploy Pages (needs adapter fix)
# TODO: Configure @cloudflare/next-on-pages
```

### Environment Variables

```bash
# .env.local (development)
NEXT_PUBLIC_API_URL=http://localhost:8787

# .env.production (production)
NEXT_PUBLIC_API_URL=https://taskfolio-au-api.hello-bb8.workers.dev
```

---

## Data Sources

- **[Anthropic Economic Index](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report)** (CC-BY) — 1M real AI conversations, 6 CSV datasets
- **[O*NET](https://www.onetonline.org/)** — 20,000 occupational tasks, 974 SOC codes
- **[Jobs and Skills Australia](https://www.jobsandskills.gov.au/)** — ANZSCO taxonomy, employment data
- **[ychua/jobs](https://github.com/ychua/jobs)** — Treemap inspiration (OSS, MIT)

---

## Project Structure

```
task-folio/
├── app/                      # Next.js app (treemap + detail pages)
├── components/               # React components (TreemapVisualization)
├── api/                      # Cloudflare Worker (Hono API)
│   ├── src/
│   │   ├── index.ts         # Routes: /api/occupations, /api/tasks
│   │   ├── lib/db.ts        # D1 queries
│   │   └── lib/cache.ts     # KV cache layer
│   └── wrangler.toml        # Worker config + D1/KV bindings
├── data/pipeline/            # Data processing scripts
│   ├── step1_build_anzsco_mapping.py
│   ├── step2_integrate_anthropic_data.py
│   ├── step3_decompose_unmapped.py     # 13 subagent batches
│   ├── step4_import_to_d1.py
│   └── output/
│       └── taskfolio_master_data.json  # 6,690 tasks (6.8MB)
├── sql/schema.sql            # D1 schema (occupations, tasks, user_analyses)
├── docs/                     # Sprint plans, architecture, overview
└── package.json              # Next.js 16, D3, pnpm workspace
```

---

## Cost Analysis

**Current (Free Tier):**
- Cloudflare D1: 5GB storage, 5M rows read/day (using <0.1%)
- Cloudflare Workers: 100k requests/day (using <1%)
- Cloudflare Pages: Unlimited bandwidth
- **Total: $0/month** up to ~10k visitors/day

**At Scale (100k visitors/month):**
- D1: ~$5/month (10M reads)
- Workers: Free (within limits)
- Pages: Free
- **Total: ~$5/month**

---

## Attribution

Task data sourced from:
- **Anthropic Economic Index** (CC-BY) — Automation/augmentation percentages, success rates, economic primitives
- **O*NET** — Occupational task descriptions
- **Jobs and Skills Australia** — ANZSCO taxonomy, employment data

Built on the "jobs as bundles of tasks" framework (Autor, Zweig).

---

## License

MIT

---

## Next Steps

1. **S3.3:** Configure `@cloudflare/next-on-pages` adapter
2. **S4:** SEO meta tags, sitemap, analytics
3. **Launch:** HN, Reddit, AU tech press
4. **Domain:** Register `taskfolio.au`

See [SPRINT_PLAN.md](docs/SPRINT_PLAN.md) for detailed roadmap.
