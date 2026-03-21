#!/usr/bin/env python3
"""
Import merged tasks to D1 database via Wrangler.
"""
import json
import subprocess
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / 'output'

def main():
    # Load merged tasks
    with open(OUTPUT_DIR / 'tasks_merged.json') as f:
        tasks = json.load(f)
    
    print(f"Tasks to import: {len(tasks)}")
    
    # Get unique occupation codes
    codes = set(str(t.get('anzsco_code', '')) for t in tasks)
    print(f"Occupations: {len(codes)}")
    
    # Group tasks by occupation
    by_occupation = {}
    for t in tasks:
        code = str(t.get('anzsco_code', ''))
        if code not in by_occupation:
            by_occupation[code] = []
        by_occupation[code].append(t)
    
    # Generate SQL for update
    sql_file = OUTPUT_DIR / 'update_tasks.sql'
    with open(sql_file, 'w') as f:
        # Delete existing tasks for regenerated occupations
        regen_codes = set()
        for t in tasks:
            if t.get('source') == 'regenerated_v1.2':
                regen_codes.add(str(t['anzsco_code']))
        
        if regen_codes:
            codes_str = ','.join(f"'{c}'" for c in regen_codes)
            f.write(f"DELETE FROM tasks WHERE anzsco_code IN ({codes_str});\n")
        
        # Insert new tasks
        for t in tasks:
            if t.get('source') == 'regenerated_v1.2':
                desc = t['description'].replace("'", "''")
                f.write(f"INSERT INTO tasks (anzsco_code, description, automation_pct, augmentation_pct, timeframe, source) VALUES ('{t['anzsco_code']}', '{desc}', {t['automation_pct']}, {t['augmentation_pct']}, '{t['timeframe']}', 'regenerated_v1.2');\n")
    
    print(f"SQL written to: {sql_file}")
    
    # Execute via wrangler
    print("\nExecuting SQL...")
    result = subprocess.run(
        ['npx', 'wrangler', 'd1', 'execute', 'taskfolio-au', '--remote', '--file', str(sql_file)],
        cwd=str(Path(__file__).parent.parent.parent),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ D1 import complete")
    else:
        print(f"❌ Error: {result.stderr}")
        
    print(result.stdout[:500] if result.stdout else "")

if __name__ == '__main__':
    main()
