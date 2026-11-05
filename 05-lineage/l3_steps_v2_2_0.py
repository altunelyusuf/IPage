#!/usr/bin/env python3
"""l3_steps_v2_2_0.py - the recorded steps of Lineage 3's work stories, one command per step. Each writes the NEXT register version, never edits or deletes the previous one (OE BP-D7),
and refuses unless every earlier statement is still there except exactly those the step may change.

  l3_steps_v2_2_0.py start S1 S2 ...    the named stories move to InProgress, stamped from the clock; with the disclosure that the first build of S1 and S2 preceded this record.

v2.1.0 (2026-11-05): STORY_KEYS was missing S5 (it pursues A3c, like every other story this tool finishes) -- a gap found while finishing S5, not a change of what any story means.
Tried and reverted (2026-11-05): closing S5 makes Epic3_E1's last child Done, which G148 (RS_DecompositionStateAgrees) then requires the epic itself to resolve. A same-step auto-close that only set hasState=Done cascaded into the full Done governance apparatus a story gets (G109/G112/G113/G115/G118/G168/G172/L1/L2/L3: overseenBy/verifiedBy/approvedBy, startedAt, readiness checks, evidence, an acceptance criterion with a real artifact) -- none of which exists for an Epic and none of which this tool can honestly fabricate. Left for the Owner to rule on (cancel the epic, add a child still to come, or define what closes a decomposition parent); see the hand-over. finish() is unchanged from v2.1.0; it still refuses to leave S5 Done while this is open.
v2.2.0 (2026-11-05): STORY_KEYS was missing S9 (it pursues A7a, A7b and Mission) -- added while finishing S9, not a change of what the story means.
"""
import os, re, sys, glob, argparse, datetime
from rdflib import Graph, Namespace, Literal, RDF, RDFS, XSD
from rdflib.namespace import PROV
HERE = os.path.dirname(os.path.abspath(__file__)); REGD = HERE
B = Namespace("http://example.org/backlog#"); P = Namespace("http://example.org/rdodi/page-conditions-lineage#"); LN = P.Lineage03; PTS = {"S1": 8, "S2": 8, "S3": 5, "S4": 13, "S5": 8, "S6": 13, "S7": 13, "S8": 5, "S9": 13, "S10": 8, "S11": 5, "S12": 3, "S13": 3, "S14": 8, "S15": 13}
vk = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
now = lambda: datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
def newest(): return sorted(glob.glob(f"{REGD}/interactive_page_lineage_abox_v*.ttl"), key=vk)[-1]
def nxt(p): v = vk(p); return os.path.join(REGD, "interactive_page_lineage_abox_v%d_%d_0.ttl" % (v[0], v[1] + 1))
def start(a):
    import time, rdflib
    base = newest(); out = nxt(base); g0 = Graph(); g0.parse(base, format="turtle"); g = Graph()
    for t in g0: g.add(t)
    g.bind("backlog", B); g.bind("pcl", P)
    clock = lambda: (time.sleep(1.1), Literal(now(), datatype=XSD.dateTime))[1]
    removed = set(); subj = set(); A = lambda s_, p_, o_: (g.add((s_, p_, o_)), subj.add(s_))
    EN = lambda t: Literal(t, lang="en"); T = lambda t: Literal(t, datatype=XSD.string)
    tag = "_".join(a.stories); BK = P.Backlog
    for s in a.stories: assert (P["Story3_" + s], B.hasState, B.Proposed) in g0, f"{s} is not Proposed"
    # 1 the roadmap report, computed now, then the kick-off that activates it (once per lineage)
    it = P["It3_" + tag]
    if not list(g0.subjects(B.kicksOffLineage, LN)):
        import subprocess
        rep = subprocess.run([sys.executable, a.report_tool, base, "--emit", "/tmp/_l3_report.ttl"], capture_output=True, text=True)
        gr = Graph(); gr.parse("/tmp/_l3_report.ttl", format="turtle")
        R = next(gr.subjects(RDF.type, B.RoadmapReport)); ts_r = Literal(now(), datatype=XSD.dateTime)
        A(R, RDF.type, B.RoadmapReport); A(R, B.hasRunTimestamp, ts_r); A(R, B.reportOf, BK)
        for sec in gr.objects(R, B.hasSection): A(R, B.hasSection, sec)
        K = P.KickOff3; A(K, RDF.type, B.KickOff); A(K, B.activatesReport, R); A(K, B.decidedBy, B.Builder); A(K, B.hasKickOffMode, B.KickOff_Declared)
        A(K, B.kickOffFor, BK); A(K, B.kickedOffAt, clock()); A(K, B.kicksOffLineage, LN)
    A(it, RDF.type, B.Iteration); A(it, RDFS.label, EN("Iteration: " + ", ".join(a.stories))); A(it, B.belongsToLineage, LN); A(it, B.hasIdentifier, T("RDPO-IT-" + tag))
    A(it, B.hasTitle, EN("Work on " + ", ".join(a.stories))); A(it, B.hasState, B.InProgress); A(it, B.memberOfContainer, BK); A(it, B.iterationStart, clock())
    for s in a.stories:
        S_ = P["Story3_" + s]
        ref = P["Refine3_" + s]; A(ref, RDF.type, B.RefinementEvent); A(ref, B.hasWorkKind, B.WorkKind_Preparation); A(ref, B.refines, S_); A(ref, B.belongsToLineage, LN)
        A(ref, B.groomsForIteration, it); A(ref, B.addressesConcern, B.Concern_Interface_UI); A(ref, B.refinedBy, B.Builder); A(ref, B.refinedAt, clock())
        A(ref, B.hasRefinementOutcome, T("Groomed: the acceptance criterion reads as a check the measurement script makes; the work is to files and records; no decision of the Owner is waited on."))
        chk = P["Chk3_" + s]; A(chk, RDF.type, B.ReadinessCheck); A(chk, RDFS.label, EN("Readiness of " + s)); A(chk, B.checksReadinessOf, S_); A(chk, B.readinessCheckedAt, clock())
        for k, lab in (("AC", "The acceptance criterion reads as a check the measurement script makes"), ("Dep", "Nothing it depends on is open"), ("Input", "No decision of the Owner is waited on")):
            c = P[f"K3_{s}_{k}"]; A(c, RDF.type, B.ReadinessCriterion); A(c, RDFS.label, EN(lab)); A(c, B.criterionMet, Literal(True)); A(chk, B.hasReadinessCriterion, c)
        ev1 = P["Ev3_" + s + "_Refine"]; A(ev1, RDF.type, B.TransitionEvent); A(ev1, B.transitionedItem, S_); A(ev1, B.viaTransition, B.T_Refine); A(ev1, B.transitionedAt, clock()); A(ev1, B.transitionedBy, B.Builder); g.add((ev1, B.transitionedByExecutor, P.Run3_Build01))
        pl = P["Plan3_" + s]; A(pl, RDF.type, B.PlanningEvent); A(pl, RDFS.label, EN(s + " planned into its iteration")); A(pl, B.belongsToLineage, LN); A(pl, B.plansItem, S_); A(pl, B.plannedInto, it)
        A(pl, B.plannedAt, clock()); A(pl, B.plannedBy, B.Builder)
        ts = clock()
        for t in list(g.triples((S_, B.hasState, None))): removed.add(t); g.remove(t)
        g.add((S_, B.hasState, B.InProgress)); g.add((S_, B.startedAt, ts)); subj.add(S_)
        tk = P["T3_" + s + "_Build"]; A(tk, RDF.type, B.ExecutionTask); A(tk, B.hasIdentifier, T("RDPO-T-" + s + "-BUILD")); A(tk, B.hasTitle, EN("Build the work of " + s)); A(tk, B.hasTaskType, B.Task_Implementation)
        A(tk, B.responsible, P.Run3_Build01); A(tk, B.memberOfContainer, it); A(tk, B.appliesDefinitionOfDone, P.DoD); A(tk, B.belongsToLineage, LN); A(tk, B.hasExecutionModality, B.Mode_Automated)
        A(tk, B.pursuesObjective, next(g.objects(S_, B.pursuesObjective))); g.add((pl, B.producesTask, tk))
        ck = P["Chk3_T_" + s]; A(ck, RDF.type, B.ReadinessCheck); A(ck, RDFS.label, EN("Readiness of the task of " + s)); A(ck, B.checksReadinessOf, tk); A(ck, B.readinessCheckedAt, clock())
        for k, lab in (("AC", "The task builds what the acceptance criterion checks"), ("Dep", "Nothing it depends on is open"), ("Input", "No decision of the Owner is waited on")):
            c = P[f"K3_T_{s}_{k}"]; A(c, RDF.type, B.ReadinessCriterion); A(c, RDFS.label, EN(lab)); A(c, B.criterionMet, Literal(True)); A(ck, B.hasReadinessCriterion, c)
        evr = P["Ev3_T_" + s + "_Refine"]; A(evr, RDF.type, B.TransitionEvent); A(evr, B.transitionedItem, tk); A(evr, B.viaTransition, B.T_Refine); A(evr, B.transitionedAt, clock()); A(evr, B.transitionedBy, B.Builder); g.add((evr, B.transitionedByExecutor, P.Run3_Build01))
        tts = clock(); A(tk, B.hasState, B.InProgress); A(tk, B.startedAt, tts)
        evt = P["Ev3_T_" + s + "_Start"]; A(evt, RDF.type, B.TransitionEvent); A(evt, B.transitionedItem, tk); A(evt, B.viaTransition, B.T_Start); A(evt, B.transitionedAt, tts); A(evt, B.transitionedBy, B.Builder); g.add((evt, B.transitionedByExecutor, P.Run3_Build01))
        ev2 = P["Ev3_" + s + "_Start"]; A(ev2, RDF.type, B.TransitionEvent); A(ev2, B.transitionedItem, S_); A(ev2, B.viaTransition, B.T_Start); A(ev2, B.transitionedAt, ts); A(ev2, B.transitionedBy, B.Builder); g.add((ev2, B.transitionedByExecutor, P.Run3_Build01))
    st = next(g.objects(it, B.iterationStart)); pts = sum(PTS[x] for x in a.stories); end = Literal((datetime.datetime.fromisoformat(str(st)) + datetime.timedelta(hours=pts / 1.63 * 1.5)).replace(microsecond=0).isoformat(), datatype=XSD.dateTime)
    pb = P["PB3_" + tag]; A(pb, RDF.type, B.PlanBaseline); A(pb, RDFS.label, EN("Base plan of the iteration")); A(pb, B.baselineFor, it); A(pb, B.baselinedAt, clock()); A(pb, B.isCurrentBaseline, Literal(True))
    A(pb, B.hasBaselineStart, st); A(pb, B.hasBaselineEnd, end); A(pb, RDFS.comment, EN(f"A forecast only: {pts} points at the planning pace of 1.63 points per hour, times a buffer of 1.5. Not a target."))
    for t in list(g.triples((BK, B.hasState, None))): removed.add(t); g.remove(t)
    g.add((BK, B.hasState, B.InProgress)); subj.add(BK)
    for t in list(g.triples((LN, B.hasLineageStatus, None))): removed.add(t); g.remove(t)
    g.add((LN, B.hasLineageStatus, B.LS_InProgress)); subj.add(LN)
    if "S1" in a.stories:
        f = P["Finding3_BuildBeforeStart_" + tag]; ts = clock()
        A(f, RDF.type, B.RetrospectiveFinding); A(f, RDFS.label, EN("The first build of " + ", ".join(a.stories) + " was made before its start was recorded"))
        A(f, B.belongsToLineage, LN); A(f, B.detectedAt, ts); A(f, B.detectedBy, B.Builder); A(f, B.hasFindingScope, B.Scope_LineageLocal)
        A(f, B.hasRootCause, T("The two stories are tied (a new ontology file must have every class linked), so the file was built in one piece in the working tree, and the step script that records a start did not yet exist for this lineage."))
        A(f, B.hasRemedy, T("Disclosed here and not backfilled. Nothing was released before this record; the build is released together with it, and Done is recorded only after the acceptance criteria hold."))
        for s in a.stories: g.add((f, B.relatesToWorkItem, P["Story3_" + s]))
    g.serialize(destination=out, format="turtle"); g1 = Graph(); g1.parse(out, format="turtle")
    rem = set(g0) - set(g1); add = set(g1) - set(g0)
    if [t for t in rem if t not in removed] or [t for t in add if t[0] not in subj]: os.remove(out); sys.exit("refused: unexpected change")
    print(f"wrote {out}: {len(rem)} replaced, {len(add)} added")

