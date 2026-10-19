import os

import streamlit as st

from core import db, documents as D
from core import profile as P
from core.i18n import field_label, option_label, t
from ui.common import get_profile, lang, save_profile

SAMPLES = os.path.join(os.path.dirname(os.path.dirname(__file__)), "samples")


def _process(data: bytes, name: str) -> None:
    p = get_profile()
    res = D.extract_text(data, name)
    findings, dtype = [], "unknown"
    if res.extraction_status == "text_extracted":
        dtype = D.detect_doc_type(res.text)
        findings = [f.__dict__ for f in D.compare_with_profile(D.extract_fields(res.text), p)]
    db.add_document(name, dtype, res.upload_status, res.extraction_status, res.message, findings)


def render() -> None:
    l = lang()
    st.header(t("nav_documents", l))
    st.caption(t("docs_help", l))
    p = get_profile()

    up = st.file_uploader(t("docs_upload", l), type=["pdf", "txt", "png", "jpg", "jpeg"], key="uploader")
    if up is not None and st.session_state.get("last_upload") != (up.name, up.size):
        st.session_state["last_upload"] = (up.name, up.size)
        _process(up.getvalue(), up.name)

    samples = sorted(f for f in os.listdir(SAMPLES) if f.startswith("sample_")) if os.path.isdir(SAMPLES) else []
    if samples:
        c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
        pick = c1.selectbox(t("docs_samples", l), samples, key="sample_pick")
        if c2.button(t("btn_process_sample", l), key="btn_sample", type="primary", use_container_width=True):
            with open(os.path.join(SAMPLES, pick), "rb") as f:
                _process(f.read(), pick)

    st.caption(t("not_verified_note", l))
    st.subheader(t("docs_list_head", l))
    for d in db.list_documents():
        with st.expander(f"{d['filename']}  —  {t('state_upload', l)}: {t('up_' + d['upload_status'], l)} · "
                         f"{t('state_extraction', l)}: {t('ext_' + d['extraction_status'], l)} · "
                         f"{t('state_confirmation', l)}: {t('conf_' + d['confirmation'], l)}", expanded=d["confirmation"] == "pending" and bool(d["findings"])):
            if d["message"]:
                st.info(d["message"])
            fields = [f for f in d["findings"] if not f.get("advisory")]
            warns = [f for f in d["findings"] if f.get("advisory")]
            if warns:
                st.markdown(f"**{t('warn_head', l)}**")
                for w in warns:
                    st.warning(w["note"])
            if d["extraction_status"] == "text_extracted" and not fields:
                st.write(t("no_fields", l))
            if fields and d["confirmation"] == "pending":
                decisions = []
                for i, f in enumerate(fields):
                    cA, cB, cC = st.columns([3, 3, 2], vertical_alignment="center")
                    cA.markdown(f"**{field_label(f['field'], l)}**: `{f['proposed']}`  \n{t('q_' + f['match_quality'], l)}")
                    cur = f["current"]
                    cB.markdown(f"{t('fnd_' + f['kind'], l)}" + (f"  \n→ `{cur}`" if cur and f["kind"] == "mismatch" else ""))
                    if f["kind"] == "match":
                        choices = ["act_accept", "act_reject"]
                    elif f["kind"] == "mismatch":
                        choices = ["act_reject", "act_overwrite"]     # default = keep MY value
                    else:
                        choices = ["act_accept", "act_reject"]
                    sel = cC.selectbox(" ", choices, key=f"dec_{d['id']}_{i}", label_visibility="collapsed", format_func=lambda k: t(k, l))
                    decisions.append({"field": f["field"], "value": f["proposed"], "action": sel.replace("act_", "")})
                a, b = st.columns(2)
                if a.button(t("btn_apply", l), type="primary", key=f"apply_{d['id']}"):
                    newp = D.apply_decisions(get_profile(), decisions, d["filename"])
                    save_profile(newp)
                    db.set_document_confirmation(d["id"], "confirmed")
                    st.success(t("apply_ok", l))
                    st.rerun()
                if b.button(t("btn_reject_doc", l), key=f"rej_{d['id']}"):
                    db.set_document_confirmation(d["id"], "rejected")
                    st.rerun()
            elif d["extraction_status"] == "text_extracted" and d["confirmation"] == "pending" and not fields:
                if st.button(t("btn_reject_doc", l), key=f"rej2_{d['id']}"):
                    db.set_document_confirmation(d["id"], "rejected")
                    st.rerun()
