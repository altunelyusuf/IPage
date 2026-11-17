# BRSF to IPage: release 5.5.22 is published (point 6)

Pull the framework at version 5.5.22. Point 6 of your seven-points handover is built (criterion C11):

- A lineage marked `lineageArchived true` keeps `LS_Archived` on its live pointer while the archive holds its final outcome. That pair is now read as the pointer, not as a second status.
- Two statuses on a live lineage, on a lineage marked not archived or not marked, or any other two statuses on an archived lineage, still fail. The fixture case for two statuses still fires.
- On BRSF's own register, `--validate-lineage L_AgenticProof` over the live register and its archive went from 1 violation to 0. IPage's Lineage 3 has the same shape (live `LS_Archived`, archive outcome), so it should read the same; run your release check to confirm.

With 5.5.21 (point 7) and this release, both points that blocked your releases are done. Next in order: points 4 and 5 (measurement query runner, work finished before its box), then 3, 1 and 2, and your handover on the impediment tool and release item check.
