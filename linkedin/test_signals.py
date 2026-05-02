"""
Test LinkedIn Signals

Verify signal generation works correctly.
"""

from linkedin_signals import (
    calculate_profile_completeness,
    generate_signals,
    get_signal_summary
)


def test_profile_completeness():
    """Test profile completeness calculation."""
    print("Testing Profile Completeness:")
    print("=" * 60)
    
    # Test 1: Complete profile
    complete_profile = {
        "name": "John Doe",
        "headline": "Software Engineer at Google",
        "location": "San Francisco, CA",
        "experience": [{"company": "Google", "role": "Engineer"}],
        "education": [{"institution": "Stanford", "degree": "BS"}]
    }
    
    result = calculate_profile_completeness(complete_profile)
    print(f"Test 1 - Complete profile:")
    print(f"  Score: {result['score']}")
    print(f"  Status: {'✅' if result['score'] == 100 else '❌'}")
    
    # Test 2: Partial profile (no experience)
    partial_profile = {
        "name": "Jane Doe",
        "headline": "Student",
        "location": "Boston, MA",
        "experience": [],
        "education": [{"institution": "MIT", "degree": "BS"}]
    }
    
    result2 = calculate_profile_completeness(partial_profile)
    print(f"\nTest 2 - Partial profile (no experience):")
    print(f"  Score: {result2['score']}")
    print(f"  Status: {'✅' if result2['score'] == 80 else '❌'}")
    
    # Test 3: Empty profile
    result3 = calculate_profile_completeness({})
    print(f"\nTest 3 - Empty profile:")
    print(f"  Score: {result3['score']}")
    print(f"  Status: {'✅' if result3['score'] == 0 else '❌'}")
    
    print()


def test_generate_signals():
    """Test signal generation."""
    print("Testing Signal Generation:")
    print("=" * 60)
    
    # Mock match results
    match_results = {
        "identity": {"score": 90},
        "experience": {"score": 100},
        "education": {"score": 100},
        "timeline": {"score": 100}
    }
    
    # Mock LinkedIn profile
    linkedin_profile = {
        "name": "John Doe",
        "headline": "Software Engineer",
        "location": "San Francisco, CA",
        "experience": [{"company": "Google", "role": "Engineer"}],
        "education": [{"institution": "Stanford", "degree": "BS"}]
    }
    
    signals = generate_signals(match_results, linkedin_profile)
    
    print(f"Identity Match: {signals['identity_match']}")
    print(f"Experience Match: {signals['experience_match']}")
    print(f"Education Match: {signals['education_match']}")
    print(f"Timeline Consistency: {signals['timeline_consistency']}")
    print(f"Profile Completeness: {signals['profile_completeness']}")
    
    # Verify all signals are present
    expected_keys = [
        'identity_match', 'experience_match', 'education_match',
        'timeline_consistency', 'profile_completeness'
    ]
    
    all_present = all(key in signals for key in expected_keys)
    print(f"\nStatus: {'✅ All signals generated' if all_present else '❌ Missing signals'}")
    
    print()


def test_signal_summary():
    """Test signal summary generation."""
    print("Testing Signal Summary:")
    print("=" * 60)
    
    signals = {
        "identity_match": 90,
        "experience_match": 100,
        "education_match": 75,
        "timeline_consistency": 85,
        "profile_completeness": 100
    }
    
    summary = get_signal_summary(signals)
    
    print("Signal Summary:")
    for signal_name, signal_data in summary.items():
        print(f"  {signal_name}: {signal_data['score']} - {signal_data['status']}")
    
    print(f"\nStatus: ✅ Summary generated")
    
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LINKEDIN SIGNALS TESTS")
    print("=" * 60 + "\n")
    
    test_profile_completeness()
    test_generate_signals()
    test_signal_summary()
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
