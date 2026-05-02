"""
LinkedIn Parser

Extracts structured profile data from fetched LinkedIn HTML.

Output schema:
{
    "name": "",
    "headline": "",
    "location": "",
    "experience": [],
    "education": []
}

Parser Sources:
- HTML selectors
- aria labels
- visible section blocks
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
    
    profile = {
        "name": extract_name(soup, html),
        "headline": extract_headline(soup, html),
        "location": extract_location(soup, html),
        "experience": extract_experience(soup, html),
        "education": extract_education(soup, html)
    }
    
    return profile


def extract_name(soup, html):
    """
    Extract profile name.
    LinkedIn puts it in <title> as "Name | LinkedIn"
    """
    # Try <title> first — most reliable
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text().strip()
        if '|' in title:
            name = title.split('|')[0].strip()
            if name and name.lower() not in ['linkedin', '']:
                return name
    
    # Try h1 with class containing 'name' or 'heading'
    h1_tags = soup.find_all('h1')
    for h1 in h1_tags:
        text = h1.get_text().strip()
        if text and len(text) > 3 and len(text) < 100:
            return text
    
    return ""


def extract_headline(soup, html):
    """
    Extract professional headline (appears right after name in profile).
    """
    # Look for div with class containing 'headline' or role-related text
    headline_patterns = [
        {'class': re.compile(r'headline', re.I)},
        {'class': re.compile(r'top-card.*description', re.I)},
    ]
    
    for pattern in headline_patterns:
        element = soup.find('div', pattern)
        if element:
            text = element.get_text().strip()
            if text and len(text) > 10:
                return text[:300]
    
    # Fallback: look for text after name in visible content
    text = soup.get_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Find name line, then get next substantial line
    for i, line in enumerate(lines):
        if len(line) > 20 and i + 1 < len(lines):
            next_line = lines[i + 1]
            if len(next_line) > 20 and len(next_line) < 300:
                return next_line
    
    return ""


def extract_location(soup, html):
    """
    Extract location — typically "City, State, Country" pattern.
    """
    # Look for span/div with location-related class
    location_patterns = [
        {'class': re.compile(r'location', re.I)},
        {'class': re.compile(r'top-card.*subline', re.I)},
    ]
    
    for pattern in location_patterns:
        element = soup.find(['span', 'div'], pattern)
        if element:
            text = element.get_text().strip()
            # Validate it looks like a location (has comma or known city/country)
            if ',' in text or any(place in text for place in ['India', 'USA', 'UK', 'Canada']):
                return text
    
    # Fallback: regex pattern for location format
    text = soup.get_text()
    location_match = re.search(r'([A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]+(?:,\s*[A-Z][a-zA-Z\s]+)?)', text)
    if location_match:
        location = location_match.group(1).strip()
        if len(location) < 100:  # Sanity check
            return location
    
    return ""


def extract_experience(soup, html):
    """
    Extract experience entries from LinkedIn HTML.
    
    Returns:
        list: [{"company": "", "role": "", "start_date": "", "end_date": ""}]
    """
    experience = []
    seen_entries = set()  # Track unique entries to avoid duplicates
    
    # Strategy 1: Find experience section by id or class
    exp_section = soup.find(['section', 'div'], {'id': re.compile(r'experience', re.I)})
    if not exp_section:
        exp_section = soup.find(['section', 'div'], {'class': re.compile(r'experience', re.I)})
    
    if exp_section:
        # Look for list items containing experience entries
        entries = exp_section.find_all('li', recursive=True, limit=20)
        
        for entry in entries:
            entry_text = entry.get_text(separator=' ', strip=True)
            
            # Look for role and company patterns
            # Pattern: "Role at Company" or "Role Company" with dates
            role_company_match = re.search(
                r'^([A-Z][a-zA-Z\s]{3,60}?)\s+(?:at|@)\s+([A-Z][a-zA-Z\s&,\.]{3,60})',
                entry_text
            )
            
            if role_company_match:
                role = role_company_match.group(1).strip()
                company = role_company_match.group(2).strip()
                
                # Clean up company name (remove trailing dates/text)
                company = re.split(r'\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4})', company)[0].strip()
                
                # Create unique key to avoid duplicates
                entry_key = f"{role.lower()}|{company.lower()}"
                if entry_key in seen_entries:
                    continue
                seen_entries.add(entry_key)
                
                # Extract dates
                dates = re.findall(
                    r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|Present',
                    entry_text,
                    re.IGNORECASE
                )
                
                start_date = dates[0] if len(dates) > 0 else ""
                end_date = dates[1] if len(dates) > 1 else ""
                
                experience.append({
                    "company": company,
                    "role": role,
                    "start_date": start_date,
                    "end_date": end_date
                })
                
                if len(experience) >= 10:  # Limit to 10 entries
                    break
    
    # Strategy 2: Fallback to visible text pattern matching
    if not experience:
        text = soup.get_text()
        
        # Look for patterns like "Software Engineer · Google · Jan 2023 - Present"
        exp_patterns = re.findall(
            r'([A-Z][a-zA-Z\s]{3,40})\s*·\s*([A-Z][a-zA-Z\s&,\.]{3,50})\s*·\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4})[^·\n]{0,30})',
            text
        )
        
        for role, company, duration in exp_patterns[:10]:
            entry_key = f"{role.lower().strip()}|{company.lower().strip()}"
            if entry_key in seen_entries:
                continue
            seen_entries.add(entry_key)
            
            dates = re.findall(
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|Present',
                duration,
                re.IGNORECASE
            )
            
            experience.append({
                "company": company.strip(),
                "role": role.strip(),
                "start_date": dates[0] if len(dates) > 0 else "",
                "end_date": dates[1] if len(dates) > 1 else ""
            })
    
    return experience


def extract_education(soup, html):
    """
    Extract education entries.
    
    Returns:
        list: [{"institution": "", "degree": "", "year": ""}]
    """
    education = []
    
    # Strategy 1: Find education section by id or class
    edu_section = soup.find(['section', 'div'], {'id': re.compile(r'education', re.I)})
    if not edu_section:
        edu_section = soup.find(['section', 'div'], {'class': re.compile(r'education', re.I)})
    
    if edu_section:
        # Look for list items or divs containing education entries
        entries = edu_section.find_all(['li', 'div'], recursive=True, limit=15)
        
        found_institutions = set()
        
        for entry in entries:
            entry_text = entry.get_text()
            
            # Look for institution names
            institution_patterns = [
                r'((?:University|Institute|College|School|Academy)[^·\n]{3,60})',
                r'([A-Z][a-zA-Z\s]+(?:University|Institute|College|School|Academy)[^·\n]{0,40})',
                r'((?:IIT|NIT|BITS|VIT|SRM|Amity|Manipal|MIT|Stanford|Harvard|Berkeley)[^·\n]{3,60})',
            ]
            
            for pattern in institution_patterns:
                matches = re.findall(pattern, entry_text)
                for match in matches:
                    institution = match.strip().rstrip('·').strip()
                    
                    if len(institution) > 5 and institution not in found_institutions:
                        found_institutions.add(institution)
                        
                        # Extract degree
                        degree_match = re.search(
                            r'(Bachelor|Master|B\.?Tech|M\.?Tech|B\.?E|M\.?E|B\.?Sc|M\.?Sc|MBA|PhD|Diploma)[^·\n]{0,60}',
                            entry_text,
                            re.IGNORECASE
                        )
                        degree = degree_match.group(0).strip()[:100] if degree_match else ""
                        
                        # Extract year
                        year_match = re.search(r'(\d{4})\s*[-–]\s*(\d{4}|Present)', entry_text)
                        year = f"{year_match.group(1)}-{year_match.group(2)}" if year_match else ""
                        
                        education.append({
                            "institution": institution,
                            "degree": degree,
                            "year": year
                        })
                        
                        if len(education) >= 5:  # Limit to 5 entries
                            break
                
                if len(education) >= 5:
                    break
            
            if len(education) >= 5:
                break
    
    # Strategy 2: Fallback to visible text pattern matching
    if not education:
        text = soup.get_text()
        
        institution_patterns = [
            r'((?:University|Institute|College|School|Academy)[^·\n]{3,60})',
            r'([A-Z][a-zA-Z\s]+(?:University|Institute|College|School|Academy))',
            r'((?:IIT|NIT|BITS|VIT|SRM|Amity|Manipal|MIT|Stanford|Harvard)[^·\n]{3,60})',
        ]
        
        found_institutions = set()
        
        for pattern in institution_patterns:
            matches = re.findall(pattern, text)
            for match in matches[:5]:
                institution = match.strip().rstrip('·').strip()
                
                if len(institution) > 5 and institution not in found_institutions:
                    found_institutions.add(institution)
                    
                    education.append({
                        "institution": institution,
                        "degree": "",
                        "year": ""
                    })
    
    return education
