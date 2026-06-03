# 🚀 AI Resume Auditor — Deployment Guide

**Version:** 1.0.0  
**Date:** June 3, 2026  
**Status:** Production Ready

---

## Quick Start (5 Minutes)

```bash
# 1. Clone and navigate
git clone <repository-url>
cd resume_auditor

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browser
playwright install chromium

# 5. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 6. Launch
streamlit run ui/app.py
```

Open `http://localhost:8501` and upload a resume.

---

## Prerequisites

### Required
- Python 3.8 or higher
- pip package manager
- 2GB available RAM
- Internet connection (for API calls)

### API Keys (Required)
1. **Groq API Key** (Free tier available)
   - Sign up: https://console.groq.com
   - Create API key
   - Free quota: generous for testing

2. **GitHub Personal Access Token**
   - Go to: GitHub → Settings → Developer Settings → Personal Access Tokens (Classic)
   - Generate new token
   - Required scope: `public_repo` (read public repositories)
   - No payment required

---

## Detailed Installation

### Step 1: System Dependencies

**macOS:**
```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3
brew install python@3.10

# Verify
python3 --version
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Verify
python3 --version
```

**Windows:**
- Download Python from https://www.python.org/downloads/
- Check "Add Python to PATH" during installation
- Verify in Command Prompt: `python --version`

---

### Step 2: Clone Repository

```bash
git clone https://github.com/your-username/resume-auditor.git
cd resume-auditor
```

---

### Step 3: Virtual Environment

**Create and activate:**

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**Verify activation:**
- Your terminal should show `(venv)` prefix
- Run: `which python` (should point to venv)

---

### Step 4: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected packages:**
- streamlit (UI)
- playwright (LinkedIn fetch)
- requests (GitHub API)
- aiohttp (async URL checks)
- PyMuPDF (PDF parsing)
- sentence-transformers (semantic matching)
- scikit-learn (similarity)
- pydantic (validation)
- beautifulsoup4 (HTML parsing)
- python-dotenv (environment)
- groq (LLM API)

**Installation time:** ~2-3 minutes

---

### Step 5: Install Playwright Browser

```bash
playwright install chromium
```

**What this does:**
- Downloads Chromium browser (~100 MB)
- Required for LinkedIn profile fetching
- Headless mode (no visible window)

**Installation time:** ~1-2 minutes

---

### Step 6: Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit with your favorite editor
nano .env
# OR: code .env  # VS Code
# OR: vim .env
```

**Required configuration:**

```bash
# .env file content

# Groq API (LLM for entity extraction + LinkedIn parsing)
GROQ_API_KEY=your_groq_api_key_here

# GitHub API (fetch repositories)
GITHUB_TOKEN=your_github_personal_access_token_here
```

**How to get API keys:**

### Groq API Key
1. Go to https://console.groq.com
2. Sign up (free)
3. Navigate to "API Keys"
4. Create new key
5. Copy and paste into `.env`

### GitHub Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "Resume Auditor"
4. Scopes: Check `public_repo`
5. Click "Generate token"
6. Copy and paste into `.env`

**⚠️ Security Note:**
- Never commit `.env` to git
- `.gitignore` already configured to exclude it
- Keep your API keys private

---

## Launch Methods

### Method 1: Streamlit UI (Recommended)

```bash
streamlit run ui/app.py
```

**What happens:**
- Server starts on http://localhost:8501
- Browser opens automatically
- Upload resume via drag-and-drop
- See results in real-time dashboard

**Features:**
- Candidate overview with score + confidence
- LinkedIn verification section
- GitHub repo breakdown with tier badges
- Skill validation chips (color-coded)
- Expandable technical details per repo

---

### Method 2: CLI Mode (For Testing)

```bash
python main.py
```

**What to modify:**
- Open `main.py` in editor
- Change line: `pdf_path = "resumes/resume6.pdf"`
- Point to your test resume file
- Run: `python main.py`

**Output:**
- JSON structure printed to terminal
- Includes full analysis breakdown
- Useful for debugging and automation

---

### Method 3: Import as Library

```python
from main import run_audit_pipeline

