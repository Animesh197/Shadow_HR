"""
Test LinkedIn Parser V2 Fixes

Tests the improved validation and filtering logic.
"""

from linkedin_parser import (
    is_ui_element,
    is_achievement_or_award,
    is_experience_entry,
    is_valid_institution,
    clean_institution_name,
    normalize_experience_entry
)


def test_ui_element_detection():
    """Test UI element detection"""
    print("\n=== Testing UI Element Detection ===")
    
    test_cases = [
        ("Message", True),
        ("Connect", True),
        ("Follow", True),
        ("View profile", True),
        ("500+ connections", True),
        ("Indian Institute of Technology", False),
        ("Software Engineer at Google", False),
    ]
    
    for text, expected in test_cases:
        result = is_ui_element(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> {result} (expected {expected})")


def test_achievement_detection():
    """Test achievement/award detection"""
    print("\n=== Testing Achievement Detection ===")
    
    test_cases = [
        ("NIRMAAN 2025 – 2nd Place Winner (Delhi University)", True),
        ("Winner of Hackathon 2024", True),
        ("AWS Certified Solutions Architect", True),
        ("Indian Institute of Technology, Patna", False),
        ("Software Engineer at Google", False),
    ]
    
    for text, expected in test_cases:
        result = is_achievement_or_award(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> {result} (expected {expected})")


def test_experience_detection():
    """Test experience entry detection"""
    print("\n=== Testing Experience Detection ===")
    
    test_cases = [
        ("Product @ Meesho • IIT Kanpur • AIRBUS", True),
        ("Software Engineer at Google", True),
        ("Backend Developer · Microsoft", True),
        ("Data Scientist • Amazon", True),
        ("Indian Institute of Technology, Patna", False),
        ("Bachelor of Technology in Computer Science", False),
        ("Message", False),
    ]
    
    for text, expected in test_cases:
        result = is_experience_entry(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> {result} (expected {expected})")


def test_institution_validation():
    """Test institution validation"""
    print("\n=== Testing Institution Validation ===")
    
    test_cases = [
        ("Indian Institute of Technology, Patna", True),
        ("Newton School of Technology", True),
        ("Stanford University", True),
        ("The StackMentalist · Indian Institute of Technology, Patna", False),  # Project
        ("Product @ Meesho • IIT Kanpur • AIRBUS", False),  # Experience
        ("NIRMAAN 2025 – 2nd Place Winner (Delhi University)", False),  # Achievement
        ("Message", False),  # UI element
        ("IIT", False),  # Too short
    ]
    
    for text, expected in test_cases:
        result = is_valid_institution(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> {result} (expected {expected})")


def test_institution_cleaning():
    """Test institution name cleaning"""
    print("\n=== Testing Institution Name Cleaning ===")
    
    test_cases = [
        ("· Indian Institute of Technology, Patna", "Indian Institute of Technology, Patna"),
        ("• Stanford University", "Stanford University"),
        ("The StackMentalist · IIT Patna", "IIT Patna"),
        ("Newton School of Technology", "Newton School of Technology"),
    ]
    
    for text, expected in test_cases:
        result = clean_institution_name(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> '{result}' (expected '{expected}')")


def test_experience_normalization():
    """Test experience entry normalization"""
    print("\n=== Testing Experience Normalization ===")
    
    test_cases = [
        ("Product @ Meesho • IIT Kanpur • AIRBUS", "Product", "Meesho"),
        ("Software Engineer at Google", "Software Engineer", "Google"),
        ("Backend Developer · Microsoft", "Backend Developer", "Microsoft"),
        ("Data Scientist • Amazon", "Data Scientist", "Amazon"),
    ]
    
    for text, expected_role, expected_company in test_cases:
        result = normalize_experience_entry(text)
        role_match = result['role'] == expected_role
        company_match = result['company'] == expected_company
        status = "✅" if role_match and company_match else "❌"
        print(f"{status} '{text}'")
        print(f"   -> Role: '{result['role']}' (expected '{expected_role}')")
        print(f"   -> Company: '{result['company']}' (expected '{expected_company}')")


if __name__ == "__main__":
    print("="*70)
    print("LinkedIn Parser V2 - Validation Tests")
    print("="*70)
    
    test_ui_element_detection()
    test_achievement_detection()
    test_experience_detection()
    test_institution_validation()
    test_institution_cleaning()
    test_experience_normalization()
    
    print("\n" + "="*70)
    print("Tests Complete!")
    print("="*70)
