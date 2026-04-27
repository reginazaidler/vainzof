from __future__ import annotations


SYSTEM_PROMPT = """You are an elite SEO strategist. Analyze page/query gaps.
Return STRICT JSON only. No markdown. No extra keys.
If uncertain, still provide best-effort actionable recommendations.
"""


def build_user_prompt(
    query: str,
    page: str,
    position: float,
    ctr: float,
    is_new_query: bool,
    title: str,
    meta_description: str,
    h1: str,
    h2s: list[str],
    main_content: str,
) -> str:
    h2_block = "\n".join(f"- {h}" for h in h2s[:20])
    content_preview = main_content[:6000]

    return f"""
Analyze why this page is not ranking #1 for the target query and provide exact fixes.

Target query: {query}
Page URL: {page}
Current avg position: {position:.2f}
Current CTR: {ctr:.4f}
Is new query in this property's history: {"yes" if is_new_query else "no"}

Page signals:
Title: {title}
Meta description: {meta_description}
H1: {h1}
H2s:
{h2_block}
Main content excerpt:
{content_preview}

Return JSON exactly in this schema:
{{
  "query_intent": "",
  "why_not_rank_1": [],
  "title_fix": "",
  "opening_paragraph_fix": "",
  "sections_to_add": [],
  "faq_to_add": [],
  "trust_elements_to_add": [],
  "cta_fix": "",
  "priority": "low|medium|high",
  "recommended_action": "improve_existing_page|create_new_page",
  "new_page_slug": ""
}}

Rules:
- Focus on intent mismatch, missing content, weak structure, weak CTR/title, trust and CTA gaps.
- Make recommendations specific and implementation-ready.
- Keep arrays concise (3-7 items max).
- If this is a new query and current page intent mismatch is strong, set recommended_action=create_new_page.
- If recommended_action=improve_existing_page, new_page_slug must be an empty string.
- If recommended_action=create_new_page, provide a short kebab-case slug in English.
""".strip()
