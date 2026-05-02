"""
LinkedIn Scorer

Calculates final LinkedIn verification score based on:
- Candidate type (fresher vs experienced)
- LinkedIn signals
- Different scoring weights for each candidate type

Fresher Weights:
- Education Match: 40%
- Internship Match: 25%
- Timeline Consistency: 20%
- Identity Match: 10%
- Profile Completeness: 5%

Experienced Weights:
- Experience Match: 40%
- Timeline Consistency: 25%
- Education Match: 15%
- Identity Match: 10%
- Profile Completeness: 10%
"""


def calculate_fresher_score(signals):
    """
    Calculate LinkedIn score for fresher candidates.
    
    Focus: Academic consistency and internship verification.
    
    Args:
        signals (dict): LinkedIn signals (0-100 each)
    
    Returns:
        dict: {
            "linkedin_score": float (0-100),
            "breakdown": dict with weighted scores,
            "candidate_type": "fresher"
        }
    """
    # Weights for fresher candidates
    weights = {
        "education_match": 0.40,
        "experience_match": 0.25,  # Internships count as experience
        "timeline_consistency": 0.20,
        "identity_match": 0.10,
        "profile_completeness": 0.05
    }
    
    # Calculate weighted score
    education_score = signals.get("education_match", 0) * weights["education_match"]
    internship_score = signals.get("experience_match", 0) * weights["experience_match"]
    timeline_score = signals.get("timeline_consistency", 0) * weights["timeline_consistency"]
    identity_score = signals.get("identity_match", 0) * weights["identity_match"]
    completeness_score = signals.get("profile_completeness", 0) * weights["profile_completeness"]
    
    linkedin_score = (
        education_score +
        internship_score +
        timeline_score +
        identity_score +
        completeness_score
    )
    
    return {
        "linkedin_score": round(linkedin_score, 2),
        "breakdown": {
            "education_match": round(education_score, 2),
            "internship_match": round(internship_score, 2),
            "timeline_consistency": round(timeline_score, 2),
            "identity_match": round(identity_score, 2),
            "profile_completeness": round(completeness_score, 2)
        },
        "weights": weights,
        "candidate_type": "fresher"
    }


def calculate_experienced_score(signals):
    """
    Calculate LinkedIn score for experienced candidates.
    
    Focus: Professional consistency and work experience verification.
    
    Args:
        signals (dict): LinkedIn signals (0-100 each)
    
    Returns:
        dict: {
            "linkedin_score": float (0-100),
            "breakdown": dict with weighted scores,
            "candidate_type": "experienced"
        }
    """
    # Weights for experienced candidates
    weights = {
        "experience_match": 0.40,
        "timeline_consistency": 0.25,
        "education_match": 0.15,
        "identity_match": 0.10,
        "profile_completeness": 0.10
    }
    
    # Calculate weighted score
    experience_score = signals.get("experience_match", 0) * weights["experience_match"]
    timeline_score = signals.get("timeline_consistency", 0) * weights["timeline_consistency"]
    education_score = signals.get("education_match", 0) * weights["education_match"]
    identity_score = signals.get("identity_match", 0) * weights["identity_match"]
    completeness_score = signals.get("profile_completeness", 0) * weights["profile_completeness"]
    
    linkedin_score = (
        experience_score +
        timeline_score +
        education_score +
        identity_score +
        completeness_score
    )
    
    return {
        "linkedin_score": round(linkedin_score, 2),
        "breakdown": {
            "experience_match": round(experience_score, 2),
            "timeline_consistency": round(timeline_score, 2),
            "education_match": round(education_score, 2),
            "identity_match": round(identity_score, 2),
            "profile_completeness": round(completeness_score, 2)
        },
        "weights": weights,
        "candidate_type": "experienced"
    }


