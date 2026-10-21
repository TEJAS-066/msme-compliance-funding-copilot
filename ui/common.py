"""Shared UI helpers, GovTech clean styling, and 5-stage stepper."""
from __future__ import annotations

import textwrap
import streamlit as st

from core import config, db
from core import profile as P
from core.i18n import t
from services import llm


def lang() -> str:
    return st.session_state.get("lang", "en")


def get_profile() -> dict:
    if "profile" not in st.session_state:
        st.session_state["profile"] = db.load_profile() or P.empty_profile()
    return st.session_state["profile"]


def save_profile(p: dict) -> None:
    st.session_state["profile"] = p
    db.save_profile(p)


def multiuser() -> bool:
    return config.get("MSME_MULTIUSER") == "1"


def admin_unlocked() -> bool:
    """Local mode: always. Shared mode: only after the correct ADMIN_PIN (and only if one is configured)."""
    if not multiuser():
        return True
    return bool(st.session_state.get("admin_ok"))


def apply_custom_styles(theme: str | None = None) -> None:
    """Inject clean, human-crafted GovTech & Fintech portal styling with full Light / Dark theme support."""
    theme = theme or st.session_state.get("theme", "light")
    is_dark = "dark" in str(theme).lower() or "🌙" in str(theme)

    if is_dark:
        bg_main = "#0B1120"
        sidebar_bg = "#0F172A"
        sidebar_border = "#1E293B"
        card_bg = "#111827"
        border_col = "#1F2937"
        text_primary = "#F8FAFC"
        text_secondary = "#94A3B8"
        heading_col = "#FFFFFF"
        metric_bg = "#111827"
        btn_sec_bg = "#1F2937"
        btn_sec_border = "#374151"
        btn_sec_text = "#FFFFFF"
        btn_sec_hover = "#374151"
        input_bg = "#1F2937"
    else:
        bg_main = "#F8FAFC"
        sidebar_bg = "#F1F5F9"
        sidebar_border = "#E2E8F0"
        card_bg = "#FFFFFF"
        border_col = "#E2E8F0"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        heading_col = "#0F172A"
        metric_bg = "#FFFFFF"
        btn_sec_bg = "#FFFFFF"
        btn_sec_border = "#CBD5E1"
        btn_sec_text = "#0F172A"
        btn_sec_hover = "#F1F5F9"
        input_bg = "#FFFFFF"

    css = textwrap.dedent(f"""
    <style>
    /* Full Theme root styling - Guaranteed Full-Screen Dark/Light Uniformity */
    .stApp, div[data-testid="stAppViewContainer"], div[data-testid="stAppViewBlockContainer"], .main, .block-container {{
        background-color: {bg_main} !important;
        background: {bg_main} !important;
        color: {text_primary} !important;
    }}

    /* Streamlit Top Header & Deploy Bar Elimination - No White Strip or Deploy Button */
    header[data-testid="stHeader"], div[data-testid="stHeader"] {{
        background-color: {bg_main} !important;
        background: {bg_main} !important;
        border: none !important;
        box-shadow: none !important;
    }}
    .stDeployButton, div[data-testid="stDeployButton"], button[data-testid="stDeployButton"],
    #MainMenu, footer, div[data-testid="stDecoration"], div[data-testid="stToolbar"], div[data-testid="stStatusWidget"] {{
        display: none !important;
        visibility: hidden !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {sidebar_border} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {text_primary} !important;
    }}

    /* Global Text Contrast */
    .stApp p, .stApp span, .stApp label, .stApp li {{
        color: {text_primary} !important;
    }}

    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
        color: {heading_col} !important;
        font-weight: 700 !important;
    }}

    /* Base typography & layout padding */
    .main .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 2.5rem;
        max-width: 1140px;
    }}
    
    /* Metrics styling */
    div[data-testid="stMetric"] {{
        background-color: {metric_bg} !important;
        border: 1px solid {border_col} !important;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }}
    div[data-testid="stMetricValue"] {{
        font-weight: 700;
        color: {heading_col} !important;
    }}
    div[data-testid="stMetricLabel"] {{
        font-weight: 500;
        color: {text_secondary} !important;
    }}

    /* Container card styling */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {{
        background-color: {card_bg} !important;
        border: 1px solid {border_col} !important;
    }}

    /* Primary buttons - Guaranteed Crisp White Text on Emerald */
    button[data-testid="baseButton-primary"],
    button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button {{
        background-color: #0B6E4F !important;
        background: #0B6E4F !important;
        border-color: #0B6E4F !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }}
    button[data-testid="baseButton-primary"] *,
    button[kind="primary"] *,
    div[data-testid="stFormSubmitButton"] > button * {{
        color: #FFFFFF !important;
    }}
    button[data-testid="baseButton-primary"]:hover,
    button[kind="primary"]:hover {{
        background-color: #085039 !important;
        background: #085039 !important;
        border-color: #085039 !important;
        color: #FFFFFF !important;
    }}
    button[data-testid="baseButton-primary"]:hover *,
    button[kind="primary"]:hover * {{
        color: #FFFFFF !important;
    }}

    /* Secondary / Default Buttons - EXPLICIT HIGH CONTRAST & READABLE */
    button[data-testid="baseButton-secondary"],
    button[kind="secondary"],
    div[data-testid="stButton"] > button:not([data-testid="baseButton-primary"]):not([kind="primary"]) {{
        background-color: {btn_sec_bg} !important;
        background: {btn_sec_bg} !important;
        border: 1.5px solid {btn_sec_border} !important;
        color: {btn_sec_text} !important;
        font-weight: 600 !important;
    }}
    button[data-testid="baseButton-secondary"] *,
    button[kind="secondary"] *,
    div[data-testid="stButton"] > button:not([data-testid="baseButton-primary"]):not([kind="primary"]) * {{
        color: {btn_sec_text} !important;
    }}
    button[data-testid="baseButton-secondary"]:hover,
    button[kind="secondary"]:hover,
    div[data-testid="stButton"] > button:not([data-testid="baseButton-primary"]):not([kind="primary"]):hover {{
        background-color: {btn_sec_hover} !important;
        background: {btn_sec_hover} !important;
        border-color: #0B6E4F !important;
        color: {heading_col} !important;
    }}
    button[data-testid="baseButton-secondary"]:hover *,
    button[kind="secondary"]:hover *,
    div[data-testid="stButton"] > button:not([data-testid="baseButton-primary"]):not([kind="primary"]):hover * {{
        color: {heading_col} !important;
    }}

    /* Inputs, Textareas, Selectboxes */
    input, textarea, div[data-baseweb="input"], div[data-baseweb="base-input"] {{
        background-color: {input_bg} !important;
        border-color: {border_col} !important;
        color: {text_primary} !important;
    }}
    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        border-color: {border_col} !important;
        color: {text_primary} !important;
    }}
    div[data-baseweb="popover"], ul[role="listbox"] {{
        background-color: {input_bg} !important;
        border: 1px solid {border_col} !important;
    }}
    li[role="option"] {{
        background-color: {input_bg} !important;
        color: {text_primary} !important;
    }}
    li[role="option"]:hover, li[aria-selected="true"] {{
        background-color: {btn_sec_hover} !important;
        color: {heading_col} !important;
    }}

    /* Pixel-Perfect Circular 'i' info button */
    div[data-testid="stPopover"] > button {{
        border-radius: 9999px !important;
        width: 38px !important;
        height: 38px !important;
        min-width: 38px !important;
        max-width: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;
        padding: 0 !important;
        margin: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 1.5px solid {border_col} !important;
        background-color: {card_bg} !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        cursor: pointer !important;
    }}
    div[data-testid="stPopover"] > button * {{
        font-size: 1.15rem !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
        color: {heading_col} !important;
        text-align: center !important;
    }}

    /* Mobile Responsive Optimizations (< 768px) */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-top: 0.8rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            padding-bottom: 2rem !important;
        }}
        div[data-testid="stHorizontalBlock"] {{
            flex-wrap: wrap !important;
            gap: 0.5rem !important;
        }}
        div[data-testid="column"] {{
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }}
        div[data-testid="stMetric"] {{
            margin-bottom: 0.5rem;
            width: 100% !important;
        }}
        div[data-testid="stButton"] > button {{
            width: 100% !important;
            margin-bottom: 0.4rem;
        }}
        div[data-testid="stPopover"] > button {{
            width: 36px !important;
            height: 36px !important;
        }}
    }}
    </style>
    """).strip()
    st.html(css)


