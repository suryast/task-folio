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
            f"- {t['description']} ({t['time_pct']}% of time, auto={t['automation_pct']}, aug={t['augmentation_pct']})"
            for t in profile["selected_tasks"]
        )
        user_msg = f"Occupation: {profile['occupation_title']}\n\nTasks:\n{task_summary}"

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
