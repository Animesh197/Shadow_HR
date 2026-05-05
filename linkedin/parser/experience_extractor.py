import re
from .filters import is_noise, clean_text, is_valid_text

def extract_experience(soup):
    from .section_finder import find_section_by_heading

    experience = []
    seen = set()

    section = find_section_by_heading(soup, "experience")
    if not section:
        return []

    items = section.find_all(['li', 'div'])

    for item in items:
        text = item.get_text(" ", strip=True)

        if is_noise(text):
            continue

        lines = [clean_text(l) for l in text.split('\n') if l.strip()]

        role, company = "", ""

        # Heuristic: first line = role, second = company
        if len(lines) >= 2:
            role = lines[0]
            company = lines[1]

        if not (is_valid_text(role) and is_valid_text(company)):
            continue

        key = f"{role.lower()}|{company.lower()}"
        if key in seen:
            continue
        seen.add(key)

        # Extract dates
        date_match = re.findall(
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|Present',
            text,
            re.IGNORECASE
        )

        experience.append({
            "role": role,
            "company": company,
            "start_date": date_match[0] if len(date_match) > 0 else "",
            "end_date": date_match[1] if len(date_match) > 1 else ""
        })

        if len(experience) >= 10:
            break

    return experience