# ============================================================
# UPDATED README ANALYZER (PRODUCTION READY)
# ============================================================
# Improvements:
# 1. Regex-safe tech detection
# 2. Modern ecosystem support
# 3. Deep package.json parsing
# 4. requirements.txt + pyproject.toml parsing
# 5. Weighted scoring
# 6. False-claim penalties
# 7. Confidence score
# 8. Better verdict granularity
# ============================================================

import requests
import base64
import os
import json
import re
from collections import defaultdict
from utils.github_cache import get_cached_file, set_cached_file


# ============================================================
# STEP 1: MASTER TECH MAP
# ============================================================
# normalized_name : aliases

MASTER_TECH_MAP = {
    "react": ["react", "react-dom"],
    "nextjs": ["next", "nextjs"],
    "vue": ["vue", "nuxt"],
    "angular": ["@angular/core"],
    "svelte": ["svelte"],

    "express": ["express"],
    "nestjs": ["@nestjs/core"],
    "fastapi": ["fastapi"],
    "django": ["django"],
    "flask": ["flask"],

    "mongodb": ["mongodb", "mongoose"],
    "postgresql": ["postgresql", "psycopg2", "pg"],
    "mysql": ["mysql"],
    "redis": ["redis"],

    "tensorflow": ["tensorflow", "tensorflow-gpu"],
    "pytorch": ["torch", "torchvision"],
    "langchain": ["langchain", "@langchain/core"],
    "openai": ["openai"],
    "llamaindex": ["llama-index"],
    "transformers": ["transformers", "sentence-transformers"],

    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "nginx": ["nginx"],

    "prisma": ["prisma"],
    "sequelize": ["sequelize"],
    "typeorm": ["typeorm"],

    "jest": ["jest"],
    "pytest": ["pytest"],
    "eslint": ["eslint"],
    "tailwind": ["tailwindcss"],
    "socketio": ["socket.io"],
    "graphql": ["graphql"],
    "axios": ["axios"],
}


# ============================================================
# STEP 2: CATEGORY MAP
# ============================================================

TECH_CATEGORY_MAP = {
    "react": "core_framework",
    "nextjs": "core_framework",
    "vue": "core_framework",
    "angular": "core_framework",
    "svelte": "core_framework",

    "express": "backend",
    "nestjs": "backend",
    "fastapi": "backend",
    "django": "backend",
    "flask": "backend",

    "mongodb": "database",
    "postgresql": "database",
    "mysql": "database",
    "redis": "database",

    "tensorflow": "ai_ml",
    "pytorch": "ai_ml",
    "langchain": "ai_ml",
    "openai": "ai_ml",
    "llamaindex": "ai_ml",
    "transformers": "ai_ml",

    "docker": "infra",
    "kubernetes": "infra",
    "nginx": "infra",

    "prisma": "orm",
    "sequelize": "orm",
    "typeorm": "orm",

    "jest": "testing",
    "pytest": "testing",
    "eslint": "tooling",
    "tailwind": "ui_library",
    "socketio": "networking",
    "graphql": "api",
    "axios": "tooling",
}


# ============================================================
# STEP 3: CATEGORY WEIGHTS
# ============================================================

TECH_WEIGHTS = {
    "core_framework": 10,
    "backend": 9,
    "database": 8,
    "ai_ml": 10,
    "infra": 7,
    "orm": 6,
    "testing": 4,
    "ui_library": 3,
    "networking": 4,
    "api": 5,
    "tooling": 2,
}


# ============================================================
# STEP 4: SOURCE CONFIDENCE
# ============================================================

SOURCE_CONFIDENCE = {
    "package.json": 1.0,
    "requirements.txt": 1.0,
    "pyproject.toml": 1.0,
    "dockerfile": 0.9,
    "infra": 0.85,
    "language": 0.5,
}


# ============================================================
# STEP 5: FILE FETCHER
# ============================================================

