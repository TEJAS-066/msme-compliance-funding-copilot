import os

import streamlit as st

from core import db
from core import profile as P
from core import tasks as T
from core.i18n import t
from services import notifications as N
from services.whatsapp import handle_message
from ui.common import get_profile, lang


def render() -> None:
    l = lang()
    st.header(t("nav_channel", l))

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
    for m in hist:
        with st.chat_message(m["role"], avatar="🟢" if m["role"] == "assistant" else None):
            st.text(m["text"])
    q = st.chat_input(t("ch_sim_ph", l), key="wa_input")
    if q:
        hist.append({"role": "user", "text": q})
        hist.append({"role": "assistant", "text": handle_message(q, get_profile(), db.confirmed_doc_types())})
        st.rerun()
