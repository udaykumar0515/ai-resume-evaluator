import re
from typing import Dict, List, Union, Set, Tuple
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')


# ===== CONSTANTS =====
SKILL_SYNONYMS = {
    # AI/ML
    "machine learning": ["ml", "machine learning", "ai", "deep learning", "dl", "neural networks", "nlp", "computer vision"],
    "python": ["python", "python3", "py", "pandas", "numpy", "scipy"],
    "tensorflow": ["tf", "tensorflow", "keras"],
    "pytorch": ["pytorch", "torch"],
    
    # Web Development
    "javascript": ["js", "javascript", "es6", "esnext", "typescript", "ts", "react.js", "next.js", "node.js", "express.js"],
    "react": ["react", "reactjs", "react.js", "redux", "context api"],
    "html/css": ["html", "html5", "css", "css3", "bootstrap", "tailwind", "sass", "scss", "less"],
    "web development": ["frontend", "backend", "fullstack", "responsive design", "ux/ui", "single page apps", "spa"],
    
    # Cloud/DevOps
    "aws": ["aws", "amazon web services", "s3", "ec2", "lambda", "rds"],
    "azure": ["azure", "microsoft azure", "azure functions", "cosmos db"],
    "docker": ["docker", "containers", "docker compose", "docker swarm"],
    "kubernetes": ["k8s", "kubernetes", "helm", "istio"],
    
    # Databases
    "sql": ["sql", "postgresql", "mysql", "mariadb", "sqlite", "pl/sql"],
    "mongodb": ["mongodb", "mongo", "documentdb"],
    "redis": ["redis", "redis cache"],
    
    # Programming Languages
    "java": ["java", "j2ee", "spring boot"],
    "c++": ["c++", "cpp", "c plus plus"],
    "c#": ["c#", "csharp", ".net"],
    "go": ["golang", "go"],
    
    # Tools
    "git": ["git", "github", "gitlab", "bitbucket", "version control"],
    "jenkins": ["jenkins", "ci/cd"],
    "terraform": ["terraform", "iac", "infrastructure as code"],
}

CUSTOM_STOPWORDS = {
    # Basic English
    "and", "or", "the", "with", "you", "will", "our", "your", "their", "this",
    "that", "have", "from", "which", "also", "they", "would", "about", "there",
    
    # JD Noise Words
    "work", "like", "into", "using", "need", "looking", "good", "make", "want",
    "able", "help", "team", "strong", "experience", "role", "knowledge", "understanding",
    "familiarity", "etc", "including", "within", "various", "ability", "focus",
    
    # Corporate Jargon
    "solutions", "leverage", "enable", "stakeholders", "align", "deliverables",
    "paradigm", "ecosystem", "holistic", "value-added", "best practices"
}
ENGLISH_STOPWORDS = set(stopwords.words('english'))
STOPWORDS = ENGLISH_STOPWORDS | CUSTOM_STOPWORDS

FUNDAMENTAL_SKILLS = {
    # CS Fundamentals
    "c", "c++", "data structures", "algorithms", "git", "oop", "debugging",
    "apis", "rest", "graphql", "json", "xml", "yaml", "linux", "bash",
    "unit testing", "integration testing", "agile", "scrum", "design patterns",
    
    # Math
    "linear algebra", "calculus", "statistics", "probability", "discrete math",
    
    # Core Concepts
    "operating systems", "compilers", "networking", "distributed systems",
    "security", "cryptography", "blockchain"
}

CRITICAL_SECTIONS = ["skills", "experience", "work experience", "internships", "employment history"]
HIGH_SECTIONS = ["projects", "education", "technical skills"]
OPTIONAL_SECTIONS = ["certifications", "publications", "volunteer", "languages", "awards", "hobbies", "patents"]

WEAK_VERBS = [
    "did", "made", "helped", "worked on", "was involved in", "participated in",
    "contributed to", "took part in", "assisted with", "provided support for",
    "exposed to", "familiar with", "handled", "managed", "responsible for"
]

STRONG_VERBS = [
    "developed", "implemented", "designed", "optimized", "led", "built", "achieved",
    "architected", "engineered", "spearheaded", "pioneered", "transformed",
    "accelerated", "automated", "streamlined", "orchestrated", "mentored",
    "reduced", "increased", "scaled", "secured", "debugged", "refactored",
    "deployed", "containerized", "migrated", "integrated", "published"
]

