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
from linkedin.linkedin_parser import parse_linkedin_profile
from linkedin.linkedin_matcher import match_resume_linkedin
from linkedin.linkedin_signals import generate_signals
from linkedin.linkedin_scorer import calculate_linkedin_score


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
    linkedin_profile = {}
    linkedin_match_results = {}

    if linkedin_url:
        print(f"\n Fetching LinkedIn profile: {linkedin_url}")
        linkedin_html, linkedin_fetch_status = fetch_linkedin_html(linkedin_url)
        print(f" LinkedIn fetch status: {linkedin_fetch_status}")
        
        # ---------------- LinkedIn Parsing ----------------
        if linkedin_fetch_status == "success" and linkedin_html:
            print("\n Parsing LinkedIn profile...")
            linkedin_profile = parse_linkedin_profile(linkedin_html)
            print(f" LinkedIn profile parsed:")
            print(f"   Name: {linkedin_profile.get('name')}")
            print(f"   Headline: {linkedin_profile.get('headline')[:80] if linkedin_profile.get('headline') else ''}")
            print(f"   Location: {linkedin_profile.get('location')}")
            print(f"   Experience entries: {len(linkedin_profile.get('experience', []))}")
            print(f"   Education entries: {len(linkedin_profile.get('education', []))}")
            
            # ---------------- LinkedIn Matching ----------------
            print("\n Matching Resume ↔ LinkedIn...")
            linkedin_match_results = match_resume_linkedin(parsed, linkedin_profile)
            print(f" Match Results:")
            print(f"   Identity Match: {linkedin_match_results['identity']['score']}%")
            print(f"   Experience Match: {linkedin_match_results['experience']['score']}%")
            print(f"   Education Match: {linkedin_match_results['education']['score']}%")
            print(f"   Timeline Consistency: {linkedin_match_results['timeline']['score']}%")
            print(f"   Overall Score: {linkedin_match_results['overall_score']}%")
            print(f"   Overall Match: {'✅ Yes' if linkedin_match_results['overall_match'] else '❌ No'}")
            
            # ---------------- LinkedIn Signals ----------------
            print("\n Generating LinkedIn signals...")
            linkedin_signals = generate_signals(linkedin_match_results, linkedin_profile)
            print(f" Signals Generated:")
            print(f"   Identity Match: {linkedin_signals['identity_match']}")
            print(f"   Experience Match: {linkedin_signals['experience_match']}")
            print(f"   Education Match: {linkedin_signals['education_match']}")
            print(f"   Timeline Consistency: {linkedin_signals['timeline_consistency']}")
            print(f"   Profile Completeness: {linkedin_signals['profile_completeness']}")
            
            # ---------------- LinkedIn Scoring ----------------
            print("\n Calculating LinkedIn verification score...")
            candidate_type = parsed.get("candidate_classification", {}).get("candidate_type", "fresher")
            linkedin_score_result = calculate_linkedin_score(
                linkedin_signals,
                candidate_type,
                linkedin_profile,
                linkedin_match_results
            )
            print(f" LinkedIn Score: {linkedin_score_result['linkedin_score']}")
            print(f" Candidate Type: {linkedin_score_result['candidate_type']}")
            print(f" Confidence: {linkedin_score_result['confidence']['confidence_level']}")
            print(f" Verification Status: {linkedin_score_result['verification_status']}")
        else:
            print(f"\n Skipping LinkedIn parsing (fetch status: {linkedin_fetch_status})")
            linkedin_signals = {}
            linkedin_score_result = {}

    # Store parsed profile, match results, signals, and score for downstream phases
    parsed["_linkedin_profile"] = linkedin_profile
    parsed["_linkedin_match"] = linkedin_match_results
    parsed["_linkedin_signals"] = linkedin_signals
    parsed["_linkedin_score"] = linkedin_score_result
    parsed["_linkedin_match"] = linkedin_match_results

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
    
    # Extract LinkedIn score if available
    linkedin_score_value = None
    if parsed.get("_linkedin_score"):
        linkedin_score_value = parsed["_linkedin_score"].get("linkedin_score")
        if linkedin_score_value:
            print(f" Including LinkedIn score in portfolio evaluation: {linkedin_score_value}")

    final_result = select_top_repos(
        repos,
        parsed,
        pulse_results,
        demo_results,
        links,   # NEW
        k=3,
        linkedin_score=linkedin_score_value
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
            "fetch_status": linkedin_fetch_status,
            "profile": parsed.get("_linkedin_profile", {}),
            "match_results": parsed.get("_linkedin_match", {}),
            "signals": parsed.get("_linkedin_signals", {}),
            "score": parsed.get("_linkedin_score", {})
        }
    }


