"""Create a DRAFT scheme record to fill from OFFICIAL text. Drafts live in data/drafts/ and are NEVER loaded by the app.
Run: python scripts/new_scheme.py --id pmegp --name "PMEGP"
Then: paste the official text into your AI tool with the prompt in docs/UPGRADE_PLAYBOOK.md (Phase B),
review every line yourself, then move the record into data/schemes.json and run scripts/validate_catalogue.py."""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True, help="stable id, lowercase letters/digits/_ only")
    ap.add_argument("--name", required=True)
    a = ap.parse_args()
    if not a.id.replace("_", "").isalnum() or a.id != a.id.lower():
        print("id must be lowercase letters/digits/underscore")
        return 1
    rec = {
        "id": a.id, "name": {"en": a.name, "ta": "TODO-native-review"}, "category": "TODO loan|subsidy|guarantee|registration",
        "description": {"en": "TODO one plain sentence, from the source", "ta": "TODO"}, "keywords": [a.id],
        "last_verified": "TODO-YYYY-MM-DD", "data_version": "0.1.0", "review_status": "unverified",
        "source_ids": ["TODO-add-to-sources-first"], "benefits": [],
        "criteria": [{"id": "TODO", "required": True, "label": {"en": "TODO", "ta": "TODO"}, "field": "TODO profile field",
                      "op": "eq|ne|in|not_in|lte|gte|lt|gt", "value": "TODO", "source_ids": ["TODO"]}],
        "documents": [], "unresolved": ["TODO list anything the source does not settle"],
        "_how_to_fill": "Every criterion needs source_ids that exist in 'sources'. Prefer official pages. Unknown => put it in 'unresolved'.",
    }
    d = os.path.join(ROOT, "data", "drafts")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{a.id}.json")
    if os.path.exists(path):
        print("draft already exists:", path)
        return 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    print("draft created:", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
