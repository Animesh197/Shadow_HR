import requests
import os
from datetime import datetime

GITHUB_API = "https://api.github.com"

# Simple in-process cache for commit results
_COMMIT_CACHE = {}


# Step 1: Fetch Commit Data from GitHub API
def fetch_commits(owner, repo, max_commits=100):
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"

    params = {
        "per_page": max_commits
    }

    headers = {}

    # Add GitHub token if available
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        response = requests.get(url, params=params, headers=headers)

        # Handle specific errors
        if response.status_code == 403:
            return "RATE_LIMIT"

        if response.status_code == 409:
            return "EMPTY_REPO"

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching commits for {repo}: {e}")
        return "ERROR"


# Step 2: Extract Commit Dates
def extract_commit_dates(commits):
    """
    Extract commit timestamps
    """

    dates = []

    for commit in commits:
        try:
            date_str = commit["commit"]["author"]["date"]
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            dates.append(date_obj)
        except:
            continue

    return sorted(dates)


# def analyze_commit_pattern(dates):
#     """
#     Core logic to detect authenticity
#     """

#     if not dates:
#         return {
#             "commit_score": 0,
#             "verdict": "No commits found"
#         }

#     total_commits = len(dates)

#     # lifespan
#     lifespan_days = (dates[-1] - dates[0]).days + 1

#     # gaps between commits
#     gaps = []
#     for i in range(1, len(dates)):
#         gap = (dates[i] - dates[i - 1]).days
#         gaps.append(gap)

#     avg_gap = sum(gaps) / len(gaps) if gaps else 0

#     # Heuristics (VERY IMPORTANT)
#     if total_commits <= 2:
#         return {
#             "commit_score": 10,
#             "verdict": "Single/Minimal commit — suspicious"
#         }

#     if lifespan_days <= 1:
#         return {
#             "commit_score": 20,
#             "verdict": "All commits in one day — likely dumped code"
#         }

#     if avg_gap > 30:
#         return {
#             "commit_score": 40,
#             "verdict": "Very sparse commits — weak activity"
#         }

#     # Good case
#     return {
#         "commit_score": 80,
#         "verdict": "Healthy iterative development"
#     }

def analyze_commit_pattern(dates):
    """
    Improved commit scoring.

    Same heuristics.
    Better score granularity.
    """

    if not dates:
        return {
            "commit_score": 0,
            "verdict": "No commits found"
        }

    total_commits = len(dates)

    # lifespan
    lifespan_days = (dates[-1] - dates[0]).days + 1

    # gap analysis
    gaps = []

    for i in range(1, len(dates)):
        gap = (dates[i] - dates[i - 1]).days
        gaps.append(gap)

    avg_gap = sum(gaps) / len(gaps) if gaps else 0

    # ============================================================
    # STAGE 1 — SAME EXISTING HEURISTICS
    # ============================================================

    if total_commits <= 2:
        return {
            "commit_score": 10,
            "verdict": "Single/Minimal commit — suspicious"
        }

    if lifespan_days <= 1:
        return {
            "commit_score": 20,
            "verdict": "All commits in one day — likely dumped code"
        }

    if avg_gap > 30:
        return {
            "commit_score": 40,
            "verdict": "Very sparse commits — weak activity"
        }
    # ============================================================
    # STAGE 2 — ADD RESOLUTION
    # ============================================================

    # commit density
    commits_per_day = total_commits / max(lifespan_days, 1)

    score = 50

    # total commits contribution
    if total_commits >= 100:
        score += 20
    elif total_commits >= 50:
        score += 15
    elif total_commits >= 20:
        score += 10
    elif total_commits >= 10:
        score += 5

    # lifespan contribution
    if lifespan_days >= 365:
        score += 10
    elif lifespan_days >= 180:
        score += 7
    elif lifespan_days >= 90:
        score += 5

    # average gap contribution
    if avg_gap <= 3:
        score += 10
    elif avg_gap <= 7:
        score += 7
    elif avg_gap <= 14:
        score += 4

    # commit density balance
    if 0.05 <= commits_per_day <= 2:
        score += 5

    # cap score
    score = min(score, 95)

    # verdict tiers
    if score >= 90:
        verdict = "Exceptional iterative development"
    elif score >= 75:
        verdict = "Healthy iterative development"
    elif score >= 60:
        verdict = "Moderate development consistency"
    else:
        verdict = "Basic activity pattern"

    return {
        "commit_score": round(score),
        "verdict": verdict
    }



def analyze_repo_commits(owner, repo):
    cache_key = f"{owner}/{repo}"
    if cache_key in _COMMIT_CACHE:
        return _COMMIT_CACHE[cache_key]

    commits = fetch_commits(owner, repo)

    if commits == "RATE_LIMIT":
        result = {"commit_score": 0, "verdict": "Rate limit exceeded — commit data unavailable"}
    elif commits == "EMPTY_REPO":
        result = {"commit_score": 5, "verdict": "Empty repository — no commits"}
    elif commits == "ERROR":
        result = {"commit_score": 0, "verdict": "Error fetching commit data"}
    else:
        dates = extract_commit_dates(commits)
        result = analyze_commit_pattern(dates)

    _COMMIT_CACHE[cache_key] = result
    return result