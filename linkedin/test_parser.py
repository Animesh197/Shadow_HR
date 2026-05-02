"""
Test LinkedIn Parser

Quick test to verify the parser extracts data correctly.
"""

from linkedin_parser import parse_linkedin_profile


def test_parser_with_sample_html():
    """
    Test parser with a minimal sample HTML structure.
    """
    sample_html = """
    <html>
    <head>
        <title>John Doe | LinkedIn</title>
    </head>
    <body>
        <h1>John Doe</h1>
        <div class="top-card-description">Software Engineer at Google | Python, AI, Cloud</div>
        <div class="location">San Francisco, California, USA</div>
        
        <section id="experience">
            <h2>Experience</h2>
            <li>
                <div>Software Engineer at Google</div>
                <div>Jan 2022 - Present</div>
            </li>
            <li>
                <div>Backend Developer at Microsoft</div>
                <div>Jun 2020 - Dec 2021</div>
            </li>
        </section>
        
        <section id="education">
            <h2>Education</h2>
            <li>
                <div>Stanford University</div>
                <div>Bachelor of Science in Computer Science</div>
                <div>2016 - 2020</div>
            </li>
        </section>
    </body>
    </html>
    """
    
    profile = parse_linkedin_profile(sample_html)
    
    print("Parsed Profile:")
    print(f"Name: {profile['name']}")
    print(f"Headline: {profile['headline']}")
    print(f"Location: {profile['location']}")
    print(f"\nExperience ({len(profile['experience'])} entries):")
    for exp in profile['experience']:
        print(f"  - {exp['role']} at {exp['company']} ({exp['start_date']} - {exp['end_date']})")
    print(f"\nEducation ({len(profile['education'])} entries):")
    for edu in profile['education']:
        print(f"  - {edu['institution']}: {edu['degree']} ({edu['year']})")
    
    # Assertions
    assert profile['name'] == "John Doe", f"Expected 'John Doe', got '{profile['name']}'"
    assert len(profile['experience']) > 0, "Should extract at least one experience entry"
    assert len(profile['education']) > 0, "Should extract at least one education entry"
    
    print("\n✅ All tests passed!")


def test_parser_with_empty_html():
    """
    Test parser handles empty/invalid HTML gracefully.
    """
    profile = parse_linkedin_profile("")
    
    assert profile['name'] == ""
    assert profile['headline'] == ""
    assert profile['location'] == ""
    assert profile['experience'] == []
    assert profile['education'] == []
    
    print("✅ Empty HTML test passed!")


if __name__ == "__main__":
    print("Testing LinkedIn Parser...\n")
    test_parser_with_empty_html()
    print()
    test_parser_with_sample_html()
