"""
Advanced Repo Selection Engine
"""

from vitality_audit.infra_analyzer import check_repo_infra
from vitality_audit.commit_analyzer import analyze_repo_commits
from vitality_audit.readme_analyzer import analyze_readme_alignment
from validation.browser_validator import fetch_rendered_html
# from scoring.verification_index import compute_verification_index
from scoring.verification_index import compute_final_score_v2
from scoring.confidence_score import compute_confidence_score
from vitality_audit.semantic_matcher import compute_semantic_similarity
from datetime import datetime, timezone
from urllib.parse import urlparse
import requests


# ---------------- NORMALIZATION ----------------
def normalize(text):
    return text.lower().replace(" ", "").replace("-", "").replace("_", "")


# ---------------- DOMAIN UTILS ----------------
def extract_domain(url):
    try:
        return urlparse(url).netloc.replace("www.", "")
    except:
        return ""


# ---------------- DEMO VALIDATION ----------------
def is_demo_url_valid(url, demo_results):
    if not url:
        return False

    url_domain = extract_domain(url)

    for d in demo_results:
        if d.get("score", 0) <= 0:
            continue

        d_domain = extract_domain(d.get("url", ""))

        if url_domain and url_domain == d_domain:
            return True

    return False


def check_valid_demo_for_project(project, demo_results):
    proj_norm = normalize(project)

    for d in demo_results:
        if d.get("score", 0) <= 0:
            continue

        url_norm = normalize(d.get("url", ""))

        if proj_norm in url_norm:
            return True

    return False


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
    infra = compute_infra_score(repo)
    commit = repo.get("commit_score", 0)
    alignment = repo.get("alignment_score", 0)
    live_demo = repo.get("live_demo", False)
    demo_quality = repo.get("demo_score", 0)

    stars_score = min(stars * 2, 10)
    recency_score = min(recency, 10)
    infra_score = min(infra, 10)
    commit_score = commit * 0.5
    alignment_score = alignment * 0.4

    demo_score = 10 if live_demo else 0
    demo_quality_score = demo_quality * 2

    score = (
        stars_score +
        recency_score +
        infra_score +
        commit_score +
        alignment_score +
        demo_score +
        demo_quality_score
    )

    return round(score, 2)



def compute_project_repo_match_score(project, repo, readme_text):
    """
    Hybrid scoring: keyword + semantic
    """

    proj_norm = normalize(project)

    name = repo.get("name", "")
    repo_name_norm = normalize(name)

    desc = repo.get("description") or ""
    readme = readme_text or ""

    score = 0

    # ✅ HARD PRIORITY (CRITICAL FIX)
    if proj_norm in repo_name_norm or repo_name_norm in proj_norm:
        score += 20   # strong boost

    # ---------------- KEYWORD MATCH ----------------
    if proj_norm in normalize(name):
        score += 10

    if proj_norm in normalize(desc):
        score += 5

    if proj_norm in normalize(readme):
        score += 8

    # ---------------- SEMANTIC MATCH ----------------
    semantic_inputs = [
        name,
        desc,
        readme[:1000]  # limit size
    ]

    best_semantic = 0

    for text in semantic_inputs:
        sim = compute_semantic_similarity(project, text)
        best_semantic = max(best_semantic, sim)

    # scale semantic score
    score += best_semantic * 10  # converts 0–1 → 0–10

    return score


