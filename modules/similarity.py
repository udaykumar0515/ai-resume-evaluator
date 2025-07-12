import re
from typing import List, Tuple, Dict, Union, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import unicodedata
from collections import defaultdict
import numpy as np
from sentence_transformers import SentenceTransformer  # Optional for semantic similarity
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeMatcher:
    """
    Enhanced resume-job description matching system with multiple comparison methods
    and additional features like section weighting and match explanations.
    """
    
    def __init__(
        self,
        method: str = "tfidf",
        section_weights: Optional[Dict[str, float]] = None,
        min_skill_match: float = 0.7,
        use_gpu: bool = False
    ):
        """
        Initialize the matcher with configuration options.
        
        Args:
            method: 'tfidf' or 'embedding' (for semantic similarity)
            section_weights: Dictionary of weights for structured resume sections
            min_skill_match: Minimum similarity threshold to consider skills matched
            use_gpu: Whether to use GPU for embedding model if available
        """
        self.method = method
        self.section_weights = section_weights or {
            'skills': 0.4,
            'projects': 0.3,
            'education': 0.15,
            'experience': 0.15
        }
        self.min_skill_match = min_skill_match
        self.embedding_model = None
        
        if self.method == "embedding":
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                if use_gpu:
                    self.embedding_model = self.embedding_model.to('cuda')
            except ImportError:
                logger.warning("SentenceTransformers not installed. Falling back to TF-IDF.")
                self.method = "tfidf"

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Normalize and clean input text.
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned and normalized text
        """
        if not isinstance(text, str):
            return ""
            
        text = unicodedata.normalize("NFKC", text)
        text = re.sub(r"\n+", " ", text)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s-]", "", text)  # Remove special chars except spaces and hyphens
        return text.strip().lower()

    def combine_structured_resume(self, resume_data: Dict[str, Union[str, List]]) -> str:
        """
        Combine structured fields (skills, projects, etc.) into one string for similarity comparison.
        Applies section weights if specified.
        
        Args:
            resume_data: Dictionary containing resume sections
            
        Returns:
            Combined and weighted resume text
        """
        combined_parts = defaultdict(list)
        
        for field, value in resume_data.items():
            if not value:
                continue
                
            if isinstance(value, list):
                if all(isinstance(item, str) for item in value):
                    # Simple string list (like skills)
                    combined_parts[field].extend(value)
                elif all(isinstance(item, dict) for item in value):
                    # List of dictionaries (like projects or experience)
                    for item in value:
                        combined_parts[field].extend(str(v) for v in item.values() if v)
            elif isinstance(value, str):
                combined_parts[field].append(value)
        
        # Apply section weights if specified
        if self.section_weights:
            weighted_text = []
            for field, text_parts in combined_parts.items():
                weight = self.section_weights.get(field, 1.0)
                if weight > 0:
                    section_text = " ".join(text_parts)
                    # Repeat text based on weight (simplified approach)
                    weighted_text.extend([section_text] * int(weight * 10))
            return self.clean_text(" ".join(weighted_text))
        else:
            return self.clean_text(" ".join(" ".join(parts) for parts in combined_parts.values()))

    def compute_tfidf_similarity(self, jd_text: str, resume_texts: List[str]) -> List[float]:
        """
        Compute cosine similarity scores between JD and multiple resumes using TF-IDF.
        
        Args:
            jd_text: Job description text
            resume_texts: List of resume texts
            
        Returns:
            List of similarity scores
        """
        documents = [self.clean_text(jd_text)] + [self.clean_text(resume) for resume in resume_texts]
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(documents)
        scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        return [float(round(score, 4)) for score in scores]

    def compute_embedding_similarity(self, jd_text: str, resume_texts: List[str]) -> List[float]:
        """
        Compute cosine similarity scores between JD and multiple resumes using sentence embeddings.
        
        Args:
            jd_text: Job description text
            resume_texts: List of resume texts
            
        Returns:
            List of similarity scores
        """
        if not self.embedding_model:
            raise ValueError("Embedding model not initialized")
            
        documents = [self.clean_text(jd_text)] + [self.clean_text(resume) for resume in resume_texts]
        embeddings = self.embedding_model.encode(documents)
        scores = cosine_similarity(embeddings[0:1], embeddings[1:]).flatten()
        return [float(round(score, 4)) for score in scores]

    def analyze_matches(self, jd_text: str, resume_text: str) -> Dict[str, Union[float, List[str]]]:
        """
        Analyze matches between JD and resume to identify key overlapping terms.
        
        Args:
            jd_text: Job description text
            resume_text: Resume text
            
        Returns:
            Dictionary with match analysis including overlapping terms
        """
        jd_clean = self.clean_text(jd_text)
        resume_clean = self.clean_text(resume_text)
        
        # Tokenize and find overlaps
        jd_tokens = set(re.findall(r"\b[\w-]+\b", jd_clean))
        resume_tokens = set(re.findall(r"\b[\w-]+\b", resume_clean))
        overlapping = jd_tokens & resume_tokens
        
        # Find bigram overlaps
        jd_bigrams = set(zip(jd_tokens, list(jd_tokens)[1:]))
        resume_bigrams = set(zip(resume_tokens, list(resume_tokens)[1:]))
        overlapping_bigrams = jd_bigrams & resume_bigrams
        
        return {
            "overlapping_terms": list(overlapping),
            "overlapping_bigrams": [" ".join(bigram) for bigram in overlapping_bigrams],
            "match_percentage": len(overlapping) / max(1, len(jd_tokens))
        }

    def get_similarity_score(
        self,
        jd_text: str,
        resumes: List[Union[str, Dict]],
        mode: str = "raw",
        return_analysis: bool = False
    ) -> List[Tuple[int, float, Optional[Dict]]]:
        """
        Main entry point for getting similarity scores between JD and resumes.
        
        Args:
            jd_text: Job description text
            resumes: List of resumes (raw text or structured dicts)
            mode: 'raw' for text resumes, 'structured' for parsed resumes
            return_analysis: Whether to include match analysis
            
        Returns:
            List of tuples containing (index, score, analysis_dict)
        """
        if not jd_text or not resumes:
            return []
            
        try:
            if mode == "structured":
                processed_resumes = [self.combine_structured_resume(r) for r in resumes]
            else:
                processed_resumes = [self.clean_text(r) if isinstance(r, str) else "" for r in resumes]

            if self.method == "embedding":
                scores = self.compute_embedding_similarity(jd_text, processed_resumes)
            else:
                scores = self.compute_tfidf_similarity(jd_text, processed_resumes)
                
            results = []
            for idx, score in enumerate(scores):
                analysis = None
                if return_analysis:
                    analysis = self.analyze_matches(jd_text, processed_resumes[idx])
                results.append((idx, score, analysis))
                
            return results
            
        except Exception as e:
            logger.error(f"Error calculating similarity scores: {str(e)}")
            return []