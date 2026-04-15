def compute_verification_index(repos, audit_signals):
    """
    Final credibility score (0–100)
    """

    if not repos:
        return {
            "verification_score": 0,
            "label": "Unverified",
            "confidence": "Low",
            "reasons": ["No valid repositories found"]
        }

    # ---------------- 1. TOP REPO SCORE ----------------
    top_scores = [r.get("score", 0) for r in repos[:3]]
    avg_repo_score = sum(top_scores) / len(top_scores)

    repo_component = avg_repo_score * 0.5  # weight 50%

    # ---------------- 2. MATCH RATIO ----------------
    match_ratio = audit_signals.get("match_ratio", 0)

    match_component = match_ratio * 100 * 0.3  # weight 30%

    # ---------------- 3. CONSISTENCY BONUS ----------------
    bonus = 0

    for repo in repos:
        if repo.get("live_demo"):
            bonus += 2
        if repo.get("commit_score", 0) >= 60:
            bonus += 2
        if repo.get("alignment_score", 0) >= 50:
            bonus += 2

    bonus = min(bonus, 20)  # cap
    bonus_component = bonus * 0.2

    # ---------------- 4. PENALTIES ----------------
    penalty = 0

    if audit_signals.get("penalty_flag"):
        penalty += 10

    missing = len(audit_signals.get("missing_projects", []))
    penalty += missing * 5

    # weak repos
    for repo in repos:
        if repo.get("commit_score", 0) <= 20:
            penalty += 3

    # ---------------- FINAL SCORE ----------------
    final_score = repo_component + match_component + bonus_component - penalty

    final_score = max(0, min(100, round(final_score)))

    # ---------------- LABEL ----------------
    if final_score >= 75:
        label = "Verified"
        confidence = "High"
    elif final_score >= 50:
        label = "Moderate"
        confidence = "Medium"
    else:
        label = "Suspicious"
        confidence = "Low"

    # ---------------- REASONS ----------------
    reasons = []

    if match_ratio < 0.5:
        reasons.append("Low project verification ratio")

    if missing > 0:
        reasons.append(f"{missing} claimed projects not found")

    for repo in repos:
        if repo.get("commit_score", 0) <= 20:
            reasons.append(f"Weak commit history in {repo.get('name')}")

        if not repo.get("live_demo"):
            reasons.append(f"No demo for {repo.get('name')}")

    return {
        "verification_score": final_score,
        "label": label,
        "confidence": confidence,
        "reasons": list(set(reasons))  # remove duplicates
    }