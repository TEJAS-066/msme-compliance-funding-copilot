"""Validate data/schemes.json and show which criteria rest on OFFICIAL vs secondary sources.
Run: python scripts/validate_catalogue.py   (exit 1 if invalid)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import catalogue as C  # noqa: E402

if __name__ == "__main__":
    import json
    with open(C.CATALOGUE_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    problems = C.validate(raw)
    if problems:
        print("INVALID catalogue:")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    print(f"catalogue {raw['catalogue_version']}: VALID  ({len(raw['schemes'])} schemes, {len(raw['sources'])} sources)\n")
    for r in C.coverage(raw):
        print(f"{r['scheme_id']}  [{r['review_status']}]  last verified {r['last_verified']}")
        print(f"   criteria: {r['criteria']}   official-backed: {len(r['official_backed'])}   secondary-only: {r['secondary_only'] or '-'}   unsourced: {r['unsourced'] or '-'}")
        print(f"   documents not verified from a source: {r['documents_unverified'] or '-'}")
    print("\nTo-do for the data owner: every 'secondary-only' criterion needs an official page, or a 'needs review' tag stays.")
