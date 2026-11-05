#!/usr/bin/env python3
"""digest_audit_v1_0_0.py - the closed stages of Lineage 3 still hold what they closed on.

  python3 digest_audit_v1_0_0.py REGISTER.ttl [Lineage03]

Recomputes each closed stage's digest (the framework's backlog_pipeline_verify state digest, scoped to the lineage) and compares it with the
digest the stage's output recorded. Set aside, and only these: execution tasks produced by planning; work items an owner-decided scope change
admits for an accepted request; and scope deliverables, goals and objectives such a change introduced after the stage closed, tied to it by
prov:wasDerivedFrom. Anything else added to or removed from a closed stage fails. Vendored from rdodi-ecosystem's lineage_disk_audit v1.6.0
(--digest) when Lineage 3 moved to IPage; its self-test runs there against the full register.
"""
import os, re, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
BRSF = os.environ.get("BRSF_ROOT") or next((d for d in (os.path.join(ROOT, "..", "backlog-roadmap-framework"), os.path.join(ROOT, "..", "ontologies", "backlog-roadmap-framework"), "/tmp/brsf") if os.path.isdir(os.path.join(d, "03-tooling"))), "")
B = "http://example.org/backlog#"
def _vk(p): return [int(x) for x in re.findall(r"\d+", os.path.basename(p).split("_v")[-1])]
def _pv():
    import glob, importlib.util
    fw = BRSF
    pvp = sorted(glob.glob(f"{fw}/03-tooling/backlog_pipeline_verify_v*.py"), key=_vk)[-1]; tbox = sorted(glob.glob(f"{fw}/01-ontologies/backlog_tbox_v*.ttl"), key=_vk)[-1]
    sp = importlib.util.spec_from_file_location("pv", pvp); pv = importlib.util.module_from_spec(sp); sp.loader.exec_module(pv); pv.STAGE_TYPES = pv._load_stage_types(tbox); return pv
def digest_check(g, lineage="Lineage01"):
    from rdflib import Graph, RDF, URIRef
    pv = _pv(); LN = next((s for s in g.subjects(RDF.type, URIRef(B + "Lineage")) if str(s).endswith("#" + lineage)), None)
    if LN is None: return False, [f"no lineage {lineage}"]
    other = {t for st in pv.ORDER for t in pv.STAGE_TYPES[st]} - {"ExecutionTask"}
    planned = {o for _, o in g.subject_objects(URIRef(B + "producesTask"))}
    tasks = {s for s in g.subjects(RDF.type, URIRef(B + "ExecutionTask")) if (s, URIRef(B + "belongsToLineage"), LN) in g and s in planned
             and not any((s, RDF.type, URIRef(B + t)) in g for t in other)}
    ownerd = [sc for sc in g.subjects(RDF.type, URIRef(B + "ScopeChange")) if (sc, URIRef(B + "decidedBy"), URIRef(B + "Owner")) in g
              and any((cr, RDF.type, URIRef(B + "ChangeRequest")) in g and (cr, URIRef(B + "hasDisposition"), URIRef(B + "Disp_Accepted")) in g for cr in g.objects(sc, URIRef(B + "fulfillsRequest")))]
    named = {o for sc in ownerd for o in g.objects(sc, URIRef(B + "admitsItem"))}
    off_stage = {t for st in pv.ORDER if st != "Stage_Backlog" for t in pv.STAGE_TYPES[st]}; in_backlog = set(pv.STAGE_TYPES["Stage_Backlog"]) - {"ExecutionTask"}
    admitted = {s for s in named if (s, URIRef(B + "belongsToLineage"), LN) in g and any((s, RDF.type, URIRef(B + t)) in g for t in in_backlog) and not any((s, RDF.type, URIRef(B + t)) in g for t in off_stage)}
    # v1.6.0: chain elements an owner-decided, accepted change introduced, tied to it by prov:wasDerivedFrom
    WDF = URIRef("http://www.w3.org/ns/prov#wasDerivedFrom")
    chain_types = {"ScopeDeliverable", "Goal", "Objective"}; work_types = set(pv.STAGE_TYPES["Stage_Backlog"]) - set(pv.STAGE_TYPES["Stage_Objective"])
    introduced = {s for sc in ownerd for s in g.subjects(WDF, sc) if (s, URIRef(B + "belongsToLineage"), LN) in g
                  and any((s, RDF.type, URIRef(B + t)) in g for t in chain_types) and not any((s, RDF.type, URIRef(B + t)) in g for t in work_types)}
    g2 = Graph()
    for t in g:
        if t[0] not in tasks and t[0] not in admitted and t[0] not in introduced: g2.add(t)
    msgs, ok, outs = [], True, {}
    for o in g.subjects(RDF.type, URIRef(B + "StageOutput")):
        if (o, URIRef(B + "belongsToLineage"), LN) in g: outs[str(g.value(o, URIRef(B + "outputOfStage"))).split("#")[-1]] = str(g.value(o, URIRef(B + "hasStateDigest")))
    for st in pv.ORDER:
        if st not in outs: msgs.append(f"{st}: no output recorded"); continue
        r = pv.state_digest(g2, st, LN) == outs[st]; ok &= r
        msgs.append(f"{st}: {'reproduces' if r else 'DOES NOT REPRODUCE'}" + (f" (with {len(tasks)} planned task(s) and {len(admitted)} owner-admitted item(s) set aside)" if st == "Stage_Backlog" else "")
                    + (f" ({len(introduced)} chain element(s) introduced by an owner-decided change set aside)" if introduced and st != "Stage_Backlog" else ""))
    return ok, msgs

if __name__ == "__main__":
    from rdflib import Graph
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    g = Graph(); g.parse(a[0], format="turtle"); ok, msgs = digest_check(g, a[1] if len(a) > 1 else "Lineage03")
    for m in msgs: print("  " + m)
    print("DIGEST AUDIT: " + ("PASS -- every closed stage reproduces" if ok else "FAIL -- a closed stage's state changed")); sys.exit(0 if ok else 1)
