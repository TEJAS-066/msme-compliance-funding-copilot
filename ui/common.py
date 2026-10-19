"""Shared UI helpers, GovTech clean styling, and 5-stage stepper."""
from __future__ import annotations

import textwrap
import streamlit as st

from core import db
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


def apply_custom_styles(theme: str | None = None) -> None:
    """Inject clean, human-crafted GovTech & Fintech portal styling with Light / Dark theme support."""
    theme = theme or st.session_state.get("theme", "light")
    is_dark = "dark" in str(theme).lower() or "🌙" in str(theme)

    if is_dark:
        bg_main = "#0B1120"
        card_bg = "#1E293B"
        border_col = "#334155"
        text_primary = "#F8FAFC"
        text_secondary = "#94A3B8"
        metric_bg = "#1E293B"
    else:
        bg_main = "#F8FAFC"
        card_bg = "#FFFFFF"
        border_col = "#E2E8F0"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        metric_bg = "#FFFFFF"

    css = textwrap.dedent(f"""
    <style>
    /* Theme root styling */
    .stApp {{
        background-color: {bg_main} !important;
        color: {text_primary} !important;
    }}

    /* Base typography & layout padding */
    .main .block-container {{
        padding-top: 1.5rem;
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
        color: {text_primary} !important;
    }}
    div[data-testid="stMetricLabel"] {{
        font-weight: 500;
        color: {text_secondary} !important;
    }}

    /* Container card styling */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {{
        background-color: {card_bg} !important;
        border-color: {border_col} !important;
    }}

    /* Clean buttons */
    button[kind="primary"] {{
        background-color: #0B6E4F !important;
        border-color: #0B6E4F !important;
        font-weight: 600;
    }}
    button[kind="primary"]:hover {{
        background-color: #085039 !important;
        border-color: #085039 !important;
    }}

    /* Mobile Responsive Optimizations (< 768px) */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-top: 1rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            padding-bottom: 2rem !important;
        }}
        div[data-testid="stHorizontalBlock"] {{
            flex-wrap: wrap !important;
            gap: 0.6rem !important;
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
    }}
    </style>
    """).strip()
    st.html(css)


def render_page_header(title_key: str, info_key: str) -> None:
    """Standardized page header with title and interactive Page Guide popover."""
    l = lang()
    c_title, c_info = st.columns([5, 1], vertical_alignment="center")
    c_title.header(t(title_key, l))
    with c_info:
        with st.popover("ℹ️ " + t("btn_page_info", l), use_container_width=True):
            st.markdown(f"#### ℹ️ {t(title_key, l)}")
            st.info(t(info_key, l))
            st.caption("GovTech AI • " + t("btn_page_info", l))


@st.dialog("🏛️ MSME Copilot — Quick Guided Tour")
def show_onboarding_tour() -> None:
    """Interactive multi-step onboarding tour dialog for new vendors and judges."""
    l = lang()
    step = st.session_state.get("tour_step", 1)

    if step == 1:
        st.markdown(f"#### 🏛️ {t('tour_step_1_title', l)}")
        st.write(t("tour_step_1_desc", l))
        st.info("💡 **Rules decide • AI explains • The owner acts**")
    elif step == 2:
        st.markdown(f"#### 🧭 {t('tour_step_2_title', l)}")
        st.write(t("tour_step_2_desc", l))
        st.caption("1. Understand ➔ 2. Profile ➔ 3. Match ➔ 4. Prepare ➔ 5. Track")
    elif step == 3:
        st.markdown(f"#### 📑 {t('tour_step_3_title', l)}")
        st.write(t("tour_step_3_desc", l))
        st.caption("Udyam • GSTIN Luhn Mod-36 • Anti-Hallucination Triad")
    elif step == 4:
        st.markdown(f"#### 📄 {t('tour_step_4_title', l)}")
        st.write(t("tour_step_4_desc", l))
        st.success("📄 ReportLab PDF Bank Dossier • 📱 Multilingual WhatsApp Simulator")

    st.write("---")
    c_prev, c_ind, c_next = st.columns([1.2, 1.6, 1.2], vertical_alignment="center")
    if step > 1:
        if c_prev.button(t("tour_btn_prev", l), key=f"t_prev_{step}", use_container_width=True):
            st.session_state["tour_step"] = step - 1
            st.rerun()
    else:
        c_prev.write("")

    c_ind.markdown(f"<div style='text-align: center; font-weight: 600; color: #64748B;'>Step {step} of 4</div>", unsafe_allow_html=True)

    if step < 4:
        if c_next.button(t("tour_btn_next", l), key=f"t_next_{step}", type="primary", use_container_width=True):
            st.session_state["tour_step"] = step + 1
            st.rerun()
    else:
        if c_next.button(t("tour_btn_close", l), key="t_close", type="primary", use_container_width=True):
            st.session_state["tour_open"] = False
            st.session_state["tour_step"] = 1
            st.rerun()



def banner() -> None:
    l = lang()
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
            st.caption(":green[● 6 Agents Active]")

        cols = st.columns(3)
        for idx, (aname, adesc, astatus) in enumerate(agents):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"**{aname}**")
                    st.caption(f":blue[{astatus}] — {adesc}")
