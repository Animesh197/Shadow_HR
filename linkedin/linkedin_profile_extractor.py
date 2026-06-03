"""
LinkedIn Profile Extractor

Main pipeline for extracting structured data from LinkedIn HTML.

Flow:
1. Locate sections (Experience, Education, About, Header)
2. Extract clean text from sections
3. Use LLM to extract structured data
4. Validate with Pydantic schemas
5. Generate confidence scores
6. Return structured profile
"""

from linkedin.parsers.section_locator import locate_sections
from linkedin.parsers.section_extractor import extract_section_text
from linkedin.llm.linkedin_llm_extractor import extract_experience, extract_education, extract_header
from linkedin.llm.retry_handler import extract_with_retry
from linkedin.schemas.linkedin_schema import ExperienceEntry, EducationEntry, LinkedInProfile
from linkedin.validation.confidence import calculate_extraction_confidence
from linkedin.cache.llm_cache import get_cached_extraction, set_cached_extraction, is_cached
from bs4 import BeautifulSoup


def extract_linkedin_profile(html, linkedin_url=""):
    """
    Extract structured LinkedIn profile data from HTML.
    
    This is the main entry point that replaces parse_linkedin_profile().
    
    Args:
        html (str): Raw LinkedIn profile HTML
        linkedin_url (str): LinkedIn URL (for caching)
    
    Returns:
        dict: {
            "name": str,
            "headline": str,
            "location": str,
            "experience": [{"company": "", "role": "", "start_date": "", "end_date": ""}],
            "education": [{"institution": "", "degree": "", "year": ""}],
            "confidence": {
                "experience_confidence": float,
                "education_confidence": float,
                "headline_confidence": float,
                "location_confidence": float,
                "overall_confidence": float
            }
        }
    """
    if not html:
        return _empty_profile()
    
    # Check cache
    if linkedin_url and is_cached(linkedin_url):
        print(f"[linkedin_profile_extractor] Using cached extraction for {linkedin_url}")
        return get_cached_extraction(linkedin_url)
    
    # Step 1: Locate sections
    print("[linkedin_profile_extractor] Locating profile sections...")
    sections = locate_sections(html)
    
    # Step 2: Extract clean text from sections
    print("[linkedin_profile_extractor] Extracting clean text from sections...")
    section_texts = extract_section_text(sections)
    
    # Step 3: Extract name from HTML (same as before, simple extraction)
    name = _extract_name(html)
    
    # Step 4: Use LLM to extract structured data
    print("[linkedin_profile_extractor] Extracting experience with LLM...")
    experience_data = extract_with_retry(
        extract_experience,
        section_texts["experience_text"],
        ExperienceEntry
    )
    
    print("[linkedin_profile_extractor] Extracting education with LLM...")
    education_data = extract_with_retry(
        extract_education,
        section_texts["education_text"],
        EducationEntry
    )
    
    print("[linkedin_profile_extractor] Extracting header data with LLM...")
    header_data = extract_with_retry(
        extract_header,
        section_texts["header_text"]
    )
    
    # Step 5: Build profile
    profile = {
        "name": name,
        "headline": header_data.get("headline", ""),
        "location": header_data.get("location", ""),
        "experience": experience_data.get("experience", []),
        "education": education_data.get("education", [])
    }
    
    # Step 6: Validate with Pydantic
    try:
        validated_profile = LinkedInProfile(**profile)
        profile = validated_profile.model_dump()
    except Exception as e:
        print(f"[linkedin_profile_extractor] Validation warning: {e}")
        # Continue with unvalidated data
    
    # Step 7: Generate confidence scores
    print("[linkedin_profile_extractor] Calculating confidence scores...")
    confidence = calculate_extraction_confidence(profile)
    profile["confidence"] = confidence
    
    # Step 8: Cache result
    if linkedin_url:
        set_cached_extraction(linkedin_url, profile)
    
    print(f"[linkedin_profile_extractor] Extraction complete:")
    print(f"  - Name: {profile['name']}")
    print(f"  - Headline: {profile['headline'][:60] if profile['headline'] else 'N/A'}...")
    print(f"  - Location: {profile['location']}")
    print(f"  - Experience entries: {len(profile['experience'])}")
    print(f"  - Education entries: {len(profile['education'])}")
    print(f"  - Overall confidence: {confidence['overall_confidence']}%")
    
    return profile


def _extract_name(html):
    """
    Extract name from HTML (simple extraction from title tag).
    
    Args:
        html (str): Raw HTML
    
    Returns:
        str: Name
    """
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string if soup.title else ""
    
    # LinkedIn title format: "Name | LinkedIn"
    if '|' in title:
        name = title.split('|')[0].strip()
        return name
    
    return ""


def _empty_profile():
    """Return empty profile structure."""
    return {
        "name": "",
        "headline": "",
        "location": "",
        "experience": [],
        "education": [],
        "confidence": {
            "experience_confidence": 0.0,
            "education_confidence": 0.0,
            "headline_confidence": 0.0,
            "location_confidence": 0.0,
            "overall_confidence": 0.0
        }
    }


# Backward compatibility alias
def parse_linkedin_profile(html):
    """
    Backward compatibility wrapper for extract_linkedin_profile.
    
    This maintains the old function signature without confidence scores
    for code that still uses parse_linkedin_profile().
    """
    result = extract_linkedin_profile(html)
    
    # Remove confidence from result for backward compatibility
    result_without_confidence = {
        "name": result["name"],
        "headline": result["headline"],
        "location": result["location"],
        "experience": result["experience"],
        "education": result["education"]
    }
    
    return result_without_confidence
