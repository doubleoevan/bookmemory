from __future__ import annotations

import logging
from dataclasses import dataclass
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from readability import Document  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

# the summary must cover a reasonable percentage of the page,
# or we fall back to the full page content
MINIMUM_SUMMARY_LENGTH = 800
MINIMUM_SUMMARY_COVERAGE = 0.35


@dataclass(frozen=True)  # fields are immutable
class ExtractedResult:
    title: str
    text: str


def _html_to_text(html: str) -> str:
    """Returns text from an HTML document."""
    page = BeautifulSoup(html, "lxml")

    # ignore tags without meaningful content
    for tag in page(
        ["script", "style", "noscript", "nav", "iframe", "aside", "footer"]
    ):
        tag.decompose()

    # ignore hidden content
    hidden_selector = """
        [hidden],
        [aria-hidden="true"],
        [role="navigation"],
        [role="note"],
        [style*="display:none"],
        [style*="display: none"],
        [style*="visibility:hidden"],
        [style*="visibility: hidden"],
        [class~="hide"],
        [class*="hidden"]
    """
    for tag in page.select(hidden_selector):
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
    # set the title from the full page
    page = BeautifulSoup(html, "lxml")
    page_title = page.title.get_text(strip=True) if page.title else ""
    title = page_title or _title_from_url(url)

    # extract the page text
    page_text = _html_to_text(html)
    page_length = len(page_text)

    # extract the summary text
    try:
        document = Document(html)
        content_html = document.summary(html_partial=True)
        summary_text = _html_to_text(content_html)
        summary_length = len(summary_text)
        summary_coverage = summary_length / max(1, page_length)

        # if the summary covers a reasonable percentage of the page, we can use it
        if (
            summary_text.strip()
            and summary_length >= MINIMUM_SUMMARY_LENGTH
            and summary_coverage >= MINIMUM_SUMMARY_COVERAGE
        ):
            return ExtractedResult(title=title, text=summary_text)

    except Exception:
        # fall back safely if extraction fails
        logger.debug("readability extraction failed", exc_info=True)

    # return the full page text if the summary failed or did not cover enough of the page
    return ExtractedResult(title=title, text=page_text)
