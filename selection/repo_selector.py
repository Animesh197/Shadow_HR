from .similarity import project_repo_similarity
from .scoring import skill_match_score, repo_quality_score


def compute_repo_score(repo, claims):
    project_scores = []

    for p in claims.get("projects", []):
        project_scores.append(project_repo_similarity(p, repo))

    project_score = max(project_scores) if project_scores else 0

    skill_score = skill_match_score(claims.get("skills", []), repo)

    quality_score = repo_quality_score(repo)

    final_score = (
        0.4 * project_score +
        0.4 * skill_score +
        0.2 * quality_score
    )

    return {
        "repo": repo["name"],
        "score": final_score,
        "breakdown": {
            "project": project_score,
            "skill": skill_score,
            "quality": quality_score
        }
    }


def select_top_repos(repos, claims, k=3):
    scored = []

    for repo in repos:
        scored.append(compute_repo_score(repo, claims))

    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)

    return ranked[:k]