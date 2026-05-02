"""
LinkedIn Parser V3

Improved parser based on actual LinkedIn HTML structure.
Extracts structured profile data from fetched LinkedIn HTML.

V2.1 Updates:
- Added validation helpers to filter UI elements, achievements, projects
- Improved education extraction to only capture real institutions
- Improved experience extraction to handle multiple formats
- Better duplicate prevention

V3 Updates (2026-05-02):
- Experience: Look-ahead logic to combine role and company from separate lines
- Education: Filter minors, certificates, online courses
- Education: Better duplicate detection with base name extraction
- Education: Validate degree types (full degrees only)
- Backward compatible with fallback to old methods
"""

import re
from bs4 import BeautifulSoup


# ============================================================================
# VALIDATION HELPER FUNCTIONS
# ============================================================================

def is_ui_element(line):
    """
    Detect UI elements and navigation text.
    
    Returns True if line is a UI element (should be filtered out).
    """
    if not line or len(line) < 2:
        return True
    
    # Exact matches for common UI elements
    ui_keywords = [
        'message', 'connect', 'follow', 'view', 'show more', 'show less',
        'see more', 'see less', 'edit', 'add', 'remove', 'save', 'cancel'
    ]
    
    if line.lower().strip() in ui_keywords:
        return True
    
    # Contains UI indicators
    ui_indicators = ['connections', 'followers', 'enhance profile', 'add section', 'private to you']
    if any(indicator in line.lower() for indicator in ui_indicators):
        return True
    
    # Very short lines (likely UI)
    if len(line.strip()) < 3:
        return True
    
    return False


def is_achievement_or_award(line):
    """
    Detect achievements, awards, certifications, and competition results.
    
    Returns True if line is an achievement (should be filtered from education).
    """
    achievement_keywords = [
        'winner', 'award', 'prize', 'place', 'rank', 'achievement',
        'certification', 'certificate', 'licensed', 'hackathon', 'competition'
    ]
    
    line_lower = line.lower()
    
    # Check for achievement keywords
    if any(keyword in line_lower for keyword in achievement_keywords):
        return True
    
    # Pattern: "YYYY – Description" (common for awards)
    if re.search(r'\d{4}\s*[–-]\s*\d*(st|nd|rd|th)?\s*(place|rank|winner)', line_lower):
        return True
    
    return False


def is_experience_entry(line):
    """
    Detect if line is a work experience entry.
    
    Returns True if line looks like work experience.
    """
    # Must have reasonable length
    if len(line) < 10 or len(line) > 300:
        return False
    
    # Check for work indicators: "at", "@", "·", "•"
    work_separators = [' at ', ' @ ', ' · ', ' • ']
    has_separator = any(sep in line for sep in work_separators)
    
    if not has_separator:
        return False
    
    # Should NOT start with institution keywords (those are education)
    institution_starts = ['university', 'institute', 'college', 'school']
    if any(line.lower().startswith(keyword) for keyword in institution_starts):
        return False
    
    # Should NOT contain degree keywords (those are education)
    degree_keywords = ['bachelor', 'master', 'b.tech', 'm.tech', 'b.e', 'm.e', 'b.sc', 'm.sc', 'mba', 'phd']
    if any(keyword in line.lower() for keyword in degree_keywords):
        return False
    
    return True


def is_valid_institution(line):
    """
    Validate if a line is a real educational institution.
    
    Returns True only if line looks like a genuine institution entry.
    """
    # Must have reasonable length
    if len(line) < 10 or len(line) > 150:
        return False
    
    # Must contain institution keywords
    institution_keywords = [
        'University', 'Institute', 'College', 'School', 'Academy',
        'IIT', 'NIT', 'BITS', 'VIT', 'SRM', 'Amity', 'Manipal',
        'MIT', 'Stanford', 'Harvard', 'Berkeley', 'Cambridge', 'Oxford'
    ]
    
    has_keyword = any(keyword in line for keyword in institution_keywords)
    if not has_keyword:
        return False
    
    # Filter out work experience that mentions institutions
    # Example: "Product @ Meesho • IIT Kanpur • AIRBUS"
    work_indicators = [' @ ', ' · ', ' • ']
    if any(indicator in line for indicator in work_indicators):
        # If line starts with institution keyword, it's valid
        # Otherwise, it's likely experience mentioning institution
        if not any(line.startswith(keyword) for keyword in institution_keywords):
            return False
    
    # Filter out achievements mentioning institutions
    # Example: "NIRMAAN 2025 – 2nd Place Winner (Delhi University)"
    if is_achievement_or_award(line):
        return False
    
    # Filter out project names mentioning institutions
    # Example: "The StackMentalist · Indian Institute of Technology, Patna"
    # Projects typically have: "ProjectName · Institution"
    if ' · ' in line or ' • ' in line:
        parts = re.split(r'[·•]', line)
        # If first part doesn't contain institution keyword, it's likely a project
        if parts and not any(keyword in parts[0] for keyword in institution_keywords):
            return False
    
    # Filter out UI elements
    if is_ui_element(line):
        return False
    
    return True


