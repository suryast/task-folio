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
        "anzsco_code": "2613",
        "anzsco_title": "Software and Applications Programmers",
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
