import fitz  
from groq import Groq
import json
import os
from dotenv import load_dotenv


load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# -------- STEP 1: Extract text from PDF --------
def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)

    for page in doc:
        text += page.get_text()
        # page.get_links() to extract links, will be used later.

    # print(text)
    return text


# -------- STEP 2: Send to LLM for structured extraction --------
def extract_entities_with_llm(resume_text):
    prompt = f"""
You are an expert resume parser.

Extract the following details from the resume text:
- Name
- GitHub username or link (if available)
- Skills (as a list of technologies)
- Projects (short names or descriptions)

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

    output = response.choices[0].message.content

    return output


# -------- MAIN EXECUTION --------
if __name__ == "__main__":
    pdf_path = "resume.pdf"  # put your resume file in same folder

    print("Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)

    print("Sending to LLM...")
    result = extract_entities_with_llm(text)

    print("\n Extracted JSON:\n")
    print(result)

    # Optional: Try parsing JSON safely
    try:
        parsed = json.loads(result)
        print("\n Parsed Successfully:")
        print(json.dumps(parsed, indent=2))
    except:
        print("\n⚠️ JSON parsing failed. Raw output shown above.")