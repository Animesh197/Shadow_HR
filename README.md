# AI Resume Auditor

> An end-to-end AI-powered resume verification system that cross-references resume claims against live GitHub repositories, validates deployed demos, analyzes engineering depth, and produces a recruiter-ready credibility score.

---

## Problem Statement

Resumes lie — not always intentionally, but consistently.

Candidates list projects they barely touched, claim skills they googled once, and link GitHub repos that are empty or copied. Recruiters have no fast, reliable way to verify technical depth before an interview.

**AI Resume Auditor solves this.**

It takes a PDF resume, extracts every technical claim, fetches the candidate's GitHub repositories, runs a multi-layer analysis pipeline across commit history, README alignment, stack sophistication, infrastructure maturity, and live demo validation — then produces a structured credibility score with recruiter-readable explanations.

---

## Key Features

- PDF resume parsing with embedded link extraction
- LLM-powered entity extraction (name, GitHub, skills, projects)
- GitHub repository fetching with full pagination
- Intelligent repo pre-filtering using project name + skill + recency signals
- Semantic + fuzzy project-to-repo matching
- README alignment scoring against actual dependency evidence
- Stack sophistication analysis with ecosystem synergy bonuses
- Commit pattern analysis for development authenticity
- Infrastructure maturity detection (Docker, CI/CD, deployment configs)
- Live demo URL validation with interactivity detection
- Skill verification against code evidence across all repos
- Portfolio-level credibility scoring with penalty balancing
- Repo tiering (Flagship / Supporting / Practice / Weak)
- Streamlit UI with full engineering breakdown per repository
- Parallel execution with thread-safe caching for performance

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                          │
│              PDF Resume → Text + Embedded Links             │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      LLM EXTRACTION                         │
│         Groq (Llama 3.3 70B) → name, github, skills,       │
│                    projects, links                          │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    GITHUB DATA LAYER                        │
│         Paginated repo fetch → metadata + homepages         │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   URL VALIDATION LAYER                      │
│    Async pulse check (aiohttp) + Parallel demo validation   │
│         (ThreadPoolExecutor) + Playwright fallback          │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    PREFILTER ENGINE                         │
│     Project name match + skill overlap + recency + stars    │
│              Force-include resume-linked repos              │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│              PARALLEL REPO ENRICHMENT (5 workers)           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ Infra Scan   │ │ Commit Audit │ │  README Alignment    │ │
│  │ (cached)     │ │ (cached)     │ │  + Dep Extraction    │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
│  ┌──────────────────────┐ ┌───────────────────────────────┐  │
│  │ Stack Sophistication │ │ Complexity Scoring            │  │
│  └──────────────────────┘ └───────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│               SEMANTIC PROJECT MATCHING                     │
│    Fuzzy + token overlap + sentence-transformer embeddings  │
│         Batch pre-encoded for performance                   │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                  PORTFOLIO SCORING ENGINE                   │
│   Repo score → weighted portfolio score → penalty system    │
│        Skill validation → confidence score → tiering        │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                     STREAMLIT UI                            │
│   Score dashboard + repo breakdown + engineering signals    │
└─────────────────────────────────────────────────────────────┘
```

---

## End-to-End Pipeline

```
1. PDF Upload
   └── Extract raw text + embedded hyperlinks (PyMuPDF)

2. LLM Entity Extraction
   └── Groq API → structured JSON: name, github, skills[], projects[]

3. GitHub Username Resolution
   └── Priority: resume links > LLM output

4. Repository Fetch
   └── Paginated GitHub API → all public repos with metadata + homepages

5. URL Pulse Check
   └── Async aiohttp HEAD requests → alive/dead status for all links

6. Demo URL Validation
   └── Parallel classification → hosted_demo / code / ignored / unknown
   └── Interactivity detection → HTML keyword + Playwright fallback

7. Repo Pre-filter
   └── Score each repo: project name match + skill overlap + recency + stars
   └── Force-include repos directly linked in resume
   └── Select top 8 for deep analysis

8. Parallel Repo Enrichment (per repo, 5 outer + 3 inner threads)
   ├── Infra scan: Docker, CI, deployment configs, dependencies
   ├── Commit analysis: pattern scoring, lifespan, gap analysis
   ├── README alignment: tech claim extraction vs dependency evidence
   ├── Stack sophistication: tech weights + synergy bonuses
   └── Complexity scoring: architecture depth + gated baseline

9. Semantic Project Matching
   └── Batch embeddings → fuzzy + token + semantic scoring per project

10. Portfolio Scoring
    └── Repo score per repo → weighted portfolio aggregation
    └── Penalty system with forgiveness rules
    └── Skill validation across all repos
    └── Repo tiering + confidence scoring

11. Output
    └── final_score, label, reasons, repos[], skill_validation, audit{}
