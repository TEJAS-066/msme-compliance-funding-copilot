import os
import re

from core import profile as P
from core.i18n import TR, field_label, option_label, t

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAMIL = re.compile("[\u0b80-\u0bff]")
FMT = re.compile(r"\{(\w+)\}")


def test_every_key_has_both_languages():
    for k, (en, ta) in TR.items():
        assert en.strip() and ta.strip(), k


def test_tamil_strings_contain_tamil_script():
    for k, (en, ta) in TR.items():
        assert TAMIL.search(ta), f"{k} has no Tamil text"


def test_placeholders_match_between_languages():
    for k, (en, ta) in TR.items():
        assert set(FMT.findall(en)) == set(FMT.findall(ta)), k


def _literal_keys():
    keys = set()
    for folder in ("ui", "services", "core", "app.py"):
        base = os.path.join(ROOT, folder)
        files = [base] if base.endswith(".py") else [os.path.join(base, f) for f in os.listdir(base) if f.endswith(".py")]
        for f in files:
            if f.endswith("i18n.py"):
                continue
            keys |= set(re.findall(r"""\bt\(\s*["']([a-z_0-9]+)["']\s*[,)]""", open(f, encoding="utf-8").read()))
    return keys


def test_every_literal_key_used_in_code_exists():
    missing = _literal_keys() - set(TR)
    assert not missing, missing


def test_dynamic_key_families_exist():
    fam = (["status_" + s for s in ("PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE")]
           + ["overall_" + s for s in ("meets_encoded", "potentially_eligible", "more_info_required", "unlikely_encoded")]
           + ["tier_" + s for s in ("shishu", "kishor", "tarun", "tarun_plus")]
           + ["doc_" + s for s in ("missing", "needs_review", "confirmed", "not_applicable")]
           + ["ext_" + s for s in ("text_extracted", "empty", "corrupt", "ocr_not_available", "unsupported", "skipped")]
           + ["up_accepted", "up_rejected", "conf_pending", "conf_confirmed", "conf_rejected"]
           + ["fnd_" + s for s in ("new", "match", "mismatch")] + ["q_format_validated", "q_label_match", "q_ocr_read"]
           + ["act_accept", "act_overwrite", "act_reject", "basis_declared", "basis_computed", "src_official", "src_secondary"]
           + ["rp_" + s for s in ("none", "in_app", "whatsapp_preview", "sms_preview")]
           + ["ts_" + s for s in ("open", "in_progress", "done")]
           + ["as_" + s for s in ("not_started", "preparing", "submitted_by_owner", "under_review", "approved", "rejected")]
           + [f"step_{i}" for i in range(1, 7)]
           + ["nav_" + s for s in ("dashboard", "profile", "documents", "schemes", "checklist", "copilot", "channel", "forms", "tasks", "admin")]
           + ["op_" + s for s in ("lte", "gte", "lt", "gt", "eq", "ne", "in", "not_in")]
           + ["nba_" + s for s in ("load_profile", "overdue", "answer_field", "upload_docs", "prepare", "review_inputs", "add_task")])
    assert [k for k in fam if k not in TR] == []


def test_every_profile_field_has_both_labels():
    for f, m in P.FIELDS.items():
        assert m["label"].get("en") and TAMIL.search(m["label"].get("ta", "")), f


def test_every_catalogue_text_has_tamil():
    from core.catalogue import get_catalogue
    for s in get_catalogue()["schemes"]:
        assert TAMIL.search(s["name"]["ta"]) and TAMIL.search(s["description"]["ta"]), s["id"]
        for b in s["benefits"]:
            assert TAMIL.search(b["text"]["ta"])
        for c in s["criteria"]:
            assert TAMIL.search(c["label"]["ta"]), c["id"]
        for d in s["documents"]:
            assert TAMIL.search(d["name"]["ta"]) and TAMIL.search(d["why"]["ta"])


def test_missing_key_is_visible_not_silent():
    assert t("definitely_missing", "en") == "[definitely_missing]"


def test_option_labels():
    assert option_label("activity", "manufacturing", "ta") == "உற்பத்தி"
    assert option_label("activity", "education_training", "en") == "Education Training"
    assert option_label("activity", "manufacturing", "hi") == "विनिर्माण"
    assert option_label("activity", "manufacturing", "te") == "ఉత్పత్తి"


HINDI = re.compile("[\u0900-\u097f]")
TELUGU = re.compile("[\u0c00-\u0c7f]")


def test_hindi_dictionary_present_and_valid():
    from core.i18n_hi import TR_HI
    assert len(TR_HI) == len(TR)
    for k, (en, _) in TR.items():
        assert k in TR_HI, f"Missing key in TR_HI: {k}"
        hi_text = TR_HI[k]
        assert set(FMT.findall(en)) == set(FMT.findall(hi_text)), f"Placeholder mismatch in Hindi for {k}"
        # If text is not just acronyms/numbers, it should have Hindi script
        if not re.match(r"^[\d\s\.\-—:\(\)\{\}A-Z_]+$", en):
            assert HINDI.search(hi_text), f"Key {k} has no Devanagari script: {hi_text}"


def test_telugu_dictionary_present_and_valid():
    from core.i18n_te import TR_TE
    assert len(TR_TE) == len(TR)
    for k, (en, _) in TR.items():
        assert k in TR_TE, f"Missing key in TR_TE: {k}"
        te_text = TR_TE[k]
        assert set(FMT.findall(en)) == set(FMT.findall(te_text)), f"Placeholder mismatch in Telugu for {k}"
        if not re.match(r"^[\d\s\.\-—:\(\)\{\}A-Z_]+$", en):
            assert TELUGU.search(te_text), f"Key {k} has no Telugu script: {te_text}"


def test_t_hindi_and_telugu_resolution():
    assert HINDI.search(t("app_title", "hi"))
    assert TELUGU.search(t("app_title", "te"))
    assert HINDI.search(t("mudra_tier_line", "hi", amount="₹50,000", tier="शिशु"))
    assert TELUGU.search(t("mudra_tier_line", "te", amount="₹50,000", tier="శిశు"))


def test_profile_field_labels_multilingual():
    for f in P.FIELDS:
        hi_lbl = field_label(f, "hi")
        te_lbl = field_label(f, "te")
        assert hi_lbl and te_lbl, f"Missing multilingual label for {f}"
        if f not in ("gstin", "udyam_number"):
            assert HINDI.search(hi_lbl), f"Field {f} missing Hindi script in label"
            assert TELUGU.search(te_lbl), f"Field {f} missing Telugu script in label"


def test_retrieval_intents_multilingual():
    from services.retrieval import detect_intent
    assert detect_intent("क्या मैं मुद्रा के लिए पात्र हूँ") == "eligibility"
    assert detect_intent("నాకు అర్హత ఉందా") == "eligibility"
    assert detect_intent("क्या दस्तावेज़ चाहिए") == "documents"
    assert detect_intent("ఏమి పత్రాలు కావాలి") == "documents"
