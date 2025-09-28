import streamlit as st
from textwrap import dedent

def apply_theme():
    """Inject premium CSS theme."""
    st.markdown(dedent("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #071133 100%);
        color: #e6eef8;
    }
    .premium-header {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 18px 24px;
        border-radius: 12px;
        background: rgba(255,255,255,0.03);
        box-shadow: 0 6px 30px rgba(2,6,23,0.6);
        margin-bottom: 18px;
    }
    .premium-title { font-size: 22px; font-weight: 700; margin: 0; }
    .premium-sub { font-size: 13px; color: rgba(230,238,248,0.7); margin: 0; }
    .card {
        background: rgba(255,255,255,0.02);
        padding: 16px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.04);
        box-shadow: 0 8px 24px rgba(2,6,23,0.5);
        margin-bottom: 14px;
    }
    .stButton>button {
        border-radius: 10px;
        padding: 8px 14px;
        font-weight: 600;
    }
    </style>
    """), unsafe_allow_html=True)


def render_header(title="AI Recruiter", tagline="Smarter Resume Analysis"):
    """Premium-looking header."""
    st.markdown(f"""
    <div class="premium-header">
        <div style="flex:1">
            <div class="premium-title">{title}</div>
            <div class="premium-sub">{tagline}</div>
        </div>
        <div style="display:flex;gap:8px;">
            <button class="stButton">New Session</button>
            <button class="stButton">Docs</button>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar(default="Upload Resume"):
    """Sidebar with navigation, returns 'selected' just like option_menu did."""
    with st.sidebar:
        st.title("AI Recruiter")
        nav = st.radio("Navigation", ["Upload Resume", "About"], index=0 if default=="Upload Resume" else 1)
        st.markdown("---")
        if st.button("Upload sample resume"):
            st.session_state["upload_sample"] = True
        if st.button("Clear results"):
            st.session_state["clear_results"] = True
    return nav


def page_section(title, render_fn=None):
    """Reusable styled section card."""
    st.markdown(f"<div class='card'><h4>{title}</h4>", unsafe_allow_html=True)
    if render_fn: render_fn()
    st.markdown("</div>", unsafe_allow_html=True)
