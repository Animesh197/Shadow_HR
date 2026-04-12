import requests
from datetime import datetime

GITHUB_API = "https://api.github.com"


# Step 1: Fetch Commit Data from GitHub API
def fetch_commits(owner, repo, max_commits=100):
    """
    Fetch commit history from GitHub

    Why max_commits?
    - We don't need entire history
    - Last ~100 commits are enough to detect patterns
    """

    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"

    params = {
        "per_page": max_commits
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching commits for {repo}: {e}")
        return []


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


def analyze_commit_pattern(dates):
    """
    Core logic to detect authenticity
    """

    if not dates:
        return {
            "commit_score": 0,
            "verdict": "No commits found"
        }

    total_commits = len(dates)

    # lifespan
    lifespan_days = (dates[-1] - dates[0]).days + 1

    # gaps between commits
    gaps = []
    for i in range(1, len(dates)):
        gap = (dates[i] - dates[i - 1]).days
        gaps.append(gap)

    avg_gap = sum(gaps) / len(gaps) if gaps else 0

    # Heuristics (VERY IMPORTANT)
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

    # Good case
    return {
        "commit_score": 80,
        "verdict": "Healthy iterative development"
    }

def analyze_repo_commits(owner, repo):
    commits = fetch_commits(owner, repo)
    dates = extract_commit_dates(commits)
    return analyze_commit_pattern(dates)