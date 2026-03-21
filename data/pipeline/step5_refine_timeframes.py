"""
Step 5: Refine timeframes for Anthropic tasks (currently 'unknown').
Uses Claude Sonnet to batch-predict when AI will impact each task,
with Australian context.

Usage:
  cd ~/projects/task-folio/data/pipeline
  ANTHROPIC_API_KEY=$(pass anthropic/api-key) python3 step5_refine_timeframes.py
"""

import os
import json
import subprocess
import tempfile
from anthropic import Anthropic
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / 'output'
MASTER_DATA = OUTPUT_DIR / 'taskfolio_master_data.json'

SYSTEM_PROMPT = """You are an expert in Australian labour market analysis and AI technology adoption.
You assess when AI will meaningfully impact specific job tasks, considering Australian context."""

TIMEFRAME_PROMPT = """Predict WHEN AI will meaningfully impact these Australian job tasks.

Timeframes:
- **now**: Already happening, widely adopted
- **1-2y**: Early commercial deployment, pilots underway
- **3-5y**: Mainstream adoption expected
- **5-10y**: Significant barriers (technical/regulatory/social)
- **10y+**: Fundamental constraints (embodiment/trust/complexity)

Australian context factors:
- Regulatory timelines (TGA medical AI: 3-5y, financial services: 2-3y)
- SME adoption lag (70% of AU businesses are small, slower tech uptake)
- Geographic constraints (rural internet, remote delivery challenges)
- Privacy culture (stricter than US, cautious AI adoption)

Tasks:
{tasks}

Return ONLY valid JSON:
[{{"id": 1, "timeframe": "3-5y"}}, {{"id": 2, "timeframe": "now"}}]
"""


def main():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise Exception("Set ANTHROPIC_API_KEY")
    
    client = Anthropic(api_key=api_key)
    
    # Load master data
    print("Loading master data...")
    with open(MASTER_DATA) as f:
        tasks = json.load(f)
    
    # Find tasks with unknown/missing timeframes
    unknown = [t for t in tasks if t.get('timeframe') in ('unknown', None, '')]
    print(f"  {len(unknown)} tasks need timeframes\n")
    
    if not unknown:
        print("✅ All tasks have timeframes!")
        return
    
    # Batch predict
    predictions = []
    batch_size = 50
    
    for i in range(0, len(unknown), batch_size):
        batch = unknown[i:i+batch_size]
        print(f"[{i+1}/{len(unknown)}] Batch of {len(batch)}...")
        
        # Format task list with IDs
        task_list = "\n".join([
            f"{idx+1}. {t.get('task_description', '')[:100]}... "
            f"[auto:{t.get('automation_pct', 0):.2f}, aug:{t.get('augmentation_pct', 0):.2f}]"
            for idx, t in enumerate(batch)
        ])
        
        try:
            msg = client.messages.create(
                model='claude-sonnet-4-5-20250514',
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                messages=[{'role': 'user', 'content': TIMEFRAME_PROMPT.format(tasks=task_list)}]
            )
            
            text = msg.content[0].text
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            preds = json.loads(text.strip())
            
            # Map predictions back to actual task objects
            for pred in preds:
                task_idx = pred['id'] - 1  # 1-indexed from prompt
                if 0 <= task_idx < len(batch):
                    actual_task = batch[task_idx]
                    predictions.append({
                        'task': actual_task,
                        'timeframe': pred['timeframe']
                    })
            
            print(f"  ✅ {len(preds)} predictions")
            
        except Exception as e:
            print(f"  ❌ {e}")
            continue
    
    print(f"\n✅ Generated {len(predictions)} timeframe predictions")
    
    # Update master data in memory
    for pred in predictions:
        pred['task']['timeframe'] = pred['timeframe']
    
    # Save updated master data
    with open(MASTER_DATA, 'w') as f:
        json.dump(tasks, f, indent=2)
    print(f"✅ Updated {MASTER_DATA}")
    
    # Re-import to D1
    print("\nRe-importing timeframes to D1...")
    
    # Generate UPDATE statements
    sql_lines = []
    for pred in predictions:
        task = pred['task']
        desc_escaped = task['task_description'].replace("'", "''")[:50]  # First 50 chars for matching
        sql_lines.append(
            f"UPDATE tasks SET timeframe = '{pred['timeframe']}' "
            f"WHERE description LIKE '{desc_escaped}%';"
        )
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write('\n'.join(sql_lines))
        update_path = f.name
    
    result = subprocess.run([
        'bash', '-c',
        f'cd ~/projects/task-folio/api && '
        f'CLOUDFLARE_API_TOKEN=$(pass cloudflare/api-token) '
        f'wrangler d1 execute taskfolio-au --file={update_path} --remote'
    ], capture_output=True, text=True)
    
    if 'success' in result.stdout:
        print("✅ D1 updated")
    else:
        print(f"⚠️ D1 update: {result.stdout[:200]}")
    
    # Show distribution
    print("\nTimeframe distribution:")
    from collections import Counter
    dist = Counter(t.get('timeframe', 'unknown') for t in tasks)
    for tf, count in dist.most_common():
        pct = count / len(tasks) * 100
        print(f"  {tf:10s}: {count:4d} ({pct:4.1f}%)")


if __name__ == '__main__':
    main()
