from .filters import is_noise, clean_text, is_valid_text

INSTITUTION_KEYWORDS = [
    'university', 'institute', 'college', 'school',
    'iit', 'nit', 'bits', 'vit', 'srm', 'amity'
]

def extract_education(soup):
    from .section_finder import find_section_by_heading

    education = []
    seen = set()

    section = find_section_by_heading(soup, "education")
    if not section:
        return []

    items = section.find_all(['li', 'div'])

    for item in items:
        text = item.get_text(" ", strip=True)

        if is_noise(text):
            continue

        if not any(k in text.lower() for k in INSTITUTION_KEYWORDS):
            continue

        lines = [clean_text(l) for l in text.split('\n') if l.strip()]

        institution = lines[0] if lines else ""

        if not is_valid_text(institution):
            continue

        key = institution.lower()
        if key in seen:
            continue
        seen.add(key)

        degree = lines[1] if len(lines) > 1 else ""
        year = ""

        education.append({
            "institution": institution,
            "degree": degree,
            "year": year
        })

        if len(education) >= 5:
            break

    return education