#!/usr/bin/env python3
"""
Scrape ANU course handbook for learning outcomes.
Priority: High-enrollment STEM, Business, Health courses.
"""

import json
import re
import time
from pathlib import Path
import subprocess

# Priority ANU courses (high-enrollment, representative)
ANU_PRIORITY_COURSES = [
    # Computing/IT
    "COMP1100", "COMP1110", "COMP1130", "COMP1140",
    "COMP2100", "COMP2120", "COMP2310", "COMP2400",
    "COMP3100", "COMP3310", "COMP3500", "COMP3600",
    
    # Engineering
    "ENGN1211", "ENGN1215", "ENGN1217", "ENGN2225",
    
    # Mathematics/Statistics
    "MATH1005", "MATH1013", "MATH1014", "MATH1115", "MATH1116",
    "STAT1003", "STAT1008", "STAT2001",
    
    # Science
    "BIOL1001", "BIOL1002", "BIOL1003",
    "CHEM1101", "CHEM1201",
    "PHYS1001", "PHYS1101",
    
    # Business
    "ACCT1001", "ACCT2011", "ACCT2012",
    "FINM1001", "FINM2001", "FINM2002",
    "MGMT1001", "MGMT2002",
    "ECON1101", "ECON1102",
    
    # Psychology
    "PSYC1001", "PSYC1002", "PSYC2008",
    
    # Health
    "MEDI1000", "MEDI1001",
    
    # Law
    "LAWS1201", "LAWS1202",
]

def fetch_course(course_code: str) -> dict:
    """Fetch course details from ANU handbook."""
    url = f"https://programsandcourses.anu.edu.au/course/{course_code}"
    
    result = subprocess.run(
        ["curl", "-sL", url],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    html = result.stdout
    
    # Check if course exists
    if "Page not found" in html or "404" in html[:500]:
        return None
    
    # Extract title from <title> tag
    title_match = re.search(r'<title>([^<]+?)(?:\s*-\s*ANU)?</title>', html)
    title = title_match.group(1).strip() if title_match else course_code
    
    # Extract learning outcomes from <ol><li> structure
    lo_section = re.search(
        r'<h2 id="learning-outcomes">.*?<ol>(.*?)</ol>',
        html,
        re.DOTALL | re.IGNORECASE
    )
    
    learning_outcomes = []
    if lo_section:
        # Extract all <li> content
        outcomes = re.findall(r'<li>([^<]+)</li>', lo_section.group(1))
        learning_outcomes = [o.strip() for o in outcomes if o.strip()]
    
    # Extract school/faculty
    school_match = re.search(r'Offered by.*?<[^>]+>([^<]+)</[^>]+>', html, re.DOTALL)
    school = school_match.group(1).strip() if school_match else "Unknown"
    
    # Extract unit value
    units_match = re.search(r'(\d+)\s*units', html)
    units = int(units_match.group(1)) if units_match else 6
    
    # Determine faculty category
    faculty = "Unknown"
    if any(x in course_code for x in ["COMP", "INFO"]):
        faculty = "Computing"
    elif "ENGN" in course_code:
        faculty = "Engineering"
    elif any(x in course_code for x in ["MATH", "STAT"]):
        faculty = "Mathematics"
    elif any(x in course_code for x in ["BIOL", "CHEM", "PHYS"]):
        faculty = "Science"
    elif any(x in course_code for x in ["ACCT", "FINM", "MGMT", "ECON"]):
        faculty = "Business"
    elif "PSYC" in course_code:
        faculty = "Psychology"
    elif "MEDI" in course_code:
        faculty = "Health"
    elif "LAWS" in course_code:
        faculty = "Law"
    
    # Extract level from course code
    level_match = re.search(r'\d', course_code)
    level = int(level_match.group()) if level_match else 1
    
    return {
        "code": course_code,
        "title": title,
        "university": "ANU",
        "university_code": "ANU",
        "school": school,
        "faculty": faculty,
        "level": level,
        "credit_points": units,
        "learning_outcomes": learning_outcomes,
        "handbook_url": url
    }


def main():
    output_dir = Path(__file__).parent.parent / "data" / "courses"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    courses = []
    errors = []
    
    for i, code in enumerate(ANU_PRIORITY_COURSES):
        print(f"[{i+1}/{len(ANU_PRIORITY_COURSES)}] Fetching {code}...", end=" ", flush=True)
        
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
        
        time.sleep(0.3)  # Rate limit
    
    # Save results
    output_file = output_dir / "anu_courses.json"
    with open(output_file, "w") as f:
        json.dump(courses, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"✅ Saved {len(courses)} courses to {output_file}")
    print(f"📊 Total learning outcomes: {sum(len(c['learning_outcomes']) for c in courses)}")
    if errors:
        print(f"⚠ Errors ({len(errors)}): {', '.join(errors)}")


if __name__ == "__main__":
    main()
