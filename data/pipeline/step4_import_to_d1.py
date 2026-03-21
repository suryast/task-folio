"""
Step 4: Import master data to Cloudflare D1.
Loads taskfolio_master_data.json and inserts 361 occupations + 6,690 tasks.

Usage:
  cd ~/projects/task-folio/data/pipeline
  python3 step4_import_to_d1.py
"""

import json
import subprocess
import tempfile
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path(__file__).parent / 'output'
MASTER_DATA = OUTPUT_DIR / 'taskfolio_master_data.json'
YCHUA_DATA = Path.home() / 'projects' / 'ychua-jobs' / 'site' / 'data.json'
MAPPING_FILE = OUTPUT_DIR / 'anzsco_onet_mapping.csv'


def escape_sql(s):
    """Escape single quotes for SQL."""
    if s is None:
        return 'NULL'
    return "'" + str(s).replace("'", "''") + "'"


def main():
    print("Loading data...")
    
    # Load master task data
    with open(MASTER_DATA) as f:
        tasks = json.load(f)
    print(f"  {len(tasks)} tasks loaded")
    
    # Load ANZSCO metadata
    with open(YCHUA_DATA) as f:
        anzsco_data = json.load(f)
    anzsco_meta = {o['slug'].split('-')[0]: o for o in anzsco_data}
    
    # Load mapping for O*NET codes and confidence
    import pandas as pd
    mapping = pd.read_csv(MAPPING_FILE)
    mapping_dict = {str(row['anzsco_code']): (row['onet_soc_code'], row['confidence']) 
                    for _, row in mapping.iterrows()}
    
    # Group tasks by occupation
    tasks_by_occ = defaultdict(list)
    for task in tasks:
        code = str(task['anzsco_code'])
        tasks_by_occ[code].append(task)
    
    print(f"  {len(tasks_by_occ)} unique occupations")
    
    # Generate SQL
    sql_lines = []
    
    # Insert occupations
    print("\nGenerating occupation inserts...")
    for code, occ_tasks in sorted(tasks_by_occ.items()):
        title = occ_tasks[0]['anzsco_title']
        meta = anzsco_meta.get(code, {})
        onet_code, confidence = mapping_dict.get(code, (None, None))
        source = occ_tasks[0].get('source', 'unknown')
        
        employment = meta.get('jobs', 0)
        pay = meta.get('pay', 0)
        outlook = meta.get('outlook_desc', '')
        education = meta.get('education', '')
        
        sql_lines.append(
            f"INSERT INTO occupations (anzsco_code, title, employment, median_pay_aud, "
            f"outlook, education, onet_code, mapping_confidence, source) VALUES ("
            f"{escape_sql(code)}, {escape_sql(title)}, {employment}, {pay}, "
            f"{escape_sql(outlook)}, {escape_sql(education)}, "
            f"{escape_sql(onet_code)}, {confidence if confidence else 'NULL'}, "
            f"{escape_sql(source)});"
        )
    
    # Insert tasks
    print("Generating task inserts...")
    for code, occ_tasks in sorted(tasks_by_occ.items()):
        for task in occ_tasks:
            desc = task.get('task_description', '').replace('\n', ' ')
            automation = task.get('automation_pct')
            augmentation = task.get('augmentation_pct')
            frequency = task.get('frequency', 'as_needed')
            timeframe = task.get('timeframe', 'unknown')
            ai_exposure = task.get('ai_exposure_estimate', 50)
            task_type = task.get('task_type', 'Core')
            source = task.get('source', 'unknown')
            onet_task_id = task.get('task_id')
            
            # Frequency weight mapping
            freq_weight_map = {
                'daily': 1.0,
                'weekly': 0.5,
                'monthly': 0.2,
                'as_needed': 0.1
            }
            freq_weight = freq_weight_map.get(frequency, 0.3)
            
            sql_lines.append(
                f"INSERT INTO tasks (occupation_id, onet_task_id, description, "
                f"automation_pct, augmentation_pct, frequency, frequency_weight, "
                f"timeframe, taskfolio_score, source) VALUES ("
                f"(SELECT id FROM occupations WHERE anzsco_code = {escape_sql(code)}), "
                f"{escape_sql(onet_task_id)}, {escape_sql(desc)}, "
                f"{automation if automation is not None else 'NULL'}, "
                f"{augmentation if augmentation is not None else 'NULL'}, "
                f"{escape_sql(frequency)}, {freq_weight}, "
                f"{escape_sql(timeframe)}, {ai_exposure}, "
                f"{escape_sql(source)});"
            )
    
    print(f"\nGenerated {len(sql_lines)} SQL statements")
    
    # Write to temp file (D1 doesn't support explicit transactions)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write('\n'.join(sql_lines))
        temp_path = f.name
    
    print(f"Wrote SQL to {temp_path}")
    
    # Execute via wrangler
    print("\nExecuting import...")
    result = subprocess.run([
        'bash', '-c',
        f'cd ~/projects/task-folio/api && '
        f'CLOUDFLARE_API_TOKEN=$(pass cloudflare/api-token) '
        f'wrangler d1 execute taskfolio-au --file={temp_path} --remote'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Error:")
        print(result.stderr)
        return 1
    
    print(result.stdout)
    
    # Verify
    print("\nVerifying import...")
    verify_sql = "SELECT COUNT(*) as count FROM occupations; SELECT COUNT(*) as count FROM tasks;"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write(verify_sql)
        verify_path = f.name
    
    result = subprocess.run([
        'bash', '-c',
        f'cd ~/projects/task-folio/api && '
        f'CLOUDFLARE_API_TOKEN=$(pass cloudflare/api-token) '
        f'wrangler d1 execute taskfolio-au --file={verify_path} --remote'
    ], capture_output=True, text=True)
    
    print(result.stdout)
    
    print("\n✅ Import complete!")


if __name__ == '__main__':
    main()
