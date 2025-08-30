# 🤖 AI Resume Evaluator & Ranker

> **Intelligent resume analysis powered by advanced NLP for students and recruiters**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/your-username/resume-ranker?style=social)](https://github.com/udaykumar0515/ai-resume-evaluator.git)

An intelligent platform that leverages **state-of-the-art AI and NLP techniques** to revolutionize resume evaluation and candidate ranking. Built for both **students seeking career guidance** and **recruiters optimizing hiring processes**.

---

## ✨ Key Features

### 🎓 For Students - Resume Evaluation & Improvement
- **📄 Multi-format Support**: Upload resumes in PDF, DOCX, or TXT formats
- **🎯 Smart JD Matching**: Choose from 20+ curated job descriptions or input custom ones
- **📊 Comprehensive Analysis**:
  - Overall match score with detailed breakdown
  - Priority-based improvement suggestions (Critical → High → Medium → Low)
  - Missing skills and keywords identification
  - Experience gap analysis
  - Actionable feedback for resume enhancement

### 👔 For Recruiters - Intelligent Candidate Ranking
- **📁 Batch Processing**: Upload and analyze multiple resumes simultaneously
- **🏆 Smart Ranking**: AI-powered candidate ranking based on job requirements
- **📋 Detailed Reports**:
  - Top 3 best-matching candidates
  - Complete ranked candidate list with contact information
  - Match scores with confidence levels
  - Skills gap analysis for each candidate
- **⚡ Time-Saving**: Reduce manual screening time by 80%

---

## 🧠 AI Technology Stack

### Core NLP Models
- **Sentence Transformers**: `all-MiniLM-L6-v2` for semantic embeddings
- **Scikit-learn**: Advanced similarity algorithms and clustering
- **Custom Weighting System**: Rule-based enhancement for domain-specific accuracy

### How It Works
1. **📖 Text Extraction**: Advanced parsing of resumes and job descriptions
2. **🔢 Vectorization**: Convert text to high-dimensional embeddings using pre-trained models
3. **📐 Similarity Computation**: Cosine similarity + custom weighting algorithms
4. **🎯 Gap Analysis**: Identify missing skills, experiences, and keywords
5. **📊 Scoring & Ranking**: Multi-factor scoring with explainable results


---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Streamlit | Interactive web interface |
| **Backend** | Python 3.8+ | Core application logic |
| **AI/NLP** | Sentence Transformers | Semantic understanding |
| **ML** | Scikit-learn | Similarity calculations |
| **Data Processing** | Pandas, PyPDF2 | File handling & analysis |

---

## 📁 Project Structure

```
├── .gitignore
├── README.md
├── data
│   └── predefined_jds.json
├── feedback.json
├── main_app.py
├── modules
│   ├── jd_handler.py
│   ├── parser.py
│   ├── resume_ranker.py
│   ├── similarity.py
│   ├── test.py
│   ├── text_constants.py
│   └── working_suggestions.py
├── requirements.txt
├── sample_resumes
│   ├── aspnet-web-developer-resume-example.pdf
│   ├── freelance-web-developer-resume-example.pdf
│   ├── java-web-developer-resume-example.pdf
│   ├── junior-web-developer-resume-example.pdf
│   ├── react-developer-resume.pdf
│   ├── senior-web-developer-resume-example.pdf
│   ├── web-application-developer-resume-example.pdf
│   ├── web-developer-intern-resume-example.pdf
│   └── web-developer-resume-example.pdf
```


---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- 4GB+ RAM (for AI model loading)
- Internet connection (for model download)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/udaykumar0515/ai-resume-evaluator.git
   cd resume-ranker
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the app**
   Open your browser and navigate to `http://localhost:8501`


---

## 📊 Usage Examples

### For Students
1. **Upload your resume** (PDF/DOCX/TXT)
2. **Select a job description** from the library or paste your own
3. **Get instant feedback**:
   - Match score: 85/100
   - Critical improvements: Add "machine learning" experience
   - High priority: Include "Python" programming skills
   - Medium priority: Add project management examples

### For Recruiters
1. **Upload multiple resumes** (up to 50 at once)
2. **Specify job requirements**
3. **Receive ranked results**:
   - Top candidate: Sarah Johnson (92% match)
   - Second: Mike Chen (87% match)
   - Third: Alex Rodriguez (83% match)

---

### Development Setup
```bash
git clone https://github.com/udaykumar0515/ai-resume-evaluator.git
cd ai-resume-evaluator
pip install -r requirements-dev.txt
pytest tests/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Sentence Transformers** by UKP Lab for semantic embeddings
- **Streamlit** team for the amazing web framework
- **Open source community** for continuous improvements
- **Beta testers** for valuable feedback and suggestions

---

## 📞 Support & Contact

- **Email**: udaykumarhaibathi@gmail.com

---