def clean_institution_name(institution):
    """
    Clean institution name by removing prefixes, suffixes, and extra text.
    
    Example: "The StackMentalist · IIT Patna" -> "IIT Patna"
    """
    # Remove leading bullets and dashes
    institution = re.sub(r'^[·•\-\s]+', '', institution)
    
    # If contains bullet/separator, take the part with institution keyword
    if ' · ' in institution or ' • ' in institution:
        parts = re.split(r'[·•]', institution)
        institution_keywords = [
            'University', 'Institute', 'College', 'School', 'Academy',
            'IIT', 'NIT', 'BITS', 'VIT', 'SRM', 'MIT', 'Stanford'
        ]
        for part in parts:
            if any(keyword in part for keyword in institution_keywords):
                institution = part.strip()
                break
    
    # Remove trailing descriptions after comma (keep "City, State" but remove extra)
    # Example: "IIT Patna, Computer Science" -> "IIT Patna"
    parts = institution.split(',')
    if len(parts) > 2:
        institution = ', '.join(parts[:2])
    
    return institution.strip()


def normalize_experience_entry(line):
    """
    Extract role and company from experience entry.
    
    Handles formats: "Role at Company", "Role @ Company", "Role · Company"
    
    Returns: dict with 'role' and 'company'
    """
    # Try different separators
    separators = [' at ', ' @ ', ' · ', ' • ']
    
    for sep in separators:
        if sep in line:
            parts = line.split(sep, 1)  # Split only on first occurrence
            if len(parts) == 2:
                role = parts[0].strip()
                company_part = parts[1].strip()
                
                # If company has multiple items (bullets), take first
                if '•' in company_part or '·' in company_part:
                    company = re.split(r'[•·]', company_part)[0].strip()
                else:
                    company = company_part
                
                return {'role': role, 'company': company}
    
    return {'role': '', 'company': ''}


# ============================================================================
# EXPERIENCE EXTRACTION HELPERS (V3)
# ============================================================================

def is_role_line(line):
    """
    Detect if a line is a job title/role.
    
    Characteristics of role lines:
    - No separators (at, @, ·, •)
    - Reasonable length (10-100 chars)
    - Not a date line
    - Not a location line
    - Not a UI element
    - Title-case or sentence-case
    
    Returns: bool
    """
    if not line or len(line) < 10 or len(line) > 100:
        return False
    
    # Should NOT contain separators
    if any(sep in line for sep in [' at ', ' @ ', ' · ', ' • ']):
        return False
    
    # Should NOT be a date line
    if re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}', line, re.IGNORECASE):
        return False
    
    # Should NOT be a location line (City, State pattern)
    if re.match(r'^[A-Z][a-z]+,\s*[A-Z]', line):
        return False
    
    # Should NOT be a UI element
    if is_ui_element(line):
        return False
    
    # Should NOT start with numbers or bullets
    if re.match(r'^[\d•·\-\*]+', line):
        return False
    
    # Should have some capital letters (title-case)
    if not any(c.isupper() for c in line):
        return False
    
    return True


def has_company_info(line):
    """
    Detect if a line contains company information.
    
    Format: "Company · Type" or "Company • Type"
    
    Returns: bool
    """
    if not line or len(line) < 10 or len(line) > 200:
        return False
    
    # Must contain bullet separators
    if not (' · ' in line or ' • ' in line):
        return False
    
    # Should NOT be a date line
    if re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}', line, re.IGNORECASE):
        return False
    
    # Should NOT be a location line
    if re.match(r'^[A-Z][a-z]+,\s*[A-Z]', line):
        return False
    
    return True


def extract_company_from_line(line):
    """
    Extract company name from "Company · Type" or "Company • Type" format.
    
    Returns: str (company name)
    """
    # Split on bullet separators
    for sep in [' · ', ' • ']:
        if sep in line:
            parts = line.split(sep)
            if parts:
                # Take first part as company name
                company = parts[0].strip()
                # Remove any leading/trailing punctuation
                company = company.strip('·•-')
                return company
    
    return line.strip()


