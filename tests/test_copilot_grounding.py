import pytest

from core import profile as P
from core.catalogue import get_catalogue, get_source
from services import copilot, llm
from services.retrieval import detect_intent, retrieve


def test_eligibility_answer_uses_rules_engine_and_cites_catalogue(demo):
    a = copilot.answer("Am I eligible for MUDRA?", "en", demo)
    assert a.mode == "demo_deterministic" and not a.refused
    assert "Meets the criteria we have encoded" in a.text
    assert "not an approval" in a.text
    cat = get_catalogue()
    assert a.sources and all(s["url"] == get_source(s["id"], cat)["url"] for s in a.sources)   # real catalogue metadata only


def test_unknown_data_is_reported_not_assumed(demo):
    p = P.set_field(demo, "loan_needed_inr", 1_500_000)
    a = copilot.answer("Am I eligible for MUDRA?", "en", p)
    assert "Potentially eligible" in a.text and "repayment history" in a.text


def test_never_says_approved_or_guaranteed(demo):
    for q in ("Am I eligible for MUDRA?", "Am I eligible for CGTMSE?", "what can I get?"):
        low = copilot.answer(q, "en", demo).text.lower()
        assert "guaranteed funding" not in low and "you are approved" not in low


def test_out_of_scope_question_is_refused_not_invented(demo):
    a = copilot.answer("What is the GST rate on garments?", "en", demo)
    assert a.refused and "cannot find" in a.text


def test_unverified_scheme_gets_no_facts(demo):
    a = copilot.answer("Tell me about PMEGP subsidy", "en", demo)
    assert a.refused and "not verified" in a.text.lower() or "have not verified" in a.text
    assert "lakh" not in a.text.lower() and "%" not in a.text


def test_deadline_question_does_not_invent_a_date(demo):
    a = copilot.answer("What is the last date for MUDRA application?", "en", demo)
    assert "do not have a verified" in a.text
    import re
    assert not re.search(r"\b20\d\d\b", a.text)


def test_tamil_question_gets_tamil_answer(demo):
    a = copilot.answer("எனக்கு MUDRA தகுதி உள்ளதா?", "ta", demo)
    assert a.lang == "ta" and any("\u0b80" <= ch <= "\u0bff" for ch in a.text)
    assert "நாங்கள் குறியிட்ட" in a.text


def test_documents_intent_marks_unverified_items(demo):
    a = copilot.answer("What documents do I need for CGTMSE?", "en", demo)
    assert "not confirmed from a scheme source" in a.text


def test_amount_intent_quotes_catalogue_benefits(demo):
    a = copilot.answer("What is the MUDRA loan limit?", "en", demo)
    assert "Tarun Plus" in a.text and "20" in a.text


def test_empty_question():
    a = copilot.answer("   ", "en", P.empty_profile())
    assert a.refused


def test_unknown_language_falls_back_to_english(demo):
    assert copilot.answer("Am I eligible for MUDRA?", "fr", demo).lang == "en"


def test_empty_profile_still_answers_without_crashing(empty):
    a = copilot.answer("what can I get?", "en", empty)
    assert "More information required" in a.text


def test_intent_detection():
    assert detect_intent("what documents do I need") == "documents"
    assert detect_intent("random words") == "unknown"
    assert retrieve("tell me about cgtmse")["scheme_ids"] == ["cgtmse"]


# ---------------- LLM guard ----------------
CTX = {"schemes": [{"limit": "Rs 20 lakh", "x": 2000000}], "when": "2026-10-18"}


def test_guard_accepts_numbers_from_context():
    assert copilot.guard("The cap is Rs 20 lakh.", CTX) == []


def test_guard_blocks_invented_numbers():
    assert any("number not in verified" in p for p in copilot.guard("You can get Rs 50 lakh.", CTX))


def test_guard_blocks_banned_phrases():
    assert copilot.guard("Funding is guaranteed.", CTX)


def test_llm_answer_used_when_it_passes_guard(demo, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic"); monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    a = copilot.answer("Am I eligible for MUDRA?", "en", demo, _llm_complete=lambda s, u, p: "You appear to meet the encoded rules for MUDRA.")
    assert a.mode == "llm:anthropic" and a.sources            # sources always come from the catalogue


def test_llm_answer_with_invented_number_falls_back(demo, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic"); monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    a = copilot.answer("Am I eligible for MUDRA?", "en", demo, _llm_complete=lambda s, u, p: "You can borrow Rs 77 lakh at 3.5% interest.")
    assert a.mode == "demo_fallback" and "Meets the criteria we have encoded" in a.text
    assert any("rejected by guard" in n for n in a.notes)


def test_llm_failure_falls_back(demo, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini"); monkeypatch.setenv("GEMINI_API_KEY", "k")
    def boom(s, u, p): raise llm.LLMError("network down")
    a = copilot.answer("Am I eligible for MUDRA?", "en", demo, _llm_complete=boom)
    assert a.mode == "demo_fallback" and a.text and any("unavailable" in n for n in a.notes)


def test_llm_never_called_for_refusals(demo, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic"); monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    def must_not_call(s, u, p): raise AssertionError("LLM called for an out-of-scope question")
    a = copilot.answer("What is the GST rate on garments?", "en", demo, _llm_complete=must_not_call)
    assert a.refused and a.mode == "demo_deterministic"


def test_prompt_contains_rules_engine_status(demo, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic"); monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    seen = {}
    def spy(system, user, p): seen["user"] = user; return "ok"
    copilot.answer("Am I eligible for MUDRA?", "en", demo, _llm_complete=spy)
    assert "overall_status_from_rules_engine" in seen["user"] and "meets_encoded" in seen["user"]


def test_no_key_means_demo_mode(demo):
    assert llm.get_provider() is None
    assert copilot.answer("Am I eligible for MUDRA?", "en", demo).mode == "demo_deterministic"