# Run audit
result = run_audit_pipeline("path/to/resume.pdf")

# Access results
candidate = result["candidate"]
analysis = result["analysis"]
linkedin = result["linkedin"]

print(f"Score: {analysis['final_score']}")
print(f"Label: {analysis['label']}")
```

---

## Verification Tests

### Test 1: Import Check
```bash
python -c "
from linkedin.linkedin_profile_extractor import extract_linkedin_profile
from scoring.verification_index import compute_final_score_v2
print('✅ All modules working')
"
```

### Test 2: API Connection
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
assert os.getenv('GROQ_API_KEY'), 'Groq API key missing'
assert os.getenv('GITHUB_TOKEN'), 'GitHub token missing'
print('✅ API keys configured')
"
```

### Test 3: Sample Resume (Optional)
```bash
# Place a test resume in resumes/ folder
cp /path/to/your/resume.pdf resumes/test.pdf

# Run audit
python main.py
```

---

## Configuration Options

### LinkedIn Session Management

**Save browser session (avoid repeated logins):**

```bash
python linkedin/save_session.py
```

**What this does:**
- Opens Chromium browser
- You manually log in to LinkedIn
- Session cookies saved to `linkedin_session.json`
- Future runs reuse session (faster + no re-login)

**When to use:**
- First-time setup
- After LinkedIn password change
- If fetch fails with "login required" error

**⚠️ Security:**
- `linkedin_session.json` contains your session cookies
- Keep it private (already in `.gitignore`)
- Session expires after ~2 weeks (need to re-save)

---

### Streamlit Configuration

**Create `.streamlit/config.toml` (optional):**

```toml
[server]
port = 8501
headless = true

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

---

### Performance Tuning

**Adjust worker counts in code:**

```python
# validation/demo_url_validator.py
ThreadPoolExecutor(max_workers=12)  # Demo validation
# Reduce to 6-8 for slower machines

# vitality_audit/repo_selector.py
ThreadPoolExecutor(max_workers=5)   # Repo enrichment
# Reduce to 3 for slower machines
```

---

## Production Deployment

### Option 1: Streamlit Cloud (Easiest)

1. Push code to GitHub (public or private repo)
2. Go to https://streamlit.io/cloud
3. Sign in with GitHub
4. Click "New app"
5. Select your repo, branch, and `ui/app.py`
6. Add secrets:
   - `GROQ_API_KEY`
   - `GITHUB_TOKEN`
7. Deploy

**Pros:**
- Free hosting
- Automatic HTTPS
- No server management
- Auto-deploys on git push

**Cons:**
- Limited to 1GB RAM (might timeout on large repos)
- Public URL (or paid for private)

---

### Option 2: Docker Container

**Create `Dockerfile`:**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy app
COPY . .

# Expose port
EXPOSE 8501

# Run
CMD ["streamlit", "run", "ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build and run:**

```bash
docker build -t resume-auditor .
docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  -e GITHUB_TOKEN=your_token \
  resume-auditor
```

---

### Option 3: VPS/Cloud Server

**Deploy on AWS EC2, DigitalOcean, etc.:**

```bash
# 1. SSH into server
ssh user@your-server-ip

# 2. Install dependencies
sudo apt update
sudo apt install python3 python3-pip git

# 3. Clone repo
git clone https://github.com/your-username/resume-auditor.git
cd resume-auditor

# 4. Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install packages
pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium

# 6. Configure environment
nano .env  # Add API keys

# 7. Run with nohup (persistent)
nohup streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0 &

# 8. Access via
http://your-server-ip:8501
```

**Recommended server specs:**
- 2 CPU cores
- 4GB RAM
- 20GB storage
- Ubuntu 22.04 LTS

---

## Monitoring & Maintenance

### Logs

**Streamlit logs:**
```bash
tail -f ~/.streamlit/streamlit.log
```

**Application logs:**
- Printed to terminal by default
- Redirect to file: `python main.py > audit.log 2>&1`

---

### Troubleshooting

**Issue: "Module not found"**
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Issue: "LinkedIn fetch failed"**
```bash
# Save session manually
python linkedin/save_session.py

