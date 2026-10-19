import streamlit as st

from core.catalogue import L, get_scheme
from core.i18n import t
from services import monitoring as M
from ui.common import lang


def render() -> None:
    l = lang()
    st.header(t("nav_admin", l))
    st.info(t("adm_scope", l))

    st.subheader(t("adm_fresh_head", l))
    for r in M.stale_schemes():
        name = L(get_scheme(r["scheme_id"])["name"], l)
        st.markdown(f"- **{name}** — {r['last_verified']} ({r['age_days']} d) — "
                    f"{'🔴 ' + t('adm_stale', l) if r['stale'] else '🟢 ' + t('adm_ok', l)} · `{r['review_status']}`")

    st.subheader(t("adm_queue_head", l))
    for it in M.load_queue():
        box = st.container(border=True)
        box.markdown(f"**{it['title']}**  \n`{it['kind']}` · {t('adm_status', l)}: **{it['status']}**")
        box.caption(it["detail"])
        if it["status"] == "pending":
            a, b = box.columns(2)
            if a.button(t("btn_approve", l), key=f"ap_{it['id']}"):
                M.decide(it["id"], "approved"); st.rerun()
            if b.button(t("btn_reject", l), key=f"rj_{it['id']}"):
                M.decide(it["id"], "rejected"); st.rerun()
    st.markdown(f"**{t('adm_notify_head', l)}**")
    ok = M.notifiable_items()
    if not ok:
        st.write(t("adm_no_notify", l))
    for it in ok:
        st.code(f"[PREVIEW ONLY] {it['title']}", language=None)

    st.subheader(t("kpi_head", l))
    st.caption(t("kpi_note", l))
    try:
        from evaluation.run_eval import run
        k = run()
        c1, c2 = st.columns(2)
        c1.metric(t("kpi_elig", l), f"{k['eligibility']['accuracy']:.0%}", t("kpi_cases", l, ok=k['eligibility']['correct'], n=k['eligibility']['total']))
        c2.metric(t("kpi_extract", l), f"{k['extraction']['accuracy']:.0%}", t("kpi_cases", l, ok=k['extraction']['correct'], n=k['extraction']['total']))
    except Exception as e:  # keep the admin page alive even if eval files are missing
        st.error(f"KPI harness unavailable: {type(e).__name__}")
