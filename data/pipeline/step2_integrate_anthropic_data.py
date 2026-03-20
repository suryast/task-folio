"""
Step 2: Merge Anthropic Economic Index datasets and filter to mapped ANZSCO occupations.
Output: data/pipeline/output/taskfolio_master_data.json

Actual column names from Anthropic:
  onet_task_statements.csv: O*NET-SOC Code, Title, Task ID, Task, Task Type
  automation_vs_augmentation_by_task.csv: task_name, feedback_loop, directive, task_iteration, validation, learning, filtered
  task_pct_v2.csv: task_name, pct
  job_exposure.csv: occ_code, title, observed_exposure
  task_penetration.csv: task, penetration
"""

from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path(__file__).parent / 'output'
ANTHROPIC_DIR = Path.home() / 'projects' / 'anthropic-data'


def main():
    print("Loading Anthropic datasets...")

    # Core task data
    tasks = pd.read_csv(ANTHROPIC_DIR / 'onet_task_statements.csv')
    tasks = tasks.rename(columns={
        'O*NET-SOC Code': 'onet_soc_code',
        'Title': 'occupation_title',
        'Task ID': 'task_id',
        'Task': 'task_description',
        'Task Type': 'task_type',
    })
    print(f"  Tasks: {len(tasks)} rows, {tasks['onet_soc_code'].nunique()} occupations")

    # Automation/augmentation
    auto = pd.read_csv(ANTHROPIC_DIR / 'automation_vs_augmentation_by_task.csv')
    auto = auto.rename(columns={'task_name': 'task_lower'})
    print(f"  Automation: {len(auto)} rows")

    # Task usage percentage
    usage = pd.read_csv(ANTHROPIC_DIR / 'task_pct_v2.csv')
    usage = usage.rename(columns={'task_name': 'task_lower', 'pct': 'usage_pct'})
    print(f"  Usage: {len(usage)} rows")

    # Job-level exposure
    exposure = pd.read_csv(ANTHROPIC_DIR / 'job_exposure.csv')
    # occ_code is like "11-1011" (no .00 suffix)
    print(f"  Exposure: {len(exposure)} rows")

    # Task penetration
    penetration = pd.read_csv(ANTHROPIC_DIR / 'task_penetration.csv')
    penetration = penetration.rename(columns={'task': 'task_lower'})
    print(f"  Penetration: {len(penetration)} rows")

    # Create lowercase task column for joining
    tasks['task_lower'] = tasks['task_description'].str.lower().str.strip()

    # Merge task-level data
    print("\nMerging task-level data...")
    master = tasks.copy()
    master = master.merge(auto, on='task_lower', how='left')
    master = master.merge(usage, on='task_lower', how='left')
    master = master.merge(penetration, on='task_lower', how='left')

    # Merge occupation-level exposure
    # Create shortened code for matching (remove .00 suffix)
    master['occ_code_short'] = master['onet_soc_code'].str.replace(r'\.\d+$', '', regex=True)
    master = master.merge(exposure, left_on='occ_code_short', right_on='occ_code', how='left')

    print(f"  Merged: {len(master)} tasks")

    # Filter to mapped ANZSCO occupations
    print("\nFiltering to ANZSCO...")
    mapping = pd.read_csv(OUTPUT_DIR / 'anzsco_onet_mapping.csv')
    mapping['onet_soc_code'] = mapping['onet_soc_code'].astype(str)
    master['onet_soc_code'] = master['onet_soc_code'].astype(str)

    filtered = master.merge(
        mapping[['onet_soc_code', 'anzsco_code', 'anzsco_title', 'confidence']],
        on='onet_soc_code', how='inner'
    )
    print(f"  {len(filtered)} tasks from {filtered['anzsco_code'].nunique()} ANZSCO occupations")

    # Calculate automation percentage
    if 'directive' in filtered.columns:
        filtered['automation_pct'] = filtered['directive'].fillna(0)
        filtered['augmentation_pct'] = 1 - filtered['automation_pct']

    # Add source tag
    filtered['source'] = 'anthropic'

    # Select clean columns
    keep_cols = [
        'anzsco_code', 'anzsco_title', 'onet_soc_code', 'occupation_title',
        'task_id', 'task_description', 'task_type',
        'automation_pct', 'augmentation_pct',
        'usage_pct', 'penetration', 'observed_exposure',
        'feedback_loop', 'directive', 'task_iteration', 'validation', 'learning',
        'confidence', 'source'
    ]
    available_cols = [c for c in keep_cols if c in filtered.columns]
    output = filtered[available_cols].copy()

    # Validate
    print("\nValidating...")
    for col in ['task_description', 'automation_pct', 'usage_pct', 'penetration']:
        if col in output.columns:
            nulls = output[col].isnull().sum()
            pct = nulls / len(output) * 100
            status = '✅' if pct < 20 else '⚠️'
            print(f"  {status} {col}: {nulls} NULLs ({pct:.1f}%)")

    # Stats
    print(f"\n📊 Summary:")
    print(f"  Tasks per occupation: {len(output) / output['anzsco_code'].nunique():.1f} avg")
    if 'automation_pct' in output.columns:
        print(f"  Avg automation: {output['automation_pct'].mean():.3f}")
    if 'usage_pct' in output.columns:
        print(f"  Avg usage pct: {output['usage_pct'].mean():.4f}")

    # Save
    out_path = OUTPUT_DIR / 'taskfolio_master_data.json'
    output.to_json(out_path, orient='records', indent=2)
    print(f"\n✅ Saved {len(output)} tasks to {out_path}")


if __name__ == '__main__':
    main()
