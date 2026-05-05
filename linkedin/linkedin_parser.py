from bs4 import BeautifulSoup
import re

from linkedin.parser.experience_extractor import extract_experience
from linkedin.parser.education_extractor import extract_education
from linkedin.parser.fallback_extractor import fallback_experience, fallback_education


def parse_linkedin_profile(html):
    if not html:
        return empty_profile()

    soup = BeautifulSoup(html, "html.parser")
    visible_text = soup.get_text(separator='|', strip=True)

    name = extract_name(soup)
    headline = extract_headline(visible_text, name)
    location = extract_location(visible_text)

    experience = extract_experience(soup)
    education = extract_education(soup)

    # Fallbacks
    if not experience:
        experience = fallback_experience(visible_text)

    if not education:
        education = fallback_education(visible_text)

    return {
        "name": name,
        "headline": headline,
        "location": location,
        "experience": experience,
        "education": education
    }


def extract_name(soup):
    title = soup.title.string if soup.title else ""
    return title.split('|')[0].strip() if '|' in title else ""


def extract_headline(visible_text, name):
    lines = visible_text.split('|')
    for i, line in enumerate(lines):
        if name in line:
            for j in range(i+1, i+5):
                if j < len(lines) and 30 < len(lines[j]) < 300:
                    return lines[j]
    return ""




def extract_location(visible_text):
    lines = visible_text.split('|')

    for line in lines:
        line = line.strip()

        # Must match real location pattern
        if re.match(r'^[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]+(?:,\s*[A-Z][a-zA-Z\s]+)?$', line):
            
            # Reject if looks like headline
            if any(k in line.lower() for k in ['ai', 'ml', 'engineer', 'building', 'developer']):
                continue
            
            return line

    return ""


def empty_profile():
    return {
        "name": "",
        "headline": "",
        "location": "",
        "experience": [],
        "education": []
    }