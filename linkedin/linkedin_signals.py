"""
LinkedIn Signals Generator

Generates evidence signals from LinkedIn verification.

Signals (0-100):
- Identity Match
- Experience Match
- Education Match
- Timeline Consistency
- Profile Completeness

These signals are used by the scoring engine to calculate
final LinkedIn verification scores.
"""


def calculate_profile_completeness(linkedin_profile):
    """
    Calculate profile completeness score (0-100).
    
    Measures how complete the LinkedIn profile is based on:
    - Has name
    - Has headline
    - Has location
    - Has experience entries
    - Has education entries
    
    Args:
        linkedin_profile (dict): Parsed LinkedIn profile
    
    Returns:
        dict: {
            "score": 0-100,
            "details": {
                "has_name": bool,
                "has_headline": bool,
                "has_location": bool,
                "has_experience": bool,
                "has_education": bool
            }
        }
    """
    if not linkedin_profile:
        return {
            "score": 0,
            "details": {
                "has_name": False,
                "has_headline": False,
                "has_location": False,
                "has_experience": False,
                "has_education": False
            }
        }
    
    # Check each component
    has_name = bool(linkedin_profile.get("name", "").strip())
    has_headline = bool(linkedin_profile.get("headline", "").strip())
    has_location = bool(linkedin_profile.get("location", "").strip())
    has_experience = len(linkedin_profile.get("experience", [])) > 0
    has_education = len(linkedin_profile.get("education", [])) > 0
    
    # Calculate score (each component worth 20 points)
    score = 0
    if has_name:
        score += 20
    if has_headline:
        score += 20
    if has_location:
        score += 20
    if has_experience:
        score += 20
    if has_education:
        score += 20
    
    return {
        "score": score,
        "details": {
            "has_name": has_name,
            "has_headline": has_headline,
            "has_location": has_location,
            "has_experience": has_experience,
            "has_education": has_education
        }
    }


def generate_signals(match_results, linkedin_profile):
    """
    Generate all LinkedIn verification signals.
    
    Args:
        match_results (dict): Results from linkedin_matcher
        linkedin_profile (dict): Parsed LinkedIn profile
    
    Returns:
        dict: All signals (0-100 each) {
            "identity_match": int,
            "experience_match": int,
            "education_match": int,
            "timeline_consistency": int,
            "profile_completeness": int
        }
    """
    # Extract scores from match results
    identity_score = match_results.get("identity", {}).get("score", 0)
    experience_score = match_results.get("experience", {}).get("score", 0)
    education_score = match_results.get("education", {}).get("score", 0)
    timeline_score = match_results.get("timeline", {}).get("score", 0)
    
    # Calculate profile completeness
    completeness = calculate_profile_completeness(linkedin_profile)
    
    return {
        "identity_match": identity_score,
        "experience_match": experience_score,
        "education_match": education_score,
        "timeline_consistency": timeline_score,
        "profile_completeness": completeness["score"],
        "profile_completeness_details": completeness["details"]
    }


def get_signal_summary(signals):
    """
    Get a human-readable summary of signals.
    
    Args:
        signals (dict): Signals from generate_signals()
    
    Returns:
        dict: Summary with status for each signal
    """
    def get_status(score):
        if score >= 80:
            return "✅ Strong"
        elif score >= 60:
            return "⚠️  Moderate"
        else:
            return "❌ Weak"
    
    return {
        "identity_match": {
            "score": signals["identity_match"],
            "status": get_status(signals["identity_match"])
        },
        "experience_match": {
            "score": signals["experience_match"],
            "status": get_status(signals["experience_match"])
        },
        "education_match": {
            "score": signals["education_match"],
            "status": get_status(signals["education_match"])
        },
        "timeline_consistency": {
            "score": signals["timeline_consistency"],
            "status": get_status(signals["timeline_consistency"])
        },
        "profile_completeness": {
            "score": signals["profile_completeness"],
            "status": get_status(signals["profile_completeness"])
        }
    }
