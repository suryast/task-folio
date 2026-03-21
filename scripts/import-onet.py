#!/usr/bin/env python3
"""
Import O*NET 29.1 database → data/onet-full.json
"""
import csv
import json
import os
import re

DATA_DIR = "/tmp/onet_db/db_29_1_text"
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_FILE = os.path.join(PROJECT_DIR, "data", "onet-full.json")
OLD_FILE = os.path.join(PROJECT_DIR, "data", "onet", "occupations.json")

def read_tsv(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def categorize_task(text: str) -> str:
    t = text.lower()
    physical_kw = ["lift", "carry", "load ", "move ", "operate equipment", "physical",
                   "handle materials", "climb", "drive ", "haul", "dig ", "install",
                   "repair ", "maintain equipment", "assemble", "weld", "cut ",
                   "inspect equipment", "patrol", "secure ", "transport"]
    if any(k in t for k in physical_kw):
        return "physical"
    interpersonal_kw = ["communicate", "collaborate", "consult with", "discuss",
                        "interview", "advise", "train ", "supervise", "assist",
                        "work with", "customer", "client", "negotiate", "present",
                        "teach", "mentor", "counsel", "coordinate with", "liaise",
                        "contact", "meet with", "inform ", "notify", "respond to",
                        "resolve conflict", "mediate", "facilitate"]
    if any(k in t for k in interpersonal_kw):
        return "interpersonal"
    admin_kw = ["record ", "document", "report", "file ", "schedule", "budget",
                "maintain records", "process ", "prepare report", "compile",
                "enter data", "update records", "log ", "invoice", "billing",
                "purchase", "order ", "inventory", "administer", "complete forms",
                "submit", "track ", "monitor compliance"]
    if any(k in t for k in admin_kw):
        return "administrative"
    return "cognitive"

def normalize_title(s: str) -> str:
    return s.lower().strip()

def compress_text(s: str, max_len=200) -> str:
    s = re.sub(r'\s+', ' ', s).strip()
    if len(s) > max_len:
        s = s[:max_len].rsplit(' ', 1)[0]
    return s

def main():
    print("Reading occupation data...")
    occ_rows = read_tsv("Occupation Data.txt")
    occupations_meta = {}
    for row in occ_rows:
        code = row["O*NET-SOC Code"]
        occupations_meta[code] = {
            "socCode": code,
            "title": row["Title"],
            "description": compress_text(row["Description"]),
            "tasks": [],
            "technologySkills": [],
            "anzscoCode": None,
            "anzscoTitle": None,
        }
    print(f"  {len(occupations_meta)} occupations")

    print("Reading tasks...")
    task_rows = read_tsv("Task Statements.txt")
    task_count = 0
    for row in task_rows:
        code = row["O*NET-SOC Code"]
        task_type = row.get("Task Type", "")
        if code not in occupations_meta:
            continue
        task_text = row["Task"].strip()
        occupations_meta[code]["tasks"].append({
            "id": row["Task ID"],
            "name": compress_text(task_text, 200),
            "category": categorize_task(task_text),
        })
        task_count += 1
    print(f"  {task_count} tasks loaded")

    print("Reading alternate titles...")
    alt_rows = read_tsv("Alternate Titles.txt")
    alternate_titles = {}
    for row in alt_rows:
        title = row.get("Alternate Title", "").strip()
        code = row.get("O*NET-SOC Code", "").strip()
        if title and code:
            alternate_titles[normalize_title(title)] = code
    for code, occ in occupations_meta.items():
        alternate_titles[normalize_title(occ["title"])] = code
    print(f"  {len(alternate_titles)} alternate title mappings")

    print("Merging ANZSCO data from old file...")
    anzsco_count = 0
    if os.path.exists(OLD_FILE):
        with open(OLD_FILE) as f:
            old_data = json.load(f)
        for occ in old_data:
            code = occ["socCode"]
            if occ.get("anzscoCode") and occ.get("anzscoTitle") and code in occupations_meta:
                occupations_meta[code]["anzscoCode"] = occ["anzscoCode"]
                occupations_meta[code]["anzscoTitle"] = occ["anzscoTitle"]
                anzsco_count += 1
    print(f"  {anzsco_count} occupations with ANZSCO data")

    print("Filtering to occupations with tasks only...")
    occupations_with_tasks = {
        code: occ for code, occ in occupations_meta.items()
        if len(occ["tasks"]) > 0
    }
    print(f"  {len(occupations_with_tasks)} occupations with tasks")

    output = {
        "occupations": occupations_with_tasks,
        "alternateTitles": alternate_titles,
    }

    print(f"Writing to {OUT_FILE}...")
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, separators=(",", ":"), ensure_ascii=False)

    size_mb = os.path.getsize(OUT_FILE) / 1024 / 1024
    print(f"Done! {size_mb:.2f} MB | {len(occupations_with_tasks)} occupations | {len(alternate_titles)} alt titles")

if __name__ == "__main__":
    main()
