# AI Resume Evaluator - Simple Teacher Presentation Version
import streamlit as st
import os
import tempfile
import json
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
    
    # Job Description dropdown
    st.markdown("### Select Job Description")
    
    # Load predefined JDs
    try:
        with open("data/predefined_jds.json", "r") as f:
            predefined_jds = json.load(f)
        
        jd_options = ["Select a job description..."] + list(predefined_jds.keys())
        selected_jd = st.selectbox("Choose a predefined job description:", jd_options)
        
        # Display selected JD
        if selected_jd != "Select a job description...":
            jd_data = predefined_jds[selected_jd]
            
            st.markdown("### 📋 Selected Job Description")
            st.markdown(f"**Position:** {jd_data['title']}")
            st.markdown(f"**Description:** {jd_data['description']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Requirements:**")
                for req in jd_data['requirements']:
                    st.write(f"• {req}")
            
            with col2:
                st.markdown("**Responsibilities:**")
                for resp in jd_data['responsibilities']:
                    st.write(f"• {resp}")
    
    except Exception as e:
        st.error(f"Error loading job descriptions: {e}")
        selected_jd = "Select a job description..."
    
    if uploaded_file is not None:
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Parse the resume
            with st.spinner("Extracting text from resume..."):
                resume_data = parser.parse_resume(tmp_file_path)
            
            if resume_data:
                st.success("✅ Resume processed successfully!")
                
                # Show file info
                st.info(f"File: {uploaded_file.name} | Processing Date: {resume_data.get('metadata', {}).get('processing_date', 'Unknown')}")
                
                # Show sections found with their content
                st.markdown("### 📋 Resume Sections and Content")
                sections = resume_data.get('sections', {})
                if sections:
                    for section_name, section_content in sections.items():
                        if section_content.strip():  # Only show non-empty sections
                            with st.expander(f"📄 {section_name}"):
                                st.text(section_content)
                
                # Show contact information
                contact = resume_data.get('contact', {})
                if contact:
                    st.markdown("### 👤 Contact Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        if contact.get('name'):
                            st.write(f"**Name:** {contact['name']}")
                        if contact.get('email'):
                            st.write(f"**Email:** {contact['email']}")
                    with col2:
                        if contact.get('phone'):
                            st.write(f"**Phone:** {contact['phone']}")
                        if contact.get('location'):
                            st.write(f"**Location:** {contact['location']}")
                
                # Show skills
                skills = resume_data.get('skills', [])
                if skills:
                    st.markdown("### 🛠️ Skills Detected")
                    skills_text = ", ".join(skills[:10])  # Show first 10 skills
                    st.write(skills_text)
                    if len(skills) > 10:
                        st.info(f"... and {len(skills) - 10} more skills")
                
                # Show education
                education = resume_data.get('education', [])
                if education:
                    st.markdown("### 🎓 Education")
                    for i, edu in enumerate(education[:3], 1):  # Show first 3
                        st.write(f"{i}. {edu}")
                
                # Show projects
                projects = resume_data.get('projects', [])
                if projects:
                    st.markdown("### 🚀 Projects")
                    for i, proj in enumerate(projects[:3], 1):  # Show first 3
                        st.write(f"{i}. {proj}")
                
                # Show raw text
                if resume_data.get('raw_text'):
                    st.markdown("### 📝 Full Extracted Text")
                    st.text_area("", resume_data['raw_text'], height=300)
            
            else:
                st.error("❌ Failed to process the resume.")
            
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