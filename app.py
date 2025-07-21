import streamlit as st
from modules import parser, jd_handler, similarity, suggestions

def main():
    st.title("AI Resume Evaluator")

    # Initialize the ResumeMatcher
    matcher = similarity.ResumeMatcher()

    # 1. Upload Resume
    uploaded_file = st.file_uploader("Upload your Resume (PDF, DOCX)", type=["pdf", "docx"])
    if uploaded_file:
        resume_data = parser.parse_resume(uploaded_file)  # Your parser returns structured dict

    # 2. Select or Enter JD
    jds = jd_handler.load_predefined_jds("data/predefined_jds.json")
    jd_choice = st.selectbox("Select a Job Role", options=list(jds.keys()))
    jd_text = st.text_area("Or enter Job Description", value=jds.get(jd_choice, ""))

    if uploaded_file and jd_text:
        # 3. Calculate Similarity - now using the matcher instance
        results = matcher.get_similarity_score(
            jd_text, 
            [resume_data], 
            mode="structured", 
            return_analysis=True
        )
        
        # Extract the first result (since we only passed one resume)
        if results:
            idx, score, analysis = results[0]
            
            # 4. Show Similarity Score
            st.metric(label="Resume-JD Match %", value=f"{score*100:.2f}%")

            # 5. Generate & Show Suggestions
            suggestion_results = suggestions.suggest_resume_improvements(resume_data, jd_text)
            for priority, tips in suggestion_results.items():
                with st.expander(f"{priority.upper()} Suggestions ({len(tips)})"):
                    for tip in tips:
                        st.write(f"- {tip}")

            # 6. Show analysis if available
            if analysis:
                with st.expander("Detailed Match Analysis"):
                    st.json(analysis)

if __name__ == "__main__":
    main()