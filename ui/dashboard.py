from datetime import date, timedelta

import streamlit as st

from core import db, insights, tasks
from core import profile as P
from core.catalogue import list_schemes
from core.i18n import t
from services import monitoring
from services.alerts import build_alerts, whatsapp_preview
from ui.common import (apply_custom_styles, banner, completeness, get_profile,
                       lang, nba_text, render_agent_inspector, render_stepper,
                       save_profile)


def render() -> None:
    l = lang()
    apply_custom_styles()

    # Header with GovTech dignity and team badges
    st.markdown(f"""
        <div style="margin-bottom: 14px;">
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px;">
                <span class="badge-pill badge-neutral">TEJAS-066</span>
                <span class="badge-pill badge-neutral">Temenos CSR & SASTRA</span>
                <span class="badge-pill badge-verified">SDG 9.3: Inclusive Industrial Growth</span>
            </div>
            <h1 style="font-size: 2.1rem; font-weight: 700; color: #0F172A; margin: 0; padding: 0;">
                {t('app_title', l)}
            </h1>
            <p style="font-size: 1.05rem; color: #475569; margin-top: 4px;">
                {t('tagline', l)}
            </p>
        </div>
    """, unsafe_allow_html=True)

    banner()

    # 5-Stage Stepper
    render_stepper(active_stage=1)

    p = get_profile()
    is_demo = p.get("is_demo", False)

    # Lakshmi's Journey Walkthrough Card (Direct Hackathon Narrative)
    st.markdown(f"""
        <div class="gov-card" style="border-left: 4px solid #0B6E4F;">
            <div class="gov-card-header">
                <span>🌟 {t('lakshmi_tour_title', l)}</span>
                {f'<span class="badge-pill badge-verified">{t("lakshmi_active_badge", l)}</span>' if is_demo else ''}
            </div>
            <div class="gov-card-sub" style="margin-bottom: 12px;">
                {t('lakshmi_tour_desc', l)}
            </div>
        </div>
    """, unsafe_allow_html=True)

    b1, b2, _ = st.columns([3, 2, 5])
    if b1.button(t("lakshmi_tour_btn", l), type="primary", key="btn_load_demo"):
        save_profile(P.load_demo_profile())
        st.success(t("demo_loaded", l))
        st.rerun()
    if b2.button(t("btn_reset", l), key="btn_reset"):
        db.reset_all()
        st.session_state.pop("profile", None)
        st.session_state.pop("chat", None)
        st.success(t("reset_done", l))
        st.rerun()

    st.write("")

    # High-level Metrics Row
    known, total = completeness(p)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("m_profile", l), f"{known}/{total}")
    c2.metric(t("m_docs", l), len(db.confirmed_doc_types()))
    c3.metric(t("m_schemes", l), len(list_schemes()))
    c4.metric(t("m_tasks", l), len(tasks.list_tasks(include_done=False)))

    # Next Best Action (Deterministic Information Gain)
    nba = insights.next_best_action(p, db.confirmed_doc_types(), tasks.list_tasks())
    st.markdown(f"""
        <div class="gov-card" style="background: #F8FAFC; border-color: #CBD5E1;">
            <div class="gov-card-header">
                <span>🎯 {t('nba_head', l)}</span>
                <span class="badge-pill badge-action">Information Gain</span>
            </div>
            <div style="font-size: 0.95rem; font-weight: 500; color: #1E293B; margin-top: 4px;">
                {nba_text(nba, l)}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Two-Column Action Center: Alerts & Deadlines
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader(t("al_head", l))
        alerts = build_alerts(p, db.confirmed_doc_types(), db.list_documents(), tasks.list_tasks(),
                              monitoring.notifiable_items(), l)
        if not alerts:
            st.info(t("al_none", l))
        icon = {"action": "🔴", "warn": "🟠", "info": "🔵"}
        for a in alerts:
            ac1, ac2 = st.columns([5, 2])
            ac1.markdown(f"{icon[a.severity]} {a.text}")
            with ac2.popover(t("al_preview_btn", l)):
                st.code(whatsapp_preview(a, l), language=None)

    with col_right:
        st.subheader(t("dl_head", l))
        soon = [x for x in tasks.list_tasks(include_done=False) if x["due_date"] and date.fromisoformat(x["due_date"]) <= date.today() + timedelta(days=14)]
        if not soon:
            st.info(t("dl_none", l))
        for x in soon:
            st.markdown(f"- {'🔴' if tasks.is_overdue(x) else '🕑'} **{x['due_date']}** — {x['title']}")

    st.write("")
    # Specialized Multi-Agent Architecture (Round 2 Slide 5)
    render_agent_inspector()

    # Journey Steps
    st.write("")
    with st.expander(f"📋 {t('journey_head', l)}", expanded=False):
        for i in range(1, 7):
            st.markdown(f"- {t(f'step_{i}', l)}")
