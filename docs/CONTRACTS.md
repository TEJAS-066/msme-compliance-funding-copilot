# Data contracts (change only with team agreement — tests depend on these)

## Profile (`core/profile.py`)
`{"fields": {<name>: {"value": any|None, "status": "known"|"unknown", "source": "user"|"demo"|"document:<file>"|None}}, "is_demo": bool}`
Read ONLY via `profile.get(p, field)` (returns None unless known). Write ONLY via `profile.set_field` (returns a new dict).

## Scheme record (`data/schemes.json`)
`id, name{en,ta}, category, description{en,ta}, keywords[], last_verified(YYYY-MM-DD), data_version, review_status, source_ids[], benefits[{text{en,ta}, source_ids}], criteria[{id, required, label{en,ta}, field, op, value, applies_if?, source_ids[], note?}], documents[{id, doc_type, verified, applies_if?, name, why, source_ids}], unresolved[]`
ops: `eq ne in not_in lte gte lt gt`. `field` may be `enterprise_class` (derived).
`review_status` in {verified_official, partly_verified_official} => scheme is evaluated and shown. Anything else => backlog only.

## Eligibility result (`core/eligibility.py`)
`SchemeResult{scheme_id, overall in {meets_encoded, potentially_eligible, more_info_required, unlikely_encoded}, criteria[CriterionResult{id,label,status in PASS|FAIL|UNKNOWN|NOT_APPLICABLE, field, profile_value, op, target, required, source_ids, note}], unknown_fields[], facts_used{}, source_ids[]}`

## Document extraction (`core/documents.py`)
`ExtractionResult{upload_status accepted|rejected, extraction_status text_extracted|empty|corrupt|ocr_not_available|unsupported|skipped, text, message}` → `Candidate{field,value,match_quality format_validated|label_match,note}` → `Finding{field,proposed,current,kind new|match|mismatch,advisory}`.
Confirmation is per document in SQLite (`pending|confirmed|rejected`); profile changes only via `apply_decisions`.

## Copilot (`services/copilot.py`)
`answer(question, lang, profile, confirmed_types, cat=None, use_llm=True) -> Answer{text, lang, mode demo_deterministic|llm:<provider>|demo_fallback, sources[{id,title,url,tier,accessed}], refused, scheme_ids, notes[]}`

## Notifications status vocabulary
`PREVIEW_ONLY | NOT_CONFIGURED | SENT | FAILED` — SENT only on a confirmed provider acceptance.

## Insights (`core/insights.py`) — all deterministic
`unknown_impact(profile) -> [{field, criteria_count, schemes[], criteria[]}]` (sorted by blocked criteria)
`tipping_table(profile, field) -> [{at, status_at{}, status_after{}, changes[]}]` — thresholds come from the catalogue
`counterfactuals(SchemeResult) -> [{criterion, field, op, target, your_value}]` — restates the rule only
`next_best_action(profile, confirmed, tasks) -> {kind: load_profile|overdue|answer_field|upload_docs|prepare|review_inputs|add_task, ...}`

## Alerts (`services/alerts.py`)
`build_alerts(profile, confirmed, documents, tasks, approved_updates, lang) -> [Alert{kind, severity action|warn|info, text}]`; `whatsapp_preview(alert, lang)` never sends.

## Copilot trace
`Answer.trace = [{agent, detail}]` — one entry per module that touched the answer (Retrieval, Eligibility, Composer/LLM, Guard, Citations, Refusal).

## Webhook (`services/whatsapp.py`)
`handle_webhook(form, header_sig, url, profile, confirmed, env) -> (status, content_type, body)`. 403 unless signature valid (token set) or `WA_ALLOW_UNSIGNED=1`.

## Monitor (`services/monitoring.py`)
`scan_sources(cat, get, hashes) -> {hashes, changes[], baseline[], errors[]}`; changes become PENDING `SOURCE_CHANGED` queue items; only admin-approved items are notifiable.
