"""
Deployment signal collection utilities.
Detects deployment evidence from root files, nested dirs, README, homepage, Docker.
"""

import re

DEPLOYMENT_FILES = {
    "firebase.json", "railway.toml", "vercel.json",
    "netlify.toml", "procfile", ".env.example",
    "fly.toml", "render.yaml", "app.yaml"
}

COMMON_APP_DIRS = [
    "frontend", "web", "client", "app", "apps",
    "ui", "backend", "server"
]

DEPLOYMENT_HOSTING_PATTERNS = [
    r"vercel\.app", r"netlify\.app", r"onrender\.com",
    r"railway\.app", r"fly\.dev", r"firebaseapp\.com",
    r"github\.io", r"web\.app", r"pages\.dev"
]


def _has_deployment_file(file_list):
    """Check if any deployment config file exists in a list of filenames."""
    return any(f in DEPLOYMENT_FILES for f in file_list)


def _readme_has_deployment_link(readme_text):
    """Check if README contains any known deployment hosting URL."""
    if not readme_text:
        return False
    text = readme_text.lower()
    return any(re.search(pattern, text) for pattern in DEPLOYMENT_HOSTING_PATTERNS)


def collect_deployment_signals(repo, readme_text, root_items, get_contents_fn):
    """
    Collect deployment signals from multiple sources.

    Args:
        repo: repo metadata dict (needs homepage, has_pages)
        readme_text: raw README content string
        root_items: list of root directory items from GitHub API
        get_contents_fn: callable(url) → list of items (reuses existing fetcher)

    Returns:
        {
            "deployment_confidence": int (0–10),
            "signals": [str, ...]
        }
    """
    confidence = 0
    signals = []

    root_files = [item["name"].lower() for item in root_items]

    # --------------------------------------------------------
    # Step 1 — Root deployment config
    # --------------------------------------------------------
    if _has_deployment_file(root_files):
        confidence += 3
        signals.append("Root deployment config found")

    # --------------------------------------------------------
    # Step 2 — Nested deployment config (depth=1, likely dirs only)
    # --------------------------------------------------------
    elif not _has_deployment_file(root_files):
        for item in root_items:
            if item.get("type") != "dir":
                continue
            dir_name = item["name"].lower()
            if dir_name not in COMMON_APP_DIRS:
                continue
            try:
                sub_items = get_contents_fn(item.get("url", ""))
                sub_files = [i["name"].lower() for i in sub_items]
                if _has_deployment_file(sub_files):
                    confidence += 2
                    signals.append(f"Nested deployment config in /{item['name']}")
                    break
            except Exception:
                continue

    # --------------------------------------------------------
    # Step 3 — GitHub homepage set
    # --------------------------------------------------------
    homepage = repo.get("homepage") or ""
    if homepage and any(re.search(p, homepage.lower()) for p in DEPLOYMENT_HOSTING_PATTERNS):
        confidence += 2
        signals.append("GitHub homepage points to live deployment")

    # --------------------------------------------------------
    # Step 4 — README deployment links
    # --------------------------------------------------------
    if _readme_has_deployment_link(readme_text):
        confidence += 2
        signals.append("README contains deployment link")

    # --------------------------------------------------------
    # Step 5 — Docker deployment signal
    # --------------------------------------------------------
    docker_files = {"dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yaml"}
    if any(f in root_files for f in docker_files):
        confidence += 1
        signals.append("Docker deployment setup detected")

    # --------------------------------------------------------
    # Step 6 — GitHub Pages
    # --------------------------------------------------------
    if repo.get("has_pages"):
        confidence += 1
        signals.append("GitHub Pages enabled")

    return {
        "deployment_confidence": min(confidence, 10),
        "signals": signals
    }
