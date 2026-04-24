def compute_complexity_score(repo):

    score = 0
    reasons = []

    language = (repo.get("language") or "").lower()
    infra = repo.get("infra", {})
    alignment_score = repo.get("alignment_score", 0)
    commit_score = repo.get("commit_score", 0)
    detected_tech = repo.get("detected_tech", [])
    description = repo.get("description") or ""
    stars = repo.get("stars", 0)

    # --------------------------------------------------------
    # GATED BASELINE — reward repos with real substance
    # --------------------------------------------------------

    has_commits = commit_score > 10
    has_deps = infra.get("has_dependencies", False)
    has_readme_or_desc = alignment_score > 0 or len(description) > 10

    if has_commits and has_deps and has_readme_or_desc:
        score += 18
        reasons.append("Repo quality baseline met")

    # --------------------------------------------------------
    # LOGIC / ARCHITECTURE (60% of weight)
    # --------------------------------------------------------

    # commit maturity
    if commit_score >= 80:
        score += 18
        reasons.append("Strong iterative development")
    elif commit_score >= 60:
        score += 12
        reasons.append("Moderate development maturity")
    elif commit_score >= 40:
        score += 6
        reasons.append("Basic development lifecycle")

    # architecture bonus (frontend+backend, backend+db, auth+api)
    architecture_bonus = compute_architecture_bonus(detected_tech)
    score += architecture_bonus
    if architecture_bonus > 0:
        reasons.append("Multi-layer architecture detected")

    # README depth
    if alignment_score >= 60:
        score += 8
        reasons.append("Strong README technical alignment")
    elif alignment_score >= 35:
        score += 4
        reasons.append("Moderate README depth")

    # --------------------------------------------------------
    # TECH DEPTH (25% of weight)
    # --------------------------------------------------------

    stack_bonus = compute_stack_depth_bonus(detected_tech)
    score += stack_bonus
    if stack_bonus > 0:
        reasons.append("Multi-tech architecture detected")

    # --------------------------------------------------------
    # INFRA BONUS ONLY (15% of weight)
    # --------------------------------------------------------

    if infra.get("has_docker"):
        score += 8
        reasons.append("Docker detected")

    if infra.get("has_ci"):
        score += 6
        reasons.append("CI pipeline detected")

    if infra.get("has_deployment_config"):
        score += 4
        reasons.append("Deployment config detected")

    if infra.get("has_dependencies"):
        score += 4
        reasons.append("Dependency ecosystem detected")

    # --------------------------------------------------------
    # CAP + VERDICT
    # --------------------------------------------------------

    score = min(score, 100)

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


def compute_architecture_bonus(detected_tech):
    if not detected_tech:
        return 0

    detected = set(t.lower() for t in detected_tech)

    frontend  = {"react", "nextjs", "vue", "angular", "svelte"}
    backend   = {"express", "django", "flask", "fastapi", "nestjs"}
    database  = {"mongodb", "postgresql", "mysql", "redis", "prisma"}
    ai_stack  = {"tensorflow", "pytorch", "langchain", "openai", "transformers", "groq", "langgraph"}
    infra_set = {"docker", "kubernetes", "nginx"}
    auth      = {"jwt", "clerk", "passport", "authlib"}

    categories = 0
    if detected.intersection(frontend):   categories += 1
    if detected.intersection(backend):    categories += 1
    if detected.intersection(database):   categories += 1
    if detected.intersection(ai_stack):   categories += 1
    if detected.intersection(infra_set):  categories += 1
    if detected.intersection(auth):       categories += 1

    if categories >= 5:  return 22
    elif categories >= 4: return 16
    elif categories >= 3: return 10
    elif categories >= 2: return 6

    return 0
