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

        if score > 0.5:  # Stricter threshold to reduce noise
            scored.append((score, occ))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [occ for _, occ in scored[:limit]]
