def find_section_by_heading(soup, heading_text):
    for section in soup.find_all(['section', 'div']):
        texts = section.get_text(separator=" ", strip=True).lower()
        if heading_text.lower() in texts:
            return section
    return None