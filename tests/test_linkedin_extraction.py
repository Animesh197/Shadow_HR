"""
LinkedIn Extraction Tests

Tests for the new LLM-based LinkedIn extraction system.

Test Profiles:
- Fresher profile
- Student profile
- Experienced profile
- Noisy profile (with activity feed, recommendations)
- Profile with suggested profiles
"""

from linkedin.linkedin_profile_extractor import extract_linkedin_profile


def test_no_noise_in_education():
    """
    Education must never contain:
    - hashtags
    - "thanks"
    - suggested profiles
    - people also viewed
    - activity feed content
    """
    # This would be a real HTML sample
    sample_html = """
    <html>
        <title>John Doe | LinkedIn</title>
        <body>
            <div>
                <h2>Education</h2>
                <div>
                    Indian Institute of Technology Patna
                </div>
                <div>
                    Bachelor of Technology in Computer Science
                </div>
                <div>2020 - 2024</div>
                <div>#NewtonSchool</div>
                <div>Big thanks to my professors</div>
                <div>People also viewed: Jane Smith</div>
            </div>
        </body>
    </html>
    """
    
    profile = extract_linkedin_profile(sample_html)
    
    # Check education
    for edu in profile["education"]:
        institution = edu["institution"].lower()
        degree = edu["degree"].lower()
        
        # Must not contain noise
        assert '#' not in institution, f"Education contains hashtag: {institution}"
        assert 'thanks' not in institution, f"Education contains 'thanks': {institution}"
        assert 'people also viewed' not in institution, f"Education contains 'people also viewed': {institution}"
        assert '#' not in degree, f"Degree contains hashtag: {degree}"
    
    print("✅ test_no_noise_in_education passed")


def test_no_noise_in_experience():
    """
    Experience must never contain:
    - followers
    - connections
    - comments
    - recommendations
    """
    sample_html = """
    <html>
        <title>Jane Smith | LinkedIn</title>
        <body>
            <div>
                <h2>Experience</h2>
                <div>
                    Software Engineer at Google
                </div>
                <div>Jan 2023 - Present</div>
                <div>1000 followers</div>
                <div>500+ connections</div>
                <div>Recommended by 5 people</div>
            </div>
        </body>
    </html>
    """
    
    profile = extract_linkedin_profile(sample_html)
    
    # Check experience
    for exp in profile["experience"]:
        company = exp["company"].lower()
        role = exp["role"].lower()
        
        # Must not contain noise
        assert 'followers' not in company, f"Company contains 'followers': {company}"
        assert 'connections' not in company, f"Company contains 'connections': {company}"
        assert 'recommend' not in company, f"Company contains 'recommend': {company}"
        assert 'followers' not in role, f"Role contains 'followers': {role}"
    
    print("✅ test_no_noise_in_experience passed")


def test_location_not_headline():
    """
    Location must never equal headline.
    They should be distinct fields.
    """
    sample_html = """
    <html>
        <title>Bob Johnson | LinkedIn</title>
        <body>
            <div>Software Engineer specializing in AI</div>
            <div>San Francisco, California, United States</div>
        </body>
    </html>
    """
    
    profile = extract_linkedin_profile(sample_html)
    
    headline = profile["headline"]
    location = profile["location"]
    
    # Must be different
    assert headline != location, f"Headline equals location: {headline}"
    
    # Location should look like a location (has comma)
    if location:
        assert ',' in location or len(location.split()) == 1, f"Location doesn't look like location: {location}"
    
    print("✅ test_location_not_headline passed")


def test_confidence_scores():
    """
    Test that confidence scores are generated correctly.
    """
    sample_html = """
    <html>
        <title>Alice Wong | LinkedIn</title>
        <body>
            <h2>Experience</h2>
            <div>Senior Engineer at Microsoft</div>
            <div>Jan 2020 - Present</div>
            
            <h2>Education</h2>
            <div>Stanford University</div>
            <div>Master of Science in Computer Science</div>
            <div>2018</div>
        </body>
    </html>
    """
    
    profile = extract_linkedin_profile(sample_html)
    
    # Check confidence exists
    assert "confidence" in profile, "Confidence scores missing"
    
    confidence = profile["confidence"]
    assert "overall_confidence" in confidence
    assert "experience_confidence" in confidence
    assert "education_confidence" in confidence
    assert "headline_confidence" in confidence
    assert "location_confidence" in confidence
    
    # All scores should be 0-100
    for key, value in confidence.items():
        assert 0 <= value <= 100, f"Confidence score out of range: {key}={value}"
    
    print("✅ test_confidence_scores passed")
    print(f"   Overall confidence: {confidence['overall_confidence']}%")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("RUNNING LINKEDIN EXTRACTION TESTS")
    print("="*60 + "\n")
    
    try:
        test_no_noise_in_education()
        test_no_noise_in_experience()
        test_location_not_headline()
        test_confidence_scores()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60 + "\n")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()
