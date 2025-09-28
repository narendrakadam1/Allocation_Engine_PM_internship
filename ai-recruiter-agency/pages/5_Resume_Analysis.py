import streamlit as st
import os, json
from ui import apply_theme, render_header, page_section
from agents.orchestrator import Orchestrator
from utils.parsing import safe_parse

st.set_page_config(page_title="Resume Analysis", layout="wide")
apply_theme()
render_header("Resume Analysis", "Upload resumes and analyze with AI pipeline")

orch = Orchestrator()

uploaded_file = st.file_uploader("Upload a resume (PDF/TXT)", type=["pdf", "txt"])

if uploaded_file:
    os.makedirs("data", exist_ok=True)
    save_path = os.path.join("data", uploaded_file.name)
    with st.spinner("Analyzing resume..."):
        raw_result = orch.process_resume(save_path)
        result = safe_parse(raw_result)

    if not result:
        st.error("Pipeline returned empty result.")
    else:
        for k, v in result.items():
        # Use json for dicts, write otherwise
         if isinstance(v, (dict, list)):
            page_section(str(k), lambda vv=v: st.json(vv))
         else:
            page_section(str(k), lambda vv=v: st.write(vv))

    if not isinstance(result, dict):
        st.error("Pipeline returned unexpected result format.")
    else:
        # Safe display: iterate keys
        for k, v in result.items():
            try:
                page_section(str(k), lambda vv=v: st.write(vv))
            except Exception:
                st.write(f"{k}: {v}")
