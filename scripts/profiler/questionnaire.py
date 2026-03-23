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


def get_tasks_for_occupation(anzsco_code: int | str) -> list[dict]:
    """Get all tasks for an ANZSCO occupation code."""
    # Normalize to string for comparison (data has mixed int/str)
    code_str = str(anzsco_code)
    return [t for t in _load_all_tasks() if str(t["anzsco_code"]) == code_str]


def build_profile(anzsco_code: int | str, selections: dict) -> dict:
    """Build a user profile from task selections.

    selections: {task_description: {"does_task": bool, "time_pct": float}}
    """
    all_tasks = {t["task_description"]: t for t in get_tasks_for_occupation(anzsco_code)}

    selected = []
    for task_desc, sel in selections.items():
        if sel.get("does_task") and task_desc in all_tasks:
            task = all_tasks[task_desc].copy()
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
