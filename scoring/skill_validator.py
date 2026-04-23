# ============================================================
# SKILL VALIDATION ENGINE
# ============================================================
# Maps resume skills → code evidence across repos
# Output: verified, weak_evidence, unsupported
# ============================================================

# Skill → what to look for in dependency signals / detected_tech
SKILL_EVIDENCE_MAP = {
    "react": ["react"],
    "nextjs": ["nextjs"],
    "vue": ["vue"],
    "angular": ["angular"],
    "svelte": ["svelte"],
    "express": ["express"],
    "fastapi": ["fastapi"],
    "django": ["django"],
    "flask": ["flask"],
    "nestjs": ["nestjs"],
    "node.js": ["express", "nestjs"],
    "mongodb": ["mongodb"],
    "postgresql": ["postgresql"],
    "mysql": ["mysql"],
    "redis": ["redis"],
    "prisma": ["prisma"],
    "sequelize": ["sequelize"],
    "typeorm": ["typeorm"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "langchain": ["langchain"],
    "langgraph": ["langchain"],
    "openai": ["openai"],
    "transformers": ["transformers"],
    "docker": ["docker"],
    "tailwind": ["tailwind"],
    "tailwind css": ["tailwind"],
    "graphql": ["graphql"],
    "socket.io": ["socketio"],
    "jest": ["jest"],
    "pytest": ["pytest"],
    "typescript": ["typescript"],
    "python": ["python"],
    "javascript": ["javascript"],
}


def compute_skill_validation(skills, repos):
    """
    Cross-reference resume skills against detected_tech across all repos.

    Returns:
        {
            "verified": [...],
            "weak_evidence": [...],
            "unsupported": [...],
            "validation_score": 0-100
        }
    """

    if not skills or not repos:
        return {
            "verified": [],
            "weak_evidence": [],
            "unsupported": list(skills) if skills else [],
            "validation_score": 0
        }

    # Collect all detected tech across repos
    all_detected = set()
    for repo in repos:
        for tech in repo.get("detected_tech", []):
            all_detected.add(tech.lower())

        # Also check dependency_signals
        dep_signals = repo.get("dependency_signals", {})
        for techs in dep_signals.values():
            for t in techs:
                all_detected.add(t.lower())

    verified = []
    weak_evidence = []
    unsupported = []

    for skill in skills:
        skill_lower = skill.lower()
        evidence_keys = SKILL_EVIDENCE_MAP.get(skill_lower, [skill_lower])

        # Strong match: skill directly in detected tech
        if skill_lower in all_detected:
            verified.append(skill)
            continue

        # Check mapped evidence keys
        matched = any(key in all_detected for key in evidence_keys)

        if matched:
            verified.append(skill)
        elif skill_lower in ["git", "github", "postman", "figma", "ui/ux", "api testing"]:
            # Tools that can't be verified from code — treat as weak
            weak_evidence.append(skill)
        else:
            unsupported.append(skill)

    total = len(skills)
    verified_count = len(verified)
    weak_count = len(weak_evidence)

    validation_score = round(
        ((verified_count + weak_count * 0.5) / max(total, 1)) * 100, 2
    )

    return {
        "verified": verified,
        "weak_evidence": weak_evidence,
        "unsupported": unsupported,
        "validation_score": validation_score
    }
