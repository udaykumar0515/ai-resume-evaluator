# Fixed suggestions system that works with the existing modules
import re
import logging
from typing import Dict, List, Set, Any
from collections import defaultdict
from modules.text_constants import SKILL_SYNONYMS, IMPACT_VERBS, QUANTIFIABLE_METRICS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_jd_keywords(jd_text: str) -> Set[str]:
    """Extract relevant keywords from job description"""
    if not jd_text:
        return set()
    
    # Simple but effective keyword extraction
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.]{2,}\b', jd_text.lower())
    
    # Filter out common words and keep technical terms
    stopwords = {
        'and', 'the', 'for', 'with', 'you', 'will', 'our', 'team', 'work', 
        'experience', 'knowledge', 'skills', 'using', 'able', 'good', 'strong',
        'requirements', 'qualifications', 'preferred', 'required', 'must', 'should'
    }
    
    keywords = set()
    for word in words:
        if word not in stopwords and len(word) > 2:
            keywords.add(word)
    
    return keywords

def analyze_section_quality(section_name: str, content: str, jd_keywords: Set[str]) -> Dict[str, Any]:
    """Analyze individual section quality"""
    
    analysis = {
        "score": 0.0,
        "word_count": 0,
        "keyword_matches": 0,
        "issues": [],
        "strengths": [],
        "specific_suggestions": []
    }
    
    if not content or not isinstance(content, str):
        analysis["issues"].append("Section is empty or invalid")
        return analysis
    
    # Basic metrics
    analysis["word_count"] = len(content.split())
    content_lower = content.lower()
    
    # Keyword matching
    matched_keywords = [kw for kw in jd_keywords if kw in content_lower]
    analysis["keyword_matches"] = len(matched_keywords)
    
    # Section-specific analysis
    if section_name.lower() in ["skills", "technical skills", "key skills"]:
        return analyze_skills_section(content, jd_keywords, analysis)
    elif section_name.lower() in ["experience", "work experience", "internships", "employment"]:
        return analyze_experience_section(content, jd_keywords, analysis)
    elif section_name.lower() in ["projects", "personal projects", "academic projects"]:
        return analyze_projects_section(content, jd_keywords, analysis)
    elif section_name.lower() in ["education", "academic background"]:
        return analyze_education_section(content, analysis)
    else:
        # Generic section analysis
        base_score = min(100, 50 + (len(matched_keywords) * 10))
        analysis["score"] = base_score
    
    return analysis

def analyze_skills_section(content: str, jd_keywords: Set[str], analysis: Dict) -> Dict:
    """Detailed skills section analysis"""
    suggestions = []
    issues = []
    strengths = []
    
    # Check for skill categories 
    skill_categories_found = []
    for category, synonyms in SKILL_SYNONYMS.items():
        if any(skill in content.lower() for skill in synonyms):
            skill_categories_found.append(category)
    
    if skill_categories_found:
        strengths.append(f"Found skills in: {', '.join(skill_categories_found)}")
    
    # Check for missing JD keywords
    missing_skills = []
    for keyword in list(jd_keywords)[:5]:  # Check top 5 JD keywords
        if keyword not in content.lower():
            # Check if it's a technical skill
            if any(keyword in synonyms for synonyms in SKILL_SYNONYMS.values()):
                missing_skills.append(keyword)
    
    if missing_skills:
        suggestions.append(f"Consider adding these JD-relevant skills: {', '.join(missing_skills[:3])}")
    
    # Check for proficiency indicators
    if not re.search(r'\b(beginner|intermediate|advanced|expert|\d+\s*years?)\b', content.lower()):
        suggestions.append("Add proficiency levels like 'Python (Advanced)', 'React (2+ years)'")
    
    # Calculate score
    score = min(100, 40 + (len(skill_categories_found) * 15) + (len([k for k in jd_keywords if k in content.lower()]) * 5))
    
    analysis.update({
        "score": score,
        "issues": issues,
        "strengths": strengths,
        "specific_suggestions": suggestions,
        "skill_categories": skill_categories_found
    })
    
    return analysis

def analyze_experience_section(content: str, jd_keywords: Set[str], analysis: Dict) -> Dict:
    """Analyze experience section"""
    suggestions = []
    issues = []
    strengths = []
    
    # Check for quantifiable achievements
    has_metrics = any(re.search(pattern, content) for pattern in QUANTIFIABLE_METRICS)
    if has_metrics:
        strengths.append("Contains quantifiable achievements")
    else:
        suggestions.append("Add specific metrics: 'Increased efficiency by 40%', 'Managed team of 5'")
    
    # Check for action verbs
    weak_verbs_found = [verb for verb in IMPACT_VERBS["weak"] if verb in content.lower()]
    strong_verbs_found = [verb for verb in IMPACT_VERBS["strong"] if verb in content.lower()]
    
    if len(weak_verbs_found) > len(strong_verbs_found):
        suggestions.append(f"Replace weak terms like '{weak_verbs_found[0]}' with strong action verbs like 'developed', 'implemented'")
    
    # Check for JD keyword relevance
    jd_matches = len([kw for kw in jd_keywords if kw in content.lower()])
    if jd_matches < 3:
        suggestions.append("Include more job-relevant technologies and responsibilities")
    
    score = min(100, 50 + (20 if has_metrics else 0) + (min(jd_matches * 5, 30)))
    
    analysis.update({
        "score": score,
        "issues": issues,
        "strengths": strengths,
        "specific_suggestions": suggestions
    })
    
    return analysis

