# # parser.py
# from parser import parse_resume
# parsed_data = parse_resume(r"D:\uday\Vscode\Projects\AI_resume_evaluator\resumes\resume_webdev.pdf")
# print(parsed_data)

# # jd_handler.py
# from jd_handler import get_job_roles, get_description_for_role

# def interactive_test():
#     print("Available job roles:")
#     roles = get_job_roles()
#     for i, role in enumerate(roles, 1):
#         print(f"{i}. {role}")

#     choice = input("\nEnter a job role name exactly as above OR type 'custom' to enter your own JD:\n").strip()

#     if choice.lower() == 'custom':
#         jd_text = input("Enter your custom job description:\n")
#         print("\n--- You entered a custom JD ---\n")
#         print(jd_text)
#     elif choice in roles:
#         jd_text = get_description_for_role(choice)
#         print(f"\n--- Job Description for '{choice}' ---\n")
#         print(jd_text)
#     else:
#         print("Invalid input. Please run the test again.")

# if __name__ == "__main__":
#     interactive_test()

# similarity.py
from similarity import ResumeMatcher

# 📝 Sample JD
jd_text = """
We are looking for a Machine Learning Engineer with experience in Python, scikit-learn, and model evaluation.
Bonus if you've used TensorFlow or deployed models in production.
"""

# 👨‍🎓 Simulated structured resume (like parsed student resume)
structured_resume = {
    "skills": ["Python", "Machine Learning", "scikit-learn", "TensorFlow"],
    "projects": [
        {"title": "ML Classifier", "description": "Built a spam classifier using scikit-learn"},
        {"title": "Deployed Model", "description": "Deployed a sentiment analysis model using Flask and Docker"}
    ],
    "education": "BTech in Computer Science",
    "experience": []
}

# 👨‍💼 Simulated raw resume text (like for recruiter mode)
raw_resume = """
Experienced Python developer with a strong background in data science and machine learning.
Worked on classification models using scikit-learn and deep learning models using TensorFlow and Keras.
Deployed models to AWS EC2 using Flask.
"""

# 🔍 Initialize the matcher
matcher = ResumeMatcher(method="tfidf")

# 🎯 Structured mode test (student mode)
structured_result = matcher.get_similarity_score(
    jd_text, [structured_resume], mode="structured", return_analysis=True
)
print("\n🎓 Structured Resume Result:")
print(structured_result)

# 📦 Raw mode test (recruiter mode)
raw_result = matcher.get_similarity_score(
    jd_text, [raw_resume], mode="raw", return_analysis=True
)
print("\n💼 Raw Resume Result:")
print(raw_result)
