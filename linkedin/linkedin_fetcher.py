"""
LinkedIn Fetcher

Fetches LinkedIn profile HTML using Playwright.

Why Playwright:
- LinkedIn blocks plain requests heavily
- Requires JS rendering for profile sections
- Requires authenticated session (cookies)

Setup:
1. Set LINKEDIN_SESSION_FILE env var to path of Playwright storage_state.json
2. Generate storage_state.json by logging into LinkedIn once via Playwright

Flow:
    LinkedIn URL
        ↓
    Cache Check
        ↓
    Load Session (if available)
        ↓
    Playwright Open Page
        ↓
    Wait For Profile Section
        ↓
    Extract HTML
        ↓
    Cache + Return
"""

import time
import os
from dotenv import load_dotenv
from threading import Lock
from linkedin.linkedin_cache import get_cached_html, set_cached_html, is_cached

load_dotenv()

# Rate limiting — avoid triggering LinkedIn bot detection
_TIME_LOCK = Lock()
_LAST_CALL_TIME = 0
MIN_DELAY = 3  # seconds between LinkedIn fetches

# Retry config
MAX_RETRIES = 2
RETRY_DELAY = 5  # seconds between retries

# Timeout for page load (ms)
PAGE_TIMEOUT = 15000
WAIT_AFTER_LOAD = 4000  # ms — wait for JS sections to render


def _rate_limit():
    global _LAST_CALL_TIME
    with _TIME_LOCK:
        elapsed = time.time() - _LAST_CALL_TIME
        if elapsed < MIN_DELAY:
            time.sleep(MIN_DELAY - elapsed)
        _LAST_CALL_TIME = time.time()


def fetch_linkedin_html(linkedin_url):
    """
    Fetch rendered LinkedIn profile HTML.

    Returns:
        html (str) — rendered page content, or "" on failure
        status (str) — "success", "blocked", "timeout", "error", "no_url"
    """

    if not linkedin_url:
        return "", "no_url"

    # Cache hit
    if is_cached(linkedin_url):
        cached = get_cached_html(linkedin_url)
        return cached, "success"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            _rate_limit()

            from playwright.sync_api import sync_playwright

            # Load session file path from env
            session_file = os.getenv("LINKEDIN_SESSION_FILE", "")

            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"]
                )

                # Load saved session (cookies) if available — required to bypass auth wall
                context_kwargs = {
                    "user_agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "viewport": {"width": 1280, "height": 800}
                }

                if session_file and os.path.exists(session_file):
                    context_kwargs["storage_state"] = session_file
                    print(f"[linkedin_fetcher] Using session file: {session_file}")
                else:
                    print("[linkedin_fetcher] No session file found — fetch may hit auth wall. "
                          "Set LINKEDIN_SESSION_FILE in .env to enable authenticated fetching.")

                context = browser.new_context(**context_kwargs)

                # Apply stealth to mask webdriver fingerprint (bypasses PerimeterX detection)
                try:
                    from playwright_stealth import Stealth
                    page = context.new_page()
                    Stealth().apply_stealth_sync(page)
                except ImportError:
                    print("[linkedin_fetcher] playwright-stealth not installed — bot detection risk. Run: pip install playwright-stealth")
                    page = context.new_page()

                response = page.goto(
                    linkedin_url,
                    timeout=PAGE_TIMEOUT,
                    wait_until="domcontentloaded"
                )

                # Wait for JS-rendered sections
                page.wait_for_timeout(WAIT_AFTER_LOAD)

                html = page.content()
                browser.close()

                # Detect LinkedIn auth wall / block
                if _is_blocked(html):
                    print(f"[linkedin_fetcher] Blocked by LinkedIn auth wall: {linkedin_url}")
                    return html, "blocked"

                set_cached_html(linkedin_url, html)
                print(f"[linkedin_fetcher] Successfully fetched: {linkedin_url}")
                return html, "success"

        except Exception as e:
            print(f"[linkedin_fetcher] Attempt {attempt}/{MAX_RETRIES} failed for {linkedin_url}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    return "", "error"


def _is_blocked(html):
    """
    Detect if LinkedIn returned an auth wall or CAPTCHA instead of a profile.
    """
    if not html:
        return True

    html_lower = html.lower()

    block_signals = [
        "join now",
        "sign in",
        "authwall",
        "checkpoint",
        "captcha",
        "we can't let you",
        "please verify"
    ]

    # If multiple block signals present, it's a wall
    hits = sum(1 for signal in block_signals if signal in html_lower)
    return hits >= 2