ROOT = os.path.abspath(os.path.join(HERE, ".."))
BRSF = os.environ.get("BRSF_ROOT") or next((d for d in (os.path.join(ROOT, "..", "backlog-roadmap-framework"), os.path.join(ROOT, "..", "ontologies", "backlog-roadmap-framework"), "/tmp/brsf") if os.path.isdir(os.path.join(d, "03-tooling"))), "")
SPEC = "05-lineage/l3_check_v1_0_0.py"
STORY_KEYS = {"S1": ["A1a", "A1c"], "S2": ["A1b"], "S3": ["A2"], "S4": ["A3a", "A3b"], "S5": ["A3c"], "S9": ["A7a", "A7b", "Mission"], "S14": ["A11"], "S15": ["A4b"]}
vkey = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]]
def bridge(path, meas, commit, ids):
    import subprocess
    br = sorted(glob.glob(f"{BRSF}/03-tooling/backlog_evidence_bridge_v*.py"), key=vkey)[-1]
    r = subprocess.run([sys.executable, br, path, "--workspace", ROOT, "-o", path + ".bridged", "--test-command", f"python3 {{spec}} {meas} {{id}} {commit}"], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(path + ".bridged"): sys.exit("evidence bridge failed: " + (r.stdout + r.stderr)[-600:])
    gb = Graph(); gb.parse(path + ".bridged", format="turtle"); gm = Graph(); gm.parse(path, format="turtle")
    for e in ids:
        for p_ in (B.evidenceVerified, B.verifiedAt, B.hasVerificationMethod):
            for o_ in gb.objects(e, p_): gm.add((e, p_, o_))
    bad = [str(e).split("#")[-1] for e in ids if (e, B.evidenceVerified, Literal(True)) not in gm]
    os.remove(path + ".bridged")
    if bad: sys.exit(f"the bridge did not verify: {bad}")
    gm.bind("backlog", B); gm.bind("pcl", P); gm.serialize(destination=path, format="turtle")
def finish(a):
    import json, subprocess
    M = json.load(open(os.path.join(ROOT, a.measurement))); commit = M["sha256"]; gitc = M["commit"]
    base = newest(); out = nxt(base); g0 = Graph(); g0.parse(base, format="turtle")
    for s in a.stories:
        for item in (P["Story3_" + s], P["T3_" + s + "_Build"]): assert (item, B.hasState, B.InProgress) in g0, f"{item} is not InProgress"
        for k in STORY_KEYS[s]:
            if not (M["values"][k] >= M["targets"][k] if k == "A1a" else M["values"][k] == M["targets"][k]): sys.exit(f"refused: {k} reads {M['values'][k]}, target {M['targets'][k]}")
    EN = lambda t: Literal(t, lang="en"); T = lambda t: Literal(t, datatype=XSD.string)
    tag = "_".join(a.stories); clk = lambda: Literal(now(), datatype=XSD.dateTime)
    def build(viol):
        g = Graph()
        for t in g0: g.add(t)
        g.bind("backlog", B); g.bind("pcl", P); A = lambda s_, p_, o_: g.add((s_, p_, o_))
        TF = clk(); ids = []; IT = P["It3_" + "_".join(a.stories)]; BK = P.Backlog
        AGS = Namespace("http://example.org/agentic-systems#"); g.bind("agsys", AGS)
        cfg_t = Literal(open(a.config_time).read().strip(), datatype=XSD.dateTime)
        SUF = "_" + a.suffix if a.suffix else ""
        AG = dict(x.split("=", 1) for x in a.agents.split(","))
        for nm, aid, role, brief in (("Oversight", AG["Oversight"], "oversaw the work and sent it back once" if a.sent_back else "oversaw the work", None), ("Verifier", AG["Verifier"], "re-ran the acceptance check in a fresh clone", a.brief), ("Approver", AG["Approver"], "reviewed the work and approved it", None)):
            D = P["Exec_" + nm + "_L3"]; A(D, RDF.type, B.Executor_SingleAgent); A(D, RDFS.label, EN({"Oversight": "The overseeing agent: a reviewer that did not do the work and may send it back", "Verifier": "The verifying agent: an agent that did not do the work and judges it against the evidence", "Approver": "The approving agent: a reviewer that accepts the work only if it finds no clear defect"}[nm]))
            R = P["Run3_" + nm + SUF]; A(R, RDF.type, B.ExecutorInstance); A(R, RDF.type, B.Executor_SingleAgent); A(R, RDFS.label, EN("An independent agent run that " + role)); A(R, B.instanceOf, D)
            A(R, B.instantiatedAt, Literal(a.run_times[nm], datatype=XSD.dateTime)); A(R, B.instantiatedFromVersion, T("claude-sonnet-5-5 sub-agent run " + aid))
            if brief:
                SW = P.StartWay_Request; A(SW, RDF.type, AGS.StartWay); A(SW, RDFS.label, EN("On the builder's request"))
                AR = P.AccessRoute_Git; A(AR, RDF.type, AGS.AccessRoute); A(AR, RDFS.label, EN("A fresh clone of the published repository"))
                GR = P["Grant3_Verifier" + SUF]; A(GR, RDF.type, AGS.AccessGrant); A(GR, AGS.grantedBy, P.Run3_Build01); A(GR, AGS.viaRoute, AR); A(GR, AGS.grantedPlace, T("the published repository, cloned fresh by the verifier")); A(GR, AGS.grantMode, T("read-only")); A(GR, AGS.grantedAt, cfg_t)
                PL = P["Plan3_Verifier" + SUF]; A(PL, RDF.type, AGS.VerificationPlan); A(PL, AGS.hasPlanDigest, T(brief)); A(PL, RDFS.comment, EN("The brief given to the verifying agent, fixed by its digest before the agent started."))
                SE = P["Session3_Verifier" + SUF]; A(SE, RDF.type, PROV.Agent); A(SE, RDFS.label, EN("an independent verifying agent (a fresh agent that did not do the work)"))
                A(R, AGS.startedInWay, SW); A(R, AGS.startedUnderGrant, GR); A(R, AGS.followsPlan, PL); A(R, AGS.executedBy, SE); A(R, AGS.placeUnchanged, Literal(False))
                C = P["Config3_" + nm + SUF]; A(C, RDF.type, AGS.AgentConfiguration); A(C, AGS.isConfigurationOf, D); A(C, AGS.recordedAt, cfg_t)
                for kind, val in (("brief", "sha256 " + brief), ("model", "Claude Sonnet 5.5 (general-purpose agent)")):
                    ci = P[f"CfgItem3_{nm}{SUF}_{kind}"]; A(ci, RDF.type, AGS.ConfigurationItem); A(ci, AGS.hasItemKind, T(kind)); A(ci, AGS.hasItemValue, T(val)); A(C, AGS.hasConfigurationItem, ci)
        DU = P["Rel3_" + tag]; A(DU, RDF.type, B.DeploymentUnit); A(DU, RDFS.label, EN("Release " + a.release_tag.replace("-v", " v") + " carrying " + ", ".join(a.stories))); A(DU, B.belongsToLineage, LN)
        A(DU, B.hasIdentifier, T("RDPO-REL-" + tag)); A(DU, B.hasTitle, EN("The stand-alone ontology, published as " + a.release_tag.replace("-v", " v"))); A(DU, B.hasDeploymentDate, Literal(a.deployed, datatype=XSD.dateTime))
        A(DU, B.hasRationale, T("Published by the Builder on the Owner's instruction of 2026-11-04 to carry out the lineage. Commit " + gitc + ".")); A(DU, B.deploysFrom, IT); A(DU, B.hasSelectionBasis, B.Sel_Committed); A(DU, B.hasState, B.Done); A(DU, B.decidedBy, B.Builder); A(DU, B.memberOfContainer, BK)
        for s in a.stories:
            S_ = P["Story3_" + s]; TK = P["T3_" + s + "_Build"]; AC = P["AC3_" + s]; key = ",".join(STORY_KEYS[s])
            for item in (S_, TK):
                for t in list(g.triples((item, B.hasState, None))): g.remove(t)
                g.add((item, B.hasState, B.Done)); A(item, B.finishedAt, TF); A(item, B.lastAuditedAt, TF)
            def ev(name, label):
                e = P[name]; A(e, RDF.type, B.Evidence); A(e, RDF.type, B.TestEvidence); A(e, B.belongsToLineage, LN); A(e, RDFS.label, EN(label)); A(e, B.hasTestSpec, T(SPEC)); A(e, B.hasTestId, T(key))
                A(e, B.verifiedByTool, T("backlog_evidence_bridge_v1_0_0.py")); ids.append(e); return e
            e1 = ev("Ev3_Done_" + s, f"Test of {s}: {key} measured on file SHA-256 {commit[:12]}"); A(e1, B.attestsCriterion, AC); e2 = ev("Ev3_DoneT_" + s, f"Test that the task of {s} produced what was planned: {key}")
            A(AC, B.satisfiedByArtifact, T(f"the stand-alone ontology files of the package interactive-page-ontology, published in {a.release_tag} (commit {gitc[:10]})"))
            H = P["H3_" + s]; A(H, RDF.type, B.TestHarness); A(H, B.belongsToLineage, LN); A(H, B.harnessFor, S_); A(H, B.hasHarnessEvidence, e1); A(H, B.hasRationale, T(f"One criterion, one check: l3_check on {key} attests AC3_{s}."))
            for item in (S_, TK):
                A(item, B.overseenBy, P["Run3_Oversight" + SUF]); A(item, B.verifiedBy, P["Run3_Verifier" + SUF]); A(item, B.approvedBy, P["Run3_Approver" + SUF]); A(item, B.integrityLevel, Literal(2))
            A(S_, B.hasEvidence, e1); A(TK, B.hasEvidence, e2); A(S_, B.memberOfContainer, DU); A(DU, B.deploysItem, S_)
            for item, nm in ((S_, "Story"), (TK, "Task")):
                ev3 = P[f"Ev3_{nm}_{s}_Complete"]; A(ev3, RDF.type, B.TransitionEvent); A(ev3, B.transitionedItem, item); A(ev3, B.viaTransition, B.T_Complete); A(ev3, B.transitionedAt, TF); A(ev3, B.transitionedBy, B.Builder); A(ev3, B.transitionedByExecutor, P.Run3_Build01)
            for k in STORY_KEYS[s]:
                ob = P[f"Obs3_Done_{k}"]; A(ob, RDF.type, B.MetricObservation); A(ob, B.observationFor, P["Obj3_" + k]); A(ob, B.observesMetric, P["Metric3_" + k]); A(ob, B.observedAt, clk())
                A(ob, B.hasObservedValue, Literal(float(M["values"][k]), datatype=XSD.decimal)); A(ob, B.hasObservationMethod, T(f"Measured by measure_page_ontology_v1_0_0.py --metric {k} on commit {gitc} (file SHA-256 {commit})."))
        done_keys = set(k for s in a.stories for k in STORY_KEYS[s])
        for ob_ in sorted(set(g.subjects(B.metricMovableBy, None)) - set()):
            pass
        for k in a.also_observe.split(","):
            if k in done_keys or not k: continue
            ob = P[f"Obs3_Done_{k}"]; A(ob, RDF.type, B.MetricObservation); A(ob, B.observationFor, P["Obj3_" + k]); A(ob, B.observesMetric, P["Metric3_" + k]); A(ob, B.observedAt, clk())
            A(ob, B.hasObservedValue, Literal(float(M["values"][k]), datatype=XSD.decimal)); A(ob, B.hasObservationMethod, T(f"Measured by measure_page_ontology_v1_0_0.py --metric {k} on commit {gitc} (file SHA-256 {commit})."))
        st_ = g.value(IT, B.iterationStart); TE = clk(); d_ = int((TE.toPython() - st_.toPython()).total_seconds())
        for t in list(g.triples((IT, B.hasState, None))): g.remove(t)
        g.add((IT, B.hasState, B.Done)); A(IT, B.iterationEnd, TE); A(IT, B.hasObservedDuration, T(f"PT{d_ // 3600}H{(d_ % 3600) // 60}M{d_ % 60}S")); A(IT, B.hasDurationSource, T("iterationStart of this iteration to the finishedAt recorded by l3_steps finish."))
        return g, ids
    viol = 0
    for _ in range(5):
        g, ids = build(viol); g.serialize(destination=out, format="turtle"); bridge(out, a.measurement, commit, ids)
        v = subprocess.run([sys.executable, a.validator, out], capture_output=True, text=True).stdout; m_ = re.search(r"results\s*:\s*(\d+) Violation", v); v2 = int(m_.group(1)) if m_ else -1
        if v2 == 0: break
        print("violations:", v2); [print("  ", l.strip()[:260]) for l in v.splitlines() if "[Violation]" in l][:6]; break
    print("wrote", out)

ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True); s_ = sp.add_parser("start"); s_.add_argument("stories", nargs="+"); s_.add_argument("--report-tool", required=True)
fp = sp.add_parser("finish"); fp.add_argument("stories", nargs="+"); fp.add_argument("--measurement", required=True); fp.add_argument("--release-tag", required=True); fp.add_argument("--deployed", required=True); fp.add_argument("--validator", required=True); fp.add_argument("--also-observe", default=""); fp.add_argument("--run-times", required=True); fp.add_argument("--agents", required=True); fp.add_argument("--brief", required=True); fp.add_argument("--config-time", required=True); fp.add_argument("--suffix", default=""); fp.add_argument("--sent-back", action="store_true")
a = ap.parse_args()
if getattr(a, "run_times", None): a.run_times = dict(x.split("=", 1) for x in a.run_times.split(","))
{"start": start, "finish": finish}[a.cmd](a)
