"""Decision-support on top of the rules engine (still 100% deterministic, no LLM).

1. unknown_impact   - which missing fact would settle the most open criteria? ("information gain")
2. tipping_points   - at which values does the verdict change? (derived from the catalogue's own thresholds)
3. counterfactuals  - for a failed criterion, what does the RULE require? (explanation, not advice to change facts)
4. next_best_action - one prioritised thing to do now
"""
from __future__ import annotations

from datetime import date

from core import eligibility as E
from core import profile as P
from core.catalogue import get_catalogue, list_schemes

NUMERIC_FIELDS = ("loan_needed_inr", "investment_inr", "turnover_inr")


def _blockers(crit, profile: dict, cat: dict) -> list[str]:
    """Profile fields whose absence makes this criterion UNKNOWN."""
    out = []
    cond = crit.get("applies_if")
    if cond and P.get(profile, cond["field"]) is None:
        out.append(cond["field"])
        return out                                   # condition unknown: that is the first blocker
    fld = crit["field"]
    if fld == "enterprise_class":
        if P.get(profile, "enterprise_class_declared") is None:
            out += [f for f in ("investment_inr", "turnover_inr") if P.get(profile, f) is None]
    elif P.get(profile, fld) is None:
        out.append(fld)
    return out


def unknown_impact(profile: dict, cat: dict | None = None) -> list[dict]:
    """Rank unknown profile fields by how many UNKNOWN criteria (across verified schemes) they block."""
    cat = cat or get_catalogue()
    tally: dict[str, dict] = {}
    for sc in list_schemes(cat):
        res = E.evaluate_scheme(sc, profile, cat)
        by_id = {c["id"]: c for c in sc["criteria"]}
        for r in res.criteria:
            if r.status != E.UNKNOWN:
                continue
            for f in _blockers(by_id[r.id], profile, cat):
                d = tally.setdefault(f, {"field": f, "criteria_count": 0, "schemes": set(), "criteria": []})
                d["criteria_count"] += 1
                d["schemes"].add(sc["id"])
                d["criteria"].append(f"{sc['id']}:{r.id}")
    out = [{**d, "schemes": sorted(d["schemes"])} for d in tally.values()]
    return sorted(out, key=lambda d: (-d["criteria_count"], d["field"]))


def tipping_points(field: str, cat: dict | None = None) -> list[int]:
    """Numeric thresholds in the catalogue that involve `field`."""
    cat = cat or get_catalogue()
    pts: set[int] = set()
    for sc in list_schemes(cat):
        for c in sc["criteria"]:
            for spec in (c, c.get("applies_if") or {}):
                if spec.get("field") == field and spec.get("op") in ("lte", "gte", "lt", "gt"):
                    pts.add(int(spec["value"]))
    if field in ("investment_inr", "turnover_inr"):
        key = "investment" if field == "investment_inr" else "turnover"
        for lim in cat["classification"]["limits_inr"].values():
            pts.add(int(lim[key]))
    return sorted(pts)


def tipping_table(profile: dict, field: str, cat: dict | None = None) -> list[dict]:
    """For each threshold t: verdicts AT t and just above (t+1). `changes` marks real tipping points."""
    cat = cat or get_catalogue()
    rows = []
    for t in tipping_points(field, cat):
        at = {k: v.overall for k, v in E.evaluate_all(P.set_field(profile, field, t, "whatif"), cat).items()}
        after = {k: v.overall for k, v in E.evaluate_all(P.set_field(profile, field, t + 1, "whatif"), cat).items()}
        rows.append({"at": t, "status_at": at, "status_after": after,
                     "changes": [k for k in at if at[k] != after[k]]})
    return rows


OP_WORD = {"lte": "at most", "gte": "at least", "lt": "below", "gt": "above", "eq": "exactly", "ne": "not", "in": "one of", "not_in": "none of"}


def counterfactuals(result: E.SchemeResult) -> list[dict]:
    """What each FAILED required criterion demands. Purely a restatement of the rule."""
    return [{"criterion": r.id, "label": r.label, "field": r.field, "op": r.op, "target": r.target, "your_value": r.profile_value}
            for r in result.criteria if r.status == E.FAIL and r.required]


def next_best_action(profile: dict, confirmed_types: set[str], tasks: list[dict], cat: dict | None = None,
                     today: date | None = None) -> dict:
    """Return {'kind': ..., params...}; UI renders it via i18n key 'nba_<kind>'."""
    cat = cat or get_catalogue()
    known = sum(1 for v in profile["fields"].values() if v["status"] == "known")
    if known == 0:
        return {"kind": "load_profile"}
    overdue = [t for t in tasks if t.get("due_date") and t["status"] != "done"
               and date.fromisoformat(t["due_date"]) < (today or date.today())]
    if overdue:
        return {"kind": "overdue", "title": overdue[0]["title"]}
    impact = unknown_impact(profile, cat)
    if impact:
        top = impact[0]
        return {"kind": "answer_field", "field": top["field"], "n": top["criteria_count"], "schemes": top["schemes"]}
    from core.checklist import build_checklist
    results = E.evaluate_all(profile, cat)
    for sid, r in results.items():
        if r.overall == E.MEETS:
            missing = [i for i in build_checklist(sid, profile, confirmed_types, cat=cat) if i["status"] == "missing"]
            if missing:
                return {"kind": "upload_docs", "scheme": sid, "docs": [i["name"] for i in missing]}
    if any(r.overall == E.MEETS for r in results.values()):
        sid = next(s for s, r in results.items() if r.overall == E.MEETS)
        return {"kind": "prepare", "scheme": sid}
    if all(r.overall == E.UNLIKELY for r in results.values()):
        return {"kind": "review_inputs"}
    return {"kind": "add_task"}
