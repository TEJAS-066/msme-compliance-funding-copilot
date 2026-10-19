import streamlit as st

from core import db
from core.catalogue import L, get_catalogue, get_scheme, list_schemes
from core.checklist import build_checklist, summarize
from core.i18n import t
from ui.common import get_profile, lang


def render() -> None:
    l = lang()
    cat = get_catalogue()
    st.header(t("nav_checklist", l))
    ids = [s["id"] for s in list_schemes(cat)]
    sid = st.selectbox(t("sch_pick", l), ids, key="chk_pick", format_func=lambda i: L(get_scheme(i, cat)["name"], l))
    items = build_checklist(sid, get_profile(), db.confirmed_doc_types(), db.pending_doc_types(), cat)
    s = summarize(items)
    st.progress(s["confirmed"] / s["total"] if s["total"] else 0.0, text=t("chk_progress", l, done=s["confirmed"], total=s["total"]))
    icon = {"confirmed": "✅", "needs_review": "🟡", "missing": "⬜", "not_applicable": "➖"}

    for verified, head in ((True, "chk_verified_head"), (False, "chk_unverified_head")):
        group = [i for i in items if i["verified"] == verified]
        if not group:
            continue
        st.markdown(f"#### {t(head, l)}")
        for it in group:
            extra = f" {t('chk_applicability_unknown', l)}" if it["applicability_unknown"] else ""
            st.markdown(f"{icon[it['status']]} **{L(it['name'], l)}** — {t('doc_' + it['status'], l)}{extra}")
            st.caption(L(it["why"], l))
