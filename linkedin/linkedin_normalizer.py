"""
LinkedIn Entity Normalizer

Normalizes company names and institution names for stable matching.

Goal: Make Resume ↔ LinkedIn comparisons robust against:
- Spelling variations
- Legal suffixes (Corp, Inc, Ltd, Pvt Ltd)
- Abbreviations (IIT vs Indian Institute of Technology)
- Case differences
- Extra whitespace

Examples:
    "Microsoft Corporation" → "microsoft"
    "Microsoft India Pvt Ltd" → "microsoft"
    "Indian Institute of Technology Delhi" → "iit delhi"
    "IIT Delhi" → "iit delhi"
"""

import re


# ============================================================
# COMPANY NAME NORMALIZATION
# ============================================================

# Common company suffixes to remove
COMPANY_SUFFIXES = [
    r'\bCorporation\b',
    r'\bCorp\.?\b',
    r'\bIncorporated\b',
    r'\bInc\.?\b',
    r'\bLimited\b',
    r'\bLtd\.?\b',
    r'\bLLC\b',
    r'\bL\.L\.C\.?\b',
    r'\bPvt\.?\b',
    r'\bPrivate\b',
    r'\bPublic\b',
    r'\bCo\.?\b',
    r'\bCompany\b',
    r'\bGroup\b',
    r'\bHoldings?\b',
    r'\bInternational\b',
    r'\bGlobal\b',
    r'\bTechnologies\b',
    r'\bTech\b',
    r'\bSolutions?\b',
    r'\bServices?\b',
    r'\bSystems?\b',
    r'\bSoftware\b',
    r'\bIndia\b',
    r'\bUSA\b',
    r'\bAmerica\b',
    r'\bEurope\b',
    r'\bAsia\b',
]

# Company name mappings for common variations
COMPANY_ALIASES = {
    'google': ['alphabet', 'google inc', 'google llc'],
    'microsoft': ['msft', 'ms'],
    'amazon': ['amzn', 'aws'],
    'facebook': ['meta', 'fb'],
    'ibm': ['international business machines'],
    'apple': ['apple inc'],
    'oracle': ['oracle corp'],
    'salesforce': ['salesforce.com'],
    'adobe': ['adobe systems'],
    'intel': ['intel corp'],
    'nvidia': ['nvidia corp'],
    'qualcomm': ['qualcomm inc'],
    'cisco': ['cisco systems'],
    'sap': ['sap se'],
    'vmware': ['vmware inc'],
    'dell': ['dell technologies', 'dell emc'],
    'hp': ['hewlett packard', 'hewlett-packard', 'hpe'],
    'accenture': ['accenture plc'],
    'tcs': ['tata consultancy services', 'tata consultancy'],
    'infosys': ['infosys limited'],
    'wipro': ['wipro limited'],
    'cognizant': ['cognizant technology solutions'],
    'hcl': ['hcl technologies'],
    'tech mahindra': ['tech mahindra limited'],
}


def normalize_company_name(company_name):
    """
    Normalize company name for matching.
    
    Args:
        company_name (str): Raw company name
    
    Returns:
        str: Normalized company name (lowercase, no suffixes)
    
    Examples:
        "Microsoft Corporation" → "microsoft"
        "Google India Pvt Ltd" → "google"
        "Tata Consultancy Services" → "tcs"
    """
    if not company_name:
        return ""
    
    # Convert to lowercase
    normalized = company_name.lower().strip()
    
    # Remove common suffixes
    for suffix in COMPANY_SUFFIXES:
        normalized = re.sub(suffix, '', normalized, flags=re.IGNORECASE)
    
    # Remove punctuation and extra whitespace
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    # Check for exact match first
    for canonical, aliases in COMPANY_ALIASES.items():
        if normalized == canonical:
            return canonical
        if normalized in aliases:
            return canonical
    
    # Check for partial match (only if normalized contains the alias as a word)
    for canonical, aliases in COMPANY_ALIASES.items():
        # Check if canonical name appears as a complete word in normalized
        if re.search(r'\b' + re.escape(canonical) + r'\b', normalized):
            return canonical
        # Check if any alias appears as a complete word
        for alias in aliases:
            if re.search(r'\b' + re.escape(alias) + r'\b', normalized):
                return canonical
    
    return normalized