def analyze_projects_section(content: str, jd_keywords: Set[str], analysis: Dict) -> Dict:
    """Analyze projects section"""
    suggestions = []
    issues = []
    strengths = []
    
    # Split into individual projects
    projects = re.split(r'\n\s*[•\-\*]\s*|\n\s*\d+\.\s*', content)
    projects = [p.strip() for p in projects if len(p.strip()) > 20]
    
    if len(projects) < 2:
        suggestions.append("Add 2-3 projects to showcase diverse technical skills")
    
    project_has_tech = 0
    project_has_results = 0
    
    for project in projects:
        # Check for technology stack
        tech_mentioned = any(tech in project.lower() for tech_list in SKILL_SYNONYMS.values() for tech in tech_list)
        if tech_mentioned:
            project_has_tech += 1
        
        # Check for results/impact
        has_impact = any(re.search(pattern, project) for pattern in QUANTIFIABLE_METRICS)
        if has_impact:
            project_has_results += 1
    
    if project_has_tech > 0:
        strengths.append(f"{project_has_tech} projects mention specific technologies")
    else:
        suggestions.append("Specify technologies used in each project (e.g., 'Built with React, Node.js, MongoDB')")
    
    if project_has_results == 0:
        suggestions.append("Add project outcomes: user count, performance improvements, or GitHub stars")
    
    # JD alignment
    jd_matches = len([kw for kw in jd_keywords if kw in content.lower()])
    
    score = min(100, 30 + (len(projects) * 10) + (project_has_tech * 10) + (project_has_results * 15) + (jd_matches * 3))
    
    analysis.update({
        "score": score,
        "issues": issues,
        "strengths": strengths,
        "specific_suggestions": suggestions,
        "project_count": len(projects)
    })
    
    return analysis

def analyze_education_section(content: str, analysis: Dict) -> Dict:
    """Analyze education section"""
    suggestions = []
    issues = []
    strengths = []
    
    # Check for degree information
    has_degree = bool(re.search(r'\b(bachelor|master|phd|b\.?tech|m\.?tech|bsc|msc)\b', content.lower()))
    if has_degree:
        strengths.append("Educational qualification clearly mentioned")
    
    # Check for GPA/grades
    has_grades = bool(re.search(r'\b(\d\.\d+|gpa|cgpa|\d+%)\b', content.lower()))
    if not has_grades:
        suggestions.append("Consider adding GPA/CGPA if above 3.0/7.0")
    
    # Check for relevant coursework
    has_coursework = bool(re.search(r'\b(coursework|courses|subjects|specialization)\b', content.lower()))
    if not has_coursework:
        suggestions.append("Add relevant coursework that aligns with the job requirements")
    
    score = min(100, 60 + (20 if has_degree else 0) + (10 if has_grades else 0) + (10 if has_coursework else 0))
    
    analysis.update({
        "score": score,
        "issues": issues,
        "strengths": strengths,
        "specific_suggestions": suggestions
    })
    
    return analysis

def generate_enhanced_suggestions(resume_data: Dict, jd_text: str) -> Dict[str, Any]:
    """Generate comprehensive, personalized suggestions - FIXED VERSION"""
    
    try:
        logger.info("Starting personalized suggestion generation")
        
        # Extract JD keywords
        jd_keywords = extract_jd_keywords(jd_text)
        logger.info(f"Extracted {len(jd_keywords)} keywords from JD")
        
        # Initialize results structure
        results = {
            "overall_score": 0,
            "section_scores": {},
            "priority_suggestions": {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            },
            "personalized_advice": [],
            "style_feedback": [],
            "reasoning": {}
        }
        
        # Analyze each section
        total_weighted_score = 0
        section_weights = {"skills": 0.3, "experience": 0.25, "projects": 0.25, "education": 0.2}
        sections_analyzed = 0
        
        for section_name, content in resume_data.items():
            # Skip metadata sections
            if section_name in ['sections', 'metadata', 'global_entities', 'section_entities']:
                continue
                
            # Convert content to string for analysis
            if isinstance(content, list):
                content_str = ' '.join(str(item) for item in content if item)
            elif isinstance(content, dict):
                content_str = ' '.join(f"{k}: {v}" for k, v in content.items() if v)
            elif isinstance(content, str):
                content_str = content
            else:
                continue
            
            # Only analyze if content exists
            if content_str and content_str.strip():
                logger.info(f"Analyzing section: {section_name}")
                analysis = analyze_section_quality(section_name, content_str, jd_keywords)
                results["section_scores"][section_name] = analysis
                
                # Calculate weighted score
                weight = section_weights.get(section_name.lower(), 0.1)
                total_weighted_score += analysis["score"] * weight
                sections_analyzed += 1
                
                # Categorize suggestions by priority
                categorize_suggestions(analysis, results["priority_suggestions"], section_name)
        
        # Calculate overall score
        if sections_analyzed > 0:
            results["overall_score"] = min(100, total_weighted_score)
        else:
            results["overall_score"] = 0
        
        # Generate reasoning
        results["reasoning"] = generate_priority_reasoning(results, jd_keywords, sections_analyzed)
        
        # Add personalized advice
        results["personalized_advice"] = generate_personalized_advice(results, jd_keywords)
        
        logger.info(f"Generated suggestions with overall score: {results['overall_score']:.1f}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in generate_enhanced_suggestions: {e}")
        # Return a basic valid structure on error
        return {
            "overall_score": 0,
            "section_scores": {},
            "priority_suggestions": {
                "critical": [f"Error analyzing resume: {str(e)}"], 
                "high": [], 
                "medium": [], 
                "low": []
            },
            "personalized_advice": [f"Unable to analyze resume: {str(e)}"],
            "style_feedback": [],
            "reasoning": {"error": f"Analysis failed: {str(e)}"}
        }

