import PyPDF2
from docx import Document
import re
import unicodedata
import os
from datetime import datetime
from functools import lru_cache
import torch
from modules.text_constants import SKILL_KEYWORDS, SKILL_CATEGORIES, INSTITUTION_KEYWORDS

# Set offline mode for transformers to avoid internet dependency
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

# Try to import transformers with offline mode
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not available, using fallback parsing")

class ResumeNER:
    def __init__(self):
        self._model_loaded = False
        self._device = 0 if torch.cuda.is_available() else -1
        self.ner_pipeline = None
        self.use_fallback = False

    def _load_model(self):
        if not self._model_loaded and TRANSFORMERS_AVAILABLE:
            try:
                self.ner_pipeline = pipeline(
                    "ner",
                    model="dslim/bert-base-NER",
                    aggregation_strategy="simple",
                    device=self._device
                )
                self._model_loaded = True
                print("✅ NER model loaded successfully")
            except Exception as e:
                print(f"⚠️ NER model failed to load: {e}")
                print("🔄 Using fallback parsing methods")
                self.use_fallback = True
                self._model_loaded = True  # Mark as loaded to avoid retries
        elif not TRANSFORMERS_AVAILABLE:
            self.use_fallback = True
            self._model_loaded = True

    def extract_entities(self, text):
        self._load_model()  # Only load when first used
        
        if self.use_fallback:
            return self._fallback_entity_extraction(text)
        
        try:
            entities = self.ner_pipeline(text)
            return {
                "entities": self._format_entities(entities),
                "raw": entities
            }
        except Exception as e:
            print(f"NER Error: {e}, using fallback")
            return self._fallback_entity_extraction(text)

    def _fallback_entity_extraction(self, text):
        """Fallback entity extraction using regex patterns"""
        entities = {
            "PER": [],  # Person names
            "ORG": [],  # Organizations
            "LOC": []   # Locations
        }
        
        # Extract person names (simple heuristic)
        # Look for capitalized words that could be names
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        potential_names = re.findall(name_pattern, text)
        
        # Filter out common non-name words
        non_names = {'Web Development', 'Machine Learning', 'Data Science', 'Computer Science', 
                    'Information Technology', 'Software Engineering', 'Bachelor Degree', 
                    'Master Degree', 'High School', 'College University'}
        
        for name in potential_names:
            if name not in non_names and len(name.split()) == 2:
                entities["PER"].append(name)
        
        # Extract organizations (companies, universities)
        org_keywords = ['University', 'College', 'Institute', 'Corporation', 'Company', 
                       'Ltd', 'Inc', 'LLC', 'Technologies', 'Systems', 'Services']
        
        for keyword in org_keywords:
            pattern = r'\b[A-Z][a-zA-Z\s]+' + re.escape(keyword) + r'\b'
            orgs = re.findall(pattern, text)
            entities["ORG"].extend(orgs)
        
        # Extract locations (cities, states, countries)
        location_pattern = r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b'
        potential_locations = re.findall(location_pattern, text)
        
        # Simple location filtering
        common_locations = {'New York', 'California', 'Texas', 'Florida', 'India', 
                           'United States', 'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad'}
        
        for loc in potential_locations:
            if loc in common_locations or any(word in loc for word in ['City', 'State', 'Country']):
                entities["LOC"].append(loc)
        
        # Remove duplicates and clean
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return {
            "entities": entities,
            "raw": []
        }

    def _format_entities(self, raw_entities):
        grouped = {}
        for entity in raw_entities:
            label = entity["entity_group"]
            if label not in grouped:
                grouped[label] = []
            grouped[label].append(entity["word"])
        return grouped

ner = ResumeNER()


INSTITUTION_KEYWORDS = INSTITUTION_KEYWORDS