BUZZWORDS = {
    "synergy", "self-starter", "go-getter", "think outside the box",
    "hard worker", "team player", "detail-oriented", "fast learner",
    "passionate", "innovative", "results-driven", "ninja", "rockstar",
    "guru", "thought leadership", "dynamic", "proactive", "excellent communicator",
    "strategic thinker", "change agent", "disruptor", "visionary", "highly motivated",
    "outside the box", "bleeding edge", "value add", "client-centric", "customer-focused"
}

GENERIC_PHRASES = {
    "responsible for": "Replace with specific achievements (e.g., 'Increased X by Y%')",
    "worked with": "Specify your contribution (e.g., 'Built X using Y that reduced Z by 40%')",
    "assisted in": "Quantify impact (e.g., 'Reduced processing time by 30% through...')",
    "exposure to": "State your actual proficiency level (e.g., 'Advanced: 3+ years of X')",
    "involved in": "Describe leadership (e.g., 'Led team of 5 to deliver X ahead of schedule')",
    "helped with": "Concrete actions (e.g., 'Developed feature X using Y, improving metrics Z')",
    "basic knowledge of": "Explicit level (e.g., 'Intermediate: Built 3 projects using X')",
    "familiar with": "Replace with experience (e.g., 'Implemented X using Y in production')",
    "understanding of": "Demonstrate application (e.g., 'Applied X to solve Y problem')"
}

ACHIEVEMENT_TRIGGERS = {
    # Quantifiable Metrics
    r"\d+%": "percentages",
    r"\$\d+": "dollar amounts",
    r"\d+k|\d+,\d+": "large numbers (e.g., 10k users)",
    r"\d+x": "multiples",
    
    # Time Metrics
    r"\d+\s*(days|weeks|months|years)": "time periods",
    r"from\s+\d+\s+to\s+\d+": "time ranges",
    
    # Performance
    r"improved|increased|reduced|saved|boosted|optimized": "actionable results",
    r"efficiency|accuracy|performance|throughput|latency": "key metrics",
    
    # Scale
    r"scaled\s+from\s+\d+\s+to\s+\d+": "growth metrics",
    r"handled\s+\d+": "capacity numbers",
    
    # Technical
    r"api\s+calls|requests|queries": "throughput metrics",
    r"uptime|availability": "reliability stats"
}
CONTACT_PATTERNS = {
    "email": re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b"),
    "phone": re.compile(r"(\+\d{1,3}[-\.\s]?)?\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4}"),
    "linkedin": re.compile(r"(linkedin\.com/in/|@)[\w-]+"),
    "github": re.compile(r"github\.com/[\w-]+"),
}

# ===== HELPER FUNCTIONS =====
def normalize_keyword(keyword: str) -> str:
    """Standardize terms using synonyms."""
    keyword = keyword.lower()
    for standard_term, variants in SKILL_SYNONYMS.items():
        if keyword in variants:
            return standard_term
    return keyword

def extract_keywords(text: str) -> Set[str]:
    """Extract and normalize keywords from text."""
    words = set(re.findall(r"\b[a-z0-9]{3,}\b", text.lower()))
    return {normalize_keyword(w) for w in words if w not in STOPWORDS}

def detect_achievements(text: str) -> Tuple[bool, List[str]]:
    """Check for quantifiable results and return examples."""
    found = []
    for pattern, label in ACHIEVEMENT_TRIGGERS.items():
        if re.search(pattern, text.lower()):
            found.append(label)
    return bool(found), found

def analyze_contact_info(text: str) -> Dict[str, bool]:
    """Check for presence of contact information."""
    return {field: bool(pattern.search(text)) for field, pattern in CONTACT_PATTERNS.items()}

