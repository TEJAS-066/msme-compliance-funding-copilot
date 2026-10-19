import streamlit as st

from core import forms as F
from core import profile as P
from core.catalogue import L, get_catalogue, get_scheme, list_schemes
from core.i18n import t
from core import db
from services.report import readiness_report
from ui.common import get_profile, lang


def render() -> None:
    l = lang()
    cat = get_catalogue()
    st.header(t("nav_forms", l))
    st.info(t("frm_intro", l))
    ids = [s["id"] for s in list_schemes(cat)]
    sid = st.selectbox(t("sch_pick", l), ids, key="frm_pick", format_func=lambda i: L(get_scheme(i, cat)["name"], l))
    p = get_profile()
    rows = F.prepare_worksheet(p, l)
    missing = sum(r["missing"] for r in rows)
    if missing:
        st.warning(t("frm_missing_count", l, n=missing))
    for r in rows:
        val = t("frm_missing", l) if r["missing"] else (P.fmt_inr(r["value"]) if P.FIELDS[r["field"]]["kind"] == "int" and r["field"] != "employees" else r["value"])
        st.markdown(f"{'⚠️' if r['missing'] else '✅'} **{r['label']}**: {val}")
        st.caption(r["hint"])
    st.download_button(t("btn_download", l), F.worksheet_text(p, L(get_scheme(sid, cat)["name"], l), l),
                       file_name=f"worksheet_{sid}.txt", key="dl_ws")
    st.download_button(t("rep_btn", l), readiness_report(p, db.confirmed_doc_types(), l), file_name="readiness_report.txt", key="dl_report")
