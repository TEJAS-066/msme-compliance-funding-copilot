"""Shell (tour + theme + info menu): content completeness, config safety, the JS behaviour tests, and wiring in the app."""
import json
import os
import re
import shutil
import subprocess

import pytest
from streamlit.testing.v1 import AppTest

from ui import shell
from ui.tour_content import LANGS, STEP_DEFS, TEXT, UI, steps_for

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = {"ta": re.compile("[\u0b80-\u0bff]"), "hi": re.compile("[\u0900-\u097f]"), "te": re.compile("[\u0c00-\u0c7f]")}
NAV = ["nav_dashboard", "nav_profile", "nav_documents", "nav_schemes", "nav_checklist", "nav_copilot", "nav_channel", "nav_forms", "nav_tasks", "nav_admin"]


def test_every_language_has_every_step_with_real_text():
    ids = [d[0] for d in STEP_DEFS]
    for code, _ in LANGS:
        assert set(TEXT[code]) == set(ids), code
        for sid in ids:
            title, body = TEXT[code][sid]
            assert title.strip() and len(body) > 25 and len(title) < 70 and len(body) < 330, (code, sid)
        for key in UI["en"]:
            assert UI[code][key].strip(), (code, key)


def test_non_english_text_uses_the_right_script():
    for code, rx in SCRIPTS.items():
        assert all(rx.search(TEXT[code][sid][0] + TEXT[code][sid][1]) for sid in TEXT[code]), code


def test_step_pages_and_selectors_are_valid():
    for sid, page, sel, place in STEP_DEFS:
        assert page in NAV and place in ("center", "top", "bottom", "left", "right") and isinstance(sel, list)
        if place == "center":
            assert sel == []


def test_tour_targets_exist_as_keyed_containers_in_the_pages():
    src = open(os.path.join(ROOT, "ui", "dashboard.py"), encoding="utf-8").read()
    for key in ("tour_stepper", "tour_nba", "tour_agents", "btn_load_demo"):
        assert key in src, key


def test_config_and_script_are_safe_to_inline():
    cfg = shell.build_config("ta", NAV, "nav_documents")
    assert cfg["currentNav"] == 2 and cfg["lang"] == "ta" and len(cfg["steps"]) == len(STEP_DEFS)
    cfg["steps"][0]["title"] = "</script><script>alert(1)</script>"
    js = shell.build_script(cfg)
    assert "</script>" not in js and "__CFG__" not in js and "__CSS__" not in js
    assert js.count("--msme-accent") > 5                     # CSS really inlined


def test_page_info_is_localised():
    assert shell.page_info("nav_dashboard", "en") and shell.page_info("nav_dashboard", "ta") != shell.page_info("nav_dashboard", "en")


def test_javascript_behaviour_in_simulated_browser():
    if not shutil.which("node") or not os.path.isdir(os.path.join(ROOT, "tests", "js", "node_modules", "jsdom")):
        pytest.skip("needs node + `cd tests/js && npm install` (jsdom)")
    r = subprocess.run(["node", "--test"], cwd=os.path.join(ROOT, "tests", "js"), capture_output=True, text=True, timeout=240)
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-500:]


def test_app_renders_shell_without_deprecated_api_or_errors():
    at = AppTest.from_file(os.path.join(ROOT, "app.py"), default_timeout=60)
    at.run()
    assert not at.exception
    assert not any("components.v1.html" in str(getattr(w, "value", "")) for w in at.warning)


@pytest.mark.parametrize("lang", [n for _, n in LANGS])
def test_all_four_languages_render_every_page(lang):
    at = AppTest.from_file(os.path.join(ROOT, "app.py"), default_timeout=90)
    at.run()
    at.sidebar.radio(key="lang_radio").set_value(lang).run()
    for k in NAV:
        at.sidebar.radio(key="nav").set_value(k).run()
        assert not at.exception, (lang, k, [e.value for e in at.exception][:1])
