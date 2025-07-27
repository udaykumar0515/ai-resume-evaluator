import streamlit as st
from modules import parser, jd_handler, similarity, suggestions
from modules.resume_ranker import ResumeRanker
import tempfile
import os
import pandas as pd
from typing import List, Dict

# Configure Streamlit
st.set_page_config(
    page_title="AI Resume Evaluator",
    page_icon="📄",
    layout="wide"
)

# Cache expensive resources
@st.cache_resource
def load_components():
    return {
        'matcher': similarity.ResumeMatcher(),
        'ranker': ResumeRanker(),
        'jds': jd_handler.load_predefined_jds("data/predefined_jds.json")
    }

def init_session_state():
    if 'processed_resumes' not in st.session_state:
        st.session_state.processed_resumes = {}

def display_evaluation_results(resume_data: Dict, jd_text: str, score: float):
    """Enhanced results display with new sections"""
    st.success(f"**Match Score:** {score*100:.1f}%")
    suggestion_results = suggestions.suggest_resume_improvements(resume_data, jd_text)
    
    # 1. Show Metrics First
    if "metrics" in suggestion_results:
        with st.expander("📊 Resume Metrics", expanded=True):
            for metric in suggestion_results["metrics"]:
                st.write(f"• {metric}")
    
    # 2. Show Strengths
    if "strengths" in suggestion_results:
        st.subheader("✅ Your Strengths")

        skill_matches = []
        fundamentals = ""

        for strength in suggestion_results["strengths"]:
            if strength.startswith("✅ Strong Keyword Matches:"):
                continue
            elif "Strong Fundamental Skills" in strength:
                fundamentals = strength.split(":")[1].strip()
            elif ": " in strength:
                category, terms = strength.split(": ", 1)
                if category.strip().lower() != "other":
                    skill_matches.append(terms.strip())

        # Show skill matches in one line
        if skill_matches:
            st.markdown("**🛠️ Skill Matches**")
            st.write(", ".join(skill_matches))

        # Show fundamentals
        if fundamentals:
            st.markdown("**📘 Fundamental Skills**")
            st.write(fundamentals)
        # Show 'Other' (optional, muted)
        for strength in suggestion_results["strengths"]:
            if ": " in strength:
                category, terms = strength.split(": ", 1)
                if category.strip().lower() == "other":
                    st.markdown("**Other Keywords** _(less relevant)_")
                    st.caption(", ".join(terms.strip().split(", ")[:5]))


    # 3. Show Improvement Areas
    st.subheader("🔍 Improvement Suggestions")
    for priority in ["critical", "high", "medium", "low"]:
        if priority in suggestion_results:
            with st.expander(f"{priority.title()} Priority ({len(suggestion_results[priority])})"):
                for tip in suggestion_results[priority]:
                    st.write(f"• {tip}")
    
    # 4. Additional Tips
    if "tips" in suggestion_results:
        st.subheader("💡 General Tips")
        for tip in suggestion_results["tips"]:
            st.info(tip)

def display_ranking_results(df: pd.DataFrame):
    """Display results for multiple resume ranking"""
    st.success(f"Ranked {len(df)} resumes")
    
    # Show top 3 in an attractive layout
    if len(df) >= 3:
        st.subheader("🏆 Top 3 Candidates")
        cols = st.columns(3)
        for i in range(3):
            with cols[i]:
                st.metric(
                    label=f"Rank {i+1}: {df.iloc[i]['Name']}",
                    value=f"{df.iloc[i]['Score (%)']}%",
                    help=f"Contact: {df.iloc[i]['Email']}"
                )
    
    # Full results table
    st.dataframe(
        df.style.background_gradient(subset=["Score (%)"], cmap="YlGn"),
        use_container_width=True,
        height=min(600, 35 * (len(df) + 1))
    )
    
    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "💾 Download Rankings",
        csv,
        "resume_rankings.csv",
        "text/csv",
        key="download_rankings"
    )

def process_resume_upload(uploaded_file, mode: str) -> Dict:
    """Parse and cache uploaded resume"""
    cache_key = f"{mode}_{uploaded_file.name}"
    
    if cache_key not in st.session_state.processed_resumes:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            st.session_state.processed_resumes[cache_key] = parser.parse_resume(uploaded_file)
    
    return st.session_state.processed_resumes[cache_key]

def get_jd_input(jds: Dict[str, str], tab_prefix: str) -> str:
    """Get job description from user with tab-specific keys"""
    col1, col2 = st.columns([1, 2])

    with col1:
        jd_choice = st.selectbox(
            "Select Job Role",
            options=["Custom Input"] + list(jds.keys()),
            key=f"{tab_prefix}_jd_choice"
        )

    with col2:
        if jd_choice == "Custom Input":
            return st.text_area(
                "Enter Job Description",
                height=200,
                placeholder="Paste the job description here...",
                key=f"{tab_prefix}_custom_jd"
            )
        else:
            st.text_area(
                "Job Description (Predefined)",
                value=jds.get(jd_choice, ""),
                height=200,
                key=f"{tab_prefix}_readonly_jd",
                disabled=True
            )
            return jds.get(jd_choice, "")

def evaluation_tab(components: Dict):
    """Single resume evaluation interface"""
    st.header("📝 Resume Evaluation")
    
    uploaded_file = st.file_uploader(
        "Upload Your Resume (PDF/DOCX)", 
        type=["pdf", "docx"],
        key="eval_upload"
    )
    
    jd_text = get_jd_input(components['jds'], "eval")
    
    if st.button("Evaluate", type="primary", key="eval_button") and uploaded_file and jd_text:
        resume_data = process_resume_upload(uploaded_file, "eval")
        results = components['matcher'].get_similarity_score(
            jd_text,
            [resume_data],
            mode="structured"
        )
        
        if results:
            score = results[0][1]
            display_evaluation_results(resume_data, jd_text, score)

def ranking_tab(components: Dict):
    """Multiple resume ranking interface"""
    st.header("🏆 Resume Ranking")
    
    uploaded_files = st.file_uploader(
        "Upload Resumes (PDF/DOCX)", 
        accept_multiple_files=True,
        type=["pdf", "docx"],
        key="rank_uploads"
    )
    
    jd_text = get_jd_input(components['jds'], "rank")
    
    if st.button("Rank Resumes", type="primary", key="rank_button") and uploaded_files and jd_text:
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_paths = []
            for file in uploaded_files:
                path = os.path.join(tmp_dir, file.name)
                with open(path, "wb") as f:
                    f.write(file.getbuffer())
                file_paths.append(path)
            
            df = components['ranker'].process_batch(file_paths, jd_text)
            
        if not df.empty:
            display_ranking_results(df)
        else:
            st.warning("No qualifying resumes found")

def main():
    components = load_components()
    init_session_state()
    
    st.title("AI Resume Evaluator")
    st.write("Optimized for student feedback and recruiter bulk processing")
    
    tab1, tab2 = st.tabs(["Resume Evaluation", "Resume Ranking"])
    
    with tab1:
        evaluation_tab(components)
    
    with tab2:
        ranking_tab(components)

if __name__ == "__main__":
    main()