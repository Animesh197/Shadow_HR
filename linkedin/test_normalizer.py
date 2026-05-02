"""
Test LinkedIn Normalizer

Verify entity normalization works correctly.
"""

from linkedin_normalizer import (
    normalize_company_name,
    normalize_institution_name,
    normalize_role_name,
    normalize_experience_list,
    normalize_education_list
)


def test_company_normalization():
    """Test company name normalization."""
    print("Testing Company Normalization:")
    print("=" * 60)
    
    test_cases = [
        ("Microsoft Corporation", "microsoft"),
        ("Microsoft India Pvt Ltd", "microsoft"),
        ("Google Inc", "google"),
        ("Google LLC", "google"),
        ("Tata Consultancy Services", "tcs"),
        ("TCS Limited", "tcs"),
        ("Amazon Web Services", "amazon"),
        ("Meta Platforms Inc", "facebook"),
        ("Infosys Limited", "infosys"),
    ]
    
    for input_name, expected in test_cases:
        result = normalize_company_name(input_name)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_name}' → '{result}' (expected: '{expected}')")
    
    print()


def test_institution_normalization():
    """Test institution name normalization."""
    print("Testing Institution Normalization:")
    print("=" * 60)
    
    test_cases = [
        ("Indian Institute of Technology Delhi", "iit delhi"),
        ("IIT Delhi", "iit delhi"),
        ("IIT-Delhi", "iit delhi"),
        ("Massachusetts Institute of Technology", "mit"),
        ("MIT", "mit"),
        ("Stanford University", "stanford"),
        ("University of California Berkeley", "berkeley"),
        ("Birla Institute of Technology and Science Pilani", "bits pilani"),
        ("BITS Pilani", "bits pilani"),
        ("Vellore Institute of Technology", "vit"),
        ("VIT", "vit"),
    ]
    
    for input_name, expected in test_cases:
        result = normalize_institution_name(input_name)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_name}' → '{result}' (expected: '{expected}')")
    
    print()


def test_role_normalization():
    """Test role name normalization."""
    print("Testing Role Normalization:")
    print("=" * 60)
    
    test_cases = [
        ("Software Development Engineer", "software engineer"),
        ("SDE", "software engineer"),
        ("Software Developer", "software engineer"),
        ("Backend Developer", "backend engineer"),
        ("Backend Dev", "backend engineer"),
        ("Frontend Engineer", "frontend engineer"),
        ("Full Stack Developer", "full stack engineer"),
        ("Data Scientist", "data scientist"),
        ("ML Engineer", "data scientist"),
        ("Intern", "intern"),
        ("Summer Intern", "intern"),
    ]
    
    for input_name, expected in test_cases:
        result = normalize_role_name(input_name)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_name}' → '{result}' (expected: '{expected}')")
    
    print()


def test_batch_normalization():
    """Test batch normalization of experience and education lists."""
    print("Testing Batch Normalization:")
    print("=" * 60)
    
    # Test experience normalization
    experience = [
        {"company": "Microsoft Corporation", "role": "Software Development Engineer"},
        {"company": "Google Inc", "role": "Backend Developer"},
    ]
    
    normalized_exp = normalize_experience_list(experience)
    print("Experience normalization:")
    for exp in normalized_exp:
        print(f"  {exp['company']} → {exp['company_normalized']}")
        print(f"  {exp['role']} → {exp['role_normalized']}")
    
    # Test education normalization
    education = [
        {"institution": "Indian Institute of Technology Delhi", "degree": "B.Tech"},
        {"institution": "Stanford University", "degree": "MS"},
    ]
    
    normalized_edu = normalize_education_list(education)
    print("\nEducation normalization:")
    for edu in normalized_edu:
        print(f"  {edu['institution']} → {edu['institution_normalized']}")
    
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LINKEDIN NORMALIZER TESTS")
    print("=" * 60 + "\n")
    
    test_company_normalization()
    test_institution_normalization()
    test_role_normalization()
    test_batch_normalization()
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
