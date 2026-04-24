# validation/demo_url_validator.py

import requests
from urllib.parse import urlparse
from validation.browser_validator import fetch_rendered_html

DEMO_HOSTING = [
    "vercel.app", "netlify.app", "onrender.com",
    "streamlit.app", "huggingface.co", "railway.app",
    "firebaseapp.com", "web.app", "github.io", "pages.dev"
]

VIDEO_DEMO = [
    "youtube.com", "youtu.be"
]

CODE_HOSTING = [
    "github.com", "gitlab.com"
]

# URLs that should never be counted as demos
IGNORE_DOMAINS = [
    "linkedin.com",
    "leetcode.com",
    "codeforces.com",
    "codechef.com",
    "hackerrank.com",
    "drive.google.com",
    "docs.google.com",
    "holopin.io",
    "twitter.com",
    "x.com",
    "instagram.com",
    "medium.com",
    "dev.to",
    "stackoverflow.com",
]


def classify_url(url):
    domain = urlparse(url).netloc.lower()

    if any(d in domain for d in IGNORE_DOMAINS):
        return "ignored"

    if any(d in domain for d in CODE_HOSTING):
        return "code"

    if any(d in domain for d in VIDEO_DEMO):
        return "video_demo"

    if any(d in domain for d in DEMO_HOSTING):
        return "hosted_demo"

    return "unknown"


def check_url_status(url, pulse_results=None):
    # Reuse pulse check result if available to avoid duplicate fetch
    if pulse_results:
        for p in pulse_results:
            if p.get("url") == url:
                status = p.get("status")
                # pulse only gives status, not html — still need html for interactivity
                if status is not None and status >= 400:
                    return status, ""
                if status is None:
                    return None, ""
                break

    try:
        response = requests.get(url, timeout=5)
        return response.status_code, response.text[:2000]
    except Exception:
        return None, ""


def detect_interactivity(html):
    html = html.lower()

    keywords = [
        "predict", "submit", "upload", "try", "run",
        "inference", "classify"
    ]

    if any(word in html for word in keywords):
        return True

    if "<input" in html or "<textarea" in html or "<button" in html:
        return True

    return False


def evaluate_demo_url(url, pulse_results=None):
    result = {
        "url": url,
        "type": None,
        "status": None,
        "is_interactive": False,
        "score": 0,
        "remarks": ""
    }

    url_type = classify_url(url)
    result["type"] = url_type

    if url_type in ["code", "video_demo", "ignored"]:
        if url_type == "code":
            result["remarks"] = "Code repository, not a demo"
        elif url_type == "ignored":
            result["score"] = 0
            result["remarks"] = "Social/competitive profile, not a demo"
        else:
            result["score"] = 2
            result["remarks"] = "Video demo available"

        return result

    status, html = check_url_status(url, pulse_results)
    # fallback to Playwright only if html is weak and status was OK
    if status and status < 400 and html and len(html) < 1000:
        rendered_html = fetch_rendered_html(url)
        if rendered_html:
            html = rendered_html

    result["status"] = status

    if status is None:
        result["score"] = -2
        result["remarks"] = "URL not reachable"
        return result

    if status >= 400:
        result["score"] = -2
        result["remarks"] = "Broken link"
        return result

    if url_type == "video_demo":
        result["score"] = 2
        result["remarks"] = "Video demo available"
        return result

    interactive = detect_interactivity(html)

    if not interactive:
        rendered_html = fetch_rendered_html(url)
        if rendered_html:
            interactive = detect_interactivity(rendered_html)
            html = rendered_html

    result["is_interactive"] = interactive

    if interactive:
        result["score"] = 3
        result["remarks"] = "Interactive demo detected"
    else:
        result["score"] = 1
        result["remarks"] = "Weak/static demo"

    return result


def evaluate_all_urls(urls, pulse_results=None):
    from concurrent.futures import ThreadPoolExecutor, as_completed

    results = [None] * len(urls)

    with ThreadPoolExecutor(max_workers=12) as executor:
        future_to_idx = {
            executor.submit(evaluate_demo_url, url, pulse_results): i
            for i, url in enumerate(urls)
        }

        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                results[idx] = {
                    "url": urls[idx],
                    "type": "unknown",
                    "status": None,
                    "is_interactive": False,
                    "score": 0,
                    "remarks": f"Error: {e}"
                }

    return results