# Simplified AI Resume Evaluator - Teacher Presentation Version
import streamlit as st
import pandas as pd
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, Any

# Import only basic modules
try:
    from modules import parser
except Exception as e:
    st.error(f"❌ Error importing modules: {e}")
    st.stop()

# Configure Streamlit
st.set_page_config(
    page_title="AI Resume Evaluator",
    page_icon="📄", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple CSS styling
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

.section-header {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 5px;
    border-left: 4px solid #667eea;
    margin: 1rem 0;
}

.feedback-box {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 5px;
    border: 1px solid #dee2e6;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Resume Evaluator</h1>
    <p>Basic Resume Analysis and Feedback System</p>
</div>
""", unsafe_allow_html=True)

# Create two tabs
tab1, tab2 = st.tabs(["📄 Resume Evaluation", "💬 Feedback"])

# Tab 1: Resume Evaluation
with tab1:
    st.markdown("### Upload and Analyze Resume")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a resume file",
        type=['pdf', 'docx', 'txt'],
        help="Upload your resume in PDF, DOCX, or TXT format"
    )
    
    if uploaded_file is not None:
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Parse the resume
            with st.spinner("Processing resume..."):
                resume_data = parser.parse_resume(tmp_file_path)
            
            if resume_data:
                st.success("✅ Resume processed successfully!")
                
                # Display extracted text in sections
                st.markdown("### Extracted Resume Content")
                
                # Personal Information
                if resume_data.get('personal_info'):
                    st.markdown('<div class="section-header"><h4>👤 Personal Information</h4></div>', unsafe_allow_html=True)
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
                
                # Skills
                if resume_data.get('skills'):
                    st.markdown('<div class="section-header"><h4>🛠️ Skills</h4></div>', unsafe_allow_html=True)
                    skills_text = ", ".join(resume_data['skills'][:10])  # Show first 10 skills
                    st.write(skills_text)
                
                # Experience
                if resume_data.get('experience'):
                    st.markdown('<div class="section-header"><h4>💼 Work Experience</h4></div>', unsafe_allow_html=True)
                    for i, exp in enumerate(resume_data['experience'][:3]):  # Show first 3 experiences
                        st.write(f"**{i+1}.** {exp}")
                
                # Education
                if resume_data.get('education'):
                    st.markdown('<div class="section-header"><h4>🎓 Education</h4></div>', unsafe_allow_html=True)
                    for i, edu in enumerate(resume_data['education'][:3]):  # Show first 3 education entries
                        st.write(f"**{i+1}.** {edu}")
                
                # Raw text (simplified)
                if resume_data.get('raw_text'):
                    st.markdown('<div class="section-header"><h4>📝 Full Text</h4></div>', unsafe_allow_html=True)
                    st.text_area("Extracted Text", resume_data['raw_text'][:1000] + "..." if len(resume_data['raw_text']) > 1000 else resume_data['raw_text'], height=200)
            
            else:
                st.error("❌ Failed to process the resume. Please try a different file.")
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
    
    else:
        st.info("👆 Please upload a resume file to get started")

# Tab 2: Feedback
with tab2:
    st.markdown("### Provide Feedback")
    
    # Simple feedback form
    st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
    
    # Feedback input
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
            # Simple feedback storage
            feedback_data = {
                "timestamp": datetime.now().isoformat(),
                "feedback": feedback_text,
                "rating": rating
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display recent feedback
    if os.path.exists("feedback.json"):
        try:
            with open("feedback.json", "r") as f:
                all_feedback = json.load(f)
            
            if all_feedback:
                st.markdown("### Recent Feedback")
                for i, feedback in enumerate(all_feedback[-3:]):  # Show last 3 feedback entries
                    with st.expander(f"Feedback {len(all_feedback) - i} - {feedback['rating']}"):
                        st.write(f"**Time:** {feedback['timestamp']}")
                        st.write(f"**Feedback:** {feedback['feedback']}")
        except Exception as e:
            st.error(f"Error loading feedback: {str(e)}")

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Instructions")
    st.markdown("""
    1. **Resume Evaluation Tab:**
       - Upload your resume (PDF/DOCX/TXT)
       - View extracted information
       - See parsed content in sections
    
    2. **Feedback Tab:**
       - Provide feedback about the system
       - Rate the experience
       - View recent feedback
    """)
    
    st.markdown("### 🔧 System Info")
    st.info("""
    **Version:** Basic 1.0  
    **Features:** Resume parsing, text extraction, feedback collection  
    **Status:** Development Phase
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>AI Resume Evaluator - Basic Version | Made for Educational Purposes</p>
</div>
""", unsafe_allow_html=True)
