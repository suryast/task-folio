#!/usr/bin/env python3
"""Import JSA employment projections to D1."""

import json
import pandas as pd
import subprocess

# Read projections
df = pd.read_csv('data/jsa_employment_projections_2025_2035.csv')
print(f"Loaded {len(df)} projections")

# Generate SQL updates
sql_statements = []
for _, row in df.iterrows():
    code = str(row['anzsco']).zfill(4)
    baseline = int(row['baseline_2025'] * 1000)  # Convert to actual count
    proj_2035 = int(row['proj_2035'] * 1000)
    growth_pct = round(row['10yr_pct'] * 100, 1)  # Convert to percentage
    
    # Determine outlook based on growth
    if growth_pct >= 15:
        outlook = 'strong_growth'
    elif growth_pct >= 5:
        outlook = 'moderate_growth'
    elif growth_pct >= 0:
        outlook = 'stable'
    elif growth_pct >= -5:
        outlook = 'declining'
    else:
        outlook = 'strong_decline'
    
    sql = f"UPDATE occupations SET employment = {baseline}, outlook = '{outlook}' WHERE anzsco_code = '{code}';"
    sql_statements.append(sql)

# Write to file
with open('/tmp/jsa_update.sql', 'w') as f:
    f.write('\n'.join(sql_statements))

print(f"Generated {len(sql_statements)} SQL updates")
print("Sample:")
for s in sql_statements[:5]:
    print(f"  {s}")
