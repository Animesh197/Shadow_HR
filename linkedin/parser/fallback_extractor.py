import re
from .filters import clean_text

def fallback_experience(visible_text):
    results = []

    lines = [clean_text(l) for l in visible_text.split('|') if l.strip()]

    for line in lines:
        if ' at ' in line.lower():
            parts = line.split(' at ')
            if len(parts) == 2:
                results.append({
                    "role": parts[0],
                    "company": parts[1],
                    "start_date": "",
                    "end_date": ""
                })

        if len(results) >= 5:
            break

    return results


def fallback_education(visible_text):
    results = []

    keywords = ['university', 'institute', 'college', 'school', 'iit', 'nit']

    lines = [clean_text(l) for l in visible_text.split('|') if l.strip()]

    for line in lines:
        if any(k in line.lower() for k in keywords):
            results.append({
                "institution": line,
                "degree": "",
                "year": ""
            })

        if len(results) >= 5:
            break

    return results