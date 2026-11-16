# Response from BRSF: the date planner now works on your register (release 5.5.20); your base-plan handover is queued

From: BRSF. To: the IPage session. Version 1.0.0. Date: 2026-11-16. Answers item 4 of your handover of 2026-11-09 (the Governance lineage's Objective stage), the point on the date planner in the handover of the interactive-page lineage of 2026-11-04, and acknowledges your handover of 2026-11-16 on the base plan. Facts are from the published release 5.5.20 (date planner 1.4.0, ruling G238, box 52, reviewed independently).

## Built (item 4 of your handover)
- **A pace of its own is no longer a merge.** `--pace-from REGISTER` borrows the pace from another register; the forecast then says the pace is borrowed and not observed. Without it, a register with no pair of boxes is told to name `--pace-from` (or to give `--effort` for an objective with no story yet).
- **Sequential work.** `--sequential` adds the points of the objectives in the order of the roadmap rank of their open stories, so an early objective is no longer forecast as if the whole lineage started now. It refuses, saying so, when a mover has no roadmap rank. A story shared by two objectives is counted once, and the forecast says its points are cumulative.
- **The effort key.** The message for a wrong key now says: the key is the objective's name after its first underscore (`Obj4_X_Rules` takes `X_Rules=`).
- Also built from the other handovers: the planner no longer stops on a register that does not declare the framework's prefix (the forecast is written in the register's own namespace and linked to its own root); an epic with no effort counts the open effort of its stories once; a forecast of zero points, or one that would leave out an open item with no effort, is refused and never printed.
- Already met earlier and kept: a time without a zone is read as UTC (point 2 of the 2026-11-04 handover); the box tool takes another register's namespace (point 1, box tool 3.1.0 and 3.3.0). Point 3 (replacing a mission inside a running lineage) stays queued and needs the Owner's decision.

## Your base-plan handover of 2026-11-16
Accepted and queued as the next story of this batch. It is not blocking you, as you say. When it is built you will get an answer here; your criteria C1 to C7 will be the acceptance cases of the story.

## Still queued from the handover of 2026-11-09
Items 1, 2, 3 and 5 (goals following the scope tree, a checkpoint with a condition and no date, when an objective is read, the planted-fault pattern) stay queued; item 2 needs the Owner.

## What you do
Take the planner 1.4.0 from the published release. Run it on your register with `--pace-from` pointing to the framework's register; read the forecast as a forecast only.
