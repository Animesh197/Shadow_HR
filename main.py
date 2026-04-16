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

        print("\n Final Parsed Output:")
        print(json.dumps(parsed, indent=2))

    except:
        print("\n⚠️ JSON parsing failed. Raw output shown above.")
        parsed = {}

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

    demo_results = evaluate_all_urls(all_links)

    for d in demo_results:
        print(d)

    # ---------------- Repo Selection ----------------
    print("\n Selecting top relevant repositories...\n")

    final_result = select_top_repos(
        repos,
        parsed,
        pulse_results,
        demo_results,
        k=3
    )

    print("\n Final Output:")
    print(json.dumps(final_result, indent=2))

    # ---------------- CLEAN RETURN ----------------
    return {
        "candidate": {
            "name": parsed.get("name"),
            "github": github_username,
            "skills": parsed.get("skills"),
            "projects": parsed.get("projects")
        },
        "analysis": final_result
    }


# =========================================================
# 🧪 CLI ENTRY POINT (FOR TESTING)
# =========================================================

if __name__ == "__main__":
    pdf_path = "resume.pdf"

    output = run_audit_pipeline(pdf_path)

    print("\n ================= FINAL STRUCTURED OUTPUT =================\n")
    print(json.dumps(output, indent=2))