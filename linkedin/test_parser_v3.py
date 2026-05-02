"""
Test LinkedIn Parser V3 Fixes

Tests the new helper functions for experience and education extraction.
"""

from linkedin_parser import (
    # V3 Experience helpers
    is_role_line,
    has_company_info,
    extract_company_from_line,
    # V3 Education helpers
    is_minor_or_certificate,
    is_online_course,
    extract_institution_base_name,
    is_full_degree
)


def test_role_detection():
    """Test role line detection"""
    print("\n=== Testing Role Line Detection ===")
    
    test_cases = [
        ("Assistant Software Developer", True),
        ("Software Developer", True),
        ("Cybersecurity Analyst Intern", True),
        ("The StackMentalist · Internship", False),  # Has separator
        ("Jun 2025 - Aug 2025", False),  # Date line
        ("Pune District, Maharashtra, India", False),  # Location
        ("Message", False),  # UI element
    ]
    
    for text, expected in test_cases:
        result = is_role_line(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> {result} (expected {expected})")


def test_company_info_detection():
    """Test company info line detection"""
    print("\n=== Testing Company Info Detection ===")
    
    test_cases = [
        ("The StackMentalist · Internship", True),
        ("Plugseal Innovation Services Private Limited · Internship", True),
        ("Tata Group · Internship", True),
        ("Assistant Software Developer", False),  # No separator
        ("Jun 2025 - Aug 2025", False),  # Date line
    ]
    
    for text, expected in test_cases:
        result = has_company_info(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> {result} (expected {expected})")


def test_company_extraction():
    """Test company name extraction"""
    print("\n=== Testing Company Extraction ===")
    
    test_cases = [
        ("The StackMentalist · Internship", "The StackMentalist"),
        ("Plugseal Innovation Services Private Limited · Internship", "Plugseal Innovation Services Private Limited"),
        ("Tata Group · Internship", "Tata Group"),
        ("Product @ Meesho • IIT Kanpur • AIRBUS", "Product @ Meesho"),  # Takes first part
    ]
    
    for text, expected in test_cases:
        result = extract_company_from_line(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}'")
        print(f"   -> '{result}' (expected '{expected}')")


def test_minor_certificate_detection():
    """Test minor/certificate detection"""
    print("\n=== Testing Minor/Certificate Detection ===")
    
    test_cases = [
        ("Minor in AI by IIT Ropar", True),
        ("Indian Institute of Technology, Ropar - Minor in AI", True),
        ("AWS Certified Solutions Architect", True),
        ("Certificate in Data Science", True),
        ("Indian Institute of Technology, Patna", False),
        ("Bachelor of Technology", False),
    ]
    
    for text, expected in test_cases:
        result = is_minor_or_certificate(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> {result} (expected {expected})")


def test_online_course_detection():
    """Test online course detection"""
    print("\n=== Testing Online Course Detection ===")
    
    test_cases = [
        ("CS50 - Online Course", True),
        ("Coursera Machine Learning", True),
        ("edX Python Programming", True),
        ("Indian Institute of Technology, Patna", False),
        ("Bachelor of Technology", False),
    ]
    
    for text, expected in test_cases:
        result = is_online_course(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> {result} (expected {expected})")


def test_institution_base_name_extraction():
    """Test institution base name extraction"""
    print("\n=== Testing Institution Base Name Extraction ===")
    
    test_cases = [
        ("Indian Institute of Technology, Patna - BS, Computer Science", "Indian Institute of Technology, Patna"),
        ("Indian Institute of Technology, Patna", "Indian Institute of Technology, Patna"),
        ("BS-MS ID at IIT Patna", "IIT Patna"),
        ("Newton School of Technology", "Newton School of Technology"),
    ]
    
    for text, expected in test_cases:
        result = extract_institution_base_name(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}'")
        print(f"   -> '{result}' (expected '{expected}')")


def test_full_degree_validation():
    """Test full degree validation"""
    print("\n=== Testing Full Degree Validation ===")
    
    test_cases = [
        ("Bachelor of Technology", True),
        ("Master of Science", True),
        ("B.Tech in Computer Science", True),
        ("BS in Computer Science", True),
        ("MBA", True),
        ("PhD in AI", True),
        ("Minor in AI", False),
        ("Certificate in Data Science", False),
        ("", False),
    ]
    
    for text, expected in test_cases:
        result = is_full_degree(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> {result} (expected {expected})")


if __name__ == "__main__":
    print("="*70)
    print("LinkedIn Parser V3 - Validation Tests")
    print("="*70)
    
    test_role_detection()
    test_company_info_detection()
    test_company_extraction()
    test_minor_certificate_detection()
    test_online_course_detection()
    test_institution_base_name_extraction()
    test_full_degree_validation()
    
    print("\n" + "="*70)
    print("Tests Complete!")
    print("="*70)
