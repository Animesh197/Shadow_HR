from .text_utils import token_overlap_score, normalized_contains

def generate_candidates(project, repos, top_k=5):
    scored = []

    for repo in repos:
        name = repo.get("name", "")
        desc = repo.get("description", "")

        score = (
            token_overlap_score(project, name) * 2 +
            token_overlap_score(project, desc)
        )

        # Ensure prefixed/renamed repos are never missed
        if score == 0 and normalized_contains(project, name):
            score = 1.5  # strong enough to become a candidate

        if score > 0:
            scored.append((repo, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    return [r[0] for r in scored[:top_k]]