import copy

import pytest

from core import eligibility as E
from core import profile as P
from core.catalogue import get_scheme


def crit(res, cid):
    return next(c for c in res.criteria if c.id == cid)


def test_demo_profile_meets_both(demo):
    r = E.evaluate_all(demo)
    assert r["pmmy_mudra"].overall == E.MEETS and r["cgtmse"].overall == E.MEETS


def test_missing_data_is_unknown_never_pass(empty):
    r = E.evaluate_all(empty)
    for res in r.values():
        assert all(c.status == E.UNKNOWN for c in res.criteria)
        assert res.overall == E.MORE_INFO


def test_fail_beats_unknown(empty):
    p = P.set_field(empty, "activity", "agriculture")
    res = E.evaluate_scheme(get_scheme("pmmy_mudra"), p)
    assert res.overall == E.UNLIKELY and crit(res, "nonfarm").status == E.FAIL


def test_conditional_criterion_not_applicable_when_condition_false(demo):
    res = E.evaluate_scheme(get_scheme("pmmy_mudra"), demo)        # loan 8 lakh
    assert crit(res, "tarun_plus_history").status == E.NA


def test_conditional_criterion_unknown_when_condition_unknown(empty):
    res = E.evaluate_scheme(get_scheme("pmmy_mudra"), empty)
    assert crit(res, "tarun_plus_history").status == E.UNKNOWN     # can't even tell if it applies


def test_conditional_criterion_applies_above_threshold(demo):
    p = P.set_field(demo, "loan_needed_inr", 1_500_000)
    res = E.evaluate_scheme(get_scheme("pmmy_mudra"), p)
    assert crit(res, "tarun_plus_history").status == E.UNKNOWN and res.overall == E.POTENTIAL
    assert "previous_tarun_repaid" in res.unknown_fields


def test_updating_profile_changes_result(demo):
    before = E.evaluate_all(demo)["cgtmse"].overall
    after = E.evaluate_all(P.set_field(demo, "activity", "agriculture"))["cgtmse"].overall
    assert before != after


@pytest.mark.parametrize("loan,expected", [(1_000_000, E.NA), (1_000_001, E.UNKNOWN)])
def test_tarun_plus_threshold_boundary(demo, loan, expected):
    p = P.set_field(demo, "loan_needed_inr", loan)
    assert crit(E.evaluate_scheme(get_scheme("pmmy_mudra"), p), "tarun_plus_history").status == expected


@pytest.mark.parametrize("loan,expected", [(2_000_000, E.PASS), (2_000_001, E.FAIL)])
def test_pmmy_cap_boundary(demo, loan, expected):
    p = P.set_field(demo, "loan_needed_inr", loan)
    assert crit(E.evaluate_scheme(get_scheme("pmmy_mudra"), p), "loan_cap").status == expected


def test_cgtmse_ten_crore_boundary(demo):
    ok = E.evaluate_scheme(get_scheme("cgtmse"), P.set_field(demo, "loan_needed_inr", 100_000_000))
    bad = E.evaluate_scheme(get_scheme("cgtmse"), P.set_field(demo, "loan_needed_inr", 100_000_001))
    assert crit(ok, "amount_cap").status == E.PASS and crit(bad, "amount_cap").status == E.FAIL


def test_medium_enterprise_fails_cgtmse(demo):
    p = P.set_field(P.set_field(demo, "investment_inr", 300_000_000), "turnover_inr", 500_000_000)
    assert crit(E.evaluate_scheme(get_scheme("cgtmse"), p), "size_mse").status == E.FAIL


def test_results_carry_sources_and_facts(demo):
    res = E.evaluate_scheme(get_scheme("cgtmse"), demo)
    assert res.source_ids and all(c.source_ids for c in res.criteria)
    assert res.facts_used["activity"] == "manufacturing"


def test_engine_does_not_mutate_profile(demo):
    snap = copy.deepcopy(demo)
    E.evaluate_all(demo)
    assert demo == snap


def test_unsupported_operator_raises():
    with pytest.raises(ValueError):
        E._compare("matches_regex", "a", "a")


def test_bad_type_comparison_becomes_unknown(demo):
    sc = copy.deepcopy(get_scheme("pmmy_mudra"))
    p = copy.deepcopy(demo)
    p["fields"]["loan_needed_inr"]["value"] = "not-a-number"
    assert crit(E.evaluate_scheme(sc, p), "loan_cap").status == E.UNKNOWN


@pytest.mark.parametrize("amt,tier", [(0, "shishu"), (50_000, "shishu"), (50_001, "kishor"), (500_000, "kishor"),
                                       (500_001, "tarun"), (1_000_000, "tarun"), (1_000_001, "tarun_plus"),
                                       (2_000_000, "tarun_plus"), (2_000_001, None), (None, None)])
def test_mudra_tiers(amt, tier):
    assert E.mudra_tier(amt) == tier
