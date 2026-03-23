import pytest
from profiler.report import generate_markdown, generate_html
from profiler.questionnaire import build_profile, calculate_personalised_score, get_tasks_for_occupation


@pytest.fixture
def sample_profile():
    tasks = get_tasks_for_occupation("1111")  # Chief Executives
    if len(tasks) < 2:
        pytest.skip("Not enough tasks for ANZSCO 1111")
    selections = {
        tasks[0]["id"]: {"does_task": True, "time_pct": 60},
        tasks[1]["id"]: {"does_task": True, "time_pct": 40},
    }
    profile = build_profile("1111", selections)
    profile["score"] = calculate_personalised_score(profile)
    return profile


def test_generate_markdown(sample_profile):
    md = generate_markdown(sample_profile)
    assert "Chief Executives" in md or "1111" in md
    assert "overall" in md.lower() or "exposure" in md.lower()
    assert "%" in md


def test_generate_html(sample_profile):
    html = generate_html(sample_profile)
    assert "<html" in html
    assert "Chief Executives" in html or "1111" in html
    assert "</html>" in html
    assert "<style" in html


def test_markdown_includes_timeframes(sample_profile):
    md = generate_markdown(sample_profile)
    assert any(tf in md for tf in ["now", "1-2y", "3-5y", "5-10y", "10y+"])


def test_html_is_self_contained(sample_profile):
    html = generate_html(sample_profile)
    assert 'src="http' not in html
