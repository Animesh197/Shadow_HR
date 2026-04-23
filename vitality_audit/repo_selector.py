"""
Advanced Repo Selection Engine
"""

from vitality_audit.infra_analyzer import check_repo_infra
from vitality_audit.commit_analyzer import analyze_repo_commits
from vitality_audit.readme_analyzer import analyze_readme_alignment
from validation.browser_validator import fetch_rendered_html
from scoring.verification_index import compute_final_score_v2
from scoring.confidence_score import compute_confidence_score
from scoring.skill_validator import compute_skill_validation
from vitality_audit.semantic_matcher import compute_semantic_similarity
from vitality_audit.matching.matcher import match_project
from vitality_audit.complexity_analyzer import compute_complexity_score
from vitality_audit.demo_quality_analyzer import compute_demo_quality
from vitality_audit.stack_sophistication_analyzer import compute_stack_score
from concurrent.futures import ThreadPoolExecutor

from datetime import datetime, timezone
from urllib.parse import urlparse
import requests


def extract_repo_names_from_links(links):
    repo_names = set()

    for url in links:
        if "github.com" in url:
            parts = url.split("/")
            if len(parts) >= 5:
                repo_name = parts[4]
                if repo_name and repo_name != "":
                    repo_names.add(repo_name.lower())

    return repo_names


# ---------------- NORMALIZATION ----------------
from vitality_audit.matching.text_utils import normalize_text, normalized_contains
def normalize(text):
    """Strip-all-separators normalize for backwards compat."""
    return normalize_text(text).replace(" ", "")


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
    # Try full name, then core name (before any parenthetical)
    names_to_try = [project]
    if "(" in project:
        core = project.split("(")[0].strip()
        if core:
            names_to_try.append(core)

    for d in demo_results:
        if d.get("score", 0) <= 0:
            continue

        url_norm = normalize(d.get("url", ""))

        for name in names_to_try:
            proj_norm = normalize(name)
            if proj_norm and proj_norm in url_norm:
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

    # Use pre-computed infra_score if available
    if infra.get("infra_score") is not None:
        return infra.get("infra_score", 0)

    score = 0
    if infra.get("has_docker"):
        score += 15
    if infra.get("has_ci"):
        score += 15
    if infra.get("has_dependencies"):
        score += 10
    if infra.get("has_deployment_config"):
        score += 10

    return score



def compute_repo_score(repo):

    # ---------------- RAW SIGNALS ----------------
    stars = repo.get("stars", 0)
    recency_weight = get_recency_weight(repo.get("pushed_at"))

    infra_raw = compute_infra_score(repo)

    commit_score = repo.get("commit_score", 0)
    alignment_score = repo.get("alignment_score", 0)
    demo_score = repo.get("demo_score", 0)
    complexity_score = repo.get("complexity_score", 0)
    stack_score = repo.get("stack_score", 0)

    # ---------------- NORMALIZED COMPONENTS ----------------

    # commit quality → 15%
    commit_component = (commit_score / 100) * 15

    # README alignment → 15%
    alignment_component = (alignment_score / 100) * 15

    # complexity → 15%
    complexity_component = (complexity_score / 100) * 15

    # stack depth → 15%
    sophistication_component = (stack_score / 100) * 15

    # infra → 10% (max infra_score = 50)
    infra_component = (min(infra_raw, 50) / 50) * 10

    # demo quality → 10%
    demo_component = (demo_score / 10) * 10

    # recency → 5%
    recency_component = (recency_weight / 5) * 5

    # stars → 5%
    stars_component = min(stars / 20, 1) * 5

    # ---------------- FINAL SCORE ----------------
    score = (
        commit_component +
        alignment_component +
        complexity_component +
        sophistication_component +
        infra_component +
        demo_component +
        recency_component +
        stars_component
    )

    return round(min(score, 100), 2)



from vitality_audit.readme_analyzer import fetch_readme as _fetch_readme_raw

def fetch_readme(owner, repo):
    """Fetch README content (uses authenticated call from readme_analyzer)."""
    content = _fetch_readme_raw(owner, repo)
    return content[:3000] if content else ""


