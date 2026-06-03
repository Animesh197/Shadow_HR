"""
LinkedIn LLM Extractor

Uses LLM (Groq - Llama 3.3 70B) to extract structured data from LinkedIn sections.
"""

from groq import Groq
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_experience(experience_text):
    """
    Extract work experience from Experience section text.
    
    Args:
        experience_text (str): Clean text from Experience section
    
    Returns:
        dict: {"experience": [{"company": "", "role": "", "start_date": "", "end_date": ""}]}
    """
    if not experience_text or len(experience_text.strip()) < 10:
        return {"experience": []}
    
    prompt = f"""You are an expert at extracting professional work experience from LinkedIn profiles.

Extract ONLY work experience entries from the following text.

IGNORE and DO NOT extract:
- Suggested profiles
- Social content (likes, comments, reactions)
- Activity posts
- Comments
- Reactions
- Recommendations
- "People also viewed"
- Hashtags
- Followers/connections counts
- Any non-work-experience content

For each work experience entry, extract:
- company: Company name only (not including "at" or other text)
- role: Job title
- start_date: Start date (e.g., "Jan 2023", "2023", or empty if not found)
- end_date: End date (e.g., "Dec 2024", "Present", or empty if not found)

Return ONLY valid JSON. No markdown, no backticks, no explanations.

Format:
{{
  "experience": [
    {{
      "company": "",
      "role": "",
      "start_date": "",
      "end_date": ""
    }}
  ]
}}

If no valid experience entries found, return: {{"experience": []}}

LinkedIn Experience Section Text:
{experience_text}
"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    return _clean_json_response(response.choices[0].message.content)


def extract_education(education_text):
    """
    Extract education from Education section text.
    
    Args:
        education_text (str): Clean text from Education section
    
    Returns:
        dict: {"education": [{"institution": "", "degree": "", "year": ""}]}
    """
    if not education_text or len(education_text.strip()) < 10:
        return {"education": []}
    
    prompt = f"""You are an expert at extracting education history from LinkedIn profiles.

Extract ONLY education entries from the following text.

IGNORE and DO NOT extract:
- Hashtags (anything starting with #)
- Social content (likes, comments, reactions)
- Activity posts
- Competitions
- Achievements (unless part of degree description)
- Recommendations
- "People also viewed"
- Any non-education content

For each education entry, extract:
- institution: School/University name only
- degree: Degree type and field (e.g., "Bachelor of Technology in Computer Science", or empty if not found)
- year: Graduation year or year range (e.g., "2023", "2020-2024", or empty if not found)

Return ONLY valid JSON. No markdown, no backticks, no explanations.

Format:
{{
  "education": [
    {{
      "institution": "",
      "degree": "",
      "year": ""
    }}
  ]
}}

If no valid education entries found, return: {{"education": []}}

LinkedIn Education Section Text:
{education_text}
"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    return _clean_json_response(response.choices[0].message.content)


def extract_header(header_text):
    """
    Extract headline and location from header section.
    
    Args:
        header_text (str): Clean text from header section
    
    Returns:
        dict: {"headline": "", "location": ""}
    """
    if not header_text or len(header_text.strip()) < 10:
        return {"headline": "", "location": ""}
    
    prompt = f"""You are an expert at extracting profile header information from LinkedIn.

Extract the following from the header text:
- headline: Professional summary/tagline (usually describes role and expertise)
- location: Geographic location ONLY (format: "City, State, Country" or "City, Country")

RULES:
- Headline must be professional summary text, NOT a location
- Location must be geographic location only, NOT a professional summary
- Never confuse headline with location
- Return empty string if not found

Return ONLY valid JSON. No markdown, no backticks, no explanations.

Format:
{{
  "headline": "",
  "location": ""
}}

LinkedIn Header Text:
{header_text}
"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    return _clean_json_response(response.choices[0].message.content)


def _clean_json_response(output):
    """
    Clean LLM response to extract valid JSON.
    
    Args:
        output (str): Raw LLM response
    
    Returns:
        dict: Parsed JSON
    """
    output = output.strip()
    
    # Remove markdown code blocks
    if output.startswith("```"):
        output = output.split("```")[1]
        if output.startswith("json"):
            output = output[4:]
        output = output.strip()
    
    # Remove trailing markdown
    if output.endswith("```"):
        output = output[:-3].strip()
    
    try:
        return json.loads(output)
    except json.JSONDecodeError as e:
        print(f"[linkedin_llm_extractor] JSON decode error: {e}")
        print(f"[linkedin_llm_extractor] Raw output: {output[:200]}")
        # Return empty structure
        if "experience" in output.lower():
            return {"experience": []}
        elif "education" in output.lower():
            return {"education": []}
        else:
            return {"headline": "", "location": ""}
