from __future__ import annotations

from bookmemory.db.models.bookmark import LoadMethod
from bookmemory.services.extraction.http_fetch import FetchError, fetch_html
from bookmemory.services.extraction.html_extract import extract_html
from bookmemory.services.extraction.playwright_fetch import (
    fetch_rendered_html,
)

# fallback to playwright if the extracted text falls below this threshold
MINIMUM_HTTP_LENGTH = 600

# cap the length of extracted text to persist in the database
MAXIMUM_CONTENT_LENGTH = 250_000


def _trim_extracted_text(text: str) -> str:
    trimmed = (text or "").strip()
    if len(trimmed) > MAXIMUM_CONTENT_LENGTH:
        return trimmed[:MAXIMUM_CONTENT_LENGTH]
    return trimmed


def _should_fallback_to_playwright(*, extracted_text: str) -> bool:
    return len((extracted_text or "").strip()) < MINIMUM_HTTP_LENGTH


async def extract_content(*, url: str) -> tuple[str, LoadMethod]:
    """
    Returns extracted HTML content from a URL.
    Use playwright if the site is JS-heavy or blocked and content was too small.
    """
    # try to fetch the content with HTTP first
    try:
        fetched_html = await fetch_html(url=url)
        extracted_content = extract_html(html=fetched_html.html, url=url)
        text = _trim_extracted_text(extracted_content.text)

        if _should_fallback_to_playwright(extracted_text=text):
            raise FetchError("extracted text too small; likely JS-heavy")

        return text, LoadMethod.http

    except FetchError as http_error:
        # retry the fetch with playwright if an error suggests that the site is JS-heavy or blocked
        can_try_playwright_status = http_error.status_code in {401, 403, 429}
        can_try_playwright_message = (
            "content-type" in str(http_error).lower()
            or "js-heavy" in str(http_error).lower()
            or "too small" in str(http_error).lower()
        )

        if not (can_try_playwright_status or can_try_playwright_message):
            raise

        # fetch and return the content with playwright
        rendered_html = await fetch_rendered_html(url=url)
        extracted_content = extract_html(html=rendered_html.html, url=rendered_html.url)
        text = _trim_extracted_text(extracted_content.text)
        return text, LoadMethod.playwright
