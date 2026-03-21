#!/usr/bin/env python3
"""
Re-generate tasks for occupations that had bad SOC mappings.

These 68 occupations had tasks generated from wrong US occupations
(e.g., Fencers → Dancers). Now with correct ISCO-based mapping,
we regenerate tasks using the correct SOC codes.
"""

import json
import os
import anthropic
from pathlib import Path
import time

OUTPUT_DIR = Path(__file__).parent / 'output'
CROSSWALK_DIR = Path(__file__).parent.parent / 'crosswalks'

# Anthropic client
client = anthropic.Anthropic()

def get_mismatched_occupations():
    """Get list of occupations that need re-generation."""
    import pandas as pd
    
    old = pd.read_csv(OUTPUT_DIR / 'anzsco_onet_mapping.csv')
    new = pd.read_csv(CROSSWALK_DIR / 'anzsco_to_soc_improved.csv')
    
    changes = []
    for _, old_row in old.iterrows():
        anzsco = str(old_row['anzsco_code'])
        new_rows = new[new['anzsco_code'].astype(str) == anzsco]
        
        if len(new_rows) > 0:
            new_soc = new_rows.iloc[0]['soc_code']
            old_soc = old_row['onet_soc_code'][:7] if pd.notna(old_row['onet_soc_code']) else None
            
            if old_soc != new_soc and old_row['confidence'] < 0.85:
                changes.append({
                    'anzsco_code': anzsco,
                    'anzsco_title': old_row['anzsco_title'],
                    'old_soc': old_soc,
                    'new_soc': new_soc,
                    'old_confidence': old_row['confidence']
                })
    
    return changes

def generate_tasks_for_occupation(anzsco_code: str, title: str, soc_code: str) -> list:
    """Generate AU-specific tasks using Claude."""
    
    prompt = f"""You are an occupational analyst creating task breakdowns for Australian jobs.

## Occupation
Title: {title}
ANZSCO Code: {anzsco_code}
Related US SOC Code: {soc_code}

## Instructions
Generate 15-20 specific tasks for this Australian occupation. For each task:

1. Write a clear, actionable task description (1-2 sentences)
2. Estimate AI automation potential (0.0-1.0) - can AI fully do this without human?
3. Estimate AI augmentation potential (0.0-1.0) - can AI assist humans doing this?
4. Predict timeframe for AI impact: "now", "1-2y", "3-5y", "5-10y", or "10y+"
5. Consider Australian regulatory context (TGA, ASIC, APRA, Privacy Act, state licensing)

## Important
- Focus on Australian context, not US
- Be specific about actual tasks, not vague descriptions
- Consider physical vs cognitive aspects

## Output Format (JSON only, no markdown)
{{
  "tasks": [
    {{
      "description": "...",
      "automation_pct": 0.XX,
      "augmentation_pct": 0.XX,
      "timeframe": "now|1-2y|3-5y|5-10y|10y+",
      "source": "regenerated_v1.2"
    }}
  ]
}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=4000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        text = response.content[0].text
        # Find JSON in response
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            return data.get('tasks', [])
    except Exception as e:
        print(f"  Error generating tasks: {e}")
        return []
    
    return []

def main():
    print("=== Re-generating Tasks for Mis-mapped Occupations ===\n")
    
    # Get list of occupations to regenerate
    mismatched = get_mismatched_occupations()
    print(f"Occupations to regenerate: {len(mismatched)}\n")
    
    # Load existing tasks
    tasks_cache_path = OUTPUT_DIR / 'tasks_cache.json'
    with open(tasks_cache_path) as f:
        all_tasks = json.load(f)
    
    # Index by anzsco
    tasks_by_anzsco = {}
    for task in all_tasks:
        anzsco = str(task.get('anzsco_code', ''))
        if anzsco not in tasks_by_anzsco:
            tasks_by_anzsco[anzsco] = []
        tasks_by_anzsco[anzsco].append(task)
    
    # Track progress
    regenerated = 0
    failed = 0
    new_tasks = []
    
    for i, occ in enumerate(mismatched):
        anzsco = occ['anzsco_code']
        title = occ['anzsco_title']
        new_soc = occ['new_soc']
        
        print(f"[{i+1}/{len(mismatched)}] {anzsco} {title}")
        print(f"  Old SOC: {occ['old_soc']} ({occ['old_confidence']:.0%}) → New SOC: {new_soc}")
        
        # Generate new tasks
        tasks = generate_tasks_for_occupation(anzsco, title, new_soc)
        
        if tasks:
            print(f"  Generated {len(tasks)} tasks")
            
            # Add metadata
            for task in tasks:
                task['anzsco_code'] = anzsco
                task['occupation_title'] = title
                task['soc_code'] = new_soc
                new_tasks.append(task)
            
            # Remove old tasks for this occupation
            tasks_by_anzsco[anzsco] = tasks
            regenerated += 1
        else:
            print(f"  FAILED - keeping old tasks")
            failed += 1
        
        # Rate limiting
        time.sleep(0.5)
    
    # Rebuild all_tasks from tasks_by_anzsco
    updated_tasks = []
    for anzsco, tasks in tasks_by_anzsco.items():
        updated_tasks.extend(tasks)
    
    # Save updated tasks
    output_path = OUTPUT_DIR / 'tasks_regenerated.json'
    with open(output_path, 'w') as f:
        json.dump(updated_tasks, f, indent=2)
    
    print(f"\n=== Summary ===")
    print(f"Regenerated: {regenerated}")
    print(f"Failed: {failed}")
    print(f"Total tasks: {len(updated_tasks)}")
    print(f"\nSaved to: {output_path}")

if __name__ == '__main__':
    main()
