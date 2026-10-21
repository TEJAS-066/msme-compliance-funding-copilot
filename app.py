"""MSME Compliance & Funding Copilot - Streamlit entrypoint.   Run:  streamlit run app.py"""
import secrets

import streamlit as st

from core import config, db
from core.i18n import t
from ui import (admin_view, channel_view, chat_view, checklist_view, dashboard, documents_view, forms_view,
                profile_view, schemes_view, shell, tasks_view)
from ui.common import apply_custom_styles, get_profile
from ui.tour_content import LANGS

config.load_env_file()          # reads .env if present (only NAMES are ever reported, never values)
st.set_page_config(page_title="MSME Copilot — TEJAS066", page_icon="🏛️", layout="wide")


@st.cache_resource
def _housekeeping() -> int:
    """Once per server process: in shared mode delete data of visitors inactive for 7+ days."""
    return db.purge_inactive_owners(7) if config.get("MSME_MULTIUSER") == "1" else 0


if config.get("MSME_MULTIUSER") == "1":          # shared deployment: every browser session gets private data
    _housekeeping()
    db.set_owner(st.session_state.setdefault("owner", "u" + secrets.token_hex(6)))
else:                                            # laptop demo: one local user (also what the WhatsApp webhook reads)
    db.set_owner("local")

apply_custom_styles(st.session_state.get("theme", "light"))

PAGES = [
    ("nav_dashboard", dashboard.render), ("nav_profile", profile_view.render), ("nav_documents", documents_view.render),
    ("nav_schemes", schemes_view.render), ("nav_checklist", checklist_view.render), ("nav_copilot", chat_view.render),
    ("nav_channel", channel_view.render), ("nav_forms", forms_view.render), ("nav_tasks", tasks_view.render),
    ("nav_admin", admin_view.render),
]
NAV_KEYS = [k for k, _ in PAGES]

with st.sidebar:
    st.caption("TEJAS 2026 Finals • Team TEJAS066")
    st.markdown("## 🏛️ MSME Copilot")
    names = [n for _, n in LANGS]
    choice = st.radio("Language / மொழி / भाषा / భాష", names, horizontal=True, key="lang_radio")
    lang = LANGS[names.index(choice)][0]
    st.session_state["lang"] = lang
    st.write("")
    page_key = st.radio("Navigate", NAV_KEYS, key="nav", format_func=lambda k: t(k, lang), label_visibility="collapsed")
    st.write("---")
    if get_profile().get("is_demo"):
        st.success("Demo: Lakshmi (Tiruppur)")
    st.caption(t("sidebar_motto", lang))

shell.install(lang, NAV_KEYS, page_key)
dict(PAGES)[page_key]()
