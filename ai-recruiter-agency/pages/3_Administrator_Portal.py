import streamlit as st
from ui import apply_theme, render_header, page_section

st.set_page_config(page_title="Administrator Portal", layout="wide")
apply_theme()
render_header("Administrator Dashboard", "Monitor cycles, stats, and approvals")

st.markdown("### 📊 Dashboard")
st.metric("Total Students", 120)
st.metric("Total Organizations", 35)
st.metric("Jobs Posted", 50)

st.markdown("---")

st.markdown("### ✅ Approve / Override Matches")
with st.form("approve"):
    student = st.selectbox("Select Student", ["Alice", "Bob", "Charlie"])
    decision = st.radio("Decision", ["Approve", "Reject", "Reassign"])
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.success(f"{student} decision recorded: {decision}")

st.markdown("---")
st.markdown("### 📤 Export Reports")
if st.button("Export PDF"):
    st.info("PDF Export (placeholder)")
if st.button("Export CSV"):
    st.info("CSV Export (placeholder)")
