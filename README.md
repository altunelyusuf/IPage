# IPage: Interactive HTML pages

One stand-alone ontology of interactive pages, organised by kind, that carries the Owner's page rules, so that RDODI can use it to build and check its default page format.

This was the mission of Lineage 3, decided by the Owner on 2026-11-04. On 2026-11-05 the Owner moved the work out of RDODI's agenda into this repository and a session of its own. RDODI now uses what is published here.

On 2026-11-08 the Owner ruled that IPage is run as the lineage framework now runs a package: one Governance lineage that looks after how IPage's lineages live, and narrow Delivery lineages that build the product, each planned in packages. Lineages 2 and 3 are concluded and set down in the archive; Lineage 3's unfinished work is carried forward to the new lineages.

## What is here

| Folder | Holds |
|---|---|
| `01-ontologies` | the T-Box (257 classes under one root, sorted into ten kinds of page part, plus the governance vocabulary for rule-check results, plus the default page format class) and the A-Box: ten quality standards and methods tied to the page parts they govern, eleven page qualities, the Owner's 28 page rules each with its source instruction, its quality and its kind of page part, and the one default page format individual |
| `02-shacl-safeguards` | the shapes: every class is labelled, every standard applies to a page part, every rule has one source, one quality and one kind of part, every rule has a shape to check a page against (the reviews of 2026-11-08 found these shapes do not yet refuse a page in the project's own checks; the repair is carried forward), and every rule-check result names its rule, its viewport and its evidence |
| `03-tooling` | the release check every release passes |
| `04-documentation` | the changelogs and the session start guide |
| `05-lineage` | the register of IPage's lineages and its tools: the step script that records starts, finishes, withdrawals and the closing of a lineage, the check that attests a story, the measurement scripts, the evidence and digest audits, and the extraction that carried the register here |
| `06-page-measure` | the one browser measurement: reads a page against every one of the Owner's 28 rules at desktop and phone width |
| `07-handover-inbox` | hand-overs to the session that works here (`pending`, then `accepted`) |
| `08-default-format` | the one default page format every new course page starts from unless its profile names its own, built from the ontology and measured to pass every one of the 28 rules |

## Where it came from

Versions 1.0.0 to 1.2.1 of the ontology were published in the Ontologies monorepo as the package `interactive-page-ontology`. That copy is frozen and points here. Lineage 3's register up to version 0.39.0 is in RDODI's register (`rdodi-ecosystem/28-interactive-html-surface/13-overview-lineage-register`), which keeps the whole history. Version 0.40.0 here carried every statement of Lineage 3 unchanged, and the lineage writes only here from now on.

## Starting a session

Read `04-documentation/SESSION_START_v1_0_9.md`.

## Licences

The repository is under the Apache License 2.0 (`LICENSE`). The ontology files state their own licence, CC BY 4.0, in their headers.
