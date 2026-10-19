"""Scheme catalogue loader + validator.

WHY: every fact the product shows must come from this one version-controlled file,
with a source and a verification date. The validator refuses a catalogue where a
scheme has criteria without sources, so unsourced facts can't sneak in.
"""
from __future__ import annotations

import json
import os
from datetime import date
from functools import lru_cache
from typing import Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CATALOGUE_PATH = os.path.join(DATA_DIR, "schemes.json")

VERIFIED_STATUSES = {"verified_official", "partly_verified_official"}


class CatalogueError(ValueError):
    pass


def L(text_obj: Any, lang: str = "en") -> str:
    """Pick a language from {'en':..,'ta':..}; fall back to English, never crash."""
    if isinstance(text_obj, dict):
        return text_obj.get(lang) or text_obj.get("en") or ""
    return str(text_obj or "")


def validate(cat: dict) -> list[str]:
    """Return a list of problems (empty list = valid)."""
    problems: list[str] = []
    sources = cat.get("sources", {})
    for sid, s in sources.items():
        for k in ("title", "url", "tier", "accessed"):
            if not s.get(k):
                problems.append(f"source {sid}: missing {k}")
        if s.get("tier") not in ("official", "secondary"):
            problems.append(f"source {sid}: tier must be official|secondary")
        if not str(s.get("url", "")).startswith("http"):
            problems.append(f"source {sid}: url must start with http")
    for sc in cat.get("schemes", []):
        sid = sc.get("id", "?")
        for k in ("name", "description", "last_verified", "review_status", "source_ids", "criteria"):
            if k not in sc:
                problems.append(f"scheme {sid}: missing {k}")
        try:
            date.fromisoformat(sc.get("last_verified", ""))
        except ValueError:
            problems.append(f"scheme {sid}: last_verified must be YYYY-MM-DD")
        for src in sc.get("source_ids", []):
            if src not in sources:
                problems.append(f"scheme {sid}: unknown source {src}")
        for c in sc.get("criteria", []):
            if not c.get("source_ids"):
                problems.append(f"scheme {sid} criterion {c.get('id')}: no source_ids (unsourced criteria not allowed)")
            for src in c.get("source_ids", []):
                if src not in sources:
                    problems.append(f"scheme {sid} criterion {c.get('id')}: unknown source {src}")
        for d in sc.get("documents", []):
            if d.get("verified") and not d.get("source_ids"):
                problems.append(f"scheme {sid} document {d.get('id')}: marked verified but has no source")
    return problems


@lru_cache(maxsize=1)
def _load_default() -> dict:
    return load(CATALOGUE_PATH)


def load(path: str = CATALOGUE_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        cat = json.load(f)
    problems = validate(cat)
    if problems:
        raise CatalogueError("Invalid catalogue:\n- " + "\n- ".join(problems))
    return cat


def get_catalogue() -> dict:
    return _load_default()


def list_schemes(cat: dict | None = None) -> list[dict]:
    cat = cat or get_catalogue()
    return [s for s in cat["schemes"] if s.get("review_status") in VERIFIED_STATUSES]


def get_scheme(scheme_id: str, cat: dict | None = None) -> dict | None:
    cat = cat or get_catalogue()
    for s in cat["schemes"]:
        if s["id"] == scheme_id:
            return s
    return None


def get_source(source_id: str, cat: dict | None = None) -> dict | None:
    cat = cat or get_catalogue()
    return cat["sources"].get(source_id)


def unverified_backlog(cat: dict | None = None) -> list[dict]:
    cat = cat or get_catalogue()
    return cat.get("unverified_backlog", [])


def freshness_days(scheme: dict, today: date | None = None) -> int:
    today = today or date.today()
    return (today - date.fromisoformat(scheme["last_verified"])).days