def fetch_readme(owner, repo):
    """
    Fetch README content (lightweight)
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"

    headers = {
        "Accept": "application/vnd.github.v3.raw"
    }

    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.text[:3000]  # limit size
    except:
        pass

    return ""


# ---------------- PROJECT MATCHING ----------------
def match_projects_with_repos(repos, projects, pulse_results, demo_results):
    matched_repos = []
    project_status = []

    # ---------------- README CACHE ----------------
    readme_cache = {}

    for proj in projects:
        best_repo = None
        best_score = 0

        for repo in repos:
            owner = repo.get("owner")
            name = repo.get("name")

            # -------- FETCH README (CACHED) --------
            if name not in readme_cache:
                if owner and name:
                    readme_cache[name] = fetch_readme(owner, name)
                else:
                    readme_cache[name] = ""

            readme_text = readme_cache[name]

            # -------- COMPUTE MATCH SCORE --------
            score = compute_project_repo_match_score(proj, repo, readme_text)

            if score > best_score:
                best_score = score
                best_repo = repo

        # ---------------- THRESHOLD ----------------
        # if best_repo and best_score >= 8:

        #     homepage_demo = is_demo_url_valid(best_repo.get("homepage"), demo_results)
        #     proj_demo = check_valid_demo_for_project(proj, demo_results)

        #     live_demo = homepage_demo or proj_demo

        #     best_repo["live_demo"] = live_demo

        #     matched_repos.append(best_repo)

        #     project_status.append({
        #         "project": proj,
        #         "status": "found",
        #         "repo": best_repo["name"],
        #         "match_score": best_score,
        #         "live_demo": live_demo
        #     })

        # else:
        #     project_status.append({
        #         "project": proj,
        #         "status": "not_found",
        #         "match_score": best_score
        #     })

        proj_norm = normalize(proj)

        repo_name_norm = normalize(best_repo.get("name", "")) if best_repo else ""

        # Strong name match check
        name_match = (
            proj_norm in repo_name_norm or
            repo_name_norm in proj_norm
        )

        # Final decision
        if best_repo and (name_match or best_score >= 6):

            homepage_demo = is_demo_url_valid(best_repo.get("homepage"), demo_results)
            proj_demo = check_valid_demo_for_project(proj, demo_results)

            live_demo = homepage_demo or proj_demo

            best_repo["live_demo"] = live_demo

            matched_repos.append(best_repo)

            project_status.append({
                "project": proj,
                "status": "found",
                "repo": best_repo["name"],
                "match_score": best_score,
                "live_demo": live_demo,
                "match_type": "name_match" if name_match else "score_match"
            })

        else:
            project_status.append({
                "project": proj,
                "status": "not_found",
                "match_score": best_score
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
        final_score = skill_score + compute_repo_score(repo_copy)

        repo_copy["score"] = final_score
        scored.append(repo_copy)

    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[:k]



# ---------------- PREFILTER (NEW) ----------------
def prefilter_repos(repos, parsed_data, top_n=8):
    """
    Improved lightweight filtering before expensive analysis
    """

    projects = parsed_data.get("projects", [])
    skills = [s.lower() for s in parsed_data.get("skills", [])]

    scored = []

    for repo in repos:
        score = 0

        name = repo.get("name", "").lower()
        language = (repo.get("language") or "").lower()
        stars = repo.get("stars", 0)
        pushed_at = repo.get("pushed_at")

        # ---------------- PROJECT MATCH (HIGH WEIGHT) ----------------
        for proj in projects:
            if normalize(proj) in normalize(name):
                score += 10

        # ---------------- SKILL MATCH ----------------
        if language in skills:
            score += 5

        # ---------------- STARS ----------------
        score += min(stars, 5)

        # ---------------- RECENCY ----------------
        if pushed_at:
            try:
                from datetime import datetime
                days = (datetime.utcnow() - datetime.strptime(pushed_at, "%Y-%m-%dT%H:%M:%SZ")).days

                if days < 30:
                    score += 5
                elif days < 90:
                    score += 3
                elif days < 180:
                    score += 1
            except:
                pass

        scored.append((repo, score))

    # sort by score
    scored.sort(key=lambda x: x[1], reverse=True)

    selected = [r[0] for r in scored[:top_n]]

    print(f"\n Prefilter selected {len(selected)} repos out of {len(repos)}")

    return selected


# ---------------- MAIN SELECTOR ----------------
def select_top_repos(repos, parsed_data, pulse_results, demo_results, k=3):

    projects = parsed_data.get("projects", [])
    skills = parsed_data.get("skills", [])

    # ---------------- PREFILTER ----------------
    repos = prefilter_repos(repos, parsed_data, top_n=8)

    print("\n Prefiltered Repos:")
    print([r["name"] for r in repos])

    # ---------------- ENRICH ----------------
    for repo in repos:
        owner = repo.get("owner")
        name = repo.get("name")

        repo["infra"] = check_repo_infra(owner, name) if owner and name else {}

        commit_data = analyze_repo_commits(owner, name) if owner and name else {}
        repo["commit_score"] = commit_data.get("commit_score", 0)
        repo["commit_verdict"] = commit_data.get("verdict", "")

        alignment_data = analyze_readme_alignment(owner, name, repo) if owner and name else {}
        repo["alignment_score"] = alignment_data.get("alignment_score", 0)
        repo["alignment_verdict"] = alignment_data.get("verdict", "")

        repo["live_demo"] = is_demo_url_valid(repo.get("homepage"), demo_results)

        demo_score = 0
        homepage_domain = extract_domain(repo.get("homepage"))

        for result in demo_results:
            if extract_domain(result.get("url", "")) == homepage_domain:
                demo_score = result.get("score", 0)
                break

        repo["demo_score"] = demo_score

    # ---------------- PROJECT MATCHING ----------------
    matched_repos, project_status = match_projects_with_repos(
        repos, projects, pulse_results, demo_results
    )

    print("\n Project Matching Status:")
    for p in project_status:
        print(p)

    # ---------------- AUDIT SIGNALS ----------------
    total_projects = len(projects)
    matched_count = len(matched_repos)

    match_ratio = matched_count / total_projects if total_projects else 0

    missing_projects_list = [
        p["project"] for p in project_status if p["status"] == "not_found"
    ]

    audit_signals = {
        "total_projects": total_projects,
        "matched_projects": matched_count,
        "missing_projects": len(missing_projects_list),
        "missing_projects_list": missing_projects_list
    }
    print("\n Missing Projects:")
    print(missing_projects_list)

    print("\n Audit Signals:")
    print(audit_signals)

    # ---------------- SCORING ----------------
    for repo in matched_repos:
        repo["score"] = compute_repo_score(repo)

    matched_repos.sort(key=lambda x: x["score"], reverse=True)

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

    # ---------------- FINAL SCORE ----------------
    final_score, label, reasons = compute_final_score_v2(final_repos, audit_signals)
    confidence_score, confidence_label, confidence_reasons = compute_confidence_score(final_repos ,audit_signals)

    return {
        "repos": final_repos,
        "final_score": final_score,
        "label": label,
        "reasons": reasons,

        "confidence": {
            "score": confidence_score,
            "level": confidence_label,
            "reasons": confidence_reasons
        },

        "audit": {
            "total_projects": total_projects,
            "matched_projects": matched_count,
            "missing_projects": missing_projects_list
        }
    }