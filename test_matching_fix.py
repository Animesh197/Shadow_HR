"""
Test script to verify matching improvements.

Tests:
1. CBSE is accepted as valid institution
2. Fuzzy matching works for education
3. Fuzzy matching works for experience
4. Substring matching works
"""

import sys


def test_cbse_acceptance():
    """Test that CBSE is accepted as a valid institution."""
    print("\n" + "="*70)
    print("TEST 1: CBSE Institution Acceptance")
    print("="*70)
    
    from linkedin.linkedin_normalizer import normalize_institution_name
    
    # Test CBSE normalization
    cbse_variations = [
        "CBSE",
        "cbse",
        "Central Board of Secondary Education",
        "CBSE Board"
    ]
    
    for variation in cbse_variations:
        normalized = normalize_institution_name(variation)
        print(f"  {variation:40} → {normalized}")
        assert normalized != "", f"CBSE variant '{variation}' should normalize to something"
    
    # Check that they all normalize to same thing
    normalized_set = set(normalize_institution_name(v) for v in cbse_variations)
    assert len(normalized_set) == 1, f"All CBSE variations should normalize to same value, got: {normalized_set}"
    
    print("✅ CBSE accepted as valid institution")
    return True


def test_education_fuzzy_matching():
    """Test that education matcher uses fuzzy matching."""
    print("\n" + "="*70)
    print("TEST 2: Education Fuzzy Matching")
    print("="*70)
    
    from linkedin.linkedin_matcher import education_matcher
    
    # Test exact match
    resume_edu = [
        {"institution": "Stanford University", "degree": "BS Computer Science", "year": "2020"}
    ]
    linkedin_edu = [
        {"institution": "Stanford University", "degree": "Bachelor of Science", "year": "2020"}
    ]
    
    result = education_matcher(resume_edu, linkedin_edu)
    print(f"  Exact match score: {result['score']}%")
    print(f"  Matched: {result['matched_count']}/{result['total_resume_count']}")
    assert result['score'] == 100, "Exact match should score 100%"
    print("✅ Exact match works")
    
    # Test fuzzy match (slight variation)
    resume_edu = [
        {"institution": "Indian Institute of Technology Delhi", "degree": "BTech", "year": "2022"}
    ]
    linkedin_edu = [
        {"institution": "IIT Delhi", "degree": "BTech CSE", "year": "2022"}
    ]
    
    result = education_matcher(resume_edu, linkedin_edu)
    print(f"\n  Fuzzy match (IIT) score: {result['score']}%")
    print(f"  Matched: {result['matched_count']}/{result['total_resume_count']}")
    assert result['score'] >= 70, f"IIT Delhi variations should match (got {result['score']}%)"
    print("✅ Fuzzy match works for IIT variations")
    
    # Test CBSE matching
    resume_edu = [
        {"institution": "CBSE", "degree": "12th", "year": "2018"}
    ]
    linkedin_edu = [
        {"institution": "Central Board of Secondary Education", "degree": "Class 12", "year": "2018"}
    ]
    
    result = education_matcher(resume_edu, linkedin_edu)
    print(f"\n  CBSE match score: {result['score']}%")
    print(f"  Matched: {result['matched_count']}/{result['total_resume_count']}")
    if result['matched_count'] > 0:
        print(f"  Match details: {result['matches'][0]}")
    assert result['score'] >= 70, f"CBSE variations should match (got {result['score']}%)"
    print("✅ Fuzzy match works for CBSE")
    
    # Test substring match
    resume_edu = [
        {"institution": "MIT", "degree": "MS", "year": "2021"}
    ]
    linkedin_edu = [
        {"institution": "Massachusetts Institute of Technology", "degree": "Master of Science", "year": "2021"}
    ]
    
    result = education_matcher(resume_edu, linkedin_edu)
    print(f"\n  Substring match (MIT) score: {result['score']}%")
    print(f"  Matched: {result['matched_count']}/{result['total_resume_count']}")
    assert result['score'] >= 70, f"MIT variations should match (got {result['score']}%)"
    print("✅ Substring match works")
    
    return True


