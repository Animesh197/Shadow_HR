import requests
import os
from utils.deployment_utils import collect_deployment_signals

GITHUB_API = "https://api.github.com"

# Simple in-process cache for infra results
_INFRA_CACHE = {}


# ---------------- HEADERS (IMPORTANT) ----------------
def get_headers():
    token = os.getenv("GITHUB_TOKEN")

    if token:
        return {"Authorization": f"token {token}"}

    return {}

# ---------------- SAFE REQUEST ----------------
def safe_get(url):
    try:
        response = requests.get(url, headers=get_headers())

        if response.status_code != 200:
            if response.status_code == 404:
                print(f"Empty or uninitialized repo: {owner}/{repo_name}")
            else:
                print(f"Infra API failed: {url} → {response.status_code}")
            return None

        return response.json()

    except Exception as e:
        print(f"Infra request error: {e}")
        return None


# ---------------- ROOT + SHALLOW SCAN ----------------
def get_repo_contents(url):
    data = safe_get(url)

    if not data or not isinstance(data, list):
        return []

    return data


# ---------------- DEEP TREE SCAN (CRITICAL FIX) ----------------
def check_dependencies_in_tree(owner, repo_name):
    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/git/trees/HEAD?recursive=1"

    data = safe_get(url)

    if not data:
        return False

    files = data.get("tree", [])

    for f in files:
        path = f.get("path", "").lower()

        if "package.json" in path or "requirements.txt" in path:
            return True

    return False


# ---------------- MAIN FUNCTION ----------------
def check_repo_infra(owner, repo_name, repo=None, readme_text=""):
    cache_key = f"{owner}/{repo_name}"
    if cache_key in _INFRA_CACHE:
        return _INFRA_CACHE[cache_key]

    base_url = f"{GITHUB_API}/repos/{owner}/{repo_name}/contents"

    root_items = get_repo_contents(base_url)

    if not root_items:
        return {
            "has_docker": False,
            "has_ci": False,
            "has_dependencies": False,
            "has_deployment_config": False,
            "deployment_confidence": 0,
            "deployment_signals": [],
            "infra_score": 0
        }

    root_files = [item["name"].lower() for item in root_items]

    # ---------------- ROOT CHECK ----------------
    has_dependencies = any(
        f in root_files for f in ["package.json", "requirements.txt", "pyproject.toml"]
    )

    has_docker = any(
        f in root_files for f in ["dockerfile", "docker-compose.yml", "docker-compose.yaml"]
    )

    has_ci = any(".github" in f for f in root_files)

    has_deployment_config = any(
        f in root_files for f in ["firebase.json", "railway.toml", "vercel.json", "netlify.toml", "procfile", ".env.example"]
    )

    # ---------------- SHALLOW FOLDER SCAN ----------------
    if not has_dependencies:
        for item in root_items:
            if item.get("type") == "dir":
                sub_items = get_repo_contents(item.get("url"))

                sub_files = [i["name"].lower() for i in sub_items]

                if any(f in sub_files for f in ["package.json", "requirements.txt"]):
                    has_dependencies = True
                    break

    # ---------------- DEEP TREE SCAN (FINAL FALLBACK) ----------------
    if not has_dependencies:
        has_dependencies = check_dependencies_in_tree(owner, repo_name)

    # ---------------- DEPLOYMENT CONFIDENCE ----------------
    repo_meta = repo or {}
    deployment_data = collect_deployment_signals(
        repo_meta, readme_text, root_items, get_repo_contents
    )
    deployment_confidence = deployment_data["deployment_confidence"]
    deployment_signals = deployment_data["signals"]

    # Update has_deployment_config if confidence signals found it
    if not has_deployment_config and deployment_confidence >= 2:
        has_deployment_config = True

    # ---------------- INFRA SCORE ----------------
    infra_score = 0
    if has_docker:
        infra_score += 15
    if has_ci:
        infra_score += 15
    if has_dependencies:
        infra_score += 10
    infra_score += min(deployment_confidence, 10)  # replaces flat +10 for deployment

    result = {
        "has_docker": has_docker,
        "has_ci": has_ci,
        "has_dependencies": has_dependencies,
        "has_deployment_config": has_deployment_config,
        "deployment_confidence": deployment_confidence,
        "deployment_signals": deployment_signals,
        "infra_score": infra_score
    }

    _INFRA_CACHE[cache_key] = result
    return result