# Verify linkedin_session.json exists
ls -la linkedin_session.json
```

**Issue: "Groq API error"**
```bash
# Check API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GROQ_API_KEY'))"

# Verify quota: https://console.groq.com
```

**Issue: "GitHub API rate limit"**
```bash
# Check token
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GITHUB_TOKEN'))"

# Verify token: https://github.com/settings/tokens
```

**Issue: "Playwright browser not found"**
```bash
playwright install chromium
playwright install-deps chromium
```

---

## Security Best Practices

### API Key Management
- ✅ Use `.env` file (never hardcode)
- ✅ Add `.env` to `.gitignore`
- ✅ Rotate keys periodically
- ✅ Use separate keys for dev/prod

### LinkedIn Session
- ✅ Keep `linkedin_session.json` private
- ✅ Don't commit to git (in `.gitignore`)
- ✅ Re-save after password changes
- ✅ Delete if sharing server access

### Server Security (Production)
- ✅ Use HTTPS (SSL/TLS)
- ✅ Enable firewall (allow only 8501)
- ✅ Keep system updated
- ✅ Use strong passwords
- ✅ Implement rate limiting
- ✅ Monitor logs for suspicious activity

---

## Performance Benchmarks

**Test Environment:**
- MacBook Pro M1
- 16GB RAM
- 100 Mbps internet

**Benchmark Results:**

| Operation | Time |
|---|---|
| PDF extraction | ~1 sec |
| LLM entity extraction | ~3 sec |
| GitHub repo fetch (30 repos) | ~5 sec |
| LinkedIn fetch (first time) | ~10 sec |
| LinkedIn fetch (cached) | <1 sec |
| URL pulse check (20 URLs) | ~3 sec |
| Demo validation (20 URLs) | ~8 sec |
| Repo enrichment (8 repos) | ~25 sec |
| Semantic matching | ~2 sec |
| Total (full pipeline) | **~3-4 min** |

**Bottlenecks:**
1. Repo enrichment (25 sec) — parallelized already
2. Demo validation (8 sec) — parallelized already
3. LinkedIn fetch (10 sec first time) — caching helps

---

## Scaling Recommendations

### For 10-50 resumes/day
- ✅ Current setup sufficient
- ✅ Use Streamlit Cloud or small VPS
- ✅ No additional optimization needed

### For 100-500 resumes/day
- 📌 Use Redis for cross-instance caching
- 📌 Consider background job queue (Celery)
- 📌 Monitor API rate limits
- 📌 Scale to 2-4 server instances

### For 1000+ resumes/day
- 📌 Implement distributed caching (Redis cluster)
- 📌 Use message queue (RabbitMQ/SQS)
- 📌 Load balancer for Streamlit instances
- 📌 Consider serverless for burst scaling
- 📌 Implement batch processing
- 📌 Cache GitHub/LinkedIn data aggressively

---

## Support & Resources

### Documentation
- **System Overview:** [COMPLETE_SYSTEM_STATUS.md](COMPLETE_SYSTEM_STATUS.md)
- **Architecture Details:** [project_report.md](project_report.md)
- **LinkedIn Design:** [linkedin/ARCHITECTURE.md](linkedin/ARCHITECTURE.md)
- **Optimization Details:** [OPTIMIZATION_COMPLETE.md](OPTIMIZATION_COMPLETE.md)

### External Resources
- Groq API Docs: https://console.groq.com/docs
- GitHub API Docs: https://docs.github.com/en/rest
- Streamlit Docs: https://docs.streamlit.io
- Playwright Docs: https://playwright.dev/python

---

## Upgrade Path

**To update to latest version:**

```bash
# 1. Pull latest code
git pull origin main

# 2. Activate venv
source venv/bin/activate

# 3. Update dependencies
pip install -r requirements.txt --upgrade

# 4. Restart application
# Ctrl+C to stop, then:
streamlit run ui/app.py
```

---

## License

[Your license here]

---

## Support

For issues, questions, or contributions:
- GitHub Issues: [your-repo]/issues
- Email: your-email@example.com

---

**Status:** ✅ Production Ready  
**Last Updated:** June 3, 2026  
**Maintained By:** [Your name/team]
