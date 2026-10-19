"""Opens every page in both languages with Streamlit's headless AppTest and asserts no exception."""
import os

import pytest
from streamlit.testing.v1 import AppTest

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")

PAGES = ["nav_dashboard", "nav_profile", "nav_documents", "nav_schemes", "nav_checklist",
         "nav_copilot", "nav_channel", "nav_forms", "nav_tasks", "nav_admin"]


def boot(lang="English"):
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    assert not at.exception
    at.sidebar.radio(key="lang_radio").set_value(lang).run()
    return at


@pytest.mark.parametrize("lang", ["English", "தமிழ்"])
@pytest.mark.parametrize("page", PAGES)
def test_every_page_renders(page, lang):
    at = boot(lang)
    at.button(key="btn_load_demo")       # exists on dashboard
    at.sidebar.radio(key="nav").set_value(page).run()
    assert not at.exception, [e.value for e in at.exception]


def test_load_demo_profile_then_schemes_page_shows_results():
    at = boot()
    at.button(key="btn_load_demo").click().run()
    assert not at.exception
    at.sidebar.radio(key="nav").set_value("nav_schemes").run()
    assert not at.exception
    text = " ".join(m.value for m in at.markdown)
    assert "Meets the criteria we have encoded" in text


def test_profile_edit_changes_eligibility():
    at = boot()
    at.button(key="btn_load_demo").click().run()
    at.sidebar.radio(key="nav").set_value("nav_profile").run()
    at.selectbox(key="prof_activity").set_value("agriculture")
    at.button(key="btn_save_profile").click().run()
    assert not at.exception
    at.sidebar.radio(key="nav").set_value("nav_schemes").run()
    text = " ".join(m.value for m in at.markdown)
    assert "Unlikely to qualify" in text


def test_sample_document_flow_apply_to_profile():
    at = boot()
    at.button(key="btn_load_demo").click().run()
    at.sidebar.radio(key="nav").set_value("nav_documents").run()
    at.selectbox(key="sample_pick").set_value("sample_udyam_lakshmi.pdf")
    at.button(key="btn_sample").click().run()
    assert not at.exception
    apply_btns = [b for b in at.button if b.key and b.key.startswith("apply_")]
    assert apply_btns, "document review UI did not appear"
    apply_btns[0].click().run()
    assert not at.exception
    assert at.session_state["profile"]["fields"]["udyam_number"]["value"] == "UDYAM-TN-02-0000123"


def test_chat_answers_in_tamil():
    at = boot("தமிழ்")
    at.button(key="btn_load_demo").click().run()
    at.sidebar.radio(key="nav").set_value("nav_copilot").run()
    at.chat_input(key="chat_input").set_value("எனக்கு MUDRA தகுதி உள்ளதா?").run()
    assert not at.exception
    assert any("நாங்கள் குறியிட்ட" in m.value for m in at.markdown)


def test_task_flow():
    at = boot()
    at.sidebar.radio(key="nav").set_value("nav_tasks").run()
    at.text_input(key="tsk_title").set_value("Collect Udyam certificate")
    [b for b in at.button if b.label == "Add task"][0].click().run()
    assert not at.exception
    assert any("Collect Udyam certificate" in m.value for m in at.markdown)
    [b for b in at.button if b.key and b.key.startswith("done_")][0].click().run()
    assert not at.exception


def test_dashboard_shows_next_best_action_and_alerts():
    at = boot()
    at.button(key="btn_load_demo").click().run()
    assert not at.exception
    text = " ".join(x.value for x in at.success) + " ".join(m.value for m in at.markdown)
    assert "next best action" in text.lower() and "Scheme match" in text


def test_dashboard_tamil_alert_text():
    at = boot("தமிழ்")
    at.button(key="btn_load_demo").click().run()
    assert any("திட்டப் பொருத்தம்" in m.value for m in at.markdown)


def test_what_if_table_present():
    at = boot()
    at.button(key="btn_load_demo").click().run()
    at.sidebar.radio(key="nav").set_value("nav_schemes").run()
    assert not at.exception and len(at.dataframe) >= 1


def test_chat_has_module_trace():
    at = boot()
    at.button(key="btn_load_demo").click().run()
    at.sidebar.radio(key="nav").set_value("nav_copilot").run()
    at.chat_input(key="chat_input").set_value("Am I eligible for CGTMSE?").run()
    assert not at.exception
    assert any("module trace" in e.label for e in at.expander)


def test_whatsapp_simulator_replies_and_is_labelled():
    at = boot()
    at.button(key="btn_load_demo").click().run()
    at.sidebar.radio(key="nav").set_value("nav_channel").run()
    assert any("SIMULATOR" in w.value for w in at.warning)
    at.chat_input(key="wa_input").set_value("hi").run()
    assert not at.exception
    assert any("I never submit" in x.value for x in at.text)


def test_send_button_reports_not_configured_honestly():
    at = boot()
    at.sidebar.radio(key="nav").set_value("nav_tasks").run()
    at.text_input(key="tsk_title").set_value("Call bank")
    [b for b in at.button if b.label == "Add task"][0].click().run()
    at.sidebar.radio(key="nav").set_value("nav_channel").run()
    at.text_input(key="ch_phone").set_value("+910000000000")
    at.button(key="ch_send").click().run()
    assert not at.exception
    assert any("NOT_CONFIGURED" in w.value for w in at.warning)
