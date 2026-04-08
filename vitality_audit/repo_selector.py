"""
Advanced Repo Selection Engine

Features:
1. Project ↔ Repo matching with tracking
2. Ratio-based penalty system
3. Mandatory inclusion of matched repos
4. Skill-based fallback to fill remaining slots
5. Stores audit signals for future scoring
"""

def normalize(text):
    return text.lower().replace(" ", "").replace("-", "").replace("_", "")


def match_projects_with_repos(repos, projects):
    matched_repos = []
    project_status = []

    normalized_projects = [normalize(p) for p in projects]

    for i, proj in enumerate(projects):
        proj_norm = normalized_projects[i]
        found = False

        for repo in repos:
            repo_name_norm = normalize(repo["name"])

            if proj_norm in repo_name_norm:
                matched_repos.append(repo)
                project_status.append({
                    "project": proj,
                    "status": "found",
                    "repo": repo["name"]
                })
                found = True
                break

        if not found:
            project_status.append({
                "project": proj,
                "status": "not_found"
            })

    return matched_repos, project_status


def score_repo_by_skills(repo, skills):
    score = 0

    repo_lang = (repo.get("language") or "").lower()
    skills_lower = [s.lower() for s in skills]

    for skill in skills_lower:
        if skill in repo_lang:
            score += 2

    return score


def get_skill_based_repos(repos, skills, exclude_names, k):
    scored = []

    for repo in repos:
        if repo["name"] in exclude_names:
            continue

        score = score_repo_by_skills(repo, skills)

        repo_copy = repo.copy()
        repo_copy["score"] = score
        scored.append(repo_copy)

    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[:k]


def select_top_repos(repos, parsed_data, k=3):

    projects = parsed_data.get("projects", [])
    skills = parsed_data.get("skills", [])

    # STEP 1: Match projects
    matched_repos, project_status = match_projects_with_repos(repos, projects)

    print("\n Project Matching Status:")
    for p in project_status:
        print(p)

    total_projects = len(projects)
    matched_count = len(matched_repos)

    # STEP 2: Ratio-based penalty
    penalty_flag = False
    match_ratio = 0

    if total_projects > 0:
        match_ratio = matched_count / total_projects

        if match_ratio < 0.5:
            penalty_flag = True
            print("\n⚠️ Low project verification ratio → penalty applied")

    # STEP 3: Start building final repo list
    final_repos = []

    # Add matched repos first (MANDATORY)
    for repo in matched_repos:
        final_repos.append(repo)

    # STEP 4: Fill remaining slots using skill-based selection
    remaining_slots = k - len(final_repos)

    if remaining_slots > 0:
        exclude_names = [r["name"] for r in final_repos]

        skill_repos = get_skill_based_repos(
            repos,
            skills,
            exclude_names,
            remaining_slots
        )

        final_repos.extend(skill_repos)

    # STEP 5: If no matched repos at all
    if matched_count == 0:
        print("\n⚠️ Claimed projects not found on GitHub")

    print("\n Final Selected Repositories:")
    print([r["name"] for r in final_repos])

    # STEP 6: Store audit signals (VERY IMPORTANT for later)
    audit_signals = {
        "total_projects": total_projects,
        "matched_projects": matched_count,
        "match_ratio": match_ratio,
        "penalty_flag": penalty_flag,
        "missing_projects": [
            p["project"] for p in project_status if p["status"] == "not_found"
        ]
    }

    print("\n Audit Signals:")
    print(audit_signals)

    return final_repos