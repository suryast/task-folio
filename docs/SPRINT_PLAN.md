# TaskFolio — Sprint Execution Plan

## Sprint 1: Core Engine ✅

**Goal:** O*NET data integration, task decomposition engine, AI exposure scoring, API routes.

**Completed:**
- ✅ O*NET integration — 101 occupations with validated task breakdowns
- ✅ ANZSCO mapping for Australian job titles
- ✅ AI-powered decomposition for any role (Claude Haiku 4.5)
- ✅ Per-task AI exposure scoring with reasoning and timeframes
- ✅ Frequency-weighted job-level exposure score
- ✅ API routes: `POST /api/analyze`, `GET /api/occupations/search`, `GET /api/occupations/[code]`
- ✅ 25 tests passing

---

## Sprint 2: Anthropic Economic Index + Data Expansion ✅

**Goal:** Integrate Anthropic Economic Index for research-backed economic primitives. Expand from 101 to 361 ANZSCO occupations.

**Completed:**
- ✅ S2.1 — ANZSCO → O*NET mapping (147 high-confidence matches)
- ✅ S2.2 — Anthropic Economic Index integration (3,074 tasks)
- ✅ S2.3 — Claude-generated tasks for 214 unmapped occupations (3,616 tasks)
- ✅ S2.4 — Cloudflare D1 database setup (361 occupations, 6,690 tasks)
- ✅ S2.5 — 100% timeframe coverage (23.5% now, 31% 1-2y, 31.4% 3-5y, 10.9% 5-10y, 3.3% 10y+)

### S2.1 — ANZSCO → O*NET Mapping Expansion

**Story:** Map remaining ANZSCO occupations to O*NET codes for full 361-occupation coverage.

**Tasks:**
- Extract 361 ANZSCO occupations from ychua's `site/data.json`
- Load Anthropic's `onet_task_statements.csv`
- Implement fuzzy matching using `difflib.SequenceMatcher`
- Generate confidence scores for each match
- Export matches with confidence >0.7 to `anzsco_onet_mapping.csv`
- Manual review: Flag matches with confidence <0.85

**Acceptance Criteria:**
- ✅ 250-300 ANZSCO occupations mapped to O*NET
- ✅ CSV with columns: `anzsco_code`, `anzsco_title`, `onet_soc_code`, `onet_title`, `confidence`
- ✅ Confidence threshold >0.7 documented
- ✅ Unmapped occupations identified (~100-110)

**Script:** `data/step1_build_anzsco_mapping.py`

---

### S2.2 — Integrate Anthropic Economic Index

**Story:** Merge all Anthropic Economic Index datasets for complete task data with economic primitives.

**Tasks:**
- Load 6 Anthropic CSV files (tasks, automation, primitives, usage, wages, employment)
- Merge on `task_id` and `onet_soc_code`
- Join with ANZSCO mapping
- Filter to mapped occupations only
- Validate data completeness
- Export to `taskfolio_master_data.json`

**Acceptance Criteria:**
- ✅ All Anthropic datasets merged
- ✅ Data includes: task description, automation/augmentation, success rate, time savings, education, autonomy
- ✅ ~2,500-3,500 tasks (250-300 occupations × 10-12 avg)

**Script:** `data/step2_integrate_anthropic_data.py`

---

### S2.3 — Generate Tasks for Unmapped Occupations

**Story:** Use Claude Haiku 4.5 to generate tasks for ~100-110 unmapped ANZSCO occupations.

**Tasks:**
- Load unmapped occupations
- Write task decomposition prompt
- Call Anthropic API per occupation
- Parse JSON responses
- Score generated tasks (frequency, exposure)
- Append to master data
- Handle API errors

**Acceptance Criteria:**
- ✅ 8-12 tasks per unmapped occupation
- ✅ All tasks have: description, frequency, AI exposure estimate
- ✅ Cost: <$50 API spend

**Script:** `data/step3_decompose_unmapped.py`

---

### S2.4 — Database Population

**Story:** Import expanded occupation + task data into production database.

**Tasks:**
- Write migration for new Anthropic fields (economic primitives)
- Import 361 occupations
- Import ~4,500 tasks with all primitives
- Verify data integrity
- Create indexes for performance

**Acceptance Criteria:**
- ✅ All occupations imported
- ✅ All tasks with foreign keys
- ✅ Economic primitives queryable
- ✅ Sample queries work

---

### S2.5 — Timeframe Predictions ✅

**Story:** Users need to know WHEN each task will be affected, not just IF.

**Tasks:**
- ✅ Design timeframe prediction prompt
- ✅ Batch 3,074 Anthropic tasks into 13 subagent batches
- ✅ Generate timeframes using in-session Claude Sonnet
- ✅ Parse timeframes (now, 1-2y, 3-5y, 5-10y, 10y+)
- ✅ Apply Australian context adjustments
- ✅ Merge into master data
- ✅ Update D1 database

**Acceptance Criteria:**
- ✅ All 6,690 tasks have timeframe predictions (100% coverage)
- ✅ Realistic distribution: 23.5% now, 31% 1-2y, 31.4% 3-5y, 10.9% 5-10y, 3.3% 10y+
- ✅ Australian adjustments applied (regulatory lag, SME adoption, physical constraints)
- ✅ Cost: $0 (used in-session generation instead of external API)

---

## Sprint 3: Frontend UI

**Goal:** Build the treemap landing page and task breakdown UI.

**Top priorities:**
- D3.js treemap landing page (fork from ychua)
- Task breakdown detail page with economic primitives
- Custom job analysis input form
- Mobile responsive
- Dark mode

---

## Sprint 4: Launch

**Goal:** SEO, analytics, legal, and go live.

**Top priorities:**
- SEO meta tags, sitemap, robots.txt
- Analytics (Cloudflare Web Analytics)
- Legal pages (privacy, terms, attribution)
- Launch content (HN, Reddit, AU tech press)
- **DAY 40: GO LIVE 🚀**

---

## Data Pipeline

```
step1 → ANZSCO→O*NET fuzzy mapping (361 occupations)
step2 → Merge 6 Anthropic Economic Index datasets
step3 → Generate tasks for ~100 unmapped occupations (Claude Haiku)
step4 → Import to database with economic primitives
step5 → Timeframe predictions + TaskFolio scores
```

## Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Anthropic API rate limits | High | `sleep()` between batches |
| Database size | Medium | Monitor, optimize queries |
| Mapping confidence too low | Medium | Manual review + AI fallback |
| Missing fields | Low | Defaults or NULL |
