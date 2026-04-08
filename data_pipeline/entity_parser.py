"""
Uses LLM (Groq - Llama 3.3 70B) to extract structured data:
- Name
- GitHub
- Skills
- Projects

Also cleans JSON output from LLM
"""

from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_entities_with_llm(resume_text):
    prompt = f"""
You are an expert resume parser.

Extract the following details from the resume text:
- Name
- GitHub username or link (if available)
- Skills (as a list of technologies)
- Projects (short names or descriptions)

Return only raw JSON.
Do NOT include markdown formatting, backticks, or explanations. 

Return ONLY valid JSON in this format:

{{
  "name": "",
  "github": "",
  "skills": [],
  "projects": []
}}

Resume Text:
{resume_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content


def clean_json_output(output):
    output = output.strip()

    if output.startswith("```"):
        output = output.split("```")[1]
        if output.startswith("json"):
            output = output[4:]

    return output.strip()