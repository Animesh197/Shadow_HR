# ============================================================
# PHASE 7 — CONFIDENCE SCORE UPGRADE
# ============================================================

import statistics


def compute_confidence_score(repos, verification_score, verification_data):
    """
    Confidence = trustworthiness of evaluation.
    """

    if not repos:
        return 0, "Low", []

    total_projects = verification_data.get("total_projects", 1)
    matched_projects = verification_data.get("matched_projects", 0)

    # ============================================================
    # 1. PORTFOLIO SCORE CONFIDENCE
    # ============================================================

    portfolio_component = verification_score / 100

    # ============================================================
    # 2. REPO SCORE CONSISTENCY
    # ============================================================

    repo_scores = [r.get("score", 0) for r in repos]

    if len(repo_scores) >= 2:
        std_dev = statistics.pstdev(repo_scores)

        # lower variance = higher confidence
        consistency_component = max(0, 1 - (std_dev / 40))

    else:
        consistency_component = 0.5

    # ============================================================
    # 3. MATCH QUALITY
    # ============================================================

    match_component = matched_projects / max(total_projects, 1)
# ============================================================
    # 4. SIGNAL AGREEMENT
    # ============================================================

    agreement_scores = []

    for repo in repos[:5]:

        agreement = 0

        if repo.get("commit_score", 0) >= 60:
            agreement += 1

        if repo.get("alignment_score", 0) >= 60:
            agreement += 1

        if repo.get("complexity_score", 0) >= 60:
            agreement += 1

        if repo.get("demo_score", 0) >= 5:
            agreement += 1

        agreement_scores.append(agreement / 4)

    signal_agreement = (
        sum(agreement_scores) / len(agreement_scores)
        if agreement_scores else 0
    )

    # ============================================================
    # 5. REPO COUNT CONFIDENCE
    # ============================================================

    repo_count = len(repos)

    if repo_count >= 8:
        repo_count_component = 1.0
    elif repo_count >= 5:
        repo_count_component = 0.8
    elif repo_count >= 3:
        repo_count_component = 0.6
    else:
        repo_count_component = 0.4

    # ============================================================
    # FINAL CONFIDENCE
    # ============================================================

    confidence = (
        portfolio_component * 0.25 +
        consistency_component * 0.20 +
        match_component * 0.20 +
        signal_agreement * 0.20 +
        repo_count_component * 0.15
    )

    confidence = confidence * 100

    # ============================================================
    # CLAMP
    # ============================================================

    confidence = max(0, min(100, confidence))

    label = "High" if confidence >= 75 else "Medium" if confidence >= 50 else "Low"
    return round(confidence, 2), label, []