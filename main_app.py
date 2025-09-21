# AI Resume Evaluator - Smaller Version
import streamlit as st
import os
import tempfile
import json
import random
from datetime import datetime
from modules import parser

# Configure Streamlit
st.set_page_config(
    page_title="AI Resume Evaluator",
    page_icon="🤖", 
    layout="wide"
)

# Simple CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.score-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 3rem;
    border-radius: 15px;
    text-align: center;
    margin: 2rem 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.score-number {
    font-size: 4rem;
    font-weight: bold;
    margin: 1rem 0;
}

.score-text {
    font-size: 1.5rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Resume Evaluator</h1>
    <p>Simple Resume-Job Match Scoring System</p>
</div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["📊 Resume Scoring", "💬 Feedback"])

# Tab 1: Resume Scoring
with tab1:
    st.markdown("### Upload Resume and Select Job Description")

    col1, col2 = st.columns(2)

    with col1:
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type=['pdf', 'docx', 'txt'],
            help="Upload your resume in PDF, DOCX, or TXT format"
        )

    with col2:
        # Job Description dropdown
        try:
            with open("data/predefined_jds.json", "r") as f:
                predefined_jds = json.load(f)
            
            jd_options = ["Select a job description..."] + list(predefined_jds.keys())
            selected_jd = st.selectbox("Choose a job description:", jd_options)
            
        except Exception as e:
            st.error(f"Error loading job descriptions: {e}")
            selected_jd = "Select a job description..."

    # Show score when both resume and JD are selected
    if uploaded_file is not None and selected_jd != "Select a job description...":
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Parse the resume
            with st.spinner("Analyzing resume and calculating match score..."):
                resume_data = parser.parse_resume(tmp_file_path)
                
                # Generate a mock score (you can replace this with real scoring logic)
                base_score = random.randint(65, 95)
                
                # Adjust score based on resume content
                if resume_data and resume_data.get('skills'):
                    skills_count = len(resume_data['skills'])
                    if skills_count > 5:
                        base_score += 5
                    elif skills_count > 10:
                        base_score += 10
                
                # Ensure score is between 0-100
                final_score = min(100, max(0, base_score))
                
                # Determine score category
                if final_score >= 90:
                    category = "Excellent Match"
                    color = "#28a745"
                elif final_score >= 80:
                    category = "Good Match"
                    color = "#17a2b8"
                elif final_score >= 70:
                    category = "Fair Match"
                    color = "#ffc107"
                else:
                    category = "Poor Match"
                    color = "#dc3545"
            
            # Display the score
            st.markdown(f"""
            <div class="score-card">
                <h2>Match Score</h2>
                <div class="score-number" style="color: {color};">{final_score}%</div>
                <div class="score-text">{category}</div>
                <p>Resume: {uploaded_file.name}</p>
                <p>Job: {selected_jd}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show some basic info
            if resume_data:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Skills Found", len(resume_data.get('skills', [])))
                with col2:
                    st.metric("Sections Detected", len(resume_data.get('sections', {})))
                with col3:
                    st.metric("File Size", f"{len(uploaded_file.getvalue())} bytes")
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")

    else:
        # Show instructions when files are not selected
        if uploaded_file is None and selected_jd == "Select a job description...":
            st.info("👆 Please upload a resume file and select a job description to see the match score")
        elif uploaded_file is None:
            st.info("👆 Please upload a resume file to see the match score")
        elif selected_jd == "Select a job description...":
            st.info("👆 Please select a job description to see the match score")

# Tab 2: Feedback
with tab2:
    st.markdown("### Provide Feedback")
    
    # Simple feedback form
    feedback_text = st.text_area(
        "Enter your feedback:",
        placeholder="Share your thoughts about the resume evaluation system...",
        height=150
    )
    
    # Rating
    rating = st.selectbox(
        "Rate the system:",
        ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]
    )
    
    # Submit button
    if st.button("Submit Feedback", type="primary"):
        if feedback_text.strip():
            # Create feedback data
            feedback_data = {
                "timestamp": datetime.now().isoformat(),
                "feedback": feedback_text,
                "rating": rating,
                "user_id": "anonymous"
            }
            
            # Save to JSON file
            try:
                if os.path.exists("feedback.json"):
                    with open("feedback.json", "r") as f:
                        all_feedback = json.load(f)
                else:
                    all_feedback = []
                
                all_feedback.append(feedback_data)
                
                with open("feedback.json", "w") as f:
                    json.dump(all_feedback, f, indent=2)
                
                st.success("✅ Feedback submitted successfully!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error saving feedback: {str(e)}")
        else:
            st.warning("⚠️ Please enter some feedback before submitting.")
    
    # Display recent feedback
    if os.path.exists("feedback.json"):
        try:
            with open("feedback.json", "r") as f:
                all_feedback = json.load(f)
            
            if all_feedback:
                st.markdown("### Recent Feedback")
                for i, feedback in enumerate(all_feedback[-3:]):  # Show last 3 feedback entries
                    with st.expander(f"Feedback #{len(all_feedback) - i} - {feedback['rating']}"):
                        st.write(f"**Time:** {feedback['timestamp']}")
                        st.write(f"**Feedback:** {feedback['feedback']}")
        except Exception as e:
            st.error(f"Error loading feedback: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>AI Resume Evaluator - Smaller Version | Educational Purpose</p>
</div>
""", unsafe_allow_html=True)
