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
           + ["fnd_" + s for s in ("new", "match", "mismatch")] + ["q_format_validated", "q_label_match"]
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
