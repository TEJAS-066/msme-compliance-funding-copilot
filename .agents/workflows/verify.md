---
description: Run the full verification report (tests, KPIs, catalogue sources, secret scan, risky claims) and summarise it for the reviewer.
---
# Verify the current state

1. Run `python scripts/verify_phase.py --phase <current-phase>` and show the full report.
2. If anything FAILS, fix only that, rerun, and show the new report. Never weaken a test to pass.
3. Write a 10-line summary: what changed, what the report proves, what it does NOT prove, and what a human must still check by eye.
4. Output the review request template from docs/UPGRADE_PLAYBOOK.md filled with real values.
