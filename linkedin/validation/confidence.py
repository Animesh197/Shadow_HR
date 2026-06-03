"""
Confidence Scoring

Generates confidence scores for extracted LinkedIn profile data.
"""


def calculate_extraction_confidence(profile_data):
    """
    Calculate confidence scores for extracted profile data.
    
    Args:
        profile_data (dict): Extracted LinkedIn profile data
    
    Returns:
        dict: {
            "experience_confidence": float (0-100),
            "education_confidence": float (0-100),
            "headline_confidence": float (0-100),
            "location_confidence": float (0-100),
            "overall_confidence": float (0-100)
        }
    """
    experience = profile_data.get("experience", [])
    education = profile_data.get("education", [])
    headline = profile_data.get("headline", "")
    location = profile_data.get("location", "")
    
    # Experience confidence
    experience_conf = _calculate_experience_confidence(experience)
    
    # Education confidence
    education_conf = _calculate_education_confidence(education)
    
    # Headline confidence
    headline_conf = _calculate_headline_confidence(headline)
    
    # Location confidence
    location_conf = _calculate_location_confidence(location)
    
    # Overall confidence (weighted average)
    overall_conf = (
        experience_conf * 0.30 +
        education_conf * 0.30 +
        headline_conf * 0.20 +
        location_conf * 0.20
    )
    
    return {
        "experience_confidence": round(experience_conf, 2),
        "education_confidence": round(education_conf, 2),
        "headline_confidence": round(headline_conf, 2),
        "location_confidence": round(location_conf, 2),
        "overall_confidence": round(overall_conf, 2)
    }


def _calculate_experience_confidence(experience):
    """
    Calculate confidence for experience extraction.
    
    Factors:
    - Has at least one entry: +30
    - Role exists for each entry: +20 per entry (max 40)
    - Company exists for each entry: +20 per entry (max 40)
    - Dates exist for each entry: +10 per entry (max 20)
    """
    if not experience:
        return 0.0
    
    score = 30.0  # Has entries
    
    num_entries = len(experience)
    
    # Role completeness (max 40 points)
    roles_complete = sum(1 for e in experience if e.get("role", "").strip())
    score += min((roles_complete / num_entries) * 40, 40)
    
    # Company completeness (max 40 points)
    companies_complete = sum(1 for e in experience if e.get("company", "").strip())
    score += min((companies_complete / num_entries) * 40, 40)
    
    # Date completeness (max 20 points)
    dates_complete = sum(1 for e in experience 
                        if e.get("start_date", "").strip() or e.get("end_date", "").strip())
    score += min((dates_complete / num_entries) * 20, 20)
    
    return min(score, 100.0)


def _calculate_education_confidence(education):
    """
    Calculate confidence for education extraction.
    
    Factors:
    - Has at least one entry: +30
    - Institution exists for each entry: +40 per entry (max 50)
    - Degree exists for each entry: +15 per entry (max 20)
    - Year exists for each entry: +10 per entry (max 10)
    """
    if not education:
        return 0.0
    
    score = 30.0  # Has entries
    
    num_entries = len(education)
    
    # Institution completeness (max 50 points)
    institutions_complete = sum(1 for e in education if e.get("institution", "").strip())
    score += min((institutions_complete / num_entries) * 50, 50)
    
    # Degree completeness (max 20 points)
    degrees_complete = sum(1 for e in education if e.get("degree", "").strip())
    score += min((degrees_complete / num_entries) * 20, 20)
    
    # Year completeness (max 10 points)
    years_complete = sum(1 for e in education if e.get("year", "").strip())
    score += min((years_complete / num_entries) * 10, 10)
    
    return min(score, 100.0)


def _calculate_headline_confidence(headline):
    """
    Calculate confidence for headline extraction.
    
    Factors:
    - Exists: +50
    - Length > 20 chars: +30
    - Doesn't look like location: +20
    """
    if not headline or not headline.strip():
        return 0.0
    
    score = 50.0  # Exists
    
    # Length check
    if len(headline) > 20:
        score += 30.0
    else:
        score += 15.0  # Partial credit for short headlines
    
    # Not a location (doesn't match City, State pattern)
    if not _looks_like_location(headline):
        score += 20.0
    
    return min(score, 100.0)


def _calculate_location_confidence(location):
    """
    Calculate confidence for location extraction.
    
    Factors:
    - Exists: +50
    - Has comma (City, State/Country): +30
    - Looks like proper location format: +20
    """
    if not location or not location.strip():
        return 0.0
    
    score = 50.0  # Exists
    
    # Has comma separator
    if ',' in location:
        score += 30.0
    
    # Looks like proper location
    if _looks_like_location(location):
        score += 20.0
    
    return min(score, 100.0)


def _looks_like_location(text):
    """
    Check if text looks like a geographic location.
    
    Args:
        text (str): Text to check
    
    Returns:
        bool: True if looks like location
    """
    import re
    
    # Location typically has:
    # - Comma separator(s)
    # - Proper capitalization
    # - Short length (<100 chars)
    
    if len(text) > 100:
        return False
    
    # Check for comma-separated format
    if ',' in text:
        parts = [p.strip() for p in text.split(',')]
        # Each part should start with capital letter and be reasonable length
        if all(p and p[0].isupper() and len(p) < 50 for p in parts):
            return True
    
    # Single word location (e.g., "London", "India")
    if len(text.split()) == 1 and text[0].isupper():
        return True
    
    return False
