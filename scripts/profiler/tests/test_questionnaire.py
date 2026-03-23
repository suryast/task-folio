import pytest
from profiler.questionnaire import (
    get_tasks_for_occupation,
    build_profile,
    calculate_personalised_score,
)


def test_get_tasks_for_occupation():
    tasks = get_tasks_for_occupation("2613")
    assert len(tasks) > 0
    assert all("description" in t for t in tasks)
    assert all("automation_pct" in t for t in tasks)


def test_build_profile_basic():
    tasks = get_tasks_for_occupation("2613")
    selections = {
        tasks[0]["id"]: {"does_task": True, "time_pct": 50},
        tasks[1]["id"]: {"does_task": True, "time_pct": 30},
        tasks[2]["id"]: {"does_task": True, "time_pct": 20},
    }
    profile = build_profile("2613", selections)
    assert profile["anzsco_code"] == "2613"
    assert len(profile["selected_tasks"]) == 3
    assert sum(t["time_pct"] for t in profile["selected_tasks"]) == 100


def test_calculate_personalised_score():
    tasks = get_tasks_for_occupation("2613")
    selections = {
        tasks[0]["id"]: {"does_task": True, "time_pct": 100},
    }
    profile = build_profile("2613", selections)
    score = calculate_personalised_score(profile)
    assert 0 <= score["overall_exposure"] <= 1
    assert "automation_weighted" in score
    assert "augmentation_weighted" in score
    assert "timeframe_breakdown" in score
    assert isinstance(score["timeframe_breakdown"], dict)


def test_score_differs_by_task_selection():
    """Different task selections should produce different scores."""
    tasks = get_tasks_for_occupation("2613")
    sel_a = {tasks[0]["id"]: {"does_task": True, "time_pct": 100}}
    sel_b = {tasks[-1]["id"]: {"does_task": True, "time_pct": 100}}
    score_a = calculate_personalised_score(build_profile("2613", sel_a))
    score_b = calculate_personalised_score(build_profile("2613", sel_b))
    assert score_a != score_b or len(tasks) == 1
