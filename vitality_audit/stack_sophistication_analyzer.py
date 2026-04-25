TECH_SCORES = {
    # frontend
    "react": 6, "nextjs": 9, "vue": 5, "angular": 6, "svelte": 6,
    # backend
    "express": 5, "fastapi": 7, "django": 6, "nestjs": 7, "flask": 4,
    # database
    "mongodb": 5, "postgresql": 6, "mysql": 4, "redis": 6, "prisma": 8,
    "drizzle": 7,
    # infra
    "docker": 8, "kubernetes": 10, "nginx": 6, "vercel": 4, "firebase": 5,
    # ai/ml
    "tensorflow": 10, "pytorch": 10, "langchain": 9, "langgraph": 10,
    "openai": 7, "transformers": 8, "groq": 7,
    # orm
    "sequelize": 5, "typeorm": 5,
    # auth
    "clerk": 6, "nextauth": 5, "jwt": 4,
    # state
    "zustand": 5, "redux": 5, "reactquery": 5,
    # ui
    "tailwind": 4, "shadcn": 5, "radix": 4, "framermotion": 4, "lucide": 2,
    # forms/validation
    "zod": 4, "reacthookform": 4,
    # tooling
    "graphql": 7, "socketio": 6, "axios": 2, "stripe": 5, "cloudinary": 4,
    "typescript": 5,
    # aws
    "aws": 8,
}

# Ecosystem synergy bonuses
SYNERGY_BONUSES = [
    ({"react", "nextjs"},                                    10, "React + NextJS ecosystem"),
    ({"nextjs", "prisma", "tailwind"},                       15, "NextJS + Prisma + Tailwind stack"),
    ({"nextjs", "clerk", "prisma"},                          12, "NextJS + Auth + ORM"),
    ({"nextjs", "zod", "reacthookform"},                     8,  "NextJS + validation stack"),
    ({"express", "mongodb"},                                  8, "MERN backend"),
    ({"fastapi", "postgresql"},                               8, "FastAPI + PostgreSQL"),
    ({"langchain", "openai"},                                12, "LangChain + OpenAI AI stack"),
    ({"langchain", "groq"},                                  12, "LangChain + Groq AI stack"),
    ({"langgraph", "langchain"},                             15, "LangGraph agent stack"),
    ({"react", "express", "mongodb"},                        10, "Full MERN stack"),
    ({"nextjs", "prisma", "postgresql"},                     12, "NextJS + Prisma + PostgreSQL"),
    ({"fastapi", "langchain", "openai"},                     15, "AI API stack"),
    ({"clerk", "prisma", "nextjs"},                          12, "Auth + ORM + NextJS"),
    ({"redis", "express"},                                    6, "Caching layer"),
    ({"docker", "express"},                                   8, "Containerized backend"),
    ({"zustand", "react"},                                    6, "State management"),
    ({"socketio", "express"},                                 8, "Real-time backend"),
    ({"stripe", "nextjs"},                                    8, "Payment integration"),
    ({"cloudinary", "nextjs"},                                6, "Media management"),
    ({"typescript", "nextjs"},                                6, "Type-safe NextJS"),
    ({"reactquery", "nextjs"},                                7, "Server state management"),
]


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

    unique_tech = set(tech.lower() for tech in detected_tech)

    # Tech weight accumulation
    for tech in unique_tech:
        if tech in TECH_SCORES:
            score += TECH_SCORES[tech]
            reasons.append(f"{tech} detected")

    # Breadth bonus
    tech_count = len(unique_tech)
    if tech_count >= 10:
        score += 20
        reasons.append("Large ecosystem stack")
    elif tech_count >= 7:
        score += 15
        reasons.append("Broad technology stack")
    elif tech_count >= 6:
        score += 12
        reasons.append("Strong technology stack")
    elif tech_count >= 5:
        score += 10
        reasons.append("Moderate technology diversity")
    elif tech_count >= 3:
        score += 5
        reasons.append("Basic technology diversity")

    # Synergy bonuses
    for tech_set, bonus, label in SYNERGY_BONUSES:
        if tech_set.issubset(unique_tech):
            score += bonus
            reasons.append(label)

    score = min(score, 100)

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
