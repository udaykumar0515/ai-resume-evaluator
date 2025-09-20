# AI Resume Evaluator - Teacher Presentation Mockup
import streamlit as st
import pandas as pd
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, Any

# Import modules
try:
    from modules import parser
except Exception as e:
    st.error(f"❌ Error importing modules: {e}")
    st.stop()

# Configure Streamlit
st.set_page_config(
    page_title="AI Resume Evaluator",
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling to look professional
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.section-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    border-left: 4px solid #667eea;
    margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.feedback-card {
    background: #f8f9fa;
    padding: 2rem;
    border-radius: 10px;
    border: 1px solid #dee2e6;
    margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    margin: 0.5rem;
}

.skill-tag {
    background: #e3f2fd;
    color: #1976d2;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.9rem;
    margin: 0.2rem;
    display: inline-block;
}

.experience-item {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 3px solid #667eea;
}

.tab-content {
    padding: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Resume Evaluator</h1>
    <p>Intelligent Resume Analysis and Feedback System</p>
    <p style="font-size: 0.9rem; opacity: 0.9;">Powered by Advanced NLP and Machine Learning</p>
</div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["📄 Resume Analysis", "💬 Feedback & Suggestions"])

# Tab 1: Resume Analysis
with tab1:
    st.markdown("### Upload and Analyze Resume")
    
    # File upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type=['pdf', 'docx', 'txt'],
            help="Upload your resume in PDF, DOCX, or TXT format"
        )
    
    with col2:
        st.markdown("**Supported Formats:**")
        st.markdown("• PDF Documents")
        st.markdown("• Word Documents (.docx)")
        st.markdown("• Text Files (.txt)")
    
    if uploaded_file is not None:
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Parse the resume
            with st.spinner("🔍 Analyzing resume with AI..."):
                resume_data = parser.parse_resume(tmp_file_path)
            
            if resume_data:
                st.success("✅ Resume analyzed successfully!")
                
                # Display results in a professional layout
                st.markdown("### 📊 Analysis Results")
                
                # Metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown('<div class="metric-card"><h3>📄</h3><p>Resume Parsed</p></div>', unsafe_allow_html=True)
                
                with col2:
                    skills_count = len(resume_data.get('skills', []))
                    st.markdown(f'<div class="metric-card"><h3>{skills_count}</h3><p>Skills Found</p></div>', unsafe_allow_html=True)
                
                with col3:
                    exp_count = len(resume_data.get('experience', []))
                    st.markdown(f'<div class="metric-card"><h3>{exp_count}</h3><p>Experience Items</p></div>', unsafe_allow_html=True)
                
                with col4:
                    edu_count = len(resume_data.get('education', []))
                    st.markdown(f'<div class="metric-card"><h3>{edu_count}</h3><p>Education Items</p></div>', unsafe_allow_html=True)
                
                # Personal Information
                if resume_data.get('personal_info'):
                    st.markdown('<div class="section-card"><h4>👤 Personal Information</h4></div>', unsafe_allow_html=True)
                    personal_info = resume_data['personal_info']
                    col1, col2 = st.columns(2)
                    with col1:
                        if personal_info.get('name'):
                            st.write(f"**Name:** {personal_info['name']}")
                        if personal_info.get('email'):
                            st.write(f"**Email:** {personal_info['email']}")
                    with col2:
                        if personal_info.get('phone'):
                            st.write(f"**Phone:** {personal_info['phone']}")
                        if personal_info.get('location'):
                            st.write(f"**Location:** {personal_info['location']}")
                
                # Skills section
                if resume_data.get('skills'):
                    st.markdown('<div class="section-card"><h4>🛠️ Technical Skills</h4></div>', unsafe_allow_html=True)
                    skills_html = ""
                    for skill in resume_data['skills'][:15]:  # Show first 15 skills
                        skills_html += f'<span class="skill-tag">{skill}</span>'
                    st.markdown(skills_html, unsafe_allow_html=True)
                    
                    if len(resume_data['skills']) > 15:
                        st.info(f"... and {len(resume_data['skills']) - 15} more skills")
                
                # Experience section
                if resume_data.get('experience'):
                    st.markdown('<div class="section-card"><h4>💼 Work Experience</h4></div>', unsafe_allow_html=True)
                    for i, exp in enumerate(resume_data['experience'][:5]):  # Show first 5 experiences
                        st.markdown(f'<div class="experience-item"><strong>{i+1}.</strong> {exp}</div>', unsafe_allow_html=True)
                
                # Education section
                if resume_data.get('education'):
                    st.markdown('<div class="section-card"><h4>🎓 Education</h4></div>', unsafe_allow_html=True)
                    for i, edu in enumerate(resume_data['education'][:3]):  # Show first 3 education entries
                        st.markdown(f'<div class="experience-item"><strong>{i+1}.</strong> {edu}</div>', unsafe_allow_html=True)
                
                # Projects section
                if resume_data.get('projects'):
                    st.markdown('<div class="section-card"><h4>🚀 Projects</h4></div>', unsafe_allow_html=True)
                    for i, proj in enumerate(resume_data['projects'][:3]):  # Show first 3 projects
                        st.markdown(f'<div class="experience-item"><strong>{i+1}.</strong> {proj}</div>', unsafe_allow_html=True)
                
                # Raw text section (collapsible)
                if resume_data.get('raw_text'):
                    with st.expander("📝 View Full Extracted Text"):
                        st.text_area("", resume_data['raw_text'][:2000] + "..." if len(resume_data['raw_text']) > 2000 else resume_data['raw_text'], height=300)
            
            else:
                st.error("❌ Failed to process the resume. Please try a different file.")
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
    
    else:
        st.info("👆 Please upload a resume file to get started")
        
        # Show sample resume suggestions
        st.markdown("### 📋 Sample Resumes Available")
        sample_files = [f for f in os.listdir("sample_resumes") if f.endswith('.pdf')]
        if sample_files:
            col1, col2, col3 = st.columns(3)
            for i, file in enumerate(sample_files[:6]):
                with [col1, col2, col3][i % 3]:
                    st.markdown(f"• {file}")

