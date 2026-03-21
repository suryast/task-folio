# Data Pipeline

Run these scripts in order to populate the D1 database.

## Prerequisites

```bash
# External data (clone alongside task-folio)
git clone https://github.com/ychua/jobs ../ychua-jobs

# Download Anthropic Economic Index from HuggingFace
# Place CSV files in ../anthropic-data/
```

## Steps

```bash
cd data/pipeline

# Step 1: ANZSCO → O*NET mapping
python step1_build_anzsco_mapping.py

# Step 2: Merge Anthropic datasets
python step2_integrate_anthropic_data.py

# Step 3: Generate tasks for unmapped occupations (needs ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY="..."
python step3_decompose_unmapped.py

# Step 4: Import to Cloudflare D1 (needs wrangler configured)
python step4_import_to_d1.py
```

## Output

All intermediate files go to `output/`:
- `anzsco_onet_mapping.csv` — 250-300 mapped occupations
- `unmapped_occupations.json` — ~100 unmapped (for step 3)
- `taskfolio_master_data.json` — Complete task dataset
- `generated_tasks.json` — Claude-generated tasks
