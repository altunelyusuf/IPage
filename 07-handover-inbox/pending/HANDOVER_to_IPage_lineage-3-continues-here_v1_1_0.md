# Hand-over to the IPage session: Lineage 3 continues here

Date: 2026-11-05. From the session that ran Lineage 3 until the move.

## The mission

"Build one stand-alone ontology of interactive pages, organised by kind, that carries the Owner's page rules, so that RDODI can use it to build and check its default page format." Decided by the Owner on 2026-11-04. On 2026-11-05 the Owner moved the work into this repository and a session of its own. The mission is unchanged.

## What is complete

| Piece of work | What is really true now | How to check |
|---|---|---|
| The page parts as one stand-alone ontology | 254 classes, each one connected to another | `measure_page_ontology_v2_1_0.py --metric A1a` reads 254; `--metric A1c` reads 0 |
| The page parts sorted into a tree of kinds | Ten kinds under one root, and no class without a parent other than the root | `--metric A1b` reads 1 |
| Quality standards tied to page parts | Ten standards and methods (WCAG 2.2 AA, Nielsen, Shneiderman, cognitive load theory, axe-core, pa11y, WAVE, WAI-ARIA, Inclusive Components, ISO/IEC 25010), each tied to the page parts it governs | `--metric A2` reads 10 |
| The Owner's 28 page rules | Each rule is recorded once, with the Owner's words as source, one of eleven page qualities and one kind of page part; a shape checks that each has exactly one of each | `--metric A3a` and `--metric A3b` read 28 |
| The move here | The ontology, the register (v0.42.0) and the tools are in this repository | `measure_ipage_home_v1_1_0.py` reads 4 once the move is released and recorded |

Each finished piece passed an independent overseer, a verifier working from a fresh clone, and a separate approver. Their records are in the register.

## What is open: your work, in order

1. **Turn each rule into a shape a page can be checked against.** Each shape names its rule with `ipo:forRule`. Objective A3c, target 28.
2. **Build the one browser measurement.** It reads a page against every rule at desktop and phone width and lists each rule as measured. Put it in `06-page-measure/measure_page_rules_v*.py`, with `--list-rules`. Objective A4b, target 28.
3. **Build the default page format from the ontology.** It is an `ipo:DefaultPageFormat` with `ipo:builtFrom` links, and a page `08-default-format/default_page_format*.html` that passes the measurement. Objectives A7a, A7b and the mission objective. Match the look of the existing RDODI, CME and VAF pages; do not invent a new look.
4. **Release every change through the one release path and measure again from a fresh clone.** Objective A9.
5. **Write the final hand-over** when the work is complete. Objective A10.

Five pieces left this lineage, because they change files outside this repository: the Stage 4 gate rows, the shipped pages, the profiles-to-pages map, and the course page (two pieces). The out-scoping declaration in the register names them. They are not yours. The out-scoping rests on the session's recommendation, accepted under the Owner's standing ruling that this session's recommendations are accepted by default, and the Owner was told before it was recorded. If the Owner reverses it, the five pieces come back through a change request.

## How to work here

Follow `04-documentation/SESSION_START_v1_0_1.md`: three clones side by side, both disciplines read fresh, the release check passing before any work, and every story started in the register before its files change.

## Known framework limits

- The date planner cannot compare naive and aware times. The forecast for the new objective was computed over a copy with the times read as UTC, and the forecast says so.
- The framework has no link from a scope change to the goals and objectives it introduces. We tie each such element to its scope change with `prov:wasDerivedFrom`, and the digest audit here sets it aside on that tie. Both limits have been handed to the framework: the first on 2026-11-04, the second on 2026-11-05.
