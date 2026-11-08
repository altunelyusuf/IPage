# Handover to IPage: a page's version should say what changed in that page, not which template release built it

Date: 2026-11-08. From: a course-management session. To: IPage. Kind: finding with measured evidence and a proposal; nothing here changes an IPage file.

## What the owner said

A file's version should not affect the version number of another file. A chapter's file must not continue from a number that another chapter's file reached. The owner asked for a correct version management.

## What was measured (read from the course repositories, 2026-11-08)

- The page builder's own header says a page's version is the template, data and builder versions together (for example "page version 9.90.0 and later = template 9.52.1 + data 2.25.0 + builder 4.18.0").
- The consequence: one template release gives every chapter a new page number, whether or not that chapter's content changed. One course's chapter 7 page went 9.41.0, 9.64.0, 9.76.0, 9.84.0, 9.85.0, and its neighbouring chapter's page sits at 9.86.0 beside it. In the second course, chapter 8 is at 9.92.1, chapter 10 at 9.95.0 and chapter 11 at 9.96.0.
- The OEE rule on the size of a version bump says a file's number tells a user how much changed in that file, that a released file is never renumbered, and that the rule applies from each file's next release.

## Proposal

1. A page's file name carries its own version, continuing from its own predecessor, with the step sized by the change to that page (a corrected wording is a patch, an added section or feature is a minor step, a removed or renamed part is a major step).
2. The template, data and builder versions used to build a page are recorded inside the page as inputs (provenance), and are not counted in its number.
3. A template release that changes nothing in a chapter's content produces no new page for that chapter.
4. No released page is renamed. The new line starts from each page's own last version.

## What is not decided here

Which of the template's own numbers (the 9.x series) stay as the template's version: that is yours. The check that enforces the rule on course files is being built on the course-management side and reads only the file series, so it does not depend on your answer.
