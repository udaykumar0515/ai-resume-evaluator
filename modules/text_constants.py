import nltk
from nltk.corpus import stopwords

# Load English stopwords, downloading quietly if missing
try:
    ENGLISH_STOPWORDS = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords', quiet=True)
    ENGLISH_STOPWORDS = set(stopwords.words('english'))

# Additional domain-specific stopwords used across modules
CUSTOM_STOPWORDS = {
    "and", "or", "the", "with", "you", "will", "our", "your", "their", "this",
    "that", "have", "from", "which", "also", "they", "would", "about", "there",
    "work", "like", "into", "using", "need", "looking", "good", "make", "want",
    "able", "help", "team", "strong", "experience", "role", "knowledge", "understanding",
    "familiarity", "etc", "including", "within", "various", "ability", "focus",
    "solutions", "leverage", "enable", "stakeholders", "align", "deliverables",
    "paradigm", "ecosystem", "holistic", "value-added", "best", "practices",
    "basic", "basics", "development", "grow", "frameworks"
}

STOPWORDS = ENGLISH_STOPWORDS | CUSTOM_STOPWORDS

# === Shared skill dictionaries and patterns ===

# Parser skill dictionaries
SKILL_KEYWORDS = {
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "C++": ["c\\+\\+"],
    "C": ["c\\b"],
    "SQL": ["sql"],
    "HTML": ["html"],
    "CSS": ["css"],
    "React": ["react"],
    "Node.js": ["node", "node.js", "nodejs"],
    "Pygame": ["pygame"],
    "Streamlit": ["streamlit"],
    "Git": ["git"],
    "Machine Learning": ["machine learning", "ml"],
    "Data Structures": ["data structures"],
    "Web Development": ["web development"],
    "DeepFace": ["deepface"]
}

SKILL_CATEGORIES = {
    "Programming Languages": ["python", "java", "javascript", "c\\+\\+", "c"],
    "Web Technologies": ["html", "css", "react", "node"],
    "Databases": ["sql"],
    "Frameworks": ["pygame", "streamlit"],
    "Data Science": ["machine learning", "ml", "data structures"],
    "Tools": ["git"],
    "Concepts": ["web development"],
    "Computer Vision": ["deepface"]
}

INSTITUTION_KEYWORDS = [
    "college", "university", "institute", "school", "academy",
    "foundation", "research center", "company", "corporation", "services"
]

# Working suggestions constants
SKILL_SYNONYMS = {
    "python": ["python", "python3", "py", "pandas", "numpy", "scipy", "flask", "django", "fastapi"],
    "javascript": ["js", "javascript", "es6", "typescript", "ts", "react", "vue", "angular", "node.js", "nodejs"],
    "java": ["java", "spring", "spring boot", "hibernate", "j2ee"],
    "machine learning": ["ml", "ai", "deep learning", "tensorflow", "pytorch", "scikit-learn", "keras"],
    "web development": ["html", "css", "react", "vue", "angular", "frontend", "backend", "fullstack"],
    "databases": ["sql", "mysql", "postgresql", "mongodb", "nosql", "redis", "sqlite"],
    "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "devops", "jenkins"],
    "mobile": ["android", "ios", "react native", "flutter", "kotlin", "swift"],
    "data science": ["pandas", "numpy", "matplotlib", "seaborn", "jupyter", "data analysis"],
    "version control": ["git", "github", "gitlab", "bitbucket", "svn"]
}

IMPACT_VERBS = {
    "weak": ["did", "made", "helped", "worked on", "was involved in", "participated in", "assisted", "contributed"],
    "strong": [
        "developed", "implemented", "optimized", "led", "built", "achieved", "designed",
        "reduced", "increased", "automated", "streamlined", "deployed", "created", "managed"
    ]
}

QUANTIFIABLE_METRICS = [
    r"\d+%", r"\$\d+[\
w,]*", r"\d+k\b", r"\d+,\d+", r"\d+x\b",
    r"\d+\s*(users|customers|clients|people)", r"\d+\s*(hours|days|months|weeks)",
    r"\d+\s*(projects|applications|systems|features)", r"\d+\s*(million|billion|thousand)"
]