```

---

## Scoring Logic

### Per-Repository Score (0–100)

Each repository is scored independently before portfolio aggregation.

| Parameter | Weight | What It Measures |
|---|---|---|
| Complexity Score | 25% | Architecture depth, gated baseline, multi-layer detection |
| README Alignment | 20% | Tech claims in README vs actual dependency evidence (capped at 80) |
| Stack Sophistication | 20% | Tech weights + ecosystem synergy bonuses |
| Commit Quality | 15% | Development authenticity, lifespan, commit density |
| Demo Quality | 10% | Live demo presence, interactivity, homepage validation |
| Infra Maturity | 5% | Docker, CI/CD, deployment configs (bonus only) |
| Recency + Stars | 5% | Last push recency + star count |

**Complexity Score** is gated — a repo must have commits, dependencies, and a README/description to receive the baseline bonus (+18). This prevents empty repos from scoring artificially.

**README Alignment** compares tech keywords claimed in the README against evidence from `package.json`, `requirements.txt`, `pyproject.toml`, `prisma/schema.prisma`, `firebase.json`, `next.config.js`, and other config files. Repos with no README but strong dependency evidence receive partial credit (up to 60).

**Stack Sophistication** rewards ecosystem synergy, not just library count:
- React + NextJS → +10
- NextJS + Prisma + Tailwind → +15
- LangChain + Groq → +12
- LangGraph agent stack → +15
- Full MERN stack → +10

**Infra Maturity** is bonus-only. Missing Docker or CI does not penalize — it simply adds no upside.

---

### Portfolio Final Score (0–100)

| Component | Weight | Formula |
|---|---|---|
| Weighted Repo Strength | 35% | top_repo×0.7 + second×0.2 + third×0.1 |
| Project Match Ratio | 20% | verified_projects / total_claimed |
| Consistency | 15% | avg(live_demo + commits≥60 + alignment≥40 + complexity≥45) |
| Demo Strength | 10% | fraction of repos with demo_score ≥ 3 |
| Diversity | 10% | fraction of repos scoring ≥ 50 (capped at 3) |
| Complexity Index | 5% | avg complexity across repos / 100 |
| Skill Validation | 5% | verified + 0.5×weak_evidence / total_skills |

**Penalty System** (max 12 points):
- Most projects missing (>70%): −12
- Many projects missing (>50%): −6
- Per missing project: −2 each
- Weak commit history per repo: −2
- Dumped code detected: −4
- Low README alignment per repo: −1
- Low complexity per repo: −1
- No live demos: −3

**Penalty Reductions:**
- At least 1 project matched → penalty × 0.7
- Live demo exists → penalty × 0.8
- Strong verified repos (score ≥ 50) with missing projects → penalty × 0.5

---

### Score Labels

| Score Range | Label |
|---|---|
| 85–100 | Strong Authentic |
| 70–84 | Likely Authentic |
| 55–69 | Moderate Confidence |
| 35–54 | Needs Review |
| 0–34 | Suspicious |

---

### Repo Tiers

| Tier | Score Threshold | Meaning |
|---|---|---|
| Tier 1 — Flagship | ≥ 75 | Showcase-quality project |
| Tier 2 — Supporting | ≥ 50 | Solid, real project |
| Tier 3 — Practice | ≥ 25 | Learning/tutorial project |
| Tier 4 — Weak/Noisy | < 25 | Minimal or empty repo |

---

## Tech Stack

| Layer | Technology |
|---|---|
| PDF Parsing | PyMuPDF (fitz) |
| LLM Extraction | Groq API (Llama 3.3 70B) |
| GitHub API | requests (paginated) |
| Async URL Check | aiohttp + asyncio |
| Parallel Execution | concurrent.futures ThreadPoolExecutor |
| Browser Rendering | Playwright (Chromium, headless) |
| Semantic Matching | sentence-transformers (all-MiniLM-L6-v2) |
| Similarity | scikit-learn cosine_similarity |
| UI | Streamlit |
| Caching | Thread-safe in-process dict (github_cache) |
| Environment | python-dotenv |

---

## Folder Structure

```
resume_auditor/
├── main.py                          # Pipeline entrypoint
├── github_utils.py                  # Paginated GitHub repo fetch
├── requirements.txt
├── .env
│
├── data_pipeline/
│   ├── pdf_extractor.py             # PDF text + link extraction
│   ├── entity_parser.py             # LLM entity extraction (Groq)
│   └── github_finder.py             # GitHub username normalization
│
├── vitality_audit/
│   ├── repo_selector.py             # Prefilter, enrichment, matching, scoring
│   ├── readme_analyzer.py           # README alignment + dependency evidence
│   ├── commit_analyzer.py           # Commit pattern analysis
│   ├── infra_analyzer.py            # Infrastructure detection
│   ├── complexity_analyzer.py       # Engineering complexity scoring
│   ├── stack_sophistication_analyzer.py  # Stack depth + synergy
│   ├── demo_quality_analyzer.py     # Demo quality scoring
│   ├── pulse_checker.py             # Async URL liveness check
│   ├── semantic_matcher.py          # Sentence transformer embeddings
│   └── matching/
│       ├── matcher.py               # Project-to-repo matching orchestrator
│       ├── candidate_generator.py   # Candidate repo shortlisting
│       ├── feature_extractor.py     # Feature vector extraction
│       ├── reranker.py              # Final match scoring + classification
│       └── text_utils.py            # Normalization + token overlap
│
├── validation/
│   ├── demo_url_validator.py        # Parallel demo URL classification
│   └── browser_validator.py        # Playwright HTML rendering
│
├── scoring/
│   ├── verification_index.py        # Portfolio final score
│   ├── confidence_score.py          # Confidence scoring
│   └── skill_validator.py           # Skill evidence validation
│
├── utils/
│   └── github_cache.py              # Thread-safe file content cache
│
├── ui/
│   └── app.py                       # Streamlit dashboard
│
└── resumes/                         # Resume PDFs (gitignored)
```

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/resume-auditor.git
cd resume-auditor

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browser
playwright install chromium

# 5. Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

---

## Environment Variables

```env
GROQ_API_KEY=your_groq_api_key_here
GITHUB_TOKEN=your_github_personal_access_token_here
```

**GROQ_API_KEY** — Get from [console.groq.com](https://console.groq.com). Free tier available.

**GITHUB_TOKEN** — Generate at GitHub → Settings → Developer Settings → Personal Access Tokens (Classic). Only `public_repo` scope needed.

---

## Usage

### Streamlit UI

```bash
streamlit run ui/app.py
```

Open `http://localhost:8501`, upload a PDF resume, and wait for the analysis.

