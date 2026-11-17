# IPage 1.19.2

Date: 2026-11-17. Lineage 4 (Governance): records only. Box 1's stories are groomed, and the lineage's Definition of Done is rewritten with checks that run.

- **Box 1's five stories groomed for box 1.** Each story declares the design concern it touches: the interface between sessions for the four hand-over stories, data for Lineage 2's records. Each has a refinement that names box 1 and records the typed tasks planned and what each does:
  - D1 (closing an epic): design, build, verification, validation.
  - D3 and D4 (two incoming hand-overs): analysis, build, verification, validation.
  - D2 (the archive tool) and D5 (Lineage 2 set down): verification and validation only, because their work was done before the box. How that earlier work is recorded waits on the framework's answer.
- **Acceptance criteria rewritten as what a reader sees.** Each names the artifact that satisfies it. None is measured any more by IPage's own measurement script, and each refinement keeps the old text. D2's criterion no longer says "three flaws": the hand-over named two and withdrew the third.
- **Definition of Done of Lineage 4 rewritten** with nine criteria, each with a check query or command, an expected result and its current status:
  - evidence exists, and a verifier is named;
  - the verifier is not the builder;
  - the story was groomed for its box before the box opened;
  - its story ran a verification and a validation task;
  - its criterion names its artifact, and no criterion is measured by a script of IPage's own;
  - the register validates with no violation;
  - IPage's release check passes.

  Each query criterion was tested by planting faults in a scratch copy, and each fired where it should. The old comment, which relied on IPage's own script, is replaced. Criterion 2's label is corrected to what its query checks (a verifier is named); independence is criterion 3.
- Register v0_71 -> v0_72. Under the framework's release 5.5.22: 0 violations. The new warning, a criterion read as a list of files on D3 and D4, is cleared by rewording. Every other warning was answered in 1.19.1.

## Handed over to the framework
`HANDOVER_ipage_to_backlog-roadmap-framework_box-tool-writes-its-own-grooming-and-done_v1_0_0.md`, in its own inbox. The box tool's `open` writes a fixed grooming text for every story, marks readiness met without checking it, and adds its own Definition of Done unless one is named in its own pattern. The framework's criterion resolution reads only its own register. Box 1 does not open until the first two are fixed, and until points 4 and 5 of the hand-over of 2026-11-16 are answered.

**Unplanned work:** the records in this release are the grooming and the Definition of Done of Lineage 4, made before box 1 opens. The Owner confirmed the work on 2026-11-17 at 16:02 Istanbul ("Fine proceed"), after the session recommended starting the grooming and the Definition of Done rewrite while the framework's answers are awaited.