def clean_entities(entity_dict):
    cleaned = {}
    for label, words in entity_dict.items():
        processed = []
        buffer = []
        
        for word in words:
            if word.lower() in ["interns", "inter"]:
                continue

            if label == "ORG":
                if word == "IBM SkillsB":
                    word = "IBM SkillsBuild"
                elif word == "Web Development Inter":
                    continue
                elif word == "Vardhaman":
                    word = "Vardhaman College of Engineering"
                elif word == "Elsystems":
                    word = "Elsystems Services"
                elif word == "Edunet":
                    word = "Edunet Foundation"
                elif word == "Deep":
                    continue

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
        
        filtered = []
        for entity in processed:
            entity = entity.strip()
            
            if len(entity) < 3 or entity.isdigit():
                continue
                
            if any(c in entity for c in ":@()") or "http" in entity.lower():
                continue
                
            if label == "PER":
                if len(entity.split()) > 3:
                    continue
                filtered.append(entity)
                continue
                
            if label == "ORG":
                if any(kw in entity.lower() for kw in INSTITUTION_KEYWORDS):
                    filtered.append(entity)
                    continue
                if entity in ["Elsystems", "Edunet", "Cognifyz", "IBM", "CodTech"]:
                    filtered.append(entity)
                    continue
            
            if (not any(skill.lower() in entity.lower() for skill in SKILL_KEYWORDS.keys()) and
                not entity.lower() in ["web", "app", "ml", "ai"]):
                filtered.append(entity)
        
        if filtered:
            cleaned[label] = sorted(list(set(filtered)))
    
    return cleaned

@lru_cache(maxsize=16)
def split_sections(text: str) -> dict:
    sections = {}
    headers = [
        "Contact", "Profile",
        "Career Objective", "Professional Summary", "Summary", "Objective",
        "Education", "Academic Background", "Qualifications",
        "Skills", "Technical Skills", "Key Skills", "Core Competencies",
        "Certifications", "Licenses", "Certificates",
        "Internships", "Work Experience", "Experience", "Employment History",  # Added variations
        "Projects", "Personal Projects", "Academic Projects",
        "Languages", 
        "Declaration", "References"
    ]

    # Make the pattern more flexible with case-insensitive matching
    pattern = r"(?im)^\s*(" + "|".join(re.escape(h) + r"s?" for h in headers) + r")\s*:?\s*$"
    
    current_section = "Header"
    sections[current_section] = ""
    
    for line in text.split('\n'):
        line = line.strip()
        # Check if line matches any header
        match = re.fullmatch(pattern, line)
        if match:
            current_section = match.group(1).strip().rstrip(':')
            sections[current_section] = ""
        else:
            sections[current_section] += line + "\n"
    
    sections = {k: v.strip() for k, v in sections.items() if v.strip()}
    
    if "Header" in sections:
        header_content = sections.pop("Header")
        if any(x in header_content.lower() for x in ["@", "http", "linkedin", "github", "phone"]):
            sections["Contact"] = header_content
        else:
            sections["Profile"] = header_content
            
    return sections

def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def extract_text_from_pdf(file_path_or_buffer) -> str:
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(file_path_or_buffer)
        for page in pdf_reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
    return text.strip()

def extract_text_from_docx(file_path_or_buffer) -> str:
    """Extract text from DOCX file"""
    try:
        doc = Document(file_path_or_buffer)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text)
    except Exception as e:
        print(f"Error extracting DOCX text: {e}")
        return ""

def extract_contact_info(text):
    contact = {}
    lines = text.strip().splitlines()
    if lines:
        first_line = lines[0].strip()
        if not any(c in first_line for c in ["@", "http", "://", "www."]):
            contact["name"] = first_line
    
    if "name" not in contact:
        entities = ner.extract_entities(text)
        if "PER" in entities:
            contact["name"] = " ".join(entities["PER"][:2])

    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    if match:
        contact["email"] = match.group(0)

    phone_match = re.search(r"(\+91[-\s]?)?[0-9]{10}", text)
    if phone_match:
        contact["phone"] = phone_match.group(0).strip()

    linkedin_match = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[^\s]+", text)
    if linkedin_match:
        contact["linkedin"] = linkedin_match.group(0)

    github_match = re.search(r"(https?://)?(www\.)?github\.com/[^\s]+", text)
    if github_match:
        contact["github"] = github_match.group(0)

    return contact

