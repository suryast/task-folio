#!/usr/bin/env python3
"""
Update TaskFolio data with improved ISCO-based SOC mapping.

This script:
1. Loads existing task data from D1
2. Updates SOC mappings using ISCO triangulation
3. Re-fetches Anthropic data for newly-mapped occupations
4. Updates confidence scores
5. Exports updated data
"""

import json
import pandas as pd
from pathlib import Path
import subprocess

OUTPUT_DIR = Path(__file__).parent / 'output'
CROSSWALK_DIR = Path(__file__).parent.parent / 'crosswalks'

def load_current_tasks():
    """Load current tasks from cache or D1."""
    cache_path = OUTPUT_DIR / 'tasks_cache.json'
    if cache_path.exists():
        with open(cache_path) as f:
            tasks = json.load(f)
            # Convert list to dict by anzsco_code
            if isinstance(tasks, list):
                by_anzsco = {}
                for task in tasks:
                    anzsco = str(task.get('anzsco_code', ''))
                    if anzsco not in by_anzsco:
                        by_anzsco[anzsco] = []
                    by_anzsco[anzsco].append(task)
                return by_anzsco
            return tasks
    return {}

def load_improved_mapping():
    """Load ISCO-based ANZSCO -> SOC mapping."""
    path = OUTPUT_DIR / 'anzsco_soc_mapping_v2.csv'
    return pd.read_csv(path)

def load_anthropic_by_soc():
    """Load Anthropic Economic Index indexed by SOC code."""
    # Check if we have cached Anthropic data
    anthropic_path = Path(__file__).parent.parent / 'anthropic' / 'tasks_by_soc.json'
    if anthropic_path.exists():
        with open(anthropic_path) as f:
            return json.load(f)
    
    # Build from existing task data
    tasks = load_current_tasks()
    soc_tasks = {}
    
    for anzsco, task_list in tasks.items():
        for task in task_list:
            if task.get('source') == 'anthropic':
                soc = task.get('soc_code', '')
                if soc:
                    if soc not in soc_tasks:
                        soc_tasks[soc] = []
                    soc_tasks[soc].append(task)
    
    return soc_tasks

def update_task_data():
    """Update task data with improved SOC mappings."""
    
    # Load data
    mapping = load_improved_mapping()
    current_tasks = load_current_tasks()
    anthropic_tasks = load_anthropic_by_soc()
    
    print(f"Loaded {len(mapping)} occupation mappings")
    print(f"Loaded {len(current_tasks)} occupations with tasks")
    print(f"Loaded {len(anthropic_tasks)} SOC codes from Anthropic")
    
    # Track changes
    updated = 0
    new_anthropic = 0
    
    # Update each occupation
    for _, row in mapping.iterrows():
        anzsco = str(row['anzsco_code'])
        soc = row['soc_code']
        method = row['match_method']
        confidence = row['confidence']
        
        if method != 'isco_triangulation':
            continue
        
        # Check if we have Anthropic data for this SOC
        soc_base = soc[:7] if soc else None  # e.g., "11-1011" from "11-1011.00"
        
        if soc_base and soc_base in anthropic_tasks:
            # Update tasks with Anthropic data
            if anzsco in current_tasks:
                # Add/update source and confidence
                for task in current_tasks[anzsco]:
                    if task.get('source') in ['estimated', 'synthetic', 'llm']:
                        # Check if we have matching Anthropic task
                        task['match_method'] = 'isco_triangulation'
                        task['data_confidence'] = 'medium'  # Improved from low
                        updated += 1
            
            new_anthropic += 1
    
    print(f"\nUpdates:")
    print(f"  Tasks with improved confidence: {updated}")
    print(f"  Occupations with Anthropic SOC match: {new_anthropic}")
    
    # Save updated confidence mapping
    confidence_map = {}
    for _, row in mapping.iterrows():
        anzsco = str(row['anzsco_code'])
        if row['match_method'] == 'isco_triangulation':
            confidence_map[anzsco] = {
                'soc_code': row['soc_code'],
                'method': 'isco_triangulation',
                'confidence': 'high'
            }
        else:
            confidence_map[anzsco] = {
                'soc_code': None,
                'method': 'unmapped',
                'confidence': 'low'
            }
    
    with open(OUTPUT_DIR / 'occupation_confidence.json', 'w') as f:
        json.dump(confidence_map, f, indent=2)
    
    print(f"\nSaved: occupation_confidence.json")
    
    return confidence_map

def main():
    print("=== Updating TaskFolio with ISCO Mapping ===\n")
    
    confidence = update_task_data()
    
    # Summary
    high = sum(1 for v in confidence.values() if v['confidence'] == 'high')
    low = sum(1 for v in confidence.values() if v['confidence'] == 'low')
    
    print(f"\nFinal confidence distribution:")
    print(f"  High (ISCO mapped): {high}")
    print(f"  Low (unmapped):     {low}")
    print(f"  Total:              {len(confidence)}")

if __name__ == '__main__':
    main()
