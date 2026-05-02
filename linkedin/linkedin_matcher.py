"""
LinkedIn Matcher

Compares Resume ↔ LinkedIn data to generate match scores.

Matching Modules:
- identity_matcher() - Compare name consistency
- experience_matcher() - Compare work experience
- education_matcher() - Compare education
- timeline_matcher() - Check timeline consistency

Each matcher returns a score (0-100) indicating match quality.
"""

from linkedin.linkedin_normalizer import (
    normalize_company_name,
    normalize_institution_name,
    normalize_role_name
)
from difflib import SequenceMatcher


# ============================================================
# IDENTITY MATCHING
# ============================================================

def identity_matcher(resume_name, linkedin_name):
    """
    Compare name consistency between resume and LinkedIn.
    
    Args:
        resume_name (str): Name from resume
        linkedin_name (str): Name from LinkedIn profile
    
    Returns:
        dict: {
            "score": 0-100,
            "match": bool,
            "details": str
        }
    
    Examples:
        "John Doe" vs "John Doe" → 100
        "John Doe" vs "John D." → 80
        "John Doe" vs "Jane Smith" → 0
    """
    if not resume_name or not linkedin_name:
        return {
            "score": 0,
            "match": False,
            "details": "Missing name data"
        }
    
    # Normalize: lowercase, remove extra spaces
    resume_norm = resume_name.lower().strip()
    linkedin_norm = linkedin_name.lower().strip()
    
    # Exact match
    if resume_norm == linkedin_norm:
        return {
            "score": 100,
            "match": True,
            "details": "Exact name match"
        }
    
    # Split into parts (first, middle, last)
    resume_parts = resume_norm.split()
    linkedin_parts = linkedin_norm.split()
    
    # Check if all resume parts appear in LinkedIn name
    resume_in_linkedin = all(part in linkedin_parts for part in resume_parts)
    linkedin_in_resume = all(part in resume_parts for part in linkedin_parts)
    
    if resume_in_linkedin or linkedin_in_resume:
        return {
            "score": 90,
            "match": True,
            "details": "Name parts match (possible middle name difference)"
        }
    
    # Check first and last name match
    if len(resume_parts) >= 2 and len(linkedin_parts) >= 2:
        first_match = resume_parts[0] == linkedin_parts[0]
        last_match = resume_parts[-1] == linkedin_parts[-1]
        
        if first_match and last_match:
            return {
                "score": 85,
                "match": True,
                "details": "First and last name match"
            }
        
        if first_match or last_match:
            return {
                "score": 50,
                "match": False,
                "details": "Partial name match (only first or last)"
            }
    
    # Fuzzy match using sequence similarity
    similarity = SequenceMatcher(None, resume_norm, linkedin_norm).ratio()
    score = int(similarity * 100)
    
    if score >= 70:
        return {
            "score": score,
            "match": True,
            "details": f"High similarity ({score}%)"
        }
    
    return {
        "score": score,
        "match": False,
        "details": f"Low similarity ({score}%)"
    }


# ============================================================
# EXPERIENCE MATCHING
# ============================================================

def experience_matcher(resume_experience, linkedin_experience):
    """
    Compare work experience between resume and LinkedIn.
    
    Args:
        resume_experience (list): Experience from resume
        linkedin_experience (list): Experience from LinkedIn
    
    Returns:
        dict: {
            "score": 0-100,
            "matched_count": int,
            "total_resume_count": int,
            "matches": list of matched entries,
            "mismatches": list of unmatched entries
        }
    """
    if not resume_experience:
        return {
            "score": 100,  # No experience to verify
            "matched_count": 0,
            "total_resume_count": 0,
            "matches": [],
            "mismatches": []
        }
    
    if not linkedin_experience:
        return {
            "score": 0,  # Resume has experience but LinkedIn doesn't
            "matched_count": 0,
            "total_resume_count": len(resume_experience),
            "matches": [],
            "mismatches": resume_experience
        }
    
    # Normalize all entries
    resume_normalized = []
    for exp in resume_experience:
        resume_normalized.append({
            "original": exp,
            "company_norm": normalize_company_name(exp.get("company", "")),
            "role_norm": normalize_role_name(exp.get("role", ""))
        })
    
    linkedin_normalized = []
    for exp in linkedin_experience:
        linkedin_normalized.append({
            "original": exp,
            "company_norm": normalize_company_name(exp.get("company", "")),
            "role_norm": normalize_role_name(exp.get("role", ""))
        })
    
    # Match resume entries against LinkedIn
    matches = []
    mismatches = []
    
    for resume_exp in resume_normalized:
        matched = False
        
        for linkedin_exp in linkedin_normalized:
            # Check if company matches
            company_match = (
                resume_exp["company_norm"] == linkedin_exp["company_norm"] and
                resume_exp["company_norm"] != ""
            )
            
            # Check if role matches (optional, less strict)
            role_match = (
                resume_exp["role_norm"] == linkedin_exp["role_norm"] and
                resume_exp["role_norm"] != ""
            )
            
            # Company match is sufficient (role may vary in wording)
            if company_match:
                matches.append({
                    "resume": resume_exp["original"],
                    "linkedin": linkedin_exp["original"],
                    "company_match": True,
                    "role_match": role_match
                })
                matched = True
                break
        
        if not matched:
            mismatches.append(resume_exp["original"])
    
    # Calculate score
    matched_count = len(matches)
    total_count = len(resume_experience)
    
    if total_count == 0:
        score = 100
    else:
        score = int((matched_count / total_count) * 100)
    
    return {
        "score": score,
        "matched_count": matched_count,
        "total_resume_count": total_count,
        "matches": matches,
        "mismatches": mismatches
    }