# Tab 2: Feedback & Suggestions
with tab2:
    st.markdown("### 💬 Provide Feedback")
    
    # Feedback form
    st.markdown('<div class="feedback-card">', unsafe_allow_html=True)
    
    # Feedback input
    feedback_text = st.text_area(
        "Share your thoughts about the resume evaluation system:",
        placeholder="How was your experience? Any suggestions for improvement?",
        height=150
    )
    
    # Rating system
    col1, col2 = st.columns([1, 2])
    
    with col1:
        rating = st.selectbox(
            "Rate the system:",
            ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]
        )
    
    with col2:
        feedback_type = st.selectbox(
            "Feedback type:",
            ["General", "Bug Report", "Feature Request", "Improvement Suggestion"]
        )
    
    # Submit button
    if st.button("Submit Feedback", type="primary", use_container_width=True):
        if feedback_text.strip():
            # Create feedback data
            feedback_data = {
                "timestamp": datetime.now().isoformat(),
                "feedback": feedback_text,
                "rating": rating,
                "type": feedback_type,
                "user_id": "anonymous"
            }
            
            # Save to JSON file (mock storage)
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
                
                # Show confirmation
                st.info(f"Thank you for your {rating} rating! Your feedback has been recorded.")
                
            except Exception as e:
                st.error(f"❌ Error saving feedback: {str(e)}")
        else:
            st.warning("⚠️ Please enter some feedback before submitting.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display recent feedback
    if os.path.exists("feedback.json"):
        try:
            with open("feedback.json", "r") as f:
                all_feedback = json.load(f)
            
            if all_feedback:
                st.markdown("### 📊 Recent Feedback")
                
                # Show feedback statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Feedback", len(all_feedback))
                with col2:
                    avg_rating = sum(1 for f in all_feedback if "⭐⭐⭐⭐" in f.get('rating', '') or "⭐⭐⭐⭐⭐" in f.get('rating', ''))
                    st.metric("Positive Ratings", f"{avg_rating}/{len(all_feedback)}")
                with col3:
                    st.metric("Latest", all_feedback[-1]['timestamp'][:10] if all_feedback else "None")
                
                # Show recent feedback entries
                for i, feedback in enumerate(all_feedback[-5:]):  # Show last 5 feedback entries
                    with st.expander(f"Feedback #{len(all_feedback) - i} - {feedback['rating']} - {feedback['type']}"):
                        st.write(f"**Time:** {feedback['timestamp']}")
                        st.write(f"**Feedback:** {feedback['feedback']}")
        except Exception as e:
            st.error(f"Error loading feedback: {str(e)}")

# Sidebar
with st.sidebar:
    st.markdown("### 📋 How to Use")
    st.markdown("""
    **1. Resume Analysis Tab:**
    - Upload your resume file
    - View AI-extracted information
    - See parsed content in organized sections
    - Analyze skills, experience, and education
    
    **2. Feedback Tab:**
    - Provide system feedback
    - Rate your experience
    - View feedback history
    - Submit improvement suggestions
    """)
    
    st.markdown("### 🔧 System Information")
    st.info("""
    **Version:** 1.0.0  
    **Features:** 
    - AI-powered resume parsing
    - Text extraction and analysis
    - Skills identification
    - Feedback collection system
    
    **Status:** Development Phase
    """)
    
    st.markdown("### 📊 Quick Stats")
    if os.path.exists("feedback.json"):
        try:
            with open("feedback.json", "r") as f:
                feedback_data = json.load(f)
            st.metric("Total Feedback", len(feedback_data))
        except:
            st.metric("Total Feedback", "0")
    else:
        st.metric("Total Feedback", "0")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>AI Resume Evaluator</strong> | Intelligent Resume Analysis System</p>
    <p style="font-size: 0.9rem;">Powered by Advanced NLP and Machine Learning Technologies</p>
</div>
""", unsafe_allow_html=True)