"""
Handles PDF processing:
- Extracts raw text from resume
- Extracts embedded links (ground truth URLs)
"""

import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)

    for page in doc:
        text += page.get_text()

    return text


def extract_links_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    links = []

    for page in doc:
        page_links = page.get_links()

        for link in page_links:
            uri = link.get("uri")
            if uri:
                links.append(uri)

    return links