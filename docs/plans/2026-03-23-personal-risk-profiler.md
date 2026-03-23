# Personal Risk Profiler — Implementation Plan

> **For Claude:** Use the `executing-plans` skill to implement this plan task-by-task.

**Goal:** Let anyone clone the repo, run a local questionnaire about their job tasks, optionally enrich with a local LLM, and get a personalised AI exposure report — no API, no MCP, no service.

**Architecture:** Python CLI (`scripts/profiler.py`) reads master data from `data/pipeline/output/taskfolio_master_data.json`, runs an interactive questionnaire, optionally enriches via local LLM (ollama/llama.cpp/any OpenAI-compatible endpoint), and outputs both Markdown and self-contained HTML reports. AGENTS.md is updated to point coding agents at the data + profiler.

**Tech Stack:** Python 3.11+ (stdlib + jinja2 for HTML), no heavy deps. Optional: any OpenAI-compatible API for enrichment.

**Data flow:**
```
User clones repo
  → python scripts/profiler.py
  → Select occupation (fuzzy search)
  → Questionnaire: which tasks they do, time allocation, context
  → [Optional] LLM enrichment: custom tasks, workplace nuance
  → Personalised score + Markdown report + HTML report
```

---

### Task 1: Occupation Fuzzy Search Module

**Files:**
- Create: `scripts/profiler/occupation_search.py`
- Test: `scripts/profiler/tests/test_occupation_search.py`

**Step 1: Write the failing test**

```python
# scripts/profiler/tests/test_occupation_search.py
import pytest
from profiler.occupation_search import search_occupations, load_occupations

def test_exact_match():
    occs = load_occupations()
    results = search_occupations(occs, "Software Engineer")
    assert len(results) > 0
    assert results[0]["anzsco_title"] == "Software Engineer"

def test_fuzzy_match():
    occs = load_occupations()
    results = search_occupations(occs, "softwar eng")
    assert len(results) > 0
    assert "Software" in results[0]["anzsco_title"]

def test_partial_match():
    occs = load_occupations()
    results = search_occupations(occs, "nurse")
    assert len(results) > 0

def test_no_match():
    occs = load_occupations()
    results = search_occupations(occs, "xyzzyflorp")
    assert len(results) == 0

def test_returns_max_10():
    occs = load_occupations()
    results = search_occupations(occs, "manager")
    assert len(results) <= 10
```

**Step 2: Run test to verify it fails**

Run: `cd ~/projects/task-folio && python -m pytest scripts/profiler/tests/test_occupation_search.py -v`
Expected: FAIL — module not found

**Step 3: Write implementation**

```python
# scripts/profiler/occupation_search.py
"""Fuzzy occupation search over TaskFolio master data."""
from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "pipeline" / "output" / "taskfolio_master_data.json"


def load_occupations() -> list[dict]:
    """Load unique occupations from master data."""
    with open(DATA_PATH) as f:
        tasks = json.load(f)
    seen = set()
    occupations = []
    for t in tasks:
        key = t["anzsco_code"]
        if key not in seen:
            seen.add(key)
            occupations.append({
                "anzsco_code": t["anzsco_code"],
                "anzsco_title": t["anzsco_title"],
                "onet_soc_code": t.get("onet_soc_code"),
                "occupation_title": t.get("occupation_title"),
            })
    return occupations


def search_occupations(occupations: list[dict], query: str, limit: int = 10) -> list[dict]:
    """Fuzzy search occupations by title. Returns top matches."""
    query_lower = query.lower().strip()
    if not query_lower:
        return []

    scored = []
    for occ in occupations:
        title = occ["anzsco_title"].lower()
        alt = (occ.get("occupation_title") or "").lower()

        # Exact substring match scores highest
        if query_lower in title or query_lower in alt:
            score = 0.9 + SequenceMatcher(None, query_lower, title).ratio() * 0.1
        else:
            score = max(
                SequenceMatcher(None, query_lower, title).ratio(),
                SequenceMatcher(None, query_lower, alt).ratio(),
            )

        if score > 0.3:
            scored.append((score, occ))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [occ for _, occ in scored[:limit]]
```

**Step 4: Create `__init__.py` files**

```bash
touch scripts/profiler/__init__.py
touch scripts/profiler/tests/__init__.py
```

**Step 5: Run test to verify it passes**