# ============================================================================
# EDUCATION EXTRACTION HELPERS (V3)
# ============================================================================

def is_minor_or_certificate(line):
    """
    Detect minors, certificates, and certifications.
    
    Returns: bool
    """
    line_lower = line.lower()
    
    # Check for minor keywords
    minor_keywords = ['minor in', 'minor', 'certificate', 'certification', 'certified']
    if any(keyword in line_lower for keyword in minor_keywords):
        return True
    
    # Pattern: "Minor in X by Institution"
    if re.search(r'minor\s+in\s+.+\s+by\s+', line_lower):
        return True
    
    return False


def is_online_course(line):
    """
    Detect online courses and MOOCs.
    
    Returns: bool
    """
    line_lower = line.lower()
    
    # Check for online course keywords
    course_keywords = ['online course', 'mooc', 'coursera', 'edx', 'udemy', 'cs50', 'udacity', 'khan academy']
    if any(keyword in line_lower for keyword in course_keywords):
        return True
    
    return False


def extract_institution_base_name(institution):
    """
    Extract core institution name for duplicate detection.
    
    Examples:
    - "Indian Institute of Technology, Patna - BS" → "Indian Institute of Technology, Patna"
    - "IIT Patna" → "IIT Patna"
    - "BS-MS ID at IIT Patna" → "IIT Patna"
    
    Returns: str
    """
    # Remove degree info after dash
    if ' - ' in institution:
        institution = institution.split(' - ')[0].strip()
    
    # Remove "at Institution" pattern
    if ' at ' in institution:
        parts = institution.split(' at ')
        # Take the part with institution keywords
        institution_keywords = ['University', 'Institute', 'College', 'School', 'IIT', 'NIT', 'MIT']
        for part in parts:
            if any(keyword in part for keyword in institution_keywords):
                institution = part.strip()
                break
    
    # Remove program IDs (BS-MS ID, etc.)
    institution = re.sub(r'^[A-Z]{2,}-[A-Z]{2,}\s+ID\s+', '', institution)
    
    return institution.strip()


def is_full_degree(degree):
    """
    Validate if degree is a full degree program (not minor/certificate).
    
    Returns: bool
    """
    if not degree:
        return False
    
    degree_lower = degree.lower()
    
    # Check for full degree keywords
    full_degree_keywords = [
        'bachelor', 'master', 'b.tech', 'm.tech', 'b.e', 'm.e',
        'b.sc', 'm.sc', 'bs', 'ms', 'mba', 'phd', 'doctorate'
    ]
    
    has_degree = any(keyword in degree_lower for keyword in full_degree_keywords)
    
    # Should NOT be a minor or certificate
    not_minor = 'minor' not in degree_lower
    not_certificate = 'certificate' not in degree_lower and 'certification' not in degree_lower
    
    return has_degree and not_minor and not_certificate


def parse_linkedin_profile(html):
    """
    Extract structured profile from LinkedIn HTML.
    
    Args:
        html (str): Raw HTML from linkedin_fetcher
    
    Returns:
        dict: Structured profile with name, headline, location, experience[], education[]
    """
    if not html:
        return {
            "name": "",
            "headline": "",
            "location": "",
            "experience": [],
            "education": []
        }
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Get visible text with pipe separator for easier parsing
    visible_text = soup.get_text(separator='|', strip=True)
    
    profile = {
        "name": extract_name(soup),
        "headline": extract_headline(soup, visible_text),
        "location": extract_location(soup, visible_text),
        "experience": extract_experience(soup, visible_text),
        "education": extract_education(soup, visible_text)
    }
    
    return profile


def extract_name(soup):
    """
    Extract profile name from <title> tag.
    LinkedIn format: "Name | LinkedIn"
    """
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text().strip()
        if '|' in title:
            name = title.split('|')[0].strip()
            if name and name.lower() not in ['linkedin', '']:
                return name
    
    # Fallback: try h1 tags
    h1_tags = soup.find_all('h1')
    for h1 in h1_tags:
        text = h1.get_text().strip()
        if text and 3 < len(text) < 100:
            return text
    
    return ""


