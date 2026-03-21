#!/usr/bin/env python3
"""Validate the regenerated tasks output for data integrity."""

import json

print("Validating regenerated_tasks.json...")
print("=" * 60)

# Load tasks
with open('data/pipeline/output/regenerated_tasks.json', 'r') as f:
    tasks = json.load(f)

# Validation checks
errors = []
warnings = []

# Check 1: All tasks have required fields
required_fields = ['anzsco_code', 'occupation_title', 'description', 
                   'automation_pct', 'augmentation_pct', 'timeframe', 'source']

for i, task in enumerate(tasks):
    missing = [f for f in required_fields if f not in task]
    if missing:
        errors.append(f"Task {i}: Missing fields {missing}")

# Check 2: Valid automation/augmentation percentages
for i, task in enumerate(tasks):
    auto = task.get('automation_pct', 0)
    aug = task.get('augmentation_pct', 0)
    
    if not (0 <= auto <= 1):
        errors.append(f"Task {i} ({task['anzsco_code']}): Invalid automation_pct {auto}")
    if not (0 <= aug <= 1):
        errors.append(f"Task {i} ({task['anzsco_code']}): Invalid augmentation_pct {aug}")

# Check 3: Valid timeframes
valid_timeframes = ['now', '1-2y', '3-5y', '5-10y', '10y+']
for i, task in enumerate(tasks):
    tf = task.get('timeframe', '')
    if tf not in valid_timeframes:
        errors.append(f"Task {i} ({task['anzsco_code']}): Invalid timeframe '{tf}'")

# Check 4: Source field is correct
for i, task in enumerate(tasks):
    if task.get('source') != 'regenerated_v1.2':
        warnings.append(f"Task {i} ({task['anzsco_code']}): Unexpected source '{task.get('source')}'")

# Check 5: Task count per occupation
from collections import Counter
task_counts = Counter(t['anzsco_code'] for t in tasks)

for anzsco, count in task_counts.items():
    if count < 15 or count > 20:
        warnings.append(f"ANZSCO {anzsco}: {count} tasks (expected 15-20)")

# Check 6: Non-empty descriptions
for i, task in enumerate(tasks):
    desc = task.get('description', '')
    if not desc or len(desc) < 10:
        errors.append(f"Task {i} ({task['anzsco_code']}): Description too short or empty")

# Print results
print(f"Total tasks validated: {len(tasks)}")
print(f"Unique occupations: {len(task_counts)}")
print()

if errors:
    print(f"❌ ERRORS FOUND: {len(errors)}")
    for err in errors[:10]:  # Show first 10
        print(f"  - {err}")
    if len(errors) > 10:
        print(f"  ... and {len(errors) - 10} more")
else:
    print("✓ No errors found")

print()

if warnings:
    print(f"⚠️  WARNINGS: {len(warnings)}")
    for warn in warnings[:10]:  # Show first 10
        print(f"  - {warn}")
    if len(warnings) > 10:
        print(f"  ... and {len(warnings) - 10} more")
else:
    print("✓ No warnings")

print()
print("=" * 60)

if not errors:
    print("✓ VALIDATION PASSED - Output file is valid")
else:
    print("❌ VALIDATION FAILED - Please review errors")

print()
print("Task count distribution:")
for anzsco in sorted(task_counts.keys())[:5]:
    count = task_counts[anzsco]
    title = next((t['occupation_title'] for t in tasks if t['anzsco_code'] == anzsco), 'Unknown')
    print(f"  {anzsco} ({title}): {count} tasks")
print(f"  ... and {len(task_counts) - 5} more occupations")
