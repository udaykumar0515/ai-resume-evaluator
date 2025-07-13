import re
from typing import Dict, List, Union

def suggest_resume_improvements(resume_data: Dict[str, Union[str, List]], jd_text: str = "") -> Dict[str, List[str]]:
    """
    Suggest improvements based on resume structure and optional job description.
    Returns a dictionary with suggestion categories.
    """

    suggestions = {
        "general_tips": [],
        "section_tips": [],
        "job_match_tips": []
    }

    # --- GENERAL FORMAT SUGGESTIONS ---
    total_words = 0
    for value in resume_data.values():
        if isinstance(value, str):
            total_words += len(value.split())
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    total_words += len(item.split())
                elif isinstance(item, dict):
                    total_words += sum(len(str(v).split()) for v in item.values())

    if total_words < 200:
        suggestions["general_tips"].append("Your resume seems too short. Consider adding more details.")
    elif total_words > 1000:
        suggestions["general_tips"].append("Your resume might be too long. Try keeping it concise and relevant.")

    if 'objective' in resume_data and isinstance(resume_data['objective'], str):
        if len(resume_data['objective'].split()) < 10:
            suggestions["section_tips"].append("Your career objective seems too short. Add more clarity about your goals.")
        elif len(resume_data['objective'].split()) > 50:
            suggestions["section_tips"].append("Your career objective is too long. Keep it concise and to the point.")

    # --- SECTION-BASED SUGGESTIONS ---
    if not resume_data.get("projects"):
        suggestions["section_tips"].append("Add at least 1-2 projects to showcase your hands-on experience.")

    if not resume_data.get("experience"):
        suggestions["section_tips"].append("Include internships, part-time jobs, or freelance experience if any.")

    if not resume_data.get("skills"):
        suggestions["section_tips"].append("Mention your technical or soft skills clearly.")

    if not resume_data.get("education"):
        suggestions["section_tips"].append("Include your education background.")

    if "skills" in resume_data and isinstance(resume_data["skills"], list):
        if len(resume_data["skills"]) < 5:
            suggestions["section_tips"].append("List more relevant skills to show your competency.")

    # --- JOB DESCRIPTION BASED SUGGESTIONS ---
    if jd_text:
        jd_text = jd_text.lower()
        jd_keywords = set(re.findall(r"\b\w+\b", jd_text))

        resume_text = ""
        for v in resume_data.values():
            if isinstance(v, str):
                resume_text += " " + v.lower()
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        resume_text += " " + item.lower()
                    elif isinstance(item, dict):
                        resume_text += " " + " ".join(str(val).lower() for val in item.values())

        missing_keywords = []
        for keyword in jd_keywords:
            if keyword in ["and", "or", "the", "with", "you", "will", "our", "your"]:
                continue
            if keyword not in resume_text:
                missing_keywords.append(keyword)

        if len(missing_keywords) > 0:
            suggestions["job_match_tips"].append(
                "Try to include more role-relevant keywords from the job description (e.g., "
                + ", ".join(missing_keywords[:5]) + ("..." if len(missing_keywords) > 5 else "") + ")."
            )

    return suggestions