def categorize_suggestions(analysis: Dict, priority_dict: Dict, section_name: str):
    """Categorize suggestions by priority"""
    score = analysis.get("score", 0)
    suggestions = analysis.get("specific_suggestions", [])
    
    for suggestion in suggestions:
        formatted_suggestion = f"[{section_name.title()}] {suggestion}"
        
        if score < 30:
            priority_dict["critical"].append(formatted_suggestion)
        elif score < 50:
            priority_dict["high"].append(formatted_suggestion)
        elif score < 70:
            priority_dict["medium"].append(formatted_suggestion)
        else:
            priority_dict["low"].append(formatted_suggestion)

def generate_priority_reasoning(results: Dict, jd_keywords: Set[str], sections_analyzed: int) -> Dict[str, str]:
    """Generate reasoning for priorities"""
    reasoning = {}
    
    overall_score = results.get("overall_score", 0)
    
    if overall_score < 40:
        reasoning["overall"] = f"Low score ({overall_score:.1f}%) indicates major gaps in JD alignment and resume quality"
    elif overall_score < 70:
        reasoning["overall"] = f"Moderate score ({overall_score:.1f}%) shows good foundation but needs targeted improvements"
    else:
        reasoning["overall"] = f"Strong score ({overall_score:.1f}%) with minor optimization opportunities"
    
    # Count suggestions by priority
    critical_count = len(results["priority_suggestions"].get("critical", []))
    high_count = len(results["priority_suggestions"].get("high", []))
    
    if critical_count > 0:
        reasoning["critical"] = f"Critical issues ({critical_count}) directly impact recruiter screening and ATS compatibility"
    
    if high_count > 0:
        reasoning["high"] = f"High priority items ({high_count}) significantly affect job matching potential"
    
    reasoning["analysis"] = f"Analyzed {sections_analyzed} resume sections against {len(jd_keywords)} job requirements"
    
    return reasoning

def generate_personalized_advice(results: Dict, jd_keywords: Set[str]) -> List[str]:
    """Generate personalized advice based on analysis"""
    advice = []
    
    section_scores = results.get("section_scores", {})
    
    # Find lowest scoring section
    if section_scores:
        lowest_section = min(section_scores.items(), key=lambda x: x[1].get("score", 0))
        section_name, section_data = lowest_section
        score = section_data.get("score", 0)
        
        if score < 50:
            advice.append(f"Focus on improving your {section_name} section first - it's currently your weakest area at {score:.1f}%")
    
    # JD alignment advice
    total_matches = sum(section.get("keyword_matches", 0) for section in section_scores.values())
    if total_matches < len(jd_keywords) * 0.3:
        advice.append(f"Only {total_matches} out of {len(jd_keywords)} key job requirements are reflected in your resume")
    
    return advice

# Main function for integration
def get_enhanced_suggestions(resume_data: Dict, jd_text: str = "") -> Dict[str, Any]:
    """Main function to get enhanced, personalized suggestions - FIXED VERSION"""
    try:
        return generate_enhanced_suggestions(resume_data, jd_text)
    except Exception as e:
        logger.error(f"Error in get_enhanced_suggestions: {e}")
        return {
            "overall_score": 0,
            "section_scores": {},
            "priority_suggestions": {
                "critical": [f"Analysis error: {str(e)}"], 
                "high": [], 
                "medium": [], 
                "low": []
            },
            "personalized_advice": [f"Unable to analyze resume: {str(e)}"],
            "style_feedback": [],
            "reasoning": {"error": f"System error: {str(e)}"}
        }