def render_page_header(title_key: str, info_key: str = "") -> None:
    """Page title + a collapsed 'About this page' note. Theme switch and the guided tour live in the global
    floating control (ui/shell.py) - one place, no page reruns."""
    l = lang()
    st.header(t(title_key, l))
    if info_key:
        with st.expander("ℹ️ " + t("about_page", l), expanded=False):
            st.write(t(info_key, l))


def banner() -> None:
    l = lang()
    if multiuser():
        st.caption("🔒 " + t("multiuser_note", l))
    st.warning(t("demo_banner", l), icon="🧪")
    prov = llm.get_provider()
    if prov:
        st.info(t("ai_mode_llm", l, provider=prov), icon="🤖")
    else:
        st.info(t("ai_mode_demo", l), icon="⚙️")


def completeness(p: dict) -> tuple[int, int]:
    known = sum(1 for v in p["fields"].values() if v["status"] == "known")
    return known, len(p["fields"])


def nba_text(nba: dict, l: str) -> str:
    """Render a core.insights.next_best_action() dict in the user's language."""
    from core.catalogue import L, get_scheme
    from core.i18n import field_label
    k = nba["kind"]
    if k == "overdue":
        return t("nba_overdue", l, title=nba["title"])
    if k == "answer_field":
        names = ", ".join(L(get_scheme(s)["name"], l).split("(")[-1].strip(")") for s in nba["schemes"])
        return t("nba_answer_field", l, field=field_label(nba["field"], l), n=nba["n"], schemes=names)
    if k == "upload_docs":
        return t("nba_upload_docs", l, docs=", ".join(L(d, l) for d in nba["docs"]), scheme=L(get_scheme(nba["scheme"])["name"], l))
    if k == "prepare":
        return t("nba_prepare", l, scheme=L(get_scheme(nba["scheme"])["name"], l))
    return t("nba_" + k, l)


