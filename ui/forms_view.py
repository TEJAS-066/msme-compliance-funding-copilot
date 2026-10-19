"""Form assistance = a REVIEWABLE PREPARATION WORKSHEET, not the official bank form.
Organized into a clean, human-crafted GovTech pre-application dossier.
"""
from __future__ import annotations

import streamlit as st

from core import db, forms as F
from core import profile as P
from core.catalogue import L, get_catalogue, get_scheme, list_schemes
from core.i18n import t
from services.report import generate_pdf_dossier, readiness_report
from ui.common import get_profile, lang, render_page_header


def render() -> None:
    l = lang()
    cat = get_catalogue()
    render_page_header("nav_forms", "pinfo_forms")
    st.info(t("frm_intro", l))

    ids = [s["id"] for s in list_schemes(cat)]
    sid = st.selectbox(t("sch_pick", l), ids, key="frm_pick", format_func=lambda i: L(get_scheme(i, cat)["name"], l))
    p = get_profile()
    rows = F.prepare_worksheet(p, l)
    missing = sum(r["missing"] for r in rows)
    total = len(rows)
    ready_pct = int(100 * (total - missing) / total) if total > 0 else 0

    # Metric summary row
    m1, m2, m3 = st.columns(3)
    m1.metric("Pre-filled Fields", f"{total - missing} / {total}")
    m2.metric("Missing Fields", f"{missing}", delta=f"-{missing}" if missing else "Ready", delta_color="inverse")
    m3.metric("Application Readiness", f"{ready_pct}%")

    if missing:
        st.warning(t("frm_missing_count", l, n=missing))

    # Form fields in clean 2-column layout with bordered containers
    col1, col2 = st.columns(2)
    half = (len(rows) + 1) // 2
    for i, r in enumerate(rows):
        target_col = col1 if i < half else col2
        with target_col:
            with st.container(border=True):
                icon = "⚠️" if r["missing"] else "✅"
                val = t("frm_missing", l) if r["missing"] else (
                    P.fmt_inr(r["value"]) if P.FIELDS[r["field"]]["kind"] == "int" and r["field"] != "employees" else str(r["value"])
                )
                st.markdown(f"**{icon} {r['label']}**")
                st.markdown(f"### {val}" if not r["missing"] else f"*{val}*")
                st.caption(r["hint"])

    st.write("---")
    st.caption("Review every detail carefully before taking this worksheet to your bank or CSC. Nothing is submitted online.")

    # Action buttons in side-by-side columns
    b1, b2, b3 = st.columns(3)
    b1.download_button(
        label=f"📄 {t('btn_download', l)}",
        data=F.worksheet_text(p, L(get_scheme(sid, cat)["name"], l), l),
        file_name=f"worksheet_{sid}.txt",
        key="dl_ws",
        use_container_width=True,
    )
    b2.download_button(
        label=f"📋 {t('rep_btn', l)}",
        data=readiness_report(p, db.confirmed_doc_types(), l),
        file_name="readiness_report.txt",
        key="dl_report",
        use_container_width=True
    )
    b3.download_button(
        label=f"🏛️ {t('btn_download_pdf', l)}",
        data=generate_pdf_dossier(p, db.confirmed_doc_types(), sid, cat=cat),
        file_name=f"bank_dossier_{sid}.pdf",
        mime="application/pdf",
        key="dl_pdf",
        type="primary",
        use_container_width=True
    )

