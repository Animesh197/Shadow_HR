# ============================================================
# PHASE 5 — STACK SOPHISTICATION ANALYZER
# ============================================================
# Goal:
# Reward advanced engineering stacks.
#
# Output:
# stack_score → 0–100
# stack_verdict
# ============================================================


TECH_SCORES = {

    # frontend
    "react": 6,
    "nextjs": 7,
    "vue": 5,
    "angular": 6,
    "svelte": 6,

    # backend
    "express": 5,
    "fastapi": 7,
    "django": 6,
    "nestjs": 7,
    "flask": 4,

    # database
    "mongodb": 5,
    "postgresql": 6,
    "mysql": 4,
    "redis": 5,

    # infra
    "docker": 8,
    "kubernetes": 10,
    "nginx": 6,

    # ai/ml
    "tensorflow": 10,
    "pytorch": 10,
    "langchain": 9,
    "openai": 7,
    "transformers": 8,

    # orm
    "prisma": 7,
    "sequelize": 5,
    "typeorm": 5,

    # tooling
    "graphql": 7,
    "socketio": 6,
    "tailwind": 3,
    "axios": 2,
}
# ============================================================
# MAIN STACK SCORING
# ============================================================

def compute_stack_score(repo):

    score = 0
    reasons = []

    detected_tech = repo.get("detected_tech", [])

    if not detected_tech:
        return {
            "stack_score": 0,
            "stack_verdict": "No stack detected",
            "stack_reasons": []
        }

    # --------------------------------------------------------
    # UNIQUE STACK
    # --------------------------------------------------------

    unique_tech = set([tech.lower() for tech in detected_tech])

    # --------------------------------------------------------
    # TECH WEIGHT ACCUMULATION
    # --------------------------------------------------------

    for tech in unique_tech:

        if tech in TECH_SCORES:
            score += TECH_SCORES[tech]
            reasons.append(f"{tech} contributes to sophistication")

    # --------------------------------------------------------
    # STACK BREADTH BONUS
    # --------------------------------------------------------

    tech_count = len(unique_tech)

    if tech_count >= 10:
        score += 20
        reasons.append("Large ecosystem stack")

    elif tech_count >= 7:
        score += 15
        reasons.append("Broad technology stack")

    elif tech_count >= 5:
        score += 10
        reasons.append("Moderate technology diversity")
        # --------------------------------------------------------
    # ADVANCED STACK COMBINATIONS
    # --------------------------------------------------------

    advanced_bonus = compute_advanced_stack_bonus(unique_tech)

    score += advanced_bonus

    if advanced_bonus > 0:
        reasons.append("Advanced architecture combination detected")

    # --------------------------------------------------------
    # CAP
    # --------------------------------------------------------

    score = min(score, 100)

    # --------------------------------------------------------
    # VERDICT
    # --------------------------------------------------------

    if score >= 85:
        verdict = "Highly sophisticated engineering stack"
    elif score >= 65:
        verdict = "Strong modern stack"
    elif score >= 45:
        verdict = "Moderately advanced stack"
    else:
        verdict = "Basic technology stack"

    return {
        "stack_score": round(score, 2),
        "stack_verdict": verdict,
        "stack_reasons": reasons
    }

# ============================================================
# ADVANCED STACK BONUS
# ============================================================

def compute_advanced_stack_bonus(unique_tech):

    bonus = 0

    # --------------------------------------------------------
    # AI + Backend
    # --------------------------------------------------------

    ai_stack = {
        "tensorflow", "pytorch", "langchain", "openai", "transformers"
    }

    backend = {
        "express", "fastapi", "django", "flask", "nestjs"
    }

    database = {
        "mongodb", "postgresql", "mysql", "redis"
    }

    infra = {
        "docker", "kubernetes", "nginx"
    }

    frontend = {
        "react", "nextjs", "vue", "angular", "svelte"
    }

    # --------------------------------------------------------
    # Combination scoring
    # --------------------------------------------------------

    if unique_tech.intersection(ai_stack) and unique_tech.intersection(backend):
        bonus += 10

    if unique_tech.intersection(frontend) and unique_tech.intersection(backend):
        bonus += 8

    if unique_tech.intersection(database) and unique_tech.intersection(backend):
        bonus += 6

    if unique_tech.intersection(infra):
        bonus += 6

    return min(bonus, 25)