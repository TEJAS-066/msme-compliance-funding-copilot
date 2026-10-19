"""Shared UI helpers, GovTech human-crafted styling, and 5-stage stepper."""
from __future__ import annotations

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


def apply_custom_styles() -> None:
    """Inject clean, human-crafted GovTech & Fintech portal styling."""
    st.markdown("""
        <style>
        /* Base typography & color tone */
        .main .block-container {
            padding-top: 1.8rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }
        
        /* Card container */
        .gov-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 18px 22px;
            margin-bottom: 18px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        }
        .gov-card-header {
            font-size: 1.05rem;
            font-weight: 600;
            color: #0F172A;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .gov-card-sub {
            font-size: 0.85rem;
            color: #64748B;
            line-height: 1.4;
        }

        /* 5-Stage Stepper */
        .stepper-bar {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin: 12px 0 22px 0;
        }
        @media (max-width: 800px) {
            .stepper-bar {
                grid-template-columns: 1fr;
            }
        }
        .step-box {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 10px 12px;
            transition: border-color 0.2s ease;
        }
        .step-box.active {
            border: 1.5px solid #0B6E4F;
            background: #F0FDF4;
        }
        .step-num {
            font-size: 0.72rem;
            font-weight: 700;
            color: #0B6E4F;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .step-title {
            font-size: 0.88rem;
            font-weight: 600;
            color: #0F172A;
            margin-top: 2px;
        }
        .step-desc {
            font-size: 0.74rem;
            color: #64748B;
            margin-top: 2px;
            line-height: 1.25;
        }

        /* Badge pills */
        .badge-pill {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 0.72rem;
            font-weight: 600;
            line-height: 1.4;
        }
        .badge-verified {
            background-color: #DCFCE7;
            color: #166534;
            border: 1px solid #BBF7D0;
        }
        .badge-action {
            background-color: #FEF3C7;
            color: #92400E;
            border: 1px solid #FDE68A;
        }
        .badge-neutral {
            background-color: #F1F5F9;
            color: #334155;
            border: 1px solid #E2E8F0;
        }
        .badge-agent {
            background-color: #EFF6FF;
            color: #1E40AF;
            border: 1px solid #BFDBFE;
        }

        /* Agent Inspector Grid */
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
            gap: 12px;
            margin-top: 10px;
        }
        .agent-box {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 12px 14px;
        }
        .agent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .agent-name {
            font-size: 0.86rem;
            font-weight: 600;
            color: #1E293B;
        }
        .agent-desc {
            font-size: 0.76rem;
            color: #64748B;
            margin-top: 4px;
            line-height: 1.3;
        }
        </style>
    """, unsafe_allow_html=True)


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
    """Render the 5-Stage Methodology Stepper (Understand -> Profile -> Match -> Prepare -> Track)."""
    l = lang()
    stages = [
        (1, t("stage_1_name", l), t("stage_1_desc", l)),
        (2, t("stage_2_name", l), t("stage_2_desc", l)),
        (3, t("stage_3_name", l), t("stage_3_desc", l)),
        (4, t("stage_4_name", l), t("stage_4_desc", l)),
        (5, t("stage_5_name", l), t("stage_5_desc", l)),
    ]
    html = ['<div class="stepper-bar">']
    for num, name, desc in stages:
        active_cls = " active" if num == active_stage else ""
        html.append(f"""
            <div class="step-box{active_cls}">
                <div class="step-num">Stage {num}</div>
                <div class="step-title">{name}</div>
                <div class="step-desc">{desc}</div>
            </div>
        """)
    html.append('</div>')
    st.markdown("".join(html), unsafe_allow_html=True)


def render_agent_inspector() -> None:
    """Render the 6 Specialized AI Agents inspector card from Slide 5."""
    l = lang()
    agents = [
        (t("agent_doc_name", l), t("agent_doc_desc", l), t("status_active", l)),
        (t("agent_retrieval_name", l), t("agent_retrieval_desc", l), t("status_active", l)),
        (t("agent_elig_name", l), t("agent_elig_desc", l), t("status_active", l)),
        (t("agent_form_name", l), t("agent_form_desc", l), t("status_active", l)),
        (t("agent_deadline_name", l), t("agent_deadline_desc", l), t("status_active", l)),
        (t("agent_monitor_name", l), t("agent_monitor_desc", l), t("status_active", l)),
    ]
    st.markdown(f"""
        <div class="gov-card">
            <div class="gov-card-header">
                <span>🤖 {t('agent_inspector_title', l)}</span>
                <span class="badge-pill badge-verified">6 Agents Operational</span>
            </div>
            <div class="agent-grid">
    """, unsafe_allow_html=True)

    agent_cols = st.columns(3)
    for idx, (aname, adesc, astatus) in enumerate(agents):
        with agent_cols[idx % 3]:
            st.markdown(f"""
                <div class="agent-box">
                    <div class="agent-header">
                        <span class="agent-name">{aname}</span>
                        <span class="badge-pill badge-agent">{astatus}</span>
                    </div>
                    <div class="agent-desc">{adesc}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
