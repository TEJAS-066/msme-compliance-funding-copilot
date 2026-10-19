"""MSME Compliance & Funding Copilot - Streamlit entrypoint.   Run:  streamlit run app.py"""
import streamlit as st

from core.i18n import t
from ui import (admin_view, channel_view, chat_view, checklist_view, dashboard, documents_view, forms_view, profile_view,
                schemes_view, tasks_view)

st.set_page_config(page_title="MSME Copilot", page_icon="🧾", layout="wide")

PAGES = [
    ("nav_dashboard", dashboard.render), ("nav_profile", profile_view.render), ("nav_documents", documents_view.render),
    ("nav_schemes", schemes_view.render), ("nav_checklist", checklist_view.render), ("nav_copilot", chat_view.render), ("nav_channel", channel_view.render),
    ("nav_forms", forms_view.render), ("nav_tasks", tasks_view.render), ("nav_admin", admin_view.render),
]

with st.sidebar:
    choice = st.radio("Language / மொழி", ["English", "தமிழ்"], horizontal=True, key="lang_radio")
    st.session_state["lang"] = "ta" if choice == "தமிழ்" else "en"
    lang = st.session_state["lang"]
    st.title("🧾 MSME Copilot")
    page_key = st.radio("Navigate", [k for k, _ in PAGES], key="nav", format_func=lambda k: t(k, lang), label_visibility="collapsed")

dict(PAGES)[page_key]()
