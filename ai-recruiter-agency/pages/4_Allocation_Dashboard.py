import streamlit as st
import json, os
from ui import apply_theme, render_header, page_section
from agents.orchestrator import Orchestrator
from utils.parsing import safe_parse

st.set_page_config(page_title="Allocation Dashboard", layout="wide")
apply_theme()
render_header("AI Allocation", "Skill matching & automated allocation")

orch = Orchestrator()

students_path = os.path.join("data", "students.json")
orgs_path = os.path.join("data", "organizations.json")

students = json.load(open(students_path)) if os.path.exists(students_path) else []
orgs = json.load(open(orgs_path)) if os.path.exists(orgs_path) else []

st.markdown("### AI Allocation Dashboard")
st.write("Students:", len(students), " | Organizations:", len(orgs))

from utils.parsing import safe_parse

if st.button("Run Allocation"):
    if not students or not orgs:
        st.warning("No students or organizations registered. Add some first.")
    else:
        with st.spinner("Running AI allocation..."):
            results = []
            for s in students:
                parsed = orch.process_profile(s, orgs)
                results.extend(parsed.get("matches", []))

        if results:
            page_section("Allocation Results", lambda: st.dataframe(results))
        else:
            st.info("No matches found.")

