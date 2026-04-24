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


def compute_skill_validation(skills, repos, all_repos=None):
    """
    Cross-reference resume skills against detected_tech.
    Scans final_repos deeply + lightweight scan of all_repos (top 15–20).
    """

    if not skills or not repos:
        return {
            "verified": [],
            "weak_evidence": [],
            "unsupported": list(skills) if skills else [],
            "validation_score": 0
        }

    # Collect detected tech from final repos (deep)
    all_detected = set()
    for repo in repos:
        for tech in repo.get("detected_tech", []):
            all_detected.add(tech.lower())
        dep_signals = repo.get("dependency_signals", {})
        for techs in dep_signals.values():
            for t in techs:
                all_detected.add(t.lower())

    # Lightweight scan of broader repo pool (topics, description, language)
    scan_pool = all_repos or []
    for repo in scan_pool[:20]:
        lang = (repo.get("language") or "").lower()
        if lang:
            all_detected.add(lang)
        for topic in (repo.get("topics") or []):
            all_detected.add(topic.lower())
        desc = (repo.get("description") or "").lower()
        for tech in SKILL_EVIDENCE_MAP:
            if tech in desc:
                all_detected.add(tech)

    verified = []
    weak_evidence = []
    unsupported = []

    # Language/ecosystem inference map for medium evidence
    ECOSYSTEM_MAP = {
        "javascript": {"react", "nextjs", "express", "vue", "angular", "node.js"},
        "typescript": {"react", "nextjs", "express", "nestjs", "angular"},
        "python": {"fastapi", "django", "flask", "langchain", "tensorflow", "pytorch"},
    }

    for skill in skills:
        skill_lower = skill.lower()
        evidence_keys = SKILL_EVIDENCE_MAP.get(skill_lower, [skill_lower])

        # Strong evidence: exact dependency/import match
        if skill_lower in all_detected:
            verified.append(skill)
            continue

        matched = any(key in all_detected for key in evidence_keys)
        if matched:
            verified.append(skill)
            continue

        # Medium evidence: ecosystem/language match
        ecosystem_match = False
        for lang, ecosystem in ECOSYSTEM_MAP.items():
            if lang in all_detected and skill_lower in ecosystem:
                ecosystem_match = True
                break
        if ecosystem_match:
            weak_evidence.append(skill)
            continue

        # Weak evidence: tools that can't be verified from code
        if skill_lower in ["git", "github", "postman", "figma", "ui/ux", "api testing",
                            "nosql", "html", "css", "sql"]:
            weak_evidence.append(skill)
            continue

        # Unverified — no signal found, but don't penalize heavily
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