def test_experience_fuzzy_matching():
    """Test that experience matcher uses fuzzy matching."""
    print("\n" + "="*70)
    print("TEST 3: Experience Fuzzy Matching")
    print("="*70)
    
    from linkedin.linkedin_matcher import experience_matcher
    
    # Test exact match
    resume_exp = [
        {"company": "Google", "role": "Software Engineer", "start_date": "2020", "end_date": "2022"}
    ]
    linkedin_exp = [
        {"company": "Google", "role": "SWE", "start_date": "2020", "end_date": "2022"}
    ]
    
    result = experience_matcher(resume_exp, linkedin_exp)
    print(f"  Exact match score: {result['score']}%")
    print(f"  Matched: {result['matched_count']}/{result['total_resume_count']}")
    assert result['score'] == 100, "Exact company match should score 100%"
    print("✅ Exact company match works")
    
    # Test fuzzy match (company variation)
    resume_exp = [
        {"company": "Microsoft Corporation", "role": "Software Engineer", "start_date": "2021", "end_date": "Present"}
    ]
    linkedin_exp = [
        {"company": "Microsoft", "role": "SDE II", "start_date": "2021", "end_date": "Present"}
    ]
    
    result = experience_matcher(resume_exp, linkedin_exp)
    print(f"\n  Fuzzy match (Microsoft) score: {result['score']}%")
    print(f"  Matched: {result['matched_count']}/{result['total_resume_count']}")
    assert result['score'] >= 70, f"Microsoft variations should match (got {result['score']}%)"
    print("✅ Fuzzy match works for company variations")
    
    # Test substring match
    resume_exp = [
        {"company": "TCS", "role": "Developer", "start_date": "2019", "end_date": "2020"}
    ]
    linkedin_exp = [
        {"company": "Tata Consultancy Services", "role": "Developer", "start_date": "2019", "end_date": "2020"}
    ]
    
    result = experience_matcher(resume_exp, linkedin_exp)
    print(f"\n  Substring match (TCS) score: {result['score']}%")
    print(f"  Matched: {result['matched_count']}/{result['total_resume_count']}")
    if result['matched_count'] > 0:
        print(f"  Match details: {result['matches'][0]}")
    assert result['score'] >= 70, f"TCS variations should match (got {result['score']}%)"
    print("✅ Substring match works for company abbreviations")
    
    return True


def test_multiple_entries():
    """Test matching with multiple entries."""
    print("\n" + "="*70)
    print("TEST 4: Multiple Entry Matching")
    print("="*70)
    
    from linkedin.linkedin_matcher import experience_matcher, education_matcher
    
    # Test multiple experience entries with some matches
    resume_exp = [
        {"company": "Google", "role": "SWE", "start_date": "2022", "end_date": "Present"},
        {"company": "Microsoft Corporation", "role": "Intern", "start_date": "2021", "end_date": "2021"},
        {"company": "Unknown Startup", "role": "Developer", "start_date": "2020", "end_date": "2021"}
    ]
    linkedin_exp = [
        {"company": "Google LLC", "role": "Software Engineer", "start_date": "2022", "end_date": "Present"},
        {"company": "Microsoft", "role": "SWE Intern", "start_date": "2021", "end_date": "2021"}
    ]
    
    result = experience_matcher(resume_exp, linkedin_exp)
    print(f"  Experience score: {result['score']}%")
    print(f"  Matched: {result['matched_count']}/{result['total_resume_count']}")
    print(f"  Mismatches: {len(result['mismatches'])}")
    
    # Should match 2 out of 3 (Google and Microsoft)
    assert result['matched_count'] >= 2, f"Should match at least 2 entries (got {result['matched_count']})"
    print(f"✅ Matched {result['matched_count']}/{result['total_resume_count']} experience entries correctly")
    
    # Test multiple education entries
    resume_edu = [
        {"institution": "IIT Delhi", "degree": "BTech", "year": "2022"},
        {"institution": "CBSE", "degree": "12th", "year": "2018"}
    ]
    linkedin_edu = [
        {"institution": "Indian Institute of Technology Delhi", "degree": "BTech CSE", "year": "2022"},
        {"institution": "Central Board of Secondary Education", "degree": "Class XII", "year": "2018"}
    ]
    
    result = education_matcher(resume_edu, linkedin_edu)
    print(f"\n  Education score: {result['score']}%")
    print(f"  Matched: {result['matched_count']}/{result['total_resume_count']}")
    print(f"  Mismatches: {len(result['mismatches'])}")
    
    # Should match both entries
    assert result['matched_count'] == 2, f"Should match both entries (got {result['matched_count']})"
    print(f"✅ Matched {result['matched_count']}/{result['total_resume_count']} education entries correctly")
    
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("MATCHING FIX VERIFICATION")
    print("="*70)
    
    tests = [
        ("CBSE Acceptance", test_cbse_acceptance),
        ("Education Fuzzy Matching", test_education_fuzzy_matching),
        ("Experience Fuzzy Matching", test_experience_fuzzy_matching),
        ("Multiple Entry Matching", test_multiple_entries)
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
                print(f"\n❌ Test '{test_name}' failed")
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
        print("\nMatching improvements verified:")
        print("  ✅ CBSE accepted as valid institution")
        print("  ✅ Fuzzy matching works for education (70% similarity)")
        print("  ✅ Fuzzy matching works for experience (70% similarity)")
        print("  ✅ Substring matching works (MIT ↔ Massachusetts Institute...)")
        print("  ✅ Multiple entries handled correctly")
        print("\n✅ Experience and Education matching is now more flexible!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
