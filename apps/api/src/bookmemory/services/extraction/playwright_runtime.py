from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import anyio
from playwright.async_api import Browser, Playwright, async_playwright


@dataclass(frozen=True)
class PlaywrightRuntime:
    playwright: Playwright
    browser: Browser


_runtime: Optional[PlaywrightRuntime] = None
_runtime_lock = anyio.Lock()


async def start_playwright_runtime() -> PlaywrightRuntime:
    # use a lock to prevent concurrent initialization of the Playwright runtime.
    global _runtime
    async with _runtime_lock:
        if _runtime is not None:
            return _runtime

        playwright = await async_playwright().start()
        try:
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-background-networking",
                    "--disable-default-apps",
                    "--disable-extensions",
                    "--disable-sync",
                    "--no-first-run",
                ],
            )
        except Exception:
            # stop playwright if the browser launch fails
            await playwright.stop()
            raise

        _runtime = PlaywrightRuntime(playwright=playwright, browser=browser)
        return _runtime


async def stop_playwright_runtime() -> None:
    global _runtime

    # use a lock to prevent concurrent shutdown of the Playwright runtime.
    async with _runtime_lock:
        if _runtime is None:
            return

        # close the browser first, then stop playwright.
        try:
            try:
                await _runtime.browser.close()
            except Exception:
                pass
        finally:
            try:
                await _runtime.playwright.stop()
            except Exception:
                pass
            _runtime = None


def get_playwright_runtime() -> PlaywrightRuntime:
    """Returns the process-level Playwright runtime singleton."""
    if _runtime is None:
        raise RuntimeError("PlaywrightRuntime is not started")
    return _runtime
