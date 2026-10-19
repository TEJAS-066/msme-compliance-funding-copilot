"""Application-readiness report: one text file an owner can carry to a bank / Common Service Centre."""
from __future__ import annotations

from datetime import date

from core import eligibility as E
from core import profile as P
from core.catalogue import L, get_catalogue, get_scheme, list_schemes, get_source
from core.i18n import field_label, option_label, t
from services.copilot import _docs_text, _eligibility_text, _fmt_val


def readiness_report(profile: dict, confirmed: set[str], lang: str = "en", cat: dict | None = None,
                     today: date | None = None) -> str:
    cat = cat or get_catalogue()
    today = today or date.today()
    out = [t("rep_title", lang), f"{t('rep_date', lang)}: {today.isoformat()}"]
    if profile.get("is_demo"):
        out.append(t("demo_banner", lang))
    out += ["", t("rep_profile", lang), "-" * 40]
    for fld, meta in P.FIELDS.items():
        v = P.get(profile, fld)
        if v is None:
            continue
        shown = _fmt_val(fld, v, lang)
        out.append(f"- {field_label(fld, lang)}: {shown}")
    unknown = [field_label(f, lang) for f in P.FIELDS if P.get(profile, f) is None]
    if unknown:
        out.append(f"- {t('rep_unknown', lang)}: {', '.join(unknown)}")
    cls, basis = P.enterprise_class(profile, cat)
    if cls:
        out.append("- " + t("derived_class", lang, cls=option_label("cls", cls, lang), basis=t("basis_" + basis, lang)))

    results = E.evaluate_all(profile, cat)
    for sc in list_schemes(cat):
        out += ["", L(sc["name"], lang), "=" * 40, _eligibility_text(sc["id"], profile, cat, lang), "", _docs_text(sc["id"], profile, cat, lang, confirmed)]
        srcs = [get_source(s, cat) for s in sc["source_ids"]]
        out.append(t("ans_sources", lang) + ":")
        out += [f"  • {s['title']} — {s['url']} ({s['tier']}, {s['accessed']})" for s in srcs]
        if sc.get("unresolved"):
            out.append(t("sch_unresolved", lang) + ":")
            out += [f"  ? {u}" for u in sc["unresolved"]]
    out += ["", t("rep_disclaimer", lang)]
    return "\n".join(out)
