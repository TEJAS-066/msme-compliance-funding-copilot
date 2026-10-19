"""Monitoring Agent (starter): curated update queue + catalogue freshness + change detection primitive.

HONEST SCOPE: this does NOT crawl government portals on a schedule. It gives the team
(1) a staleness check on every catalogue record, (2) an admin approve/reject queue so
nothing reaches an owner before a human verifies it, and (3) `fetch_and_hash` - the
primitive a scheduled job would call. Wire the schedule in Phase 5 (GitHub Actions cron).
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import date
from typing import Callable

import requests

from core.catalogue import get_catalogue, freshness_days
from core.db import conn, now

QUEUE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "review_queue.json")
MAX_AGE_DAYS = 90


def stale_schemes(cat: dict | None = None, today: date | None = None, max_age: int = MAX_AGE_DAYS) -> list[dict]:
    cat = cat or get_catalogue()
    out = []
    for s in cat["schemes"]:
        age = freshness_days(s, today)
        out.append({"scheme_id": s["id"], "last_verified": s["last_verified"], "age_days": age, "stale": age > max_age,
                    "review_status": s["review_status"]})
    return out


def load_queue() -> list[dict]:
    with open(QUEUE_PATH, encoding="utf-8") as f:
        items = json.load(f)["items"]
    with conn() as c:
        decided = {r["item_id"]: r["decision"] for r in c.execute("SELECT * FROM review_decisions").fetchall()}
    for it in items:
        it["status"] = decided.get(it["id"], it["status"])
    return items


def decide(item_id: str, decision: str) -> None:
    if decision not in ("approved", "rejected"):
        raise ValueError("decision must be approved|rejected")
    with conn() as c:
        c.execute("INSERT INTO review_decisions(item_id,decision,decided_at) VALUES(?,?,?) "
                  "ON CONFLICT(item_id) DO UPDATE SET decision=excluded.decision, decided_at=excluded.decided_at",
                  (item_id, decision, now()))


def notifiable_items() -> list[dict]:
    """Only admin-APPROVED items may ever produce an owner notification."""
    return [i for i in load_queue() if i["status"] == "approved"]


def fetch_and_hash(url: str, get: Callable = requests.get, timeout: int = 20) -> dict:
    try:
        r = get(url, timeout=timeout, headers={"User-Agent": "msme-copilot-monitor/0.1"})
    except Exception as e:
        return {"ok": False, "error": type(e).__name__, "hash": None}
    if r.status_code != 200:
        return {"ok": False, "error": f"HTTP {r.status_code}", "hash": None}
    return {"ok": True, "error": None, "hash": hashlib.sha256(r.content).hexdigest()}


# ---------------------------------------------------------------- source-change scanning
import re  # noqa: E402

HASHES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "source_hashes.json")


def normalize(content: bytes, content_type: str = "") -> bytes:
    """Hash visible text for HTML (so markup/script churn doesn't raise false alarms); raw bytes for PDFs."""
    if content[:4] == b"%PDF" or "pdf" in content_type.lower():
        return content
    txt = content.decode("utf-8", "ignore")
    txt = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", txt)
    txt = re.sub(r"(?s)<!--.*?-->", " ", txt)
    txt = re.sub(r"(?s)<[^>]+>", " ", txt)
    return re.sub(r"\s+", " ", txt).strip().lower().encode("utf-8")


def scan_sources(cat: dict | None = None, get: Callable = requests.get, hashes: dict | None = None,
                 today: date | None = None) -> dict:
    """Fetch every catalogue source, compare with last hash. Returns {hashes, changes, baseline, errors}.
    Dynamic pages (counters, dates) can still cause false positives - that is why a HUMAN reviews each change."""
    cat = cat or get_catalogue()
    today = today or date.today()
    hashes = dict(hashes or {})
    out = {"hashes": hashes, "changes": [], "baseline": [], "errors": []}
    for sid, s in cat["sources"].items():
        try:
            r = get(s["url"], timeout=30, headers={"User-Agent": "msme-copilot-monitor/0.2"})
        except Exception as e:
            out["errors"].append({"source_id": sid, "error": type(e).__name__})
            continue
        if r.status_code != 200:
            out["errors"].append({"source_id": sid, "error": f"HTTP {r.status_code}"})
            continue
        ctype = getattr(r, "headers", {}).get("content-type", "") if getattr(r, "headers", None) else ""
        digest = hashlib.sha256(normalize(r.content, ctype)).hexdigest()
        old = hashes.get(sid)
        if old is None:
            out["baseline"].append(sid)
        elif old["sha256"] != digest:
            users = [sc["id"] for sc in cat["schemes"] if sid in sc["source_ids"]]
            out["changes"].append({"source_id": sid, "title": s["title"], "url": s["url"], "schemes": users,
                                   "previous_checked": old["checked"], "today": today.isoformat()})
        hashes[sid] = {"sha256": digest, "checked": today.isoformat()}
    return out


def changes_to_queue_items(changes: list[dict]) -> list[dict]:
    return [{"id": f"chg-{c['source_id']}-{c['today']}", "kind": "SOURCE_CHANGED",
             "title": f"Source changed: {c['title']}", "scheme_id": (c["schemes"] or [None])[0],
             "detail": (f"Page content changed since {c['previous_checked']}. Affects: {', '.join(c['schemes']) or 'no scheme'}. "
                        "A human must read the source and update data/schemes.json BEFORE anyone is notified. "
                        "May be a false alarm (dynamic page)."),
             "source_url": c["url"], "status": "pending"} for c in changes]


def append_queue(items: list[dict], path: str = QUEUE_PATH) -> int:
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    have = {i["id"] for i in doc["items"]}
    new = [i for i in items if i["id"] not in have]
    doc["items"].extend(new)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return len(new)