Run: `cd ~/projects/task-folio && python -m pytest scripts/profiler/tests/test_occupation_search.py -v`
Expected: 5 PASS

**Step 6: Commit**

```bash
git add scripts/profiler/
git commit -m "feat(profiler): add occupation fuzzy search module"
```

---

### Task 2: Questionnaire Engine

**Files:**
- Create: `scripts/profiler/questionnaire.py`
- Test: `scripts/profiler/tests/test_questionnaire.py`

**Step 1: Write the failing test**

```python
# scripts/profiler/tests/test_questionnaire.py
import json
import pytest
from profiler.questionnaire import (
    get_tasks_for_occupation,
    build_profile,
    calculate_personalised_score,
)

def test_get_tasks_for_occupation():
    tasks = get_tasks_for_occupation(261312)  # Software Engineer
    assert len(tasks) > 0
    assert all("task_description" in t for t in tasks)
    assert all("automation_pct" in t for t in tasks)

def test_build_profile_basic():
    tasks = get_tasks_for_occupation(261312)
    # Simulate: user does first 3 tasks, 50/30/20 time split
    selections = {
        tasks[0]["task_id"]: {"does_task": True, "time_pct": 50},
        tasks[1]["task_id"]: {"does_task": True, "time_pct": 30},
        tasks[2]["task_id"]: {"does_task": True, "time_pct": 20},
    }
    profile = build_profile(261312, selections)
    assert profile["anzsco_code"] == 261312
    assert len(profile["selected_tasks"]) == 3
    assert sum(t["time_pct"] for t in profile["selected_tasks"]) == 100

def test_calculate_personalised_score():
    tasks = get_tasks_for_occupation(261312)
    selections = {
        tasks[0]["task_id"]: {"does_task": True, "time_pct": 100},
    }
    profile = build_profile(261312, selections)
    score = calculate_personalised_score(profile)
    assert 0 <= score["overall_exposure"] <= 1
    assert "automation_weighted" in score
    assert "augmentation_weighted" in score
    assert "timeframe_breakdown" in score
    assert isinstance(score["timeframe_breakdown"], dict)

def test_score_differs_by_task_selection():
    """Different task selections should produce different scores."""
    tasks = get_tasks_for_occupation(261312)
    sel_a = {tasks[0]["task_id"]: {"does_task": True, "time_pct": 100}}
    sel_b = {tasks[-1]["task_id"]: {"does_task": True, "time_pct": 100}}
    score_a = calculate_personalised_score(build_profile(261312, sel_a))
    score_b = calculate_personalised_score(build_profile(261312, sel_b))
    # Scores should differ (different tasks have different exposure)
    assert score_a != score_b or len(tasks) == 1
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest scripts/profiler/tests/test_questionnaire.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# scripts/profiler/questionnaire.py
"""Task questionnaire and personalised score calculation."""
from __future__ import annotations

import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "pipeline" / "output" / "taskfolio_master_data.json"

_cache: list[dict] | None = None


def _load_all_tasks() -> list[dict]:
    global _cache
    if _cache is None:
        with open(DATA_PATH) as f:
            _cache = json.load(f)
    return _cache


def get_tasks_for_occupation(anzsco_code: int) -> list[dict]:
    """Get all tasks for an ANZSCO occupation code."""
    return [t for t in _load_all_tasks() if t["anzsco_code"] == anzsco_code]


def build_profile(anzsco_code: int, selections: dict) -> dict:
    """Build a user profile from task selections.

    selections: {task_id: {"does_task": bool, "time_pct": float}}
    """
    all_tasks = {t["task_id"]: t for t in get_tasks_for_occupation(anzsco_code)}

    selected = []
    for task_id, sel in selections.items():
        if sel.get("does_task") and task_id in all_tasks:
            task = all_tasks[task_id].copy()
            task["time_pct"] = sel["time_pct"]
            selected.append(task)

    occ_info = get_tasks_for_occupation(anzsco_code)[0] if get_tasks_for_occupation(anzsco_code) else {}

    return {
        "anzsco_code": anzsco_code,
        "anzsco_title": occ_info.get("anzsco_title", "Unknown"),
        "selected_tasks": selected,
        "total_tasks_available": len(all_tasks),
        "tasks_selected": len(selected),
    }


def calculate_personalised_score(profile: dict) -> dict:
    """Calculate personalised AI exposure score weighted by time allocation."""
    tasks = profile["selected_tasks"]
    if not tasks:
        return {
            "overall_exposure": 0,
            "automation_weighted": 0,
            "augmentation_weighted": 0,
            "timeframe_breakdown": {},
        }

    total_time = sum(t["time_pct"] for t in tasks)
    if total_time == 0:
        total_time = 1  # avoid division by zero

    auto_weighted = sum(t["automation_pct"] * t["time_pct"] for t in tasks) / total_time
    aug_weighted = sum(t["augmentation_pct"] * t["time_pct"] for t in tasks) / total_time

    # Overall exposure = max of automation + augmentation, capped at 1
    overall = min(auto_weighted + aug_weighted, 1.0)

    # Timeframe breakdown: weighted by time
    timeframes: dict[str, float] = {}
    for t in tasks:
        tf = t.get("timeframe", "unknown")
        timeframes[tf] = timeframes.get(tf, 0) + t["time_pct"]
    # Normalise to percentages
    for tf in timeframes:
        timeframes[tf] = round(timeframes[tf] / total_time * 100, 1)

    return {
        "overall_exposure": round(overall, 3),
        "automation_weighted": round(auto_weighted, 3),
        "augmentation_weighted": round(aug_weighted, 3),
        "timeframe_breakdown": timeframes,
    }
```

