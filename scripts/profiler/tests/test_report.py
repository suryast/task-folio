# scripts/profiler/tests/test_report.py
import pytest
from profiler.report import generate_markdown, generate_html
from profiler.questionnaire import build_profile, calculate_personalised_score, get_tasks_for_occupation

@pytest.fixture
def sample_profile():
    # Use ANZSCO 1111 (Chief Executives) - exists in data
    tasks = get_tasks_for_occupation(1111)
    if len(tasks) < 2:
        pytest.skip("Not enough tasks for ANZSCO 1111")
    selections = {
        tasks[0]["task_description"]: {"does_task": True, "time_pct": 60},
        tasks[1]["task_description"]: {"does_task": True, "time_pct": 40},
    }
    profile = build_profile(1111, selections)
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
    # Self-contained — no external CSS/JS links
    assert "<style" in html

def test_markdown_includes_timeframes(sample_profile):
    md = generate_markdown(sample_profile)
    # Should mention at least one timeframe
    assert any(tf in md for tf in ["now", "1-2y", "3-5y", "5-10y", "10y+"])

def test_html_is_self_contained(sample_profile):
    html = generate_html(sample_profile)
    # No external CSS/JS dependencies (footer link to taskfolio.ai is fine)
    assert '<link' not in html or '<link' not in html.lower()
    assert 'src="http' not in html
    assert '<script' not in html or 'src=' not in html
