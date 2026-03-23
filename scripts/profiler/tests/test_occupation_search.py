import pytest
from profiler.occupation_search import search_occupations, load_occupations


def test_exact_match():
    occs = load_occupations()
    results = search_occupations(occs, "Chief Executives and Managing Directors")
    assert len(results) > 0
    assert results[0]["occupation_title"] == "Chief Executives and Managing Directors"


def test_fuzzy_match():
    occs = load_occupations()
    results = search_occupations(occs, "software developer")
    assert len(results) > 0
    assert any("Software" in r["occupation_title"] for r in results)


def test_partial_match():
    occs = load_occupations()
    results = search_occupations(occs, "nurse")
    assert len(results) > 0


def test_no_match():
    occs = load_occupations()
    results = search_occupations(occs, "zzzqqxxyyzz999")
    assert len(results) == 0


def test_returns_max_10():
    occs = load_occupations()
    results = search_occupations(occs, "manager")
    assert len(results) <= 10