**Step 4: Run tests**

Run: `python -m pytest scripts/profiler/tests/test_questionnaire.py -v`
Expected: 4 PASS

**Step 5: Commit**

```bash
git add scripts/profiler/questionnaire.py scripts/profiler/tests/test_questionnaire.py
git commit -m "feat(profiler): add questionnaire engine with personalised scoring"
```

---

### Task 3: LLM Enrichment Module (Optional)

**Files:**
- Create: `scripts/profiler/enrichment.py`
- Test: `scripts/profiler/tests/test_enrichment.py`

**Step 1: Write the failing test**

```python
# scripts/profiler/tests/test_enrichment.py
import pytest
from unittest.mock import patch, MagicMock
from profiler.enrichment import enrich_profile, is_llm_available

def test_is_llm_available_no_endpoint():
    assert is_llm_available(endpoint=None) is False

def test_is_llm_available_with_endpoint():
    with patch("profiler.enrichment._check_endpoint", return_value=True):
        assert is_llm_available(endpoint="http://localhost:11434/v1") is True

def test_enrich_profile_adds_insights():
    profile = {
        "anzsco_code": 261312,
        "anzsco_title": "Software Engineer",
        "selected_tasks": [
            {"task_description": "Write code", "time_pct": 80, "automation_pct": 0.3, "augmentation_pct": 0.8}
        ],
    }
    mock_response = {
        "custom_tasks": ["Review AI-generated code for correctness"],
        "workplace_context": "Startup with heavy AI tooling adoption",
        "risk_adjustments": {"task_0": {"rationale": "Already using Copilot", "adjustment": 0.1}},
    }
    with patch("profiler.enrichment._call_llm", return_value=mock_response):
        enriched = enrich_profile(profile, endpoint="http://localhost:11434/v1")
    assert "enrichment" in enriched
    assert enriched["enrichment"]["custom_tasks"] == mock_response["custom_tasks"]

def test_enrich_profile_graceful_failure():
    """LLM failure should not crash — returns profile unchanged."""
    profile = {"selected_tasks": [], "anzsco_title": "Test"}
    with patch("profiler.enrichment._call_llm", side_effect=Exception("connection refused")):
        result = enrich_profile(profile, endpoint="http://bad:1234/v1")
    assert "enrichment" not in result or result.get("enrichment_error")
```

**Step 2: Run test to verify it fails**

**Step 3: Write implementation**

