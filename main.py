"""
Main pipeline runner

Flow:
1. Extract text + links from PDF
2. Run LLM entity extraction
3. Normalize GitHub username
4. Fetch GitHub repos
5. Run Pulse Check (resume links + repo homepages)
6. Validate demo URLs
7. Select top repos using:
   - project matching (semantic)
   - live demo boost
   - skill fallback
8. Return structured output (for UI)
"""

import json

from data_pipeline.pdf_extractor import extract_text_from_pdf, extract_links_from_pdf
from data_pipeline.entity_parser import extract_entities_with_llm, clean_json_output
from data_pipeline.github_finder import normalize_github_username
from github_utils import fetch_github_repos
from vitality_audit.repo_selector import select_top_repos
from vitality_audit.pulse_checker import run_pulse_check
from validation.demo_url_validator import evaluate_all_urls
from linkedin.candidate_classifier import classify_candidate
from linkedin.linkedin_fetcher import fetch_linkedin_html


def extract_linkedin_url(links, llm_linkedin):
    """
    Extract LinkedIn URL — resume embedded links take priority over LLM output.
    """
    for link in links:
        if "linkedin.com/in/" in link:
            return link.split("?")[0]  # strip query params

    if llm_linkedin and "linkedin.com" in llm_linkedin:
        return llm_linkedin.split("?")[0]

    return ""


# =========================================================
# 🔁 CORE PIPELINE FUNCTION (USED BY UI)
# =========================================================

def run_audit_pipeline(pdf_path):
    print(" Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)

    print(" Extracting links from PDF...")
    links = extract_links_from_pdf(pdf_path)

    print("\n Links Found:")
    for l in links:
        print(l)

    # ---------------- LLM Extraction ----------------
    print("\n Sending to LLM...")
    result = extract_entities_with_llm(text)

    print("\n Extracted JSON:\n")
    print(result)

    cleaned = clean_json_output(result)

    try:
        parsed = json.loads(cleaned)

        github_username = normalize_github_username(parsed.get("github"), links)
        parsed["github"] = github_username

        linkedin_url = extract_linkedin_url(links, parsed.get("linkedin_url", ""))
        parsed["linkedin_url"] = linkedin_url

        # ---------------- Candidate Classification ----------------
        classification = classify_candidate(
            parsed.get("experience", []),
            parsed.get("education", [])
        )
        parsed["candidate_classification"] = classification

        print("\n Candidate Classification:")
        print(json.dumps(classification, indent=2))

        print("\n Final Parsed Output:")
        print(json.dumps(parsed, indent=2))

    except:
        print("\n⚠️ JSON parsing failed. Raw output shown above.")
        parsed = {}

    # ---------------- LinkedIn Fetch ----------------
    linkedin_url = parsed.get("linkedin_url", "")
    linkedin_html = ""
    linkedin_fetch_status = "skipped"

    if linkedin_url:
        print(f"\n Fetching LinkedIn profile: {linkedin_url}")
        linkedin_html, linkedin_fetch_status = fetch_linkedin_html(linkedin_url)
        print(f" LinkedIn fetch status: {linkedin_fetch_status}")

    # Store HTML internally for downstream phases — never returned in output
    parsed["_linkedin_html"] = linkedin_html

    # ---------------- GitHub Fetch ----------------
    github_username = parsed.get("github")

    if not github_username:
        print("\n No GitHub username found")
        return {
            "candidate": parsed,
            "analysis": None
        }

    print("\n Fetching GitHub repositories...")
    print("\n Final GitHub Username:", github_username)

    repos = fetch_github_repos(github_username)

    print(f"\n Total Repositories Found: {len(repos)}\n")

    # ---------------- Pulse Check ----------------
    print("\n Running Pulse Check...\n")

    repo_homepages = []

    for repo in repos:
        homepage = repo.get("homepage")
        if homepage:
            repo_homepages.append(homepage)

    all_links = links + repo_homepages

    print("\n Checking these links (including repo homepages):")
    for link in all_links:
        print(link)

    pulse_results = run_pulse_check(all_links)

    print("\n Pulse Check Results:")
    for r in pulse_results:
        print(r)

    # ---------------- Demo Validation ----------------
    print("\n Validating Demo URLs...\n")

    demo_results = evaluate_all_urls(all_links, pulse_results)

    for d in demo_results:
        print(d)

    # ---------------- Repo Selection ----------------
    print("\n Selecting top relevant repositories...\n")

    final_result = select_top_repos(
        repos,
        parsed,
        pulse_results,
        demo_results,
        links,   # NEW
        k=3
    )

    print("\n Final Output:")
    print(json.dumps(final_result, indent=2))

    # ---------------- CLEAN RETURN ----------------
    return {
        "candidate": {
            "name": parsed.get("name"),
            "github": github_username,
            "linkedin_url": parsed.get("linkedin_url", ""),
            "skills": parsed.get("skills"),
            "projects": parsed.get("projects"),
            "experience": parsed.get("experience", []),
            "education": parsed.get("education", []),
            "candidate_classification": parsed.get("candidate_classification", {})
        },
        "analysis": final_result,
        "linkedin": {
            "fetch_status": linkedin_fetch_status
        }
    }


# =========================================================
# 🧪 CLI ENTRY POINT (FOR TESTING)
# =========================================================

if __name__ == "__main__":
    pdf_path = "resumes/resume5.pdf"

    output = run_audit_pipeline(pdf_path)

    print("\n ================= FINAL STRUCTURED OUTPUT =================\n")

    # Print summary only — avoids BlockingIOError from large HTML/JSON dumps
    candidate = output.get("candidate", {})
    analysis = output.get("analysis", {})
    linkedin = output.get("linkedin", {})

    print(f"Name:            {candidate.get('name')}")
    print(f"GitHub:          {candidate.get('github')}")
    print(f"LinkedIn URL:    {candidate.get('linkedin_url')}")
    print(f"LinkedIn Fetch:  {linkedin.get('fetch_status')}")
    print(f"Candidate Type:  {candidate.get('candidate_classification', {}).get('candidate_type')}")
    print(f"Final Score:     {analysis.get('final_score')} — {analysis.get('label')}")
    print(f"Confidence:      {analysis.get('confidence', {}).get('level')}")
    print(f"Projects:        {analysis.get('audit', {}).get('matched_projects')}/{analysis.get('audit', {}).get('total_projects')} verified")
    print(f"Skills verified: {len(analysis.get('skill_validation', {}).get('verified', []))}")
    print(f"Reasons:         {analysis.get('reasons', [])}")
    print()
    print("Repos:")
    for r in analysis.get("repos", []):
        print(f"  {r.get('name'):30s} score={r.get('score')}  tier={r.get('tier')}")