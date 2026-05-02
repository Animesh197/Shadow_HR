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
linkedin = output.get("linkedin", {})
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

# ── Step 1.5: LinkedIn Verification ───────────────────────────────────────────

linkedin_profile = linkedin.get("profile", {})
linkedin_score_data = linkedin.get("score", {})
linkedin_match = linkedin.get("match_results", {})

if linkedin_profile and linkedin_profile.get("name"):
    st.markdown("### 🔗 LinkedIn Verification")
    
    # LinkedIn Score Overview
    linkedin_score = linkedin_score_data.get("linkedin_score", 0)
    confidence = linkedin_score_data.get("confidence", {})
    verification_status = linkedin_score_data.get("verification_status", "N/A")
    
    col1, col2, col3 = st.columns(3)
    
    # Score with color
    score_color_linkedin = score_color(linkedin_score)
    col1.markdown(
        f'<div style="text-align:center"><p style="color:#94a3b8;font-size:14px;margin:0">LinkedIn Score</p><p style="color:{score_color_linkedin};font-size:32px;font-weight:700;margin:0">{round(linkedin_score, 1)}</p></div>',
        unsafe_allow_html=True
    )
    
    # Confidence
    conf_level = confidence.get("confidence_level", "N/A")
    conf_color = "#22c55e" if conf_level == "high" else "#f59e0b" if conf_level == "medium" else "#ef4444"
    col2.markdown(
        f'<div style="text-align:center"><p style="color:#94a3b8;font-size:14px;margin:0">Confidence</p><p style="color:{conf_color};font-size:24px;font-weight:700;margin:0;text-transform:capitalize">{conf_level}</p></div>',
        unsafe_allow_html=True
    )
    
    # Verification Status
    status_icon = "✅" if "Verified" in verification_status else "⚠️" if "Partially" in verification_status else "❌"
    col3.markdown(
        f'<div style="text-align:center"><p style="color:#94a3b8;font-size:14px;margin:0">Status</p><p style="font-size:18px;font-weight:600;margin:0">{status_icon} {verification_status.replace("✅ ", "").replace("⚠️  ", "").replace("❌ ", "")}</p></div>',
        unsafe_allow_html=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Match Scores
    st.markdown("**Verification Breakdown:**")
    
    match_col1, match_col2, match_col3, match_col4 = st.columns(4)
    
    identity_score = linkedin_match.get("identity", {}).get("score", 0)
    experience_score = linkedin_match.get("experience", {}).get("score", 0)
    education_score = linkedin_match.get("education", {}).get("score", 0)
    timeline_score = linkedin_match.get("timeline", {}).get("score", 0)
    
    match_col1.metric("Identity Match", f"{identity_score}%")
    match_col2.metric("Experience Match", f"{experience_score}%")
    match_col3.metric("Education Match", f"{education_score}%")
    match_col4.metric("Timeline", f"{timeline_score}%")
    
    # Experience Verification
    experience_data = linkedin_match.get("experience", {})
    if experience_data:
        matched_exp = experience_data.get("matched_count", 0)
        total_exp = experience_data.get("total_resume_count", 0)
        mismatches_exp = experience_data.get("mismatches", [])
        
        if matched_exp > 0:
            st.success(f"✅ {matched_exp}/{total_exp} work experience entries verified on LinkedIn")
        
        if mismatches_exp:
            with st.expander(f"⚠️ {len(mismatches_exp)} experience mismatch(es)"):
                for mismatch in mismatches_exp:
                    st.write(f"• {mismatch.get('role', 'N/A')} at {mismatch.get('company', 'N/A')}")
    
    # Education Verification
    education_data = linkedin_match.get("education", {})
    if education_data:
        matched_edu = education_data.get("matched_count", 0)
        total_edu = education_data.get("total_resume_count", 0)
        mismatches_edu = education_data.get("mismatches", [])
        
        if matched_edu > 0:
            st.success(f"✅ {matched_edu}/{total_edu} education entries verified on LinkedIn")
        
        if mismatches_edu:
            with st.expander(f"⚠️ {len(mismatches_edu)} education mismatch(es)"):
                for mismatch in mismatches_edu:
                    st.write(f"• {mismatch.get('institution', 'N/A')}")
    
    # LinkedIn Profile Info (expandable)
    with st.expander("View LinkedIn Profile Details"):
        st.markdown(f"**Name:** {linkedin_profile.get('name', 'N/A')}")
        st.markdown(f"**Headline:** {linkedin_profile.get('headline', 'N/A')}")
        st.markdown(f"**Location:** {linkedin_profile.get('location', 'N/A')}")
        
        linkedin_exp = linkedin_profile.get("experience", [])
        if linkedin_exp:
            st.markdown(f"**Experience ({len(linkedin_exp)} entries):**")
            for exp in linkedin_exp[:3]:
                st.write(f"• {exp.get('role', 'N/A')} at {exp.get('company', 'N/A')}")
        
        linkedin_edu = linkedin_profile.get("education", [])
        if linkedin_edu:
            st.markdown(f"**Education ({len(linkedin_edu)} entries):**")
            for edu in linkedin_edu:
                st.write(f"• {edu.get('institution', 'N/A')}")
    
    st.divider()
elif linkedin.get("fetch_status") == "blocked":
    st.warning("⚠️ LinkedIn profile is private or blocked. Verification skipped.")
    st.divider()
elif linkedin.get("fetch_status") == "error":
    st.warning("⚠️ Could not fetch LinkedIn profile. Verification skipped.")
    st.divider()
# If no LinkedIn URL, don't show anything (no penalty)

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