### CLI

```bash
python main.py
```

Edit `pdf_path` in `main.py` to point to your resume file. Output is printed as structured JSON.

---

## Example Audit Output

```json
{
  "candidate": {
    "name": "Jane Doe",
    "github": "janedoe",
    "skills": ["React", "NextJS", "Node.js", "MongoDB", "LangChain", "Docker"],
    "projects": ["JewelTrack", "QuickServe"]
  },
  "analysis": {
    "final_score": 71.4,
    "label": "Likely Authentic",
    "reasons": [
      "Live demos detected",
      "Most projects successfully verified",
      "Consistent engineering quality"
    ],
    "repos": [
      {
        "name": "JewelTrack",
        "score": 74.2,
        "tier": "Tier 1 — Flagship",
        "commit_score": 80,
        "alignment_score": 62,
        "complexity_score": 67,
        "stack_score": 58,
        "live_demo": true,
        "demo_score": 8,
        "detected_tech": ["react", "nextjs", "mongodb", "prisma", "tailwind"],
        "stack_verdict": "Strong modern stack",
        "complexity_verdict": "Moderately sophisticated project"
      }
    ],
    "audit": {
      "total_projects": 2,
      "matched_projects": 2,
      "missing_projects": []
    },
    "skill_validation": {
      "verified": ["React", "NextJS", "MongoDB", "LangChain"],
      "weak_evidence": ["Git", "Figma"],
      "unsupported": ["Docker"],
      "validation_score": 71.4
    }
  }
}
```

---

## Performance Optimization

| Optimization | Technique | Saving |
|---|---|---|
| Parallel demo validation | ThreadPoolExecutor (12 workers) | ~120s |
| Deduplication of URL fetches | Pulse results reused in demo validator | ~40s |
| Parallel repo enrichment | 5 outer + 3 inner threads per repo | ~30s |
| Infra + commit caching | In-process dict keyed by owner/repo | ~10s |
| Batch embeddings | Pre-encode all texts before matching loop | ~3s |
| File content caching | Thread-safe github_cache (no re-fetch) | ~15s |
| Playwright rate limiting | Thread-safe lock + 2s delay + cache | Prevents blocking |

**Estimated total runtime:** ~2.5–3.5 min for a 30-repo profile (down from ~4.5 min).

---

## Why This Project Matters

Technical hiring is broken in a specific way: the signal-to-noise ratio on resumes is near zero. Everyone claims React, everyone lists "full-stack developer", everyone has a GitHub link.

This system treats a resume as a hypothesis and GitHub as the evidence. It doesn't ask "does this person claim to know NextJS?" — it asks "is there a `next.config.js`, a `prisma/schema.prisma`, a deployed Vercel URL, and 80+ commits spread across 6 months?"

That's the difference between a keyword scanner and an engineering audit.

---

## Future Roadmap

- [ ] LinkedIn profile cross-referencing
- [ ] Code quality analysis (cyclomatic complexity, test coverage)
- [ ] Plagiarism detection against public boilerplate repos
- [ ] Multi-resume batch processing
- [ ] Recruiter dashboard with candidate comparison
- [ ] Webhook integration for ATS systems
- [ ] Fine-tuned LLM for resume entity extraction
- [ ] Private repo support via OAuth
- [ ] Contribution graph analysis (fork vs original work)
- [ ] PDF report export

---

## License

MIT License — see [LICENSE](LICENSE) for details.
