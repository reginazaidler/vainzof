from __future__ import annotations

from dataclasses import dataclass

import requests
import trafilatura
from bs4 import BeautifulSoup


@dataclass
class PageSnapshot:
    page: str
    title: str
    meta_description: str
    h1: str
    h2s: list[str]
    main_content: str


def _safe_text(node) -> str:
    if not node:
        return ""
    return node.get_text(" ", strip=True)


def extract_page_snapshot(url: str, timeout: int = 20) -> PageSnapshot:
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "seo-gap-agent/1.0"})
    response.raise_for_status()
    html = response.text

    soup = BeautifulSoup(html, "html.parser")
    title = _safe_text(soup.find("title"))
    meta_description = ""
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag and meta_tag.get("content"):
        meta_description = meta_tag["content"].strip()

    h1 = _safe_text(soup.find("h1"))
    h2s = [_safe_text(h2) for h2 in soup.find_all("h2") if _safe_text(h2)]

    downloaded = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        no_fallback=False,
    )
    main_content = downloaded or ""

    return PageSnapshot(
        page=url,
        title=title,
        meta_description=meta_description,
        h1=h1,
        h2s=h2s,
        main_content=main_content,
    )
