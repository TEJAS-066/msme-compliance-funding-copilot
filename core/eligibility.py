"""Deterministic eligibility engine.  RULES DECIDE; AI EXPLAINS; THE OWNER ACTS.

No LLM is called here. Each criterion returns PASS / FAIL / UNKNOWN / NOT_APPLICABLE.
Missing data is UNKNOWN -- never an automatic PASS.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core import profile as P
from core.catalogue import get_catalogue, list_schemes

PASS, FAIL, UNKNOWN, NA = "PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE"

# overall status keys (labels live in core/i18n.py)
MEETS = "meets_encoded"
POTENTIAL = "potentially_eligible"
MORE_INFO = "more_info_required"
UNLIKELY = "unlikely_encoded"


@dataclass
class CriterionResult:
    id: str
    label: dict
    status: str
    field: str
    profile_value: Any
    op: str
    target: Any
    required: bool
    source_ids: list
    note: str | None = None


@dataclass
class SchemeResult:
    scheme_id: str
    overall: str
    criteria: list[CriterionResult] = field(default_factory=list)
    unknown_fields: list[str] = field(default_factory=list)
    facts_used: dict = field(default_factory=dict)
    source_ids: list = field(default_factory=list)

    def counts(self) -> dict:
        c = {PASS: 0, FAIL: 0, UNKNOWN: 0, NA: 0}
        for r in self.criteria:
            c[r.status] += 1
        return c


def _resolve(profile: dict, fld: str, cat: dict) -> tuple[Any, bool]:
    """Return (value, known). 'enterprise_class' is derived from the profile."""
    if fld == "enterprise_class":
        cls, _ = P.enterprise_class(profile, cat)
        return cls, cls is not None
    v = P.get(profile, fld)
    return v, v is not None


def _compare(op: str, value: Any, target: Any) -> bool | None:
    """True/False, or None if the comparison can't be made (bad type)."""
    try:
        if op == "eq":
            return value == target
        if op == "ne":
            return value != target
        if op == "in":
            return value in target
        if op == "not_in":
            return value not in target
        if op in ("lte", "gte", "lt", "gt"):
            v, t = float(value), float(target)
            return {"lte": v <= t, "gte": v >= t, "lt": v < t, "gt": v > t}[op]
    except (TypeError, ValueError):
        return None
    raise ValueError(f"unsupported op {op}")


def evaluate_criterion(crit: dict, profile: dict, cat: dict) -> CriterionResult:
    base = dict(id=crit["id"], label=crit["label"], field=crit["field"], op=crit["op"],
                target=crit["value"], required=crit.get("required", True),
                source_ids=crit.get("source_ids", []), note=crit.get("note"))

    cond = crit.get("applies_if")
    if cond:
        cv, cknown = _resolve(profile, cond["field"], cat)
        if not cknown:
            # We can't even tell whether this criterion applies -> UNKNOWN, not N/A.
            return CriterionResult(status=UNKNOWN, profile_value=None, **base)
        applies = _compare(cond["op"], cv, cond["value"])
        if applies is False:
            return CriterionResult(status=NA, profile_value=None, **base)

    value, known = _resolve(profile, crit["field"], cat)
    if not known:
        return CriterionResult(status=UNKNOWN, profile_value=None, **base)
    ok = _compare(crit["op"], value, crit["value"])
    if ok is None:
        return CriterionResult(status=UNKNOWN, profile_value=value, **base)
    return CriterionResult(status=PASS if ok else FAIL, profile_value=value, **base)


def overall_status(results: list[CriterionResult]) -> str:
    req = [r for r in results if r.required and r.status != NA]
    if any(r.status == FAIL for r in req):
        return UNLIKELY
    if all(r.status == PASS for r in req):
        return MEETS            # includes the case of zero applicable criteria
    unknown = sum(1 for r in req if r.status == UNKNOWN)
    if unknown / len(req) >= 0.5:
        return MORE_INFO
    return POTENTIAL


def evaluate_scheme(scheme: dict, profile: dict, cat: dict | None = None) -> SchemeResult:
    cat = cat or get_catalogue()
    results = [evaluate_criterion(c, profile, cat) for c in scheme["criteria"]]
    unknown_fields = sorted({r.field for r in results if r.status == UNKNOWN})
    facts = {r.field: r.profile_value for r in results if r.profile_value is not None}
    srcs = sorted({s for r in results for s in r.source_ids} | set(scheme.get("source_ids", [])))
    return SchemeResult(scheme_id=scheme["id"], overall=overall_status(results), criteria=results,
                        unknown_fields=unknown_fields, facts_used=facts, source_ids=srcs)


def evaluate_all(profile: dict, cat: dict | None = None) -> dict[str, SchemeResult]:
    cat = cat or get_catalogue()
    return {s["id"]: evaluate_scheme(s, profile, cat) for s in list_schemes(cat)}


def mudra_tier(loan_inr: int | None) -> str | None:
    """Informational: which PMMY loan category an amount falls in (source: PIB factsheet)."""
    if loan_inr is None:
        return None
    if loan_inr <= 50_000:
        return "shishu"
    if loan_inr <= 500_000:
        return "kishor"
    if loan_inr <= 1_000_000:
        return "tarun"
    if loan_inr <= 2_000_000:
        return "tarun_plus"
    return None
