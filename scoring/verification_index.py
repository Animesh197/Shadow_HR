# ============================================================
# PHASE 6 — PORTFOLIO SCORE UPGRADE
# ============================================================

def compute_final_score_v2(repos, verification_data):
    """
    Portfolio-level credibility score.
    """

    if not repos:
        return 0, "Suspicious (Low)", ["No valid repositories found"]

    repos = sorted(repos, key=lambda x: x.get("score", 0), reverse=True)

    total_projects = verification_data.get("total_projects", 1)
    matched = verification_data.get("matched_projects", 0)
    missing = verification_data.get("missing_projects", 0)

    match_ratio = matched / max(total_projects, 1)

    # ============================================================
    # 1. REPO STRENGTH
    # ============================================================

    weights = [0.5, 0.3, 0.2]

    weighted_repo_score = sum(
        repos[i].get("score", 0) * weights[i]
        for i in range(min(3, len(repos)))
    ) / 100

    # ============================================================
    # 2. CONSISTENCY
    # ============================================================

    consistency_scores = []

    for r in repos[:5]:

        c = 0

        if r.get("live_demo"):
            c += 1

        if r.get("commit_score", 0) >= 60:
            c += 1

        if r.get("alignment_score", 0) >= 60:
            c += 1

        if r.get("complexity_score", 0) >= 60:
            c += 1

        consistency_scores.append(c / 4)

    consistency = (
        sum(consistency_scores) / len(consistency_scores)
        if consistency_scores else 0
    )
    # ============================================================
    # 3. DEMO STRENGTH
    # ============================================================

    demo_strength = sum(
        1 for r in repos if r.get("demo_score", 0) >= 5
    ) / len(repos)

    # ============================================================
    # 4. DIVERSITY
    # ============================================================

    strong_repos = sum(
        1 for r in repos
        if r.get("score", 0) >= 70
    )

    diversity = min(strong_repos / 3, 1)

    # ============================================================
    # 5. COMPLEXITY INDEX
    # ============================================================

    complexity_index = sum(
        r.get("complexity_score", 0)
        for r in repos
    ) / (len(repos) * 100)

    # ============================================================
    # 6. FINAL SCORE
    # ============================================================

    final_score = (
        weighted_repo_score * 100 * 0.35 +
        match_ratio * 100 * 0.20 +
        consistency * 100 * 0.15 +
        demo_strength * 100 * 0.10 +
        diversity * 100 * 0.10 +
        complexity_index * 100 * 0.10
    )
# ============================================================
    # PENALTIES
    # ============================================================

    penalty = 0
    reasons = []

    missing_ratio = missing / max(total_projects, 1)

    if missing_ratio > 0.7:
        penalty += 18
        reasons.append("Most claimed projects not found")

    elif missing_ratio > 0.4:
        penalty += 10
        reasons.append("Many claimed projects missing")

    elif missing > 0:
        penalty += 4 * missing
        reasons.append(f"{missing} project(s) not found")

    # ============================================================
    # SIGNAL PENALTIES
    # ============================================================

    for r in repos:

        name = r.get("name", "repo")

        if r.get("commit_score", 0) <= 20:
            penalty += 2
            reasons.append(f"Weak commit history in {name}")

        if "dumped code" in r.get("commit_verdict", "").lower():
            penalty += 5
            reasons.append(f"Possible dumped code in {name}")

        if r.get("alignment_score", 0) < 40:
            penalty += 2
            reasons.append(f"Low README-code alignment in {name}")

        if r.get("complexity_score", 0) < 30:
            penalty += 1
            reasons.append(f"Low technical depth in {name}")

    if demo_strength == 0:
        penalty += 5
        reasons.append("No live demos found")

    penalty = min(penalty, 30)

    # ============================================================
    # FINALIZE
    # ============================================================

    final_score -= penalty
    final_score = max(0, min(100, final_score))

    # ============================================================
    # LABELS
    # ============================================================

    if final_score >= 80:
        label = "Verified (High)"

    elif final_score >= 55:
        label = "Moderate (Medium)"

    else:
        label = "Suspicious (Low)"

    # ============================================================
    # POSITIVE SIGNALS
    # ============================================================

    if match_ratio >= 0.7:
        reasons.append("Most projects successfully verified")

    if demo_strength > 0:
        reasons.append("Live demos detected")

    if complexity_index >= 0.6:
        reasons.append("Technically sophisticated portfolio")

    if consistency >= 0.7:
        reasons.append("Consistent engineering quality")

    reasons = list(set(reasons))

    return round(final_score, 2), label, reasons