```python
# scripts/profiler/enrichment.py
"""Optional LLM enrichment for personalised profiles."""
from __future__ import annotations

import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI job analyst. Given an occupation and the user's selected tasks with time allocation, provide:
1. custom_tasks: Up to 3 additional tasks the user might do that aren't in the standard list
2. workplace_context: A brief description of their likely work environment based on their task mix
3. risk_adjustments: For each task (keyed as task_0, task_1, ...), suggest an adjustment (-0.2 to +0.2) to the automation score with rationale

Respond ONLY with valid JSON matching this schema:
{"custom_tasks": [...], "workplace_context": "...", "risk_adjustments": {"task_0": {"rationale": "...", "adjustment": 0.0}, ...}}"""


def _check_endpoint(endpoint: str) -> bool:
    """Check if an OpenAI-compatible endpoint is reachable."""
    try:
        url = endpoint.rstrip("/") + "/models"
        req = urllib.request.Request(url, method="GET")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def is_llm_available(endpoint: str | None = None) -> bool:
    if not endpoint:
        return False
    return _check_endpoint(endpoint)


def _call_llm(endpoint: str, messages: list[dict], model: str = "llama3.2") -> dict:
    """Call an OpenAI-compatible chat completions endpoint."""
    url = endpoint.rstrip("/") + "/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }).encode()

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())

    content = data["choices"][0]["message"]["content"]
    return json.loads(content)


def enrich_profile(
    profile: dict,
    endpoint: str,
    model: str = "llama3.2",
) -> dict:
    """Enrich a profile with LLM-generated insights. Fails gracefully."""
    try:
        task_summary = "\n".join(
            f"- {t['task_description']} ({t['time_pct']}% of time, auto={t['automation_pct']}, aug={t['augmentation_pct']})"
            for t in profile["selected_tasks"]
        )
        user_msg = f"Occupation: {profile['anzsco_title']}\n\nTasks:\n{task_summary}"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ]
        result = _call_llm(endpoint, messages, model)
        profile["enrichment"] = result
    except Exception as e:
        logger.warning("LLM enrichment failed: %s", e)
        profile["enrichment_error"] = str(e)

    return profile
```

**Step 4: Run tests**

Run: `python -m pytest scripts/profiler/tests/test_enrichment.py -v`
Expected: 4 PASS

**Step 5: Commit**

```bash
git add scripts/profiler/enrichment.py scripts/profiler/tests/test_enrichment.py
git commit -m "feat(profiler): add optional LLM enrichment module"
```

---

### Task 4: Report Generator (Markdown + HTML)

**Files:**
- Create: `scripts/profiler/report.py`
- Create: `scripts/profiler/templates/report.html`
- Test: `scripts/profiler/tests/test_report.py`

**Step 1: Write the failing test**

```python
# scripts/profiler/tests/test_report.py
import pytest
from profiler.report import generate_markdown, generate_html
from profiler.questionnaire import build_profile, calculate_personalised_score, get_tasks_for_occupation

@pytest.fixture
def sample_profile():
    tasks = get_tasks_for_occupation(261312)
    selections = {
        tasks[0]["task_id"]: {"does_task": True, "time_pct": 60},
        tasks[1]["task_id"]: {"does_task": True, "time_pct": 40},
    }
    profile = build_profile(261312, selections)
    profile["score"] = calculate_personalised_score(profile)
    return profile

def test_generate_markdown(sample_profile):
    md = generate_markdown(sample_profile)
    assert "Software Engineer" in md or "261312" in md
    assert "overall" in md.lower() or "exposure" in md.lower()
    assert "%" in md

def test_generate_html(sample_profile):
    html = generate_html(sample_profile)
    assert "<html" in html
    assert "Software Engineer" in html or "261312" in html
    assert "</html>" in html
    # Self-contained — no external CSS/JS links
    assert "<style" in html

def test_markdown_includes_timeframes(sample_profile):
    md = generate_markdown(sample_profile)
    # Should mention at least one timeframe
    assert any(tf in md for tf in ["now", "1-2y", "3-5y", "5-10y", "10y+"])

def test_html_is_self_contained(sample_profile):
    html = generate_html(sample_profile)
    # No external resource links
    assert 'href="http' not in html
    assert 'src="http' not in html
```

**Step 2: Run test to verify it fails**

**Step 3: Write implementation**

`scripts/profiler/report.py` — Markdown generator + HTML template using string formatting (no jinja2 dep to keep it zero-dep).

`scripts/profiler/templates/report.html` — Self-contained HTML template with inline CSS, neobrutal style matching the site, bar charts via pure CSS.

(Implementation is straightforward — Markdown is f-string formatted tables, HTML is a template string with CSS variables for the neobrutal palette.)

**Step 4: Run tests, commit**

```bash
git commit -m "feat(profiler): add markdown + HTML report generators"
```

---

### Task 5: Interactive CLI

**Files:**
- Create: `scripts/profiler/__main__.py` (entry point)
- Create: `scripts/profiler/cli.py`

