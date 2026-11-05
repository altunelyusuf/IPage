# Hand-over to the BRSF/lineage framework session: closing a decomposition parent has no honest path for an Epic

Date: 2026-11-05. From the IPage session, while finishing Story S5 ("Make each page rule a shape a page can be checked against", objective A3c).

## Where this was found

No real `07-handover-inbox` was reachable for the backlog-roadmap-framework repository from this session (the clone available here, `https://github.com/altunelyusuf/backlog-roadmap-framework`, is a public distribution mirror -- it carries a `.public-distribution-url` file and has no inbox folder). This is filed in IPage's own inbox as the stated fallback, addressed to whichever session governs BRSF, rather than left unfiled.

## The gap

Epic3_E1 decomposes into Story3_S1..S5. S1-S4 were already Done. Finishing S5 (this session's own work -- the ontology and SHACL shapes it adds are complete, verified, and committed; see commit `467bf0ee48a0fd75fb13185a0b281814d2779a93` in IPage) makes every one of Epic3_E1's children Done, which trips **G148** (`RS_DecompositionStateAgrees`): a parent whose children are all Done/Cancelled, with at least one Done, may not itself stay open.

G148's own message states the fix is mechanical: "either record the item as Done, or cancel it, or add the child that is still to come." Recording an Epic as Done is not actually that simple under this register's own further rules. A same-step attempt that only set `hasState Done` on Epic3_E1 (mirroring how a Story and its Task already close) immediately failed 18 further violations, all on Epic3_E1 itself: G109 (verifiedBy), G112/G113/G115 (flow points and status history: startedAt, a recorded move into InProgress, that move leaving Proposed), G118 (overseenBy/verifiedBy/approvedBy or human approval), G168/G172 (a readiness check, before a recorded start), L1 (a finish with no start), L2 (bridge-verified Evidence), L3 (an acceptance criterion with a real satisfying artifact, a derived test harness, `lastAuditedAt`, a refinement event addressing every applicable concern).

None of this exists for Epic3_E1, because nothing in this lineage's tooling ever carries an Epic through the same ceremony a Story goes through (start, readiness check, refinement, acceptance criterion, evidence, oversight/verification/approval). Fabricating these records for an Epic that was never itself built, reviewed or tested would be a false record, not a closure -- exactly what this discipline's own B3 and L3 rules exist to prevent.

## What is NOT done because of this

Story3_S5 is not yet recorded Done in IPage's register. Its real work -- the ontology and shapes -- is finished, independently verified, and committed. Only the register's own bookkeeping step is blocked, because `l3_steps finish S5` correctly refuses to leave a G148 violation behind (its validator check fails the run rather than silently writing a violating register).

## What this needs from the framework (or its Owner)

One of:
1. A defined, honest ceremony for closing a decomposition parent -- what evidence an Epic itself needs to be Done, scaled to what an Epic actually is (a grouping, not a thing built and tested on its own), so G148 can be satisfied truthfully; or
2. A ruling that G148 does not apply to `backlog:Epic` the same way it applies to a Story/Task (a different, lighter closure rule for pure containers); or
3. The Owner's decision to cancel Epic3_E1 instead of closing it Done, if "every child finished" is itself sufficient closure for this epic and no further epic-level artifact is wanted.

This is a stipulation (BP-D56/BP-D57's B2b distinction): no existing rule or evidence decides which of these is right, so it is not this session's call to make unilaterally. Recommendation, offered for the Owner's ruling: option 2, a lighter `EpicClosureShape` that only requires every child Done/Cancelled plus a stated closing note -- because an Epic is, by this register's own model, a grouping of stories rather than a work item with its own build-test-review cycle, and inventing that cycle for it after the fact would be exactly the "review evidence alone is insufficient" failure L3 itself warns against.

## How to verify this report

- `python3 05-lineage/l3_steps_v2_1_0.py finish S5 --measurement 05-lineage/l3_measurement_S5_v1_0_0.json --release-tag IPage-v1.3.3 --deployed <now> --validator <highest backlog_validate_v*.py> --run-times "Oversight=<t>,Verifier=<t>,Approver=<t>" --agents "Oversight=x,Verifier=y,Approver=z" --brief <sha256> --config-time <file with an earlier timestamp> --suffix S5` reproduces the 18 violations once Epic3_E1 is set to `hasState backlog:Done` with nothing else added (the code path is in the diff this session reverted; see commit history around `467bf0e`).
- `05-lineage/l3_measurement_S5_v1_0_0.json` carries the SHA-256 and commit of the verified ontology/shapes build this is otherwise blocking.
