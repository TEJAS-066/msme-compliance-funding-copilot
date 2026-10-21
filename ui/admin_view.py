import streamlit as st

from core import config
from core.catalogue import L, get_scheme
from core.i18n import t
from services import monitoring as M
from ui.common import admin_unlocked, lang, render_page_header


def render() -> None:
    l = lang()
    render_page_header("nav_admin", "pinfo_admin")
    if not admin_unlocked():
        pin = config.get("ADMIN_PIN")
        if not pin:
            st.warning(t("adm_locked", l))
            return
        entered = st.text_input(t("adm_pin", l), type="password", key="adm_pin_input")
        if entered:
            if entered == pin:
                st.session_state["admin_ok"] = True
                st.rerun()
            st.error(t("adm_pin_wrong", l))
        return

    # ---- 1. KPIs: ONLY numbers that are actually measured here, on small synthetic sets
    with st.container(border=True):
        st.subheader(t("kpi_head", l))
        st.caption(t("kpi_note", l))
        try:
            from evaluation.run_eval import run
            k = run()
            c1, c2 = st.columns(2)
            c1.metric(t("kpi_elig", l), f"{k['eligibility']['accuracy']:.0%}", t("kpi_cases", l, ok=k['eligibility']['correct'], n=k['eligibility']['total']))
            c2.metric(t("kpi_extract", l), f"{k['extraction']['accuracy']:.0%}", t("kpi_cases", l, ok=k['extraction']['correct'], n=k['extraction']['total']))
            if k["extraction"].get("skipped"):
                st.caption("OCR samples skipped (OCR not installed): " + ", ".join(k["extraction"]["skipped"]))
        except Exception as e:                 # never show a made-up number if measuring fails
            st.error(f"KPI harness could not run: {type(e).__name__}")

    # ---- 2. Catalogue freshness
    st.subheader(t("adm_fresh_head", l))
    for r in M.stale_schemes():
        name = L(get_scheme(r["scheme_id"])["name"], l)
        st.markdown(f"- **{name}** — {r['last_verified']} ({r['age_days']} d) — "
                    f"{'🔴 ' + t('adm_stale', l) if r['stale'] else '🟢 ' + t('adm_ok', l)} · `{r['review_status']}`")

    # ---- 3. Update queue (human approval before anyone is notified)
    st.subheader(t("adm_queue_head", l))
    st.info(t("adm_scope", l))
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

    # ---- 4. Notification preview
    st.markdown(f"**{t('adm_notify_head', l)}**")
    ok = M.notifiable_items()
    if not ok:
        st.write(t("adm_no_notify", l))
    for it in ok:
        st.code(f"[PREVIEW ONLY] {it['title']}", language=None)
