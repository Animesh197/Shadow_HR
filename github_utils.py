import requests

def fetch_github_repos(username):

    url = f"https://api.github.com/users/{username}/repos"
    print(f"-------------------{url}")

    response = requests.get(url)

    if response.status_code != 200:
        print(" Failed to fetch GitHub data")
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
            "pushed_at": repo.get("pushed_at")
        })
    print([repo['name'] for repo in repos])
    return repos


# fetches the githup repo and then send it for the selection