import streamlit as st
import tempfile
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import run_audit_pipeline

st.set_page_config(page_title="AI Resume Auditor", layout="wide")

# ── Helpers ──────────────────────────────────────────────────────────────────

def safe(value, fallback="N/A"):
    return value if value not in [None, "", [], {}] else fallback

def fmt_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%d %b %Y")
    except:
        return "Unknown"

def score_color(score):
    if score >= 70: return "#22c55e"
    if score >= 50: return "#f59e0b"
    return "#ef4444"

def tier_badge(tier):
    colors = {
        "Tier 1": "#6366f1",
        "Tier 2": "#3b82f6",
        "Tier 3": "#94a3b8",
        "Tier 4": "#64748b",
    }
    key = tier.split("—")[0].strip() if tier else "Tier 4"
    color = colors.get(key, "#64748b")
    label = tier if tier else "Untiered"
    return f'<span style="background:{color};color:white;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600">{label}</span>'

def chip(text, bg="#1e293b", color="#e2e8f0"):
    return f'<span style="display:inline-block;background:{bg};color:{color};padding:4px 10px;margin:3px;border-radius:14px;font-size:12px">{text}</span>'

def generate_summary(repo):
    parts = []
    score = repo.get("score", 0)
    if repo.get("live_demo"):
        parts.append("deployed")
    stack = repo.get("stack_score", 0)
    if stack >= 50:
        parts.append("sophisticated tech stack")
    elif stack >= 25:
        parts.append("modern tech stack")
    complexity = repo.get("complexity_score", 0)
    if complexity >= 65:
        parts.append("high engineering depth")
    elif complexity >= 40:
        parts.append("moderate engineering depth")
    commit = repo.get("commit_score", 0)
    if commit >= 75:
        parts.append("healthy development activity")
    elif commit <= 20:
        parts.append("limited commit history")
    if not parts:
        return "Basic project with limited signals."
    return "Project with " + ", ".join(parts) + "."

# ── Header ───────────────────────────────────────────────────────────────────

st.markdown("## 🧾 AI Resume Auditor")
st.caption("Verify technical claims against live GitHub evidence.")
st.divider()

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if not uploaded_file:
    st.stop()

with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
    tmp.write(uploaded_file.read())
    pdf_path = tmp.name

with st.spinner("Analyzing resume..."):
    output = run_audit_pipeline(pdf_path)

candidate = output["candidate"]
result = output["analysis"]
audit = result.get("audit", {})
repos = result.get("repos", [])
reasons = result.get("reasons", [])
skill_val = result.get("skill_validation", {})

# ── Step 1: Candidate Overview ────────────────────────────────────────────────

st.markdown("### Candidate Overview")

c1, c2, c3 = st.columns(3)
final_score = round(result.get("final_score", 0), 1)
c1.metric("Final Score", f"{final_score} / 100")
c2.metric("Confidence", result.get("confidence", {}).get("level", "N/A"))
c3.metric("Projects Verified", f"{audit.get('matched_projects', 0)} / {audit.get('total_projects', 0)}")

st.markdown(f"**Name:** {safe(candidate.get('name'))}  &nbsp;&nbsp; **GitHub:** `{safe(candidate.get('github'))}`")
st.divider()

# ── Step 2: Key Findings (merged, deduplicated) ───────────────────────────────

st.markdown("### Key Findings")

seen = set()
unique_reasons = []
for r in reasons:
    if r not in seen:
        seen.add(r)
        unique_reasons.append(r)

for r in unique_reasons[:5]:
    lower = r.lower()
    if any(w in lower for w in ["verified", "detected", "matched", "authentic", "consistent"]):
        st.success(f"✅ {r}")
    elif any(w in lower for w in ["missing", "weak", "low", "suspicious", "not found"]):
        st.warning(f"⚠️ {r}")
    else:
        st.info(f"📌 {r}")

missing = audit.get("missing_projects", [])
if missing:
    for m in missing:
        st.error(f"❌ Project not found on GitHub: **{m}**")
else:
    st.success("✅ All resume projects verified on GitHub")

st.divider()

# ── Step 3: Skills (compact, expandable) ─────────────────────────────────────

st.markdown("### Claimed Skills")

skills = candidate.get("skills", [])
verified = set(skill_val.get("verified", []))
weak = set(skill_val.get("weak_evidence", []))

if skills:
    visible = skills[:12]
    rest = skills[12:]

    html = ""
    for s in visible:
        if s in verified:
            html += chip(s, "#166534", "#dcfce7")
        elif s in weak:
            html += chip(s, "#78350f", "#fef3c7")
        else:
            html += chip(s, "#1e293b", "#94a3b8")
    st.markdown(html, unsafe_allow_html=True)

    if rest:
        with st.expander(f"View {len(rest)} more skills"):
            html2 = "".join(chip(s, "#1e293b", "#94a3b8") for s in rest)
            st.markdown(html2, unsafe_allow_html=True)

    st.caption("🟢 Verified in code &nbsp; 🟡 Weak evidence &nbsp; ⚫ Unverified")
