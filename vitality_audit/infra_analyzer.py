import requests


def get_repo_contents(url):
    response = requests.get(url)
    if response.status_code != 200:
        return []
    return response.json()


def check_repo_infra(owner, repo_name):
    base_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"

    # STEP 1: Root scan
    root_items = get_repo_contents(base_url)
    root_files = [item["name"].lower() for item in root_items]

    has_dependencies = any(
        f in root_files for f in ["package.json", "requirements.txt"]
    )

    has_docker = any(
        f in root_files for f in ["dockerfile", "docker-compose.yml"]
    )

    has_ci = any(".github" in f for f in root_files)

    # STEP 2: If not found → shallow folder scan
    if not has_dependencies:
        for item in root_items:
            if item["type"] == "dir":
                sub_url = item["url"]
                sub_items = get_repo_contents(sub_url)

                sub_files = [i["name"].lower() for i in sub_items]

                if any(f in sub_files for f in ["package.json", "requirements.txt"]):
                    has_dependencies = True
                    break

    return {
        "has_docker": has_docker,
        "has_ci": has_ci,
        "has_dependencies": has_dependencies
    }