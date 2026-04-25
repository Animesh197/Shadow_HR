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
    # frontend frameworks
    "react": ["react", "react-dom", "react-scripts"],
    "nextjs": ["next", "nextjs", "@next/font", "next-themes"],
    "vue": ["vue", "nuxt", "@vue/core"],
    "angular": ["@angular/core"],
    "svelte": ["svelte", "@sveltejs/kit"],

    # backend
    "express": ["express", "express-async-handler"],
    "nestjs": ["@nestjs/core", "@nestjs/common"],
    "fastapi": ["fastapi"],
    "django": ["django", "djangorestframework"],
    "flask": ["flask"],

    # database
    "mongodb": ["mongodb", "mongoose"],
    "postgresql": ["postgresql", "psycopg2", "pg", "postgres"],
    "mysql": ["mysql", "mysql2"],
    "redis": ["redis", "ioredis"],

    # ai/ml
    "tensorflow": ["tensorflow", "tensorflow-gpu", "@tensorflow/tfjs"],
    "pytorch": ["torch", "torchvision"],
    "langchain": ["langchain", "@langchain/core", "@langchain/openai", "@langchain/community"],
    "langgraph": ["langgraph", "@langchain/langgraph"],
    "openai": ["openai", "@openai/openai"],
    "groq": ["groq", "groq-sdk"],
    "llamaindex": ["llama-index", "llamaindex"],
    "transformers": ["transformers", "sentence-transformers"],

    # infra
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "nginx": ["nginx"],

    # orm / data
    "prisma": ["prisma", "@prisma/client", "@prisma/adapter"],
    "sequelize": ["sequelize"],
    "typeorm": ["typeorm"],
    "drizzle": ["drizzle-orm", "drizzle-kit"],

    # auth
    "clerk": ["@clerk/nextjs", "@clerk/clerk-sdk-node", "@clerk/react", "clerk"],
    "nextauth": ["next-auth", "next-auth/react", "@auth/core"],
    "jwt": ["jsonwebtoken", "jose", "jwt-decode"],

    # state management
    "zustand": ["zustand"],
    "redux": ["redux", "@reduxjs/toolkit", "react-redux"],
    "reactquery": ["@tanstack/react-query", "react-query", "@tanstack/query-core"],

    # ui / styling
    "tailwind": ["tailwindcss", "@tailwindcss/forms", "@tailwindcss/typography"],
    "shadcn": ["@shadcn/ui", "shadcn-ui", "shadcn"],
    "radix": ["@radix-ui/react-dialog", "@radix-ui/react-dropdown-menu", "@radix-ui/react-slot"],
    "framermotion": ["framer-motion"],
    "lucide": ["lucide-react", "lucide"],

    # forms / validation
    "zod": ["zod"],
    "reacthookform": ["react-hook-form", "@hookform/resolvers"],

    # tooling
    "jest": ["jest", "@jest/core", "vitest"],
    "pytest": ["pytest"],
    "eslint": ["eslint"],
    "typescript": ["typescript", "ts-node", "@types/node"],
    "socketio": ["socket.io", "socket.io-client"],
    "graphql": ["graphql", "@apollo/client", "apollo-server"],
    "axios": ["axios"],
    "stripe": ["stripe", "@stripe/stripe-js"],
    "cloudinary": ["cloudinary", "next-cloudinary"],
    "firebase": ["firebase", "firebase-admin"],
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
    "langgraph": "ai_ml",
    "openai": "ai_ml",
    "groq": "ai_ml",
    "llamaindex": "ai_ml",
    "transformers": "ai_ml",

    "docker": "infra",
    "kubernetes": "infra",
    "nginx": "infra",

    "prisma": "orm",
    "sequelize": "orm",
    "typeorm": "orm",
    "drizzle": "orm",

    "clerk": "auth",
    "nextauth": "auth",
    "jwt": "auth",

    "zustand": "state",
    "redux": "state",
    "reactquery": "state",

    "jest": "testing",
    "pytest": "testing",
    "eslint": "tooling",
    "typescript": "tooling",
    "axios": "tooling",
    "stripe": "tooling",
    "cloudinary": "tooling",
    "firebase": "infra",

    "tailwind": "ui_library",
    "shadcn": "ui_library",
    "radix": "ui_library",
    "framermotion": "ui_library",
    "lucide": "ui_library",

    "zod": "tooling",
    "reacthookform": "tooling",

    "socketio": "networking",
    "graphql": "api",
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
    "auth": 6,
    "state": 4,
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
    readme_lower = readme_text.lower()

    # Normalize common dot-notation variants before matching
    readme_normalized = (
        readme_lower
        .replace("next.js", "nextjs")
        .replace("node.js", "nodejs")
        .replace("express.js", "express")
        .replace("react.js", "react")
        .replace("vue.js", "vue")
        .replace("tailwindcss", "tailwind")
        .replace("react native", "reactnative")
        .replace("react-native", "reactnative")
        .replace("socket.io", "socketio")
        .replace("framer motion", "framermotion")
        .replace("framer-motion", "framermotion")
        .replace("react hook form", "reacthookform")
        .replace("react-hook-form", "reacthookform")
        .replace("next auth", "nextauth")
        .replace("next-auth", "nextauth")
    )

    claimed = set()

    for tech, aliases in MASTER_TECH_MAP.items():
        # also check normalized tech name directly
        if tech in readme_normalized:
            claimed.add(tech)
            continue
        for alias in aliases:
            alias_norm = alias.lower().replace(".", "").replace("-", "").replace("/", "").replace("@", "")
            if alias_norm in readme_normalized or regex_contains(readme_normalized, alias.lower()):
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
                alias_lower = alias.lower()
                # substring match handles scoped packages like @prisma/client
                if any(alias_lower in dep or dep in alias_lower for dep in dep_names):
                    detected[tech] = {
                        "source": "package.json",
                        "confidence": SOURCE_CONFIDENCE["package.json"]
                    }
                    break

    except Exception as e:
        import logging
        logging.warning(f"[readme_analyzer] package.json parse error: {e}")

    return detected


