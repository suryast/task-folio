#!/usr/bin/env python3
"""
Scrape University of Sydney course handbook for learning outcomes.
"""

import json
import re
import time
from pathlib import Path
import subprocess

# Priority USyd courses
USYD_PRIORITY_COURSES = [
    # Computing
    "INFO1110", "INFO1111", "INFO1112", "INFO1113",
    "INFO2222", "INFO2120",
    "COMP2017", "COMP2123", "COMP2823",
    "COMP3027", "COMP3308", "COMP3520",
    "DATA1001", "DATA2001",
    
    # Engineering
    "ENGG1801", "ENGG1810", "ENGG1820",
    
    # Mathematics/Statistics  
    "MATH1001", "MATH1002", "MATH1003", "MATH1004", "MATH1005",
    "STAT1021", "STAT2011", "STAT2012",
    
    # Science
    "BIOL1001", "BIOL1002",
    "CHEM1001", "CHEM1002",
    "PHYS1001", "PHYS1002",
    
    # Business
    "ACCT1001", "ACCT1006", "ACCT2011",
    "FINC1001", "FINC2011", "FINC2012",
    "BUSS1020", "BUSS1030",
    "ECON1001", "ECON1002",
    
    # Psychology
    "PSYC1001", "PSYC1002", "PSYC2012",
    
    # Law
    "LAWS1006", "LAWS1015",
]


def fetch_course(course_code: str) -> dict:
    """Fetch course details from Sydney handbook."""
    url = f"https://www.sydney.edu.au/units/{course_code}"
    
    result = subprocess.run(
        ["curl", "-sL", url],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    html = result.stdout
    
    if "Page not found" in html or "404" in html[:1000] or len(html) < 3000:
        return None
    
    # Extract title
    title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    if not title_match:
        title_match = re.search(r'<title>([^|<]+)', html)
    title = title_match.group(1).strip() if title_match else course_code
    
    # Extract learning outcomes
    # Sydney uses <span class="learning-outcomes-detail">
    outcomes = re.findall(
        r'<span class="learning-outcomes-detail">\.?\s*([^<]+)</span>',
        html
    )
    learning_outcomes = [o.strip() for o in outcomes if o.strip()]
    
    # Extract credit points
    points_match = re.search(r'(\d+)\s*credit\s*points?', html, re.IGNORECASE)
    credit_points = int(points_match.group(1)) if points_match else 6
    
    # Determine faculty
    faculty = "Unknown"
    if any(x in course_code for x in ["INFO", "COMP", "DATA"]):
        faculty = "Computing"
    elif "ENGG" in course_code:
        faculty = "Engineering"
    elif any(x in course_code for x in ["MATH", "STAT"]):
        faculty = "Mathematics"
    elif any(x in course_code for x in ["BIOL", "CHEM", "PHYS"]):
        faculty = "Science"
    elif any(x in course_code for x in ["ACCT", "FINC", "BUSS", "ECON"]):
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
        "university": "University of Sydney",
        "university_code": "USYD",
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
    
    for i, code in enumerate(USYD_PRIORITY_COURSES):
        print(f"[{i+1}/{len(USYD_PRIORITY_COURSES)}] Fetching {code}...", end=" ", flush=True)
        
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
    
    output_file = output_dir / "usyd_courses.json"
    with open(output_file, "w") as f:
        json.dump(courses, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"✅ Saved {len(courses)} courses to {output_file}")
    print(f"📊 Total learning outcomes: {sum(len(c['learning_outcomes']) for c in courses)}")
    if errors:
        print(f"⚠ Errors ({len(errors)}): {', '.join(errors)}")


if __name__ == "__main__":
    main()
