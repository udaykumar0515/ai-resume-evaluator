# AI Resume Evaluator - Simple Teacher Presentation Version
import streamlit as st
import os
import tempfile
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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Resume Evaluator</h1>
    <p>Simple Resume Text Extraction and Feedback System</p>
</div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["📄 Resume Evaluation", "💬 Feedback"])

# Tab 1: Resume Evaluation
with tab1:
    st.markdown("### Upload Resume and Extract Text")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a resume file",
        type=['pdf', 'docx', 'txt'],
        help="Upload your resume in PDF, DOCX, or TXT format"
    )
    
    # Job Description dropdown (just for show)
    st.markdown("### Select Job Description (Optional)")
    jd_options = [
        "Select a job description...",
        "Software Developer",
        "Data Scientist", 
        "Web Developer",
        "Machine Learning Engineer",
        "Full Stack Developer"
    ]
    selected_jd = st.selectbox("Choose a predefined job description:", jd_options)
    
    if uploaded_file is not None:
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Parse the resume
            with st.spinner("Extracting text from resume..."):
                resume_data = parser.parse_resume(tmp_file_path)
            
            # Debug information
            st.write("Debug - Resume data keys:", list(resume_data.keys()) if resume_data else "None")
            
            if resume_data and resume_data.get('raw_text'):
                st.success("✅ Resume processed successfully!")
                
                # Show extracted text
                st.markdown("### Extracted Resume Text")
                st.text_area("", resume_data['raw_text'], height=400)
                
                # Show file info
                st.info(f"File: {uploaded_file.name} | Characters: {len(resume_data['raw_text'])}")
            
            else:
                st.error("❌ Failed to extract text from the resume.")
                if resume_data:
                    st.write("Available data:", resume_data)
            
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
            # Just show alert - no real storage
            st.success("✅ Feedback submitted successfully!")
            st.balloons()
        else:
            st.warning("⚠️ Please enter some feedback before submitting.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>AI Resume Evaluator - Simple Version | Educational Purpose</p>
</div>
""", unsafe_allow_html=True)