# ---------------- PROJECT MATCHING ----------------

def match_projects_with_repos(repos, projects, pulse_results, demo_results):
    matched_repos = []
    project_status = []

    # ---------------- README CACHE ----------------
    readme_cache = {}

    # Preload READMEs once (IMPORTANT for performance)
    for repo in repos:
        owner = repo.get("owner")
        name = repo.get("name")

        if name not in readme_cache:
            if owner and name:
                readme_cache[name] = fetch_readme(owner, name)
            else:
                readme_cache[name] = ""

    # ---------------- PROJECT MATCHING ----------------
    for proj in projects:

        best_repo, best_score, confidence_label, features = match_project(
            proj,
            repos,
            readme_cache
        )

        # ---------------- FALLBACK MATCH (RULE BASED) ----------------
        if not best_repo:
            for repo in repos:
                if normalized_contains(proj, repo.get("name", "")):
                    best_repo = repo
                    best_score = 0.5
                    confidence_label = "rule_based_override"
                    break

        # ---------------- DECISION ----------------
        if best_repo and confidence_label in ["high_confidence", "medium_confidence", "low_confidence", "rule_based_override"]:

            # ---------------- DEMO CHECK ----------------
            homepage_demo = is_demo_url_valid(best_repo.get("homepage"), demo_results)
            proj_demo = check_valid_demo_for_project(proj, demo_results)
            repo_demo = check_valid_demo_for_project(best_repo.get("name", ""), demo_results)

            live_demo = homepage_demo or proj_demo or repo_demo
            best_repo["live_demo"] = live_demo

            matched_repos.append(best_repo)

            project_status.append({
                "project": proj,
                "status": "found",
                "repo": best_repo.get("name"),
                "match_score": round(best_score, 2),
                "confidence": confidence_label,
                "live_demo": live_demo,

                # 🔍 DEBUG SIGNALS (VERY IMPORTANT)
                "signals": {
                    "name_overlap": round(features.get("name_overlap", 0), 3),
                    "name_exact": round(features.get("name_exact", 0), 3),
                    "semantic": round(features.get("semantic_max", 0), 3),
                    "desc_overlap": round(features.get("desc_overlap", 0), 3),
                    "readme_overlap": round(features.get("readme_overlap", 0), 3)
                }
            })

        else:
            project_status.append({
                "project": proj,
                "status": "not_found",
                "match_score": round(best_score, 2) if best_score else 0,
                "confidence": confidence_label if best_repo else "no_match"
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
def prefilter_repos(repos, parsed_data, links, top_n=8):
    """
    Improved lightweight filtering before expensive analysis
    """
    resume_repo_names = extract_repo_names_from_links(links)  # newly added
    projects = parsed_data.get("projects", [])
    skills = [s.lower() for s in parsed_data.get("skills", [])]

    scored = []

    for repo in repos:
        score = 0

        repo_name = (repo.get("name") or "").lower()
        language = (repo.get("language") or "").lower()
        stars = repo.get("stargazers_count", 0)
        pushed_at = repo.get("pushed_at", "")

        # FORCE INCLUDE RESUME-LINKED REPOS
        if repo_name in resume_repo_names:
            score += 100  # ensures it never gets filtered out

        # ---------------- PROJECT MATCH (HIGH WEIGHT) ----------------
        for proj in projects:
            if normalized_contains(proj, repo_name):
                score += 10

        # ---------------- SKILL MATCH ----------------
        if language and language in skills:  # ✅ safe check
            score += 5

        # ---------------- STARS ----------------
        score += min(stars, 5)  # ✅ now valid

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
        print(f"[PREFILTER] {repo_name} → score: {score}")

    # sort by score
    scored.sort(key=lambda x: x[1], reverse=True)

    selected = [r[0] for r in scored[:top_n]]


    print(f"\n Prefilter selected {len(selected)} repos out of {len(repos)}")
        
    return selected


# PHASE 8 — PARALLEL REPO ENRICHMENT
# ============================================================

def enrich_repo(repo, owner, demo_results):

    name = repo.get("name")

    # --------------------------------------------------------
    # INFRA
    # --------------------------------------------------------

    infra_data = check_repo_infra(owner, name)

    repo["infra"] = infra_data

    # --------------------------------------------------------
    # COMMITS
    # --------------------------------------------------------

    commit_data = analyze_repo_commits(owner, name)

    repo.update(commit_data)

    # --------------------------------------------------------
    # README ALIGNMENT
    # --------------------------------------------------------

    alignment_data = analyze_readme_alignment(owner, name, repo)

    repo["alignment_score"] = alignment_data.get(
        "alignment_score", 0
    )

    repo["alignment_verdict"] = alignment_data.get(
        "verdict", ""
    )

    # Merge detected_tech from README verified_tech + dependency signals
    readme_tech = alignment_data.get("verified_tech", [])
    dep_signals = repo.get("dependency_signals", {})
    dep_tech = []
    for techs in dep_signals.values():
        dep_tech.extend(techs)

    repo["detected_tech"] = list(set(readme_tech + dep_tech))

    # --------------------------------------------------------
    # COMPLEXITY
    # --------------------------------------------------------

    complexity_data = compute_complexity_score(repo)

    repo.update(complexity_data)

    # --------------------------------------------------------
    # STACK
    # --------------------------------------------------------

    stack_data = compute_stack_score(repo)

    repo.update(stack_data)

    # --------------------------------------------------------
    # DEMO
    # --------------------------------------------------------

    repo["live_demo"] = is_demo_url_valid(
        repo.get("homepage"),
        demo_results
    )

    demo_data = compute_demo_quality(repo, demo_results)

    repo["demo_score"] = demo_data.get(
        "demo_quality_score", 0
    )

    repo["demo_verdict"] = demo_data.get(
        "demo_quality_verdict", ""
    )

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    repo["score"] = compute_repo_score(repo)

    return repo


# ---------------- MAIN SELECTOR ----------------
def select_top_repos(repos, parsed_data, pulse_results, demo_results, links, k=2):

    projects = parsed_data.get("projects", [])
    skills = parsed_data.get("skills", [])

    # ---------------- PREFILTER ----------------
    repos = prefilter_repos(repos, parsed_data, links, top_n=8)

    print("\n Prefiltered Repos:")
    print([r["name"] for r in repos])


        # ---------------- ENRICH (PARALLEL) ----------------
    enriched_repos = []

    with ThreadPoolExecutor(max_workers=5) as executor:

        # futures = [
        #     executor.submit(enrich_repo, repo, demo_results)
        #     for repo in repos
        # ]
        futures = [
            executor.submit(
                enrich_repo,
                repo,
                repo.get("owner"),
                demo_results
            )
            for repo in repos
        ]

        for future in futures:
            try:
                enriched_repos.append(future.result())
            except Exception as e:
                print(f"[PHASE8] Repo enrichment failed: {e}")

    repos = enriched_repos

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

        # debug scoring breakdown
        repo["score_breakdown"] = {
            "commit": repo.get("commit_score", 0),
            "alignment": repo.get("alignment_score", 0),
            "infra": compute_infra_score(repo),
            "demo": repo.get("demo_score", 0),
            "stars": repo.get("stars", 0),
            "recency": get_recency_weight(repo.get("pushed_at"))
        }

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
    confidence_score, confidence_label, confidence_reasons = compute_confidence_score(final_repos, final_score, audit_signals)

    # ---------------- SKILL VALIDATION ----------------
    skill_validation = compute_skill_validation(skills, final_repos)

    # ---------------- REPO TIERING ----------------
    for repo in final_repos:
        s = repo.get("score", 0)
        if s >= 75:
            repo["tier"] = "Tier 1 — Flagship"
        elif s >= 50:
            repo["tier"] = "Tier 2 — Supporting"
        elif s >= 25:
            repo["tier"] = "Tier 3 — Practice"
        else:
            repo["tier"] = "Tier 4 — Weak/Noisy"

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
        },

        "skill_validation": skill_validation
    }