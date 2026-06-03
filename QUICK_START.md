# ⚡ Quick Start — AI Resume Auditor

**Get running in 5 minutes.**

---

## Prerequisites

- Python 3.8+
- Git
- 2GB RAM

---

## Installation

```bash
# 1. Clone
git clone <repository-url>
cd resume_auditor

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR: venv\Scripts\activate  # Windows

# 3. Install
pip install -r requirements.txt
playwright install chromium

# 4. Configure
cp .env.example .env
nano .env  # Add your API keys
```

---

## Required API Keys

### Groq API Key (Free)
1. Go to https://console.groq.com
2. Sign up
3. Create API key
4. Paste into `.env`: `GROQ_API_KEY=your_key`

### GitHub Token (Free)
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Check scope: `public_repo`
4. Paste into `.env`: `GITHUB_TOKEN=your_token`

---

## Launch

```bash
streamlit run ui/app.py
```

Open http://localhost:8501 and upload a resume.

---

## What You'll See

### 1. Candidate Overview
- Final score (0-100)
- Confidence level (High/Medium/Low)
- Verification status
- Projects verified count

### 2. LinkedIn Verification (if URL provided)
- Identity match score
- Experience match score
- Education match score
- Timeline consistency
- Overall LinkedIn score

### 3. GitHub Repos
Each repo shows:
- Tier badge (Flagship/Supporting/Practice/Weak)
- Score breakdown
- Live demo status
- Detected tech stack
- Commit quality
- Engineering signals

### 4. Skills
Color-coded chips:
- 🟢 Green = Verified in code
- 🟡 Yellow = Weak evidence
- ⚪ Grey = Unverified

---

## CLI Mode (Optional)

```bash
# Edit pdf_path in main.py
nano main.py

# Run
python main.py
```

---

## Test Files

Place test resumes in `resumes/` folder:
```bash
resumes/
  ├── resume1.pdf
  ├── resume2.pdf
  └── test_resume.pdf
```

---

## LinkedIn Session (Optional but Recommended)

For faster LinkedIn fetching:

```bash
python linkedin/save_session.py
```

This opens a browser where you log in manually. Session is saved and reused.

---

## Troubleshooting

**Module not found?**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**LinkedIn fetch failed?**
```bash
python linkedin/save_session.py
```

**API errors?**
- Check `.env` has correct keys
- Verify at https://console.groq.com
- Verify at https://github.com/settings/tokens

**Browser not found?**
```bash
playwright install chromium
```

---

## Example Output

```
Name:            Jane Doe
GitHub:          janedoe
LinkedIn:        https://linkedin.com/in/janedoe

LinkedIn Verification:
  Identity Match:       95%
  Experience Match:     88%
  Education Match:      90%
  Overall Score:        85/100

Final Score:     76.3 — Likely Authentic
Confidence:      High
Projects:        2/2 verified
Skills verified: 4

Repos:
  JewelTrack      score=82  tier=Tier 1 — Flagship
  QuickServe      score=68  tier=Tier 2 — Supporting
```

---

## Documentation

- **Full System:** [COMPLETE_SYSTEM_STATUS.md](COMPLETE_SYSTEM_STATUS.md)
- **Deployment:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Summary:** [FINAL_SUMMARY.md](FINAL_SUMMARY.md)
- **Architecture:** [project_report.md](project_report.md)

---

## Next Steps

1. ✅ Test with 3-5 real resumes
2. ✅ Review score distribution
3. ✅ Adjust thresholds if needed
4. ✅ Deploy to production

**System is production ready!**

---

**Questions?** Read DEPLOYMENT_GUIDE.md or COMPLETE_SYSTEM_STATUS.md
