"""
Test script to verify section extraction fixes.

Tests:
1. None handling
2. Empty string handling
3. Malformed HTML handling
4. BeautifulSoup object handling
5. Missing attributes handling
"""

import sys


def test_none_handling():
    """Test that None inputs don't cause AttributeError."""
    print("\n" + "="*70)
    print("TEST 1: None Handling")
    print("="*70)
    
    from linkedin.parsers.section_locator import locate_sections
    from linkedin.parsers.section_extractor import extract_section_text
    
    # Test None HTML
    sections = locate_sections(None)
    assert isinstance(sections, dict), "locate_sections should return dict"
    assert sections["experience_section"] == "", "Should return empty string for None"
    assert sections["education_section"] == "", "Should return empty string for None"
    print("✅ None HTML handled correctly")
    
    # Test extraction with empty sections
    texts = extract_section_text(sections)
    assert isinstance(texts, dict), "extract_section_text should return dict"
    assert texts["experience_text"] == "", "Should return empty string"
    print("✅ Empty sections handled correctly")


def test_empty_string_handling():
    """Test that empty strings don't cause errors."""
    print("\n" + "="*70)
    print("TEST 2: Empty String Handling")
    print("="*70)
    
    from linkedin.parsers.section_locator import locate_sections
    from linkedin.parsers.section_extractor import extract_section_text
    
    # Test empty string
    sections = locate_sections("")
    assert sections["experience_section"] == "", "Should handle empty string"
    print("✅ Empty string HTML handled correctly")
    
    # Test extraction with empty sections
    texts = extract_section_text(sections)
    assert texts["experience_text"] == "", "Should return empty string"
    print("✅ Empty string extraction handled correctly")


def test_malformed_html():
    """Test that malformed HTML doesn't crash."""
    print("\n" + "="*70)
    print("TEST 3: Malformed HTML Handling")
    print("="*70)
    
    from linkedin.parsers.section_locator import locate_sections
    from linkedin.parsers.section_extractor import extract_section_text
    
    # Malformed HTML
    malformed = "<div><h2>Experience</h2><p>Test<div>"  # Missing closing tags
    
    try:
        sections = locate_sections(malformed)
        assert isinstance(sections, dict), "Should return dict even with malformed HTML"
        print("✅ Malformed HTML handled without crash")
        
        texts = extract_section_text(sections)
        assert isinstance(texts, dict), "Should extract text without crash"
        print("✅ Malformed HTML extraction handled")
    except Exception as e:
        print(f"❌ Malformed HTML caused error: {e}")
        return False
    
    return True


def test_missing_attributes():
    """Test HTML with elements missing attributes."""
    print("\n" + "="*70)
    print("TEST 4: Missing Attributes Handling")
    print("="*70)
    
    from linkedin.parsers.section_extractor import _clean_section_html
    
    # HTML with elements that might not have get() method
    html = """
    <html>
        <head><title>Test</title></head>
        <body>
            <div>
                <h2>Experience</h2>
                <div>Software Engineer</div>
            </div>
        </body>
    </html>
    """
    
    try:
        result = _clean_section_html(html)
        assert isinstance(result, str), "Should return string"
        print(f"✅ Missing attributes handled, extracted {len(result)} chars")
    except AttributeError as e:
        print(f"❌ AttributeError occurred: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True


def test_beautifulsoup_object():
    """Test passing BeautifulSoup objects."""
    print("\n" + "="*70)
    print("TEST 5: BeautifulSoup Object Handling")
    print("="*70)
    
    from bs4 import BeautifulSoup
    from linkedin.parsers.section_extractor import _clean_section_html
    
    html = "<div><h2>Test</h2><p>Content</p></div>"
    soup = BeautifulSoup(html, 'html.parser')
    
    try:
        result = _clean_section_html(soup)
        assert isinstance(result, str), "Should convert BeautifulSoup to string"
        print(f"✅ BeautifulSoup object handled, extracted {len(result)} chars")
    except Exception as e:
        print(f"❌ Error handling BeautifulSoup object: {e}")
        return False
    
    return True


def test_real_world_scenario():
    """Test with realistic LinkedIn HTML."""
    print("\n" + "="*70)
    print("TEST 6: Real World Scenario")
    print("="*70)
    
    from linkedin.parsers.section_locator import locate_sections
    from linkedin.parsers.section_extractor import extract_section_text
    
    # Realistic LinkedIn-like HTML
    html = """
    <html>
        <head><title>John Doe | LinkedIn</title></head>
        <body>
            <div class="header">
                <h1>John Doe</h1>
                <div>Software Engineer</div>
                <div>San Francisco, CA</div>
            </div>
            <div class="profile-section">
                <h2>Experience</h2>
                <div>
                    <div>Senior Engineer</div>
                    <div>Google</div>
                    <div>Jan 2020 - Present</div>
                </div>
            </div>
            <div class="profile-section">
                <h2>Education</h2>
                <div>
                    <div>Stanford University</div>
                    <div>BS Computer Science</div>
                    <div>2016-2020</div>
                </div>
            </div>
        </body>
    </html>
    """
    
    try:
        sections = locate_sections(html)
        print(f"  - Experience section: {len(sections['experience_section'])} chars")
        print(f"  - Education section: {len(sections['education_section'])} chars")
        print(f"  - Header section: {len(sections['header_section'])} chars")
        
        texts = extract_section_text(sections)
        print(f"  - Experience text: {len(texts['experience_text'])} chars")
        print(f"  - Education text: {len(texts['education_text'])} chars")
        print(f"  - Header text: {len(texts['header_text'])} chars")
        
        print("✅ Real world scenario handled successfully")
        
        # Show sample of extracted text
        if texts['experience_text']:
            print(f"\n  Sample experience text:\n  {texts['experience_text'][:100]}")
        
    except Exception as e:
        print(f"❌ Real world scenario failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("SECTION EXTRACTION FIX VERIFICATION")
    print("="*70)
    
    tests = [
        ("None Handling", test_none_handling),
        ("Empty String Handling", test_empty_string_handling),
        ("Malformed HTML", test_malformed_html),
        ("Missing Attributes", test_missing_attributes),
        ("BeautifulSoup Objects", test_beautifulsoup_object),
        ("Real World Scenario", test_real_world_scenario)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result is None or result is True:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nThe section extraction pipeline is now robust and handles:")
        print("  - None values")
        print("  - Empty strings")
        print("  - Malformed HTML")
        print("  - Missing attributes")
        print("  - BeautifulSoup objects")
        print("\n✅ Pipeline will not crash on AttributeError")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
