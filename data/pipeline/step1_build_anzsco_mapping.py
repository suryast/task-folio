"""
Step 1: Map 361 ANZSCO occupations to O*NET SOC codes using fuzzy matching.
Output: data/pipeline/output/anzsco_onet_mapping.csv
"""

from difflib import SequenceMatcher
from pathlib import Path
import pandas as pd
import json

OUTPUT_DIR = Path(__file__).parent / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)


def normalize_title(title: str) -> str:
    return title.lower().strip().replace('&', 'and')


def calculate_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def main():
    # Load ANZSCO data from ychua's repo
    ychua_path = Path(__file__).parent.parent.parent / 'ychua-jobs' / 'site' / 'data.json'
    print(f"Loading ANZSCO occupations from {ychua_path}...")
    with open(ychua_path) as f:
        anzsco_data = json.load(f)
    print(f"  Loaded {len(anzsco_data)} ANZSCO occupations")

    # Load O*NET occupations from Anthropic dataset
    anthropic_path = Path(__file__).parent.parent.parent / 'anthropic-data' / 'onet_task_statements.csv'
    print(f"Loading O*NET occupations from {anthropic_path}...")
    onet_tasks = pd.read_csv(anthropic_path)
    onet_occupations = onet_tasks.groupby('onet_soc_code').agg({'occupation_title': 'first'}).reset_index()
    print(f"  Loaded {len(onet_occupations)} O*NET occupations")

    # Fuzzy match
    mappings = []
    for occ in anzsco_data:
        code, title = occ['code'], occ['name']
        best_match, best_score = None, 0

        for _, row in onet_occupations.iterrows():
            score = calculate_similarity(title, row['occupation_title'])
            if score > best_score:
                best_score = score
                best_match = row

        if best_score > 0.7:
            mappings.append({
                'anzsco_code': code,
                'anzsco_title': title,
                'onet_soc_code': best_match['onet_soc_code'],
                'onet_title': best_match['occupation_title'],
                'confidence': round(best_score, 3),
            })
            if best_score < 0.85:
                print(f"  ⚠️  Low ({best_score:.2f}): {title} → {best_match['occupation_title']}")

    df = pd.DataFrame(mappings)
    df.to_csv(OUTPUT_DIR / 'anzsco_onet_mapping.csv', index=False)

    # Stats
    print(f"\n✅ Mapping complete:")
    print(f"  Total: {len(anzsco_data)} | Mapped: {len(mappings)} | Unmapped: {len(anzsco_data) - len(mappings)}")
    print(f"  High (>0.85): {len(df[df['confidence'] > 0.85])}")
    print(f"  Medium (0.7-0.85): {len(df[(df['confidence'] >= 0.7) & (df['confidence'] <= 0.85)])}")

    # Save unmapped
    mapped_codes = set(df['anzsco_code'])
    unmapped = [o for o in anzsco_data if o['code'] not in mapped_codes]
    with open(OUTPUT_DIR / 'unmapped_occupations.json', 'w') as f:
        json.dump(unmapped, f, indent=2)
    print(f"  📋 Unmapped saved to output/unmapped_occupations.json")


if __name__ == '__main__':
    main()
