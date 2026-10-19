from datetime import date, timedelta

import streamlit as st

from core import db, insights, tasks
from core import profile as P
from core.catalogue import list_schemes
from core.i18n import t
from services import monitoring
from services.alerts import build_alerts, whatsapp_preview
from ui.common import banner, completeness, get_profile, lang, nba_text, save_profile


def render() -> None:
    l = lang()
    st.title(t("app_title", l))
    st.caption(t("tagline", l))
    banner()
    st.write(t("dash_intro", l))

    p = get_profile()
    known, total = completeness(p)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("m_profile", l), f"{known}/{total}")
    c2.metric(t("m_docs", l), len(db.confirmed_doc_types()))
    c3.metric(t("m_schemes", l), len(list_schemes()))
    c4.metric(t("m_tasks", l), len(tasks.list_tasks(include_done=False)))

    # ---- next best action (information-gain driven, deterministic)
    nba = insights.next_best_action(p, db.confirmed_doc_types(), tasks.list_tasks())
    st.success(f"**{t('nba_head', l)}**  \n{nba_text(nba, l)}", icon="🎯")

    # ---- alerts + deadlines (the 'Lakshmi sees her next steps and deadlines' story)
    alerts = build_alerts(p, db.confirmed_doc_types(), db.list_documents(), tasks.list_tasks(),
                          monitoring.notifiable_items(), l)
    st.subheader(t("al_head", l))
    if not alerts:
        st.write(t("al_none", l))
    icon = {"action": "🔴", "warn": "🟠", "info": "🔵"}
    for i, a in enumerate(alerts):
        c1, c2 = st.columns([5, 2])
        c1.markdown(f"{icon[a.severity]} {a.text}")
        with c2.popover(t("al_preview_btn", l)):
            st.code(whatsapp_preview(a, l), language=None)

    st.subheader(t("dl_head", l))
    soon = [x for x in tasks.list_tasks(include_done=False) if x["due_date"] and date.fromisoformat(x["due_date"]) <= date.today() + timedelta(days=14)]
    if not soon:
        st.write(t("dl_none", l))
    for x in soon:
        st.markdown(f"- {'🔴' if tasks.is_overdue(x) else '🕑'} **{x['due_date']}** — {x['title']}")

    st.subheader(t("journey_head", l))
    for i in range(1, 7):
        st.markdown(f"- {t(f'step_{i}', l)}")

    b1, b2 = st.columns(2)
    if b1.button(t("btn_load_demo", l), type="primary", key="btn_load_demo"):
        save_profile(P.load_demo_profile())
        st.success(t("demo_loaded", l))
        st.rerun()
    if b2.button(t("btn_reset", l), key="btn_reset"):
        db.reset_all()
        st.session_state.pop("profile", None)
        st.session_state.pop("chat", None)
        st.success(t("reset_done", l))
        st.rerun()
