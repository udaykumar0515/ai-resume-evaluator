import os
import re
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
from docx import Document
import unicodedata


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text.
    """
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text(file_path: str) -> str:
    """
    Extract raw text from PDF, DOCX, or TXT.
    """
    try:
        if file_path.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file_path)
            return clean_text(" ".join([page.extract_text() or "" for page in reader.pages]))

        elif file_path.endswith(".docx"):
            doc = Document(file_path)
            return clean_text("\n".join([p.text for p in doc.paragraphs]))

        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                return clean_text(f.read())

        else:
            raise ValueError("Unsupported file type.")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""


def load_resumes(resume_dir: str) -> List[Tuple[str, str]]:
    """
    Load and extract text from all resumes in a folder.
    Returns: List of (filename, text)
    """
    resumes = []
    for filename in os.listdir(resume_dir):
        filepath = os.path.join(resume_dir, filename)
        if os.path.isfile(filepath) and filepath.lower().endswith((".pdf", ".docx", ".txt")):
            text = extract_text(filepath)
            if text:
                resumes.append((filename, text))
    return resumes


def match_resumes_to_jd(resumes: List[Tuple[str, str]], jd_text: str, top_k=5) -> List[Tuple[str, float]]:
    """
    Compute cosine similarity between job description and resumes.
    Returns top_k matching resumes with their scores.
    """
    documents = [jd_text] + [text for _, text in resumes]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)

    jd_vector = tfidf_matrix[0]
    resume_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(jd_vector, resume_vectors).flatten()

    scored_resumes = [(resumes[i][0], round(similarities[i], 4)) for i in range(len(resumes))]
    ranked = sorted(scored_resumes, key=lambda x: x[1], reverse=True)

    return ranked[:top_k]


# 🧪 === TEST SECTION ===
if __name__ == "__main__":
    resume_folder = r"D:\uday\Vscode\Projects\AI_resume_evaluator\data\resumes"  # folder with resumes

    # Sample JD string (instead of loading from a file)
    sample_jd = """
    Job Title: Junior Full Stack Developer

    We are looking for a passionate Full Stack Developer to join our tech team.

    Responsibilities:
    - Build and maintain web applications using React, Node.js, and MongoDB.
    - Collaborate with designers and backend developers.
    - Write clean and scalable code with unit tests.

    Requirements:
    - Proficient in JavaScript, HTML, CSS.
    - Familiarity with frontend frameworks like React or Angular.
    - Experience in backend development using Node.js or Python.
    - Understanding of REST APIs and databases (MongoDB/MySQL).
    - Strong problem-solving skills and eagerness to learn.

    Bonus:
    - Knowledge of Git, CI/CD, and Agile methodologies.
    """

    resumes = load_resumes(resume_folder)

    print(f"\n🔍 Matching {len(resumes)} resumes against the sample JD...\n")
    matches = match_resumes_to_jd(resumes, sample_jd, top_k=5)

    print("🏆 Top Resume Matches:")
    for rank, (filename, score) in enumerate(matches, start=1):
        print(f"{rank}. {filename} - Score: {score}")
