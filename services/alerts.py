"""Alerts & deadlines for the dashboard (the 'Lakshmi sees her next steps and deadlines' story).

Pure function over state -> list of alerts. Rendering a WhatsApp-style message from an alert is a
PREVIEW: nothing is sent from here.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from core import eligibility as E
from core import profile as P
from core.catalogue import L, get_catalogue, get_scheme
from core.checklist import build_checklist
from core.i18n import t

SEV_ORDER = {"action": 0, "warn": 1, "info": 2}


@dataclass
class Alert:
    kind: str
    severity: str          # action | warn | info
    text: str


def build_alerts(profile: dict, confirmed: set[str], documents: list[dict], tasks: list[dict],
                 approved_updates: list[dict], lang: str = "en", cat: dict | None = None,
                 today: date | None = None, horizon_days: int = 14) -> list[Alert]:
    cat = cat or get_catalogue()
    today = today or date.today()
    out: list[Alert] = []

    for sid, res in E.evaluate_all(profile, cat).items():
        name = L(get_scheme(sid, cat)["name"], lang)
        if res.overall in (E.MEETS, E.POTENTIAL):
            out.append(Alert("scheme_match", "info", t("al_scheme", lang, name=name, status=t("overall_" + res.overall, lang).split(" — ")[0])))
            missing = [i for i in build_checklist(sid, profile, confirmed, cat=cat) if i["status"] == "missing"]
            if missing:
                out.append(Alert("missing_docs", "warn", t("al_missing_docs", lang, n=len(missing), name=name)))

    for tk in tasks:
        if tk["status"] == "done" or not tk.get("due_date"):
            continue
        due = date.fromisoformat(tk["due_date"])
        if due < today:
            out.append(Alert("task_overdue", "action", t("al_task_overdue", lang, title=tk["title"], due=tk["due_date"])))
        elif due <= today + timedelta(days=horizon_days):
            out.append(Alert("task_due", "warn", t("al_task_due", lang, title=tk["title"], due=tk["due_date"])))

    for d in documents:
        if d["confirmation"] == "pending" and d["extraction_status"] == "text_extracted":
            out.append(Alert("doc_review", "action", t("al_doc_review", lang, file=d["filename"])))

    mm = P.class_mismatch(profile, cat)
    if mm:
        out.append(Alert("class_mismatch", "warn", t("al_class_mismatch", lang, computed=mm)))

    for u in approved_updates:
        out.append(Alert("catalogue_update", "info", t("al_update", lang, title=u["title"])))

    return sorted(out, key=lambda a: SEV_ORDER[a.severity])


def whatsapp_preview(alert: Alert, lang: str = "en") -> str:
    """How this alert WOULD read as a WhatsApp message. Never sends."""
    return f"{t('al_wa_prefix', lang)}\n{alert.text}\n\n{t('al_preview_note', lang)}"
