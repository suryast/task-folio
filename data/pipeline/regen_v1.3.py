#!/usr/bin/env python3
"""
V1.3 Regeneration: Replace synthetic tasks with O*NET-backed tasks
for 174 occupations that now have verified SOC mappings.

Uses Claude to generate AU-specific tasks informed by the O*NET mapping.
Source tag: 'onet' (empirical, backed by verified O*NET crosswalk).
"""

import json
import os
import subprocess
import time
import csv
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / 'output'

# Load Anthropic API key from pass
API_KEY = subprocess.check_output(["pass", "show", "anthropic/api-key"]).decode().strip()

# Load O*NET occupation data for context
ONET_DATA = {}
onet_path = Path('/tmp/onet_occupations.txt')
if onet_path.exists():
    with open(onet_path) as f:
        for row in csv.DictReader(f, delimiter='\t'):
            ONET_DATA[row['O*NET-SOC Code']] = {
                'title': row['Title'],
                'description': row.get('Description', '')
            }


def generate_tasks(anzsco_code: str, title: str, soc_code: str, confidence: float) -> list:
    """Generate AU-specific tasks using Claude, informed by O*NET mapping."""
    
    onet_info = ONET_DATA.get(soc_code, {})
    onet_title = onet_info.get('title', 'Unknown')
    onet_desc = onet_info.get('description', '')
    
    prompt = f"""You are an occupational analyst creating task breakdowns for Australian jobs.

## Occupation
Australian Title: {title}
ANZSCO Code: {anzsco_code}
Mapped O*NET Equivalent: {onet_title} (SOC {soc_code}, confidence: {confidence:.0%})
O*NET Description: {onet_desc}

## Instructions
Generate 15-20 specific tasks for this AUSTRALIAN occupation. For each task:

1. Write a clear, actionable task description (1-2 sentences)
2. Estimate AI automation potential (0.0-1.0) — can AI fully replace human?
3. Estimate AI augmentation potential (0.0-1.0) — can AI assist humans?
4. Predict timeframe: "now", "1-2y", "3-5y", "5-10y", or "10y+"
5. Consider Australian context (AU regulations, licensing, industry norms)

## Important
- Tasks must reflect the AUSTRALIAN version of this role
- Use Australian terminology and regulatory context (TGA, ASIC, APRA, Privacy Act, Fair Work, SafeWork, state licensing)
- Be specific — real tasks, not vague descriptions
- Consider physical vs cognitive aspects
- Do NOT include tasks from the O*NET description verbatim — adapt for AU context

## Output Format (JSON only, no markdown)
{{
  "tasks": [
    {{
      "description": "...",
      "automation_pct": 0.XX,
      "augmentation_pct": 0.XX,
      "timeframe": "now|1-2y|3-5y|5-10y|10y+"
    }}
  ]
}}"""

    import urllib.request
    
    data = json.dumps({
        "model": "claude-sonnet-4-5-20250514",
        "thinking": {"type": "disabled"},
        "max_tokens": 4000,
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    )
    
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        text = result['content'][0]['text']
        
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            parsed = json.loads(text[start:end])
            return parsed.get('tasks', [])
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []
    
    return []


def main():
    # Load targets
    with open(OUTPUT_DIR / 'regen_targets.json') as f:
        targets = json.load(f)
    
    print(f"=== V1.3 Task Regeneration ===")
    print(f"Occupations to process: {len(targets)}")
    print(f"O*NET reference data: {len(ONET_DATA)} occupations\n")
    
    all_tasks = {}  # anzsco_code -> [tasks]
    success = 0
    failed = 0
    
    for i, occ in enumerate(targets):
        code = str(occ['anzsco_code'])
        title = occ['title']
        soc = occ['onet_code']
        conf = occ['mapping_confidence']
        
        print(f"[{i+1}/{len(targets)}] {code} {title} → {soc} ({conf:.0%})")
        
        tasks = generate_tasks(code, title, soc, conf)
        
        if tasks:
            # Add source metadata
            for t in tasks:
                t['source'] = 'onet'
            all_tasks[code] = tasks
            success += 1
            print(f"  ✅ {len(tasks)} tasks")
        else:
            failed += 1
            print(f"  ❌ Failed")
        
        # Rate limiting - be gentle
        if (i + 1) % 10 == 0:
            print(f"  ... {success} success, {failed} failed so far ...")
            time.sleep(1)
        else:
            time.sleep(0.3)
    
    # Save results
    output_path = OUTPUT_DIR / 'regen_v1.3_tasks.json'
    with open(output_path, 'w') as f:
        json.dump(all_tasks, f, indent=2)
    
    total_tasks = sum(len(t) for t in all_tasks.values())
    print(f"\n=== Complete ===")
    print(f"Success: {success}/{len(targets)}")
    print(f"Failed: {failed}")
    print(f"Total tasks generated: {total_tasks}")
    print(f"Saved to {output_path}")
    
    # Generate SQL for import
    sql_path = OUTPUT_DIR / 'regen_v1.3_import.sql'
    sql_lines = []
    
    for code, tasks in all_tasks.items():
        # Delete old synthetic tasks
        sql_lines.append(
            f"DELETE FROM tasks WHERE occupation_id = "
            f"(SELECT id FROM occupations WHERE anzsco_code = '{code}') "
            f"AND source = 'synthetic';"
        )
        
        # Insert new tasks
        for t in tasks:
            desc = t['description'].replace("'", "''")
            auto = t.get('automation_pct', 0)
            aug = t.get('augmentation_pct', 0)
            timeframe = t.get('timeframe', 'unknown')
            score = round((auto + aug) * 100)
            freq = 'as_needed'
            freq_weight = 0.1
            
            sql_lines.append(
                f"INSERT INTO tasks (occupation_id, description, automation_pct, augmentation_pct, "
                f"frequency, frequency_weight, timeframe, taskfolio_score, source) VALUES ("
                f"(SELECT id FROM occupations WHERE anzsco_code = '{code}'), "
                f"'{desc}', {auto}, {aug}, '{freq}', {freq_weight}, '{timeframe}', {score}, 'onet');"
            )
    
    with open(sql_path, 'w') as f:
        f.write('\n'.join(sql_lines))
    
    print(f"SQL import file: {sql_path} ({len(sql_lines)} statements)")


if __name__ == '__main__':
    main()
