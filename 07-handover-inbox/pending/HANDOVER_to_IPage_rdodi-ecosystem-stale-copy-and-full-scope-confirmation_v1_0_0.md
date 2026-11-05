# Hand-over to the IPage session: rdodi-ecosystem's own copy is stale, and the Owner confirms full scope transfer

Date: 2026-11-05. From the rdodi-ecosystem session, after the Owner reviewed the 2026-11-05 move of Lineage 3.

## The Owner's ruling this carries

On 2026-11-05 the Owner said the IPage scope is to be **totally** transferred to this repository and session — not partly kept on rdodi-ecosystem's own agenda waiting for a lineage, as an earlier report to the Owner suggested. This hand-over, and the removal it describes, is how rdodi-ecosystem is acting on that.

## What was checked, and what it found

rdodi-ecosystem's own merged T-Box (`01-stage-vocabularies/rdodi_ecosystem_tbox_v1_12_2.ttl`) still carries a copy of the interactive-page vocabulary under the `ipo:` prefix, consolidated into it as a module (BP-D54) before Lineage 3 moved here. It was checked against this repository's current ontology (`01-ontologies/interactive_page_ontology_tbox_v1_3_0.ttl`), fresh-cloned at commit `bda758474c29a7865eb958decfa4cb161cf60bd7`:

- rdodi-ecosystem's embedded copy: 238 classes.
- This repository's current ontology: 256 classes.
- Every one of rdodi-ecosystem's 238 classes, matched by local name, is present here.

**Finding: nothing is missing here. rdodi-ecosystem's copy is a stale, superseded snapshot; this repository's own, independently-verified ontology already covers it and has grown past it.** No action is asked of this session on the ontology's content.

## What rdodi-ecosystem still has to do, and the one open question

Before rdodi-ecosystem can remove its stale copy, four properties of its own vocabulary (not `ipo:`-prefixed) declare their domain or range as `ipo:InteractiveHTMLSurface`: `producesSurface`, `recordForPage`, `forSurface`, `predatesSelectionRule`. Removing the local copy leaves these four pointing at a class defined only in this separate repository — a cross-repository reference the structure and connectedness checks were not built to recognize (their "a term declared by another package is a dependency, not a gap" exemption assumes the dependency sits in the same governance clone, which IPage no longer does, now that it is its own repository).

This is a stipulation for the Owner, not something either session's rules already settle, so rdodi-ecosystem is asking the Owner before touching its own files further. It is recorded here so this repository's own session has the full picture and is not asked to do anything about it — the fix, whatever the Owner decides, is rdodi-ecosystem's own file change.

## Verification performed

- `measure_page_ontology` class count and rdodi-ecosystem's own `grep`/rdflib count were cross-checked directly against both fresh-cloned repositories in the same session, not asserted from an earlier turn.
- The class-name comparison above was run with rdflib against both T-Box files as they stand at the commits named.
