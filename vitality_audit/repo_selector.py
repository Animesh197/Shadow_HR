"""
Advanced Repo Selection Engine

Includes:
- Project ↔ Repo matching
- Live demo detection
- Ratio-based penalty
- Infra analysis (docker, ci, dependencies)
- Score-based ranking (stars + recency + infra + live demo)
"""

from vitality_audit.infra_analyzer import check_repo_infra
from datetime import datetime, timezone


# ---------------- NORMALIZATION ----------------
def normalize(text):
    return text.lower().replace(" ", "").replace("-", "").replace("_", "")


# ---------------- RECENCY ----------------
def get_recency_weight(pushed_at):
    if not pushed_at:
        return 0

    try:
        pushed_date = datetime.strptime(pushed_at, "%Y-%m-%dT%H:%M:%SZ")
        pushed_date = pushed_date.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        days_diff = (now - pushed_date).days

        if days_diff < 30:
            return 5
        elif days_diff < 90:
            return 3
        elif days_diff < 180:
            return 2
        else:
            return 0
    except:
        return 0


# ---------------- INFRA SCORE ----------------
def compute_infra_score(repo):
    infra = repo.get("infra", {})

    score = 0

    if infra.get("has_docker"):
        score += 3
    if infra.get("has_ci"):
        score += 2
    if infra.get("has_dependencies"):
        score += 2

    return score


# ---------------- FINAL SCORE ----------------
def compute_repo_score(repo):
    stars = repo.get("stars", 0)
    recency = get_recency_weight(repo.get("pushed_at"))
    live_demo = repo.get("live_demo", False)

    infra_score = compute_infra_score(repo)

    score = (stars * 2) + recency + infra_score

    if live_demo:
        score += 5

    return score


# ---------------- LIVE DEMO ----------------
def check_live_demo(project, pulse_results):
    proj_norm = normalize(project)

    for result in pulse_results:
        if not result.get("alive"):
            continue

        url = result.get("url", "").lower()

        if proj_norm in url:
            return True

    return False


# ---------------- PROJECT MATCHING ----------------
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


# ---------------- SKILL SCORING ----------------
def score_repo_by_skills(repo, skills):
    score = 0
    repo_lang = (repo.get("language") or "").lower()

    for skill in skills:
        if skill.lower() in repo_lang:
            score += 2

    return score


# ---------------- SKILL FALLBACK ----------------
def get_skill_based_repos(repos, skills, exclude_names, k):
    scored = []

    for repo in repos:
        if repo["name"] in exclude_names:
            continue

        repo_copy = repo.copy()

        skill_score = score_repo_by_skills(repo_copy, skills)
        repo_copy["live_demo"] = False  # fallback repos

        final_score = skill_score + compute_repo_score(repo_copy)
        repo_copy["score"] = final_score

        scored.append(repo_copy)

    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[:k]


# ---------------- MAIN SELECTOR ----------------
def select_top_repos(repos, parsed_data, pulse_results, k=3):

    projects = parsed_data.get("projects", [])
    skills = parsed_data.get("skills", [])

    # ✅ STEP 0: Attach infra signals ONCE
    for repo in repos:
        owner = repo.get("owner")
        name = repo.get("name")

        if owner and name:
            repo["infra"] = check_repo_infra(owner, name)
        else:
            repo["infra"] = {}

    # STEP 1: Project matching
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

    # STEP 3: Assign live_demo flags
    for repo in matched_repos:
        repo["live_demo"] = False

    for p in project_status:
        if p["status"] == "found" and p.get("live_demo"):
            for repo in matched_repos:
                if repo["name"] == p["repo"]:
                    repo["live_demo"] = True

    # STEP 4: Score matched repos
    for repo in matched_repos:
        repo["score"] = compute_repo_score(repo)

    matched_repos.sort(key=lambda x: x["score"], reverse=True)

    # STEP 5: Build final list
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

    # STEP 6: Audit signals
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