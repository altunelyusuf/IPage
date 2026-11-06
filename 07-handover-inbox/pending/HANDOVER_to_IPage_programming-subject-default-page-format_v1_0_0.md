# Hand-over to the IPage session: should a "programming subject" profile name its own page format?

Date: 2026-11-06. From the rdodi-ecosystem session.

## Where this was found

A hand-over sits in `rdodi-ecosystem/07-handover-inbox/deferred/HANDOVER_sen0414_to_RDODI_programming-profile-default-page_v1_0_0.md` (filed 2026-10-01 by the SEN0414 course session), asking RDODI to adopt its course page template as the default Stage-4 page for "a programming subject: research plus documentation where the reader must run the claims." RDODI's own gap register (`01-profiles/RDODI_PROFILE_AND_PAGE_GAPS_v1_0_0.md`, gaps C3/C4) and two of RDODI's own lineages (Lineage02, Lineage03 -- both now abandoned) each excluded the decision from their scope, each time with the same note: "not part of the mission ... for a later decision." No lineage ever opened to decide it.

Re-checked today, fresh, not from memory: the course repository (`altunelyusuf/AdvancedProgrammingWithPython`) has since released the template well past the work-in-progress commit the hand-over cited -- `main` now carries `course_page_template_v9_53_2.html` under tags up to `sen0414-v2.44.0`. The template itself is no longer unreleased.

## Why this is IPage's question, not RDODI's

This repository's own mission and README state that the ontology exists "so that RDODI can use it to build and check its default page format," and `08-default-format/default_page_format_v1_0_0.html` is described as the page "every new course page starts from **unless its own profile names a different one**." Deciding whether a profile may name its own page format, and whether this course page qualifies, is that same decision -- a page-format-per-profile question inside the page ontology this repository now owns. RDODI's own ruling (Owner, 2026-11-05, recorded in rdodi-ecosystem's `CR3_Move`) is to consume what is published here, not to carry a standing backlog deciding page formats itself. I have not asked RDODI's session to build or decide any part of this.

## The proposal, as the course session stated it

A profile for "research plus documentation where the reader must run the claims," whose page: runs every example with the real interpreter at build time and again in-browser (Pyodide); shows the subject as one connected tree, an ontology graph, a class diagram and an ERD, each diagram with zoom that never covers it; gives each subject-slice its own answering agent; offers a practice side (quiz, exercises, mock exam, spaced review) and a lab (editor, tracer, code pipeline, SPARQL console); and a reference/About side. Full detail, measured evidence (0 FAIL across 23 chapters, headless Chromium, phone and desktop widths, WCAG 2 A/AA) and stated limits are in the original hand-over, still in rdodi-ecosystem's inbox at the path above -- not copied here in full to avoid two copies of the same record.

Two things it still lacks, found and recorded by RDODI (not yet decided anywhere):
- No vocabulary slot exists for "an executed example" or for the syntax/behaviour of a language construct -- today the course keeps these as plain ABox annotations rather than a modelled kind of page content. If this repository's own page-part ontology is where such a content kind belongs (a page part fed by an executed example), that is this session's call, not RDODI's.
- The course page's graded-exam layer is course-specific and would need to ship off by default if a generic profile adopted this template.

## What this hand-over asks

Nothing is asked to be built from this filing alone. It asks only that this session decide, when it next touches the default-page-format mission: does a "programming research-and-documentation" page format belong here (as a second named format alongside the generic default, or as a profile-named variant of it), and if so, what of the above (the executed-example content kind in particular) is this ontology's concern versus RDODI's own document-generation vocabulary. RDODI's gap register and the two abandoned lineages that parked this question are cited above so the decision isn't made from a second-hand summary.

## Not asked

This session's own files are not edited by this filing; the log row is this session's to write. No student data is in this hand-over or referenced by path.
