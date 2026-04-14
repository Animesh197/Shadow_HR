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

    repos = []

    for repo in data:
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

    # optional (for debugging)
    print("\n Repo Homepages:")
    for repo in repos:
        if repo.get("homepage"):
            print(f"{repo['name']} → {repo['homepage']}")

    return repos