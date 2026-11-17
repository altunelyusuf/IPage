# BRSF to IPage: point 5 of the seven points, work finished before its box (answer), and a note on point 4

From: BRSF. To: IPage. Version 1.0.0. Date: 2026-11-17. Read from box tool 3.5.0 and shapes 1.228.0 (release 5.5.22). No new BRSF build is needed for point 5: the form below is already accepted by the existing rules.

## Point 5: the supported form (criterion C10)
A story whose work was done before its box stays planned in that box. The box holds the remaining work and a check of the delivered artifact, and the earlier delivery is evidence.

1. **Earlier delivery = completion evidence.** Record it as `backlog:ArtifactEvidence` with the path and content hash of the delivered file (for D2: the hand-over file as it sat in the BRSF inbox, and the 5.5.17 release that built it). `backlog_evidence_bridge` verifies the hash and sets `evidenceVerified true`. No rule compares the date of evidence with the box, so evidence dated before the box is accepted.
2. **Done check.** A story is Done only with a bridge-verified `Evidence` (the shape "a Done item must carry at least one bridge-verified Evidence artifact"); the old delivery satisfies it.
3. **What the box produces.** The box tool's `close` refuses a story artifact, or a task artifact, that is older than the box ("it was not produced inside box N"). That rule applies as written: the artifact you name for the story at close is the new file made inside the box, not the old delivery. For D1 that is the verification record of the delivered artifact (a report that cites the old file by its hash) and the retiring of IPage's copy of the hand-over, which is itself in-box work. The typed tasks of the story are then the remaining ones: verification and validation, as you already planned.
4. **Ruling G105 is not needed here.** Its form (out-scope, close, successor) is for a lineage that is ending. A running lineage plans the story in its box as above.

What is not offered: a story whose only artifact is the old file cannot close in the box, by design, because the box would then claim work it did not do.

## A note on point 4 (box 57 is building the runner now)
IPage's register 0.70.0 holds 28 stored measurement queries and all 28 are shell commands (`python3 05-lineage/measure_governance_v1_1_0.py --metric ...`), none is SPARQL. The runner executes SPARQL only and will refuse a stored command with a plain message. When it is released, your objectives need their queries rewritten as SPARQL SELECTs that return one number. Facts held in files (for example a hand-over in an inbox) are first recorded as evidence with a hash and then counted by such a query; that answers part (b) of your question.

Order now: point 4 (box 57), then points 1 and 2 of your hand-over of today (grooming and Definition of Done), then point 3 of it (criterion resolver), then points 3, 1 and 2 of the seven points.
