import re
from typing import List, Tuple, Dict, Union, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import unicodedata
from pathlib import Path
import json

class ResumeMatcher:
    """
    Resume-JD matcher that automatically prioritizes skills and experience.
    Handles both raw text resumes and structured data.
    """
    
    # Default field weights with strong emphasis on skills and experience
    DEFAULT_WEIGHTS = {
        'skills': 0.5,          # Highest priority
        'experience': 0.3,      # Second highest priority
        'projects': 0.1,
        'education': 0.05,
        'certifications': 0.05
    }
    
    # Fields considered as "skills" for skill-specific matching
    SKILL_FIELDS = {'skills', 'technologies', 'programming', 'tools'}
    
    # Fields considered as "experience" 
    EXPERIENCE_FIELDS = {'experience', 'work', 'employment', 'internships'}
    
    def __init__(self, min_skill_match: float = 0.7):
        """
        Initialize with skill matching threshold.
        
        Args:
            min_skill_match: Minimum similarity threshold to consider skills matched (0-1)
        """
        self.min_skill_match = min_skill_match
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))

    @staticmethod
    def clean_text(text: str) -> str:
        """Normalize and clean text."""
        if not text:
            return ""
        text = unicodedata.normalize("NFKC", str(text))
        text = re.sub(r"\n+", " ", text)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s-]", "", text.lower())
        return text.strip()

    def preprocess_resume(self, resume: Union[str, Dict, Path]) -> Dict[str, str]:
        """
        Normalize input resume to structured format with emphasized skills/experience.
        
        Args:
            resume: Can be:
                   - Path to JSON file
                   - Raw text string
                   - Already parsed dictionary
                   
        Returns:
            Dictionary with weighted text sections
        """
        # Handle file path input
        if isinstance(resume, (str, Path)) and str(resume).endswith('.json'):
            with open(resume, 'r') as f:
                resume = json.load(f)
        
        # Handle raw text input
        if isinstance(resume, str):
            return {'raw_text': self.clean_text(resume)}
        
        # Process structured data
        if isinstance(resume, dict):
            processed = {}
            
            # Extract and weight sections
            for field, value in resume.items():
                clean_field = field.lower()
                
                # Combine all skill-related fields
                if clean_field in self.SKILL_FIELDS:
                    processed.setdefault('skills', [])
                    if isinstance(value, list):
                        processed['skills'].extend(value)
                    elif isinstance(value, str):
                        processed['skills'].append(value)
                
                # Combine all experience-related fields
                elif clean_field in self.EXPERIENCE_FIELDS:
                    processed.setdefault('experience', [])
                    if isinstance(value, list):
                        if all(isinstance(x, str) for x in value):
                            processed['experience'].extend(value)
                        elif all(isinstance(x, dict) for x in value):
                            for item in value:
                                processed['experience'].append(
                                    f"{item.get('title', '')} {item.get('description', '')}"
                                )
                    elif isinstance(value, str):
                        processed['experience'].append(value)
                
                # Handle other fields normally
                else:
                    if isinstance(value, list):
                        processed[field] = " ".join(str(x) for x in value)
                    else:
                        processed[field] = str(value)
            
            return processed
        
        raise ValueError("Unsupported resume format")

    def prepare_weighted_text(self, resume_data: Dict[str, str]) -> str:
        """
        Combine resume sections with automatic weighting based on field importance.
        
        Args:
            resume_data: Preprocessed resume data
            
        Returns:
            Weighted text string with emphasized skills/experience
        """
        weighted_parts = []
        
        for field, weight in self.DEFAULT_WEIGHTS.items():
            if field in resume_data:
                text = resume_data[field]
                if isinstance(text, list):
                    text = " ".join(text)
                
                # Apply weighting by repeating important sections
                repeat_factor = max(1, int(weight * 10))
                weighted_parts.extend([self.clean_text(text)] * repeat_factor)
        
        # Include raw text if present (for unstructured resumes)
        if 'raw_text' in resume_data and not weighted_parts:
            return self.clean_text(resume_data['raw_text'])
        
        return " ".join(weighted_parts)

    def calculate_skill_match(self, jd_text: str, resume_text: str) -> float:
        """
        Calculate specialized skill matching score.
        
        Args:
            jd_text: Job description text
            resume_text: Resume text with emphasized skills
            
        Returns:
            Skill match ratio (0-1)
        """
        # Extract potential skills (words with capital letters or specific patterns)
        jd_skills = set(re.findall(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*\b|\b\w{3,}ing\b|\b\w{3,}s\b)", jd_text))
        resume_skills = set(re.findall(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*\b|\b\w{3,}ing\b|\b\w{3,}s\b)", resume_text))
        
        if not jd_skills:
            return 0.0
            
        matched = jd_skills & resume_skills
        return len(matched) / len(jd_skills)

    def match_resume_to_jd(
        self,
        jd_text: str,
        resume: Union[str, Dict, Path],
        return_skill_match: bool = False
    ) -> Union[float, Tuple[float, float]]:
        """
        Match a single resume to job description with skill/experience priority.
        
        Args:
            jd_text: Job description text
            resume: Resume in any supported format
            return_skill_match: Whether to return separate skill match score
            
        Returns:
            Similarity score (0-1) or tuple (overall_score, skill_match_score)
        """
        # Preprocess inputs
        clean_jd = self.clean_text(jd_text)
        processed_resume = self.preprocess_resume(resume)
        weighted_resume_text = self.prepare_weighted_text(processed_resume)
        
        # Calculate overall similarity
        texts = [clean_jd, weighted_resume_text]
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        overall_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0][0]
        
        if not return_skill_match:
            return overall_score
            
        # Calculate specialized skill match
        skill_score = self.calculate_skill_match(clean_jd, weighted_resume_text)
        return (overall_score, skill_score)

    def match_batch(
        self,
        jd_text: str,
        resumes: List[Union[str, Dict, Path]],
        threshold: float = 0.5
    ) -> List[Tuple[int, float, float]]:
        """
        Match multiple resumes to a job description with skill priority.
        
        Args:
            jd_text: Job description text
            resumes: List of resumes in any supported format
            threshold: Minimum score to consider
            
        Returns:
            List of tuples (index, overall_score, skill_score)
        """
        results = []
        clean_jd = self.clean_text(jd_text)
        
        # Preprocess all resumes first
        processed_resumes = [self.preprocess_resume(r) for r in resumes]
        weighted_texts = [self.prepare_weighted_text(r) for r in processed_resumes]
        
        # Calculate TF-IDF scores
        texts = [clean_jd] + weighted_texts
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        overall_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
        
        # Calculate skill matches
        for idx, (score, resume_text) in enumerate(zip(overall_scores, weighted_texts)):
            skill_score = self.calculate_skill_match(clean_jd, resume_text)
            if score >= threshold or skill_score >= self.min_skill_match:
                results.append((idx, float(score), float(skill_score)))
        
        return sorted(results, key=lambda x: (x[2], x[1]), reverse=True)  # Sort by skill score then overall