def extract_education_info(text):
    education = []
    sections = split_sections(text)
    
    if "Education" in sections:
        edu_text = sections["Education"]
        edu_pattern = r"(?i)((?:B\.?Tech|B\.?E|B\.?Sc|B\.?Com|B\.?A|M\.?Tech|M\.?Sc|M\.?Com|M\.?A|Ph\.?D|Bachelor|Master|Diploma|PGDM|MBA|MCA)\b[^@\n]*)(?:@|at|,)?\s*([^\n,\(\)]*)(?:\(([^\)\n]*)\)|-\s*(.*))?"
        
        matches = re.finditer(edu_pattern, edu_text)
        for match in matches:
            degree = match.group(1).strip()
            institution = match.group(2).strip()
            dates = match.group(3) or match.group(4)
            dates = dates.strip() if dates else None
            
            # Add the fallback date extraction here
            if not dates:
                fallback = re.search(r"\b(20\d{2})\b", match.group(0))
                if fallback:
                    dates = fallback.group(1)
            
            institution = re.sub(r"\s+", " ", institution)
            institution = re.sub(r"\s*,\s*", ", ", institution)
            
            education.append({
                "degree": degree,
                "institution": institution if institution else None,
                "dates": dates if dates else None
            })
    
    return education

def extract_skills(text):
    skills_found = set()
    sections = split_sections(text)
    
    skills_text = ""
    for section in ["Skills", "Technical Skills", "Key Skills"]:
        if section in sections:
            skills_text += sections[section] + "\n"
    
    for skill, patterns in SKILL_KEYWORDS.items():
        for pattern in patterns:
            if re.search(r"\b" + pattern + r"\b", skills_text, re.IGNORECASE):
                skills_found.add(skill)
    
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
    categories = SKILL_CATEGORIES
    
    output = []
    for category, patterns in categories.items():
        skills_in_category = []
        for skill in skills_list:
            for pattern in patterns:
                if re.search(r"\b" + pattern + r"\b", skill.lower()):
                    skills_in_category.append(skill)
                    break
        
        if skills_in_category:
            output.append(f"{category}: {', '.join(sorted(set(skills_in_category)))}")
    
    return "\n".join(output)

def extract_projects(text):
    projects = []
    sections = split_sections(text)
    
    if "Projects" in sections:
        proj_text = sections["Projects"]
        project_items = re.split(r"\n\s*•\s*|\n\s*\d+\.\s*", proj_text)
        project_items = [re.sub(r"\s+", " ", item.strip()) for item in project_items if item.strip()]
        
        for item in project_items:
            # Remove any remaining bullet points
            item = re.sub(r"^•\s*", "", item)
            projects.append(item)
    
    return projects

def extract_internships(text):
    internships = []
    sections = split_sections(text)
    
    if "Internships" in sections:
        intern_text = sections["Internships"]
        patterns = [
            r"(?i)(.+?)\s*[-–]\s*(.+?)\s*\((.+?)\)\s*(.*)",  # Company - Role (Duration) Desc
            r"(?i)(.+?)\s*[-–]\s*(.+?)\s*\[(.+?)\]\s*(.*)",  # Company - Role [Duration] Desc
            r"(?i)(.+?)\s*,\s*(.+?)\s*,\s*(.+?)\s*(.*)"      # Company, Role, Duration, Desc
        ]
        
        for line in intern_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('•'):
                continue
                
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    company = match.group(1).strip()
                    role = match.group(2).strip()
                    duration = match.group(3).strip()
                    description = match.group(4).strip() if match.group(4) else ""
                    
                    internships.append({
                        "company": company,
                        "role": role,
                        "duration": duration,
                        "description": description
                    })
                    break
    
    return internships

