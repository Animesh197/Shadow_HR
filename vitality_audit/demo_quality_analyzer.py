# ============================================================
# PHASE 4 — DEMO QUALITY ANALYZER
# ============================================================
# Goal:
# Evaluate realism and strength of demo proof.
#
# Output:
# demo_quality_score → 0–10
# demo_quality_verdict
# ============================================================


def compute_demo_quality(repo, demo_results):

    score = 0
    reasons = []

    homepage = repo.get("homepage")
    live_demo = repo.get("live_demo", False)
    repo_name = (repo.get("name") or "").lower()

    # --------------------------------------------------------
    # NO DEMO
    # --------------------------------------------------------

    if not live_demo:
        return {
            "demo_quality_score": 0,
            "demo_quality_verdict": "No live demo",
            "demo_quality_reasons": []
        }

    # --------------------------------------------------------
    # BASE SCORE
    # --------------------------------------------------------

    score += 3
    reasons.append("Live demo detected")

    # --------------------------------------------------------
    # HOMEPAGE BONUS
    # --------------------------------------------------------

    if homepage:
        score += 2
        reasons.append("Repository homepage configured")
# --------------------------------------------------------
    # DOMAIN VALIDATION
    # --------------------------------------------------------

    homepage_domain = extract_domain(homepage)

    for result in demo_results:

        url = result.get("url", "")
        demo_score = result.get("score", 0)

        if extract_domain(url) == homepage_domain:

            if demo_score >= 3:
                score += 3
                reasons.append("Strong demo validation")

            elif demo_score >= 2:
                score += 2
                reasons.append("Moderate demo validation")

            elif demo_score > 0:
                score += 1
                reasons.append("Weak demo validation")

            break

    # --------------------------------------------------------
    # PROJECT-SPECIFIC BONUS
    # --------------------------------------------------------

    if homepage and repo_name:

        homepage_lower = homepage.lower()

        if repo_name.replace("_", "") in homepage_lower.replace("-", ""):
            score += 2
            reasons.append("Project-specific demo URL")

    # --------------------------------------------------------
    # CAP
    # --------------------------------------------------------

    score = min(score, 10)

    # --------------------------------------------------------
    # VERDICT
    # --------------------------------------------------------

    if score >= 9:
        verdict = "Strong verified demo"
    elif score >= 7:
        verdict = "Good live demo"
    elif score >= 5:
        verdict = "Moderate demo quality"
    elif score >= 3:
        verdict = "Basic demo presence"
    else:
        verdict = "Weak demo evidence"

    return {
        "demo_quality_score": score,
        "demo_quality_verdict": verdict,
        "demo_quality_reasons": reasons
    }


# ============================================================
# SHARED DOMAIN EXTRACTION
# ============================================================

from urllib.parse import urlparse


def extract_domain(url):
    try:
        return urlparse(url).netloc.replace("www.", "")
    except:
        return ""