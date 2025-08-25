import os
import re
import pandas as pd
from tqdm import tqdm
from typing import List, Union
from concurrent.futures import ThreadPoolExecutor
from modules import parser, similarity

class ResumeRanker:
    """High-performance resume ranking based on job description"""

    def __init__(self, min_score: float = 0.0, workers: int = 4):
        """
        Args:
            min_score: Minimum similarity score (0-1) to include in results
            workers: Number of threads for parallel processing
        """
        self.min_score = min_score * 100  # Convert to percentage
        self.workers = workers
        self.matcher = similarity.ResumeMatcher(method="tfidf")
        self.email_pattern = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
        self.phone_pattern = re.compile(r"(\+91[-\s]?)?[0-9]{10}")
        self.jd_text = None

    def _extract_email(self, text: str) -> str:
        match = self.email_pattern.search(text)
        return match.group(0) if match else "N/A"

    def _extract_phone(self, text: str) -> str:
        match = self.phone_pattern.search(text)
        return match.group(0).strip() if match else "N/A"

    def _extract_name(self, text: str, filename: str) -> str:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:3]:
            if (1 <= len(line.split()) <= 3 and 
                not any(x in line.lower() for x in ["@", "linkedin", "github", "http"])):
                return line
        return os.path.splitext(os.path.basename(filename))[0]

    def _extract_metadata(self, text: str, filename: str) -> dict:
        return {
            'name': self._extract_name(text, filename),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'text': text
        }

    def _process_single(self, filepath: Union[str, os.PathLike]) -> Union[dict, None]:
        filename = os.path.basename(filepath)
        try:
            ext = os.path.splitext(filename)[-1].lower()

            if ext == ".pdf":
                with open(filepath, 'rb') as f:
                    text = parser.extract_text_from_pdf(f)
            elif ext == ".docx":
                with open(filepath, 'rb') as f:
                    text = parser.extract_text_from_docx(f)
            else:
                print(f"Unsupported file format: {filename}")
                return None

            meta = self._extract_metadata(text, filename)
            score = self.matcher.get_similarity_score(
                self.jd_text, [text], mode="raw"
            )[0][1] * 100

            return {
                "Name": meta['name'],
                "Score (%)": round(score, 2),
                "Email": meta['email'],
                "Phone": meta['phone'],
                "Filename": filename
            }

        except Exception as e:
            print(f"Skipped {filename} due to error: {str(e)}")
            return None

    def process_batch(self, resume_paths: List[str], jd_text: str) -> pd.DataFrame:
        if not jd_text:
            raise ValueError("Job description text must be provided.")

        self.jd_text = jd_text

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            results = list(tqdm(
                executor.map(self._process_single, resume_paths),
                total=len(resume_paths),
                desc="Processing resumes"
            ))

        df = pd.DataFrame([r for r in results if r is not None])

        if not df.empty:
            df.sort_values("Score (%)", ascending=False, inplace=True)
            df.reset_index(drop=True, inplace=True)
            df.index += 1
            df.index.name = "Rank"

        return df if not df.empty else pd.DataFrame(
            columns=["Rank", "Name", "Score (%)", "Email", "Phone", "Filename"]
        )
