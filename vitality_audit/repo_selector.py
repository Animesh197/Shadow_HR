"""
Advanced Repo Selection Engine

Now includes:
- Project ↔ Repo matching
- Live demo detection (via pulse check)
- Ratio-based penalty
- Mandatory inclusion of matched repos
- Skill-based fallback
"""

def normalize(text):
    return text.lower().replace(" ", "").replace("-", "").replace("_", "")


# NEW: Check if project has live demo
def check_live_demo(project, pulse_results):
    proj_norm = normalize(project)

    for result in pulse_results:
        if not result.get("alive"):
            continue

        url = result.get("url", "").lower()

        if proj_norm in url:
            return True

    return False


def match_projects_with_repos(repos, projects, pulse_results):
    matched_repos = []
    project_status = []

    for proj in projects:
        proj_norm = normalize(proj)
        found = False

        for repo in repos:
            repo_name_norm = normalize(repo["name"])

            if proj_norm in repo_name_norm:
                live_demo = check_live_demo(proj, pulse_results)

                matched_repos.append(repo)

                project_status.append({
                    "project": proj,
                    "status": "found",
                    "repo": repo["name"],
                    "live_demo": live_demo
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

    for skill in skills:
        if skill.lower() in repo_lang:
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


def select_top_repos(repos, parsed_data, pulse_results, k=3):

    projects = parsed_data.get("projects", [])
    skills = parsed_data.get("skills", [])

    # STEP 1: Match projects + live demo
    matched_repos, project_status = match_projects_with_repos(
        repos, projects, pulse_results
    )

    print("\n Project Matching Status:")
    for p in project_status:
        print(p)

    # STEP 2: Ratio-based penalty
    total_projects = len(projects)
    matched_count = len(matched_repos)

    match_ratio = matched_count / total_projects if total_projects else 0
    penalty_flag = match_ratio < 0.5 if total_projects else False

    if penalty_flag:
        print("\n⚠️ Low project verification ratio → penalty applied")

    if matched_count == 0:
        print("\n⚠️ Claimed projects not found on GitHub")

    # STEP 3: Boost repos with live demo
    for repo in matched_repos:
        repo["live_demo"] = False

    for p in project_status:
        if p["status"] == "found" and p.get("live_demo"):
            for repo in matched_repos:
                if repo["name"] == p["repo"]:
                    repo["live_demo"] = True

    # Sort → live demo first
    matched_repos.sort(key=lambda x: x.get("live_demo", False), reverse=True)

    # STEP 4: Build final list
    final_repos = matched_repos.copy()

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

    print("\n Final Selected Repositories:")
    print([r["name"] for r in final_repos])

    # STEP 5: Audit signals
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