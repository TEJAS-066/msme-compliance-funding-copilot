import copy

import pytest

from core import catalogue as C


def test_shipped_catalogue_is_valid():
    assert C.validate(C.get_catalogue()) == []


def test_every_verified_scheme_has_sources_and_date():
    for s in C.list_schemes():
        assert s["source_ids"] and s["last_verified"]


def test_unsourced_criterion_is_rejected():
    cat = copy.deepcopy(C.get_catalogue())
    cat["schemes"][0]["criteria"][0]["source_ids"] = []
    assert any("unsourced" in p for p in C.validate(cat))


def test_unknown_source_reference_is_rejected():
    cat = copy.deepcopy(C.get_catalogue())
    cat["schemes"][0]["source_ids"].append("does_not_exist")
    assert any("unknown source" in p for p in C.validate(cat))


def test_verified_document_requires_source():
    cat = copy.deepcopy(C.get_catalogue())
    cat["schemes"][0]["documents"][0]["source_ids"] = []
    assert any("verified but has no source" in p for p in C.validate(cat))


def test_bad_date_is_rejected():
    cat = copy.deepcopy(C.get_catalogue())
    cat["schemes"][0]["last_verified"] = "18/10/2026"
    assert any("last_verified" in p for p in C.validate(cat))


def test_unverified_backlog_is_never_listed_as_a_scheme():
    ids = {s["id"] for s in C.list_schemes()}
    assert not ids & {b["id"] for b in C.unverified_backlog()}


def test_localisation_falls_back_to_english():
    assert C.L({"en": "x"}, "ta") == "x"
    assert C.L(None, "ta") == ""
