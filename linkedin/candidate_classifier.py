"""
Candidate Classifier

Classifies candidate as:
- experienced
- fresher

Based on work experience timeline.
"""

from datetime import datetime
from dateutil import parser as date_parser
import re


def parse_date(date_str):
    """
    Parse date string to datetime object.
    Handles: "Jan 2023", "2023", "January 2023", "Present", etc.
    """
    if not date_str:
        return None

    date_str = date_str.strip()

    # Handle "Present" or "Current"
    if date_str.lower() in ["present", "current", "now"]:
        return datetime.now()

    try:
        # Try parsing with dateutil (handles most formats)
        return date_parser.parse(date_str, fuzzy=True)
    except:
        # Fallback: extract year only
        year_match = re.search(r'\b(20\d{2})\b', date_str)
        if year_match:
            year = int(year_match.group(1))
            return datetime(year, 1, 1)

    return None


def compute_experience_months(experience_list):
    """
    Compute total months of work experience.
    Returns: (total_months, full_time_months, internship_months, has_full_time_role)
    """
    total_months = 0
    full_time_months = 0
    internship_months = 0
    has_full_time_role = False

    for exp in experience_list:
        role = (exp.get("role") or "").lower()
        start_date_str = exp.get("start_date", "")
        end_date_str = exp.get("end_date", "")

        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        if not start_date:
            continue

        if not end_date:
            end_date = datetime.now()

        # Compute duration in months
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        months = max(months, 0)

        total_months += months

        # Classify as internship or full-time
        is_internship = any(kw in role for kw in ["intern", "trainee", "apprentice"])

        if is_internship:
            internship_months += months
        else:
            full_time_months += months
            has_full_time_role = True

    return total_months, full_time_months, internship_months, has_full_time_role


def is_recent_graduate(education_list):
    """
    Check if candidate graduated recently (within last 2 years).
    """
    current_year = datetime.now().year

    for edu in education_list:
        year_str = edu.get("year", "")

        # Extract year
        year_match = re.search(r'\b(20\d{2})\b', year_str)
        if year_match:
            grad_year = int(year_match.group(1))
            if current_year - grad_year <= 2:
                return True

    return False


def classify_candidate(experience_list, education_list):
    """
    Classify candidate as experienced or fresher.

    Logic (from linkedin.md):
    - If full_time_months >= 12: experienced
    - If has_full_time_role and full_time_months >= 6: experienced
    - If internship_only: fresher
    - If recent_graduate: fresher
    - Else: fresher
    """

    total_months, full_time_months, internship_months, has_full_time_role = compute_experience_months(experience_list)

    recent_grad = is_recent_graduate(education_list)

    # Classification rules
    if full_time_months >= 12:
        return {
            "candidate_type": "experienced",
            "total_experience_months": total_months,
            "full_time_months": full_time_months,
            "internship_months": internship_months,
            "reason": "12+ months full-time experience"
        }

    if has_full_time_role and full_time_months >= 6:
        return {
            "candidate_type": "experienced",
            "total_experience_months": total_months,
            "full_time_months": full_time_months,
            "internship_months": internship_months,
            "reason": "6+ months full-time experience"
        }

    if internship_months > 0 and full_time_months == 0:
        return {
            "candidate_type": "fresher",
            "total_experience_months": total_months,
            "full_time_months": full_time_months,
            "internship_months": internship_months,
            "reason": "Internship-only experience"
        }

    if recent_grad:
        return {
            "candidate_type": "fresher",
            "total_experience_months": total_months,
            "full_time_months": full_time_months,
            "internship_months": internship_months,
            "reason": "Recent graduate"
        }

    # Default: fresher
    return {
        "candidate_type": "fresher",
        "total_experience_months": total_months,
        "full_time_months": full_time_months,
        "internship_months": internship_months,
        "reason": "No significant full-time experience"
    }