def extract_certifications(text):
    certs = []
    sections = split_sections(text)
    
    if "Certifications" in sections:
        cert_text = sections["Certifications"]
        cert_items = re.split(r"\n\s*•\s*", cert_text)
        cert_items = [re.sub(r"\s+", " ", item.strip()) for item in cert_items if item.strip()]
        
        for item in cert_items:
            # Remove any remaining bullet points
            item = re.sub(r"^•\s*", "", item)
            certs.append(item)
    
    return certs

def combine_structured_resume(resume_data: dict, section_weights: dict = None) -> str:
    """
    Combine structured resume data into a single text for scoring.
    This function handles resume data processing, not scoring.
    """
    from collections import defaultdict
    
    if section_weights is None:
        section_weights = {
            'skills': 0.6,
            'experience': 0.25,
            'projects': 0.1,
            'education': 0.05
        }
    
    combined = defaultdict(list)
    
    for section, content in resume_data.items():
        if not content:
            continue
            
        if isinstance(content, list):
            if all(isinstance(x, str) for x in content):
                combined[section].extend(content)
            elif all(isinstance(x, dict) for x in content):
                for item in content:
                    combined[section].extend(
                        f"{k}: {v}" for k, v in item.items() if v
                    )
        elif isinstance(content, str):
            combined[section].append(content)
    
    # Apply section weights with exponential boosting
    weighted_text = []
    for section, text_parts in combined.items():
        weight = section_weights.get(section, 1.0)
        if weight > 0:
            section_text = " ".join(text_parts)
            weighted_text.append((section_text + " ") * int(weight * 15))
    
    # Use the clean_text function from this module
    return clean_text(" ".join(weighted_text))

def parse_resume(file_path_or_buffer, file_type=None):
    """Determine file type and extract text accordingly"""
    if file_type is None:
        if hasattr(file_path_or_buffer, 'name'):
            ext = os.path.splitext(file_path_or_buffer.name)[-1].lower()
            file_type = 'docx' if ext == '.docx' else 'txt' if ext == '.txt' else 'pdf'
    
    if file_type == 'docx':
        text = extract_text_from_docx(file_path_or_buffer)
    elif file_type == 'txt':
        # For TXT files, just read the content directly
        with open(file_path_or_buffer, 'r', encoding='utf-8') as f:
            text = f.read()
    else:  # default to PDF
        text = extract_text_from_pdf(file_path_or_buffer)
    
    sections = split_sections(text)
    global_entities = ner.extract_entities(text)

    # Extract entities from all section texts combined
    all_section_texts = "\n\n".join(sections.values())
    batch_entities = ner.extract_entities(all_section_texts)

    # Filter relevant entities for each section
    section_entities = {}
    # Map entity labels present in each section using cleaned entities for stability
    cleaned_batch = clean_entities(batch_entities.get("entities", {})) if isinstance(batch_entities, dict) else {}
    for section_name, section_text in sections.items():
        present_labels = {}
        for label, words in cleaned_batch.items():
            hits = [w for w in words if w.lower() in section_text.lower()]
            if hits:
                present_labels[label] = hits
        section_entities[section_name] = present_labels
    return {
        "metadata": {
            "processing_date": datetime.now().isoformat(),
            "file_type": file_type
        },
        "raw_text": text,  # Add raw text for scoring
        "sections": sections,
        "global_entities": global_entities,
        "section_entities": section_entities, 
        "contact": extract_contact_info(text),
        "education": extract_education_info(text),
        "skills": extract_skills(text),
        "projects": extract_projects(text),
        "certifications": extract_certifications(text),
        "internships": extract_internships(text)  # THIS WAS MISSING
    }

