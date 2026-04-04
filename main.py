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

    return text


# -------- NEW: Extract links from PDF --------
def extract_links_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    links = []

    for page in doc:
        page_links = page.get_links()
        
        for link in page_links:
            uri = link.get("uri")
            if uri:
                links.append(uri)

    return links


# -------- NEW: Extract GitHub from links --------
def extract_github_from_links(links):
    for link in links:
        if "github.com" in link:
            return link.rstrip("/").split("/")[-1]
    return ""


# -------- STEP 2: Send to LLM for structured extraction --------
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

    output = response.choices[0].message.content

    return output


# -------- Clean LLM Output --------
def clean_json_output(output):
    output = output.strip()

    if output.startswith("```"):
        output = output.split("```")[1]
        if output.startswith("json"):
            output = output[4:]
    
    return output.strip()


# -------- MAIN EXECUTION --------
if __name__ == "__main__":
    pdf_path = "resume.pdf"

    print("🔄 Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)

    print("🔗 Extracting links from PDF...")
    links = extract_links_from_pdf(pdf_path)

    print("\n🌐 Links Found:")
    for l in links:
        print(l)

    print("\n🧠 Sending to LLM...")
    result = extract_entities_with_llm(text)

    print("\n📄 Extracted JSON:\n")
    print(result)

    cleaned = clean_json_output(result)

    try:
        parsed = json.loads(cleaned)

        # -------- NEW: Fix GitHub using links --------
        if not parsed.get("github"):
            github_from_links = extract_github_from_links(links)
            parsed["github"] = github_from_links

        print("\n✅ Final Parsed Output:")
        print(json.dumps(parsed, indent=2))

    except:
        print("\n⚠️ JSON parsing failed. Raw output shown above.")