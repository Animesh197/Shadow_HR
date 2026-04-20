import requests
import os

def fetch_github_repos(username):
    repos = []
    page = 1

    headers = {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}"
    }

    while True:
        url = f"https://api.github.com/users/{username}/repos?page={page}&per_page=100"

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"GitHub API error: {response.status_code}")
            break

        data = response.json()

        if not data:
            break

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

        page += 1

    print(f"Total repos fetched: {len(repos)}")
    print([repo['name'] for repo in repos])

    return repos