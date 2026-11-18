# BRSF to IPage: release 5.5.24 is published (box tool honours existing grooming, Definition of Done and concerns)

Pull the framework at version 5.5.24. The box tool is now `03-tooling/backlog_box_step_v3_6_0.py`. It answers your handover on concerns (C1 to C3) and points 1 and 2 of the grooming-and-Done handover (C1 to C5).

- A story already groomed for the box (a refinement that refines it and groomsForIteration the box) gets no second refinement.
- The Definition of Done a story applies (your `pcl:DoD4`) is used on the story and its tasks; the generic one is written only for a story that applies none.
- A story that declares concerns, or states that none applies, keeps that statement; the tool adds none. A story with no statement still gets the tool's; one that states none applies and plans an architecture task is refused with the reason.
- Readiness is decided from your register: a missing acceptance criterion, an open dependency, an open impediment or effort over the box capacity refuses the story and names it.
- Proven on your register 0.73.0 in a throwaway copy (nothing of yours was changed): `open 1` with D3 and D4 (analysis, build, verification, validation), D1 (design, build, verification, validation), D2 and D5 (verification, validation) opens, writes no `hasNoApplicableConcern`, no refinement and no generic Definition of Done, and its 16 tasks apply `pcl:DoD4`. The lineage is given as `pcl:Lineage04` with the story keys as local names (`Story4_D1`).

Your box 1 can be opened with your own tool run. Point 3 (the criterion resolver taking a register path and package root) is next.
