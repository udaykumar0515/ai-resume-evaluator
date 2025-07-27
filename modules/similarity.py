import re
import unicodedata
import logging
import numpy as np
from typing import List, Tuple, Dict, Union, Optional
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import torch
from modules.suggestions import STOPWORDS 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeMatcher:
    """
    Advanced resume-job description matching system with semantic understanding.
    Combines embedding-based and keyword-based approaches for optimal results.
    """

    def __init__(
        self,
        method: str = "hybrid",  # Updated default to hybrid
        section_weights: Optional[Dict[str, float]] = None,
        min_skill_match: float = 0.65,
        use_gpu: bool = False,
        embedding_model: str = 'balanced',  # fast/balanced/accurate
        tfidf_params: Optional[Dict] = None
    ):
        """
        Initialize matcher with enhanced configuration options.
        """
        self.method = method
        self.section_weights = section_weights or {
            'skills': 0.6,
            'experience': 0.25,
            'projects': 0.1,
            'education': 0.05
        }
        self.min_skill_match = min_skill_match
        self.device = 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu'
        
        # Enhanced embedding model selection
        self.embedding_models = {
            'fast': 'all-MiniLM-L6-v2',
            'balanced': 'all-mpnet-base-v2',
            'accurate': 'paraphrase-multilingual-mpnet-base-v2'
        }
        self.embedding_model_name = self.embedding_models.get(
            embedding_model,
            'all-mpnet-base-v2'
        )
        
        # Initialize embedding model
        if self.method in ('hybrid', 'embedding'):
            try:
                self.embedding_model = SentenceTransformer(
                    self.embedding_model_name,
                    device=self.device
                )
                logger.info(f"Loaded {self.embedding_model_name} on {self.device}")
            except Exception as e:
                logger.error(f"Embedding model failed: {str(e)}")
                self.method = 'tfidf' if method != 'hybrid' else 'tfidf-only'
        
        # Enhanced TF-IDF configuration
        if self.method in ('hybrid', 'tfidf'):
            self.tfidf_params = tfidf_params or {
                'ngram_range': (1, 3),
                'stop_words': 'english',
                'min_df': 2,
                'max_features': 5000
            }
            self.vectorizer = TfidfVectorizer(**self.tfidf_params)
            self.jd_vector = None

    @staticmethod
    def clean_text(text: str) -> str:
        """Advanced text normalization preserving tech terminology"""
        if not isinstance(text, str):
            return ""
        
        # Preserve key tech symbols (+, #, .) while cleaning
        text = unicodedata.normalize("NFKC", text)
        text = re.sub(r"[^\w\s+.#@-]", "", text)
        text = re.sub(r"\s+", " ", text).lower().strip()
        
        # Standardize common tech terms
        replacements = {
            r"\bc\+\+\b": "cpp",
            r"\bc#\b": "csharp",
            r"\b\.net\b": "dotnet",
            r"\bjs\b": "javascript",
            r"\baws\b": "amazon web services",
            r"\bgcp\b": "google cloud",
            r"\bai\b": "artificial intelligence",
            r"\bml\b": "machine learning"
        }
        for pattern, repl in replacements.items():
            text = re.sub(pattern, repl, text)
        
        return text

    def combine_structured_resume(self, resume_data: Dict) -> str:
        """Enhanced resume combining with semantic weighting"""
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
            weight = self.section_weights.get(section, 1.0)
            if weight > 0:
                section_text = " ".join(text_parts)
                weighted_text.append((section_text + " ") * int(weight * 15))
        
        return self.clean_text(" ".join(weighted_text))

    def compute_tfidf_similarity(self, jd_text: str, resume_texts: List[str]) -> List[float]:
        """Enhanced TF-IDF with dynamic fitting"""
        try:
            if self.jd_vector is None:
                all_texts = [self.clean_text(jd_text)] + [self.clean_text(r) for r in resume_texts]
                tfidf_matrix = self.vectorizer.fit_transform(all_texts)
                self.jd_vector = tfidf_matrix[0:1]
                resume_vectors = tfidf_matrix[1:]
            else:
                resume_vectors = self.vectorizer.transform(
                    [self.clean_text(r) for r in resume_texts]
                )
            
            scores = cosine_similarity(self.jd_vector, resume_vectors).flatten()
            return [float(round(score, 4)) for score in scores]
        except Exception as e:
            logger.error(f"TF-IDF error: {str(e)}")
            return [0.0] * len(resume_texts)

    def compute_embedding_similarity(self, jd_text: str, resume_texts: List[str]) -> List[float]:
        """Optimized embedding computation with chunking"""
        try:
            documents = [self.clean_text(jd_text)] + [self.clean_text(r) for r in resume_texts]
            
            # Dynamic batch sizing
            avg_len = sum(len(d) for d in documents) / len(documents)
            batch_size = max(1, min(64, int(4000 / avg_len)))
            
            embeddings = []
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                batch_emb = self.embedding_model.encode(
                    batch,
                    device=self.device,
                    show_progress_bar=False,
                    convert_to_tensor=True
                )
                embeddings.append(batch_emb)
            
            embeddings = torch.cat(embeddings).cpu().numpy()
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            
            return cosine_similarity(embeddings[0:1], embeddings[1:]).flatten().tolist()
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            return [0.0] * len(resume_texts)

    def analyze_matches(self, jd_text: str, resume_text: str) -> Dict:
        """Enhanced match analysis with better term filtering and grouping"""
        jd_clean = self.clean_text(jd_text)
        resume_clean = self.clean_text(resume_text)
        
        # Custom stopwords for analysis
        analysis_stopwords = STOPWORDS | {
            'using', 'with', 'for', 'basic', 'basics', 'knowledge', 'experience'
        }
        
        # Extract meaningful terms (longer than 3 chars, not stopwords)
        jd_tokens = {
            word for word in re.findall(r'\b[\w+.#-]{3,}\b', jd_clean)
            if word not in analysis_stopwords
        }
        resume_tokens = {
            word for word in re.findall(r'\b[\w+.#-]{3,}\b', resume_clean)
            if word not in analysis_stopwords
        }
        
        # Enhanced skill ontology
        SKILL_ONTOLOGY = {
            "programming": {"python", "java", "c++", "c#", "javascript", "typescript"},
            "web": {"html", "css", "react", "angular", "vue", "django", "flask"},
            "data": {"sql", "mongodb", "pandas", "numpy", "tensorflow", "pytorch"},
            "devops": {"docker", "kubernetes", "aws", "azure", "ci/cd", "terraform"},
            "soft_skills": {"leadership", "communication", "teamwork", "problem-solving"}
        }
        
        # Find direct matches
        overlapping = jd_tokens & resume_tokens
        
        # Find ontology-expanded matches
        expanded_matches = set(overlapping)
        for term in overlapping:
            for category, terms in SKILL_ONTOLOGY.items():
                if term in terms:
                    expanded_matches.update(terms)
        
        # Calculate meaningful percentages
        jd_total_terms = max(1, len(jd_tokens))
        direct_match_pct = len(overlapping) / jd_total_terms
        expanded_match_pct = len(expanded_matches) / jd_total_terms
        
        # Group terms by category
        term_categories = defaultdict(list)
        for term in expanded_matches:
            found = False
            for category, terms in SKILL_ONTOLOGY.items():
                if term in terms:
                    term_categories[category].append(term)
                    found = True
            if not found:
                term_categories["other"].append(term)
        assert all(term not in STOPWORDS for term in overlapping), f"Junk term found: {overlapping}"

        return {
            "match_quality": {
                "direct_match": float(round(direct_match_pct, 4)),
                "expanded_match": float(round(expanded_match_pct, 4)),
                "jd_term_count": len(jd_tokens),
                "resume_term_count": len(resume_tokens)
            },
            "term_categories": dict(term_categories),
            "missing_terms": sorted(jd_tokens - expanded_matches)[:10],
            "raw_analysis": {
                "overlapping_terms": sorted(overlapping),
                "match_percentage": direct_match_pct
            }
        }

    def format_analysis(self, analysis: Dict) -> str:
        """Human-readable analysis formatting"""
        output = []
        
        # Match quality section
        match_qual = analysis["match_quality"]
        output.append("=== MATCH QUALITY ===")
        output.append(f"Direct Match: {match_qual['direct_match']:.1%}")
        output.append(f"Expanded Match: {match_qual['expanded_match']:.1%}")
        output.append(f"JD Terms: {match_qual['jd_term_count']} | Resume Terms: {match_qual['resume_term_count']}")
        
        # Term categories
        output.append("\n=== MATCHED SKILLS ===")
        for category, terms in analysis["term_categories"].items():
            if terms:  # Only show non-empty categories
                output.append(f"{category.upper()}: {', '.join(sorted(terms)[:5])}" + 
                             ("..." if len(terms) > 5 else ""))
        
        # Missing terms
        if analysis.get("missing_terms"):
            output.append("\n=== SUGGESTED IMPROVEMENTS ===")
            output.append("Consider adding: " + ", ".join(analysis["missing_terms"][:5]))
        
        return "\n".join(output)

    def get_similarity_score(
        self,
        jd_text: str,
        resumes: List[Union[str, Dict]],
        mode: str = "structured",
        return_analysis: bool = True,
        formatted_output: bool = True
    ) -> List[Tuple[int, float, Optional[Union[Dict, str]]]]:
        """Hybrid scoring with comprehensive analysis"""
        if not jd_text or not resumes:
            return []
        
        try:
            # Pre-process resumes
            processed_resumes = [
                self.combine_structured_resume(r) if isinstance(r, dict) 
                else self.clean_text(r) 
                for r in resumes
            ]
            
            # Calculate scores
            tfidf_scores = []
            embedding_scores = []
            
            if self.method in ('hybrid', 'tfidf'):
                tfidf_scores = self.compute_tfidf_similarity(jd_text, processed_resumes)
            
            if self.method in ('hybrid', 'embedding'):
                embedding_scores = self.compute_embedding_similarity(jd_text, processed_resumes)
            
            # Combine scores for hybrid mode
            if self.method == 'hybrid':
                scores = [
                    0.6 * emb + 0.4 * tf 
                    for emb, tf in zip(embedding_scores, tfidf_scores)
                ]
            else:
                scores = embedding_scores if self.method == 'embedding' else tfidf_scores
            
            # Generate analysis
            results = []
            for idx, score in enumerate(scores):
                analysis = None
                if return_analysis:
                    try:
                        analysis = self.analyze_matches(jd_text, processed_resumes[idx])
                        analysis["score_components"] = {
                            "final": float(round(score, 4)),
                            "embedding": float(round(embedding_scores[idx], 4)) if embedding_scores else None,
                            "tfidf": float(round(tfidf_scores[idx], 4)) if tfidf_scores else None
                        }
                        if formatted_output:
                            analysis["formatted"] = self.format_analysis(analysis)
                    except Exception as e:
                        logger.warning(f"Analysis failed for resume {idx}: {str(e)}")
                        analysis = {"error": str(e)}
                
                results.append((idx, float(round(score, 4)), 
                               analysis["formatted"] if formatted_output else analysis))
            
            return results
        
        except Exception as e:
            logger.error(f"Scoring failed: {str(e)}")
            return []