"""Copilot Orchestrator.

Order of operations (this is the product's core promise):
  1. retrieve   -> which verified schemes does the question touch?
  2. evaluate   -> the RULES ENGINE decides eligibility (never the LLM)
  3. ground     -> build a context of verified facts + rule results + sources
  4. explain    -> deterministic template (demo mode) OR LLM, then GUARD the LLM text
  5. cite       -> sources are appended from catalogue metadata, never from LLM output
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from core import eligibility as E
from core import insights as I
from core import profile as P
from core.catalogue import get_catalogue, get_scheme, get_source, L
from core.checklist import build_checklist
from core.i18n import t, field_label, option_label
from services import llm
from services.retrieval import retrieve

BANNED_PHRASES = ["guaranteed", "you will definitely", "you are approved", "assured approval", "100% sure"]


@dataclass
class Answer:
    text: str
    lang: str
    mode: str                       # demo_deterministic | llm:<provider> | demo_fallback
    sources: list[dict] = field(default_factory=list)
    refused: bool = False
    scheme_ids: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    trace: list[dict] = field(default_factory=list)      # which module did what (shown in the UI)


# ---------- grounding ----------
def build_context(scheme_ids: list[str], profile: dict, cat: dict, confirmed_types: set[str]) -> dict:
    results = E.evaluate_all(profile, cat)
    ctx = {"profile_known_facts": {k: v["value"] for k, v in profile["fields"].items() if v["status"] == "known"},
           "profile_unknown_fields": [k for k, v in profile["fields"].items() if v["status"] != "known"], "schemes": []}
    for sid in scheme_ids:
        sc, res = get_scheme(sid, cat), results[sid]
        ctx["schemes"].append({
            "id": sid, "name": L(sc["name"], "en"), "description": L(sc["description"], "en"),
            "overall_status_from_rules_engine": res.overall,
            "criteria": [{"label": L(c.label, "en"), "status": c.status, "your_value": c.profile_value} for c in res.criteria],
            "benefits": [L(b["text"], "en") for b in sc["benefits"]],
            "documents": [{"name": L(d["name"], "en"), "status": d["status"], "verified_from_source": d["verified"]}
                          for d in build_checklist(sid, profile, confirmed_types, cat=cat)],
            "unresolved": sc.get("unresolved", []),
            "last_verified": sc["last_verified"],
        })
    return ctx


def _sources_for(scheme_ids: list[str], cat: dict) -> list[dict]:
    seen, out = set(), []
    for sid in scheme_ids:
        sc = get_scheme(sid, cat)
        for src_id in sc["source_ids"]:
            if src_id in seen:
                continue
            seen.add(src_id)
            s = get_source(src_id, cat)
            out.append({"id": src_id, "title": s["title"], "url": s["url"], "tier": s["tier"], "accessed": s["accessed"]})
    return out


# ---------- deterministic templates ----------
def _fmt_val(fld: str, v, lang: str = "en") -> str:
    """Human-readable value: rupee grouping for amounts, translated labels for choices."""
    if v is None:
        return "-"
    if fld == "enterprise_class":
        return option_label("cls", str(v), lang)
    kind = P.FIELDS.get(fld, {}).get("kind")
    if kind == "int":
        return str(v) if fld == "employees" else P.fmt_inr(v)
    if kind == "select":
        return option_label(fld, str(v), lang)
    return str(v)


def _req_text(op: str, fld: str, target, lang: str) -> str:
    def f(v):
        return _fmt_val(fld, v, lang) if not isinstance(v, (list, tuple)) else ", ".join(option_label(fld, str(x), lang) for x in v)
    return f"{t('op_' + op, lang)} {f(target)}"


def _eligibility_text(sid: str, profile: dict, cat: dict, lang: str) -> str:
    sc, res = get_scheme(sid, cat), E.evaluate_scheme(get_scheme(sid, cat), profile, cat)
    lines = [t("ans_elig_head", lang, name=L(sc["name"], lang), status=t("overall_" + res.overall, lang)), t("ans_why", lang)]
    icon = {E.PASS: "✔", E.FAIL: "✖", E.UNKNOWN: "?", E.NA: "–"}
    for c in res.criteria:
        extra = ""
        if c.status in (E.PASS, E.FAIL):
            extra = " — " + t("ans_your_value", lang, value=_fmt_val(c.field, c.profile_value, lang))
        elif c.status == E.UNKNOWN:
            extra = " — " + t("ans_dont_know", lang, field=field_label(c.field, lang))
        lines.append(f"{icon[c.status]} {L(c.label, lang)} [{t('status_' + c.status, lang)}]{extra}")
    if res.unknown_fields:
        lines.append(t("ans_unknown", lang, fields=", ".join(field_label(f, lang) for f in res.unknown_fields)))
    for cf in I.counterfactuals(res):
        lines.append("↳ " + t("ans_would_need", lang, field=field_label(cf["field"], lang),
                              req=_req_text(cf["op"], cf["field"], cf["target"], lang)))
    if sid == "pmmy_mudra":
        tier = E.mudra_tier(P.get(profile, "loan_needed_inr"))
        if tier:
            lines.append(t("mudra_tier_line", lang, amount=P.fmt_inr(P.get(profile, "loan_needed_inr")), tier=t("tier_" + tier, lang)))
    lines.append(t("ans_not_approval", lang))
    return "\n".join(lines)


def _docs_text(sid: str, profile: dict, cat: dict, lang: str, confirmed: set[str]) -> str:
    sc = get_scheme(sid, cat)
    lines = [t("ans_docs_head", lang, name=L(sc["name"], lang))]
    for it in build_checklist(sid, profile, confirmed, cat=cat):
        if it["status"] == "not_applicable":
            continue
        tag = "" if it["verified"] else " " + t("ans_docs_unverified_tag", lang)
        lines.append(f"- {L(it['name'], lang)} [{t('doc_' + it['status'], lang)}]{tag}")
    return "\n".join(lines)


def _amount_text(sid: str, cat: dict, lang: str) -> str:
    sc = get_scheme(sid, cat)
    return "\n".join([L(sc["name"], lang), t("ans_benefits_head", lang)] + [f"- {L(b['text'], lang)}" for b in sc["benefits"]])


def _next_text(sid: str, profile: dict, cat: dict, lang: str, confirmed: set[str]) -> str:
    sc, res = get_scheme(sid, cat), E.evaluate_scheme(get_scheme(sid, cat), profile, cat)
    lines = [t("ans_next_head", lang, name=L(sc["name"], lang))]
    n = 1
    if res.unknown_fields:
        lines.append(f"{n}. " + t("ans_next_fill", lang, fields=", ".join(field_label(f, lang) for f in res.unknown_fields))); n += 1
    missing = [L(i["name"], lang) for i in build_checklist(sid, profile, confirmed, cat=cat) if i["status"] == "missing"]
    if missing:
        lines.append(f"{n}. " + t("ans_next_docs", lang, docs=", ".join(missing))); n += 1
    lines.append(f"{n}. " + t("ans_next_bank", lang))
    return "\n".join(lines)


def _deterministic(intent: str, sids: list[str], backlog: list[dict], profile: dict, cat: dict, lang: str, confirmed: set[str]) -> tuple[str, bool]:
    """Returns (text, refused)."""
    if backlog and not sids:
        return "\n".join(t("ans_backlog", lang, name=L(b["name"], lang)) for b in backlog), True
    if intent == "deadline":
        return t("ans_deadline", lang), False
    if not sids:
        if intent in ("eligibility", "next_steps"):          # "what can I get?" -> evaluate every verified scheme
            sids = [s["id"] for s in E.list_schemes(cat)]
        else:
            return t("ans_refuse", lang), True
    parts = []
    for sid in sids:
        sc = get_scheme(sid, cat)
        if intent == "documents":
            parts.append(_docs_text(sid, profile, cat, lang, confirmed))
        elif intent == "amount":
            parts.append(_amount_text(sid, cat, lang))
        elif intent in ("next_steps", "form"):
            parts.append(_next_text(sid, profile, cat, lang, confirmed))
        elif intent == "eligibility":
            parts.append(_eligibility_text(sid, profile, cat, lang))
        else:  # overview / unknown intent with a matched scheme
            parts.append(f"{L(sc['name'], lang)}\n{L(sc['description'], lang)}\n\n" + _amount_text(sid, cat, lang).split("\n", 1)[1])
    return "\n\n".join(parts), False


# ---------- LLM path + guard ----------
_NUM = re.compile(r"\d[\d,]*\.?\d*")


def _norm(n: str) -> str:
    return n.replace(",", "").rstrip(".")


def guard(answer_text: str, context: dict) -> list[str]:
    """Return a list of violations (empty = acceptable). The LLM may only restate numbers present in the grounding context."""
    problems = []
    low = answer_text.lower()
    for ph in BANNED_PHRASES:
        if ph in low:
            problems.append(f"banned phrase: {ph}")
    allowed = {_norm(n) for n in _NUM.findall(json.dumps(context, ensure_ascii=False))}
    for n in _NUM.findall(answer_text):
        n2 = _norm(n)
        if n2 and n2 not in allowed and not (n2.isdigit() and int(n2) <= 10):
            problems.append(f"number not in verified context: {n2}")
    return problems


SYSTEM_PROMPT = (
    "You explain Indian MSME scheme information to a small business owner in simple words.\n"
    "STRICT RULES:\n"
    "1. Use ONLY the facts in the CONTEXT json. If the context does not answer the question, say you cannot find it in verified sources.\n"
    "2. Eligibility status comes from 'overall_status_from_rules_engine'. Never change or contradict it.\n"
    "3. Never invent amounts, deadlines, documents, percentages or URLs. Never promise approval or funding.\n"
    "4. Say what is unknown instead of assuming. Keep it short, in the requested language.\n"
    "5. Do not output links; sources are added separately."
)


def answer(question: str, lang: str, profile: dict, confirmed_types: set[str] | None = None,
           cat: dict | None = None, use_llm: bool = True, _llm_complete=None) -> Answer:
    cat = cat or get_catalogue()
    confirmed_types = confirmed_types or set()
    lang = lang if lang in ("en", "ta", "hi", "te") else "en"
    q = (question or "").strip()
    if not q:
        return Answer(t("ans_empty", lang), lang, "demo_deterministic", refused=True)

    trace: list[dict] = []
    r = retrieve(q, cat)
    trace.append({"agent": "Retrieval", "detail": f"intent={r['intent']}; schemes={r['scheme_ids'] or '-'}; unverified_mentions={[b['id'] for b in r['backlog']] or '-'}"})
    sids = r["scheme_ids"] or ([s["id"] for s in E.list_schemes(cat)] if r["intent"] in ("eligibility", "next_steps") and not r["backlog"] else [])
    det_text, refused = _deterministic(r["intent"], r["scheme_ids"], r["backlog"], profile, cat, lang, confirmed_types)
    sources = _sources_for(sids, cat)
    notes: list[str] = []
    for sid in sids:
        res = E.evaluate_scheme(get_scheme(sid, cat), profile, cat)
        c = res.counts()
        trace.append({"agent": "Eligibility (rules engine)",
                      "detail": f"{sid}: {res.overall} — PASS {c['PASS']} · FAIL {c['FAIL']} · UNKNOWN {c['UNKNOWN']} · N/A {c['NOT_APPLICABLE']}"})
    if refused:
        trace.append({"agent": "Refusal", "detail": "no verified source covers this — nothing invented"})

    provider = llm.get_provider() if use_llm else None
    if provider and sids and not refused and r["intent"] != "deadline":
        ctx = build_context(sids, profile, cat, confirmed_types)
        lang_name = {"en": "English", "ta": "Tamil", "hi": "Hindi", "te": "Telugu"}.get(lang, "English")
        user = f"LANGUAGE: {lang_name}\nQUESTION: {q}\nCONTEXT: {json.dumps(ctx, ensure_ascii=False)}"
        try:
            text = (_llm_complete or llm.complete)(SYSTEM_PROMPT, user, provider)
            problems = guard(text, ctx)
            if not problems:
                trace.append({"agent": f"LLM ({provider})", "detail": "reworded the verified context"})
                trace.append({"agent": "Guard", "detail": "PASSED — no invented numbers or promises"})
                trace.append({"agent": "Citations", "detail": f"{len(sources)} source(s) attached from catalogue metadata"})
                return Answer(text, lang, f"llm:{provider}", sources, False, sids, notes, trace)
            notes.append("LLM answer rejected by guard: " + "; ".join(problems))
            trace.append({"agent": "Guard", "detail": "REJECTED the LLM text → deterministic answer used"})
        except llm.LLMError as e:
            notes.append(f"LLM unavailable: {e}")
            trace.append({"agent": "LLM", "detail": "unavailable → deterministic answer used"})
        trace.append({"agent": "Citations", "detail": f"{len(sources)} source(s) attached from catalogue metadata"})
        return Answer(det_text, lang, "demo_fallback", sources, refused, sids, notes, trace)

    trace.append({"agent": "Composer", "detail": "deterministic template from verified catalogue + rule results (no LLM)"})
    trace.append({"agent": "Citations", "detail": f"{len(sources)} source(s) attached from catalogue metadata"})
    return Answer(det_text, lang, "demo_deterministic", sources, refused, sids, notes, trace)
