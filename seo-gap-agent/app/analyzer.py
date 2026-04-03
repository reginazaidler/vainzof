from __future__ import annotations

import json
from typing import Any

import requests

from app.prompts import SYSTEM_PROMPT, build_user_prompt


REQUIRED_KEYS = {
    "query_intent",
    "why_not_rank_1",
    "title_fix",
    "opening_paragraph_fix",
    "sections_to_add",
    "faq_to_add",
    "trust_elements_to_add",
    "cta_fix",
    "priority",
}


def _extract_json_object(raw_text: str) -> dict[str, Any]:
    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:].strip()

    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model response did not contain a JSON object")

    parsed = json.loads(raw_text[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("Parsed response is not a JSON object")
    missing = REQUIRED_KEYS - set(parsed.keys())
    if missing:
        raise ValueError(f"Missing required keys from AI response: {sorted(missing)}")
    return parsed


def analyze_page_gap(
    api_key: str,
    model: str,
    payload: dict[str, Any],
    timeout: int = 40,
) -> dict[str, Any]:
    user_prompt = build_user_prompt(
        query=payload["query"],
        page=payload["page"],
        position=payload["position"],
        ctr=payload["ctr"],
        title=payload.get("title", ""),
        meta_description=payload.get("meta_description", ""),
        h1=payload.get("h1", ""),
        h2s=payload.get("h2s", []),
        main_content=payload.get("main_content", ""),
    )

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return _extract_json_object(content)
