"""
Quick test script to verify LinkedIn extraction refactor.

This tests the new LLM-based extraction system with a sample HTML.
"""

from linkedin.linkedin_profile_extractor import extract_linkedin_profile


def test_basic_extraction():
    """Test basic extraction with sample HTML."""
    
    sample_html = """
    <html>
        <head>
            <title>Arun Kumar Giri | LinkedIn</title>
        </head>
        <body>
            <div class="header">
                <div>Building Real-World AI Systems (LLMs, Intelligent Pipelines, Automation)</div>
                <div>Bengaluru, Karnataka, India</div>
            </div>
            
            <div class="section">
                <h2>Experience</h2>
                <div class="experience-entry">
                    <div>Software Engineer</div>
                    <div>Google</div>
                    <div>Jan 2023 - Present</div>
                    <div>Building scalable systems</div>
                </div>
                <div class="experience-entry">
                    <div>Intern</div>
                    <div>Microsoft</div>
                    <div>Jun 2022 - Aug 2022</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Education</h2>
                <div class="education-entry">
                    <div>Indian Institute of Technology Patna</div>
                    <div>Bachelor of Technology in Computer Science</div>
                    <div>2019 - 2023</div>
                </div>
            </div>
            
            <div class="noise">
                <div>#NewtonSchool</div>
                <div>People also viewed: John Doe, Jane Smith</div>
                <div>500+ connections</div>
                <div>Big thanks to my mentors!</div>
            </div>
        </body>
    </html>
    """
    
    print("="*70)
    print("TESTING LINKEDIN EXTRACTION REFACTOR")
    print("="*70)
    print("\n🔄 Extracting profile from sample HTML...\n")
    
    try:
        profile = extract_linkedin_profile(sample_html, "test-profile")
        
        print("✅ EXTRACTION SUCCESSFUL\n")
        print("="*70)
        print("EXTRACTED PROFILE")
        print("="*70)
        
        print(f"\n📝 Name: {profile['name']}")
        print(f"💼 Headline: {profile['headline']}")
        print(f"📍 Location: {profile['location']}")
        
        print(f"\n🏢 Experience ({len(profile['experience'])} entries):")
        for i, exp in enumerate(profile['experience'], 1):
            print(f"  {i}. {exp['role']} at {exp['company']}")
            if exp.get('start_date') or exp.get('end_date'):
                print(f"     {exp.get('start_date', '')} - {exp.get('end_date', '')}")
        
        print(f"\n🎓 Education ({len(profile['education'])} entries):")
        for i, edu in enumerate(profile['education'], 1):
            print(f"  {i}. {edu['institution']}")
            if edu.get('degree'):
                print(f"     {edu['degree']}")
            if edu.get('year'):
                print(f"     {edu['year']}")
        
        print(f"\n📊 Confidence Scores:")
        confidence = profile.get('confidence', {})
        print(f"  - Overall: {confidence.get('overall_confidence', 0):.1f}%")
        print(f"  - Experience: {confidence.get('experience_confidence', 0):.1f}%")
        print(f"  - Education: {confidence.get('education_confidence', 0):.1f}%")
        print(f"  - Headline: {confidence.get('headline_confidence', 0):.1f}%")
        print(f"  - Location: {confidence.get('location_confidence', 0):.1f}%")
        
        print("\n" + "="*70)
        print("VALIDATION CHECKS")
        print("="*70)
        
        # Check for noise
        issues = []
        
        # Check education for noise
        for edu in profile['education']:
            inst = edu['institution'].lower()
            if '#' in inst:
                issues.append(f"❌ Education contains hashtag: {edu['institution']}")
            if 'thanks' in inst:
                issues.append(f"❌ Education contains 'thanks': {edu['institution']}")
            if 'people also viewed' in inst:
                issues.append(f"❌ Education contains 'people also viewed': {edu['institution']}")
        
        # Check experience for noise
        for exp in profile['experience']:
            company = exp['company'].lower()
            if 'connections' in company:
                issues.append(f"❌ Experience contains 'connections': {exp['company']}")
            if 'followers' in company:
                issues.append(f"❌ Experience contains 'followers': {exp['company']}")
        
        # Check location vs headline
        if profile['location'] and profile['headline']:
            if profile['location'] == profile['headline']:
                issues.append(f"❌ Location equals headline: {profile['location']}")
        
        if issues:
            print("\n⚠️  ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n✅ All validation checks passed!")
            print("  - No hashtags in education")
            print("  - No 'thanks' in education")
            print("  - No 'people also viewed' in education")
            print("  - No 'connections' in experience")
            print("  - Location and headline are distinct")
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETE")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ EXTRACTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_extraction()
    exit(0 if success else 1)
