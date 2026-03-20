"""
Step 4: Import occupation and task data into Cloudflare D1.
Generates SQL and executes via wrangler CLI.
"""

import json
import subprocess
from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path(__file__).parent / 'output'
SQL_DIR = Path(__file__).parent.parent.parent / 'sql'
DB_NAME = 'taskfolio-au'


def escape_sql(val: str) -> str:
    return val.replace("'", "''") if val else ''


def import_occupations():
    print("Importing occupations...")
    df = pd.read_json(OUTPUT_DIR / 'taskfolio_master_data.json')

    # Load JSA stats
    ychua_path = Path(__file__).parent.parent.parent / 'ychua-jobs' / 'site' / 'data.json'
    jsa = {}
    if ychua_path.exists():
        with open(ychua_path) as f:
            jsa = {o['code']: o for o in json.load(f)}

    stmts = []
    for code, group in df.groupby('anzsco_code'):
        title = group['anzsco_title'].iloc[0]
        onet = group.get('onet_soc_code', pd.Series([None])).iloc[0]
        conf = group.get('confidence', pd.Series([None])).iloc[0]
        source = group.get('source', pd.Series(['anthropic'])).iloc[0]
        j = jsa.get(code, {})

        emp = j.get('employment', 'NULL')
        pay = j.get('median_pay', 'NULL')
        outlook = escape_sql(j.get('outlook', ''))
        education = escape_sql(j.get('education', ''))

        stmts.append(
            f"INSERT OR IGNORE INTO occupations "
            f"(anzsco_code, title, employment, median_pay_aud, outlook, education, onet_code, mapping_confidence, source) "
            f"VALUES ('{code}', '{escape_sql(title)}', {emp}, {pay}, '{outlook}', '{education}', "
            f"'{onet or ''}', {conf or 'NULL'}, '{source}');"
        )

    sql_file = SQL_DIR / 'import_occupations.sql'
    sql_file.write_text('\n'.join(stmts))
    print(f"  Generated {len(stmts)} INSERT statements")

    result = subprocess.run(
        ['wrangler', 'd1', 'execute', DB_NAME, f'--file={sql_file}'],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"  ✅ Imported {len(stmts)} occupations")
    else:
        print(f"  ❌ {result.stderr[:500]}")


def import_tasks():
    print("Importing tasks...")
    df = pd.read_json(OUTPUT_DIR / 'taskfolio_master_data.json')

    # Get occupation IDs from D1 (need mapping)
    # For now, generate SQL that looks up by anzsco_code
    stmts = []
    for _, row in df.iterrows():
        desc = escape_sql(str(row.get('task_description', row.get('description', ''))))
        code = row['anzsco_code']
        source = row.get('source', 'anthropic')

        cols = ['occupation_id', 'description', 'source']
        vals = [f"(SELECT id FROM occupations WHERE anzsco_code = '{code}')", f"'{desc}'", f"'{source}'"]

        # Add optional fields
        for field in ['automation_pct', 'augmentation_pct', 'success_rate',
                      'human_time_without_ai', 'human_time_with_ai', 'speedup_factor',
                      'human_education_years', 'ai_autonomy', 'usage_frequency',
                      'taskfolio_score']:
            if field in row and pd.notna(row[field]):
                cols.append(field)
                vals.append(str(row[field]))

        if 'frequency' in row and pd.notna(row['frequency']):
            cols.append('frequency')
            vals.append(f"'{row['frequency']}'")
        if 'timeframe' in row and pd.notna(row['timeframe']):
            cols.append('timeframe')
            vals.append(f"'{row['timeframe']}'")

        stmts.append(f"INSERT INTO tasks ({', '.join(cols)}) VALUES ({', '.join(vals)});")

    # Write in batches (D1 has limits)
    batch_size = 500
    for i in range(0, len(stmts), batch_size):
        batch = stmts[i:i + batch_size]
        sql_file = SQL_DIR / f'import_tasks_{i // batch_size}.sql'
        sql_file.write_text('\n'.join(batch))

        result = subprocess.run(
            ['wrangler', 'd1', 'execute', DB_NAME, f'--file={sql_file}'],
            capture_output=True, text=True
        )
        status = '✅' if result.returncode == 0 else '❌'
        print(f"  {status} Batch {i // batch_size}: {len(batch)} tasks")

    print(f"\n✅ Total: {len(stmts)} tasks imported")


def main():
    import_occupations()
    import_tasks()
    print("\nVerify: wrangler d1 execute taskfolio-au --command='SELECT COUNT(*) FROM occupations'")


if __name__ == '__main__':
    main()