def calculate_linkedin_confidence(signals, linkedin_profile, match_results):
    """
    Calculate confidence level for LinkedIn verification.
    
    Factors:
    - Section availability (profile completeness)
    - Parser confidence (how much data was extracted)
    - Match agreement (consistency across signals)
    - Timeline quality
    
    Args:
        signals (dict): LinkedIn signals
        linkedin_profile (dict): Parsed LinkedIn profile
        match_results (dict): Match results from matcher
    
    Returns:
        dict: {
            "confidence_level": "high" | "medium" | "low",
            "confidence_score": float (0-100),
            "factors": dict with individual factor scores
        }
    """
    # Factor 1: Profile completeness (0-100)
    completeness = signals.get("profile_completeness", 0)
    
    # Factor 2: Data availability (how much was extracted)
    has_experience = len(linkedin_profile.get("experience", [])) > 0
    has_education = len(linkedin_profile.get("education", [])) > 0
    has_headline = bool(linkedin_profile.get("headline", ""))
    
    data_availability = 0
    if has_experience:
        data_availability += 33
    if has_education:
        data_availability += 33
    if has_headline:
        data_availability += 34
    
    # Factor 3: Match consistency (variance across signals)
    signal_values = [
        signals.get("identity_match", 0),
        signals.get("experience_match", 0),
        signals.get("education_match", 0),
        signals.get("timeline_consistency", 0)
    ]
    
    # High consistency = low variance
    avg_signal = sum(signal_values) / len(signal_values)
    variance = sum((x - avg_signal) ** 2 for x in signal_values) / len(signal_values)
    std_dev = variance ** 0.5
    
    # Convert to consistency score (lower std_dev = higher consistency)
    # Max std_dev is ~50 (when signals are 0 and 100)
    consistency_score = max(0, 100 - (std_dev * 2))
    
    # Factor 4: Timeline quality
    timeline_score = signals.get("timeline_consistency", 0)
    
    # Calculate overall confidence (weighted average)
    confidence_score = (
        completeness * 0.25 +
        data_availability * 0.25 +
        consistency_score * 0.25 +
        timeline_score * 0.25
    )
    
    # Determine confidence level
    if confidence_score >= 75:
        confidence_level = "high"
    elif confidence_score >= 50:
        confidence_level = "medium"
    else:
        confidence_level = "low"
    
    return {
        "confidence_level": confidence_level,
        "confidence_score": round(confidence_score, 2),
        "factors": {
            "profile_completeness": round(completeness, 2),
            "data_availability": round(data_availability, 2),
            "match_consistency": round(consistency_score, 2),
            "timeline_quality": round(timeline_score, 2)
        }
    }


def calculate_linkedin_score(signals, candidate_type, linkedin_profile, match_results):
    """
    Main function to calculate LinkedIn verification score.
    
    Routes to appropriate scoring function based on candidate type.
    
    Args:
        signals (dict): LinkedIn signals
        candidate_type (str): "fresher" or "experienced"
        linkedin_profile (dict): Parsed LinkedIn profile
        match_results (dict): Match results from matcher
    
    Returns:
        dict: Complete LinkedIn scoring results
    """
    # Route to appropriate scoring function
    if candidate_type == "fresher":
        score_result = calculate_fresher_score(signals)
    else:
        score_result = calculate_experienced_score(signals)
    
    # Calculate confidence
    confidence_result = calculate_linkedin_confidence(signals, linkedin_profile, match_results)
    
    # Combine results
    return {
        "linkedin_score": score_result["linkedin_score"],
        "breakdown": score_result["breakdown"],
        "weights": score_result["weights"],
        "candidate_type": score_result["candidate_type"],
        "confidence": confidence_result,
        "verification_status": get_verification_status(
            score_result["linkedin_score"],
            confidence_result["confidence_level"]
        )
    }


def get_verification_status(linkedin_score, confidence_level):
    """
    Determine verification status based on score and confidence.
    
    Args:
        linkedin_score (float): LinkedIn score (0-100)
        confidence_level (str): "high" | "medium" | "low"
    
    Returns:
        str: Verification status
    """
    if linkedin_score >= 80 and confidence_level == "high":
        return "✅ Verified"
    elif linkedin_score >= 70 and confidence_level in ["high", "medium"]:
        return "✅ Verified"
    elif linkedin_score >= 60:
        return "⚠️  Partially Verified"
    else:
        return "❌ Inconsistencies Found"
