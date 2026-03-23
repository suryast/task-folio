# scripts/profiler/tests/test_occupation_search.py
import pytest
from profiler.occupation_search import search_occupations, load_occupations

def test_exact_match():
    occs = load_occupations()
    results = search_occupations(occs, "Software and Applications Programmers")
    assert len(results) > 0
    assert results[0]["anzsco_title"] == "Software and Applications Programmers"

def test_fuzzy_match():
    occs = load_occupations()
    results = search_occupations(occs, "software prog")
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