# =========================================================
# 🧪 CLI ENTRY POINT (FOR TESTING)
# =========================================================

if __name__ == "__main__":
    pdf_path = "resumes/resume6.pdf"

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
    
    linkedin_profile = linkedin.get('profile', {})
    if linkedin_profile:
        print(f"\nLinkedIn Profile:")
        print(f"  Name:          {linkedin_profile.get('name')}")
        print(f"  Headline:      {linkedin_profile.get('headline')[:60] if linkedin_profile.get('headline') else 'N/A'}...")
        print(f"  Location:      {linkedin_profile.get('location')}")
        
        # Display experience entries
        experience_list = linkedin_profile.get('experience', [])
        print(f"  Experience:    {len(experience_list)} entries")
        if experience_list:
            for i, exp in enumerate(experience_list, 1):
                print(f"    {i}. {exp.get('role', 'N/A')} at {exp.get('company', 'N/A')}")
                if exp.get('start_date') or exp.get('end_date'):
                    print(f"       {exp.get('start_date', '')} - {exp.get('end_date', '')}")
        
        # Display education entries
        education_list = linkedin_profile.get('education', [])
        print(f"  Education:     {len(education_list)} entries")
        if education_list:
            for i, edu in enumerate(education_list, 1):
                print(f"    {i}. {edu.get('institution', 'N/A')}")
                if edu.get('degree'):
                    print(f"       {edu.get('degree')}")
                if edu.get('year'):
                    print(f"       ({edu.get('year')})")
    
    # Display LinkedIn match results
    linkedin_match = linkedin.get('match_results', {})
    if linkedin_match:
        print(f"\nLinkedIn Verification:")
        print(f"  Identity Match:       {linkedin_match.get('identity', {}).get('score', 0)}%")
        print(f"  Experience Match:     {linkedin_match.get('experience', {}).get('score', 0)}%")
        print(f"  Education Match:      {linkedin_match.get('education', {}).get('score', 0)}%")
        print(f"  Timeline Consistency: {linkedin_match.get('timeline', {}).get('score', 0)}%")
        print(f"  Overall Match Score:  {linkedin_match.get('overall_score', 0)}%")
        print(f"  Verification Status:  {'✅ Verified' if linkedin_match.get('overall_match') else '⚠️  Inconsistencies Found'}")
    
    # Display LinkedIn score
    linkedin_score = linkedin.get('score', {})
    if linkedin_score:
        print(f"\nLinkedIn Score:")
        print(f"  Score:                {linkedin_score.get('linkedin_score', 0)}/100")
        print(f"  Confidence:           {linkedin_score.get('confidence', {}).get('confidence_level', 'N/A')}")
        print(f"  Verification Status:  {linkedin_score.get('verification_status', 'N/A')}")
    
    print(f"\nCandidate Type:  {candidate.get('candidate_classification', {}).get('candidate_type')}")
    print(f"Final Score:     {analysis.get('final_score')} — {analysis.get('label')}")
    
    # Show score breakdown if LinkedIn is included
    linkedin_score_obj = linkedin.get('score', {})
    if linkedin_score_obj and linkedin_score_obj.get('linkedin_score'):
        print(f"  (GitHub: 75% + LinkedIn: 25%)")
    
    print(f"Confidence:      {analysis.get('confidence', {}).get('level')}")
    print(f"Projects:        {analysis.get('audit', {}).get('matched_projects')}/{analysis.get('audit', {}).get('total_projects')} verified")
    print(f"Skills verified: {len(analysis.get('skill_validation', {}).get('verified', []))}")
    print(f"Reasons:         {analysis.get('reasons', [])}")
    print()
    print("Repos:")
    for r in analysis.get("repos", []):
        print(f"  {r.get('name'):30s} score={r.get('score')}  tier={r.get('tier')}")