def render_stepper(active_stage: int = 1) -> None:
    """Render the 5-Stage Methodology Stepper natively using Streamlit containers (no raw HTML code leaks)."""
    l = lang()
    stages = [
        (1, t("stage_1_name", l), t("stage_1_desc", l)),
        (2, t("stage_2_name", l), t("stage_2_desc", l)),
        (3, t("stage_3_name", l), t("stage_3_desc", l)),
        (4, t("stage_4_name", l), t("stage_4_desc", l)),
        (5, t("stage_5_name", l), t("stage_5_desc", l)),
    ]
    cols = st.columns(5)
    for idx, (num, name, desc) in enumerate(stages):
        with cols[idx]:
            is_active = (num == active_stage)
            with st.container(border=True):
                st.caption(f":{'green' if is_active else 'grey'}[STAGE {num}]")
                st.markdown(f"**{name}**")
                st.caption(desc)


def render_agent_inspector() -> None:
    """Render the 6 Specialized AI Agents inspector card natively from Slide 5."""
    l = lang()
    agents = [
        (t("agent_doc_name", l), t("agent_doc_desc", l), t("status_active", l)),
        (t("agent_retrieval_name", l), t("agent_retrieval_desc", l), t("status_active", l)),
        (t("agent_elig_name", l), t("agent_elig_desc", l), t("status_active", l)),
        (t("agent_form_name", l), t("agent_form_desc", l), t("status_active", l)),
        (t("agent_deadline_name", l), t("agent_deadline_desc", l), t("status_active", l)),
        (t("agent_monitor_name", l), t("agent_monitor_desc", l), t("status_active", l)),
    ]
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"#### 🤖 {t('agent_inspector_title', l)}")
        with col2:
            st.caption(f":green[● {len(agents)} " + t("agents_modules", l) + "]")

        cols = st.columns(3)
        for idx, (aname, adesc, astatus) in enumerate(agents):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"**{aname}**")
                    st.caption(f":blue[{astatus}] — {adesc}")
