def skill_match_score(skills, repo):
    text = (
        (repo.get("name") or "") + " " +
        (repo.get("description") or "") + " " +
        " ".join(repo.get("topics") or [])
    ).lower()

    if not skills:
        return 0

    matches = sum(1 for skill in skills if skill.lower() in text)

    return matches / len(skills)


def repo_quality_score(repo):
    score = 0

    if repo.get("description"):
        score += 0.4

    if repo.get("language"):
        score += 0.3

    if repo.get("topics"):
        score += 0.3

    return min(score, 1.0)