from difflib import SequenceMatcher

def text_similarity(a, b):
    a = (a or "").lower().strip()
    b = (b or "").lower().strip()
    return SequenceMatcher(None, a, b).ratio()


def project_repo_similarity(project, repo):
    # Normalize project
    if isinstance(project, str):
        project_name = project.lower().strip()
        project_desc = ""
    else:
        project_name = project.get("name", "").lower().strip()
        project_desc = project.get("description", "").lower().strip()

    repo_name = (repo.get("name", "") or "").lower().strip()
    repo_desc = (repo.get("description", "") or "").lower().strip()

    # STEP 1: Exact match (VERY IMPORTANT)
    if project_name == repo_name:
        return 1.0

    # STEP 2: Substring match (strong signal)
    if project_name in repo_name or repo_name in project_name:
        return 0.9

    # STEP 3: Fallback to similarity
    name_score = text_similarity(project_name, repo_name)
    desc_score = text_similarity(project_desc, repo_desc)

    return max(name_score, desc_score)