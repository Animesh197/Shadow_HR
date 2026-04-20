from .candidate_generator import generate_candidates
from .feature_extractor import extract_features
from .reranker import compute_final_match_score, classify_match


def match_project(project, repos, readme_cache):
    candidates = generate_candidates(project, repos)

    best = None
    best_score = 0
    best_features = None

    for repo in candidates:
        readme = readme_cache.get(repo["name"], "")

        features = extract_features(project, repo, readme)
        score = compute_final_match_score(features)

        if score > best_score:
            best = repo
            best_score = score
            best_features = features

    if not best:
        return None, 0, "no_match", {}

    label = classify_match(best_score)

    return best, best_score, label, best_features