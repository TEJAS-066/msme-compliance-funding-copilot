"""MSME Compliance & Funding Copilot - Streamlit entrypoint.   Run:  streamlit run app.py"""
import streamlit as st

from core.i18n import t
from ui import (admin_view, channel_view, chat_view, checklist_view, dashboard,
                documents_view, forms_view, profile_view, schemes_view,
                tasks_view)
from ui.common import apply_custom_styles, get_profile

st.set_page_config(page_title="MSME Copilot — TEJAS066", page_icon="🏛️", layout="wide")

apply_custom_styles()

PAGES = [
    ("nav_dashboard", dashboard.render),
    ("nav_profile", profile_view.render),
    ("nav_documents", documents_view.render),
    ("nav_schemes", schemes_view.render),
    ("nav_checklist", checklist_view.render),
    ("nav_copilot", chat_view.render),
    ("nav_channel", channel_view.render),
    ("nav_forms", forms_view.render),
    ("nav_tasks", tasks_view.render),
    ("nav_admin", admin_view.render),
]

with st.sidebar:
    st.markdown("""
        <div style="margin-bottom: 12px;">
            <div style="font-size: 0.72rem; font-weight: 700; color: #0B6E4F; text-transform: uppercase; letter-spacing: 0.5px;">
                TEJAS 2026 Finals • Team TEJAS066
            </div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-top: 2px;">
                🏛️ MSME Copilot
            </div>
            <div style="font-size: 0.8rem; color: #64748B;">
                GovTech AI Decision Support
            </div>
        </div>
    """, unsafe_allow_html=True)

    choice = st.radio("Language / மொழி", ["English", "தமிழ்"], horizontal=True, key="lang_radio")
    st.session_state["lang"] = "ta" if choice == "தமிழ்" else "en"
    lang = st.session_state["lang"]

    st.write("")
    st.caption("NAVIGATION / வழிகாட்டி")
    page_key = st.radio("Navigate", [k for k, _ in PAGES], key="nav", format_func=lambda k: t(k, lang), label_visibility="collapsed")

    st.write("---")
    p = get_profile()
    if p.get("is_demo"):
        st.markdown("""
            <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 6px; padding: 8px 10px; font-size: 0.78rem; color: #166534;">
                <strong>Demo Persona:</strong> Lakshmi (Tiruppur Textiles)
            </div>
        """, unsafe_allow_html=True)
    st.caption("Rules decide • AI explains • Owner acts")

dict(PAGES)[page_key]()
