#!/usr/bin/env python3
"""
Map university course learning outcomes to TaskFolio job tasks using Claude.
"""

import json
import os
import time
from pathlib import Path
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MAPPING_PROMPT = """You are an expert at mapping university learning outcomes to job tasks.

## Course
Code: {course_code}
Title: {course_title}
University: {university}
Faculty: {faculty}

## Learning Outcomes
{learning_outcomes}

## Available Job Tasks (from TaskFolio - Australian occupations)
{tasks_sample}

## Instructions
For each learning outcome, identify which job task(s) it prepares students for.

Match based on:
1. **Skill transfer** - Does the outcome teach skills directly applicable to the task?
2. **Cognitive level** - Apply/Analyze/Create outcomes map to complex tasks
3. **Domain alignment** - Computing outcomes → computing tasks, etc.

Be selective - only match if there's genuine skill transfer. A course on "programming fundamentals" teaches "Write production code" but NOT "Conduct code reviews" (that requires experience).

## Output Format (JSON only, no markdown)
{{
  "mappings": [
    {{
      "learning_outcome": "Apply fundamental programming concepts...",
      "matched_tasks": [
        {{
          "task_id": 123,
          "task_description": "Writing and maintaining program code",
          "confidence": 0.85,
          "reasoning": "Outcome teaches programming fundamentals directly applicable to code writing"
        }}
      ]
    }}
  ]
}}

Return ONLY valid JSON, no explanation text."""


def load_tasks():
    """Load existing tasks from D1 export or API."""
    # First try local cache
    cache_path = Path(__file__).parent.parent / "data" / "pipeline" / "output" / "tasks_cache.json"
    if cache_path.exists():
        with open(cache_path) as f:
            return json.load(f)
    
    # Otherwise fetch from API
    import subprocess
    result = subprocess.run([
        "curl", "-s", "https://taskfolio-au-api.hello-bb8.workers.dev/api/tasks?limit=500"
    ], capture_output=True, text=True, timeout=30)
    
    tasks = json.loads(result.stdout)
    
    # Cache for future runs
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(tasks, f)
    
    return tasks


def load_courses():
    """Load all scraped courses."""
    courses_dir = Path(__file__).parent.parent / "data" / "courses"
    all_courses = []
    
    for f in courses_dir.glob("*.json"):
        with open(f) as fp:
            courses = json.load(fp)
            all_courses.extend(courses)
    
    return all_courses


def get_relevant_tasks(course, all_tasks):
    """Get tasks relevant to this course's faculty."""
    faculty = course.get("faculty", "Unknown")
    
    # Map faculties to occupation keywords
    faculty_keywords = {
        "Computing": ["software", "developer", "programmer", "data", "analyst", "engineer", "IT", "web", "system"],
        "Engineering": ["engineer", "technical", "design", "system", "project"],
        "Mathematics": ["analyst", "statistician", "actuary", "data", "quantitative"],
        "Science": ["scientist", "researcher", "laboratory", "analyst"],
        "Business": ["accountant", "analyst", "manager", "finance", "business", "marketing"],
        "Psychology": ["psychologist", "counsellor", "researcher", "therapist"],
        "Law": ["lawyer", "solicitor", "barrister", "legal", "paralegal"],
        "Health": ["nurse", "doctor", "health", "medical", "clinical"],
    }
    
    keywords = faculty_keywords.get(faculty, [])
    
    # Filter tasks by occupation title containing keywords
    relevant = []
    for task in all_tasks:
        occ_title = task.get("occupation_title", "").lower()
        if any(kw in occ_title for kw in keywords):
            relevant.append(task)
    
    # If no matches, return general sample
    if not relevant:
        relevant = all_tasks[:100]
    
    # Limit to 50 most relevant
    return relevant[:50]


def map_course(course, tasks):
    """Map one course's learning outcomes to tasks."""
    
    # Format learning outcomes
    los_text = "\n".join(f"{i+1}. {lo}" for i, lo in enumerate(course["learning_outcomes"]))
    
    # Format tasks sample
    tasks_text = "\n".join(
        f"- ID {t['id']}: {t['description']} (Occupation: {t.get('occupation_title', 'Unknown')})"
        for t in tasks
    )
    
    prompt = MAPPING_PROMPT.format(
        course_code=course["code"],
        course_title=course["title"],
        university=course["university"],
        faculty=course.get("faculty", "Unknown"),
        learning_outcomes=los_text,
        tasks_sample=tasks_text
    )
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = message.content[0].text.strip()
    
    # Parse JSON response
    try:
        # Handle potential markdown wrapping
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        result = json.loads(response_text)
        return result.get("mappings", [])
    except json.JSONDecodeError as e:
        print(f"  ⚠ JSON parse error: {e}")
        return []


def main():
    output_dir = Path(__file__).parent.parent / "data" / "course_mappings"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading tasks...")
    all_tasks = load_tasks()
    print(f"  Loaded {len(all_tasks)} tasks")
    
    print("Loading courses...")
    courses = load_courses()
    print(f"  Loaded {len(courses)} courses")
    
    all_mappings = []
    errors = []
    
    for i, course in enumerate(courses):
        code = course["code"]
        print(f"[{i+1}/{len(courses)}] Mapping {code} ({course['university_code']})...", end=" ", flush=True)
        
        try:
            relevant_tasks = get_relevant_tasks(course, all_tasks)
            mappings = map_course(course, relevant_tasks)
            
            # Count total task matches
            total_matches = sum(len(m.get("matched_tasks", [])) for m in mappings)
            
            all_mappings.append({
                "course": course,
                "mappings": mappings
            })
            
            print(f"✓ {len(mappings)} LOs → {total_matches} task matches")
            
            # Save checkpoint every 10 courses
            if (i + 1) % 10 == 0:
                checkpoint_file = output_dir / f"mappings_checkpoint_{i+1}.json"
                with open(checkpoint_file, "w") as f:
                    json.dump(all_mappings, f, indent=2)
                print(f"  💾 Checkpoint saved")
            
        except Exception as e:
            print(f"✗ {e}")
            errors.append(code)
        
        time.sleep(0.5)  # Rate limit
    
    # Save final output
    output_file = output_dir / "course_task_mappings.json"
    with open(output_file, "w") as f:
        json.dump(all_mappings, f, indent=2)
    
    # Summary stats
    total_los = sum(len(m["mappings"]) for m in all_mappings)
    total_task_matches = sum(
        sum(len(lo.get("matched_tasks", [])) for lo in m["mappings"])
        for m in all_mappings
    )
    
    print(f"\n{'='*50}")
    print(f"✅ Saved {len(all_mappings)} course mappings to {output_file}")
    print(f"📊 Total learning outcomes mapped: {total_los}")
    print(f"🔗 Total task matches: {total_task_matches}")
    if errors:
        print(f"⚠ Errors ({len(errors)}): {', '.join(errors)}")


if __name__ == "__main__":
    main()
