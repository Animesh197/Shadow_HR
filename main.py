"""
Main pipeline runner

Flow:
1. Extract text + links from PDF
2. Run LLM entity extraction
3. Normalize GitHub username
4. Fetch GitHub repos
5. Run Pulse Check (resume links + repo homepages)
6. Select top repos using:
   - project matching
   - live demo boost
   - skill fallback
"""

import json

from data_pipeline.pdf_extractor import extract_text_from_pdf, extract_links_from_pdf
from data_pipeline.entity_parser import extract_entities_with_llm, clean_json_output
from data_pipeline.github_finder import normalize_github_username
from github_utils import fetch_github_repos
from vitality_audit.repo_selector import select_top_repos
from vitality_audit.pulse_checker import run_pulse_check
from validation.demo_url_validator import evaluate_all_urls


if __name__ == "__main__":
    pdf_path = "resume1.pdf"

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

    if github_username:
        print("\n Fetching GitHub repositories...")
        print("\n Final GitHub Username:", github_username)

        repos = fetch_github_repos(github_username)

        print(f"\n Total Repositories Found: {len(repos)}\n")

        # ---------------- Pulse Check (UPDATED) ----------------
        print("\n Running Pulse Check...\n")

        repo_homepages = []

        for repo in repos:
            homepage = repo.get("homepage")
            if homepage:
                repo_homepages.append(homepage)

        # Combine resume links + repo demo links
        all_links = links + repo_homepages

        print("\n Checking these links (including repo homepages):")
        for link in all_links:
            print(link)

        pulse_results = run_pulse_check(all_links)

        print("\n Pulse Check Results:")
        for r in pulse_results:
            print(r)

        
        print("\n Validating Demo URLs...\n")

        demo_results = evaluate_all_urls(all_links)

        for d in demo_results:
            print(d)

        # ---------------- Repo Selection ----------------
        print("\n Selecting top relevant repositories...\n")

        top_repos = select_top_repos(repos, parsed, pulse_results, demo_results, k=3)

        print("\n Final Output:")
        print(json.dumps(top_repos, indent=2))

    else:
        print("\n No GitHub username found")