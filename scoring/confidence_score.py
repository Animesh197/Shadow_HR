def compute_confidence_score(repos, verification_data):
    """
    Confidence Score (0–100)
    Measures how reliable the evaluation is
    """

    if not repos:
        return 0, "Low", ["No repositories available"]

    total_projects = verification_data.get("total_projects", 1)
    matched = verification_data.get("matched_projects", 0)
    missing = verification_data.get("missing_projects", 0)

    match_ratio = matched / max(total_projects, 1)

    # ---------------- COMPONENTS ----------------

    # 1. Repo coverage (more repos → more confidence)
    repo_count = len(repos)
    repo_score = min(repo_count / 5, 1)   # cap at 5 repos

    # 2. Match ratio
    match_score = match_ratio

    # 3. Demo presence
    demo_score = sum(1 for r in repos if r.get("live_demo")) / len(repos)

    # 4. Commit reliability
    commit_score = sum(
        1 for r in repos if r.get("commit_score", 0) >= 40
    ) / len(repos)

    # 5. Alignment reliability
    alignment_score = sum(
        1 for r in repos if r.get("alignment_score", 0) >= 40
    ) / len(repos)

    # ---------------- FINAL CONFIDENCE ----------------
    confidence = (
        repo_score * 0.25 +
        match_score * 0.25 +
        demo_score * 0.2 +
        commit_score * 0.15 +
        alignment_score * 0.15
    ) * 100

    confidence = round(confidence, 2)

    # ---------------- LABEL ----------------
    if confidence >= 75:
        label = "High"
    elif confidence >= 50:
        label = "Medium"
    else:
        label = "Low"

    # ---------------- REASONS ----------------
    reasons = []

    if repo_count < 3:
        reasons.append("Few repositories analyzed")

    if match_ratio < 0.5:
        reasons.append("Low project-repo match ratio")

    if demo_score == 0:
        reasons.append("No live demos found")

    if commit_score < 0.5:
        reasons.append("Weak commit activity")

    if alignment_score < 0.5:
        reasons.append("Low code-README alignment")

    return confidence, label, reasons