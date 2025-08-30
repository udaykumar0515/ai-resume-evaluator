
# AI Resume Evaluator & Ranker

An intelligent platform designed for both **students** and **recruiters** to streamline resume evaluation and ranking against job descriptions (JDs).  
This project leverages **AI-powered semantic similarity models** to assess resumes with precision, highlight improvement areas, and rank applicants effectively.

---

## 🚀 Features

### 🔹 For Students (Resume Evaluation)
- Upload your resume (PDF format).
- Select an existing job description from our curated list of 20+ JDs **or** manually enter a custom JD.
- Get:
  - **Overall Match Score** between your resume and the JD.
  - **Priority Insights**: Critical, High, Medium, and Low importance areas to improve.
  - Actionable feedback on missing keywords, skills, or experiences.

### 🔹 For Recruiters (Resume Ranking)
- Upload multiple resumes at once.
- Select or enter a job description.
- Get:
  - **Top 3 Best-Matching Resumes**.
  - A **ranked table of all candidates** with:
    - Candidate Name  
    - Email ID  
    - Phone Number  
    - Match Score  
  - Helps recruiters shortlist candidates quickly and objectively.

---

## 🧠 How AI Works Here

This project integrates **open-source NLP models** (such as `sentence-transformers` and `scikit-learn`) to perform semantic similarity scoring:

1. **Resume & JD Parsing**: Extracts text from resumes and job descriptions.
2. **Vectorization with Pre-trained Models**: Uses embeddings from models like `all-MiniLM-L6-v2` to represent text meaningfully.
3. **Cosine Similarity Matching**: Compares embeddings of resume content with the JD to compute similarity scores.
4. **Rule-Based Enhancement**: Applies keyword and weight-based scoring for transparency and fine-tuned results.
5. **Feedback Generation**: Analyzes gaps and categorizes them into **Critical / High / Medium / Low** priority suggestions.

This ensures **both accuracy and explainability** — recruiters see not just the score but also *why* it was given.

---

## ⚙️ Tech Stack

- **Frontend**: Streamlit (interactive, user-friendly UI)  
- **Backend**: Python  
- **AI/NLP**:  
  - `sentence-transformers` (for embeddings)  
  - `scikit-learn` (for similarity calculations)  
- **Data Processing**: Pandas, PyPDF2  

---

## 📊 Accuracy & Testing

- Evaluated on a set of sample resumes and job descriptions.  
- Verified consistency of scores through manual cross-checking.  
- Feedback categories tested against multiple resume formats to ensure robustness.  

---

## 📂 Project Structure

```

├── app.py                 # Main Streamlit app
├── similarity.py          # AI-based scoring & feedback logic
├── ranking.py             # Resume ranking for recruiters
├── sample\_resumes/        # Example resumes for testing
├── job\_descriptions/      # Predefined JD library
├── requirements.txt       # Dependencies
└── README.md              # Documentation

````

---

## 🔧 Installation & Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/resume-ranker.git
   cd resume-ranker
````

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   streamlit run app.py
   ```

4. Access the app at `http://localhost:8501`.

---

## 📌 Future Enhancements

* Improved feedback with LLM-powered phrasing (explain suggestions more naturally).
* Support for more resume formats (DOCX, TXT).
* Integration with job portals for automatic JD import.
* Analytics dashboard for recruiters.
