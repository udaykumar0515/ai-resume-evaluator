import os
import re
import pandas as pd
from tqdm import tqdm
from typing import List, Union, BinaryIO
from concurrent.futures import ThreadPoolExecutor
from .parser import extract_text_from_pdf, extract_text_from_docx, extract_email, extract_phone
from .similarity import ResumeMatcher

class ResumeRanker:
    """High-performance resume processing with parallel execution"""
    
    def __init__(self, min_score: float = 0.3, workers: int = 4):
        """
        Args:
            min_score: Minimum similarity score (0-1) to include in results
            workers: Number of parallel workers for processing
        """
        self.min_score = min_score * 100  # Convert to percentage
        self.workers = workers
        self.matcher = ResumeMatcher(method="embedding")

    def _extract_metadata(self, text: str, filename: str) -> dict:
        """Fast metadata extraction from raw text"""
        return {
            'name': self._extract_name(text, filename),
            'email': extract_email(text) or "N/A",
            'phone': extract_phone(text) or "N/A",
            'text': text  # Keep raw text for batch processing
        }

    def _extract_name(self, text: str, filename: str) -> str:
        """Smart name extraction from first valid line"""
        first_lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in first_lines[:3]:  # Check first 3 non-empty lines
            if (1 <= len(line.split()) <= 3 and 
                not any(x in line.lower() for x in ["@", "http", "linkedin", "github"])):
                return line
        return os.path.splitext(filename)[0]

    def _process_single(self, file: BinaryIO) -> Union[dict, None]:
        """Process a single resume file"""
        try:
            filename = file.name
            ext = os.path.splitext(filename)[-1].lower()
            
            if ext == ".pdf":
                text = extract_text_from_pdf(file)
            elif ext == ".docx":
                text = extract_text_from_docx(file)
            else:
                return None
                
            meta = self._extract_metadata(text, filename)
            score = self.matcher.get_similarity_score(meta['text'], [text], mode="raw")[0][1] * 100
            
            if score >= self.min_score:
                return {
                    'Name': meta['name'],
                    'Score (%)': round(score, 2),
                    'Email': meta['email'],
                    'Phone': meta['phone'],
                    'Filename': filename
                }
            return None
            
        except Exception as e:
            print(f"Skipped {filename} due to error: {str(e)}")
            return None

    def process_batch(self, resume_files: List[BinaryIO]) -> pd.DataFrame:
        """
        Process multiple resumes in parallel
        
        Args:
            resume_files: List of file objects with .name attributes
            
        Returns:
            DataFrame sorted by score with Rank index
        """
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            results = list(tqdm(
                executor.map(self._process_single, resume_files),
                total=len(resume_files),
                desc="Processing resumes"
            ))
        
        # Create and format results dataframe
        df = pd.DataFrame([r for r in results if r is not None])
        
        if not df.empty:
            df.sort_values("Score (%)", ascending=False, inplace=True)
            df.reset_index(drop=True, inplace=True)
            df.index += 1
            df.index.name = "Rank"
        
        return df if not df.empty else pd.DataFrame(
            columns=["Rank", "Name", "Score (%)", "Email", "Phone", "Filename"]
        )

