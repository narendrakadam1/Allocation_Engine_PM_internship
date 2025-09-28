import streamlit as st
from ui import apply_theme, render_header

st.set_page_config(page_title="AI Internship Allocation System", layout="wide")

# Theme
apply_theme()
render_header("PM Internship Allocation", "AI-powered fair internship matching")

st.markdown("## Welcome 👋")
st.write("""
This system helps students, organizations, and administrators
coordinate internship allocation in a transparent, fair, and AI-driven way.

Use the sidebar to navigate between portals:
- **Student Portal** → Register, create profile, apply for internships  
- **Organization Portal** → Register, post jobs, view applicants  
- **Administrator Portal** → Manage cycles, approve matches, export reports  
- **Allocation Dashboard** → AI matching flow & explainable recommendations  
- **Resume Analysis** → Upload a resume and run it through the AI pipeline  
""")
