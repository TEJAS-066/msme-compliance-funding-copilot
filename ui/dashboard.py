from datetime import date, timedelta

import streamlit as st

from core import db, insights, tasks
from core import profile as P
from core.catalogue import list_schemes
from core.i18n import t
from services import monitoring
from services.alerts import build_alerts, whatsapp_preview
from ui.common import (banner, completeness, get_profile,
                       lang, nba_text, render_agent_inspector, render_stepper,
                       save_profile)


def render() -> None:
    l = lang()

    # Executive Header
    st.caption("TEJAS-066 • Temenos CSR & SASTRA • SDG 9.3: Inclusive Industrial Growth")
    st.title(f"🏛️ {t('app_title', l)}")
    st.markdown(f"*{t('tagline', l)}*")

    banner()

    # 5-Stage Stepper (Native responsive cards)
    render_stepper(active_stage=1)

    p = get_profile()
    is_demo = p.get("is_demo", False)

    # Lakshmi's Journey Walkthrough Card (Direct Hackathon Narrative)
    with st.container(border=True):
        st.markdown(f"### 🌟 {t('lakshmi_tour_title', l)}")
        if is_demo:
            st.success(t("lakshmi_active_badge", l))
        st.write(t("lakshmi_tour_desc", l))

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
    with st.container(border=True):
        col_nba_1, col_nba_2 = st.columns([4, 1])
        with col_nba_1:
            st.markdown(f"**🎯 {t('nba_head', l)}**")
        with col_nba_2:
            st.caption(":orange[Information Gain]")
        st.info(nba_text(nba, l))

    # Two-Column Action Center: Alerts & Deadlines
    col_left, col_right = st.columns(2)

    with col_left:
        with st.container(border=True):
            st.subheader(t("al_head", l))
            alerts = build_alerts(p, db.confirmed_doc_types(), db.list_documents(), tasks.list_tasks(),
                                  monitoring.notifiable_items(), l)
            if not alerts:
                st.caption(t("al_none", l))
            icon = {"action": "🔴", "warn": "🟠", "info": "🔵"}
            for a in alerts:
                ac1, ac2 = st.columns([5, 2])
                ac1.markdown(f"{icon[a.severity]} {a.text}")
                with ac2.popover(t("al_preview_btn", l)):
                    st.code(whatsapp_preview(a, l), language=None)

    with col_right:
        with st.container(border=True):
            st.subheader(t("dl_head", l))
            soon = [x for x in tasks.list_tasks(include_done=False) if x["due_date"] and date.fromisoformat(x["due_date"]) <= date.today() + timedelta(days=14)]
            if not soon:
                st.caption(t("dl_none", l))
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