**Step 1: Write the CLI**

```python
# scripts/profiler/cli.py
"""Interactive CLI for TaskFolio personal risk profiler."""
from __future__ import annotations

import sys
from .occupation_search import load_occupations, search_occupations
from .questionnaire import get_tasks_for_occupation, build_profile, calculate_personalised_score
from .enrichment import is_llm_available, enrich_profile
from .report import generate_markdown, generate_html


def run():
    """Main interactive flow."""
    print("\n🎯 TaskFolio Personal Risk Profiler")
    print("=" * 40)

    # Step 1: Find occupation
    occupations = load_occupations()
    print(f"\n📊 {len(occupations)} occupations loaded.\n")

    query = input("What's your job title? > ").strip()
    if not query:
        print("No input. Exiting.")
        return

    matches = search_occupations(occupations, query)
    if not matches:
        print("No matching occupations found. Try a different title.")
        return

    print("\nMatches:")
    for i, m in enumerate(matches, 1):
        print(f"  {i}. {m['anzsco_title']} (ANZSCO {m['anzsco_code']})")

    choice = input(f"\nSelect [1-{len(matches)}]: ").strip()
    try:
        selected_occ = matches[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    anzsco = selected_occ["anzsco_code"]

    # Step 2: Task questionnaire
    tasks = get_tasks_for_occupation(anzsco)
    print(f"\n📋 {selected_occ['anzsco_title']} has {len(tasks)} tasks.\n")

    # Quick mode: show tasks, user picks which they do
    print("Which of these tasks do you perform? (y/n/s to skip rest)\n")

    selections = {}
    selected_tasks = []
    for i, task in enumerate(tasks, 1):
        ans = input(f"  {i}/{len(tasks)}: {task['task_description']}\n         [y/n/s] > ").strip().lower()
        if ans == "s":
            break
        if ans == "y":
            selected_tasks.append(task)
            selections[task["task_id"]] = {"does_task": True, "time_pct": 0}

    if not selected_tasks:
        print("No tasks selected. Exiting.")
        return

    # Time allocation
    print(f"\n⏱️  Allocate your time across {len(selected_tasks)} selected tasks (must total 100%):\n")
    remaining = 100
    for i, task in enumerate(selected_tasks):
        desc_short = task["task_description"][:60]
        if i == len(selected_tasks) - 1:
            pct = remaining
            print(f"  {desc_short}... → {pct}% (remainder)")
        else:
            pct_input = input(f"  {desc_short}...\n  Time % (remaining {remaining}%): > ").strip()
            try:
                pct = min(int(pct_input), remaining)
            except ValueError:
                pct = remaining // (len(selected_tasks) - i)
        selections[task["task_id"]]["time_pct"] = pct
        remaining -= pct

    # Step 3: Build profile + score
    profile = build_profile(anzsco, selections)
    profile["score"] = calculate_personalised_score(profile)

    # Step 4: Optional LLM enrichment
    llm_endpoint = None
    enrich = input("\n🤖 Enrich with local LLM? (requires Ollama or compatible) [y/N] > ").strip().lower()
    if enrich == "y":
        llm_endpoint = input("  Endpoint [http://localhost:11434/v1]: > ").strip()
        if not llm_endpoint:
            llm_endpoint = "http://localhost:11434/v1"
        model = input("  Model [llama3.2]: > ").strip() or "llama3.2"
        if is_llm_available(llm_endpoint):
            print("  Enriching...")
            profile = enrich_profile(profile, llm_endpoint, model)
            if "enrichment_error" in profile:
                print(f"  ⚠️  Enrichment failed: {profile['enrichment_error']}")
            else:
                print("  ✅ Enriched!")
        else:
            print(f"  ⚠️  Endpoint not reachable: {llm_endpoint}")

    # Step 5: Generate reports
    md = generate_markdown(profile)
    print("\n" + md)

    save = input("\n💾 Save reports? [Y/n] > ").strip().lower()
    if save != "n":
        from pathlib import Path
        out_dir = Path("reports")
        out_dir.mkdir(exist_ok=True)
        slug = selected_occ["anzsco_title"].lower().replace(" ", "-")

        md_path = out_dir / f"{slug}-report.md"
        md_path.write_text(md)
        print(f"  📄 {md_path}")

        html = generate_html(profile)
        html_path = out_dir / f"{slug}-report.html"
        html_path.write_text(html)
        print(f"  🌐 {html_path}")

    print("\nDone! 🎯")
```

