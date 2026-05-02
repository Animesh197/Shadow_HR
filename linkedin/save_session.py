"""
LinkedIn Session Saver

Run this ONCE to log into LinkedIn manually and save the session cookies.
The saved session file is then used by linkedin_fetcher.py for all future fetches.

Usage:
    python linkedin/save_session.py

This opens a visible browser window. Log in to LinkedIn manually, then press Enter.
The session is saved to linkedin_session.json (gitignored).
"""

import os
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

SESSION_FILE = os.getenv("LINKEDIN_SESSION_FILE", "linkedin_session.json")


def save_linkedin_session():
    print("Opening LinkedIn in browser...")
    print("Log in manually, then come back here and press Enter.")

    with sync_playwright() as p:
        # Use headless=False so you can log in manually
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        # Apply stealth so the session is saved from a stealth context
        Stealth().apply_stealth_sync(page)
        page.goto("https://www.linkedin.com/login")

        input("\nPress Enter AFTER you have fully logged in and can see your LinkedIn feed...")

        context.storage_state(path=SESSION_FILE)
        browser.close()

    print(f"\nSession saved to: {SESSION_FILE}")
    print("Make sure LINKEDIN_SESSION_FILE={} is set in your .env".format(SESSION_FILE))


if __name__ == "__main__":
    save_linkedin_session()
