from __future__ import annotations

import json
import random
import time
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
    max_attempts: int = 6,
    base_retry_delay_seconds: float = 1.0,
    max_retry_delay_seconds: float = 45.0,
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

    request_payload = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }

    last_response: requests.Response | None = None
    for attempt in range(1, max_attempts + 1):
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=request_payload,
            timeout=timeout,
        )
        last_response = response

        if response.ok:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return _extract_json_object(content)

        retryable_status_codes = {429, 500, 502, 503, 504}
        if response.status_code in retryable_status_codes and attempt < max_attempts:
            retry_after = response.headers.get("Retry-After")
            if retry_after is not None:
                try:
                    sleep_seconds = float(retry_after)
                except ValueError:
                    sleep_seconds = 0.0
            else:
                exponential_delay = min(max_retry_delay_seconds, base_retry_delay_seconds * (2 ** (attempt - 1)))
                sleep_seconds = exponential_delay + random.uniform(0.0, 0.75)

            print(
                "OpenAI request failed with retryable status"
                f" {response.status_code} (attempt {attempt}/{max_attempts})."
                f" Retrying in {sleep_seconds:.2f}s..."
            )
            time.sleep(max(0.0, sleep_seconds))
            continue

        if response.status_code in retryable_status_codes and attempt == max_attempts:
            break

        response.raise_for_status()

    if last_response is not None and last_response.status_code in {429, 500, 502, 503, 504}:
        print(
            "OpenAI analysis failed after retries. "
            f"Returning fallback payload (status={last_response.status_code})."
        )
        return {
            "query_intent": "unknown",
            "why_not_rank_1": [
                "OpenAI request limit/server error during analysis"
            ],
            "title_fix": "Retry this run later to generate title recommendations.",
            "opening_paragraph_fix": "Retry this run later to generate opening paragraph recommendations.",
            "sections_to_add": ["Retry analysis after rate limit window resets"],
            "faq_to_add": ["What should we improve once analysis is available?"],
            "trust_elements_to_add": ["N/A (rate-limited run)"],
            "cta_fix": "Retry this run later to generate CTA recommendations.",
            "priority": "low",
            "_meta": {
                "fallback_reason": "openai_retryable_error",
                "status_code": last_response.status_code,
            },
        }

    raise RuntimeError("OpenAI analysis failed without a successful response")
