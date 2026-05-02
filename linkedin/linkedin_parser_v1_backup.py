"""
LinkedIn Parser V2

Improved parser based on actual LinkedIn HTML structure.
Extracts structured profile data from fetched LinkedIn HTML.
"""

import re
from bs4 import BeautifulSoup


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
    Look for patterns like:
    - "Role at Company"
    - Followed by dates
    """
    experience = []
    seen_entries = set()
    
    # Strategy 1: Find experience section in HTML
    exp_section = soup.find(['section', 'div'], {'id': re.compile(r'experience', re.I)})
    if not exp_section:
        exp_section = soup.find(['section', 'div'], {'class': re.compile(r'experience', re.I)})
    
    if exp_section:
        # Get text from experience section
        exp_text = exp_section.get_text(separator='|', strip=True)
        lines = [l.strip() for l in exp_text.split('|') if l.strip()]
        
        # Look for "Role at Company" patterns
        for i, line in enumerate(lines):
            match = re.search(r'^([A-Z][a-zA-Z\s]{3,60}?)\s+(?:at|@)\s+([A-Z][a-zA-Z\s&,\.]{3,60})$', line)
            if match:
                role = match.group(1).strip()
                company = match.group(2).strip()
                
                # Avoid duplicates
                entry_key = f"{role.lower()}|{company.lower()}"
                if entry_key in seen_entries:
                    continue
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
    
    return experience


def extract_education(soup, visible_text):
    """
    Extract education entries.
    
    Look for university/college/institute names in education section.
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
    
    # Look for institution names
    institution_keywords = [
        'University', 'Institute', 'College', 'School', 'Academy',
        'IIT', 'NIT', 'BITS', 'VIT', 'SRM', 'Amity', 'Manipal',
        'MIT', 'Stanford', 'Harvard', 'Berkeley', 'Cambridge', 'Oxford'
    ]
    
    for i, line in enumerate(lines):
        # Skip lines that are clearly not institutions
        if any(skip in line for skip in ['Someone at', 'View', 'Connect', 'Follow', 'Message', 'Private to you']):
            continue
        
        # Check if line contains institution keywords
        if any(keyword in line for keyword in institution_keywords):
            institution = line.strip()
            
            # Skip if too short or too long
            if len(institution) < 5 or len(institution) > 150:
                continue
            
            # Skip if it's a person's description (contains "at")
            if ' at ' in institution and not institution.startswith(('University', 'Institute', 'College', 'School')):
                continue
            
            # Skip if already seen
            if institution.lower() in seen_institutions:
                continue
            seen_institutions.add(institution.lower())
            
            # Look for degree in nearby lines
            degree = ""
            year = ""
            
            for j in range(i + 1, min(i + 5, len(lines))):
                nearby_line = lines[j]
                
                # Skip lines that are clearly not degree/year info
                if any(skip in nearby_line for skip in ['Someone at', 'View', 'Connect', 'Follow']):
                    continue
                
                # Check for degree
                if not degree and re.search(
                    r'Bachelor|Master|B\.?Tech|M\.?Tech|B\.?E|M\.?E|B\.?Sc|M\.?Sc|MBA|PhD|Diploma',
                    nearby_line,
                    re.IGNORECASE
                ):
                    degree = nearby_line[:100]
                
                # Check for year
                if not year:
                    year_match = re.search(r'(\d{4})\s*[-–]\s*(\d{4}|Present)', nearby_line)
                    if year_match:
                        year = f"{year_match.group(1)}-{year_match.group(2)}"
            
            education.append({
                "institution": institution,
                "degree": degree,
                "year": year
            })
            
            if len(education) >= 5:
                break
    
    return education
