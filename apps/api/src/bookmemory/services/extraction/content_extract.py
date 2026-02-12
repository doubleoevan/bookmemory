from __future__ import annotations

from bookmemory.db.models.bookmark import LoadMethod, ExtractedContent
from bookmemory.services.extraction.http_fetch import fetch_html
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


async def extract_content(*, url: str) -> ExtractedContent:
    """
    Returns extracted HTML content from a URL.
    Use playwright if the site is JS-heavy or blocked and content was too small.
    """
    # try to fetch the extracted content with HTTP
    try:
        fetched_html = await fetch_html(url=url)
        extracted_content = extract_html(html=fetched_html.html, url=url)
        text = _trim_extracted_text(extracted_content.text)
        title = _trim_extracted_text(extracted_content.title)

        if len((text or "").strip()) >= MINIMUM_HTTP_LENGTH:
            return ExtractedContent(
                title=title,
                content=text,
                load_method=LoadMethod.http,
            )

    except Exception:
        # swallow any HTTP/extraction error and fall back to Playwright
        pass

    # try playwright if the HTTP extraction failed or the content was too short
    rendered_html = await fetch_rendered_html(url=url)
    extracted_content = extract_html(html=rendered_html.html, url=rendered_html.url)
    text = _trim_extracted_text(extracted_content.text)
    title = _trim_extracted_text(extracted_content.title)
    return ExtractedContent(
        title=title,
        content=text,
        load_method=LoadMethod.playwright,
    )