# ============================================================
# STEP 10: REQUIREMENTS PARSER
# ============================================================

def extract_from_requirements(content):
    detected = {}

    try:
        lines = [line.strip().lower() for line in content.splitlines()]

        for line in lines:
            if not line or line.startswith("#"):
                continue
            # strip version specifiers: fastapi>=0.95 → fastapi
            pkg_name = re.split(r"[>=<!;\[]", line)[0].strip()
            for tech, aliases in MASTER_TECH_MAP.items():
                for alias in aliases:
                    if alias.lower() in pkg_name or pkg_name in alias.lower():
                        detected[tech] = {
                            "source": "requirements.txt",
                            "confidence": SOURCE_CONFIDENCE["requirements.txt"]
                        }
                        break

    except Exception as e:
        import logging
        logging.warning(f"[readme_analyzer] requirements.txt parse error: {e}")

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
                if alias.lower() in lowered:
                    detected[tech] = {
                        "source": "pyproject.toml",
                        "confidence": SOURCE_CONFIDENCE["pyproject.toml"]
                    }
                    break

    except Exception as e:
        import logging
        logging.warning(f"[readme_analyzer] pyproject.toml parse error: {e}")

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

    # Always fetch all dependency files regardless of language
    package_content = fetch_file_content(owner, repo_name, "package.json")
    req_content = fetch_file_content(owner, repo_name, "requirements.txt")
    pyproject_content = fetch_file_content(owner, repo_name, "pyproject.toml")

    # Additional config files
    next_config = fetch_file_content(owner, repo_name, "next.config.js")
    vite_config = fetch_file_content(owner, repo_name, "vite.config.js")
    tsconfig = fetch_file_content(owner, repo_name, "tsconfig.json")
    firebase_config = fetch_file_content(owner, repo_name, "firebase.json")
    prisma_schema = fetch_file_content(owner, repo_name, "prisma/schema.prisma")

    docker_content = fetch_file_content(owner, repo_name, "Dockerfile")

    # ------------------------------------------------------------
    # PHASE 8 — DEPENDENCY SIGNAL CACHE (structured)
    # ------------------------------------------------------------

    parsed_pkg = extract_from_package_json(package_content)
    parsed_req = extract_from_requirements(req_content)
    parsed_pyproject = extract_from_pyproject(pyproject_content)

    all_detected = {}
    all_detected.update(parsed_pkg)
    all_detected.update(parsed_req)
    all_detected.update(parsed_pyproject)

    import logging
    logging.debug(f"[collect_repo_evidence] {repo_name}: pkg={list(parsed_pkg.keys())} req={list(parsed_req.keys())} pyproject={list(parsed_pyproject.keys())}")

    # Build structured dependency signals by category
    dep_signals = {"frontend": [], "backend": [], "database": [], "auth": [], "ai": [], "infra": [], "other": []}
    for tech in all_detected:
        cat = TECH_CATEGORY_MAP.get(tech, "other")
        if cat == "core_framework":
            dep_signals["frontend"].append(tech)
        elif cat == "backend":
            dep_signals["backend"].append(tech)
        elif cat == "database":
            dep_signals["database"].append(tech)
        elif cat == "ai_ml":
            dep_signals["ai"].append(tech)
        elif cat == "infra":
            dep_signals["infra"].append(tech)
        else:
            dep_signals["other"].append(tech)

    # jwt/auth detection
    pkg_lower = package_content.lower() + req_content.lower()
    if any(kw in pkg_lower for kw in ["jsonwebtoken", "jwt", "passport", "bcrypt", "authlib", "python-jose"]):
        dep_signals["auth"].append("jwt/auth")

    repo_data["dependency_signals"] = dep_signals

    # Infer nextjs/vite from config files
    if next_config:
        all_detected["nextjs"] = {"source": "next.config.js", "confidence": 0.95}
    if vite_config:
        all_detected["react"] = all_detected.get("react") or {"source": "vite.config.js", "confidence": 0.9}
    if prisma_schema:
        all_detected["prisma"] = {"source": "prisma/schema.prisma", "confidence": 1.0}
    if firebase_config:
        all_detected["firebase"] = {"source": "firebase.json", "confidence": 1.0}

    sources = [all_detected, detect_dockerfile(docker_content)]

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

    # If README has no recognized tech claims but evidence exists, give partial credit
    if not readme_claims and repo_evidence:
        evidence_count = len(repo_evidence)
        partial_score = min(evidence_count * 8, 60)
        return {
            "alignment_score": round(partial_score, 2),
            "verdict": classify_alignment(partial_score),
            "confidence": compute_confidence(repo_evidence),
            "claimed_tech": [],
            "verified_tech": list(repo_evidence.keys()),
            "false_claims": []
        }

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
