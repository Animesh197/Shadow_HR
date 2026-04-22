# ============================================================
# PHASE 3 — PROJECT COMPLEXITY ANALYZER
# ============================================================
# Goal:
# Estimate engineering sophistication of a repository.
#
# Output:
# complexity_score → 0–100
# complexity_verdict → label
# ============================================================


def compute_complexity_score(repo):

    score = 0
    reasons = []

    # --------------------------------------------------------
    # INPUTS AVAILABLE FROM EXISTING PIPELINE
    # --------------------------------------------------------

    language = (repo.get("language") or "").lower()
    infra = repo.get("infra", {})

    alignment_score = repo.get("alignment_score", 0)
    commit_score = repo.get("commit_score", 0)

    # optional future field
    detected_tech = repo.get("detected_tech", [])

    # --------------------------------------------------------
    # 1. LANGUAGE BASE SCORE
    # --------------------------------------------------------

    if language:
        score += 10
        reasons.append("Primary language detected")

    # --------------------------------------------------------
    # 2. INFRA COMPLEXITY
    # --------------------------------------------------------

    if infra.get("has_docker"):
        score += 12
        reasons.append("Docker detected")

    if infra.get("has_ci"):
        score += 10
        reasons.append("CI pipeline detected")

    if infra.get("has_dependencies"):
        score += 8
        reasons.append("Dependency ecosystem detected")

    # --------------------------------------------------------
    # 3. PROJECT MATURITY SIGNALS
    # --------------------------------------------------------

    if commit_score >= 80:
        score += 15
        reasons.append("Strong iterative development")

    elif commit_score >= 60:
        score += 10
        reasons.append("Moderate development maturity")

    elif commit_score >= 40:
        score += 5
        reasons.append("Basic development lifecycle")

    # --------------------------------------------------------
    # 4. README TECH DEPTH
    # --------------------------------------------------------

    if alignment_score >= 80:
        score += 10
        reasons.append("Strong README technical alignment")

    elif alignment_score >= 60:
        score += 6
        reasons.append("Moderate README depth")

    # --------------------------------------------------------
    # 5. DETECTED STACK COMPLEXITY
    # --------------------------------------------------------

    stack_bonus = compute_stack_depth_bonus(detected_tech)

    score += stack_bonus

    if stack_bonus > 0:
        reasons.append("Multi-tech architecture detected")

    # --------------------------------------------------------
    # 6. MULTI-LAYER ARCHITECTURE BONUS
    # --------------------------------------------------------

    architecture_bonus = compute_architecture_bonus(detected_tech)

    score += architecture_bonus

    if architecture_bonus > 0:
        reasons.append("Multi-layer architecture detected")
    # --------------------------------------------------------
    # CAP
    # --------------------------------------------------------

    score = min(score, 100)

    # --------------------------------------------------------
    # VERDICT
    # --------------------------------------------------------

    if score >= 85:
        verdict = "Highly complex engineering project"
    elif score >= 65:
        verdict = "Moderately sophisticated project"
    elif score >= 45:
        verdict = "Intermediate project complexity"
    else:
        verdict = "Basic project complexity"

    return {
        "complexity_score": round(score, 2),
        "complexity_verdict": verdict,
        "complexity_reasons": reasons
    }


# ============================================================
# STACK DEPTH BONUS
# ============================================================

def compute_stack_depth_bonus(detected_tech):

    if not detected_tech:
        return 0

    tech_count = len(set(detected_tech))

    if tech_count >= 10:
        return 20
    elif tech_count >= 7:
        return 15
    elif tech_count >= 5:
        return 10
    elif tech_count >= 3:
        return 5

    return 0
# ============================================================
# ARCHITECTURE BONUS
# ============================================================

def compute_architecture_bonus(detected_tech):

    if not detected_tech:
        return 0

    detected = set([t.lower() for t in detected_tech])

    frontend = {
        "react", "nextjs", "vue", "angular", "svelte"
    }

    backend = {
        "express", "django", "flask", "fastapi", "nestjs"
    }

    database = {
        "mongodb", "postgresql", "mysql", "redis"
    }

    ai_stack = {
        "tensorflow", "pytorch", "langchain", "openai", "transformers"
    }

    infra = {
        "docker", "kubernetes", "nginx"
    }

    categories = 0

    if detected.intersection(frontend):
        categories += 1

    if detected.intersection(backend):
        categories += 1

    if detected.intersection(database):
        categories += 1

    if detected.intersection(ai_stack):
        categories += 1

    if detected.intersection(infra):
        categories += 1

    if categories >= 5:
        return 20
    elif categories >= 4:
        return 15
    elif categories >= 3:
        return 10
    elif categories >= 2:
        return 5

    return 0