from __future__ import annotations

import logging
from dataclasses import dataclass
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from readability import Document  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)  # fields are immutable
class ExtractedResult:
    title: str
    text: str


def _html_to_text(html: str) -> str:
    """Returns text from an HTML document."""
    page = BeautifulSoup(html, "lxml")

    # ignore tags without meaningful content
    for tag in page(["script", "style", "noscript"]):
        tag.decompose()

    # normalize whitespace
    text = page.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n\n".join(lines)


def _title_from_url(url: str) -> str:
    """Returns a human-readable fallback title from a URL."""
    parsed = urlparse(url)
    if parsed.netloc:
        return parsed.netloc + parsed.path
    return url


def extract_content(*, html: str, url: str) -> ExtractedResult:
    """Extracts parsed HTML content with a fallback to return the entire page."""
    try:
        document = Document(html)
        content_html = document.summary(html_partial=True)
        text = _html_to_text(content_html)

        if text.strip():
            title = (document.short_title() or "").strip() or _title_from_url(url)
            return ExtractedResult(title=title, text=text)

    except Exception:
        # fall back safely if extraction fails
        logger.debug("readability extraction failed", exc_info=True)

    # fallback to the entire page with a derived title
    page = BeautifulSoup(html, "lxml")
    page_title = page.title.get_text(strip=True) if page.title else ""
    title = page_title or _title_from_url(url)
    text = _html_to_text(html)
    return ExtractedResult(title=title, text=text)
