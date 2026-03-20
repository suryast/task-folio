"""
Step 3: Generate tasks for unmapped ANZSCO occupations using Claude Haiku 4.5.
Output: Appends to data/pipeline/output/taskfolio_master_data.json
"""

import os
import json
import time
from pathlib import Path
from anthropic import Anthropic
import pandas as pd

OUTPUT_DIR = Path(__file__).parent / 'output'

PROMPT = """You are an expert in Australian occupational analysis. Break down this occupation into 8-12 core tasks.

Occupation: {title}
ANZSCO Code: {code}

For each task, return JSON:
{{
  "tasks": [
    {{
      "description": "Specific task description (1-2 sentences)",
      "frequency": "high|medium|low",
      "ai_exposure_estimate": 75
    }}
  ]
}}

Focus on concrete, observable tasks. Return ONLY valid JSON."""


def main():
    client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

    with open(OUTPUT_DIR / 'unmapped_occupations.json') as f:
        unmapped = json.load(f)
    print(f"Loaded {len(unmapped)} unmapped occupations")

    generated = []
    cost = 0

    for i, occ in enumerate(unmapped, 1):
        print(f"[{i}/{len(unmapped)}] {occ['name']}")
        try:
            msg = client.messages.create(
                model='claude-haiku-4.5-20250514',
                max_tokens=2000,
                messages=[{'role': 'user', 'content': PROMPT.format(title=occ['name'], code=occ['code'])}]
            )
            result = json.loads(msg.content[0].text)
            generated.append({
                'anzsco_code': occ['code'],
                'anzsco_title': occ['name'],
                'tasks': result['tasks'],
                'source': 'claude_generated'
            })
            print(f"  ✅ {len(result['tasks'])} tasks")
            cost += 0.0005
        except Exception as e:
            print(f"  ❌ {e}")

        if i % 10 == 0:
            time.sleep(5)

    # Save generated
    with open(OUTPUT_DIR / 'generated_tasks.json', 'w') as f:
        json.dump(generated, f, indent=2)

    # Convert and append to master data
    rows = []
    for g in generated:
        for task in g['tasks']:
            rows.append({
                'anzsco_code': g['anzsco_code'],
                'anzsco_title': g['anzsco_title'],
                'task_description': task['description'],
                'frequency': task['frequency'],
                'ai_exposure_estimate': task['ai_exposure_estimate'],
                'source': 'claude_generated',
            })

    df_gen = pd.DataFrame(rows)
    df_master = pd.read_json(OUTPUT_DIR / 'taskfolio_master_data.json')
    df_combined = pd.concat([df_master, df_gen], ignore_index=True)
    df_combined.to_json(OUTPUT_DIR / 'taskfolio_master_data.json', orient='records', indent=2)

    print(f"\n✅ Done: {len(generated)} occupations, {sum(len(g['tasks']) for g in generated)} tasks")
    print(f"  Cost: ~${cost:.2f}")
    print(f"  Total tasks now: {len(df_combined)}")


if __name__ == '__main__':
    main()
