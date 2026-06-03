"""
Section Extractor

Converts HTML sections into clean text, removing noise.

Removes:
- Suggested profiles
- People also viewed
- Posts
- Comments
- Reactions
- Connections
- Followers
- Hashtags
- Recommendations
"""

from bs4 import BeautifulSoup, Tag
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)


# Noise patterns to filter out
NOISE_PATTERNS = [
    # Social features
    r'people also viewed',
    r'suggested profiles?',
    r'view profile',
    r'follow',
    r'connect',
    r'\d+ connections?',
    r'\d+ followers?',
    r'\d+ following',
    
    # Activity feed
    r'liked this',
    r'commented on',
    r'shared this',
    r'reacted to',
    r'posted this',
    
    # Recommendations
    r'recommendations?',
    r'endorsed',
    r'skills? & endorsements?',
    
    # UI elements
    r'see more',
    r'show more',
    r'show less',
    r'view all',
    r'collapse',
    r'expand',
    
    # Hashtags
    r'#\w+',
]


def extract_section_text(sections):
    """
    Convert HTML sections into clean text.
    
    Args:
        sections (dict): Output from locate_sections()
    
    Returns:
        dict: {
            "experience_text": str,
            "education_text": str,
            "about_text": str,
            "header_text": str
        }
    """
    # Defensive: ensure sections is a dict
    if not isinstance(sections, dict):
        logger.error(f"[section_extractor] Invalid sections type: {type(sections)}")
        return {
            "experience_text": "",
            "education_text": "",
            "about_text": "",
            "header_text": ""
        }
    
    # Extract each section with error handling
    experience_text = _clean_section_html(sections.get("experience_section", ""))
    education_text = _clean_section_html(sections.get("education_section", ""))
    about_text = _clean_section_html(sections.get("about_section", ""))
    header_text = _clean_section_html(sections.get("header_section", ""))
    
    # Log results
    logger.info(f"[section_extractor] Experience text: {len(experience_text)} chars")
    logger.info(f"[section_extractor] Education text: {len(education_text)} chars")
    logger.info(f"[section_extractor] About text: {len(about_text)} chars")
    logger.info(f"[section_extractor] Header text: {len(header_text)} chars")
    
    return {
        "experience_text": experience_text,
        "education_text": education_text,
        "about_text": about_text,
        "header_text": header_text
    }


def _clean_section_html(html):
    """
    Convert section HTML to clean text with noise removed.
    
    Args:
        html (str, BeautifulSoup, or None): Section HTML
    
    Returns:
        str: Clean text (never None)
    """
    # Defensive: handle None
    if html is None:
        logger.debug("[section_extractor] Received None HTML")
        return ""
    
    # Defensive: handle empty string
    if not html:
        logger.debug("[section_extractor] Received empty HTML")
        return ""
    
    # Log input type and sample
    logger.debug(f"[section_extractor] Input type: {type(html)}")
    if isinstance(html, str):
        logger.debug(f"[section_extractor] Input sample: {html[:200]}")
    
    try:
        # Handle BeautifulSoup objects
        if isinstance(html, BeautifulSoup):
            soup = html
        # Handle Tag objects
        elif isinstance(html, Tag):
            soup = BeautifulSoup(str(html), 'html.parser')
        # Handle strings
        elif isinstance(html, str):
            soup = BeautifulSoup(html, 'html.parser')
        else:
            logger.warning(f"[section_extractor] Unexpected HTML type: {type(html)}")
            return ""
        
        # Remove script and style tags
        for tag in soup.find_all(['script', 'style']):
            try:
                tag.decompose()
            except Exception as e:
                logger.debug(f"[section_extractor] Error removing script/style: {e}")
        
        # Remove elements with noise-indicating attributes
        for tag in soup.find_all(True):
            try:
                # Defensive: check if tag is valid and has get method
                if not tag or not hasattr(tag, 'get'):
                    continue
                
                # Remove elements with aria-label suggesting noise
                aria_label = tag.get('aria-label', '')
                if aria_label and isinstance(aria_label, str):
                    aria_label_lower = aria_label.lower()
                    if any(pattern in aria_label_lower for pattern in ['follow', 'connect', 'message', 'more actions']):
                        tag.decompose()
                        continue
                
                # Remove elements with class names suggesting social features
                classes = tag.get('class', [])
                if classes:
                    # Handle both list and string classes
                    if isinstance(classes, list):
                        classes_str = ' '.join(classes).lower()
                    elif isinstance(classes, str):
                        classes_str = classes.lower()
                    else:
                        classes_str = ""
                    
                    if any(word in classes_str for word in ['follow', 'connect', 'reaction', 'comment', 'share', 'social']):
                        tag.decompose()
                        continue
            except Exception as e:
                logger.debug(f"[section_extractor] Error processing tag attributes: {e}")
                continue
        
        # Get text with separators
        try:
            text = soup.get_text(separator='|', strip=True)
        except Exception as e:
            logger.error(f"[section_extractor] Error getting text: {e}")
            return ""
        
        # Split into lines
        lines = text.split('|')
        
        # Filter lines
        clean_lines = []
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip very short lines (likely UI elements)
            if len(line) < 3:
                continue
            
            # Skip lines matching noise patterns
            if _is_noise_line(line):
                continue
            
            # Skip lines with only numbers (likely counters)
            if line.isdigit():
                continue
            
            clean_lines.append(line)
        
        # Join with newlines
        clean_text = '\n'.join(clean_lines)
        
        logger.debug(f"[section_extractor] Extracted {len(clean_text)} chars of clean text")
        
        return clean_text
        
    except Exception as e:
        logger.error(f"[section_extractor] Error cleaning section HTML: {e}")
        return ""


def _is_noise_line(line):
    """
    Check if a line matches noise patterns.
    
    Args:
        line (str): Line of text
    
    Returns:
        bool: True if line is noise
    """
    line_lower = line.lower()
    
    # Check against noise patterns
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, line_lower):
            return True
    
    # Check for specific noise indicators
    noise_phrases = [
        'people also viewed',
        'suggested profile',
        'view profile',
        'someone at',
        'big thanks',
        'grateful for',
        'excited to announce',
        'happy to share',
        'liked by',
        'and others',
    ]
    
    for phrase in noise_phrases:
        if phrase in line_lower:
            return True
    
    # Check for hashtag-only lines
    if line.startswith('#'):
        return True
    
    return False
