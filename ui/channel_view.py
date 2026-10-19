import os

import streamlit as st

from core import db
from core import profile as P
from core import tasks as T
from core.i18n import t
from services import notifications as N
from services.whatsapp import handle_message
from ui import voice
from ui.common import get_profile, lang, render_page_header


def render() -> None:
    l = lang()
    render_page_header("nav_channel", "pinfo_channel")

    # ---- 1. honest connection status + real send attempt
    st.subheader(t("ch_status_head", l))
    configured = N.whatsapp_configured()
    (st.info if configured else st.warning)(t("ch_twilio_on" if configured else "ch_twilio_off", l))
    st.markdown(f"**{t('ch_send_head', l)}**")
    open_tasks = T.list_tasks(include_done=False)
    if not open_tasks:
        st.caption(t("ch_need_task", l))
    else:
        tk = st.selectbox(" ", open_tasks, key="ch_task", format_func=lambda x: x["title"], label_visibility="collapsed")
        st.code(N.preview_reminder(tk, l), language=None)
        phone = st.text_input(t("ch_phone", l), key="ch_phone")
        if st.button(t("ch_send_btn", l), key="ch_send"):
            r = N.send_whatsapp(phone.strip(), N.preview_reminder(tk, l))
            (st.success if r.status == "SENT" else st.error if r.status == "FAILED" else st.warning)(
                t("ch_result", l, status=r.status, detail=r.detail))

    # ---- 2. simulator (same code path as the real webhook)
    st.divider()
    st.warning(t("ch_sim_banner", l), icon="📱")

    hist = st.session_state.setdefault("wa_chat", [])

    # Quick Inquiries (1-Click Demo for Jury & Reviewers)
    with st.container(border=True):
        st.caption(t("ch_quick_prompts", l))
        c1, c2, c3, c4 = st.columns(4)
        chip_query = None
        with c1:
            if st.button(f"🏛️ {t('ch_chip_elig', l)}", key="chip_elig", use_container_width=True):
                chip_query = t("ch_chip_elig", l)
        with c2:
            if st.button(f"📑 {t('ch_chip_docs', l)}", key="chip_docs", use_container_width=True):
                chip_query = t("ch_chip_docs", l)
        with c3:
            if st.button(f"💰 {t('ch_chip_subsidy', l)}", key="chip_subsidy", use_container_width=True):
                chip_query = t("ch_chip_subsidy", l)
        with c4:
            if st.button(f"🗑️ {t('ch_clear_btn', l)}", key="chip_clear", use_container_width=True):
                st.session_state["wa_chat"] = []
                st.rerun()

        if chip_query:
            hist.append({"role": "user", "text": chip_query})
            hist.append({"role": "assistant", "text": handle_message(chip_query, get_profile(), db.confirmed_doc_types(), lang=l)})
            st.rerun()

    for m in hist:
        with st.chat_message(m["role"], avatar="🟢" if m["role"] == "assistant" else None):
            st.text(m["text"])

    voice.render(l)

    q = st.chat_input(t("ch_sim_ph", l), key="wa_input")
    if q:
        hist.append({"role": "user", "text": q})
        hist.append({"role": "assistant", "text": handle_message(q, get_profile(), db.confirmed_doc_types(), lang=l)})
        st.rerun()

