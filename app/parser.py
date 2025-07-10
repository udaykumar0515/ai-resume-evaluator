import PyPDF2
from docx import Document
import re
import unicodedata
from transformers import pipeline

class ResumeNER:
    def __init__(self):
        # Load the NER pipeline
        self.ner_pipeline = pipeline(
            "ner", 
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"  # Group tokens into entities
        )
    
    def extract_entities(self, text):
        """Extract entities using Hugging Face."""
        try:
            entities = self.ner_pipeline(text)
            return self._format_entities(entities)
        except Exception as e:
            print(f"NER Error: {e}")
            return {}

    def _format_entities(self, raw_entities):
        """Group entities by type (PERSON, ORG, etc.)."""
        grouped = {}
        for entity in raw_entities:
            label = entity["entity_group"]
            if label not in grouped:
                grouped[label] = []
            grouped[label].append(entity["word"])
        return grouped

# Initialize globally (loads model once)
ner = ResumeNER()
def split_sections(text: str) -> dict:
    """
    Splits resume text into major sections using keywords.
    """
    sections = {}
    # Expanded and organized header list
    headers = [
        "Contact", "Profile",
        "Career Objective", "Professional Summary", "Summary", "Objective",
        "Education", "Academic Background", "Qualifications",
        "Skills", "Technical Skills", "Key Skills", "Core Competencies",
        "Certifications", "Licenses", "Certificates",
        "Internships", "Work Experience", "Experience", "Employment History",
        "Projects", "Personal Projects", "Academic Projects",
        "Languages", 
        "Declaration", "References"
    ]

    # Create regex pattern that matches any of these headers
    pattern = r"(?im)(^|\n)\s*(" + "|".join(re.escape(h) + r"s?" for h in headers) + r")\s*:?\s*($|\n)"

    splits = re.split(pattern, text)
    
    # Initialize with any content before first header
    current_section = "Header"
    sections[current_section] = ""
    
    for part in splits:
        if not part:
            continue
        # Check if part is a header
        is_header = any(h.lower() in part.lower() for h in headers)
        if is_header:
            current_section = part.strip().rstrip(':')
            sections[current_section] = ""
        else:
            sections[current_section] += part.strip() + "\n"
    
    # Clean up sections
    sections = {k: v.strip() for k, v in sections.items() if v.strip()}
    
    # Post-processing for header section
    if "Header" in sections:
        header_content = sections.pop("Header")
        # Check if it looks like contact info
        if any(x in header_content.lower() for x in ["@", "http", "linkedin", "github", "phone"]):
            sections["Contact"] = header_content
        else:
            sections["Profile"] = header_content
            
    return sections


def clean_text(text: str) -> str:
    """
    Cleans and normalizes raw extracted text.
    """
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)

    # Replace multiple newlines with max two
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    # Remove trailing spaces on each line
    text = "\n".join(line.strip() for line in text.splitlines())

    # Optionally remove extra spaces inside lines
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()

def extract_text_from_docx(file_path_or_buffer) -> str:
    try:
        if hasattr(file_path_or_buffer, "read"):
            raise NotImplementedError("DOCX buffer reading not implemented.")
        doc = Document(file_path_or_buffer)
        full_text = [para.text for para in doc.paragraphs]
        return "\n".join(full_text)
    except Exception as e:
        print(f"Error extracting DOCX text: {e}")
        return ""

def extract_text_from_pdf(file_path_or_buffer) -> str:
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(file_path_or_buffer)
        for page in pdf_reader.pages:
            page_text = page.extract_text() or ""  # Avoid None
            text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
    return text.strip()


def extract_text_from_txt(file_path_or_buffer) -> str:
    """
    Extracts text from a plain text file.

    Args:
        file_path_or_buffer: Path to text file or file-like buffer

    Returns:
        Text content as a string.
    """
    try:
        if hasattr(file_path_or_buffer, "read"):
            # file-like buffer
            return file_path_or_buffer.read().decode("utf-8")
        else:
            with open(file_path_or_buffer, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        print(f"Error extracting TXT text: {e}")
        return ""

import re

def extract_contact_info(text):
    contact = {}

    # Name (first line or from NER)
    lines = text.strip().splitlines()
    if lines:
        contact["name"] = lines[0].strip()

    # Email
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    if match:
        contact["email"] = match.group(0)

    # Phone (generic international + local patterns)
    phone_match = re.search(r"(\+91[-\s]?)?\d{10}", text)
    if phone_match:
        contact["phone"] = phone_match.group(0)

    # LinkedIn
    linkedin_match = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[^\s]+", text)
    if linkedin_match:
        contact["linkedin"] = linkedin_match.group(0)

    # GitHub
    github_match = re.search(r"(https?://)?(www\.)?github\.com/[^\s]+", text)
    if github_match:
        contact["github"] = github_match.group(0)

    return contact

def parse_resume(file_path_or_buffer, file_type="pdf"):
    # 1. Extract raw text
    text = extract_text(file_path_or_buffer, file_type)
    
    # 2. Clean and split sections (rule-based)
    sections = split_sections(text)

    # 3. Global entity extraction with Hugging Face NER
    global_entities = ner.extract_entities(text)

    # 4. Per-section entity extraction
    enhanced_sections = {}
    for section, content in sections.items():
        enhanced_sections[section] = {
            "text": content,
            "entities": ner.extract_entities(content)
        }

    # 5. Structured contact info
    contact_info = extract_contact_info(text)

    # Final structured output
    return {
        "sections": enhanced_sections,
        "global_entities": global_entities,
        "contact": contact_info
    }

def extract_text(file_path_or_buffer, file_type="pdf") -> str:
    """
    General text extraction method to call for a given file.

    Args:
        file_path_or_buffer: file path or buffer
        file_type: 'pdf' or 'txt'

    Returns:
        Extracted text string.
    """
    if file_type.lower() == "pdf":
        raw_text = extract_text_from_pdf(file_path_or_buffer)
    elif file_type.lower() == "txt":
        raw_text = extract_text_from_txt(file_path_or_buffer)
    elif file_type.lower() == "docx":
        raw_text = extract_text_from_docx(file_path_or_buffer)
    else:
        raise ValueError("Unsupported file type. Use 'pdf', 'txt' or 'docx'.")

    return clean_text(raw_text)

# Replace with your actual path
sample_pdf_path = r"D:\uday\Vscode\Projects\AI_resume_evaluator\data\resumes\resume_webdev.pdf"

text = extract_text(sample_pdf_path, file_type="pdf")
sections = split_sections(text)

for header, content in sections.items():
    print(f"\n{header.upper()}:")

    if header.lower() == "contact":
        contact_info = extract_contact_info(content)
        for key, value in contact_info.items():
            print(f"{key.title()}: {value}")
    else:
        print(content)
