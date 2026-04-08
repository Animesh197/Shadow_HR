from difflib import SequenceMatcher

def text_similarity(a, b):
    a = a or ""
    b = b or ""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def project_repo_similarity(project, repo):
    # Step 1: Normalize project
    if isinstance(project, str):
        project_name = project
        project_desc = ""
    else:
        project_name = project.get("name", "")
        project_desc = project.get("description", "")

    # Step 2: Normalize repo
    repo_name = repo.get("name", "") or ""
    repo_desc = repo.get("description", "") or ""

    # Step 3: Compute similarity
    name_score = text_similarity(project_name, repo_name)
    desc_score = text_similarity(project_desc, repo_desc)

    return max(name_score, desc_score)