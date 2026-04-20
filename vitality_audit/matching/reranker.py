def compute_final_match_score(features):
    score = 0

    # ---------------- STRONG SIGNALS ----------------
    score += features["name_exact"] * 40
    score += features["name_overlap"] * 25

    # ---------------- SEMANTIC ----------------
    score += features["semantic_max"] * 25

    # ---------------- SUPPORTING ----------------
    score += features["desc_overlap"] * 5
    score += features["readme_overlap"] * 5

    return score


def classify_match(score):
    if score >= 60:
        return "high_confidence"
    elif score >= 35:
        return "medium_confidence"
    else:
        return "low_confidence"