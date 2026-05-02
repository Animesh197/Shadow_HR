"""
Debug LinkedIn Parser

Fetches and saves LinkedIn HTML for inspection, then tests parsing.
"""

import os
from dotenv import load_dotenv
from linkedin_fetcher import fetch_linkedin_html
from linkedin_parser import parse_linkedin_profile

load_dotenv()

def debug_linkedin_profile(linkedin_url):
    """
    Fetch LinkedIn profile, save HTML, and test parsing.
    """
    print(f"Fetching: {linkedin_url}")
    html, status = fetch_linkedin_html(linkedin_url)
    
    print(f"Fetch status: {status}")
    print(f"HTML length: {len(html)} characters")
    
    if status == "success" and html:
        # Save HTML for inspection
        with open("linkedin_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("\n✅ HTML saved to linkedin_debug.html")
        
        # Save first 5000 chars for quick inspection
        with open("linkedin_debug_preview.txt", "w", encoding="utf-8") as f:
            f.write(html[:5000])
        print("✅ Preview saved to linkedin_debug_preview.txt")
        
        # Test parsing
        print("\n" + "="*60)
        print("PARSING RESULTS:")
        print("="*60)
        
        profile = parse_linkedin_profile(html)
        
        print(f"\nName: {profile['name']}")
        print(f"Headline: {profile['headline'][:100] if profile['headline'] else 'N/A'}")
        print(f"Location: {profile['location']}")
        print(f"\nExperience: {len(profile['experience'])} entries")
        for i, exp in enumerate(profile['experience'][:3], 1):
            print(f"  {i}. {exp['role']} at {exp['company']}")
            print(f"     {exp['start_date']} - {exp['end_date']}")
        
        print(f"\nEducation: {len(profile['education'])} entries")
        for i, edu in enumerate(profile['education'][:3], 1):
            print(f"  {i}. {edu['institution']}")
            print(f"     {edu['degree']}")
            print(f"     {edu['year']}")
        
        # Debug: Show raw text extraction
        print("\n" + "="*60)
        print("RAW TEXT EXTRACTION (first 2000 chars):")
        print("="*60)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        print(text[:2000])
        
    else:
        print(f"\n❌ Failed to fetch LinkedIn profile: {status}")


if __name__ == "__main__":
    # Use your LinkedIn URL
    linkedin_url = "https://www.linkedin.com/in/animesh-rai-8a0688226"
    debug_linkedin_profile(linkedin_url)