```python
# scripts/profiler/__main__.py
from profiler.cli import run

if __name__ == "__main__":
    run()
```

**Step 2: Test manually**

Run: `cd ~/projects/task-folio && python -m profiler` (from scripts/ dir)

**Step 3: Commit**

```bash
git commit -m "feat(profiler): add interactive CLI entry point"
```

---

### Task 6: Update AGENTS.md

**Files:**
- Modify: `AGENTS.md`

**Step 1: Add profiler section to AGENTS.md**

Append to AGENTS.md:

```markdown
## Personal Risk Profiler

TaskFolio includes a local personal risk profiler that agents can run for users.

### Data
- Master dataset: `data/pipeline/output/taskfolio_master_data.json` (6,690 tasks across 361 occupations)
- Each task has: `task_description`, `automation_pct`, `augmentation_pct`, `timeframe`, `confidence`, `source`
- Occupations use ANZSCO codes (Australian) with O*NET crosswalk

### Running the Profiler
```bash
cd scripts && python -m profiler
```

### Agent Workflow (non-interactive)
For coding agents that can't do interactive prompts, use the modules directly:

```python
from profiler.occupation_search import load_occupations, search_occupations
from profiler.questionnaire import get_tasks_for_occupation, build_profile, calculate_personalised_score
from profiler.enrichment import enrich_profile
from profiler.report import generate_markdown, generate_html

# 1. Find occupation
occs = load_occupations()
matches = search_occupations(occs, "registered nurse")

# 2. Get tasks + build profile
tasks = get_tasks_for_occupation(matches[0]["anzsco_code"])
selections = {t["task_id"]: {"does_task": True, "time_pct": 100/len(tasks)} for t in tasks}
profile = build_profile(matches[0]["anzsco_code"], selections)
profile["score"] = calculate_personalised_score(profile)

# 3. Optional: enrich with local LLM
# profile = enrich_profile(profile, endpoint="http://localhost:11434/v1")

# 4. Generate reports
print(generate_markdown(profile))
html = generate_html(profile)
```

### Enrichment
The profiler can optionally call any OpenAI-compatible endpoint (Ollama, llama.cpp, LM Studio) to:
- Suggest custom tasks not in the standard list
- Infer workplace context from task selections
- Adjust automation scores based on user's specific situation

No API key needed for local models. No data leaves the machine.
```

**Step 2: Commit**

```bash
git commit -m "docs: add personal risk profiler section to AGENTS.md"
```

---

### Task 7: Add reports/ to .gitignore + README update

**Files:**
- Modify: `.gitignore`
- Modify: `README.md`

**Step 1: Add reports/ to .gitignore**

```
# Personal profiler reports
reports/
```

**Step 2: Add profiler section to README**

Add after the System Architecture section:

```markdown
## 🎯 Personal Risk Profiler

Get a personalised AI exposure analysis for YOUR specific job:

```bash
git clone https://github.com/suryast/task-folio.git
cd task-folio/scripts
python -m profiler
```

**What it does:**
1. Search for your occupation (fuzzy matching across 361 jobs)
2. Select which tasks you actually perform
3. Allocate your time across tasks
4. (Optional) Enrich with a local LLM for custom insights
5. Get a personalised Markdown + HTML report

**No API keys. No data leaves your machine. No services to run.**

### Requirements
- Python 3.11+
- (Optional) [Ollama](https://ollama.ai) or any OpenAI-compatible local LLM for enrichment

### For AI Agents
See `AGENTS.md` for programmatic usage — point your coding agent at the repo and it can generate personalised reports using the Python modules directly.
```

**Step 3: Commit + push**

```bash
git add .gitignore README.md
git commit -m "docs: add profiler to README + gitignore reports/"
git push origin main
```

---

## Summary

| Task | What | Est. |
|------|------|------|
| 1 | Occupation fuzzy search | 5 min |
| 2 | Questionnaire engine + scoring | 5 min |
| 3 | LLM enrichment (optional) | 5 min |
| 4 | Report generator (MD + HTML) | 10 min |
| 5 | Interactive CLI | 5 min |
| 6 | AGENTS.md update | 3 min |
| 7 | .gitignore + README | 3 min |

**Total: ~36 min. Zero external deps. No MCP. No service. Clone and go.**
