"""
Step 2: Merge Anthropic Economic Index datasets and filter to mapped ANZSCO occupations.
Output: data/pipeline/output/taskfolio_master_data.json
"""

from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path(__file__).parent / 'output'
ANTHROPIC_DIR = Path(__file__).parent.parent.parent / 'anthropic-data'


def main():
    print("Loading Anthropic datasets...")
    datasets = {
        'tasks': pd.read_csv(ANTHROPIC_DIR / 'onet_task_statements.csv'),
        'automation': pd.read_csv(ANTHROPIC_DIR / 'automation_vs_augmentation_by_task.csv'),
        'primitives': pd.read_csv(ANTHROPIC_DIR / 'economic_primitives_by_task.csv'),
        'usage': pd.read_csv(ANTHROPIC_DIR / 'task_pct_v2.csv'),
        'wages': pd.read_csv(ANTHROPIC_DIR / 'wage_data.csv'),
        'employment': pd.read_csv(ANTHROPIC_DIR / 'bls_employment_may_2023.csv'),
    }
    for name, df in datasets.items():
        print(f"  {name}: {len(df)} rows")

    # Merge task-level data
    print("\nMerging...")
    master = datasets['tasks'].copy()
    for key in ['automation', 'primitives', 'usage']:
        master = master.merge(datasets[key], on='task_id', how='left', suffixes=('', f'_{key}'))
    # Merge occupation-level data
    for key in ['wages', 'employment']:
        master = master.merge(datasets[key], on='onet_soc_code', how='left', suffixes=('', f'_{key}'))
    print(f"  Merged: {len(master)} tasks")

    # Filter to mapped ANZSCO occupations
    print("\nFiltering to ANZSCO...")
    mapping = pd.read_csv(OUTPUT_DIR / 'anzsco_onet_mapping.csv')
    filtered = master.merge(
        mapping[['onet_soc_code', 'anzsco_code', 'anzsco_title', 'confidence']],
        on='onet_soc_code', how='inner'
    )
    print(f"  {len(filtered)} tasks from {filtered['anzsco_code'].nunique()} occupations")

    # Validate
    print("\nValidating...")
    for col in ['task_description', 'automation_pct', 'success_rate']:
        if col in filtered.columns:
            nulls = filtered[col].isnull().sum()
            status = '✅' if nulls == 0 else '⚠️'
            print(f"  {status} {col}: {nulls} NULLs")

    # Save
    output = OUTPUT_DIR / 'taskfolio_master_data.json'
    filtered.to_json(output, orient='records', indent=2)
    print(f"\n✅ Saved to {output}")


if __name__ == '__main__':
    main()
