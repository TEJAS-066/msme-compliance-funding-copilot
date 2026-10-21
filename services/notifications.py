"""Reminder previews + optional WhatsApp send via Twilio.

Honest status values:
  PREVIEW_ONLY    -> we only rendered the text; nothing left the app
  NOT_CONFIGURED  -> no credentials; nothing sent
  SENT            -> ONLY when Twilio returned HTTP 201 with a message sid
  FAILED          -> tried and failed
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable

import requests

from core import config
from core.i18n import t


@dataclass
class SendResult:
    status: str
    detail: str = ""
    sid: str | None = None


def preview_reminder(task: dict, lang: str = "en") -> str:
    due = task.get("due_date") or t("no_due_date", lang)
    return t("reminder_text", lang, title=task["title"], due=due)


def whatsapp_configured() -> bool:
    return all(config.get(k) for k in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM"))


def send_whatsapp(to_number: str, text: str, post: Callable = requests.post) -> SendResult:
    if not whatsapp_configured():
        return SendResult("NOT_CONFIGURED", "Twilio credentials are not set; nothing was sent.")
    sid, token = config.get("TWILIO_ACCOUNT_SID"), config.get("TWILIO_AUTH_TOKEN")
    try:
        r = post(f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json", timeout=20, auth=(sid, token),
                 data={"From": f"whatsapp:{config.get('TWILIO_WHATSAPP_FROM')}", "To": f"whatsapp:{to_number}", "Body": text})
    except Exception as e:
        return SendResult("FAILED", f"{type(e).__name__}")
    if r.status_code == 201 and r.json().get("sid"):
        return SendResult("SENT", "Accepted by Twilio (this is acceptance, not proof of handset delivery).", r.json()["sid"])
    return SendResult("FAILED", f"HTTP {r.status_code}")