def extract_headline(soup, visible_text):
    """
    Extract professional headline.
    
    LinkedIn structure in visible text:
    Name|Headline (long descriptive text)|Location|University|...
    
    Headline characteristics:
    - Appears right after name
    - 50-500 characters
    - Contains job/role keywords
    - NOT a location (no "City, State" pattern)
    - NOT a university name
    """
    lines = [l.strip() for l in visible_text.split('|') if l.strip()]
    
    # Get name first
    name = extract_name(soup)
    if not name:
        return ""
    
    # Find name in lines, then look for headline
    for i, line in enumerate(lines):
        if name in line:
            # Check next few lines for the headline
            for j in range(i + 1, min(i + 5, len(lines))):
                candidate = lines[j]
                
                # Skip short lines
                if len(candidate) < 50:
                    continue
                
                # Skip if it's too long
                if len(candidate) > 500:
                    continue
                
                # Skip if it looks like a location (City, State pattern)
                if re.match(r'^[A-Z][a-z]+,\s*[A-Z]', candidate):
                    continue
                
                # Skip if it's an educational institution
                if any(keyword in candidate for keyword in ['University', 'Institute', 'College', 'School']):
                    continue
                
                # Skip common UI elements
                if any(keyword in candidate for keyword in ['Resources', 'Enhance profile', 'Add section', 'Contact info', 'connections']):
                    continue
                
                # This looks like a headline!
                return candidate
    
    return ""


def extract_location(soup, visible_text):
    """
    Extract location.
    
    LinkedIn format: "City, State, Country" or "City, Country"
    Appears after headline in visible text.
    """
    lines = [l.strip() for l in visible_text.split('|') if l.strip()]
    
    for line in lines:
        # Look for location pattern: "City, State/Country"
        # Must have comma and reasonable length
        if ',' in line and 5 < len(line) < 100:
            # Check if it matches location patterns
            # Pattern 1: "City, State, Country"
            if re.match(r'^[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]+$', line):
                return line
            
            # Pattern 2: "City, Country"
            if re.match(r'^[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]+$', line):
                # Make sure it's not a company name or other text
                if not any(keyword in line for keyword in ['University', 'Institute', 'College', 'Inc', 'Ltd', 'Corp']):
                    return line
    
    return ""


def extract_experience(soup, visible_text):
    """
    Extract experience entries.
    
    LinkedIn shows experience in a dedicated section.
    V3: Uses look-ahead logic to combine role and company from separate lines.
    
    LinkedIn format:
    Line 1: Role (e.g., "Assistant Software Developer")
    Line 2: Company · Type (e.g., "The StackMentalist · Internship")
    Line 3: Dates
    Line 4: Location
    """
    experience = []
    seen_entries = set()
    
    # Strategy 1: Find experience section in HTML
    exp_section = soup.find(['section', 'div'], {'id': re.compile(r'experience', re.I)})
    if not exp_section:
        exp_section = soup.find(['section', 'div'], {'class': re.compile(r'experience', re.I)})
    
    # Strategy 2: Look for "Experience" heading
    if not exp_section:
        for heading in soup.find_all(['h2', 'h3']):
            if 'experience' in heading.get_text().lower():
                exp_section = heading.find_parent(['section', 'div'])
                if exp_section:
                    break
    
    if exp_section:
        # Get text from experience section
        exp_text = exp_section.get_text(separator='|', strip=True)
        lines = [l.strip() for l in exp_text.split('|') if l.strip()]
        
        # V3: Use look-ahead logic to combine role and company
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this line is a role
            if is_role_line(line):
                role = line
                company = ""
                start_date = ""
                end_date = ""
                
                # Look ahead for company info (next 1-2 lines)
                for j in range(i + 1, min(i + 3, len(lines))):
                    if has_company_info(lines[j]):
                        company = extract_company_from_line(lines[j])
                        
                        # Look for dates in next lines after company
                        for k in range(j + 1, min(j + 3, len(lines))):
                            date_line = lines[k]
                            dates = re.findall(
                                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|Present',
                                date_line,
                                re.IGNORECASE
                            )
                            if dates:
                                start_date = dates[0] if len(dates) > 0 else ""
                                end_date = dates[1] if len(dates) > 1 else ""
                                break
                        
                        break
                
                # If we found both role and company, add entry
                if role and company:
                    # Avoid duplicates
                    entry_key = f"{role.lower()}|{company.lower()}"
                    if entry_key not in seen_entries:
                        seen_entries.add(entry_key)
                        
                        experience.append({
                            "company": company,
                            "role": role,
                            "start_date": start_date,
                            "end_date": end_date
                        })
                        
                        if len(experience) >= 10:
                            break
                
                # Skip processed lines
                i = j + 1 if company else i + 1
                continue
            
            # FALLBACK: Try old method for "Role at Company" on single line
            elif is_experience_entry(line):
                entry = normalize_experience_entry(line)
                role = entry.get('role', '')
                company = entry.get('company', '')
                
                if role and company:
                    # Avoid duplicates
                    entry_key = f"{role.lower()}|{company.lower()}"
                    if entry_key not in seen_entries:
                        seen_entries.add(entry_key)
                        
                        # Look for dates in nearby lines
                        start_date = ""
                        end_date = ""
                        for j in range(i + 1, min(i + 5, len(lines))):
                            date_line = lines[j]
                            dates = re.findall(
                                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|Present',
                                date_line,
                                re.IGNORECASE
                            )
                            if dates:
                                start_date = dates[0] if len(dates) > 0 else ""
                                end_date = dates[1] if len(dates) > 1 else ""
                                break
                        
                        experience.append({
                            "company": company,
                            "role": role,
                            "start_date": start_date,
                            "end_date": end_date
                        })
                        
                        if len(experience) >= 10:
                            break
            
            i += 1
    
    return experience


