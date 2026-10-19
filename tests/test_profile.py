import pytest

from core import profile as P


def test_empty_profile_is_all_unknown(empty):
    assert all(f["status"] == "unknown" for f in empty["fields"].values())


def test_set_field_marks_known_and_is_immutable(empty):
    p2 = P.set_field(empty, "state", "Tamil Nadu")
    assert P.get(p2, "state") == "Tamil Nadu"
    assert P.get(empty, "state") is None          # original untouched


def test_blank_value_returns_to_unknown(demo):
    p2 = P.set_field(demo, "district", "")
    assert P.get(p2, "district") is None and p2["fields"]["district"]["status"] == "unknown"


def test_invalid_inputs_rejected(empty):
    with pytest.raises(ValueError):
        P.set_field(empty, "activity", "teleportation")
    with pytest.raises(ValueError):
        P.set_field(empty, "investment_inr", -5)
    with pytest.raises(ValueError):
        P.set_field(empty, "turnover_inr", "abc")
    with pytest.raises(KeyError):
        P.set_field(empty, "nope", 1)


@pytest.mark.parametrize("inv,turn,expected", [
    (25_000_000, 100_000_000, "micro"),        # exactly at both micro limits
    (25_000_001, 100_000_000, "small"),        # investment just over
    (25_000_000, 100_000_001, "small"),        # turnover just over
    (250_000_000, 1_000_000_000, "small"),
    (250_000_001, 1_000_000_000, "medium"),
    (1_250_000_000, 5_000_000_000, "medium"),
    (1_250_000_001, 5_000_000_000, "large"),
    (0, 0, "micro"),
])
def test_classification_boundaries(inv, turn, expected):
    assert P.compute_class(inv, turn) == expected


def test_declared_class_wins_and_mismatch_is_flagged(demo):
    p = P.set_field(demo, "enterprise_class_declared", "small")
    assert P.enterprise_class(p) == ("small", "declared")
    assert P.class_mismatch(p) == "micro"


def test_class_unknown_when_numbers_missing(empty):
    assert P.enterprise_class(empty) == (None, None)
    p = P.set_field(empty, "investment_inr", 1000)       # only one of the two numbers
    assert P.enterprise_class(p) == (None, None)


def test_editing_identity_clears_demo_flag(demo):
    assert demo["is_demo"] is True
    assert P.set_field(demo, "business_name", "My Real Unit")["is_demo"] is False


def test_fmt_inr_indian_grouping():
    assert P.fmt_inr(800000) == "₹8,00,000"
    assert P.fmt_inr(100000000) == "₹10,00,00,000"
    assert P.fmt_inr(999) == "₹999"
    assert P.fmt_inr(None) == "-"
