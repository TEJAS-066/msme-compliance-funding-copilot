"""Personalised document checklist.

Items come from the scheme record only. Items with verified=false are shown in a
separate 'commonly requested - not confirmed from a scheme source' group.
Status: missing | needs_review (uploaded+extracted, not yet confirmed) | confirmed | not_applicable
"""
from __future__ import annotations

from core import profile as P
from core.catalogue import get_scheme
from core.eligibility import _compare


def build_checklist(scheme_id: str, profile: dict, confirmed_types: set[str], pending_types: set[str] | None = None,
                    cat: dict | None = None) -> list[dict]:
    pending_types = pending_types or set()
    scheme = get_scheme(scheme_id, cat)
    if scheme is None:
        raise KeyError(scheme_id)
    items = []
    for d in scheme.get("documents", []):
        status = None
        cond = d.get("applies_if")
        if cond:
            v = P.get(profile, cond["field"])
            if v is None:
                status = None  # can't tell yet -> treat as applicable but flag
            elif _compare(cond["op"], v, cond["value"]) is False:
                status = "not_applicable"
        if status is None:
            t = d["doc_type"]
            status = "confirmed" if t in confirmed_types else "needs_review" if t in pending_types else "missing"
        items.append({
            "id": d["id"], "doc_type": d["doc_type"], "name": d["name"], "why": d.get("why", {}),
            "verified": bool(d.get("verified")), "source_ids": d.get("source_ids", []),
            "status": status,
            "applicability_unknown": bool(cond) and P.get(profile, cond["field"]) is None,
        })
    return items


def summarize(items: list[dict]) -> dict:
    live = [i for i in items if i["status"] != "not_applicable"]
    return {"total": len(live), "confirmed": sum(i["status"] == "confirmed" for i in live),
            "missing": [i["id"] for i in live if i["status"] == "missing"]}