def print_parsed_resume(parsed_data):
    max_width = 80
    
    def print_section(title, content):
        divider = "=" * max_width
        title_line = f" {title.upper()} ".center(max_width, "=")
        print(f"\n{divider}\n{title_line}\n{divider}\n{content}")
    
    print_section("RESUME ANALYSIS RESULTS", 
          f"Processed on: {parsed_data['metadata']['processing_date']}\n"
          f"File type: {parsed_data['metadata']['file_type']}")
    
    contact = parsed_data["contact"]
    contact_str = "\n".join(f"{k.title():<12}: {v}" for k, v in contact.items())
    print_section("CONTACT INFORMATION", contact_str)
    
    if parsed_data["education"]:
        edu_str = ""
        for i, edu in enumerate(parsed_data["education"], 1):
            edu_str += (f"{i}. {edu.get('degree', 'N/A')}\n"
                      f"   @ {edu.get('institution', 'N/A')}\n"
                      f"   {edu.get('dates', 'N/A')}\n\n")
        print_section("EDUCATION", edu_str.strip())

    # ADD THIS SECTION FOR INTERNSHIPS
    if parsed_data.get("internships"):
        intern_str = ""
        for i, intern in enumerate(parsed_data["internships"], 1):
            intern_str += (f"{i}. {intern['role']} @ {intern['company']}\n"
                         f"   Duration: {intern['duration']}\n"
                         f"   {intern.get('description', '')}\n\n")
        print_section("INTERNSHIPS", intern_str.strip())
        
    if parsed_data["skills"]:
        print_section("TECHNICAL SKILLS", 
              format_skills_output(parsed_data["skills"]))
    
    if parsed_data.get("certifications"):
        cert_str = "\n".join(f"• {cert}" for cert in parsed_data["certifications"])
        print_section("CERTIFICATIONS", cert_str)
    
    if parsed_data.get("projects"):
        proj_str = ""
        for i, proj in enumerate(parsed_data["projects"][:6], 1):
            proj_str += f"{i}. {proj}\n"
        if len(parsed_data["projects"]) > 6:
            proj_str += f"... (+{len(parsed_data['projects'])-6} more items)"
        print_section("PROJECTS", proj_str.strip())
    
    other_sections = [s for s in parsed_data["sections"] 
                     if s not in ["Contact", "Skills", "Education", "Certifications", "Projects", "Internships"]]
    if other_sections:
        other_str = "\n".join(f"• {s}" for s in other_sections)
        print_section("OTHER SECTIONS", other_str)
    
    if "ORG" in parsed_data["global_entities"]:
        orgs = clean_entities(parsed_data["global_entities"])["ORG"]
        # Normalize and deduplicate
        normalized_orgs = sorted(set(o.lower().strip().replace(".", "") for o in orgs if len(o) > 2))
        print_section("IDENTIFIED ORGANIZATIONS", ", ".join(normalized_orgs))

    sections_str = ""
    for section, content in parsed_data["sections"].items():
        if section.lower() in ["contact", "declaration"]:
            continue
            
        sections_str += f"\n► {section.upper()}:\n"
        sections_str += "-"*(len(section)+3) + "\n"
        
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        preview = "\n".join(lines[:4])
        sections_str += f"{preview}\n"
        
        entities = parsed_data.get("section_entities", {}).get(section, {})
        if entities:
            section_entities = []
            for label, items in entities.items():
                section_entities.extend(items)
            if section_entities:
                sections_str += "\nKey terms: "
                sections_str += f"{', '.join(section_entities[:5])}"
                if len(section_entities) > 5:
                    sections_str += f" (+{len(section_entities)-5} more)"
                sections_str += "\n"

    
    print_section("SECTION OVERVIEW", sections_str.strip())

if __name__ == "__main__":
    sample_pdf_path = r"D:\uday\Vscode\Projects\AI_resume_evaluator\resumes\resume_webdev.pdf"
    
    parsed_data = parse_resume(sample_pdf_path)
    parsed_data["global_entities"] = clean_entities(parsed_data["global_entities"])
    
    
    print_parsed_resume(parsed_data)