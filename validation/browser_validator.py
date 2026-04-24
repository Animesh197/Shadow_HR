try:
    from playwright.sync_api import sync_playwright
except:
    sync_playwright = None
import time
from threading import Lock

# CACHE (URL → HTML)
PLAYWRIGHT_CACHE = {}
_CACHE_LOCK = Lock()
_TIME_LOCK = Lock()

# RATE LIMIT CONFIG
LAST_CALL_TIME = 0
MIN_DELAY = 2  # seconds between calls


def fetch_rendered_html(url):
    """
    Fetch rendered HTML using Playwright with:
    - thread-safe caching
    - rate limiting
    """

    global LAST_CALL_TIME

    # 1. CACHE CHECK (thread-safe)
    with _CACHE_LOCK:
        if url in PLAYWRIGHT_CACHE:
            return PLAYWRIGHT_CACHE[url]

    # 2. RATE LIMIT (thread-safe)
    with _TIME_LOCK:
        current_time = time.time()
        elapsed = current_time - LAST_CALL_TIME
        if elapsed < MIN_DELAY:
            time.sleep(MIN_DELAY - elapsed)
        LAST_CALL_TIME = time.time()

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_timeout(3000)
            html = page.content()
            browser.close()

            with _CACHE_LOCK:
                PLAYWRIGHT_CACHE[url] = html

            return html

    except Exception as e:
        print(f"Playwright error for {url}: {e}")
        return ""