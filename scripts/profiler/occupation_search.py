"""Fuzzy occupation search over TaskFolio data."""
from __future__ import annotations

import json
from difflib import SequenceMatcher
from pathlib import Path

# Use the public tasks_cache.json which is tracked in git
DATA_PATH = Path(__file__).parent.parent.parent / "public" / "data" / "pipeline" / "output" / "tasks_cache.json"


def load_occupations() -> list[dict]:
    """Load unique occupations from task data."""
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
                "occupation_title": t["occupation_title"],
            })
    return occupations


def search_occupations(occupations: list[dict], query: str, limit: int = 10) -> list[dict]:
    """Fuzzy search occupations by title. Returns top matches."""
    query_lower = query.lower().strip()
    if not query_lower:
        return []

    scored = []
    for occ in occupations:
        title = occ["occupation_title"].lower()

        # Exact substring match scores highest
        if query_lower in title:
            score = 0.9 + SequenceMatcher(None, query_lower, title).ratio() * 0.1
        else:
            score = SequenceMatcher(None, query_lower, title).ratio()

        if score > 0.3:
            scored.append((score, occ))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [occ for _, occ in scored[:limit]]
