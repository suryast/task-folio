# TaskFolio — Technical Architecture

**Last Updated:** March 2026  
**Status:** Design Phase  
**Stack:** Cloudflare (D1, Workers, Pages, KV, R2) + Next.js + Anthropic API

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     CLOUDFLARE PAGES                         │
│   Landing Page (Static) + Next.js App (Server-Side Rendered) │
│                                                              │
│   Routes:                                                    │
│     /              → Treemap (D3.js visualization)           │
│     /analyze/:code → Task breakdown                          │
│     /analyze/custom → Custom job input                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ API calls
┌──────────────────────────┴──────────────────────────────────┐
│                     CLOUDFLARE WORKERS                        │
│              API Layer (Hono framework, TypeScript)           │
│                                                              │
│   Endpoints:                                                 │
│     GET  /api/occupations                                    │
│     GET  /api/occupations/:code                              │
│     GET  /api/tasks/:code                                    │
│     POST /api/analyze                                        │
└───────────┬──────────────┬──────────────┬───────────────────┘
            │              │              │
┌───────────┴──┐ ┌────────┴─────┐ ┌─────┴────────┐
│ CLOUDFLARE   │ │ CLOUDFLARE   │ │  ANTHROPIC    │
│ D1 Database  │ │ KV Cache     │ │  API          │
│ (SQLite)     │ │              │ │  (Claude 4.5) │
│              │ │ - Results    │ │               │
│ - occupations│ │ - Analyses   │ │ - Task decomp │
│ - tasks      │ │ - Stats      │ │               │
└──────────────┘ └──────────────┘ └───────────────┘

              ┌──────────────┐
              │ CLOUDFLARE   │
              │ R2 Storage   │
              │              │
              │ - Raw data   │
              │ - Backups    │
              └──────────────┘
```

---

## Frontend (Cloudflare Pages)

**Technology:** Next.js 16 (App Router), TypeScript, Tailwind CSS, D3.js v7

### Key Pages

```typescript
// app/page.tsx - Landing page with treemap
export default function Home() {
  // Render D3 treemap of 361 occupations
  // Click → navigate to /analyze/:code
}

// app/analyze/[code]/page.tsx - Task breakdown
export default async function AnalyzePage({ params }) {
  const occupation = await fetch(`/api/occupations/${params.code}`);
  const tasks = await fetch(`/api/tasks/${params.code}`);
  return <TaskBreakdown occupation={occupation} tasks={tasks} />;
}

