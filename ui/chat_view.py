import streamlit as st

from core import db
from core.i18n import t
from services.copilot import answer
from ui import voice
from ui.common import banner, get_profile, lang


def render() -> None:
    l = lang()
    st.header(t("nav_copilot", l))
    banner()
    st.caption(t("chat_examples", l))
    with st.expander(t("v_head", l)):
        st.caption(t("v_privacy", l))
        voice.render(l)

    hist = st.session_state.setdefault("chat", [])
    for m in hist:
        with st.chat_message(m["role"]):
            st.markdown(m["text"])
            if m["role"] == "assistant":
                a = m["answer"]
                st.caption(f"{t('ans_mode', l)}: {a.mode}")
                if a.sources:
                    with st.expander(t("ans_sources", l)):
                        for s in a.sources:
                            st.markdown(f"- [{s['title']}]({s['url']}) — {t('src_' + s['tier'], l)}, {s['accessed']}")
                if a.trace:
                    with st.expander(t("tr_head", l)):
                        for step in a.trace:
                            st.markdown(f"**{step['agent']}** — {step['detail']}")
                if a.notes:
                    with st.expander(t("chat_notes", l)):
                        for n in a.notes:
                            st.write(n)

    q = st.chat_input(t("chat_ph", l), key="chat_input")
    if q:
        hist.append({"role": "user", "text": q})
        a = answer(q, l, get_profile(), db.confirmed_doc_types())
        hist.append({"role": "assistant", "text": a.text, "answer": a})
        st.rerun()
    if hist and st.button(t("chat_clear", l), key="chat_clear"):
        st.session_state["chat"] = []
        st.rerun()
