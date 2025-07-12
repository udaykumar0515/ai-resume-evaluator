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

