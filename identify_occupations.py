#!/usr/bin/env python3
"""
Identify occupations that need task regeneration:
- SOC code changed between old and new mappings
- Old confidence < 0.85
"""

import csv
import json
from collections import defaultdict

# Read improved mappings
improved_mappings = defaultdict(set)
with open('data/crosswalks/anzsco_to_soc_improved.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        anzsco = row['anzsco_code']
        soc = row['soc_code']
        improved_mappings[anzsco].add(soc)

# Read old mappings
old_mappings = {}
with open('data/pipeline/output/anzsco_onet_mapping.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        anzsco = row['anzsco_code']
        onet_soc = row['onet_soc_code'].split('.')[0]  # Remove .XX suffix
        title = row['anzsco_title']
        confidence = float(row['confidence'])
        old_mappings[anzsco] = {
            'soc': onet_soc,
            'title': title,
            'confidence': confidence
        }

# Find occupations needing regeneration
needs_regen = []
for anzsco, old_data in old_mappings.items():
    if old_data['confidence'] < 0.85:
        old_soc = old_data['soc']
        new_socs = improved_mappings.get(anzsco, set())
        
        # Check if SOC changed
        if old_soc not in new_socs and len(new_socs) > 0:
            needs_regen.append({
                'anzsco_code': anzsco,
                'title': old_data['title'],
                'old_soc': old_soc,
                'new_socs': list(new_socs),
                'old_confidence': old_data['confidence']
            })

# Sort by ANZSCO code
needs_regen.sort(key=lambda x: x['anzsco_code'])

# Save to JSON
with open('data/pipeline/output/occupations_to_regenerate.json', 'w') as f:
    json.dump(needs_regen, f, indent=2)

print(f"Found {len(needs_regen)} occupations needing regeneration")
print("\nSample occupations:")
for occ in needs_regen[:10]:
    print(f"  {occ['anzsco_code']} {occ['title']}")
    print(f"    Old: {occ['old_soc']} (conf={occ['old_confidence']:.3f})")
    print(f"    New: {', '.join(occ['new_socs'])}")
