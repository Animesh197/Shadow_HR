"""
Section Locator

Locates profile sections in LinkedIn HTML using semantic heading detection.

Rules:
- Do NOT rely on CSS class names
- Do NOT rely on fixed DOM structure
- Use semantic heading detection
- Search for text-based section markers
- ALWAYS return valid HTML string or empty string (never None)
"""

from bs4 import BeautifulSoup
import logging

# Configure logging
logger = logging.getLogger(__name__)


def locate_sections(html):
    """
    Locate Experience, Education, About, and Header sections in LinkedIn HTML.
    
    Args:
        html (str): Raw LinkedIn profile HTML
    
    Returns:
        dict: {
            "experience_section": str (HTML) or "" (never None),
            "education_section": str (HTML) or "" (never None),
            "about_section": str (HTML) or "" (never None),
            "header_section": str (HTML) or "" (never None)
        }
    """
    if not html:
        logger.warning("[section_locator] No HTML provided")
        return {
            "experience_section": "",
            "education_section": "",
            "about_section": "",
            "header_section": ""
        }
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
    except Exception as e:
        logger.error(f"[section_locator] Failed to parse HTML: {e}")
        return {
            "experience_section": "",
            "education_section": "",
            "about_section": "",
            "header_section": ""
        }
    
    # Locate each section with defensive error handling
    experience = _locate_experience(soup)
    education = _locate_education(soup)
    about = _locate_about(soup)
    header = _locate_header(soup)
    
    # Log results
    logger.info(f"[section_locator] Experience section: {len(experience)} chars")
    logger.info(f"[section_locator] Education section: {len(education)} chars")
    logger.info(f"[section_locator] About section: {len(about)} chars")
    logger.info(f"[section_locator] Header section: {len(header)} chars")
    
    return {
        "experience_section": experience,
        "education_section": education,
        "about_section": about,
        "header_section": header
    }


def _locate_experience(soup):
    """
    Locate Experience section by finding heading containing "Experience".
    
    Returns section HTML from heading to next major section.
    Always returns str (never None).
    """
    try:
        # Find all headings (h1-h6, div with heading role, etc.)
        potential_headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        # Also check divs that might contain section headers
        potential_headings.extend(soup.find_all('div', string=lambda text: text and 'experience' in text.lower()))
        
        for heading in potential_headings:
            if not heading:
                continue
                
            heading_text = heading.get_text(strip=True).lower()
            
            # Match "Experience" heading
            if 'experience' == heading_text or heading_text.startswith('experience'):
                # Find the section container
                section = _extract_section_content(heading)
                if section:
                    section_str = str(section)
                    logger.debug(f"[section_locator] Found Experience section: {section_str[:200]}")
                    return section_str
    except Exception as e:
        logger.error(f"[section_locator] Error locating experience: {e}")
    
    return ""


def _locate_education(soup):
    """
    Locate Education section by finding heading containing "Education".
    
    Returns section HTML from heading to next major section.
    Always returns str (never None).
    """
    try:
        potential_headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        potential_headings.extend(soup.find_all('div', string=lambda text: text and 'education' in text.lower()))
        
        for heading in potential_headings:
            if not heading:
                continue
                
            heading_text = heading.get_text(strip=True).lower()
            
            # Match "Education" heading
            if 'education' == heading_text or heading_text.startswith('education'):
                section = _extract_section_content(heading)
                if section:
                    section_str = str(section)
                    logger.debug(f"[section_locator] Found Education section: {section_str[:200]}")
                    return section_str
    except Exception as e:
        logger.error(f"[section_locator] Error locating education: {e}")
    
    return ""


def _locate_about(soup):
    """
    Locate About section by finding heading containing "About".
    
    Returns section HTML from heading to next major section.
    Always returns str (never None).
    """
    try:
        potential_headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        potential_headings.extend(soup.find_all('div', string=lambda text: text and 'about' in text.lower()))
        
        for heading in potential_headings:
            if not heading:
                continue
                
            heading_text = heading.get_text(strip=True).lower()
            
            # Match "About" heading
            if 'about' == heading_text or heading_text.startswith('about'):
                section = _extract_section_content(heading)
                if section:
                    section_str = str(section)
                    logger.debug(f"[section_locator] Found About section: {section_str[:200]}")
                    return section_str
    except Exception as e:
        logger.error(f"[section_locator] Error locating about: {e}")
    
    return ""


def _locate_header(soup):
    """
    Locate profile header section (typically at top of page).
    
    Contains: name, headline, location
    Always returns str (never None).
    """
    try:
        # Strategy: Extract from <title> tag and top portion of visible content
        # Header is typically in first 20% of page
        
        # Get title tag (contains name)
        title = soup.find('title')
        title_html = str(title) if title else ""
        
        # Get first major content sections (before Experience/Education)
        # This typically contains header info
        all_text_elements = soup.find_all(['div', 'section', 'header'])
        
        # Collect elements until we hit "Experience" or "Education"
        header_elements = []
        for elem in all_text_elements[:50]:  # First 50 elements only
            if not elem:
                continue
                
            try:
                elem_text = elem.get_text(strip=True).lower()
                
                # Stop if we hit major sections
                if elem_text in ['experience', 'education', 'about']:
                    break
                
                # Include elements that likely contain header info
                if len(elem_text) > 0 and len(elem_text) < 500:
                    header_elements.append(str(elem))
            except Exception as e:
                logger.debug(f"[section_locator] Error processing header element: {e}")
                continue
        
        header_html = title_html + "\n" + "\n".join(header_elements[:10])  # First 10 elements
        logger.debug(f"[section_locator] Found Header section: {header_html[:200]}")
        return header_html
    except Exception as e:
        logger.error(f"[section_locator] Error locating header: {e}")
        return ""


def _extract_section_content(heading):
    """
    Extract section content starting from a heading element.
    
    Strategy:
    1. Start from heading
    2. Collect sibling elements until next major heading
    3. Or collect parent's content if heading is within container
    
    Returns:
        BeautifulSoup object or None (caller converts to str or "")
    """
    try:
        if not heading:
            return None
        
        # Try to find parent container
        parent = heading.find_parent(['section', 'div'])
        
        if parent:
            # Check if parent looks like a section container
            try:
                parent_text = parent.get_text(strip=True)
                if len(parent_text) > 50:  # Has substantial content
                    return parent
            except Exception as e:
                logger.debug(f"[section_locator] Error checking parent text: {e}")
        
        # Fallback: collect siblings
        siblings = []
        try:
            for sibling in heading.find_next_siblings():
                if not sibling:
                    continue
                
                try:
                    sibling_text = sibling.get_text(strip=True).lower()
                    
                    # Stop if we hit another major section heading
                    if sibling_text in ['experience', 'education', 'about', 'skills', 'licenses & certifications']:
                        break
                    
                    siblings.append(str(sibling))
                    
                    # Stop after collecting reasonable amount
                    if len(siblings) > 20:
                        break
                except Exception as e:
                    logger.debug(f"[section_locator] Error processing sibling: {e}")
                    continue
        except Exception as e:
            logger.debug(f"[section_locator] Error iterating siblings: {e}")
        
        if siblings:
            combined = str(heading) + "\n" + "\n".join(siblings)
            # Create a wrapper div
            return BeautifulSoup(combined, 'html.parser')
    
    except Exception as e:
        logger.error(f"[section_locator] Error extracting section content: {e}")
    
    return None
