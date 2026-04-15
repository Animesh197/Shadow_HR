
from playwright.sync_api import sync_playwright
import time

# CACHE (URL → HTML)
PLAYWRIGHT_CACHE = {}

# RATE LIMIT CONFIG
LAST_CALL_TIME = 0
MIN_DELAY = 2  # seconds between calls


def fetch_rendered_html(url):
    """
    Fetch rendered HTML using Playwright with:
    - caching
    - rate limiting
    """

    global LAST_CALL_TIME

    # ✅ 1. CACHE CHECK
    if url in PLAYWRIGHT_CACHE:
        return PLAYWRIGHT_CACHE[url]

    # ✅ 2. RATE LIMIT
    current_time = time.time()
    elapsed = current_time - LAST_CALL_TIME

    if elapsed < MIN_DELAY:
        time.sleep(MIN_DELAY - elapsed)

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, timeout=10000)

            # wait for JS rendering
            page.wait_for_timeout(3000)

            html = page.content()

            browser.close()

            # ✅ SAVE TO CACHE
            PLAYWRIGHT_CACHE[url] = html

            # update last call time
            LAST_CALL_TIME = time.time()

            return html

    except Exception as e:
        print(f"Playwright error for {url}: {e}")
        return ""

# Opens real Chromium browser
# Executes JS
# Returns fully rendered HTML