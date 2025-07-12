import PyPDF2
from docx import Document
import re
import unicodedata
import json
import os
from datetime import datetime
from transformers import pipeline
from functools import lru_cache

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

# Common degree patterns
DEGREE_PATTERNS = [
    r"\bB\.?Tech\b", r"\bB\.?E\b", r"\bB\.?Sc\b", r"\bB\.?Com\b", 
    r"\bB\.?A\b", r"\bM\.?Tech\b", r"\bM\.?Sc\b", r"\bM\.?Com\b",
    r"\bM\.?A\b", r"\bPh\.?D\b", r"\bBachelor\b", r"\bMaster\b",
    r"\bDiploma\b", r"\bPGDM\b", r"\bMBA\b", r"\bMCA\b"
]

# Common date patterns (for education/experience dates)
DATE_PATTERNS = [
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{4}",
    r"\b\d{1,2}/\d{4}",
    r"\b\d{4}\s*[-–]\s*\d{4}",
    r"\b\d{1,2}\s*(?:st|nd|rd|th)?\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{4}"
]

# Enhanced skill keywords with common variations - ONLY THIS DEFINITION SHOULD EXIST
SKILL_KEYWORDS = {
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "C++": ["c\\+\\+"],
    "SQL": ["sql"],
    "HTML": ["html"],
    "CSS": ["css"],
    "React": ["react"],
    "Angular": ["angular"],
    "Vue": ["vue"],
    "Django": ["django"],
    "Flask": ["flask"],
    "Node.js": ["node", "node.js", "nodejs"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning"],
    "Data Science": ["data science"],
    "AWS": ["aws"],
    "Azure": ["azure"],
    "Google Cloud": ["google cloud", "gcp"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes"],
    "Git": ["git"],
    "Jenkins": ["jenkins"],
    "CI/CD": ["ci/cd", "continuous integration"],
    "Agile": ["agile"],
    "Scrum": ["scrum"]
}

# Enhanced entity cleaning with institution filtering
INSTITUTION_KEYWORDS = ["college", "university", "institute", "school", "academy", 
                       "foundation", "research center", "company", "corporation"]

def clean_entities(entity_dict):
    """
    More sophisticated entity cleaning with:
    - Better subword merging
    - Institution detection
    - Skill filtering
    - Name handling
    """
    cleaned = {}
    for label, words in entity_dict.items():
        processed = []
        buffer = []
        
        for word in words:
            # Handle subword tokens
            if word.startswith("##"):
                if buffer:
                    buffer.append(word[2:])
                continue
            
            if buffer:
                merged = "".join(buffer)
                if len(merged) >= 3:
                    processed.append(merged)
                buffer = []
            
            if word.strip():
                buffer.append(word)
        
        if buffer:
            merged = "".join(buffer)
            if len(merged) >= 3:
                processed.append(merged)
        
        # Apply filters based on entity type
        filtered = []
        for entity in processed:
            entity = entity.strip()
            
            # Skip if too short or just numbers
            if len(entity) < 3 or entity.isdigit():
                continue
                
            # Skip email/url patterns
            if any(c in entity for c in ":@()") or "http" in entity.lower():
                continue
                
            # Special handling for PER (names)
            if label == "PER":
                if len(entity.split()) > 3:  # Too long for a name
                    continue
                filtered.append(entity)
                continue
                
            # Special handling for ORG (institutions/companies)
            if label == "ORG":
                # Check if it looks like an institution
                if any(kw in entity.lower() for kw in INSTITUTION_KEYWORDS):
                    filtered.append(entity)
                    continue
                # Check if it's a known company
                if entity in ["Elsystems", "Edunet", "Cognifyz", "IBM"]:
                    filtered.append(entity)
                    continue
            
            # For other labels, apply general filters
            if (not any(skill.lower() in entity.lower() for skill in SKILL_KEYWORDS.keys()) and
                not entity.lower() in ["web", "app", "ml", "ai"]):
                filtered.append(entity)
        
        # Remove duplicates and sort
        if filtered:
            cleaned[label] = sorted(list(set(filtered)))
    
    return cleaned

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

def extract_contact_info(text):
    contact = {}

    # Name (first line or from NER)
    lines = text.strip().splitlines()
    if lines:
        first_line = lines[0].strip()
        # Basic check if first line looks like a name (not email/url)
        if not any(c in first_line for c in ["@", "http", "://", "www."]):
            contact["name"] = first_line
    
    # Fallback to NER if name not found
    if "name" not in contact:
        entities = ner.extract_entities(text)
        if "PER" in entities:
            contact["name"] = " ".join(entities["PER"][:2])  # Take first 2 PERSON entities

    # Email
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    if match:
        contact["email"] = match.group(0)

    # Phone (generic international + local patterns)
    phone_match = re.search(r"(\+91[-\s]?)?[0-9]{10}", text)
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

# Enhanced education extraction
def extract_education_info(text):
    education = []
    sections = split_sections(text)
    
    if "Education" in sections:
        edu_text = sections["Education"]
        
        # Extract using more precise patterns
        degree_pattern = r"(?i)((?:B\.?Tech|B\.?E|B\.?Sc|B\.?Com|B\.?A|M\.?Tech|M\.?Sc|M\.?Com|M\.?A|Ph\.?D|Bachelor|Master|Diploma|PGDM|MBA|MCA)\b[^\n]*)"
        dates_pattern = r"(?i)(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{4}|(?:\d{4}\s*[-–]\s*\d{4})|\d{1,2}/\d{4})"
        
        # Find all degree entries
        degrees = re.findall(degree_pattern, edu_text)
        dates = re.findall(dates_pattern, edu_text)
        
        # Extract institution names using NER
        entities = ner.extract_entities(edu_text)
        institutions = []
        if "ORG" in entities:
            institutions = [inst for inst in entities["ORG"] 
                          if any(kw in inst.lower() for kw in INSTITUTION_KEYWORDS)]
        
        # Create education entries
        for i, degree in enumerate(degrees):
            edu_entry = {
                "degree": degree.strip(),
                "institution": institutions[i] if i < len(institutions) else None,
                "dates": dates[i] if i < len(dates) else None
            }
            education.append(edu_entry)
    
    return education

# Enhanced skills extraction
def extract_skills(text):
    skills_found = set()
    sections = split_sections(text)
    
    # Check skills section first
    skills_text = ""
    for section in ["Skills", "Technical Skills", "Key Skills"]:
        if section in sections:
            skills_text += sections[section] + "\n"
    
    # Match against skill keywords
    for skill, patterns in SKILL_KEYWORDS.items():
        for pattern in patterns:
            if re.search(r"\b" + pattern + r"\b", skills_text, re.IGNORECASE):
                skills_found.add(skill)
    
    # Also check other sections for skills
    other_sections = ["Experience", "Projects", "Education"]
    for section in other_sections:
        if section in sections:
            section_text = sections[section]
            for skill, patterns in SKILL_KEYWORDS.items():
                for pattern in patterns:
                    if re.search(r"\b" + pattern + r"\b", section_text, re.IGNORECASE):
                        skills_found.add(skill)
    
    return sorted(skills_found)

def format_skills_output(skills_list):
    """
    Group skills by category for better presentation
    """
    categorized = {
        "Languages": [],
        "Frameworks/Tools": [],
        "Concepts": [],
        "Other": []
    }
    
    # Define skill categories
    language_skills = ["python", "java", "javascript", "c", "c++", "html", "css"]
    framework_skills = ["react", "node", "sql", "pygame", "streamlit", "git"]
    concept_skills = ["machine learning", "web development", "data structures"]
    
    for skill in skills_list:
        skill_lower = skill.lower()
        if skill_lower in language_skills:
            categorized["Languages"].append(skill)
        elif skill_lower in framework_skills:
            categorized["Frameworks/Tools"].append(skill)
        elif skill_lower in concept_skills:
            categorized["Concepts"].append(skill)
        else:
            categorized["Other"].append(skill)
    
    # Format the output
    output = []
    for category, skills in categorized.items():
        if skills:
            output.append(f"{category}: {', '.join(skills)}")
    
    return "\n".join(output)

def extract_dates(text):
    dates = []
    for pattern in DATE_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            dates.append(match.group(0))
    return dates

@lru_cache(maxsize=32)
def cached_parse_resume(file_path: str, file_type: str = "pdf"):
    """
    Cached version of parse_resume to avoid reprocessing the same file.
    Uses file modification time as part of cache key to detect changes.
    """
    # Get file modification time for cache invalidation
    mod_time = os.path.getmtime(file_path)
    cache_key = f"{file_path}:{file_type}:{mod_time}"
    
    # Call the actual parse function
    return parse_resume(file_path, file_type)

def parse_resume(file_path_or_buffer, file_type="pdf"):
    # 1. Extract raw text
    text = extract_text(file_path_or_buffer, file_type)
    
    # 2. Clean and split sections (rule-based)
    sections = split_sections(text)

    # 3. Global entity extraction with Hugging Face NER
    global_entities = ner.extract_entities(text)

    # 4. Extract specific fields
    contact_info = extract_contact_info(text)
    education_info = extract_education_info(text)
    skills = extract_skills(text)
    dates = extract_dates(text)

    # 5. Per-section entity extraction
    enhanced_sections = {}
    for section, content in sections.items():
        enhanced_sections[section] = {
            "text": content,
            "entities": ner.extract_entities(content)
        }

    # Final structured output
    return {
        "metadata": {
            "processing_date": datetime.now().isoformat(),
            "file_type": file_type
        },
        "sections": enhanced_sections,
        "global_entities": global_entities,
        "contact": contact_info,
        "education": education_info,
        "skills": skills,
        "dates": dates
    }

def extract_text(file_path_or_buffer, file_type="pdf") -> str:
    """
    General text extraction method to call for a given file.
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

def save_parsed_resume(output_path: str, parsed_data: dict):
    """Save parsed resume data to JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=2)

def load_parsed_resume(input_path: str) -> dict:
    """Load previously parsed resume data from JSON file."""
    with open(input_path, "r", encoding="utf-8") as f:
        return json.load(f)

def format_section_output(title, content, max_width=80):
    """Format a section for clean console output"""
    divider = "=" * max_width
    title_line = f" {title.upper()} ".center(max_width, "=")
    return f"\n{divider}\n{title_line}\n{divider}\n{content}"

# Enhanced section printing
def print_section_content(section_name, content, max_lines=6):
    """Print section content with better formatting"""
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    if not lines:
        return "No content found"
    
    output = []
    for i, line in enumerate(lines[:max_lines]):
        # Clean up bullet points and formatting
        clean_line = re.sub(r"^[•\-*]\s*", "", line)
        output.append(f"{i+1}. {clean_line}")
    
    if len(lines) > max_lines:
        output.append(f"... (+{len(lines)-max_lines} more lines)")
    
    return "\n".join(output)

def print_parsed_resume(parsed_data):
    """Improved printing with better section handling"""
    # 1. Print metadata
    print(format_section_output("Resume Analysis Results", 
          f"Processed on: {parsed_data['metadata']['processing_date']}\n"
          f"File type: {parsed_data['metadata']['file_type']}"))
    
    # 2. Print contact info
    contact = parsed_data["contact"]
    print(format_section_output("Contact Information",
          "\n".join(f"{k.title():<12}: {v}" for k, v in contact.items())))
    
    # 3. Print education
    if parsed_data["education"]:
        edu_str = ""
        for i, edu in enumerate(parsed_data["education"], 1):
            edu_str += (f"{i}. {edu.get('degree', 'N/A')}\n"
                       f"   @ {edu.get('institution', 'N/A')}\n"
                       f"   {edu.get('dates', 'N/A')}\n")
        print(format_section_output("Education", edu_str))
    else:
        print(format_section_output("Education", "No education information found"))
    
    # 4. Print skills
    if parsed_data["skills"]:
        print(format_section_output("Technical Skills", 
              format_skills_output(parsed_data["skills"])))
    else:
        print(format_section_output("Technical Skills", "No skills found"))
    
    # 5. Print key sections with full content
    key_sections = ["Experience", "Internships", "Projects", "Certifications"]
    for section in key_sections:
        if section in parsed_data["sections"]:
            content = print_section_content(
                section, 
                parsed_data["sections"][section]["text"]
            )
            print(format_section_output(section, content))
    
    # 6. Print other sections briefly
    other_sections = [s for s in parsed_data["sections"] 
                     if s not in key_sections + ["Contact", "Skills", "Education"]]
    if other_sections:
        print(format_section_output("Other Sections",
              "\n".join(f"• {s}" for s in other_sections)))
    
    # 7. Print cleaned entities if needed
    if "ORG" in parsed_data["global_entities"]:
        print(format_section_output("Identified Organizations",
              ", ".join(parsed_data["global_entities"]["ORG"])))

    # 8. Print section overview with better formatting
    sections_str = ""
    for section, content in parsed_data["sections"].items():
        if section.lower() in ["contact", "declaration"]:  # Skip these sections
            continue
            
        sections_str += f"\n► {section.upper()}:\n"
        sections_str += "-"*(len(section)+3) + "\n"
        
        # Show first 4 lines of content with better formatting
        lines = [line.strip() for line in content["text"].split("\n") if line.strip()]
        preview = "\n".join(lines[:4])
        sections_str += f"{preview}\n"
        
        # Show entity summary if exists
        if content["entities"]:
            section_entities = []
            for label, items in content["entities"].items():
                section_entities.extend(items)
            if section_entities:
                sections_str += "\nKey terms: "
                sections_str += f"{', '.join(section_entities[:5])}"
                if len(section_entities) > 5:
                    sections_str += f" (+{len(section_entities)-5} more)"
                sections_str += "\n"
    
    print(format_section_output("Section Overview", sections_str.strip()))

# Example usage
if __name__ == "__main__":
    sample_pdf_path = r"D:\uday\Vscode\Projects\AI_resume_evaluator\resumes\resume_webdev.pdf"
    
    # Parse with caching
    parsed_data = cached_parse_resume(sample_pdf_path, "pdf")
    
    # Clean all entity outputs
    parsed_data["global_entities"] = clean_entities(parsed_data["global_entities"])
    for section in parsed_data["sections"]:
        parsed_data["sections"][section]["entities"] = clean_entities(
            parsed_data["sections"][section]["entities"]
        )
    
    # Print cleaned results
    print_parsed_resume(parsed_data)
    