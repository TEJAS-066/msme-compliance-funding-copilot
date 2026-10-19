import streamlit as st

from core import eligibility as E
from core import insights
from core import profile as P
from core.catalogue import L, get_catalogue, get_scheme, get_source, list_schemes, unverified_backlog
from core.i18n import field_label, option_label, t
from ui.common import get_profile, lang, render_page_header

ICON = {E.PASS: "✅", E.FAIL: "❌", E.UNKNOWN: "❓", E.NA: "➖"}


def _val(fld, v, l="en"):
    from services.copilot import _fmt_val
    return _fmt_val(fld, v, l)


def render() -> None:
    l = lang()
    cat = get_catalogue()
    render_page_header("nav_schemes", "pinfo_schemes")
    p = get_profile()
    results = E.evaluate_all(p, cat)
    schemes = list_schemes(cat)

    short = {"pmmy_mudra": "MUDRA", "cgtmse": "CGTMSE", "pmegp": "PMEGP"}
    cols = st.columns(len(schemes))
    for col, s in zip(cols, schemes):
        col.metric(short.get(s["id"], s["id"].upper()), t("overall_" + results[s["id"]].overall, l).split(" — ")[0])

    ids = [s["id"] for s in schemes]
    sid = st.selectbox(t("sch_pick", l), ids, key="sch_pick", format_func=lambda i: L(get_scheme(i, cat)["name"], l))
    sc, res = get_scheme(sid, cat), results[sid]

    st.subheader(L(sc["name"], l))
    st.write(L(sc["description"], l))
    st.markdown(f"**{t('overall_' + res.overall, l)}**")
    st.caption(t("sch_verified_on", l, d=sc["last_verified"]) + " · " + t("sch_review", l, s=sc["review_status"]))

    st.markdown(f"#### {t('sch_criteria', l)}")
    for c in res.criteria:
        extra = ""
        if c.status in (E.PASS, E.FAIL):
            extra = f" — {t('ans_your_value', l, value=_val(c.field, c.profile_value, l))}"
        elif c.status == E.UNKNOWN:
            extra = f" — {t('ans_dont_know', l, field=field_label(c.field, l))}"
        elif c.status == E.NA:
            extra = f" — {t('crit_applies_note', l)}"
        st.markdown(f"{ICON[c.status]} **{L(c.label, l)}** · {t('status_' + c.status, l)}{extra}")
        srcs = ", ".join(get_source(s, cat)["title"].split(" - ")[0] for s in c.source_ids)
        st.caption(f"   {t('sch_sources', l)}: {srcs}" + (f" · {c.note}" if c.note else ""))
    for cf in insights.counterfactuals(res):
        tgt = cf["target"]
        shown = ", ".join(option_label(cf["field"], str(x), l) for x in tgt) if isinstance(tgt, list) else _val(cf["field"], tgt, l)
        st.info("↳ " + t("ans_would_need", l, field=field_label(cf["field"], l), req=f"{t('op_' + cf['op'], l)} {shown}"))
    if res.facts_used:
        with st.expander(t("sch_facts_used", l)):
            st.json({field_label(k, l): _val(k, v, l) for k, v in res.facts_used.items()})

    st.markdown(f"#### {t('sch_benefits', l)}")
    for b in sc["benefits"]:
        st.markdown(f"- {L(b['text'], l)}")
    st.markdown(f"#### {t('sch_sources', l)}")
    for src_id in sc["source_ids"]:
        s = get_source(src_id, cat)
        st.markdown(f"- [{s['title']}]({s['url']}) — *{t('src_' + s['tier'], l)}*, accessed {s['accessed']}")
    if sc.get("unresolved"):
        with st.expander(t("sch_unresolved", l)):
            for u in sc["unresolved"]:
                st.markdown(f"- {u}")

    st.divider()
    st.markdown(f"**{t('sch_backlog_head', l)}**")
    for b in unverified_backlog(cat):
        st.markdown(f"- {L(b['name'], l)}")


    st.divider()
    st.subheader(t("wi_head", l))
    st.caption(t("wi_note", l))
    fld = st.selectbox(t("wi_field", l), list(insights.NUMERIC_FIELDS), key="wi_field", format_func=lambda f: field_label(f, l))
    rows = insights.tipping_table(p, fld, cat)
    short = {"pmmy_mudra": "MUDRA", "cgtmse": "CGTMSE", "pmegp": "PMEGP"}
    table = []
    for r in rows:
        row = {t("wi_at", l): P.fmt_inr(r["at"])}
        for sid in r["status_at"]:
            row[short.get(sid, sid) + " @"] = t("overall_" + r["status_at"][sid], l).split(" — ")[0]
            row[short.get(sid, sid) + " ▲"] = t("overall_" + r["status_after"][sid], l).split(" — ")[0]
        row["⚡"] = ", ".join(short.get(x, x) for x in r["changes"]) or t("wi_same", l)
        table.append(row)
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.caption("@ = " + t("wi_at", l) + " · ▲ = " + t("wi_above", l) + " · ⚡ = " + t("wi_changes", l))
