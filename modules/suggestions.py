import re
from typing import Dict, List, Union, Set, Tuple

# ===== CONSTANTS =====
SKILL_SYNONYMS = {
    "machine learning": ["ml", "machine learning", "ai", "deep learning"],
    "python": ["python", "python3", "py"],
    "docker": ["docker", "containers"],
    "aws": ["aws", "amazon web services"],
}

STOPWORDS = {"and", "or", "the", "with", "you", "will", "our", "your", "their", "this"}

CRITICAL_SECTIONS = ["skills", "experience"]
HIGH_SECTIONS = ["projects", "education"]

WEAK_VERBS = ["did", "made", "helped", "worked on", "was involved in"]
STRONG_VERBS = ["developed", "implemented", "designed", "optimized", "led", "built"]

BUZZWORDS = {
    "synergy", "self-starter", "go-getter", "think outside the box",
    "hard worker", "team player", "detail-oriented", "fast learner"
}

GENERIC_PHRASES = {
    "responsible for": "Replace with specific achievements (e.g., 'Increased X by Y%')",
    "worked with": "Specify your contribution (e.g., 'Built X using Y')",
    "assisted in": "Quantify impact (e.g., 'Reduced processing time by 30%')",
}

# ===== HELPER FUNCTIONS =====
def normalize_keyword(keyword: str) -> str:
    """Standardize terms using synonyms (e.g., 'ML' → 'machine learning')."""
    keyword = keyword.lower()
    for standard_term, variants in SKILL_SYNONYMS.items():
        if keyword in variants:
            return standard_term
    return keyword

def extract_keywords(text: str) -> Set[str]:
    """Extract and normalize keywords from text, filtering noise."""
    words = set(re.findall(r"\b[a-z0-9]{3,}\b", text.lower()))
    return {normalize_keyword(w) for w in words if w not in STOPWORDS}

def detect_achievements(text: str) -> bool:
    """Check if text contains quantifiable results or outcomes."""
    return bool(re.search(r"\d+%|\$?\d+\+?|improved|reduced|increased", text.lower()))

# ===== MAIN FUNCTION =====
def suggest_resume_improvements(
    resume_data: Dict[str, Union[str, List]], 
    jd_text: str = ""
) -> Dict[str, List[str]]:
    """
    Suggest resume improvements with prioritized, actionable feedback.
    Returns structured suggestions by priority level.
    """
    suggestions = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": []
    }

    # --- General Checks ---
    total_words = sum(
        len(str(v).split()) if isinstance(v, str) 
        else sum(len(str(item).split()) for item in v)
        for v in resume_data.values()
    )
    if total_words < 200:
        suggestions["critical"].append("Resume too short (under 200 words). Add more details.")
    elif total_words > 800:
        suggestions["medium"].append("Resume may be too long (over 800 words). Keep it concise.")

    # --- Section Presence Checks ---
    for section in CRITICAL_SECTIONS:
        if not resume_data.get(section):
            suggestions["critical"].append(f"Missing critical section: '{section}'.")
    
    for section in HIGH_SECTIONS:
        if not resume_data.get(section):
            suggestions["high"].append(f"Add '{section}' section to strengthen resume.")

    # ==== SKILL ANALYSIS ====
    if "skills" in resume_data:
        skills = [s.lower() for s in resume_data["skills"] if isinstance(s, str)]
        
        # Skill relevance to JD
        if jd_text:
            jd_keywords = extract_keywords(jd_text)
            irrelevant_skills = [
                skill for skill in skills 
                if not any(normalize_keyword(skill) in jd_keywords)
                and skill not in BUZZWORDS
            ][:3]  # Limit to top 3 examples
            if irrelevant_skills:
                suggestions["medium"].append(
                    f"Potentially irrelevant skills for this JD: {', '.join(irrelevant_skills)}. "
                    "Consider tailoring to the job description."
                )

    # ==== PROJECT/EXPERIENCE CHECKS ====
    for section in ["projects", "experience"]:
        if section in resume_data:
            for item in resume_data[section]:
                if isinstance(item, dict):
                    desc = str(item.get("description", ""))
                    
                    # Generic phrases
                    for phrase, suggestion in GENERIC_PHRASES.items():
                        if phrase in desc.lower():
                            suggestions["high"].append(suggestion)
                    
                    # Achievements check
                    if not detect_achievements(desc):
                        suggestions["high"].append(
                            f"Add quantifiable results to '{item.get('name', section)}' "
                            "(e.g., 'Improved performance by 20%')."
                        )
                    
                    # Buzzwords
                    found_buzzwords = [b for b in BUZZWORDS if b in desc.lower()]
                    if found_buzzwords:
                        suggestions["low"].append(
                            f"Replace buzzwords like '{found_buzzwords[0]}' with concrete examples."
                        )

    # ==== JD-SPECIFIC SUGGESTIONS ====
    if jd_text:
        jd_keywords = extract_keywords(jd_text)
        resume_keywords = extract_keywords(" ".join(str(v) for v in resume_data.values()))
        missing_keywords = jd_keywords - resume_keywords
        
        if missing_keywords:
            top_missing = sorted(
                missing_keywords, 
                key=lambda k: jd_text.lower().count(k), 
                reverse=True
            )[:5]
            suggestions["critical"].append(
                "Missing key JD keywords: " + ", ".join(f"'{k}'" for k in top_missing)
            )

    # ==== FORMATTING/STYLE ====
    resume_text = " ".join(str(v) for v in resume_data.values()).lower()
    if " i " in resume_text or " my " in resume_text:
        suggestions["low"].append("Avoid first-person pronouns (use 'Developed X' not 'I developed X').")
    if not re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", resume_text):
        suggestions["critical"].append("No email found in contact info.")

    return {k: v for k, v in suggestions.items() if v}