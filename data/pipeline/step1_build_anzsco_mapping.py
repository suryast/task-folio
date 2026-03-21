"""
Step 1: Map 361 ANZSCO occupations to O*NET SOC codes using fuzzy matching.
Output: data/pipeline/output/anzsco_onet_mapping.csv

Actual Anthropic dataset columns:
  onet_task_statements.csv: O*NET-SOC Code, Title, Task ID, Task, Task Type
"""

from difflib import SequenceMatcher
from pathlib import Path
import pandas as pd
import json

OUTPUT_DIR = Path(__file__).parent / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

YCHUA_PATH = Path.home() / 'projects' / 'ychua-jobs' / 'site' / 'data.json'
ANTHROPIC_PATH = Path.home() / 'projects' / 'anthropic-data' / 'onet_task_statements.csv'


def normalize_title(title: str) -> str:
    return title.lower().strip().replace('&', 'and').replace('-', ' ')


def calculate_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def main():
    # Load ANZSCO
    print(f"Loading ANZSCO from {YCHUA_PATH}...")
    with open(YCHUA_PATH) as f:
        anzsco_data = json.load(f)
    print(f"  {len(anzsco_data)} ANZSCO occupations")

    # Load O*NET occupations
    print(f"Loading O*NET from {ANTHROPIC_PATH}...")
    onet_tasks = pd.read_csv(ANTHROPIC_PATH)
    onet_occupations = onet_tasks.groupby('O*NET-SOC Code').agg({'Title': 'first'}).reset_index()
    onet_occupations.columns = ['onet_soc_code', 'onet_title']
    print(f"  {len(onet_occupations)} O*NET occupations")

    # Fuzzy match
    mappings = []
    for occ in anzsco_data:
        code = occ['slug'].split('-')[0]  # e.g., "6211-sales-assistants-general" → "6211"
        title = occ['title']
        best_match, best_score = None, 0

        for _, row in onet_occupations.iterrows():
            score = calculate_similarity(title, row['onet_title'])
            if score > best_score:
                best_score = score
                best_match = row

        if best_score > 0.5:  # Lower threshold, we can filter later
            mappings.append({
                'anzsco_code': code,
                'anzsco_title': title,
                'onet_soc_code': best_match['onet_soc_code'],
                'onet_title': best_match['onet_title'],
                'confidence': round(best_score, 3),
            })
            if best_score < 0.7:
                print(f"  ⚠️  Low ({best_score:.2f}): {title} → {best_match['onet_title']}")

    df = pd.DataFrame(mappings)
    df.to_csv(OUTPUT_DIR / 'anzsco_onet_mapping.csv', index=False)

    high = len(df[df['confidence'] > 0.85])
    med = len(df[(df['confidence'] >= 0.7) & (df['confidence'] <= 0.85)])
    low = len(df[(df['confidence'] >= 0.5) & (df['confidence'] < 0.7)])

    print(f"\n✅ Mapping complete:")
    print(f"  Total: {len(anzsco_data)} | Mapped: {len(mappings)} | Unmapped: {len(anzsco_data) - len(mappings)}")
    print(f"  High (>0.85): {high} | Medium (0.7-0.85): {med} | Low (0.5-0.7): {low}")

    # Save unmapped
    mapped_codes = set(df['anzsco_code'])
    unmapped = [o for o in anzsco_data if o['slug'].split('-')[0] not in mapped_codes]
    with open(OUTPUT_DIR / 'unmapped_occupations.json', 'w') as f:
        json.dump(unmapped, f, indent=2)
    print(f"  📋 Unmapped: {len(unmapped)} saved to output/unmapped_occupations.json")


if __name__ == '__main__':
    main()
