import os
from datetime import date, timedelta

import streamlit as st

from core import db, documents as D, insights, tasks
from core import profile as P
from core.catalogue import list_schemes
from core.i18n import t
from services import monitoring
from services.alerts import build_alerts
from ui.common import banner, completeness, get_profile, lang, nba_text, render_page_header, save_profile


def render() -> None:
    l = lang()

    # Clean, Professional Portal Header
    render_page_header("app_title", "pinfo_dashboard")
    st.markdown(f"*{t('tagline', l)}*")

    banner()

    p = get_profile()
    is_demo = p.get("is_demo", False)
    confirmed_docs = db.confirmed_doc_types()

    # --- 1. Quick Onboarding / Sample Loader ---
    with st.container(border=True):
        c_left, c_right = st.columns([3, 1], vertical_alignment="center")
        with c_left:
            st.markdown("### 🏢 Business Digital Twin & Document Ingestion")
            if is_demo:
                st.success("Active Profile: Lakshmi Garments (Sample Micro-Textile Enterprise, Tiruppur)")
            else:
                st.caption("Upload your Udyam Certificate or GSTIN to automatically populate your business digital twin, or test with sample data.")
        with c_right:
            b1, b2 = st.columns(2)
            if b1.button("🧪 Sample", key="btn_load_demo", help="Load synthetic sample profile"):
                save_profile(P.load_demo_profile())
                st.rerun()
            if b2.button("↺ Reset", key="btn_reset", help="Reset all data"):
                db.reset_all()
                st.session_state.pop("profile", None)
                st.session_state.pop("chat", None)
                st.rerun()

    st.write("")

    # --- 2. Key Business Metrics Row ---
    cls, basis = P.enterprise_class(p)
    class_label = cls.upper() if cls else "UNKNOWN"
    known, total = completeness(p)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Enterprise Class", class_label, help="Statutory class under Ministry of MSME Notification S.O. 1364(E)")
    with m2:
        st.metric(t("m_docs", l), f"{len(confirmed_docs)} Verified", help="Documents verified with Luhn Mod-36 checksum")
    with m3:
        st.metric(t("m_schemes", l), f"{len(list_schemes())} Monitored", help="Central & State credit/subsidy schemes")
    with m4:
        st.metric(t("m_profile", l), f"{known}/{total}", help="Data completeness for credit underwriting")

    st.write("")

    # --- 3. The 3-Step Core Pipeline Navigator ---
    st.markdown("### 🚀 Core Funding & Compliance Pipeline")
    p1, p2, p3 = st.columns(3)

    with p1:
        with st.container(border=True):
            st.markdown("#### 1. 📁 Ingest Documents")
            st.caption("Upload Udyam, GST, or Tax PDF/Image. Runs Luhn Mod-36 checksum & flags clerical errors.")
            st.markdown(f"**Verified**: `{len(confirmed_docs)}` documents")
            st.info("Tip: Go to **Documents** to upload and verify certificates.")

    with p2:
        with st.container(border=True):
            st.markdown("#### 2. 💰 Scheme Matching")
            st.caption("Evaluates MUDRA (up to ₹20L) & CGTMSE (up to ₹5 Cr guarantee) with zero hallucination.")
            st.markdown("**Status**: MUDRA Tarun & CGTMSE Eligible")
            st.info("Tip: Go to **Schemes** to inspect eligibility & tipping points.")

    with p3:
        with st.container(border=True):
            st.markdown("#### 3. 📄 Bank Loan Dossier")
            st.caption("Auto-fills 11-field standard bank loan application worksheet and generates official PDF pack.")
            st.markdown("**Output**: Ready for bank branch credit officer")
            st.info("Tip: Go to **Forms** to download your PDF dossier.")

    st.write("")

    # --- 4. Next Best Action ---
    nba = insights.next_best_action(p, db.confirmed_doc_types(), tasks.list_tasks())
    with st.container(border=True, key="tour_nba"):
        st.markdown(f"**🎯 {t('nba_head', l)}**")
        st.info(nba_text(nba, l))

    # --- 5. Statutory Compliance & Deadlines Center ---
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
                st.markdown(f"{icon[a.severity]} {a.text}")

    with col_right:
        with st.container(border=True):
            st.subheader(t("dl_head", l))
            soon = [x for x in tasks.list_tasks(include_done=False) if x["due_date"] and date.fromisoformat(x["due_date"]) <= date.today() + timedelta(days=14)]
            if not soon:
                st.caption(t("dl_none", l))
            for x in soon:
                st.markdown(f"- {'🔴' if tasks.is_overdue(x) else '🕑'} **{x['due_date']}** — {x['title']}")
