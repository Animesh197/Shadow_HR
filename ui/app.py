import streamlit as st
import tempfile
import sys
import os

# allow import from parent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import run_audit_pipeline

st.set_page_config(page_title="AI Resume Auditor", layout="wide")

st.title("🧾 AI Resume Auditor")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if uploaded_file:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    with st.spinner("Analyzing resume..."):
        output = run_audit_pipeline(pdf_path)

    candidate = output["candidate"]
    result = output["analysis"]

    # ---------------- HEADER ----------------
    st.header("Candidate Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Final Score", result["final_score"])
    col2.metric("Confidence", result["confidence"]["level"])
    col3.metric("Projects Verified", f"{result['audit']['matched_projects']} / {result['audit']['total_projects']}")

    st.write(f"**Name:** {candidate['name']}")
    st.write(f"**GitHub:** {candidate['github']}")

    # ---------------- REASONS ----------------
    st.subheader("Key Insights")

    for r in result["reasons"]:
        st.write("•", r)

    # ---------------- MISSING PROJECTS ----------------
    st.subheader("Missing Projects")

    missing = result["audit"]["missing_projects"]

    if missing:
        for m in missing:
            st.error(m)
    else:
        st.success("All projects verified")

    # ---------------- REPOS ----------------
    st.subheader("Top Repositories")

    for repo in result["repos"]:
        with st.container():

            st.markdown(f"### {repo['name']}")

            col1, col2, col3 = st.columns(3)

            col1.write(f"Score: {repo.get('score')}")
            col2.write(f"Language: {repo.get('language')}")
            col3.write(f"Stars: {repo.get('stars')}")

            st.write("Commit:", repo.get("commit_verdict"))
            st.write("Alignment:", repo.get("alignment_verdict"))

            st.write(
                "Live Demo:",
                "✅ Available" if repo.get("live_demo") else "❌ Not Found"
            )

            st.divider()

    # ---------------- CONFIDENCE ----------------
    st.subheader("Confidence Breakdown")

    for c in result["confidence"]["reasons"]:
        st.write("•", c)