# ============================================================
# INSTITUTION NAME NORMALIZATION
# ============================================================

# Common institution suffixes to remove
INSTITUTION_SUFFIXES = [
    r'\bUniversity\b',
    r'\bInstitute\b',
    r'\bCollege\b',
    r'\bSchool\b',
    r'\bAcademy\b',
    r'\bof Technology\b',
    r'\bof Engineering\b',
    r'\bof Science\b',
    r'\bof Management\b',
    r'\bof Business\b',
]

# Institution name mappings for common variations
INSTITUTION_ALIASES = {
    'iit delhi': ['indian institute of technology delhi', 'iit-delhi', 'iitd'],
    'iit bombay': ['indian institute of technology bombay', 'iit-bombay', 'iitb'],
    'iit madras': ['indian institute of technology madras', 'iit-madras', 'iitm'],
    'iit kanpur': ['indian institute of technology kanpur', 'iit-kanpur', 'iitk'],
    'iit kharagpur': ['indian institute of technology kharagpur', 'iit-kharagpur', 'iitkgp'],
    'iit roorkee': ['indian institute of technology roorkee', 'iit-roorkee', 'iitr'],
    'iit guwahati': ['indian institute of technology guwahati', 'iit-guwahati', 'iitg'],
    'iit hyderabad': ['indian institute of technology hyderabad', 'iit-hyderabad', 'iith'],
    'nit trichy': ['national institute of technology tiruchirappalli', 'nit-trichy', 'nitt'],
    'nit warangal': ['national institute of technology warangal', 'nit-warangal', 'nitw'],
    'bits pilani': ['birla institute of technology and science pilani', 'bits-pilani'],
    'iiit hyderabad': ['international institute of information technology hyderabad', 'iiit-hyderabad'],
    'iiit bangalore': ['international institute of information technology bangalore', 'iiit-bangalore'],
    'dtu': ['delhi technological university', 'delhi college of engineering', 'dce'],
    'nsit': ['netaji subhas institute of technology', 'nsut'],
    'vit': ['vellore institute of technology'],
    'manipal': ['manipal institute of technology', 'manipal university'],
    'amity': ['amity university'],
    'srm': ['srm institute of science and technology', 'srm university'],
    'mit': ['massachusetts institute of technology'],
    'stanford': ['stanford university'],
    'harvard': ['harvard university'],
    'berkeley': ['university of california berkeley', 'uc berkeley', 'ucb'],
    'cmu': ['carnegie mellon university', 'carnegie mellon'],
    'caltech': ['california institute of technology'],
    'oxford': ['university of oxford'],
    'cambridge': ['university of cambridge'],
}


def normalize_institution_name(institution_name):
    """
    Normalize institution name for matching.
    
    Args:
        institution_name (str): Raw institution name
    
    Returns:
        str: Normalized institution name (lowercase, no suffixes)
    
    Examples:
        "Indian Institute of Technology Delhi" → "iit delhi"
        "IIT Delhi" → "iit delhi"
        "Massachusetts Institute of Technology" → "mit"
    """
    if not institution_name:
        return ""
    
    # Convert to lowercase
    normalized = institution_name.lower().strip()
    
    # Special handling for IIT (Indian Institute of Technology)
    if 'indian institute of technology' in normalized:
        # Extract city name after "technology"
        match = re.search(r'indian institute of technology\s+(\w+)', normalized)
        if match:
            city = match.group(1)
            return f"iit {city}"
    
    # Special handling for NIT (National Institute of Technology)
    if 'national institute of technology' in normalized:
        match = re.search(r'national institute of technology\s+(\w+)', normalized)
        if match:
            city = match.group(1)
            return f"nit {city}"
    
    # Special handling for IIIT (International Institute of Information Technology)
    if 'international institute of information technology' in normalized:
        match = re.search(r'international institute of information technology\s+(\w+)', normalized)
        if match:
            city = match.group(1)
            return f"iiit {city}"
    
    # Special handling for BITS
    if 'birla institute of technology and science' in normalized:
        if 'pilani' in normalized:
            return 'bits pilani'
        return 'bits'
    
    # Remove common suffixes
    for suffix in INSTITUTION_SUFFIXES:
        normalized = re.sub(suffix, '', normalized, flags=re.IGNORECASE)
    
    # Remove punctuation and extra whitespace
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    # Check for exact match first
    for canonical, aliases in INSTITUTION_ALIASES.items():
        if normalized == canonical:
            return canonical
        if normalized in aliases:
            return canonical
    
    # Check for partial match (only if normalized contains the alias as a complete word)
    for canonical, aliases in INSTITUTION_ALIASES.items():
        # Check if canonical name appears as a complete word in normalized
        if re.search(r'\b' + re.escape(canonical) + r'\b', normalized):
            return canonical
        # Check if any alias appears as a complete word
        for alias in aliases:
            if re.search(r'\b' + re.escape(alias) + r'\b', normalized):
                return canonical
    
    return normalized


