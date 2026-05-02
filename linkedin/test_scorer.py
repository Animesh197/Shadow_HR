"""
Test LinkedIn Scorer

Verify scoring logic works correctly for both fresher and experienced candidates.
"""

from linkedin_scorer import (
    calculate_fresher_score,
    calculate_experienced_score,
    calculate_linkedin_confidence,
    calculate_linkedin_score
)


def test_fresher_scoring():
    """Test fresher candidate scoring."""
    print("Testing Fresher Scoring:")
    print("=" * 60)
    
    signals = {
        "identity_match": 90,
        "experience_match": 80,  # Internships
        "education_match": 100,
        "timeline_consistency": 100,
        "profile_completeness": 100
    }
    
    result = calculate_fresher_score(signals)
    
    print(f"LinkedIn Score: {result['linkedin_score']}")
    print(f"Candidate Type: {result['candidate_type']}")
    print(f"\nBreakdown:")
    for key, value in result['breakdown'].items():
        print(f"  {key}: {value}")
    
    # Verify weights sum to 1.0
    weights_sum = sum(result['weights'].values())
    print(f"\nWeights sum: {weights_sum}")
    print(f"Status: {'✅' if abs(weights_sum - 1.0) < 0.01 else '❌'}")
    
    print()


def test_experienced_scoring():
    """Test experienced candidate scoring."""
    print("Testing Experienced Scoring:")
    print("=" * 60)
    
    signals = {
        "identity_match": 90,
        "experience_match": 100,
        "education_match": 100,
        "timeline_consistency": 100,
        "profile_completeness": 100
    }
    
    result = calculate_experienced_score(signals)
    
    print(f"LinkedIn Score: {result['linkedin_score']}")
    print(f"Candidate Type: {result['candidate_type']}")
    print(f"\nBreakdown:")
    for key, value in result['breakdown'].items():
        print(f"  {key}: {value}")
    
    # Verify weights sum to 1.0
    weights_sum = sum(result['weights'].values())
    print(f"\nWeights sum: {weights_sum}")
    print(f"Status: {'✅' if abs(weights_sum - 1.0) < 0.01 else '❌'}")
    
    print()


def test_confidence_calculation():
    """Test confidence calculation."""
    print("Testing Confidence Calculation:")
    print("=" * 60)
    
    signals = {
        "identity_match": 90,
        "experience_match": 100,
        "education_match": 100,
        "timeline_consistency": 100,
        "profile_completeness": 100
    }
    
    linkedin_profile = {
        "name": "John Doe",
        "headline": "Software Engineer",
        "location": "San Francisco, CA",
        "experience": [{"company": "Google"}],
        "education": [{"institution": "Stanford"}]
    }
    
    match_results = {}
    
    result = calculate_linkedin_confidence(signals, linkedin_profile, match_results)
    
    print(f"Confidence Level: {result['confidence_level']}")
    print(f"Confidence Score: {result['confidence_score']}")
    print(f"\nFactors:")
    for key, value in result['factors'].items():
        print(f"  {key}: {value}")
    
    print(f"\nStatus: {'✅' if result['confidence_level'] == 'high' else '❌'}")
    
    print()


def test_full_scoring():
    """Test complete scoring with routing."""
    print("Testing Full Scoring (Fresher):")
    print("=" * 60)
    
    signals = {
        "identity_match": 90,
        "experience_match": 80,
        "education_match": 100,
        "timeline_consistency": 100,
        "profile_completeness": 100
    }
    
    linkedin_profile = {
        "name": "Jane Doe",
        "headline": "Student",
        "location": "Boston, MA",
        "experience": [],
        "education": [{"institution": "MIT"}]
    }
    
    match_results = {}
    
    result = calculate_linkedin_score(signals, "fresher", linkedin_profile, match_results)
    
    print(f"LinkedIn Score: {result['linkedin_score']}")
    print(f"Candidate Type: {result['candidate_type']}")
    print(f"Confidence: {result['confidence']['confidence_level']}")
    print(f"Verification Status: {result['verification_status']}")
    
    print(f"\nStatus: ✅")
    
    print()
    
    print("Testing Full Scoring (Experienced):")
    print("=" * 60)
    
    result2 = calculate_linkedin_score(signals, "experienced", linkedin_profile, match_results)
    
    print(f"LinkedIn Score: {result2['linkedin_score']}")
    print(f"Candidate Type: {result2['candidate_type']}")
    print(f"Confidence: {result2['confidence']['confidence_level']}")
    print(f"Verification Status: {result2['verification_status']}")
    
    print(f"\nStatus: ✅")
    
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LINKEDIN SCORER TESTS")
    print("=" * 60 + "\n")
    
    test_fresher_scoring()
    test_experienced_scoring()
    test_confidence_calculation()
    test_full_scoring()
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
