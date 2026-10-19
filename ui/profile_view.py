import streamlit as st

from core import profile as P
from core.i18n import option_label, t
from ui.common import get_profile, lang, render_page_header, save_profile


def render() -> None:
    l = lang()
    render_page_header("nav_profile", "pinfo_profile")
    st.caption(t("prof_help", l))
    p = get_profile()
    if p.get("is_demo"):
        st.warning(t("demo_banner", l), icon="🧪")

    edits: dict[str, object] = {}
    cols = st.columns(2)
    for i, (fld, meta) in enumerate(P.FIELDS.items()):
        col = cols[i % 2]
        cur = p["fields"][fld]["value"] if p["fields"][fld]["status"] == "known" else None
        label = meta["label"].get(l) or meta["label"]["en"]
        key = f"prof_{fld}"
        if meta["kind"] == "select":
            opts = [None] + meta["options"]
            idx = opts.index(cur) if cur in opts else 0
            edits[fld] = col.selectbox(label, opts, index=idx, key=key,
                                       format_func=lambda o, f=fld: t("unknown_opt", l) if o is None else option_label(f, o, l))
        else:
            edits[fld] = col.text_input(label, value="" if cur is None else str(cur), key=key)

    if st.button(t("btn_save", l), type="primary", key="btn_save_profile"):
        newp, errors = p, []
        for fld, val in edits.items():
            old = P.get(p, fld)
            if (val in (None, "") and old is None) or (val is not None and str(val) == str(old)):
                continue
            try:
                newp = P.set_field(newp, fld, val, source="user")
            except ValueError:
                errors.append(t("bad_number", l, field=P.FIELDS[fld]["label"].get(l)))
        for e in errors:
            st.error(e)
        if not errors:
            save_profile(newp)
            st.success(t("saved_ok", l))
            st.rerun()

    p = get_profile()
    cls, basis = P.enterprise_class(p)
    if cls:
        st.info(t("derived_class", l, cls=option_label("cls", cls, l), basis=t("basis_" + basis, l)))
    else:
        st.info(t("class_unknown", l))
    mm = P.class_mismatch(p)
    if mm:
        st.warning(t("class_mismatch", l, computed=option_label("cls", mm, l)))