def suggest_resume_improvements(
    resume_data: Dict[str, Union[str, List]], 
    jd_text: str = ""
) -> Dict[str, List[str]]:
    """
    Generate prioritized resume improvement suggestions.
    Returns: {"critical": [], "high": [], "medium": [], "low": [], "strengths": [], "tips": []}
    """
    suggestions = defaultdict(list)
    resume_text = " ".join(str(v) for v in resume_data.values()).lower()
    contact_info = analyze_contact_info(resume_text)

    # Stopword-filtered keyword extraction
    jd_keywords = extract_keywords(jd_text) if jd_text else set()
    resume_keywords = extract_keywords(resume_text)
    overlapping_keywords = jd_keywords & resume_keywords

    # ==== CRITICAL CHECKS ====
    for section in CRITICAL_SECTIONS:
        if not resume_data.get(section):
            suggestions["critical"].append(f"Missing critical section: '{section}'")

    if not contact_info["email"]:
        suggestions["critical"].append("No email address found")
    if not contact_info.get("phone"):
        suggestions["high"].append("Add phone number for recruiter outreach")

    # ==== OPTIONAL SECTIONS ====
    if jd_text:
        for section in OPTIONAL_SECTIONS:
            if not resume_data.get(section):
                if "engineer" in jd_text.lower() and section == "certifications":
                    suggestions["medium"].append("Consider adding a 'certifications' section (e.g., AWS/Azure certs)")
                elif "research" in jd_text.lower() and section == "publications":
                    suggestions["medium"].append("Add 'publications' section if you have research papers")

    # ==== PROFILE LINKS ====
    if not contact_info["linkedin"]:
        suggestions["low"].append("Add LinkedIn profile for professional networking")
    if "github" not in contact_info and any(x in jd_text.lower() for x in ["developer", "engineer", "programming"]):
        suggestions["medium"].append("Add GitHub profile to showcase your code")

    # ==== JD-SPECIFIC ANALYSIS ====
    if jd_keywords:
        missing_keywords = jd_keywords - resume_keywords
        top_missing = sorted(missing_keywords, key=lambda k: jd_text.lower().count(k), reverse=True)[:5]
        if top_missing:
            suggestions["critical"].append(f"Missing JD keywords: {', '.join(top_missing)}")

    # ==== SKILL ANALYSIS ====
    if "skills" in resume_data:
        skills = [s.lower() for s in resume_data["skills"] if isinstance(s, str)]
        if jd_keywords:
            irrelevant_skills = [
                skill for skill in skills
                if (normalize_keyword(skill) not in jd_keywords
                    and skill.lower() not in BUZZWORDS
                    and skill.lower() not in FUNDAMENTAL_SKILLS)
            ][:3]
            if irrelevant_skills:
                suggestions["medium"].append(f"Potentially irrelevant skills: {', '.join(irrelevant_skills)}")

        suggestions["medium"].append("Format skills with proficiency levels (e.g., 'Python (Advanced)')")

    # ==== PROJECTS/EXPERIENCE ANALYSIS ====
    for section in ["projects", "experience"]:
        if section in resume_data:
            for item in resume_data[section]:
                if isinstance(item, dict):
                    desc = str(item.get("description", ""))
                    name = str(item.get("name", section))
                    has_achievements, achievement_types = detect_achievements(desc)
                    if not has_achievements:
                        suggestions["high"].append(f"Add quantifiable results to '{name}' section")

                    for phrase, suggestion in GENERIC_PHRASES.items():
                        if phrase in desc.lower():
                            suggestions["high"].append(suggestion)

                    if any(verb in desc.lower() for verb in WEAK_VERBS):
                        suggestions["medium"].append(
                            f"Replace weak verbs in '{name}' with strong action verbs")

    # ==== STYLE AND READABILITY ====
    found_buzzwords = [b for b in BUZZWORDS if b in resume_text]
    if found_buzzwords:
        suggestions["low"].append(f"Avoid buzzwords: {', '.join(found_buzzwords[:3])}")

    if " i " in resume_text or " my " in resume_text:
        suggestions["low"].append("Avoid first-person pronouns")

    if re.search(r"\bwas\s+\w+ed\b", resume_text):
        suggestions["medium"].append("Reduce passive voice (e.g., 'was implemented' → 'implemented')")

    # ==== NEW: STRENGTHS SECTION ====
    strengths = []
    if overlapping_keywords:
        strengths.append(f"Your resume contains relevant keywords from the JD: {', '.join(sorted(overlapping_keywords)[:5])}")
    if "projects" in resume_data and len(resume_data["projects"]) >= 3:
        strengths.append("Good number of projects showcasing hands-on experience")
    if resume_data.get("internships") and len(resume_data["internships"]) >= 2:
        strengths.append("Multiple internships reflect practical exposure")

    # ==== NEW: TIPS SECTION ====
    tips = []
    if len(resume_text.split()) < 250:
        tips.append("Resume is very short — try expanding on your experiences")
    if not contact_info.get("linkedin"):
        tips.append("Add a LinkedIn link to improve credibility")
    if "certifications" not in resume_data:
        tips.append("Add certifications to showcase additional qualifications")
    if not resume_data.get("projects"):
        tips.append("Add at least 1-2 projects — recruiters value them heavily")

    suggestions["strengths"] = strengths
    suggestions["tips"] = tips
    return dict(suggestions)