def fetch_file_content(owner, repo, path):

    # --------------------------------------------------------
    # CACHE HIT
    # --------------------------------------------------------

    cached = get_cached_file(owner, repo, path)

    if cached is not None:
        return cached

    # --------------------------------------------------------
    # API FETCH
    # --------------------------------------------------------

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    headers = {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code != 200:
            set_cached_file(owner, repo, path, "")
            return ""

        data = response.json()

        content = base64.b64decode(
            data.get("content", "")
        ).decode("utf-8")

        # ----------------------------------------------------
        # CACHE STORE
        # ----------------------------------------------------

        set_cached_file(owner, repo, path, content)

        return content

    except Exception:
        return ""


# ============================================================
# STEP 6: README FETCHER
# ============================================================

def fetch_readme(owner, repo):
    readme_paths = [
        "README.md",
        "readme.md",
        "README.MD",
        "Readme.md"
    ]

    for path in readme_paths:
        content = fetch_file_content(owner, repo, path)
        if content:
            return content

    return ""


# ============================================================
# STEP 7: REGEX SAFE MATCH
# ============================================================

def regex_contains(text, keyword):
    pattern = rf"\b{re.escape(keyword)}\b"
    return bool(re.search(pattern, text, re.IGNORECASE))


# ============================================================
# STEP 8: README CLAIM EXTRACTION
# ============================================================

def extract_claimed_tech(readme_text):
    readme_text = readme_text.lower()

    claimed = set()

    for tech, aliases in MASTER_TECH_MAP.items():
        for alias in aliases:
            if regex_contains(readme_text, alias.lower()):
                claimed.add(tech)
                break

    return claimed


# ============================================================
# STEP 9: PACKAGE.JSON PARSER
# ============================================================

def extract_from_package_json(content):
    detected = {}

    try:
        data = json.loads(content)

        dependencies = {}

        for section in [
            "dependencies",
            "devDependencies",
            "peerDependencies",
            "optionalDependencies"
        ]:
            dependencies.update(data.get(section, {}))

        dep_names = [dep.lower() for dep in dependencies.keys()]

        for tech, aliases in MASTER_TECH_MAP.items():
            for alias in aliases:
                if alias.lower() in dep_names:
                    detected[tech] = {
                        "source": "package.json",
                        "confidence": SOURCE_CONFIDENCE["package.json"]
                    }
                    break

    except Exception:
        pass

    return detected


# ============================================================
# STEP 10: REQUIREMENTS PARSER
# ============================================================

def extract_from_requirements(content):
    detected = {}

    try:
        lines = [line.strip().lower() for line in content.splitlines()]

        for line in lines:
            for tech, aliases in MASTER_TECH_MAP.items():
                for alias in aliases:
                    if regex_contains(line, alias.lower()):
                        detected[tech] = {
                            "source": "requirements.txt",
                            "confidence": SOURCE_CONFIDENCE["requirements.txt"]
                        }
                        break

    except Exception:
        pass

    return detected


# ============================================================
# STEP 11: PYPROJECT.TOML PARSER
# ============================================================

def extract_from_pyproject(content):
    detected = {}

    try:
        lowered = content.lower()

        for tech, aliases in MASTER_TECH_MAP.items():
            for alias in aliases:
                if regex_contains(lowered, alias.lower()):
                    detected[tech] = {
                        "source": "pyproject.toml",
                        "confidence": SOURCE_CONFIDENCE["pyproject.toml"]
                    }
                    break

    except Exception:
        pass

    return detected


# ============================================================
# STEP 12: DOCKERFILE DETECTOR
# ============================================================

def detect_dockerfile(content):
    if not content:
        return {}

    return {
        "docker": {
            "source": "dockerfile",
            "confidence": SOURCE_CONFIDENCE["dockerfile"]
        }
    }


# ============================================================
# STEP 13: EVIDENCE COLLECTION
# ============================================================

def collect_repo_evidence(owner, repo_name, repo_data):
    evidence = defaultdict(list)

    language = (repo_data.get("language") or "").lower()

    package_content = ""
    req_content = ""
    pyproject_content = ""

    # language-aware fetch
    if language in ["javascript", "typescript"]:
        package_content = fetch_file_content(owner, repo_name, "package.json")

    elif language == "python":
        req_content = fetch_file_content(owner, repo_name, "requirements.txt")
        pyproject_content = fetch_file_content(owner, repo_name, "pyproject.toml")

    else:
        package_content = fetch_file_content(owner, repo_name, "package.json")
        req_content = fetch_file_content(owner, repo_name, "requirements.txt")
        pyproject_content = fetch_file_content(owner, repo_name, "pyproject.toml")

    docker_content = fetch_file_content(owner, repo_name, "Dockerfile")
    
    # ------------------------------------------------------------
    # PHASE 8 — DEPENDENCY SIGNAL CACHE
    # ------------------------------------------------------------

    repo_data["dependency_signals"] = {
        "package_json": package_content,
        "requirements": req_content,
        "pyproject": pyproject_content
    }

    sources = [
        extract_from_package_json(package_content),
        extract_from_requirements(req_content),
        extract_from_pyproject(pyproject_content),
        detect_dockerfile(docker_content)
    ]

    for source in sources:
        for tech, metadata in source.items():
            evidence[tech].append(metadata)

    # language fallback
    if language:
        evidence[language].append({
            "source": "language",
            "confidence": SOURCE_CONFIDENCE["language"]
        })

    # infra fallback
    infra = repo_data.get("infra", {})

    if infra.get("has_docker"):
        evidence["docker"].append({
            "source": "infra",
            "confidence": SOURCE_CONFIDENCE["infra"]
        })

    return evidence


# ============================================================
# STEP 14: WEIGHTED MATCH
# ============================================================

def calculate_weighted_match(readme_claims, repo_evidence):
    matched_weight = 0
    total_weight = 0

    for tech in readme_claims:
        category = TECH_CATEGORY_MAP.get(tech, "tooling")
        weight = TECH_WEIGHTS.get(category, 2)

        total_weight += weight

        if tech in repo_evidence:
            matched_weight += weight

    if total_weight == 0:
        return 0

    return matched_weight / total_weight


# ============================================================
# STEP 15: FALSE CLAIM PENALTY
# ============================================================

def compute_false_claim_penalty(readme_claims, repo_evidence):
    penalty = 0

    for tech in readme_claims:
        if tech not in repo_evidence:
            category = TECH_CATEGORY_MAP.get(tech, "tooling")
            weight = TECH_WEIGHTS.get(category, 2)

            penalty += weight * 0.5

    return penalty


# ============================================================
# STEP 16: CONFIDENCE SCORE
# ============================================================

def compute_confidence(repo_evidence):
    if not repo_evidence:
        return 0

    confidence_sum = 0
    count = 0

    for _, evidence_list in repo_evidence.items():
        best_confidence = max(item["confidence"] for item in evidence_list)
        confidence_sum += best_confidence
        count += 1

    return round(confidence_sum / count, 2)


# ============================================================
# STEP 17: ALIGNMENT CLASSIFIER
# ============================================================

def classify_alignment(score):
    if score >= 95:
        return "Perfect alignment"
    elif score >= 80:
        return "Strong alignment"
    elif score >= 60:
        return "Mostly aligned"
    elif score >= 40:
        return "Partial alignment"
    elif score >= 20:
        return "Weak alignment"
    else:
        return "Mismatch / possible exaggeration"


# ============================================================
# STEP 18: MAIN ANALYZER
# ============================================================

def analyze_readme_alignment(owner, repo_name, repo_data):

    readme = fetch_readme(owner, repo_name)

    if not readme:
        return {
            "alignment_score": 20,
            "verdict": "No README found",
            "confidence": 0.3,
            "claimed_tech": [],
            "verified_tech": [],
            "false_claims": []
        }

    readme_claims = extract_claimed_tech(readme)

    repo_evidence = collect_repo_evidence(
        owner,
        repo_name,
        repo_data
    )

    weighted_ratio = calculate_weighted_match(
        readme_claims,
        repo_evidence
    )

    penalty = compute_false_claim_penalty(
        readme_claims,
        repo_evidence
    )

    confidence = compute_confidence(repo_evidence)

    adjusted_score = max(0, weighted_ratio * 100 - penalty)
    adjusted_score = min(100, adjusted_score)

    verdict = classify_alignment(adjusted_score)

    false_claims = [
        tech for tech in readme_claims
        if tech not in repo_evidence
    ]

    return {
        "alignment_score": round(adjusted_score, 2),
        "verdict": verdict,
        "confidence": confidence,
        "claimed_tech": list(readme_claims),
        "verified_tech": list(repo_evidence.keys()),
        "false_claims": false_claims
    }
