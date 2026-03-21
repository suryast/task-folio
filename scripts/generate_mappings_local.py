#!/usr/bin/env python3
"""
Generate course-to-task mappings using keyword matching and heuristics.
No LLM required - uses semantic similarity based on keywords.
"""

import json
import re
from pathlib import Path

# Keywords that map learning outcomes to task categories
KEYWORD_MAPPINGS = {
    # Programming/coding
    "program": ["9094", "9095", "9076", "9077"],  # Write code, debug
    "code": ["9094", "9097", "9086", "9108"],  # Write code, code review, refactor
    "algorithm": ["9094", "9102"],  # Write code, optimize
    "debug": ["9095", "9077"],  # Debug production issues
    "software": ["9094", "9095", "9100"],  # Software dev tasks
    "procedural": ["9094"],
    "function": ["9094", "9098"],  # Functions, APIs
    
    # Object-oriented
    "object": ["9094", "9111"],  # OOP, front-end
    "class": ["9094"],
    "inheritance": ["9094"],
    "polymorphism": ["9094"],
    "interface": ["9094", "9111"],
    "java": ["9094"],
    
    # Web development
    "web": ["9076", "9077", "9079", "9080"],
    "html": ["9076", "9084"],
    "css": ["9082"],
    "javascript": ["9094", "9077"],
    "react": ["9076", "9111"],
    "ui": ["9078", "9111"],
    "user interface": ["9078", "9111"],
    "responsive": ["9076", "9111"],
    "accessibility": ["9084"],
    
    # Database
    "database": ["9096"],
    "sql": ["9096"],
    "data structure": ["9094", "9096"],
    "query": ["9096"],
    
    # Testing
    "test": ["9090", "9099"],
    "unit test": ["9090", "9099"],
    "quality": ["9097", "9099"],
    
    # Security
    "security": ["9103", "7154", "7155"],
    "threat": ["9103", "7165"],
    "vulnerability": ["9103", "7165"],
    "ethical": ["7157"],
    
    # Systems/Networks
    "operating system": ["7154"],
    "network": ["9080", "9106"],
    "system": ["9100", "9107"],
    
    # Project/Team
    "team": ["9101", "9104"],
    "project": ["9101", "9104"],
    "agile": ["9101"],
    "communicate": ["9089", "9104", "9105"],
    "report": ["9105"],
    "document": ["9105"],
    
    # Design
    "design": ["9078", "9096", "9104"],
    "uml": ["9105"],
    "architecture": ["9100", "9108"],
    
    # APIs
    "api": ["9080", "9098", "9106"],
    "rest": ["9080", "9098"],
    "integrate": ["9106"],
    
    # Deployment/DevOps
    "deploy": ["9091", "9100"],
    "cloud": ["9100"],
    "ci/cd": ["9083", "9100"],
    "pipeline": ["9083", "9100"],
    
    # Mathematics/Statistics
    "statistic": ["8851", "8852"],  # Statistician tasks
    "probability": ["8851"],
    "calculus": ["8851"],
    "mathematical": ["8851", "8852"],
    "analyse": ["8852", "8853"],
    "model": ["8852", "8854"],
    "quantitative": ["8852"],
    
    # Accounting/Finance
    "account": ["7264", "7265", "7266"],  # Accountant tasks
    "financial": ["7264", "7265", "7287"],
    "audit": ["7266", "7267"],
    "tax": ["7268"],
    "budget": ["7287"],
    "invest": ["7287", "7288"],
    
    # Economics
    "economic": ["7289", "7290"],
    "market": ["7289", "7291"],
    "policy": ["7290"],
    
    # Psychology
    "psychology": ["8031", "8032"],
    "behaviour": ["8031", "8033"],
    "cognitive": ["8032"],
    "research": ["8033", "8034"],
    "experiment": ["8034"],
    
    # Law
    "law": ["8211", "8212"],
    "legal": ["8211", "8213"],
    "contract": ["8212"],
    "regulation": ["8213"],
    "intellectual property": ["8214"],
    
    # Science
    "laboratory": ["8421", "8422"],
    "experiment": ["8421"],
    "chemical": ["8423"],
    "biological": ["8424"],
    "physics": ["8425"],
    
    # Engineering
    "engineer": ["8511", "8512"],
    "technical": ["8511", "8513"],
    "prototype": ["8512"],
}


def find_matching_tasks(learning_outcome: str, all_tasks: list) -> list:
    """Find tasks that match a learning outcome using keyword matching."""
    lo_lower = learning_outcome.lower()
    matched_task_ids = set()
    
    # Check each keyword
    for keyword, task_ids in KEYWORD_MAPPINGS.items():
        if keyword in lo_lower:
            matched_task_ids.update(task_ids)
    
    # Convert task IDs to actual task objects with confidence
    matches = []
    for task in all_tasks:
        if str(task["id"]) in matched_task_ids:
            # Calculate confidence based on how many keywords matched
            keyword_count = sum(1 for kw in KEYWORD_MAPPINGS if kw in lo_lower and str(task["id"]) in KEYWORD_MAPPINGS[kw])
            confidence = min(0.95, 0.5 + (keyword_count * 0.15))
            
            matches.append({
                "task_id": task["id"],
                "task_description": task["description"],
                "occupation_title": task["occupation_title"],
                "confidence": round(confidence, 2)
            })
    
    return matches[:5]  # Limit to top 5 matches


def map_course(course: dict, all_tasks: list) -> dict:
    """Map all learning outcomes for a course to tasks."""
    mappings = []
    
    for lo in course["learning_outcomes"]:
        matches = find_matching_tasks(lo, all_tasks)
        if matches:
            mappings.append({
                "learning_outcome": lo,
                "matched_tasks": matches
            })
    
    return {
        "course": course,
        "mappings": mappings
    }


def main():
    output_dir = Path(__file__).parent.parent / "data" / "course_mappings"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("Loading data...")
    courses = []
    for f in ["usyd_courses.json", "anu_courses.json", "unsw_courses.json", "unimelb_courses.json"]:
        path = Path(__file__).parent.parent / "data" / "courses" / f
        if path.exists():
            with open(path) as fp:
                courses.extend(json.load(fp))
    
    with open(Path(__file__).parent.parent / "data" / "pipeline" / "output" / "tasks_cache.json") as f:
        tasks = json.load(f)
    
    print(f"  Courses: {len(courses)}")
    print(f"  Tasks: {len(tasks)}")
    
    # Map all courses
    all_mappings = []
    total_lo_mapped = 0
    total_task_matches = 0
    
    for i, course in enumerate(courses):
        result = map_course(course, tasks)
        all_mappings.append(result)
        
        lo_mapped = len(result["mappings"])
        task_matches = sum(len(m["matched_tasks"]) for m in result["mappings"])
        total_lo_mapped += lo_mapped
        total_task_matches += task_matches
        
        print(f"[{i+1}/{len(courses)}] {course['code']} ({course['university_code']}): {lo_mapped} LOs → {task_matches} tasks")
    
    # Save output
    output_file = output_dir / "course_task_mappings.json"
    with open(output_file, "w") as f:
        json.dump(all_mappings, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"✅ Saved {len(all_mappings)} course mappings")
    print(f"📊 Learning outcomes with matches: {total_lo_mapped}")
    print(f"🔗 Total task matches: {total_task_matches}")


if __name__ == "__main__":
    main()
