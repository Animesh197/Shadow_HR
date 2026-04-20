from .text_utils import token_overlap_score, fuzzy_substring_score
from vitality_audit.semantic_matcher import compute_semantic_similarity


def extract_features(project, repo, readme):
    name = repo.get("name", "")
    desc = repo.get("description") or ""

    features = {}

    # ---------------- NAME SIGNAL ----------------
    features["name_overlap"] = token_overlap_score(project, name)
    features["name_exact"] = fuzzy_substring_score(project, name)

    # ---------------- DESCRIPTION ----------------
    features["desc_overlap"] = token_overlap_score(project, desc)

    # ---------------- README ----------------
    features["readme_overlap"] = token_overlap_score(project, readme[:2000])

    # ---------------- SEMANTIC ----------------
    features["semantic_name"] = compute_semantic_similarity(project, name)
    features["semantic_desc"] = compute_semantic_similarity(project, desc)
    features["semantic_readme"] = compute_semantic_similarity(project, readme[:1000])

    features["semantic_max"] = max(
        features["semantic_name"],
        features["semantic_desc"],
        features["semantic_readme"]
    )

    return features