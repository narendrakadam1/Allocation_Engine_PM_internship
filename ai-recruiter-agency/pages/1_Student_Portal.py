import streamlit as st, json, os
from ui import apply_theme, render_header

DATA_PATH = "data/students.json"

st.set_page_config(page_title="Student Portal", layout="wide")
apply_theme()
render_header("Student Portal", "Register, create profile, apply internships")

# Load DB
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, "r") as f: students = json.load(f)
else:
    students = []

st.markdown("### 🧑‍🎓 Student Registration / Login")
with st.form("student_register"):
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    education = st.text_area("Education (Degree, College, Year)")
    skills = st.text_area("Skills (comma separated)")
    preferences = st.text_area("Internship Preferences (location, role, type)")
    submitted = st.form_submit_button("Register / Update Profile")
    if submitted:
        profile = {"name": name, "email": email, "education": education, "skills": skills, "preferences": preferences}
        students.append(profile)
        with open(DATA_PATH, "w") as f: json.dump(students, f, indent=2)
        st.success(f"Profile for {name} saved!")

st.markdown("### 📄 Applied Students")
if students:
    st.table(students)
