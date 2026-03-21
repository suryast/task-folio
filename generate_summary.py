#!/usr/bin/env python3
"""Generate summary statistics for the regenerated tasks."""

import json
from collections import defaultdict

# Load regenerated tasks
with open('data/pipeline/output/regenerated_tasks.json', 'r') as f:
    tasks = json.load(f)

# Load occupations list for reference
with open('data/pipeline/output/occupations_to_regenerate.json', 'r') as f:
    occupations = json.load(f)

# Calculate statistics
stats = {
    'total_tasks': len(tasks),
    'total_occupations': len(occupations),
    'tasks_per_occupation': len(tasks) // len(occupations) if occupations else 0,
    'by_timeframe': defaultdict(int),
    'by_anzsco': defaultdict(int),
    'automation_levels': {
        'high': 0,  # >0.5
        'medium': 0,  # 0.3-0.5
        'low': 0,  # <0.3
    },
    'avg_automation': 0,
    'avg_augmentation': 0,
}

# Analyze tasks
total_auto = 0
total_aug = 0

for task in tasks:
    stats['by_timeframe'][task['timeframe']] += 1
    stats['by_anzsco'][task['anzsco_code']] += 1
    
    auto = task['automation_pct']
    total_auto += auto
    total_aug += task['augmentation_pct']
    
    if auto > 0.5:
        stats['automation_levels']['high'] += 1
    elif auto > 0.3:
        stats['automation_levels']['medium'] += 1
    else:
        stats['automation_levels']['low'] += 1

stats['avg_automation'] = total_auto / len(tasks) if tasks else 0
stats['avg_augmentation'] = total_aug / len(tasks) if tasks else 0

# Print summary report
print("=" * 80)
print("TASK REGENERATION SUMMARY REPORT")
print("=" * 80)
print()
print(f"Total Occupations Processed: {stats['total_occupations']}")
print(f"Total Tasks Generated: {stats['total_tasks']}")
print(f"Tasks per Occupation: {stats['tasks_per_occupation']}")
print()
print("Automation/Augmentation Metrics:")
print(f"  Average Automation %: {stats['avg_automation']:.1%}")
print(f"  Average Augmentation %: {stats['avg_augmentation']:.1%}")
print()
print("Task Distribution by Automation Level:")
print(f"  High (>50%): {stats['automation_levels']['high']} tasks ({stats['automation_levels']['high']/len(tasks)*100:.1f}%)")
print(f"  Medium (30-50%): {stats['automation_levels']['medium']} tasks ({stats['automation_levels']['medium']/len(tasks)*100:.1f}%)")
print(f"  Low (<30%): {stats['automation_levels']['low']} tasks ({stats['automation_levels']['low']/len(tasks)*100:.1f}%)")
print()
print("Task Distribution by Timeframe:")
for timeframe in ['now', '1-2y', '3-5y', '5-10y', '10y+']:
    count = stats['by_timeframe'][timeframe]
    pct = count / len(tasks) * 100 if tasks else 0
    print(f"  {timeframe:8s}: {count:4d} tasks ({pct:5.1f}%)")
print()
print("Sample Occupations:")
print("-" * 80)

# Show a sample of occupations with their task counts
sample_anzsco_codes = list(stats['by_anzsco'].keys())[:10]
for anzsco in sample_anzsco_codes:
    occ = next((o for o in occupations if o['anzsco_code'] == anzsco), None)
    if occ:
        task_count = stats['by_anzsco'][anzsco]
        print(f"  {anzsco} - {occ['title']}")
        print(f"    Tasks: {task_count} | Old SOC: {occ['old_soc']} ({occ['old_confidence']:.3f}) → New: {', '.join(occ['new_socs'][:3])}")

print()
print("=" * 80)
print("Output file: data/pipeline/output/regenerated_tasks.json")
print("File size: ~307 KB")
print("=" * 80)

# Save summary to JSON
summary = {
    'generation_date': '2026-03-21',
    'total_occupations': stats['total_occupations'],
    'total_tasks': stats['total_tasks'],
    'tasks_per_occupation': stats['tasks_per_occupation'],
    'avg_automation_pct': round(stats['avg_automation'], 3),
    'avg_augmentation_pct': round(stats['avg_augmentation'], 3),
    'timeframe_distribution': dict(stats['by_timeframe']),
    'automation_level_distribution': stats['automation_levels'],
}

with open('data/pipeline/output/regeneration_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("\nSummary statistics saved to: data/pipeline/output/regeneration_summary.json")
