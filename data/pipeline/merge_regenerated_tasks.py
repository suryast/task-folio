#!/usr/bin/env python3
"""
Merge regenerated tasks into the main tasks cache and prepare for D1 import.
"""

import json
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / 'output'

def main():
    # Load existing tasks
    with open(OUTPUT_DIR / 'tasks_cache.json') as f:
        all_tasks = json.load(f)
    
    print(f"Original tasks: {len(all_tasks)}")
    
    # Load regenerated tasks
    with open(OUTPUT_DIR / 'regenerated_tasks.json') as f:
        regenerated = json.load(f)
    
    print(f"Regenerated tasks: {len(regenerated)}")
    
    # Get list of ANZSCO codes that were regenerated
    regenerated_codes = set(t['anzsco_code'] for t in regenerated)
    print(f"Occupations regenerated: {len(regenerated_codes)}")
    
    # Remove old tasks for regenerated occupations
    filtered_tasks = [t for t in all_tasks if str(t.get('anzsco_code', '')) not in regenerated_codes]
    print(f"After removing old: {len(filtered_tasks)}")
    
    # Add regenerated tasks
    merged = filtered_tasks + regenerated
    print(f"After merge: {len(merged)}")
    
    # Save merged tasks
    with open(OUTPUT_DIR / 'tasks_merged.json', 'w') as f:
        json.dump(merged, f, indent=2)
    
    # Also save as tasks_cache.json (backup original first)
    import shutil
    shutil.copy(OUTPUT_DIR / 'tasks_cache.json', OUTPUT_DIR / 'tasks_cache_backup.json')
    with open(OUTPUT_DIR / 'tasks_cache.json', 'w') as f:
        json.dump(merged, f, indent=2)
    
    print(f"\nMerged saved to: tasks_merged.json")
    print(f"Updated: tasks_cache.json (backup: tasks_cache_backup.json)")

if __name__ == '__main__':
    main()