else:
    st.info("No skills detected")

st.divider()

# ── Steps 4–11: Repo Cards ────────────────────────────────────────────────────

st.markdown("### Projects")

if not repos:
    st.warning("No repositories analyzed.")

for repo in repos:
    name = safe(repo.get("name"))
    score = round(repo.get("score", 0), 1)
    tier = safe(repo.get("tier"), "")
    live_demo = repo.get("live_demo", False)
    detected_tech = repo.get("detected_tech", [])
    stack_verdict = safe(repo.get("stack_verdict"), "")
    complexity_verdict = safe(repo.get("complexity_verdict"), "")
    commit_verdict = safe(repo.get("verdict"), "")
    alignment_verdict = safe(repo.get("alignment_verdict"), "")
    infra = repo.get("infra", {})
    pushed = fmt_date(repo.get("pushed_at"))
    summary = generate_summary(repo)

    sc = score_color(score)

    st.markdown(
        f"""
        <div style="border:1px solid #334155;border-radius:12px;padding:16px 20px;margin-bottom:16px;background:#0f172a">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
                <span style="font-size:18px;font-weight:700;color:#f1f5f9">{name}</span>
                <span style="display:flex;gap:10px;align-items:center">
                    {tier_badge(tier)}
                    <span style="background:{sc};color:white;padding:4px 12px;border-radius:12px;font-size:13px;font-weight:700">Score: {score}</span>
                    {"<span style='background:#0f766e;color:white;padding:4px 10px;border-radius:12px;font-size:12px'>🚀 Live Demo</span>" if live_demo else "<span style='background:#374151;color:#9ca3af;padding:4px 10px;border-radius:12px;font-size:12px'>No Demo</span>"}
                </span>
            </div>
            <p style="color:#94a3b8;margin:10px 0 6px;font-size:13px">{summary}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Visible metrics (Step 5 — simplified)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Project Difficulty", repo.get("complexity_score", 0))
    m2.metric("Tech Sophistication", repo.get("stack_score", 0))
    m3.metric("Resume Match", round(repo.get("alignment_score", 0), 1))
    m4.metric("Live Demo", "Yes ✅" if live_demo else "No ❌")

    # Tech stack chips (Step 8 — max 5 visible)
    if detected_tech:
        visible_tech = detected_tech[:5]
        extra = len(detected_tech) - 5
        tech_html = "".join(chip(t, "#1e3a5f", "#93c5fd") for t in visible_tech)
        if extra > 0:
            tech_html += chip(f"+{extra} more", "#1e293b", "#64748b")
        st.markdown(tech_html, unsafe_allow_html=True)

    # Expandable technical details (Step 11)
    with st.expander("View Technical Details"):
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Development Activity", repo.get("commit_score", 0))
        d2.metric("Stars", repo.get("stars", 0))
        d3.metric("Language", safe(repo.get("language")))
        d4.metric("Last Updated", pushed)

        dep_col, infra_col = st.columns(2)

        with dep_col:
            st.markdown("**Deployment Setup**")
            st.write(f"Dependencies: {'✅' if infra.get('has_dependencies') else '❌'}")
            st.write(f"Deployment Config: {'✅' if infra.get('has_deployment_config') else '❌'}")
            st.write(f"Docker: {'✅' if infra.get('has_docker') else '❌'}")
            st.write(f"CI/CD: {'✅' if infra.get('has_ci') else '❌'}")
            dep_conf = infra.get("deployment_confidence", 0)
            if dep_conf:
                st.caption(f"Deployment confidence: {dep_conf}/10")

        with infra_col:
            st.markdown("**Analysis Verdicts**")
            if commit_verdict and commit_verdict != "N/A":
                st.caption(f"Development Activity: {commit_verdict}")
            if alignment_verdict and alignment_verdict != "N/A":
                st.caption(f"Resume Match: {alignment_verdict}")
            if complexity_verdict and complexity_verdict != "N/A":
                st.caption(f"Project Difficulty: {complexity_verdict}")
            if stack_verdict and stack_verdict != "N/A":
                st.caption(f"Tech Sophistication: {stack_verdict}")

        dep_signals = infra.get("deployment_signals", [])
        if dep_signals:
            st.markdown("**Deployment Signals**")
            for sig in dep_signals:
                st.caption(f"• {sig}")

        if len(detected_tech) > 5:
            st.markdown("**Full Tech Stack**")
            full_tech = "".join(chip(t, "#1e3a5f", "#93c5fd") for t in detected_tech)
            st.markdown(full_tech, unsafe_allow_html=True)
