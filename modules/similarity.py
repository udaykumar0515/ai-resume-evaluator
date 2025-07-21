import re
from typing import List, Tuple, Dict, Union, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import unicodedata
from collections import defaultdict
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeMatcher:
    """
    Resume-job description matching system using semantic embeddings by default
    with fallback to TF-IDF if embeddings are not available.
    """
    
    def __init__(
        self,
        method: str = "embedding",  # Changed default to embedding
        section_weights: Optional[Dict[str, float]] = None,
        min_skill_match: float = 0.7,
        use_gpu: bool = False,
        embedding_model_name: str = 'all-MiniLM-L6-v2'
    ):
        """
        Initialize the matcher with configuration options.
        
        Args:
            method: 'embedding' (default) or 'tfidf'
            section_weights: Dictionary of weights for structured resume sections
            min_skill_match: Minimum similarity threshold to consider skills matched
            use_gpu: Whether to use GPU for embedding model if available
            embedding_model_name: Name of the SentenceTransformer model to use
        """
        self.method = method
        self.section_weights = section_weights or {
            'skills': 0.5,  # Increased weight for skills
            'experience': 0.3,
            'education': 0.1,
            'projects': 0.1
        }
        self.min_skill_match = min_skill_match
        self.embedding_model = None
        self.embedding_model_name = embedding_model_name
        
        # Initialize the preferred method
        if self.method == "embedding":
            try:
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
                if use_gpu:
                    self.embedding_model = self.embedding_model.to('cuda')
                logger.info(f"Initialized embedding model: {self.embedding_model_name}")
            except ImportError:
                logger.warning("SentenceTransformers not installed. Falling back to TF-IDF.")
                self.method = "tfidf"
            except Exception as e:
                logger.warning(f"Failed to initialize embedding model: {str(e)}. Falling back to TF-IDF.")
                self.method = "tfidf"
        
        if self.method == "tfidf":
            logger.info("Using TF-IDF vectorizer for similarity calculation")
            self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
            self.jd_vector = None

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
                    # Repeat text based on weight (more precise approach)
                    weighted_text.append((section_text + " ") * int(weight * 10))
            return self.clean_text(" ".join(weighted_text))
        else:
            return self.clean_text(" ".join(" ".join(parts) for parts in combined_parts.values()))


    def compute_tfidf_similarity(self, jd_text: str, resume_texts: List[str]) -> List[float]:
        # Fit only once per JD
        if self.jd_vector is None:
            all_texts = [self.clean_text(jd_text)] + [self.clean_text(r) for r in resume_texts]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
            self.jd_vector = tfidf_matrix[0:1]
            resume_vectors = tfidf_matrix[1:]
        else:
            resume_vectors = self.tfidf_vectorizer.transform(
                [self.clean_text(r) for r in resume_texts]
            )
        
        scores = cosine_similarity(self.jd_vector, resume_vectors).flatten()
        return [float(round(score, 4)) for score in scores]
    def compute_embedding_similarity(self, jd_text: str, resume_texts: List[str]) -> List[float]:
        """
        Compute cosine similarity scores between JD and multiple resumes using sentence embeddings.
        More efficient batch processing.
        """
        if not self.embedding_model:
            raise ValueError("Embedding model not initialized")
            
        # Process all texts at once for better efficiency
        documents = [self.clean_text(jd_text)] + [self.clean_text(resume) for resume in resume_texts]
        
        # Batch processing for better performance
        batch_size = 32 if len(documents) > 32 else len(documents)
        embeddings = self.embedding_model.encode(
            documents,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        # Normalize embeddings for more accurate cosine similarity
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        scores = cosine_similarity(embeddings[0:1], embeddings[1:]).flatten()
        return [float(round(score, 4)) for score in scores]

    def analyze_matches(self, jd_text: str, resume_text: str) -> Dict[str, Union[float, List[str]]]:
        """
        Enhanced match analysis with term importance and skill-specific matching.
        """
        jd_clean = self.clean_text(jd_text)
        resume_clean = self.clean_text(resume_text)
        
        # Tokenize
        jd_tokens = set(re.findall(r"\b[\w-]+\b", jd_clean))
        resume_tokens = set(re.findall(r"\b[\w-]+\b", resume_clean))
        
        # Find overlaps
        overlapping = jd_tokens & resume_tokens
        
        # Find bigram overlaps
        jd_words = re.findall(r"\b[\w-]+\b", jd_clean)
        resume_words = re.findall(r"\b[\w-]+\b", resume_clean)
        
        jd_bigrams = set(zip(jd_words, jd_words[1:]))
        resume_bigrams = set(zip(resume_words, resume_words[1:]))
        overlapping_bigrams = jd_bigrams & resume_bigrams
        
        # Calculate match percentages
        jd_total_terms = max(1, len(jd_tokens))
        match_percentage = len(overlapping) / jd_total_terms
        
        # Skill-specific matching (if skills section exists)
        skill_match = {}
        if hasattr(self, 'section_weights') and 'skills' in self.section_weights:
            # Simple skill matching - in real implementation you'd want a skill ontology
            skill_terms = {'python', 'java', 'machine learning', 'aws', 
                          'sql', 'tensorflow', 'pytorch', 'docker', 'kubernetes'}
            jd_skills = jd_tokens & skill_terms
            resume_skills = resume_tokens & skill_terms
            matched_skills = jd_skills & resume_skills
            
            if jd_skills:
                skill_match = {
                    'matched_skills': list(matched_skills),
                    'skill_coverage': len(matched_skills) / max(1, len(jd_skills))
                }
        
        return {
            "overlapping_terms": list(overlapping),
            "overlapping_bigrams": [" ".join(bigram) for bigram in overlapping_bigrams],
            "match_percentage": match_percentage,
            "skill_match": skill_match,
            "jd_term_count": jd_total_terms,
            "resume_term_count": len(resume_tokens)
        }

    def get_similarity_score(
        self,
        jd_text: str,
        resumes: List[Union[str, Dict]],
        mode: str = "raw",
        return_analysis: bool = False
    ) -> List[Tuple[int, float, Optional[Dict]]]:
        """
        Main entry point with improved error handling and performance.
        """
        if not jd_text or not resumes:
            return []
            
        try:
            # Pre-process resumes based on mode
            if mode == "structured":
                processed_resumes = [self.combine_structured_resume(r) for r in resumes]
            else:
                processed_resumes = [self.clean_text(r) if isinstance(r, str) else "" for r in resumes]

            # Calculate similarity scores
            if self.method == "embedding":
                scores = self.compute_embedding_similarity(jd_text, processed_resumes)
            else:
                scores = self.compute_tfidf_similarity(jd_text, processed_resumes)
                
            # Prepare results with optional analysis
            results = []
            for idx, score in enumerate(scores):
                analysis = None
                if return_analysis:
                    try:
                        analysis = self.analyze_matches(jd_text, processed_resumes[idx])
                    except Exception as e:
                        logger.warning(f"Failed to analyze matches for resume {idx}: {str(e)}")
                        analysis = {"error": str(e)}
                
                results.append((idx, score, analysis))
                
            return results
            
        except Exception as e:
            logger.error(f"Error calculating similarity scores: {str(e)}")
            return []