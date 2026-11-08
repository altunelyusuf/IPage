# Session start: IPage

The work here is done by an agent session under two disciplines that live in other repositories. Read both fresh at every start; never use a remembered copy.

## 1. Clones, side by side

```
cd <work folder>
git clone https://github.com/altunelyusuf/IPage ipage
git clone https://github.com/altunelyusuf/Ontologies ontologies                    # not shallow: some figures read its history
git clone https://github.com/altunelyusuf/backlog-roadmap-framework backlog-roadmap-framework
pip install rdflib pyshacl --break-system-packages -q
```

The tools find the other two clones as sibling folders. Elsewhere, set `ONTOLOGIES_ROOT` and `BRSF_ROOT`.

## 2. The disciplines

- **OE Operating Discipline:** the highest version of `ontologies/oe-method/04-documentation/OE_Operating_Discipline_v*.md`, comparing the version numbers as integers.
- **Lineage Operating Discipline:** the highest version of `backlog-roadmap-framework/04-documentation/LINEAGE_OPERATING_DISCIPLINE_v*.md`, comparing the three numbers as integers.

Read both in full, state the file names and versions used, and follow them. If either cannot be reached, say so.

## 3. The state

```
cd ipage
python3 03-tooling/release_check_v1_1_0.py          # must PASS before any work
```

The register is the newest `05-lineage/interactive_page_lineage_abox_v*.ttl`. Its stories, their states and what moves each objective are the plan. The hand-over in `07-handover-inbox/pending` says what is done, what is open and how to check it.

## 4. Doing a story

Work reaches the register before it reaches a file.

1. **Start the story:** `python3 05-lineage/l3_steps_v2_5_0.py start SNN --report-tool ../backlog-roadmap-framework/03-tooling/backlog_roadmap_report_v*.py`. This writes the next register version.
2. **Build the work.**
3. **Review it:** an independent overseer reviews the work, a verifier re-runs the acceptance check from a fresh clone, and a separate approver decides.
4. **Measure it** into `05-lineage/l3_measurement_SNN_v1_0_0.json`, with the SHA-256 of the measured file and the commit.
5. **Record the finish:** `python3 05-lineage/l3_steps_v2_5_0.py finish SNN ...`.

Release with this sequence:

1. Run `python3 03-tooling/release_check_v1_1_0.py --write-manifest` until it passes.
2. Raise `VERSION.txt` and write `04-documentation/CHANGELOG_v<version>.md`.
3. Commit with the subject `IPage v<version>`.
4. Push, then tag `IPage-v<version>`. Where the environment cannot push tags, the commit subject and SHA identify the release; say so in the finish record.
5. Verify from a fresh clone.

## 5. Communication with the Owner

- Use plain language: what the piece is, what is really achieved, and what is next.
- Use human labels, not identifiers.
- Ask only when a decision is truly the Owner's, one point at a time, with an analysis and a recommendation.
