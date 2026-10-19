"""Scheduled source monitor.  Run daily from CI (see .github/workflows/monitor.yml) or by hand.

First run records a baseline. Later runs add a PENDING item to data/review_queue.json for every changed
source. Nothing reaches an owner until an admin approves it in the app.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services import monitoring as M  # noqa: E402

if __name__ == "__main__":
    old = {}
    if os.path.exists(M.HASHES_PATH):
        with open(M.HASHES_PATH, encoding="utf-8") as f:
            old = json.load(f)
    res = M.scan_sources(hashes=old)
    with open(M.HASHES_PATH, "w", encoding="utf-8") as f:
        json.dump(res["hashes"], f, indent=2)
    added = M.append_queue(M.changes_to_queue_items(res["changes"]))
    print(f"baseline: {len(res['baseline'])} · changed: {len(res['changes'])} (queued {added}) · errors: {len(res['errors'])}")
    for e in res["errors"]:
        print("  error", e)
