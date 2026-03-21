"""
Step 3: Generate tasks for unmapped ANZSCO occupations using Claude Sonnet 4.5.
Output: data/pipeline/output/generated_tasks.json + appends to taskfolio_master_data.json

Uses Sonnet for higher quality task decomposition with automation scoring.
"""

import os
import json
import time
from pathlib import Path
from anthropic import Anthropic
import pandas as pd

OUTPUT_DIR = Path(__file__).parent / 'output'

SYSTEM_PROMPT = """You are an expert in Australian labour market analysis specialising in AI impact assessment.
You have deep knowledge of ANZSCO occupation classifications and how AI/LLMs are transforming work in Australia.
Your task decompositions are used to help workers understand which specific parts of their job AI will affect."""

PROMPT = """Decompose this Australian occupation into 15-20 specific, observable tasks.

**Occupation:** {title}
**ANZSCO Code:** {code}
**Category:** {category}
**Annual Pay:** ${pay:,}
**Employment:** {jobs:,} workers

For EACH task, assess:
1. **description** — Concrete, observable task (1-2 sentences). Be specific to this occupation, not generic.
2. **task_type** — "Core" (essential to role) or "Supplemental" (supporting/administrative)
3. **automation_pct** — 0.0 to 1.0: How much of this task can AI fully automate (no human needed)?
4. **augmentation_pct** — 0.0 to 1.0: How much can AI augment (human still needed but faster/better)?
   Note: automation_pct + augmentation_pct should not exceed 1.0
5. **ai_exposure_estimate** — 0-100: Overall AI exposure score for this task
6. **timeframe** — "now" (already happening), "1-2y", "3-5y", "5-10y", "10y+" (when AI impact is likely)
7. **frequency** — "daily", "weekly", "monthly", "as_needed"

Return ONLY valid JSON:
{{
  "tasks": [
    {{
      "description": "...",
      "task_type": "Core",
      "automation_pct": 0.15,
      "augmentation_pct": 0.45,
      "ai_exposure_estimate": 60,
      "timeframe": "1-2y",
      "frequency": "daily"
    }}
  ]
}}

Be honest about low-exposure tasks too — physical, interpersonal, and creative tasks that AI won't replace soon.
Consider the Australian context (regulations, industry structure, geography)."""


def main():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        import subprocess
        api_key = subprocess.check_output(['pass', 'anthropic/api-key']).decode().strip()

    client = Anthropic(api_key=api_key)

    with open(OUTPUT_DIR / 'unmapped_occupations.json') as f:
        unmapped = json.load(f)
    print(f"Loaded {len(unmapped)} unmapped occupations")

    # Resume support
    checkpoint = OUTPUT_DIR / 'generated_tasks_checkpoint.json'
    if checkpoint.exists():
        with open(checkpoint) as f:
            generated = json.load(f)
        done_codes = {g['anzsco_code'] for g in generated}
        remaining = [o for o in unmapped if o['slug'].split('-')[0] not in done_codes]
        print(f"  Resuming: {len(generated)} done, {len(remaining)} remaining")
    else:
        generated = []
        remaining = unmapped
        done_codes = set()

    input_tokens = 0
    output_tokens = 0
    errors = []

    for i, occ in enumerate(remaining, len(generated) + 1):
        code = occ['slug'].split('-')[0]
        title = occ['title']
        category = occ.get('category', 'unknown')
        pay = occ.get('pay', 0)
        jobs = occ.get('jobs', 0)

        print(f"[{i}/{len(unmapped)}] {title} ({code})")
        try:
            msg = client.messages.create(
                model='claude-sonnet-4-5-20250514',
                max_tokens=4000,
                system=SYSTEM_PROMPT,
                messages=[{
                    'role': 'user',
                    'content': PROMPT.format(
                        title=title, code=code, category=category,
                        pay=pay, jobs=jobs
                    )
                }]
            )

            text = msg.content[0].text
            # Handle markdown code blocks
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]

            result = json.loads(text)
            tasks = result.get('tasks', [])

            generated.append({
                'anzsco_code': code,
                'anzsco_title': title,
                'category': category,
                'pay': pay,
                'jobs': jobs,
                'tasks': tasks,
                'source': 'claude_sonnet_generated'
            })

            input_tokens += msg.usage.input_tokens
            output_tokens += msg.usage.output_tokens
            print(f"  ✅ {len(tasks)} tasks ({msg.usage.input_tokens}+{msg.usage.output_tokens} tokens)")

        except json.JSONDecodeError as e:
            print(f"  ❌ JSON parse error: {e}")
            errors.append({'code': code, 'title': title, 'error': str(e)})
        except Exception as e:
            print(f"  ❌ {e}")
            errors.append({'code': code, 'title': title, 'error': str(e)})

        # Checkpoint every 20
        if i % 20 == 0:
            with open(checkpoint, 'w') as f:
                json.dump(generated, f, indent=2)
            print(f"  💾 Checkpoint saved ({len(generated)} occupations)")

        # Rate limit: ~50 req/min for Sonnet
        if i % 5 == 0:
            time.sleep(2)

    # Final save
    with open(OUTPUT_DIR / 'generated_tasks.json', 'w') as f:
        json.dump(generated, f, indent=2)

    # Convert to flat rows and append to master data
    rows = []
    for g in generated:
        for task in g['tasks']:
            rows.append({
                'anzsco_code': g['anzsco_code'],
                'anzsco_title': g['anzsco_title'],
                'task_description': task['description'],
                'task_type': task.get('task_type', 'Core'),
                'automation_pct': task.get('automation_pct', 0),
                'augmentation_pct': task.get('augmentation_pct', 0),
                'ai_exposure_estimate': task.get('ai_exposure_estimate', 50),
                'timeframe': task.get('timeframe', 'unknown'),
                'frequency': task.get('frequency', 'as_needed'),
                'source': 'claude_sonnet_generated',
            })

    df_gen = pd.DataFrame(rows)
    df_master = pd.read_json(OUTPUT_DIR / 'taskfolio_master_data.json')
    df_combined = pd.concat([df_master, df_gen], ignore_index=True)
    df_combined.to_json(OUTPUT_DIR / 'taskfolio_master_data.json', orient='records', indent=2)

    # Cost estimate (Sonnet 4.5: $3/MTok input, $15/MTok output)
    cost_in = input_tokens / 1_000_000 * 3
    cost_out = output_tokens / 1_000_000 * 15
    total_cost = cost_in + cost_out

    print(f"\n✅ Done: {len(generated)} occupations, {len(rows)} tasks generated")
    print(f"  Tokens: {input_tokens:,} in + {output_tokens:,} out")
    print(f"  Cost: ${total_cost:.2f} (${cost_in:.2f} in + ${cost_out:.2f} out)")
    print(f"  Total tasks in master: {len(df_combined)}")
    if errors:
        print(f"  ⚠️ {len(errors)} errors:")
        for e in errors:
            print(f"    {e['code']} {e['title']}: {e['error']}")

    # Cleanup checkpoint
    if checkpoint.exists():
        checkpoint.unlink()


if __name__ == '__main__':
    main()
