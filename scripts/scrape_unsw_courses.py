#!/usr/bin/env python3
"""
Scrape UNSW course handbook for learning outcomes.
UNSW embeds JSON data in the page which we can extract.
"""

import json
import re
import time
from pathlib import Path
import subprocess

UNSW_PRIORITY_COURSES = [
    # Computing
    "COMP1511", "COMP1521", "COMP1531", "COMP2511", "COMP2521", 
    "COMP3311", "COMP3331", "COMP3821", "COMP4920", "COMP6080",
    "SENG1031", "SENG2011", "SENG2021", "SENG3011",
    
    # Engineering
    "ENGG1000", "ENGG1811",
    
    # Mathematics/Statistics
    "MATH1131", "MATH1141", "MATH1231", "MATH1241",
    "STAT1021", "STAT2011", "STAT2911",
    
    # Science
    "BIOL1011", "BIOL1021",
    "CHEM1011", "CHEM1021",
    "PHYS1121", "PHYS1131",
    
    # Business
    "ACCT1501", "ACCT1511", "ACCT2511",
    "FINS1612", "FINS1613", "FINS2624",
    "MGMT1001", "MGMT2001",
    "ECON1101", "ECON1102",
    
    # Psychology
    "PSYC1001", "PSYC1011", "PSYC2001",
    
    # Law
    "LAWS1011", "LAWS1021",
]


def fetch_course(course_code: str) -> dict:
    """Fetch course details from UNSW handbook."""
    url = f"https://www.handbook.unsw.edu.au/undergraduate/courses/2026/{course_code}"
    
    result = subprocess.run(
        ["curl", "-sL", url],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    html = result.stdout
    
    if "Page Not Found" in html or "404" in html[:1000] or len(html) < 5000:
        return None
    
    # Extract JSON data from Next.js script tag
    json_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html)
    if not json_match:
        return None
    
    try:
        data = json.loads(json_match.group(1))
        page_content = data.get('props', {}).get('pageProps', {}).get('pageContent', {})
    except:
        return None
    
    title = page_content.get('title', course_code)
    
    # Extract learning outcomes
    learning_outcomes = []
    unit_los = page_content.get('unit_learning_outcomes', [])
    for lo in unit_los:
        desc = lo.get('description', '').strip()
        if desc:
            learning_outcomes.append(desc)
    
    if not learning_outcomes:
        return None
    
    # Extract faculty
    faculty_detail = page_content.get('faculty_detail', [])
    faculty = faculty_detail[0].get('name', 'Unknown') if faculty_detail else 'Unknown'
    
    # Map to simplified faculty
    faculty_simple = "Unknown"
    if any(x in course_code for x in ["COMP", "SENG"]):
        faculty_simple = "Computing"
    elif "ENGG" in course_code:
        faculty_simple = "Engineering"
    elif any(x in course_code for x in ["MATH", "STAT"]):
        faculty_simple = "Mathematics"
    elif any(x in course_code for x in ["BIOL", "CHEM", "PHYS"]):
        faculty_simple = "Science"
    elif any(x in course_code for x in ["ACCT", "FINS", "MGMT", "ECON"]):
        faculty_simple = "Business"
    elif "PSYC" in course_code:
        faculty_simple = "Psychology"
    elif "LAWS" in course_code:
        faculty_simple = "Law"
    
    # Extract level
    level_match = re.search(r'[A-Z]+(\d)', course_code)
    level = int(level_match.group(1)) if level_match else 1
    
    credit_points = int(page_content.get('credit_points', 6))
    
    return {
        "code": course_code,
        "title": title,
        "university": "University of New South Wales",
        "university_code": "UNSW",
        "faculty": faculty_simple,
        "level": level,
        "credit_points": credit_points,
        "learning_outcomes": learning_outcomes,
        "handbook_url": url
    }


def main():
    output_dir = Path(__file__).parent.parent / "data" / "courses"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    courses = []
    errors = []
    
    for i, code in enumerate(UNSW_PRIORITY_COURSES):
        print(f"[{i+1}/{len(UNSW_PRIORITY_COURSES)}] Fetching {code}...", end=" ", flush=True)
        
        try:
            course = fetch_course(code)
            if course is None:
                print("✗ Not found")
                errors.append(code)
            elif course["learning_outcomes"]:
                courses.append(course)
                print(f"✓ {len(course['learning_outcomes'])} LOs")
            else:
                print("⚠ No LOs found")
                errors.append(code)
        except Exception as e:
            print(f"✗ {e}")
            errors.append(code)
        
        time.sleep(0.3)
    
    output_file = output_dir / "unsw_courses.json"
    with open(output_file, "w") as f:
        json.dump(courses, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"✅ Saved {len(courses)} courses to {output_file}")
    print(f"📊 Total learning outcomes: {sum(len(c['learning_outcomes']) for c in courses)}")
    if errors:
        print(f"⚠ Errors ({len(errors)}): {', '.join(errors)}")


if __name__ == "__main__":
    main()
