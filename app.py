"""MSME Compliance & Funding Copilot - Streamlit entrypoint.   Run:  streamlit run app.py"""
import streamlit as st

from core.i18n import t
from ui import (admin_view, channel_view, chat_view, checklist_view, dashboard,
                documents_view, forms_view, profile_view, schemes_view,
                tasks_view)
from ui.common import (apply_custom_styles, get_profile,
                       render_spotlight_tour, show_onboarding_tour)

st.set_page_config(page_title="MSME Copilot — TEJAS066", page_icon="🏛️", layout="wide")

apply_custom_styles(st.session_state.get("theme", "light"))

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
    st.caption("TEJAS 2026 Finals • Team TEJAS066")
    st.markdown("## 🏛️ MSME Copilot")
    st.caption("GovTech AI Decision Support")

    LANG_MAP = {"English": "en", "தமிழ்": "ta", "हिन्दी": "hi", "తెలుగు": "te"}
    choice = st.radio("Language / மொழி / भाषा / భాష", list(LANG_MAP.keys()), horizontal=True, key="lang_radio")
    st.session_state["lang"] = LANG_MAP.get(choice, "en")
    lang = st.session_state["lang"]

    if st.button(t("btn_quick_tour", lang), use_container_width=True):
        st.session_state["trigger_spotlight"] = True
        st.session_state["tour_open"] = True
        st.session_state["tour_step"] = 1
        st.rerun()

    st.write("")
    st.caption("NAVIGATION / வழிகாட்டி")
    page_key = st.radio("Navigate", [k for k, _ in PAGES], key="nav", format_func=lambda k: t(k, lang), label_visibility="collapsed")

    st.write("---")
    p = get_profile()
    if p.get("is_demo"):
        st.success("Demo: Lakshmi (Tiruppur)")
    st.caption("Rules decide • AI explains • Owner acts")

render_spotlight_tour()

if st.session_state.get("tour_open"):
    show_onboarding_tour()

dict(PAGES)[page_key]()

