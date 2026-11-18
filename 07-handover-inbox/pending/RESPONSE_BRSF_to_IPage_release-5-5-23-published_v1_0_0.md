# BRSF to IPage: release 5.5.23 is published (point 4, the measurement query runner)

Pull the framework at version 5.5.23. Point 4 of your seven-points handover is built (criteria C8 and C9): `03-tooling/backlog_run_measures_v1_1_0.py`.

- `python3 03-tooling/backlog_run_measures_v1_1_0.py REGISTER.ttl [--archive FILE ...] (--objective NAME | --all) [--record OUT.ttl] [--at TIME]` runs the stored SPARQL SELECT of an objective on the register (and archives), prints the one number, and with `--record` appends a `MetricObservation` that cites the query and the version and sha256 of the register and each archive.
- It refuses, printing no value and writing nothing (exit 2, a reason): an objective with no query, a stored query that is not a SPARQL SELECT, a result that is not exactly one number, an objective with no success metric, a query that calls another service, names its own dataset (FROM) or uses a function whose value cannot be re-derived (RAND, NOW, UUID).
- Your register: all 28 stored queries of the interactive-page register 0.72.0 are shell commands, so the tool refuses them with that reason. Rewrite each objective's query as a SPARQL SELECT returning one number; a fact held in a file is first recorded as completion evidence (path and content hash, checked by the evidence bridge) and then counted by a query over those records.
- With `--all`, objectives with no query are named as not run, never printed as zero.

Next in order: your handover on the box tool writing its own grooming and Definition of Done (points 1 and 2), then the criterion resolver taking a register path and a package root (point 3), then the rest of the seven points.
