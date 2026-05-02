"""
Test LinkedIn Matcher

Verify matching logic works correctly.
"""

from linkedin_matcher import (
    identity_matcher,
    experience_matcher,
    education_matcher,
    timeline_matcher,
    match_resume_linkedin
)


def test_identity_matcher():
    """Test identity matching."""
    print("Testing Identity Matcher:")
    print("=" * 60)
    
    test_cases = [
        ("John Doe", "John Doe", 100, True),
        ("John Doe", "John D. Doe", 90, True),
        ("John Doe", "John Smith", 0, False),
        ("Animesh Kumar Rai", "Animesh Rai", 90, True),
    ]
    
    for resume_name, linkedin_name, expected_min_score, expected_match in test_cases:
        result = identity_matcher(resume_name, linkedin_name)
        status = "✅" if result["match"] == expected_match and result["score"] >= expected_min_score else "❌"
        print(f"{status} '{resume_name}' vs '{linkedin_name}'")
        print(f"   Score: {result['score']}, Match: {result['match']}, Details: {result['details']}")
    
    print()


def test_experience_matcher():
    """Test experience matching."""
    print("Testing Experience Matcher:")
    print("=" * 60)
    
    # Test case 1: Perfect match
    resume_exp = [
        {"company": "Microsoft Corporation", "role": "Software Engineer"},
        {"company": "Google Inc", "role": "Backend Developer"}
    ]
    
    linkedin_exp = [
        {"company": "Microsoft", "role": "SDE"},
        {"company": "Google", "role": "Software Developer"}
    ]
    
    result = experience_matcher(resume_exp, linkedin_exp)
    print(f"Test 1 - Perfect match:")
    print(f"  Score: {result['score']}")
    print(f"  Matched: {result['matched_count']}/{result['total_resume_count']}")
    print(f"  Status: {'✅' if result['score'] == 100 else '❌'}")
    
    # Test case 2: Partial match
    resume_exp2 = [
        {"company": "Microsoft Corporation", "role": "Software Engineer"},
        {"company": "Amazon", "role": "Backend Developer"}
    ]
    
    linkedin_exp2 = [
        {"company": "Microsoft", "role": "SDE"}
    ]
    
    result2 = experience_matcher(resume_exp2, linkedin_exp2)
    print(f"\nTest 2 - Partial match:")
    print(f"  Score: {result2['score']}")
    print(f"  Matched: {result2['matched_count']}/{result2['total_resume_count']}")
    print(f"  Mismatches: {len(result2['mismatches'])}")
    print(f"  Status: {'✅' if result2['score'] == 50 else '❌'}")
    
    # Test case 3: No experience
    result3 = experience_matcher([], [])
    print(f"\nTest 3 - No experience:")
    print(f"  Score: {result3['score']}")
    print(f"  Status: {'✅' if result3['score'] == 100 else '❌'}")
    
    print()


def test_education_matcher():
    """Test education matching."""
    print("Testing Education Matcher:")
    print("=" * 60)
    
    # Test case 1: Perfect match
    resume_edu = [
        {"institution": "Indian Institute of Technology Delhi", "degree": "B.Tech"},
        {"institution": "Stanford University", "degree": "MS"}
    ]
    
    linkedin_edu = [
        {"institution": "IIT Delhi", "degree": "Bachelor of Technology"},
        {"institution": "Stanford", "degree": "Master of Science"}
    ]
    
    result = education_matcher(resume_edu, linkedin_edu)
    print(f"Test 1 - Perfect match:")
    print(f"  Score: {result['score']}")
    print(f"  Matched: {result['matched_count']}/{result['total_resume_count']}")
    print(f"  Status: {'✅' if result['score'] == 100 else '❌'}")
    
    # Test case 2: Partial match
    resume_edu2 = [
        {"institution": "IIT Delhi", "degree": "B.Tech"},
        {"institution": "MIT", "degree": "MS"}
    ]
    
    linkedin_edu2 = [
        {"institution": "IIT Delhi", "degree": "B.Tech"}
    ]
    
    result2 = education_matcher(resume_edu2, linkedin_edu2)
    print(f"\nTest 2 - Partial match:")
    print(f"  Score: {result2['score']}")
    print(f"  Matched: {result2['matched_count']}/{result2['total_resume_count']}")
    print(f"  Status: {'✅' if result2['score'] == 50 else '❌'}")
    
    print()


def test_timeline_matcher():
    """Test timeline matching."""
    print("Testing Timeline Matcher:")
    print("=" * 60)
    
    # Test case 1: Same count
    resume_exp = [
        {"company": "Microsoft", "role": "SDE"},
        {"company": "Google", "role": "Engineer"}
    ]
    
    linkedin_exp = [
        {"company": "Microsoft", "role": "SDE"},
        {"company": "Google", "role": "Engineer"}
    ]
    
    result = timeline_matcher(resume_exp, linkedin_exp)
    print(f"Test 1 - Same count:")
    print(f"  Score: {result['score']}")
    print(f"  Consistent: {result['consistent']}")
    print(f"  Status: {'✅' if result['score'] == 100 else '❌'}")
    
    # Test case 2: Different count
    result2 = timeline_matcher(resume_exp, [])
    print(f"\nTest 2 - Different count:")
    print(f"  Score: {result2['score']}")
    print(f"  Issues: {result2['issues']}")
    
    print()


def test_full_matching():
    """Test complete resume-LinkedIn matching."""
    print("Testing Full Matching:")
    print("=" * 60)
    
    resume_data = {
        "name": "Animesh Kumar Rai",
        "experience": [
            {"company": "Microsoft Corporation", "role": "Software Engineer"}
        ],
        "education": [
            {"institution": "Indian Institute of Technology Delhi", "degree": "B.Tech"}
        ]
    }
    
    linkedin_profile = {
        "name": "Animesh Rai",
        "experience": [
            {"company": "Microsoft", "role": "SDE"}
        ],
        "education": [
            {"institution": "IIT Delhi", "degree": "Bachelor of Technology"}
        ]
    }
    
    result = match_resume_linkedin(resume_data, linkedin_profile)
    
    print(f"Identity Score: {result['identity']['score']}")
    print(f"Experience Score: {result['experience']['score']}")
    print(f"Education Score: {result['education']['score']}")
    print(f"Timeline Score: {result['timeline']['score']}")
    print(f"\nOverall Score: {result['overall_score']}")
    print(f"Overall Match: {result['overall_match']}")
    print(f"\nStatus: {'✅' if result['overall_match'] else '❌'}")
    
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LINKEDIN MATCHER TESTS")
    print("=" * 60 + "\n")
    
    test_identity_matcher()
    test_experience_matcher()
    test_education_matcher()
    test_timeline_matcher()
    test_full_matching()
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
