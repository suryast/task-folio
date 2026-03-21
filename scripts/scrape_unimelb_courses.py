#!/usr/bin/env python3
"""
Scrape University of Melbourne course handbook for learning outcomes.
"""

import json
import re
import time
from pathlib import Path
import subprocess

# Priority UniMelb courses
UNIMELB_PRIORITY_COURSES = [
    # Computing
    "COMP10001", "COMP10002", "COMP20003", "COMP20007", "COMP30020",
    "SWEN20003", "SWEN30006",
    "INFO20003",
    
    # Engineering
    "ENGR10003", "ENGR20004",
    
    # Mathematics/Statistics
    "MAST10005", "MAST10006", "MAST10007", "MAST10008",
    "MAST20004", "MAST20005", "MAST20006",
    
    # Science
    "BIOL10004", "BIOL10005",
    "CHEM10003", "CHEM10004",
    "PHYC10003", "PHYC10004",
    
    # Business
    "ACCT10001", "ACCT10002", "ACCT20001",
    "FNCE10001", "FNCE10002", "FNCE20001",
    "MGMT10001", "MGMT20001",
    "ECON10003", "ECON10004",
    
    # Psychology
    "PSYC10003", "PSYC20007", "PSYC30013",
    
    # Law
    "LAWS10001", "LAWS10002",
]


def fetch_course(course_code: str) -> dict:
    """Fetch course details from Melbourne handbook."""
    url = f"https://handbook.unimelb.edu.au/subjects/{course_code.lower()}"
    
    result = subprocess.run(
        ["curl", "-sL", url],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    html = result.stdout
    
    if "Page Not Found" in html or "404" in html[:1000] or len(html) < 2000:
        return None
    
    # Extract title
    title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    title = title_match.group(1).strip() if title_match else course_code
    
    # Extract intended learning outcomes
    # Melbourne uses <ul class="ticked-list"> after "Intended learning outcomes"
    lo_section = re.search(
        r'<div id="learning-outcomes">.*?<ul[^>]*>(.*?)</ul>',
        html,
        re.DOTALL | re.IGNORECASE
    )
    
    learning_outcomes = []
    if lo_section:
        outcomes = re.findall(r'<li[^>]*>([^<]+)</li>', lo_section.group(1))
        learning_outcomes = [o.strip() for o in outcomes if o.strip()]
    
    # Extract credit points
    points_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:credit )?points?', html, re.IGNORECASE)
    credit_points = float(points_match.group(1)) if points_match else 12.5
    
    # Determine faculty
    faculty = "Unknown"
    if any(x in course_code for x in ["COMP", "SWEN", "INFO"]):
        faculty = "Computing"
    elif "ENGR" in course_code:
        faculty = "Engineering"
    elif "MAST" in course_code:
        faculty = "Mathematics"
    elif any(x in course_code for x in ["BIOL", "CHEM", "PHYC"]):
        faculty = "Science"
    elif any(x in course_code for x in ["ACCT", "FNCE", "MGMT", "ECON"]):
        faculty = "Business"
    elif "PSYC" in course_code:
        faculty = "Psychology"
    elif "LAWS" in course_code:
        faculty = "Law"
    
    # Extract level
    level_match = re.search(r'[A-Z]+(\d)', course_code)
    level = int(level_match.group(1)) if level_match else 1
    
    return {
        "code": course_code,
        "title": title,
        "university": "University of Melbourne",
        "university_code": "MELB",
        "faculty": faculty,
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
    
    for i, code in enumerate(UNIMELB_PRIORITY_COURSES):
        print(f"[{i+1}/{len(UNIMELB_PRIORITY_COURSES)}] Fetching {code}...", end=" ", flush=True)
        
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
    
    output_file = output_dir / "unimelb_courses.json"
    with open(output_file, "w") as f:
        json.dump(courses, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"✅ Saved {len(courses)} courses to {output_file}")
    print(f"📊 Total learning outcomes: {sum(len(c['learning_outcomes']) for c in courses)}")
    if errors:
        print(f"⚠ Errors ({len(errors)}): {', '.join(errors)}")


if __name__ == "__main__":
    main()
