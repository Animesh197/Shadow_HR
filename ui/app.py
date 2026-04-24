
import streamlit as st
import tempfile
import sys
import os
from datetime import datetime

# allow import from parent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import run_audit_pipeline

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Resume Auditor", layout="wide")

st.title("🧾 AI Resume Auditor")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

# ---------------- HELPERS ----------------
def safe_get(value, fallback="N/A"):
    return value if value not in [None, "", [], {}] else fallback


def format_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%d %b %Y")
    except:
        return "Unknown"


# ---------------- MAIN ----------------
if uploaded_file:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    with st.spinner("Analyzing resume..."):
        output = run_audit_pipeline(pdf_path)

    candidate = output["candidate"]
    result = output["analysis"]

    # =========================================================
    # HEADER / EXECUTIVE SUMMARY
    # =========================================================

    st.header("Candidate Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Final Score", round(result.get("final_score", 0), 2))
    col2.metric("Confidence", result.get("confidence", {}).get("level", "N/A"))
    col3.metric(
        "Projects Verified",
        f"{result['audit']['matched_projects']} / {result['audit']['total_projects']}"
    )

    st.markdown("---")

    left, right = st.columns([2, 1])

    with left:
        st.write(f"**Candidate Name:** {safe_get(candidate.get('name'))}")
        st.write(f"**GitHub Username:** {safe_get(candidate.get('github'))}")

    with right:
        st.write(f"**Claimed Skills:** {len(candidate.get('skills', []))}")
        st.write(f"**Repositories Evaluated:** {len(result.get('repos', []))}")

    # =========================================================
    # KEY INSIGHTS
    # =========================================================

    st.header("Key Insights")

    reasons = result.get("reasons", [])

    if reasons:
        for reason in reasons:
            st.success(reason)
    else:
        st.info("No insights available")

    # =========================================================
    # PROJECT VERIFICATION
    # =========================================================

    st.header("Resume Project Verification")

    audit = result.get("audit", {})

    total_projects = audit.get("total_projects", 0)
    matched_projects = audit.get("matched_projects", 0)
    missing_projects = audit.get("missing_projects", [])

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Resume Projects", total_projects)

    with col2:
        st.metric("Verified Projects", matched_projects)

    if missing_projects:
        st.warning("Missing Resume Projects")

        for project in missing_projects:
            st.error(project)
    else:
        st.success("All resume projects successfully verified")

    # =========================================================
    # SKILLS
    # =========================================================

    st.header("Claimed Skills")

    skills = candidate.get("skills", [])

    if skills:
        skills_html = ""

        for skill in skills:
            skills_html += f'''
            <span style="
                display:inline-block;
                background:#1f2937;
                color:white;
                padding:6px 12px;
                margin:4px;
                border-radius:20px;
                font-size:13px;
            ">{skill}</span>
            '''

        st.markdown(skills_html, unsafe_allow_html=True)
    else:
        st.info("No skills detected")

    # =========================================================
    # REPOSITORY INTELLIGENCE
    # =========================================================

    st.header("Repository Intelligence")

    repos = result.get("repos", [])

    if not repos:
        st.warning("No repositories analyzed")

    for repo in repos:

        with st.container():

            st.markdown("---")

            repo_name = safe_get(repo.get("name"))
            repo_score = round(repo.get("score", 0), 2)
            repo_tier = safe_get(repo.get("tier"))

            st.subheader(f"{repo_name}")
            st.caption(repo_tier)

            # ---------------- METRICS ----------------
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Repo Score", repo_score)
            col2.metric("Language", safe_get(repo.get("language")))
            col3.metric("Commit Score", repo.get("commit_score", 0))
            col4.metric("Complexity", repo.get("complexity_score", 0))

            col5, col6, col7, col8 = st.columns(4)

            col5.metric("Alignment", round(repo.get("alignment_score", 0), 1))
            col6.metric("Stack Score", repo.get("stack_score", 0))
            col7.metric("Stars", repo.get("stars", 0))
            col8.metric(
                "Live Demo",
                "Yes" if repo.get("live_demo") else "No"
            )

            # ---------------- DETAILS ----------------
            st.write(f"**Description:** {safe_get(repo.get('description'))}")
            st.write(f"**Last Updated:** {format_date(repo.get('pushed_at'))}")

            # ---------------- TECH STACK ----------------
            detected_tech = repo.get("detected_tech", [])

            if detected_tech:
                st.write("**Tech Stack**")

                tech_html = ""

                for tech in detected_tech:
                    tech_html += f'''
                    <span style="
                        display:inline-block;
                        background:#111827;
                        color:#d1d5db;
                        padding:5px 10px;
                        margin:3px;
                        border-radius:16px;
                        font-size:12px;
                    ">{tech}</span>
                    '''

                st.markdown(tech_html, unsafe_allow_html=True)

            # ---------------- ENGINEERING SIGNALS ----------------
            st.write("**Engineering Signals**")

            infra = repo.get("infra", {})

            eng1, eng2, eng3, eng4 = st.columns(4)

            eng1.write(
                f"Dependencies: {'✅' if infra.get('has_dependencies') else '❌'}"
            )
            eng2.write(
                f"Deployment Config: {'✅' if infra.get('has_deployment_config') else '❌'}"
            )
            eng3.write(
                f"Docker: {'✅' if infra.get('has_docker') else '❌'}"
            )
            eng4.write(
                f"CI/CD: {'✅' if infra.get('has_ci') else '❌'}"
            )

            # ---------------- QUALITY INSIGHTS ----------------
            st.write("**Repository Strengths**")

            complexity_reasons = repo.get("complexity_reasons", [])

            if complexity_reasons:
                for reason in complexity_reasons:
                    st.write(f"• {reason}")

            # ---------------- VERDICTS ----------------
            st.write("**Engineering Verdicts**")

            st.info(f"Commit Health: {safe_get(repo.get('verdict'))}")
            st.info(f"Alignment: {safe_get(repo.get('alignment_verdict'))}")
            st.info(f"Complexity: {safe_get(repo.get('complexity_verdict'))}")
            st.info(f"Stack Quality: {safe_get(repo.get('stack_verdict'))}")

    # =========================================================
    # CONFIDENCE EXPLANATION
    # =========================================================

    st.header("Hiring Signals")

    reasons = result.get("reasons", [])

    if reasons:
        for reason in reasons:
            st.write(f"• {reason}")
    else:
        st.info("No hiring insights available")

