# Step 1: Fetch README

import requests
import base64
import os


def fetch_readme(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"

    headers = {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}"
    }

    try:
        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            return ""

        data = res.json()
        content = base64.b64decode(data["content"]).decode("utf-8")

        return content

    except:
        return ""



# Step 2: Extract Tech from README
def extract_tech_from_readme(readme_text):
    TECH_KEYWORDS = [
        "react", "node", "express",
        "mongodb", "mysql", "postgresql",
        "tensorflow", "pytorch",
        "docker", "kubernetes",
        "nextjs", "flask", "django"
    ]

    readme_lower = readme_text.lower()

    found = []

    for tech in TECH_KEYWORDS:
        if tech in readme_lower:
            found.append(tech)

    return found


# STEP 3: ADD FILE FETCH FUNCTION
def fetch_file_content(owner, repo, path):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"      # Fetches any file from repo, Decodes base64, Returns actual content

    headers = {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}"
    }

    try:
        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            return ""

        data = res.json()
        content = base64.b64decode(data["content"]).decode("utf-8")

        return content

    except:
        return ""


# STEP 4: PARSE package.json
import json

def extract_from_package_json(content):
    tech = []

    try:
        data = json.loads(content)

        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})

        all_deps = list(deps.keys()) + list(dev_deps.keys())

        for dep in all_deps:
            dep_lower = dep.lower()

            if "react" in dep_lower:
                tech.append("react")
            if "next" in dep_lower:
                tech.append("nextjs")
            if "express" in dep_lower:
                tech.append("express")
            if "mongodb" in dep_lower:
                tech.append("mongodb")

    except:
        pass

    return tech


# STEP 5: PARSE requirements.txt
def extract_from_requirements(content):
    tech = []

    lines = content.splitlines()

    for line in lines:
        line = line.lower()

        if "django" in line:
            tech.append("django")
        if "flask" in line:
            tech.append("flask")
        if "torch" in line:
            tech.append("pytorch")
        if "tensorflow" in line:
            tech.append("tensorflow")

    return tech


# Step 6: Extract Tech from Code
def extract_tech_from_repo(owner, repo_name, repo):
    tech = []

    # 1. Language
    if repo.get("language"):
        tech.append(repo["language"].lower())

    # 2. Infra
    infra = repo.get("infra", {})

    if infra.get("has_docker"):
        tech.append("docker")

    # 3. package.json
    pkg_content = fetch_file_content(owner, repo_name, "package.json")
    if pkg_content:
        tech.extend(extract_from_package_json(pkg_content))

    # 4. requirements.txt
    req_content = fetch_file_content(owner, repo_name, "requirements.txt")
    if req_content:
        tech.extend(extract_from_requirements(req_content))

    return list(set(tech))  # remove duplicates


# Step 4: Compare

def compare_readme_code(readme_tech, repo_tech):

    if not readme_tech:
        return {
            "alignment_score": 50,
            "verdict": "No README claims"
        }

    matches = 0

    for tech in readme_tech:
        if tech in repo_tech:
            matches += 1

    ratio = matches / len(readme_tech)

    if ratio > 0.7:
        return {
            "alignment_score": 80,
            "verdict": "Strong alignment"
        }

    elif ratio > 0.3:
        return {
            "alignment_score": 50,
            "verdict": "Partial alignment"
        }

    else:
        return {
            "alignment_score": 20,
            "verdict": "Mismatch — possible exaggeration"
        }

# def compare_readme_code(readme_tech, repo_tech):

#     # Case 1: No README signals → neutral (not penalized)
#     if not readme_tech:
#         return {
#             "alignment_score": 60,   # neutral baseline
#             "verdict": "README lacks technical detail"
#         }

#     matches = sum(1 for tech in readme_tech if tech in repo_tech)
#     ratio = matches / len(readme_tech)

#     # Case 2: Strong alignment
#     if ratio >= 0.7:
#         return {
#             "alignment_score": 85,
#             "verdict": "Strong README-code alignment"
#         }

#     # Case 3: Moderate alignment
#     elif ratio >= 0.4:
#         return {
#             "alignment_score": 70,
#             "verdict": "Partial alignment"
#         }

#     # Case 4: Weak alignment (NOT exaggeration)
#     else:
#         return {
#             "alignment_score": 50,
#             "verdict": "Weak alignment (limited consistency)"
#         }

# Step 5: Wrapper Function
def analyze_readme_alignment(owner, repo, repo_data):

    readme = fetch_readme(owner, repo)

    if not readme:
        return {
            "alignment_score": 0,
            "verdict": "No README found"
        }
    # if not readme:
    #     return {
    #         "alignment_score": 55,
    #         "verdict": "No README found"
    #     }

    readme_tech = extract_tech_from_readme(readme)
    repo_tech = extract_tech_from_repo(owner, repo, repo_data)
    return compare_readme_code(readme_tech, repo_tech)