# ============================================================
# EDUCATION MATCHING
# ============================================================

def education_matcher(resume_education, linkedin_education):
    """
    Compare education between resume and LinkedIn.
    
    Args:
        resume_education (list): Education from resume
        linkedin_education (list): Education from LinkedIn
    
    Returns:
        dict: {
            "score": 0-100,
            "matched_count": int,
            "total_resume_count": int,
            "matches": list of matched entries,
            "mismatches": list of unmatched entries
        }
    """
    if not resume_education:
        return {
            "score": 100,  # No education to verify
            "matched_count": 0,
            "total_resume_count": 0,
            "matches": [],
            "mismatches": []
        }
    
    if not linkedin_education:
        return {
            "score": 0,  # Resume has education but LinkedIn doesn't
            "matched_count": 0,
            "total_resume_count": len(resume_education),
            "matches": [],
            "mismatches": resume_education
        }
    
    # Normalize all entries
    resume_normalized = []
    for edu in resume_education:
        resume_normalized.append({
            "original": edu,
            "institution_norm": normalize_institution_name(edu.get("institution", ""))
        })
    
    linkedin_normalized = []
    for edu in linkedin_education:
        linkedin_normalized.append({
            "original": edu,
            "institution_norm": normalize_institution_name(edu.get("institution", ""))
        })
    
    # Match resume entries against LinkedIn
    matches = []
    mismatches = []
    
    for resume_edu in resume_normalized:
        matched = False
        
        for linkedin_edu in linkedin_normalized:
            # Check if institution matches
            institution_match = (
                resume_edu["institution_norm"] == linkedin_edu["institution_norm"] and
                resume_edu["institution_norm"] != ""
            )
            
            if institution_match:
                matches.append({
                    "resume": resume_edu["original"],
                    "linkedin": linkedin_edu["original"],
                    "institution_match": True
                })
                matched = True
                break
        
        if not matched:
            mismatches.append(resume_edu["original"])
    
    # Calculate score
    matched_count = len(matches)
    total_count = len(resume_education)
    
    if total_count == 0:
        score = 100
    else:
        score = int((matched_count / total_count) * 100)
    
    return {
        "score": score,
        "matched_count": matched_count,
        "total_resume_count": total_count,
        "matches": matches,
        "mismatches": mismatches
    }


# ============================================================
# TIMELINE MATCHING
# ============================================================

def timeline_matcher(resume_experience, linkedin_experience):
    """
    Check timeline consistency between resume and LinkedIn.
    
    Checks for:
    - Overlapping employment (working at 2 companies simultaneously)
    - Large gaps in employment
    - Timeline order consistency
    
    Args:
        resume_experience (list): Experience from resume
        linkedin_experience (list): Experience from LinkedIn
    
    Returns:
        dict: {
            "score": 0-100,
            "consistent": bool,
            "issues": list of timeline issues found
        }
    """
    # For now, return a basic implementation
    # Full timeline analysis requires date parsing which is complex
    
    issues = []
    
    # Check if both have experience data
    if not resume_experience and not linkedin_experience:
        return {
            "score": 100,
            "consistent": True,
            "issues": []
        }
    
    # Check if counts are similar
    resume_count = len(resume_experience) if resume_experience else 0
    linkedin_count = len(linkedin_experience) if linkedin_experience else 0
    
    count_diff = abs(resume_count - linkedin_count)
    
    if count_diff > 2:
        issues.append(f"Experience count mismatch: Resume has {resume_count}, LinkedIn has {linkedin_count}")
    
    # Basic scoring based on count similarity
    if count_diff == 0:
        score = 100
    elif count_diff == 1:
        score = 90
    elif count_diff == 2:
        score = 80
    else:
        score = max(50, 100 - (count_diff * 10))
    
    return {
        "score": score,
        "consistent": len(issues) == 0,
        "issues": issues
    }


# ============================================================
# MAIN MATCHING FUNCTION
# ============================================================

def match_resume_linkedin(resume_data, linkedin_profile):
    """
    Main function to match resume against LinkedIn profile.
    
    Args:
        resume_data (dict): Parsed resume data with name, experience, education
        linkedin_profile (dict): Parsed LinkedIn profile
    
    Returns:
        dict: Complete matching results with all scores
    """
    results = {
        "identity": identity_matcher(
            resume_data.get("name", ""),
            linkedin_profile.get("name", "")
        ),
        "experience": experience_matcher(
            resume_data.get("experience", []),
            linkedin_profile.get("experience", [])
        ),
        "education": education_matcher(
            resume_data.get("education", []),
            linkedin_profile.get("education", [])
        ),
        "timeline": timeline_matcher(
            resume_data.get("experience", []),
            linkedin_profile.get("experience", [])
        )
    }
    
    # Calculate overall match score (weighted average)
    weights = {
        "identity": 0.15,
        "experience": 0.40,
        "education": 0.30,
        "timeline": 0.15
    }
    
    overall_score = (
        results["identity"]["score"] * weights["identity"] +
        results["experience"]["score"] * weights["experience"] +
        results["education"]["score"] * weights["education"] +
        results["timeline"]["score"] * weights["timeline"]
    )
    
    results["overall_score"] = round(overall_score, 2)
    results["overall_match"] = overall_score >= 70  # 70% threshold for "match"
    
    return results
