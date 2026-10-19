from core import forms as F
from core import profile as P


def test_worksheet_prefills_only_known_values(demo):
    rows = {r["key"]: r for r in F.prepare_worksheet(demo)}
    assert rows["state"]["value"] == "Tamil Nadu" and not rows["state"]["missing"]
    assert rows["udyam"]["missing"] and rows["udyam"]["value"] is None


def test_everything_missing_for_empty_profile(empty):
    assert all(r["missing"] for r in F.prepare_worksheet(empty))


def test_worksheet_text_says_not_official_and_not_submitted(demo):
    txt = F.worksheet_text(demo, "PMMY")
    assert "not an official form" in txt and "Nothing has been submitted" in txt and "MISSING" in txt


def test_worksheet_tamil(demo):
    assert "அதிகாரப்பூர்வ படிவம் அல்ல" in F.worksheet_text(demo, "PMMY", "ta")


def test_amounts_formatted_in_indian_grouping(demo):
    assert "₹8,00,000" in F.worksheet_text(demo, "PMMY")
