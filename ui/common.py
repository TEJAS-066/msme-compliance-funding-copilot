"""Shared UI helpers. All state lives in st.session_state + SQLite (core.db)."""
from __future__ import annotations

import streamlit as st

from core import db
from core import profile as P
from core.i18n import t
from services import llm


def lang() -> str:
    return st.session_state.get("lang", "en")


def get_profile() -> dict:
    if "profile" not in st.session_state:
        st.session_state["profile"] = db.load_profile() or P.empty_profile()
    return st.session_state["profile"]


def save_profile(p: dict) -> None:
    st.session_state["profile"] = p
    db.save_profile(p)


def banner() -> None:
    l = lang()
    st.warning(t("demo_banner", l), icon="🧪")
    prov = llm.get_provider()
    if prov:
        st.info(t("ai_mode_llm", l, provider=prov), icon="🤖")
    else:
        st.info(t("ai_mode_demo", l), icon="⚙️")


def completeness(p: dict) -> tuple[int, int]:
    known = sum(1 for v in p["fields"].values() if v["status"] == "known")
    return known, len(p["fields"])


def nba_text(nba: dict, l: str) -> str:
    """Render a core.insights.next_best_action() dict in the user's language."""
    from core.catalogue import L, get_scheme
    from core.i18n import field_label
    k = nba["kind"]
    if k == "overdue":
        return t("nba_overdue", l, title=nba["title"])
    if k == "answer_field":
        names = ", ".join(L(get_scheme(s)["name"], l).split("(")[-1].strip(")") for s in nba["schemes"])
        return t("nba_answer_field", l, field=field_label(nba["field"], l), n=nba["n"], schemes=names)
    if k == "upload_docs":
        return t("nba_upload_docs", l, docs=", ".join(L(d, l) for d in nba["docs"]), scheme=L(get_scheme(nba["scheme"])["name"], l))
    if k == "prepare":
        return t("nba_prepare", l, scheme=L(get_scheme(nba["scheme"])["name"], l))
    return t("nba_" + k, l)