// app/analyze/custom/page.tsx - Custom job input
export default function CustomAnalyze() {
  // Form to POST /api/analyze
  // Display results
}
```

### Build Output

- Static HTML for `/` (treemap)
- Server-rendered for `/analyze/*`
- Edge-rendered via Cloudflare Pages Functions

### Deployment

```bash
npm run build
wrangler pages deploy .next --project-name=taskfolio-au
```

---

## API Layer (Cloudflare Workers)

**Technology:** Hono (lightweight web framework), TypeScript, Zod (validation)

### Project Structure

```
taskfolio-au-api/
├── src/
│   ├── index.ts              # Main worker entry
│   ├── routes/
│   │   ├── occupations.ts
│   │   ├── tasks.ts
│   │   └── analyze.ts
│   ├── lib/
│   │   ├── db.ts             # D1 helpers
│   │   ├── cache.ts          # KV helpers
│   │   └── anthropic.ts      # API client
│   └── types/
│       └── index.ts
├── wrangler.toml
├── package.json
└── tsconfig.json
```

### Core Implementation

```typescript
// src/index.ts
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { occupationsRouter } from './routes/occupations';
import { tasksRouter } from './routes/tasks';
import { analyzeRouter } from './routes/analyze';

type Bindings = {
  DB: D1Database;
  CACHE: KVNamespace;
  BUCKET: R2Bucket;
  ANTHROPIC_API_KEY: string;
};

const app = new Hono<{ Bindings: Bindings }>();

app.use('/*', cors());

app.get('/health', (c) => c.json({
  status: 'ok',
  timestamp: new Date().toISOString()
}));

app.route('/api/occupations', occupationsRouter);
app.route('/api/tasks', tasksRouter);
app.route('/api/analyze', analyzeRouter);

app.notFound((c) => c.json({ error: 'Not found' }, 404));

export default app;
```

### Occupations Router

```typescript
// src/routes/occupations.ts
export const occupationsRouter = new Hono<{ Bindings: Bindings }>();

// GET /api/occupations - List all
occupationsRouter.get('/', async (c) => {
  const cacheKey = 'occupations:list';
  const cached = await c.env.CACHE.get(cacheKey);
  if (cached) return c.json(JSON.parse(cached));

  const { results } = await c.env.DB
    .prepare(`
      SELECT anzsco_code, title, employment, median_pay_aud, outlook,
             ai_exposure_weighted as ai_exposure
      FROM occupations ORDER BY employment DESC LIMIT 500
    `).all();

  await c.env.CACHE.put(cacheKey, JSON.stringify(results), { expirationTtl: 3600 });
  return c.json(results);
});

// GET /api/occupations/:code - Get single
occupationsRouter.get('/:code', async (c) => {
  const code = c.req.param('code');
  const cacheKey = `occupation:${code}`;
  const cached = await c.env.CACHE.get(cacheKey);
  if (cached) return c.json(JSON.parse(cached));

  const result = await c.env.DB
    .prepare('SELECT * FROM occupations WHERE anzsco_code = ?')
    .bind(code).first();

  if (!result) return c.json({ error: 'Occupation not found' }, 404);

  await c.env.CACHE.put(cacheKey, JSON.stringify(result), { expirationTtl: 86400 });
  return c.json(result);
});

// GET /api/occupations/search - Search by title
occupationsRouter.get('/search', async (c) => {
  const query = c.req.query('q');
  if (!query || query.length < 2) {
    return c.json({ error: 'Query must be at least 2 characters' }, 400);
  }

  const { results } = await c.env.DB
    .prepare(`
      SELECT anzsco_code, title, employment, ai_exposure_weighted as ai_exposure
      FROM occupations WHERE title LIKE ? ORDER BY employment DESC LIMIT 20
    `).bind(`%${query}%`).all();

  return c.json(results);
});
```

### Tasks Router

```typescript
// src/routes/tasks.ts
export const tasksRouter = new Hono<{ Bindings: Bindings }>();

tasksRouter.get('/:code', async (c) => {
  const code = c.req.param('code');
  const cacheKey = `tasks:${code}`;
  const cached = await c.env.CACHE.get(cacheKey);
  if (cached) return c.json(JSON.parse(cached));

  const occupation = await c.env.DB
    .prepare('SELECT id FROM occupations WHERE anzsco_code = ?')
    .bind(code).first();

  if (!occupation) return c.json({ error: 'Occupation not found' }, 404);

  const { results } = await c.env.DB
    .prepare(`
      SELECT description, automation_pct, augmentation_pct, success_rate,
             human_time_without_ai, human_time_with_ai, speedup_factor,
             human_education_years, ai_autonomy, timeframe,
             taskfolio_score, frequency
      FROM tasks WHERE occupation_id = ? ORDER BY taskfolio_score DESC
    `).bind(occupation.id).all();

  const response = { anzsco_code: code, task_count: results.length, tasks: results };
  await c.env.CACHE.put(cacheKey, JSON.stringify(response), { expirationTtl: 86400 });
  return c.json(response);
});
```

### Analyze Router (Custom Job Decomposition)

```typescript
// src/routes/analyze.ts
import Anthropic from '@anthropic-ai/sdk';

export const analyzeRouter = new Hono<{ Bindings: Bindings }>();

const JobInputSchema = z.object({
  job_title: z.string().min(2).max(200),
  job_description: z.string().max(5000).optional()
});

analyzeRouter.post('/', async (c) => {
  const body = await c.req.json();
  const validation = JobInputSchema.safeParse(body);
  if (!validation.success) return c.json({ error: validation.error }, 400);

  const { job_title, job_description } = validation.data;
  const cacheKey = `custom:${job_title.toLowerCase().replace(/\s+/g, '-')}`;
  const cached = await c.env.CACHE.get(cacheKey);
  if (cached) return c.json(JSON.parse(cached));

  const anthropic = new Anthropic({ apiKey: c.env.ANTHROPIC_API_KEY });

  const prompt = `Break down this job into 8-12 core tasks with AI exposure analysis:

Job Title: ${job_title}
${job_description ? `Description: ${job_description}` : ''}

For each task, provide:
1. Task description (1-2 sentences)
2. Frequency (high/medium/low)
3. AI exposure score (0-100)
4. Estimated timeframe (0-2yr, 2-5yr, 5-10yr, 10yr+)
5. Success rate estimate (0-100)

Return ONLY valid JSON:
{
  "tasks": [
    {
      "description": "...",
      "frequency": "high",
      "ai_exposure": 85,
      "timeframe": "0-2yr",
      "success_rate": 67
    }
  ]
}`;

  try {
    const message = await anthropic.messages.create({
      model: 'claude-haiku-4.5-20250514',
      max_tokens: 2000,
      messages: [{ role: 'user', content: prompt }]
    });

    const result = JSON.parse(message.content[0].text);

    await c.env.DB
      .prepare('INSERT INTO user_analyses (job_title, job_description, analysis_json) VALUES (?, ?, ?)')
      .bind(job_title, job_description || null, JSON.stringify(result)).run();

    await c.env.CACHE.put(cacheKey, JSON.stringify(result), { expirationTtl: 604800 });
    return c.json(result);
  } catch (error) {
    console.error('Anthropic API error:', error);
    return c.json({ error: 'Failed to analyze job' }, 500);
  }
});
```

---

## Configuration

### wrangler.toml

```toml
name = "taskfolio-au-api"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[[d1_databases]]
binding = "DB"
database_name = "taskfolio-au"
database_id = "<your-database-id>"

[[kv_namespaces]]
binding = "CACHE"
id = "<your-kv-namespace-id>"

[[r2_buckets]]
binding = "BUCKET"
bucket_name = "taskfolio-data"

[vars]
ENVIRONMENT = "production"

# Secrets (set via: wrangler secret put ANTHROPIC_API_KEY)
```

---

## Database (Cloudflare D1)

**Size Estimate:**
- Occupations: ~100KB
- Tasks: ~10MB
- User analyses: ~1MB/month
- Total: <20MB

**Queries/Day Estimate:**
- Occupations list: 1,000 (cached)
- Task breakdowns: 5,000
- Custom analyses: 500
- Total: ~6,500 (well under 5M limit)

---

## KV Cache Strategy

| Key Pattern | TTL | Purpose |
|---|---|---|
| `occupations:list` | 1 hour | All occupations list |
| `occupation:{code}` | 24 hours | Single occupation |
| `tasks:{code}` | 24 hours | Tasks for occupation |
| `custom:{normalized-title}` | 7 days | Custom analysis result |
| `stats:global` | 1 hour | Global statistics |

**Usage Estimate:** 50K reads/day, 1K writes/day (within free tier)

---

## R2 Storage

```
taskfolio-data/
├── raw/
│   ├── anthropic-economic-index/
│   │   ├── onet_task_statements.csv
│   │   ├── automation_vs_augmentation_by_task.csv
│   │   ├── economic_primitives_by_task.csv
│   │   └── ...
│   └── ychua-jobs/
│       ├── data.json
│       └── scores.json
├── processed/
│   ├── anzsco_onet_mapping.csv
│   ├── taskfolio_master_data.json
│   └── generated_tasks.json
└── backups/
    └── taskfolio-au-{date}.db
```

**Storage:** ~100MB

---

## Request Flows

### 1. Browse Treemap
```
User → Pages (/) → fetch /api/occupations → KV cache (hit) → Return JSON → Render D3 treemap
```

### 2. View Occupation Tasks
```
User clicks tile (ANZSCO 2611) → Pages (/analyze/2611)
  → fetch /api/occupations/2611 + /api/tasks/2611
  → KV cache (hit) → Server-render page → Display task breakdown
```

### 3. Custom Job Analysis
```
User submits "DevOps Engineer" → POST /api/analyze
  → KV cache (miss) → Call Anthropic API → Parse JSON
  → Store in D1 user_analyses → Cache in KV (7 days) → Return breakdown
```

---

## Performance

- **Static pages (treemap):** 1,000+ concurrent users
- **Requests/second:** 100+
- **D1 queries/second:** 50+
- **Uptime:** 99.9%+ (Cloudflare SLA)
- **Edge locations:** 300+ globally
- **Failover:** Automatic

---

## Security

- **CORS:** Restricted origins
- **Rate limiting:** 100 req/min per IP
- **Input validation:** Zod schemas
- **SQL injection:** Parameterized queries only
- **Secrets:** `wrangler secret put ANTHROPIC_API_KEY` (never committed)
- **Privacy:** No PII collected, custom analyses anonymized, IPs not logged

---

## Cost Analysis

| Service | Free Tier | V1 Usage | Cost |
|---|---|---|---|
| Workers | 100K req/day | ~10K/day | $0 |
| D1 | 5GB + 5M reads/day | 20MB + 10K reads/day | $0 |
| KV | 100K reads/day | 50K/day | $0 |
| Pages | Unlimited | Static + SSR | $0 |
| R2 | 10GB storage | 100MB | $0 |
| Anthropic API | N/A | ~$50 one-time | $50 |
| **Total** | | | **$50** |

**Projected V1 monthly cost:** $0-5 (within free tier)

### Scaling Costs

| Phase | Monthly Cost |
|---|---|
| V1 (0-1K users) | $0-5 |
| Growth (1K-10K users) | $20-50 |
| Scale (10K+ users) | $200-500 |

### Migration Options (If Needed)

1. **Upgrade paid plans** — Workers $5/mo + usage, no code changes
2. **Hybrid** — Keep Cloudflare edge, add Neon PostgreSQL
3. **Full migration** — Vercel + Neon (2-3 weeks work)

---

## Development Setup

```bash
# Install Wrangler
npm install -g wrangler
wrangler login

# Clone & install
git clone https://github.com/suryast/task-folio.git
cd task-folio && npm install

# Environment
cp .env.example .env.local
# Add ANTHROPIC_API_KEY to .env.local

# Local D1
wrangler d1 execute taskfolio-au --local --file=schema.sql

# Start dev
wrangler dev --local          # API
cd frontend && npm run dev     # Frontend
```

### Testing

```bash
npm test                # Unit tests
npm run test:integration  # Integration tests
npm run test:e2e         # E2E tests
```

### Deployment

```bash
# Deploy worker
wrangler deploy

# Deploy frontend
cd frontend && npm run build
wrangler pages deploy .next

# Verify
curl https://api.taskfolio.com.au/health

# Rollback
wrangler deployments list
wrangler rollback <deployment-id>
```

### Backups

```bash
# Daily D1 backups to R2
wrangler d1 export taskfolio-au --output=backup.sql
wrangler r2 object put taskfolio-data/backups/$(date +%Y%m%d).sql --file=backup.sql

# Restore
wrangler r2 object get taskfolio-data/backups/20260315.sql --file=restore.sql
wrangler d1 execute taskfolio-au --file=restore.sql
```

---

## Architecture Decision Records

### ADR-1: Cloudflare over Vercel

**Decision:** Use Cloudflare Workers + D1 instead of Vercel + Neon

**Rationale:** Zero cost at scale, SQLite at edge (faster queries), no cold starts, integrated stack (Pages, Workers, D1, KV, R2)

**Trade-offs:** D1 less mature than PostgreSQL, smaller ecosystem, vendor lock-in

### ADR-2: Hono Framework

**Decision:** Use Hono framework in Workers

**Rationale:** Built for edge environments, tiny bundle size (<14KB), first-class Cloudflare support

**Trade-offs:** Smaller community than Express, fewer plugins

### ADR-3: Fork ychua's Treemap

**Decision:** Copy ychua's D3.js treemap instead of building custom

**Rationale:** Proven visualization, familiar UX, MIT licensed, no need to reinvent

**Trade-offs:** Older D3 patterns (v7), not React-native, some refactoring needed

---

## Monitoring

- Page views, unique visitors, geographic distribution
- API response times, cache hit rates
- Anthropic API costs, D1 query counts
- Error rates by endpoint

```bash
# View worker logs
wrangler tail
```