# ============================================================
# ROLE NAME NORMALIZATION
# ============================================================

# Role title mappings for common variations
ROLE_ALIASES = {
    'software engineer': ['sde', 'software developer', 'software dev', 'engineer', 'developer'],
    'senior software engineer': ['senior sde', 'senior software developer', 'sde 2', 'sde ii'],
    'backend engineer': ['backend developer', 'backend dev', 'server side engineer'],
    'frontend engineer': ['frontend developer', 'frontend dev', 'ui engineer', 'ui developer'],
    'full stack engineer': ['full stack developer', 'fullstack engineer', 'fullstack developer'],
    'data scientist': ['data science engineer', 'ml engineer', 'machine learning engineer'],
    'data engineer': ['data engineering', 'big data engineer'],
    'devops engineer': ['devops', 'site reliability engineer', 'sre'],
    'product manager': ['pm', 'product lead', 'product owner'],
    'intern': ['internship', 'summer intern', 'trainee'],
}


def normalize_role_name(role_name):
    """
    Normalize role/job title for matching.
    
    Args:
        role_name (str): Raw role name
    
    Returns:
        str: Normalized role name
    
    Examples:
        "Software Development Engineer" → "software engineer"
        "SDE" → "software engineer"
        "Backend Dev" → "backend engineer"
    """
    if not role_name:
        return ""
    
    # Convert to lowercase
    normalized = role_name.lower().strip()
    
    # Remove common noise words
    normalized = re.sub(r'\b(i|ii|iii|iv|1|2|3|4)\b', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    # Check for exact match first
    for canonical, aliases in ROLE_ALIASES.items():
        if normalized == canonical:
            return canonical
        if normalized in aliases:
            return canonical
    
    # Check for partial match (only if normalized contains the alias as a complete word)
    for canonical, aliases in ROLE_ALIASES.items():
        # Check if canonical name appears in normalized
        if canonical in normalized:
            return canonical
        # Check if any alias appears
        for alias in aliases:
            if alias in normalized:
                return canonical
    
    return normalized


# ============================================================
# BATCH NORMALIZATION HELPERS
# ============================================================

def normalize_experience_list(experience_list):
    """
    Normalize all companies and roles in an experience list.
    
    Args:
        experience_list (list): List of experience dicts
    
    Returns:
        list: Experience list with normalized fields added
    """
    normalized = []
    for exp in experience_list:
        normalized_exp = exp.copy()
        normalized_exp['company_normalized'] = normalize_company_name(exp.get('company', ''))
        normalized_exp['role_normalized'] = normalize_role_name(exp.get('role', ''))
        normalized.append(normalized_exp)
    return normalized


def normalize_education_list(education_list):
    """
    Normalize all institutions in an education list.
    
    Args:
        education_list (list): List of education dicts
    
    Returns:
        list: Education list with normalized fields added
    """
    normalized = []
    for edu in education_list:
        normalized_edu = edu.copy()
        normalized_edu['institution_normalized'] = normalize_institution_name(edu.get('institution', ''))
        normalized.append(normalized_edu)
    return normalized
