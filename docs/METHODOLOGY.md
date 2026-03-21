# TaskFolio Methodology

**Version:** 1.0  
**Last Updated:** 2026-03-21  
**Author:** Surya Setiyaputra

This document details the complete methodology for TaskFolio's task-level AI exposure analysis. The pipeline transforms raw occupation data into actionable AI impact predictions for 361 Australian occupations and 6,690 individual tasks.

---

## Table of Contents

1. [Overview](#overview)
2. [Data Sources](#data-sources)
3. [Pipeline Architecture](#pipeline-architecture)
4. [Step 1: ANZSCO-O*NET Fuzzy Matching](#step-1-anzsco-onet-fuzzy-matching)
5. [Step 2: Anthropic Economic Index Integration](#step-2-anthropic-economic-index-integration)
6. [Step 3: Task Generation for Unmapped Occupations](#step-3-task-generation-for-unmapped-occupations)
7. [Step 4: Timeframe Prediction](#step-4-timeframe-prediction)
8. [Step 5: AI Exposure Scoring](#step-5-ai-exposure-scoring)
9. [Australian Context Adjustments](#australian-context-adjustments)
10. [Data Quality & Limitations](#data-quality--limitations)
11. [Reproducing This Analysis](#reproducing-this-analysis)

---

## Overview

TaskFolio answers a simple question: **Which specific tasks in my job will AI affect, and when?**

Existing AI exposure tools provide occupation-level scores ("Software Developer: 85% exposed") without actionable breakdown. TaskFolio decomposes occupations into individual tasks and predicts:

- **Automation potential** — Can AI fully replace this task?
- **Augmentation potential** — Can AI assist humans doing this task?
- **Timeframe** — When will this impact occur (now, 1-2y, 3-5y, 5-10y, 10y+)?
- **Success rate** — How reliably does AI perform this task today?

### Key Metrics

| Metric | Definition | Range |
|--------|------------|-------|
| **AI Exposure** | Weighted average of task-level automation + augmentation | 0-100% |
| **Half-Life** | Estimated years until AI can perform ~50% of occupation tasks | 2-20 years |
| **Future-Proof Index** | Composite score: `100 - (AI_exposure × 40) - pay_risk - outlook_risk` | 0-100 |

### Future-Proof Index Formula

The Future-Proof Index combines three risk factors:

```
Score = 100 - AI_exposure_risk - pay_risk - outlook_risk
```

| Component | Weight | Calculation | Rationale |
|-----------|--------|-------------|-----------|
| **AI Exposure Risk** | 40 pts | `ai_exposure_weighted × 40` | Higher AI exposure = higher displacement risk |
| **Pay Risk** | 30 pts | `30 - ((pay - 40K) / 160K × 30)` | Lower pay = easier to justify automation ROI |
| **Outlook Risk** | 30 pts | `15 - (growth_10yr_pct × 0.75)` | Declining employment = shrinking opportunity |

**Outlook Risk** uses Jobs and Skills Australia's 10-year employment projections:
- +20% growth → 0 pts risk (strong demand)
- 0% growth → 15 pts risk (stagnant)
- -10% growth → 30 pts risk (declining)

**Score Interpretation:**
| Score | Label | Meaning |
|-------|-------|---------|
| 70-100 | FUTURE-PROOF | Low AI exposure + strong demand + high pay |
| 50-69 | ADAPTABLE | Moderate risk, skills transfer possible |
| 30-49 | AT RISK | High exposure or declining demand |
| 0-29 | VULNERABLE | High exposure + low pay + declining demand |

---

## Data Sources

### Primary Sources

| Source | License | Records | Usage |
|--------|---------|---------|-------|
| [Anthropic Economic Index](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report) | CC-BY 4.0 | 3,074 tasks | Automation %, augmentation %, success rates |
| [O*NET Database](https://www.onetonline.org/) | Public Domain | 19,265 tasks | Task descriptions, cognitive/physical categories |
| [Jobs and Skills Australia](https://www.jobsandskills.gov.au/) | AU Gov (CC) | 361 occupations | ANZSCO taxonomy, employment, wages |
| [JSA Employment Projections](https://www.jobsandskills.gov.au/data/employment-projections) | AU Gov (CC) | 358 occupations | 10-year employment growth projections (May 2025 → May 2035) |

### Supplementary Sources

| Source | Usage |
|--------|-------|
| ABS Labour Force Survey | Employment counts by occupation |
| ABS Employee Earnings | Median pay by occupation |
| Fair Work Commission | Award rates for unmapped wages |

### Data Freshness

- **Anthropic Index:** January 2026 release (1M conversations analyzed)
- **O*NET:** Version 29.1 (August 2025)
- **ANZSCO:** 2022 revision
- **Employment data:** August 2025 quarter

---

## Pipeline Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   ANZSCO 361    │     │   O*NET 873     │     │  Anthropic 147  │
│   occupations   │     │   occupations   │     │   occupations   │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────┬───────────┘                       │
                     │                                   │
              ┌──────▼──────┐                            │
              │ Step 1:     │                            │
              │ Fuzzy Match │                            │
              │ (147 mapped)│                            │
              └──────┬──────┘                            │
                     │                                   │
              ┌──────▼──────┐     ┌──────────────────────▼──────┐
              │ Step 2:     │◄────┤ Anthropic Economic Index    │
              │ Merge Data  │     │ automation_pct, augment_pct │
              └──────┬──────┘     │ success_rate, speedup_factor│
                     │            └─────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
  ┌──────▼──────┐         ┌──────▼──────┐
  │ 147 Mapped  │         │ 214 Unmapped│
  │ (O*NET+     │         │             │
  │  Anthropic) │         └──────┬──────┘
  └──────┬──────┘                │
         │                ┌──────▼──────┐
         │                │ Step 3:     │
         │                │ Claude Gen  │
         │                │ (3,616 tasks│
         │                └──────┬──────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼──────┐
              │ Step 4:     │
              │ Timeframe   │
              │ Prediction  │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │ Step 5:     │
              │ Scoring &   │
              │ Import to D1│
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │ 6,690 Tasks │
              │ 361 Occup.  │
              │ 100% coverage│
              └─────────────┘
```

---

## Step 1: ANZSCO-O*NET Fuzzy Matching

**Script:** `data/pipeline/step1_build_anzsco_mapping.py`

### Problem

Australian occupations use ANZSCO codes; Anthropic's data uses US O*NET SOC codes. We need to map between them.

### Approach

1. **Exact title matching** — Direct string comparison
2. **Fuzzy matching** — FuzzyWuzzy library with token_sort_ratio
3. **Manual review** — Ambiguous matches verified manually

### Algorithm

```python
from fuzzywuzzy import fuzz

def match_occupation(anzsco_title: str, onet_occupations: list) -> tuple:
    """Return best O*NET match and confidence score."""
    best_match = None
    best_score = 0
    
    for onet in onet_occupations:
        # Token sort handles word order differences
        # "Software Developer" vs "Developer, Software"
        score = fuzz.token_sort_ratio(
            anzsco_title.lower(),
            onet['title'].lower()
        )
        
        if score > best_score:
            best_score = score
            best_match = onet
    
    return best_match, best_score / 100
```

### Confidence Thresholds

| Score | Action | Example |
|-------|--------|---------|
| ≥0.90 | Auto-accept | "Accountant" → "Accountants" |
| 0.70-0.89 | Review | "ICT Manager" → "Computer and Information Systems Managers" |
| <0.70 | Reject | No reliable match found |

### Results

- **147 occupations** mapped with confidence ≥0.70
- **214 occupations** unmapped (require task generation)
- **Average confidence:** 0.84

### Edge Cases Handled

| ANZSCO Title | O*NET Match | Notes |
|--------------|-------------|-------|
| "Barristers" | "Lawyers" | AU-specific legal term |
| "General Practitioners" | "Family Medicine Physicians" | Healthcare terminology |
| "Shearers" | No match | AU-specific agricultural role |

---

## Step 2: Anthropic Economic Index Integration

**Script:** `data/pipeline/step2_integrate_anthropic_data.py`

### Anthropic Data Structure

The Economic Index provides task-level metrics from 1M real AI conversations:

```json
{
  "occupation": "Software Developers",
  "soc_code": "15-1252.00",
  "tasks": [
    {
      "description": "Write and test code for software applications",
      "automation_pct": 0.45,
      "augmentation_pct": 0.92,
      "success_rate": 0.78,
      "human_time_minutes": 120,
      "ai_time_minutes": 25,
      "speedup_factor": 4.8,
      "primitives": ["code_generation", "debugging", "testing"]
    }
  ]
}
```

### Field Definitions

| Field | Definition | Source |
|-------|------------|--------|
| `automation_pct` | Fraction of task fully completed by AI without human | Conversation analysis |
| `augmentation_pct` | Fraction of task where AI assisted human | Conversation analysis |
| `success_rate` | AI output accepted without revision | User feedback signals |
| `speedup_factor` | Human time ÷ AI time | Timestamp analysis |
| `primitives` | Economic primitives used (validation, generation, etc.) | Task decomposition |

### Merge Logic

For each mapped ANZSCO occupation:

1. Retrieve all O*NET tasks for the occupation
2. Match to Anthropic task descriptions using fuzzy matching
3. Inherit automation/augmentation metrics
4. For unmatched O*NET tasks, estimate from similar tasks

```python
def merge_anthropic_data(onet_task: dict, anthropic_tasks: list) -> dict:
    """Enrich O*NET task with Anthropic metrics."""
    
    # Find best matching Anthropic task
    best_match, score = fuzzy_match_task(
        onet_task['description'],
        anthropic_tasks
    )
    
    if score >= 0.75:
        # Direct merge
        return {
            **onet_task,
            'automation_pct': best_match['automation_pct'],
            'augmentation_pct': best_match['augmentation_pct'],
            'success_rate': best_match['success_rate'],
            'speedup_factor': best_match['speedup_factor'],
            'source': 'anthropic'
        }
    else:
        # Estimate from category averages
        category_avg = get_category_average(onet_task['category'])
        return {
            **onet_task,
            'automation_pct': category_avg['automation'],
            'augmentation_pct': category_avg['augmentation'],
            'source': 'estimated'
        }
```

### Category Averages (Fallback)

When direct task matching fails, we use category-level averages:

| Category | Avg Automation | Avg Augmentation |
|----------|----------------|------------------|
| Cognitive-Analytical | 0.52 | 0.85 |
| Cognitive-Creative | 0.31 | 0.78 |
| Interpersonal | 0.18 | 0.62 |
| Physical-Routine | 0.15 | 0.25 |
| Physical-Complex | 0.08 | 0.35 |

---

## Step 3: Task Generation for Unmapped Occupations

**Script:** `data/pipeline/step3_decompose_unmapped.py`

### Problem

214 ANZSCO occupations have no O*NET equivalent (Australian-specific roles like Shearers, Barristers, Station Managers).

### Approach

Use Claude Sonnet 4.5 to generate task breakdowns based on:
- Official ANZSCO occupation descriptions
- Australian regulatory context
- Industry-specific requirements

### Prompt Template

```markdown
You are an occupational analyst creating task breakdowns for Australian jobs.

## Occupation
Title: {title}
ANZSCO Code: {code}
Description: {description}

## Instructions
Generate 15-20 specific tasks for this occupation. For each task:

1. Write a clear, actionable task description (1-2 sentences)
2. Estimate AI automation potential (0.0-1.0)
3. Estimate AI augmentation potential (0.0-1.0)
4. Consider Australian regulatory context:
   - TGA for medical devices
   - ASIC/APRA for financial services
   - State licensing requirements
   - Privacy Act 1988 constraints

## Output Format (JSON)
{
  "tasks": [
    {
      "description": "...",
      "automation_pct": 0.XX,
      "augmentation_pct": 0.XX,
      "category": "cognitive|interpersonal|physical",
      "au_regulatory_factors": ["TGA", "Privacy Act"]
    }
  ]
}
```

### Generation Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | Claude Sonnet 4.5 | Balance of quality and cost |
| Temperature | 0.3 | Low for consistency |
| Max tokens | 4000 | ~20 tasks with metadata |
| Batch size | 15 occupations | Rate limit management |

### Quality Controls

1. **Minimum task count:** 10 tasks per occupation
2. **Category distribution:** At least 2 categories represented
3. **Range validation:** automation_pct and augmentation_pct in [0, 1]
4. **Duplicate detection:** Cosine similarity check across tasks

### Results

- **214 occupations** processed
- **3,616 tasks** generated
- **Average tasks per occupation:** 16.9
- **Batch runs:** 13 (with error recovery)

---

## Step 4: Timeframe Prediction

**Script:** `data/pipeline/step5_refine_timeframes.py`

### Timeframe Categories

| Timeframe | Label | Definition |
|-----------|-------|------------|
| `now` | Already happening | AI tools in production use (2024-2026) |
| `1-2y` | Early deployment | Enterprise adoption starting (2026-2028) |
| `3-5y` | Mainstream adoption | SME uptake, price commoditization (2028-2031) |
| `5-10y` | Significant barriers | Regulatory, infrastructure, trust barriers (2031-2036) |
| `10y+` | Fundamental constraints | Physical presence, human judgment required (2036+) |

### Prediction Factors

```python
def predict_timeframe(task: dict, occupation: dict) -> str:
    """Predict when AI will significantly impact this task."""
    
    factors = {
        'current_automation': task['automation_pct'],
        'current_augmentation': task['augmentation_pct'],
        'physical_requirement': task['category'] == 'physical',
        'regulatory_burden': len(task.get('au_regulatory_factors', [])),
        'trust_sensitivity': occupation.get('trust_sensitive', False),
        'infrastructure_dependency': task.get('requires_infrastructure', False)
    }
    
    # High automation + augmentation = happening now
    if factors['current_automation'] > 0.7 and factors['current_augmentation'] > 0.8:
        return 'now'
    
    # Physical tasks with low automation = longer timeline
    if factors['physical_requirement'] and factors['current_automation'] < 0.3:
        return '10y+' if factors['current_automation'] < 0.1 else '5-10y'
    
    # Regulatory burden adds delay
    regulatory_delay = factors['regulatory_burden'] * 1.5  # years
    
    # Base prediction from automation level
    if factors['current_automation'] > 0.5:
        base = '1-2y'
    elif factors['current_automation'] > 0.3:
        base = '3-5y'
    else:
        base = '5-10y'
    
    # Adjust for regulatory delay
    return adjust_timeframe(base, regulatory_delay)
```

### Australian Regulatory Adjustments

| Regulator | Impact | Delay Added |
|-----------|--------|-------------|
| TGA | Medical devices, health AI | +2-3 years |
| ASIC | Financial advice, trading | +1-2 years |
| APRA | Banking, insurance | +1-2 years |
| Privacy Act | Personal data processing | +0.5-1 year |
| State licensing | Trades, professionals | +1-2 years |

### Batch Processing

Timeframe prediction runs in batches to manage API costs:

```python
BATCH_CONFIG = {
    'batch_size': 30,  # occupations per batch
    'model': 'claude-sonnet-4-5',
    'max_retries': 3,
    'checkpoint_interval': 5  # save progress every 5 batches
}
```

### Distribution Results

| Timeframe | Tasks | Percentage |
|-----------|-------|------------|
| Now | 1,570 | 23.5% |
| 1-2 years | 2,071 | 31.0% |
| 3-5 years | 2,103 | 31.4% |
| 5-10 years | 726 | 10.9% |
| 10+ years | 220 | 3.3% |

---

## Step 5: AI Exposure Scoring

**Script:** `data/pipeline/step4_import_to_d1.py`

### Occupation-Level AI Exposure

```python
def calculate_ai_exposure(tasks: list) -> float:
    """
    Calculate overall AI exposure for an occupation.
    
    Formula: Simple average of (automation + augmentation) / 2 per task
    """
    if not tasks:
        return 0.0
    
    total_exposure = 0
    for task in tasks:
        task_exposure = (
            task['automation_pct'] + 
            task['augmentation_pct']
        ) / 2
        total_exposure += task_exposure
    
    return total_exposure / len(tasks)
```

### Half-Life Calculation

```python
def calculate_half_life(ai_exposure: float) -> int:
    """
    Estimate years until AI can perform ~50% of occupation tasks.
    
    Formula: half_life = 2 + (1 - exposure) * 18
    
    - 100% exposure → 2 years (already happening)
    - 50% exposure → 11 years
    - 0% exposure → 20 years
    """
    return round(2 + (1 - ai_exposure) * 18)
```

### Future-Proof Index

```python
def calculate_future_proof_index(
    ai_exposure: float,
    median_pay: int,
    outlook: str
) -> int:
    """
    Composite score combining multiple factors.
    
    Components:
    - AI Resistance (40%): 1 - ai_exposure
    - Pay Resilience (30%): normalized pay score
    - Growth Outlook (30%): employment outlook score
    """
    
    # AI resistance (inverted exposure)
    ai_resistance = (1 - ai_exposure) * 40
    
    # Pay resilience (normalized to AU median $70k)
    pay_score = min(median_pay / 140000, 1.0) * 30
    
    # Growth outlook
    outlook_scores = {
        'Strong growth': 30,
        'Moderate growth': 22,
        'Stable': 15,
        'Decline': 5
    }
    outlook_score = outlook_scores.get(outlook, 15)
    
    return round(ai_resistance + pay_score + outlook_score)
```

### Score Distribution

| Metric | Min | Max | Mean | Median |
|--------|-----|-----|------|--------|
| AI Exposure | 0.31 | 1.00 | 0.82 | 0.85 |
| Half-Life | 2 | 15 | 5.2 | 4 |
| Future-Proof Index | 18 | 89 | 42 | 38 |

---

## Australian Context Adjustments

### Why Australian-Specific Analysis?

US-centric AI impact studies don't account for:

1. **Regulatory environment** — TGA, ASIC, APRA, Privacy Act
2. **Market structure** — SME-dominated, geographic isolation
3. **Labor market** — High unionization in some sectors, casual employment
4. **Infrastructure** — Rural connectivity, physical distances

### Adjustment Factors

#### Regulatory Delays

```python
AU_REGULATORY_DELAYS = {
    'healthcare': {
        'tga_approval': 1.5,  # years
        'medicare_listing': 1.0,
        'state_registration': 0.5
    },
    'financial_services': {
        'asic_licensing': 1.0,
        'apra_compliance': 1.5,
        'aml_requirements': 0.5
    },
    'legal': {
        'state_admission': 0.5,
        'professional_indemnity': 0.3
    }
}
```

#### SME Adoption Lag

Australian SMEs (97% of businesses) adopt new technology 18-24 months after US enterprises:

```python
def apply_sme_lag(base_timeframe: str, occupation: dict) -> str:
    """
    Adjust timeframe for Australian SME adoption patterns.
    
    Based on ABS Business Characteristics Survey 2024.
    """
    sme_sectors = [
        'retail', 'hospitality', 'construction', 
        'agriculture', 'personal_services'
    ]
    
    if occupation['sector'] in sme_sectors:
        return shift_timeframe(base_timeframe, months=18)
    
    return base_timeframe
```

#### Infrastructure Constraints

```python
INFRASTRUCTURE_FACTORS = {
    'rural_connectivity': {
        'affected_occupations': ['farmers', 'miners', 'remote_health'],
        'delay_months': 24,
        'reason': '25% of AU on <25 Mbps vs 14% US'
    },
    'hardware_deployment': {
        'affected_tasks': ['physical_automation', 'robotics'],
        'delay_months': 12,
        'reason': 'Higher logistics costs, smaller market'
    }
}
```

---

## Data Quality & Limitations

### Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Anthropic data is US-centric | May overestimate automation in AU-regulated sectors | Applied regulatory delay factors |
| O*NET task descriptions are US-specific | Some tasks don't translate (e.g., "401k administration") | Filtered irrelevant tasks, generated AU-specific alternatives |
| Employment data is aggregate | No breakdown by employer size, region | Used sector-level adjustments |
| AI capabilities change rapidly | Predictions may be outdated within 6-12 months | Quarterly update pipeline planned |

### Data Quality Scores

| Source | Completeness | Accuracy | Freshness |
|--------|--------------|----------|-----------|
| Anthropic Index | 95% | High (1M conversations) | Jan 2026 |
| O*NET Tasks | 100% | High (DOL validated) | Aug 2025 |
| ANZSCO Mapping | 41% direct match | Medium (fuzzy matching) | Mar 2026 |
| Generated Tasks | 59% of occupations | Medium (LLM-generated) | Mar 2026 |

### Confidence Indicators

Tasks include a `source` field indicating data provenance:

| Source | Confidence | Count |
|--------|------------|-------|
| `anthropic` | High | 3,074 |
| `onet_matched` | Medium-High | 1,847 |
| `generated` | Medium | 3,616 |
| `estimated` | Low | 153 |

### Validation Approach

1. **Expert review:** 50 randomly sampled occupations reviewed by HR professionals
2. **User feedback:** In-app feedback mechanism (planned)
3. **Outcome tracking:** Compare predictions to actual AI adoption (longitudinal)

---

## Reproducing This Analysis

### Prerequisites

```bash
# Python 3.11+
python --version

# Required packages
pip install pandas fuzzywuzzy python-Levenshtein anthropic

# Environment variables
export ANTHROPIC_API_KEY=your_key
export CLOUDFLARE_API_TOKEN=your_token
```

### Pipeline Execution

```bash
cd data/pipeline

# Step 1: Build ANZSCO-O*NET mapping
python step1_build_anzsco_mapping.py

# Step 2: Integrate Anthropic data
python step2_integrate_anthropic_data.py

# Step 3: Generate tasks for unmapped occupations
python step3_decompose_unmapped.py

# Step 4: Predict timeframes
python step5_refine_timeframes.py

# Step 5: Import to Cloudflare D1
python step4_import_to_d1.py
```

### Expected Outputs

```
data/pipeline/output/
├── anzsco_onet_mapping.csv      # Step 1 output
├── merged_anthropic_data.json   # Step 2 output
├── generated_tasks.json         # Step 3 output
├── taskfolio_master_data.json   # Step 4-5 output (PROPRIETARY)
└── batch_*.json                 # Intermediate checkpoints
```

### Cost Estimate

| Step | API Calls | Est. Cost |
|------|-----------|-----------|
| Step 3 (task generation) | 214 × ~2000 tokens | ~$15 |
| Step 4 (timeframe prediction) | 6,690 × ~500 tokens | ~$25 |
| **Total** | | **~$40** |

---

## Citation

If you use this methodology in research, please cite:

```bibtex
@software{taskfolio_methodology_2026,
  author = {Setiyaputra, Surya},
  title = {TaskFolio: Task-level AI Exposure Methodology for Australian Occupations},
  year = {2026},
  version = {1.0},
  url = {https://github.com/suryast/task-folio/blob/main/docs/METHODOLOGY.md}
}
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-21 | Initial release |

---

## Contact

- **Issues:** [GitHub Issues](https://github.com/suryast/task-folio/issues)
- **Email:** surya@setiyaputra.me
