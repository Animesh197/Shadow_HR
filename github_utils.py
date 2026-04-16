import requests
import os

def fetch_github_repos(username):

    url = f"https://api.github.com/users/{username}/repos"
    print(f"-------------------{url}")

    headers = {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f" GitHub API Status: {response.status_code}")
        print(" GitHub API Response:", response.text)
        return []

    data = response.json()

    # ✅ CRITICAL FIX: ensure it's a list
    if not isinstance(data, list):
        print(" Unexpected GitHub response:", data)
        return []

    repos = []

    for repo in data:
        # extra safety
        if not isinstance(repo, dict):
            continue

        repos.append({
            "name": repo.get("name"),
            "owner": repo.get("owner", {}).get("login"),
            "language": repo.get("language"),
            "topics": repo.get("topics"),
            "description": repo.get("description"),
            "stars": repo.get("stargazers_count", 0),
            "pushed_at": repo.get("pushed_at"),
            "homepage": repo.get("homepage")
        })

    print([repo['name'] for repo in repos])
    return repos