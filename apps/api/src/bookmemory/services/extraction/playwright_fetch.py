from __future__ import annotations


from dataclasses import dataclass

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

import anyio

from bookmemory.core.settings import settings

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

TITLE_TIMEOUT_SECONDS = 2.0
DEFAULT_PLAYWRIGHT_TIMEOUT_SECONDS = 25.0
DEFAULT_MAXIMUM_HTML_LENGTH = 2_000_000
DEFAULT_MAXIMUM_TEXT_LENGTH = 250_000

# playwright is resource-heavy. keep concurrent browser instances very low.
_PLAYWRIGHT_FETCH_SEMAPHORE = anyio.Semaphore(settings.playwright_fetch_max_concurrency)


@dataclass(frozen=True)
class PlaywrightFetchResult:
    url: str
    html: str
    visible_text: str


class PlaywrightFetchError(Exception):
    pass


async def fetch_rendered_html(
    *,
    url: str,
    timeout_seconds: float = DEFAULT_PLAYWRIGHT_TIMEOUT_SECONDS,
    max_html_chars: int = DEFAULT_MAXIMUM_HTML_LENGTH,
    max_text_chars: int = DEFAULT_MAXIMUM_TEXT_LENGTH,
) -> PlaywrightFetchResult:
    """Returns dynamically rendered HTML from a URL"""
    async with _PLAYWRIGHT_FETCH_SEMAPHORE:
        browser = None
        browser_session = None
        try:
            async with async_playwright() as playwright:
                # launch the playwright browser and navigate to the url
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                    ],
                )
                browser_session = await browser.new_context(
                    user_agent=USER_AGENT,
                    locale="en-US",
                    extra_http_headers={
                        "Accept-Language": "en-US,en;q=0.9",
                    },
                )
                page = await browser_session.new_page()
                timeout_ms = int(timeout_seconds * 1000)
                await page.goto(url, wait_until="networkidle", timeout=timeout_ms)

                # wait for the page to render a title before extracting the HTML
                try:
                    await page.wait_for_function(
                        "() => document.title && document.title.trim().length > 0",
                        timeout=TITLE_TIMEOUT_SECONDS * 1000,
                    )
                except PlaywrightTimeoutError:
                    pass
                html = (await page.content()) or ""

                # extract visible text from the rendered DOM
                visible_text = await page.evaluate(
                    "() => (document.body && document.body.innerText) ? document.body.innerText : ''"
                )

                # validate and normalize the rendered HTML
                html = html.strip()
                if html == "":
                    raise PlaywrightFetchError("rendered HTML is empty")
                if len(html) > max_html_chars:
                    html = html[:max_html_chars]

                # normalize the visible text
                visible_text = (visible_text or "").strip()
                if len(visible_text) > max_text_chars:
                    visible_text = visible_text[:max_text_chars]

                return PlaywrightFetchResult(
                    url=page.url,
                    html=html,
                    visible_text=visible_text,
                )

        except PlaywrightTimeoutError as error:
            raise PlaywrightFetchError(
                f"playwright timeout after {timeout_seconds}s"
            ) from error
        except PlaywrightFetchError:
            raise
        except Exception as error:
            raise PlaywrightFetchError(f"playwright failed: {error}") from error
        finally:
            # end the session and close the browser
            try:
                if browser_session is not None:
                    try:
                        await browser_session.close()
                    except Exception:
                        pass
            finally:
                if browser is not None:
                    try:
                        await browser.close()
                    except Exception:
                        pass
