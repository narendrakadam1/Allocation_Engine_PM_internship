import streamlit as st, json, os
from ui import apply_theme, render_header

DATA_PATH = "data/organizations.json"

st.set_page_config(page_title="Organization Portal", layout="wide")
apply_theme()
render_header("Organization Portal", "Post job descriptions, view applicants")

if os.path.exists(DATA_PATH):
    with open(DATA_PATH, "r") as f: orgs = json.load(f)
else:
    orgs = []

st.markdown("### 🏢 Organization Registration")
with st.form("org_register"):
    org_name = st.text_input("Organization Name")
    email = st.text_input("Official Email")
    location = st.text_input("Location")
    submitted = st.form_submit_button("Register / Update Organization")
    if submitted:
        org = {"org_name": org_name, "email": email, "location": location, "jobs": []}
        orgs.append(org)
        with open(DATA_PATH, "w") as f: json.dump(orgs, f, indent=2)
        st.success(f"Organization {org_name} saved!")

st.markdown("### 📌 Post Job Descriptions")
with st.form("job_post"):
    jd_title = st.text_input("Job Title")
    jd_skills = st.text_area("Required Skills")
    jd_type = st.selectbox("Internship Type", ["Remote", "On-site", "Hybrid"])
    jd_location = st.text_input("Location")
    jd_submit = st.form_submit_button("Post Job")
    if jd_submit:
        if orgs:
            orgs[-1]["jobs"].append({"title": jd_title, "skills": jd_skills, "type": jd_type, "location": jd_location})
            with open(DATA_PATH, "w") as f: json.dump(orgs, f, indent=2)
            st.success(f"Job '{jd_title}' posted!")
        else:
            st.warning("Please register an organization first!")

st.markdown("### 📋 Registered Organizations")
if orgs:
    st.table(orgs)
