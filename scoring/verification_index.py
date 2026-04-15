def compute_final_score_v2(repos, verification_data):
    """
    Scoring V2 + Explanation Layer
    """

    if not repos:
        return 0, "Suspicious (Low)", ["No valid repositories found"]

    repos = sorted(repos, key=lambda x: x.get("score", 0), reverse=True)

    total_projects = verification_data.get("total_projects", 1)
    matched = verification_data.get("matched_projects", 0)
    missing = verification_data.get("missing_projects", 0)

    match_ratio = matched / max(total_projects, 1)

    # ---------------- BASE COMPONENTS ----------------
    weights = [0.5, 0.3, 0.2]
    weighted_score = sum(
        repos[i].get("score", 0) * weights[i]
        for i in range(min(3, len(repos)))
    ) / 100

    consistency_scores = []
    for r in repos[:5]:
        c = 0
        if r.get("live_demo"):
            c += 1
        if r.get("commit_score", 0) >= 50:
            c += 1
        if r.get("alignment_score", 0) >= 40:
            c += 1
        consistency_scores.append(c / 3)

    consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0
    demo_strength = sum(1 for r in repos if r.get("live_demo")) / len(repos)
    strong_repos = sum(1 for r in repos if r.get("score", 0) >= 60)
    diversity = min(strong_repos / 3, 1)

    final_score = (
        weighted_score * 100 * 0.4 +
        match_ratio * 100 * 0.25 +
        consistency * 100 * 0.15 +
        demo_strength * 100 * 0.1 +
        diversity * 100 * 0.1
    )

    # ---------------- PENALTIES ----------------
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

    if demo_strength == 0:
        penalty += 5
        reasons.append("No live demos found")

    penalty = min(penalty, 30)

    # ---------------- FINAL ----------------
    final_score -= penalty
    final_score = max(0, min(100, final_score))

    # ---------------- LABEL ----------------
    if final_score >= 75:
        label = "Verified (High)"
    elif final_score >= 50:
        label = "Moderate (Medium)"
    else:
        label = "Suspicious (Low)"

    # ---------------- POSITIVE SIGNALS ----------------
    if match_ratio >= 0.7:
        reasons.append("Most projects successfully verified")

    if demo_strength > 0:
        reasons.append("Live demos detected")

    if consistency > 0.6:
        reasons.append("Consistent quality across repositories")

    # remove duplicates
    reasons = list(set(reasons))

    return round(final_score, 2), label, reasons