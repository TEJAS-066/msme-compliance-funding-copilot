"""Global shell: floating ⓘ menu + light/dark switch + guided tour (speech-bubble coach marks).

Python builds a small JSON config (language, localised steps, page names); ui/assets/shell.js does the work in the
browser, drawing into the parent Streamlit page. No server round-trip for theme or tour navigation.
"""
from __future__ import annotations

import json
import os

from core.i18n import t
from ui.embed import run_html
from ui.tour_content import LANGS, UI, steps_for

ASSETS = os.path.join(os.path.dirname(__file__), "assets")


def _read(name: str) -> str:
    with open(os.path.join(ASSETS, name), encoding="utf-8") as f:
        return f.read()


def page_info(nav_key: str, lang: str) -> str:
    key = "pinfo_" + nav_key.replace("nav_", "")
    text = t(key, lang)
    return "" if text.startswith("[") else text


def build_config(lang: str, nav_keys: list[str], current_nav: str, autostart: bool = False, test_mode: bool = False) -> dict:
    return {"lang": lang, "langs": [list(x) for x in LANGS], "ui": UI, "steps": steps_for(lang), "navKeys": nav_keys,
            "currentNav": nav_keys.index(current_nav), "pageInfo": page_info(current_nav, lang),
            "autostart": autostart, "testMode": test_mode}


def build_script(cfg: dict) -> str:
    """The complete JS (config + CSS inlined). '</' is escaped so nothing can close the <script> tag early."""
    safe = lambda obj: json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")
    return _read("shell.js").replace("__CFG__", safe(cfg)).replace("__CSS__", safe(_read("shell.css")))


def install(lang: str, nav_keys: list[str], current_nav: str) -> None:
    cfg = build_config(lang, nav_keys, current_nav)
    run_html(f"<script>{build_script(cfg)}</script>", height=0)
