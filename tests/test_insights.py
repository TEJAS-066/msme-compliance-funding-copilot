import pytest

from core import eligibility as E
from core import insights as I
from core import profile as P
from core.catalogue import get_scheme


def test_unknown_impact_ranks_most_blocking_field_first(empty):
    imp = I.unknown_impact(empty)
    assert imp[0]["field"] == "activity" and imp[0]["criteria_count"] == 5
    assert set(imp[0]["schemes"]) == {"pmmy_mudra", "cgtmse", "pmegp"}


def test_unknown_impact_is_empty_when_nothing_blocks(demo):
    assert I.unknown_impact(demo) == []


def test_conditional_blocker_is_the_condition_field(demo):
    p = P.set_field(demo, "loan_needed_inr", 1_500_000)
    assert [d["field"] for d in I.unknown_impact(p)] == ["previous_tarun_repaid"]


def test_derived_class_blockers(empty):
    fields = {d["field"] for d in I.unknown_impact(empty)}
    assert {"investment_inr", "turnover_inr"} <= fields
    declared = P.set_field(empty, "enterprise_class_declared", "micro")
    fields2 = {d["field"] for d in I.unknown_impact(declared)}
    assert "investment_inr" not in fields2 and "turnover_inr" not in fields2


def test_tipping_points_come_from_catalogue():
    assert {1_000_000, 2_000_000, 100_000_000} <= set(I.tipping_points("loan_needed_inr"))
    assert I.tipping_points("investment_inr") == [25_000_000, 250_000_000, 1_250_000_000]
    assert I.tipping_points("employees") == []


def test_tipping_table_marks_real_changes(demo):
    rows = {r["at"]: r for r in I.tipping_table(demo, "loan_needed_inr")}
    assert rows[1_000_000]["changes"] == ["pmmy_mudra"]          # meets -> potentially (Tarun Plus rule starts)
    assert rows[2_000_000]["changes"] == ["pmmy_mudra"]          # PMMY cap
    assert rows[100_000_000]["changes"] == ["cgtmse"]            # Rs 10 crore
    assert rows[1_000_000]["status_after"]["pmmy_mudra"] == E.POTENTIAL


def test_tipping_table_does_not_mutate_profile(demo):
    import copy
    snap = copy.deepcopy(demo)
    I.tipping_table(demo, "loan_needed_inr")
    assert demo == snap


def test_counterfactuals_only_for_failures(demo):
    ok = E.evaluate_scheme(get_scheme("pmmy_mudra"), demo)
    assert I.counterfactuals(ok) == []
    bad = E.evaluate_scheme(get_scheme("pmmy_mudra"), P.set_field(demo, "loan_needed_inr", 2_500_000))
    cf = I.counterfactuals(bad)
    assert [c["criterion"] for c in cf] == ["loan_cap"] and cf[0]["op"] == "lte" and cf[0]["target"] == 2_000_000


def test_nba_load_profile_when_empty(empty):
    assert I.next_best_action(empty, set(), [])["kind"] == "load_profile"


def test_nba_answer_field_when_unknowns(demo):
    p = P.set_field(demo, "loan_needed_inr", 1_500_000)
    n = I.next_best_action(p, set(), [])
    assert n["kind"] == "answer_field" and n["field"] == "previous_tarun_repaid"


def test_nba_overdue_task_beats_everything(empty_with_one=None):
    p = P.set_field(P.empty_profile(), "state", "Tamil Nadu")
    n = I.next_best_action(p, set(), [{"title": "Old", "due_date": "2020-01-01", "status": "open"}])
    assert n == {"kind": "overdue", "title": "Old"}


def test_nba_upload_docs_then_prepare(demo):
    assert I.next_best_action(demo, set(), [])["kind"] == "upload_docs"
    done = {"lender_application_form", "udyam_certificate", "gst_certificate", "detailed_project_report", "category_certificate"}
    assert I.next_best_action(demo, done, [])["kind"] == "prepare"


def test_nba_review_inputs_when_all_unlikely(demo):
    p = P.set_field(demo, "activity", "agriculture")
    assert I.next_best_action(p, set(), [])["kind"] == "review_inputs"


def test_nba_ignores_done_and_future_tasks(demo):
    tasks = [{"title": "x", "due_date": "2020-01-01", "status": "done"}, {"title": "y", "due_date": "2999-01-01", "status": "open"}]
    assert I.next_best_action(demo, set(), tasks)["kind"] == "upload_docs"