def extract_education(soup, visible_text):
    """
    Extract education entries.
    
    Look for university/college/institute names in education section.
    V3: Added filtering for minors, certificates, online courses, and better duplicate detection.
    """
    education = []
    seen_institutions = set()
    
    # Strategy 1: Find education section
    edu_section = soup.find(['section', 'div'], {'id': re.compile(r'education', re.I)})
    if not edu_section:
        edu_section = soup.find(['section', 'div'], {'class': re.compile(r'education', re.I)})
    
    if edu_section:
        edu_text = edu_section.get_text(separator='|', strip=True)
        lines = [l.strip() for l in edu_text.split('|') if l.strip()]
    else:
        # Fallback: search in visible text near education keywords
        lines = [l.strip() for l in visible_text.split('|') if l.strip()]
    
    # PRE-FILTER: Remove obvious non-education lines
    filtered_lines = []
    for line in lines:
        # Skip UI elements
        if is_ui_element(line):
            continue
        # Skip achievements/awards
        if is_achievement_or_award(line):
            continue
        # Skip experience entries
        if is_experience_entry(line):
            continue
        # V3: Skip minors and certificates
        if is_minor_or_certificate(line):
            continue
        # V3: Skip online courses
        if is_online_course(line):
            continue
        filtered_lines.append(line)
    
    # Look for institution names
    institution_keywords = [
        'University', 'Institute', 'College', 'School', 'Academy',
        'IIT', 'NIT', 'BITS', 'VIT', 'SRM', 'Amity', 'Manipal',
        'MIT', 'Stanford', 'Harvard', 'Berkeley', 'Cambridge', 'Oxford',
        'Board', 'CBSE', 'ICSE'  # Added for high school boards
    ]
    
    for i, line in enumerate(filtered_lines):
        # Check if line contains institution keywords
        if any(keyword in line for keyword in institution_keywords):
            # VALIDATE: Is this actually an institution?
            if not is_valid_institution(line):
                continue
            
            # CLEAN: Remove prefixes and extra text
            institution = clean_institution_name(line)
            
            # Skip if too short after cleaning
            if len(institution) < 10:
                continue
            
            # V3: Better duplicate detection - extract base name
            institution_base = extract_institution_base_name(institution)
            
            # Skip if already seen (case-insensitive)
            if institution_base.lower() in seen_institutions:
                continue
            seen_institutions.add(institution_base.lower())
            
            # Look for degree in nearby lines
            degree = ""
            year = ""
            
            for j in range(i + 1, min(i + 5, len(filtered_lines))):
                nearby_line = filtered_lines[j]
                
                # Skip if it's another institution (moved to next entry)
                if is_valid_institution(nearby_line):
                    break
                
                # Check for degree
                if not degree and re.search(
                    r'Bachelor|Master|B\.?Tech|M\.?Tech|B\.?E|M\.?E|B\.?Sc|M\.?Sc|MBA|PhD|Diploma|Higher\s+Secondary|Middle\s+School',
                    nearby_line,
                    re.IGNORECASE
                ):
                    degree = nearby_line[:100]
                
                # Check for year
                if not year:
                    year_match = re.search(r'(\d{4})\s*[-–]\s*(\d{4}|Present)', nearby_line)
                    if year_match:
                        year = f"{year_match.group(1)}-{year_match.group(2)}"
            
            # V3: Validate it's a full degree (or high school)
            # Allow entries without degree info (might be high school or institution-only)
            # But if degree is found, validate it's not a minor/certificate
            if degree and not is_full_degree(degree):
                # Check if it's a high school (CBSE, ICSE, etc.)
                if not any(keyword in line for keyword in ['Board', 'CBSE', 'ICSE', 'Secondary', 'High School']):
                    continue
            
            education.append({
                "institution": institution,
                "degree": degree,
                "year": year
            })
            
            if len(education) >= 5:
                break
    
    return education
