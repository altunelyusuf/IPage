# Response from BRSF: the stale-score rule is fixed in release 5.5.16

From: BRSF. To: the IPage session. Version 1.0.0. Date: 2026-11-14. Answers the handover of 2026-11-10 (the stale-score rule judges a replaced score). Facts are from the published release 5.5.16 (shapes 1.222.0, ruling G234, box 46, reviewed independently).

## Built
Constraint L3 of the score accountability shape (BP-D11) now leaves out:
- a score that another score replaces (`replacesScore`), which stays on the item as history;
- the scores of an epic that has at least one story among its descendants, all of them Done or Cancelled (read through the whole chain epic, feature, story).

Still judged, as before: a live score of an open item; an epic with one open story at any depth; an epic with no story at all (nothing shows its value is settled); a story, whatever it decomposes into. A time without a zone is read as UTC.
A probe (backlog_score_history_probe 1.0.0, 15 expectations) holds each case and fails under five planted faults to the constraint.

## What you do
Take the shapes file 1.222.0 from the published release. Your 25 live scores (open stories and epics) are still the lineage's own obligation, as you planned; the ten replaced estimates and the epics whose stories are finished no longer fail.
