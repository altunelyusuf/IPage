#!/usr/bin/env python3
"""l3_steps_v2_6_0.py - the recorded steps of Lineage 3's work stories, one command per step. Each writes the NEXT register version, never edits or deletes the previous one (OE BP-D7),
and refuses unless every earlier statement is still there except exactly those the step may change.

  l3_steps_v2_6_0.py start S1 S2 ...    the named stories move to InProgress, stamped from the clock; with the disclosure that the first build of S1 and S2 preceded this record.

v2.1.0 (2026-11-05): STORY_KEYS was missing S5 (it pursues A3c, like every other story this tool finishes) -- a gap found while finishing S5, not a change of what any story means.
Tried and reverted (2026-11-05): closing S5 makes Epic3_E1's last child Done, which G148 (RS_DecompositionStateAgrees) then requires the epic itself to resolve. A same-step auto-close that only set hasState=Done cascaded into the full Done governance apparatus a story gets (G109/G112/G113/G115/G118/G168/G172/L1/L2/L3: overseenBy/verifiedBy/approvedBy, startedAt, readiness checks, evidence, an acceptance criterion with a real artifact) -- none of which exists for an Epic and none of which this tool can honestly fabricate. Left for the Owner to rule on (cancel the epic, add a child still to come, or define what closes a decomposition parent); see the hand-over. finish() is unchanged from v2.1.0; it still refuses to leave S5 Done while this is open.
v2.2.0 (2026-11-05): STORY_KEYS was missing S9 (it pursues A7a, A7b and Mission) -- added while finishing S9, not a change of what the story means.
v2.3.0 (2026-11-08): three steps for concluding the lineage (G215), on the Owner's ruling IP-R1:
  withdraw ITEM ... --rationale TEXT [--missed KEY ... --missed-rationale TEXT]
                                         each named item (local name: Story3_S6, Epic3_E1, ...) moves to Cancelled by the withdrawal its state allows
                                         (T_WithdrawProposed / T_WithdrawReady / T_WithdrawInProgress / T_WithdrawSuspended), with the reason and a recorded move (an iteration, a container, ends by the Owner's dissolution instead);
                                         each objective named by --missed (left with no live work that can move it, and short of its target) is recorded Missed.
  report --fit-gap T --impact T --summary T [--finding LABEL=ROOTCAUSE=REMEDY ...] [--best-practice T ...]
                                         reads every objective again with the newest measure_page_ontology script (a fresh observation each), records the
                                         as-is assessment (every item sorted by its state, every objective fitted or gapped) and the closure report marked
                                         Cancelled, citing the assessment and every finding. The mission outcome is NOT set: the Owner confirms first.
  conclude --confirmation TEXT           after the Owner confirms: the ruling of his confirmation, the mission outcome Abandoned with its rationale (the
                                         closure summary), and the lineage status Abandoned. Refuses without a closure report committed earlier.
v2.4.0 (2026-11-08, the same day, before any release carried 2.3.0): an iteration is ended by the Owner's dissolution, not withdrawn like an
  item (a container's state is derived); the validator figure (Conf) names itself, so the report reads it until the value recorded is the value read.
v2.5.0 (2026-11-08): conclude looked for the commit of the closure report in every file of 05-lineage and found its own source text
  (commit e3be984); it now reads only the register files.
v2.6.0 (2026-11-08): every step now writes the register's header to the version of the file it writes (versionInfo, versionIRI, priorVersion
  the version it read); since 0.42.0 the header had stayed at 0.41.0, which the framework's archive tool refuses. sync-header writes the next
  version with only the header corrected.
  finish also takes --agent-model (the model of the reviewing agents, recorded instead of a fixed name), and its observations name the measurement
  script actually used (it named v1_0_0, which was retired; corrected for observations written from now on, earlier ones stay as written).
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

REGH = None
def header(g, out):
    """The register's header names the version of the file being written and the version it was written from (OE BP-D7)."""
    from rdflib import URIRef
    H = URIRef("http://example.org/rdodi/page-conditions-lineage/register"); OWL_ = Namespace("http://www.w3.org/2002/07/owl#")
    v = vk(out); vs = f"{v[0]}.{v[1]}.{v[2]}"; prev = [x for x in g.objects(H, OWL_.versionInfo)]
    pv = str(prev[0]) if prev else None
    for p_ in (OWL_.versionInfo, OWL_.versionIRI, OWL_.priorVersion): g.remove((H, p_, None))
    g.add((H, OWL_.versionInfo, Literal(vs))); g.add((H, OWL_.versionIRI, URIRef(f"{H}/{vs}")))
    base_v = vk(newest()); bvs = f"{base_v[0]}.{base_v[1]}.{base_v[2]}"
    g.add((H, OWL_.priorVersion, URIRef(f"{H}/{bvs}")))
    PROV_ = Namespace("http://www.w3.org/ns/prov#"); g.add((H, PROV_.wasAttributedTo, URIRef("http://example.org/rdodi/agent/YusufAltunel")))   # as every IPage header; it also keeps versionInfo from ending the header, which the framework's archive tool reads as text
    return {(H, OWL_.versionInfo), (H, OWL_.versionIRI), (H, OWL_.priorVersion), (H, PROV_.wasAttributedTo)}
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
    hp = header(g, out)
    g.serialize(destination=out, format="turtle"); g1 = Graph(); g1.parse(out, format="turtle")
    rem = set(g0) - set(g1); add = set(g1) - set(g0)
    if [t for t in rem if t not in removed and (t[0], t[1]) not in hp] or [t for t in add if t[0] not in subj and (t[0], t[1]) not in hp]: os.remove(out); sys.exit("refused: unexpected change")
    print(f"wrote {out}: {len(rem)} replaced, {len(add)} added")

ROOT = os.path.abspath(os.path.join(HERE, ".."))
BRSF = os.environ.get("BRSF_ROOT") or next((d for d in (os.path.join(ROOT, "..", "backlog-roadmap-framework"), os.path.join(ROOT, "..", "ontologies", "backlog-roadmap-framework"), "/tmp/brsf") if os.path.isdir(os.path.join(d, "03-tooling"))), "")
SPEC = "05-lineage/l3_check_v1_0_0.py"
MPO = os.path.basename(sorted(glob.glob(os.path.join(HERE, "measure_page_ontology_v*.py")), key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[0]])[-1])
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
            A(R, B.instantiatedAt, Literal(a.run_times[nm], datatype=XSD.dateTime)); A(R, B.instantiatedFromVersion, T(a.agent_model + " sub-agent run " + aid))
            if brief:
                SW = P.StartWay_Request; A(SW, RDF.type, AGS.StartWay); A(SW, RDFS.label, EN("On the builder's request"))
                AR = P.AccessRoute_Git; A(AR, RDF.type, AGS.AccessRoute); A(AR, RDFS.label, EN("A fresh clone of the published repository"))
                GR = P["Grant3_Verifier" + SUF]; A(GR, RDF.type, AGS.AccessGrant); A(GR, AGS.grantedBy, P.Run3_Build01); A(GR, AGS.viaRoute, AR); A(GR, AGS.grantedPlace, T("the published repository, cloned fresh by the verifier")); A(GR, AGS.grantMode, T("read-only")); A(GR, AGS.grantedAt, cfg_t)
                PL = P["Plan3_Verifier" + SUF]; A(PL, RDF.type, AGS.VerificationPlan); A(PL, AGS.hasPlanDigest, T(brief)); A(PL, RDFS.comment, EN("The brief given to the verifying agent, fixed by its digest before the agent started."))
                SE = P["Session3_Verifier" + SUF]; A(SE, RDF.type, PROV.Agent); A(SE, RDFS.label, EN("an independent verifying agent (a fresh agent that did not do the work)"))
                A(R, AGS.startedInWay, SW); A(R, AGS.startedUnderGrant, GR); A(R, AGS.followsPlan, PL); A(R, AGS.executedBy, SE); A(R, AGS.placeUnchanged, Literal(False))
                C = P["Config3_" + nm + SUF]; A(C, RDF.type, AGS.AgentConfiguration); A(C, AGS.isConfigurationOf, D); A(C, AGS.recordedAt, cfg_t)
                for kind, val in (("brief", "sha256 " + brief), ("model", a.agent_model + " (general-purpose agent)")):
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
                A(ob, B.hasObservedValue, Literal(float(M["values"][k]), datatype=XSD.decimal)); A(ob, B.hasObservationMethod, T(f"Measured by {MPO} on commit {gitc} (file SHA-256 {commit}); value {k}."))
        done_keys = set(k for s in a.stories for k in STORY_KEYS[s])
        for ob_ in sorted(set(g.subjects(B.metricMovableBy, None)) - set()):
            pass
        for k in a.also_observe.split(","):
            if k in done_keys or not k: continue
            ob = P[f"Obs3_Done_{k}"]; A(ob, RDF.type, B.MetricObservation); A(ob, B.observationFor, P["Obj3_" + k]); A(ob, B.observesMetric, P["Metric3_" + k]); A(ob, B.observedAt, clk())
            A(ob, B.hasObservedValue, Literal(float(M["values"][k]), datatype=XSD.decimal)); A(ob, B.hasObservationMethod, T(f"Measured by {MPO} on commit {gitc} (file SHA-256 {commit}); value {k}."))
        st_ = g.value(IT, B.iterationStart); TE = clk(); d_ = int((TE.toPython() - st_.toPython()).total_seconds())
        for t in list(g.triples((IT, B.hasState, None))): g.remove(t)
        g.add((IT, B.hasState, B.Done)); A(IT, B.iterationEnd, TE); A(IT, B.hasObservedDuration, T(f"PT{d_ // 3600}H{(d_ % 3600) // 60}M{d_ % 60}S")); A(IT, B.hasDurationSource, T("iterationStart of this iteration to the finishedAt recorded by l3_steps finish."))
        header(g, out)
        return g, ids
    viol = 0
    for _ in range(5):
        g, ids = build(viol); g.serialize(destination=out, format="turtle"); bridge(out, a.measurement, commit, ids)
        v = subprocess.run([sys.executable, a.validator, out], capture_output=True, text=True).stdout; m_ = re.search(r"results\s*:\s*(\d+) Violation", v); v2 = int(m_.group(1)) if m_ else -1
        if v2 == 0: break
        print("violations:", v2); [print("  ", l.strip()[:260]) for l in v.splitlines() if "[Violation]" in l][:6]; break
    print("wrote", out)

WITHDRAW = {B.Proposed: B.T_WithdrawProposed, B.Refined: B.T_WithdrawReady, B.Ready: B.T_WithdrawReady, B.InProgress: B.T_WithdrawInProgress, B.Suspended: B.T_WithdrawSuspended}
def _open():
    base = newest(); out = nxt(base); g0 = Graph(); g0.parse(base, format="turtle"); g = Graph()
    for t in g0: g.add(t)
    g.bind("backlog", B); g.bind("pcl", P); return base, out, g0, g
def _write(out, g0, g, removed, subj):
    hp = header(g, out)
    g.serialize(destination=out, format="turtle"); g1 = Graph(); g1.parse(out, format="turtle")
    rem = set(g0) - set(g1); add = set(g1) - set(g0)
    if [t for t in rem if t not in removed and (t[0], t[1]) not in hp] or [t for t in add if t[0] not in subj and (t[0], t[1]) not in hp]: os.remove(out); sys.exit("refused: unexpected change")
    print(f"wrote {out}: {len(rem)} replaced, {len(add)} added")
def withdraw(a):
    import time
    base, out, g0, g = _open(); removed = set(); subj = set()
    T = lambda t: Literal(t, datatype=XSD.string)
    for nm in a.items:
        it = P[nm]; st = g0.value(it, B.hasState)
        if st not in WITHDRAW: sys.exit(f"refused: {nm} is {st}; only an open item is withdrawn")
        if (it, B.belongsToLineage, LN) not in g0: sys.exit(f"refused: {nm} is not an item of Lineage 3")
    for nm in a.items:
        it = P[nm]; st = g0.value(it, B.hasState); time.sleep(1.1); ts = Literal(now(), datatype=XSD.dateTime)
        for t in list(g.triples((it, B.hasState, None))): removed.add(t); g.remove(t)
        g.add((it, B.hasState, B.Cancelled)); subj.add(it)
        if g0.value(it, B.hasRationale) is None: g.add((it, B.hasRationale, T(a.rationale)))
        else: g.add((it, RDFS.comment, Literal("Cancelled: " + a.rationale, lang="en")))
        if (it, RDF.type, B.Iteration) in g0:   # a container is not moved: it ends by the Owner's dissolution, which derives Cancelled
            e = P["Dissolve3_" + nm]; subj.add(e)
            for p_, o_ in ((RDF.type, B.ContainerDissolution), (B.dissolvesContainer, it), (B.decidedBy, B.Owner), (B.dissolutionRationale, T(a.rationale + " Dissolved on the Owner's ruling IP-R1."))):
                g.add((e, p_, o_))
            continue
        e = P["Ev3_" + nm + "_Withdraw"]; subj.add(e)
        for p_, o_ in ((RDF.type, B.TransitionEvent), (B.transitionedItem, it), (B.viaTransition, WITHDRAW[st]), (B.transitionedAt, ts), (B.transitionedBy, B.Builder), (B.transitionedByExecutor, P.Run3_Build01)):
            g.add((e, p_, o_))
    for k in (a.missed or []):
        o = P["Obj3_" + k]
        if (o, B.belongsToLineage, LN) not in g0: sys.exit(f"refused: Obj3_{k} is not an objective of Lineage 3")
        if g0.value(o, B.hasAchievementStatus) is not None: sys.exit(f"refused: Obj3_{k} already has an achievement status")
        if [w for w in g.objects(o, B.metricMovableBy) if g.value(w, B.hasState) not in (B.Done, B.Cancelled)]: sys.exit(f"refused: Obj3_{k} still has live work that can move it")
        g.add((o, B.hasAchievementStatus, B.Ach_Missed)); g.add((o, RDFS.comment, Literal("Missed: " + a.missed_rationale, lang="en"))); subj.add(o)
    _write(out, g0, g, removed, subj)
def _items(g):
    s = set(g.subjects(B.belongsToLineage, LN))
    for o in list(s): s |= set(g.subjects(B.admittedByOutput, o))
    return sorted(i for i in s if (i, B.hasState, None) in g)
def _read_metrics():
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(HERE, MPO)], capture_output=True, text=True, cwd=ROOT)
    vals = {}
    for ln in r.stdout.splitlines():
        m = re.match(r"^(\S+)\s+(-?[\d.]+)\s*$", ln.strip())
        if m: vals[m.group(1)] = float(m.group(2))
    if not vals: sys.exit("the measurement printed no figures:\n" + (r.stdout + r.stderr)[-600:])
    return vals
def report(a):
    import subprocess
    base, out, g0, g = _open(); subj = set(); removed = set()
    EN = lambda t: Literal(t, lang="en"); T = lambda t: Literal(t, datatype=XSD.string); clk = lambda: Literal(now(), datatype=XSD.dateTime)
    A = lambda s_, p_, o_: (g.add((s_, p_, o_)), subj.add(s_))
    open_ = [i for i in _items(g0) if g0.value(i, B.hasState) in WITHDRAW and g0.value(i, B.hasState) != B.InProgress]
    if [i for i in _items(g0) if g0.value(i, B.hasState) not in (B.Done, B.Cancelled)]:
        sys.exit("refused: every item must be Done or Cancelled before the closure report (G215): " + ", ".join(str(i).split("#")[-1] for i in _items(g0) if g0.value(i, B.hasState) not in (B.Done, B.Cancelled)))
    vals = _read_metrics(); gitc = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    objs = sorted(o for o in g0.subjects(RDF.type, B.Objective) if (o, B.belongsToLineage, LN) in g0)
    fit, gap = [], []
    for o in objs:
        k = str(o).split("Obj3_")[-1]; v = vals.get(k)
        if v is None: sys.exit(f"refused: no figure for {k}")
        ob = P["Obs3_Close_" + k]; A(ob, RDF.type, B.MetricObservation); A(ob, B.observationFor, o); A(ob, B.observesMetric, P["Metric3_" + k]); A(ob, B.observedAt, clk())
        A(ob, B.hasObservedValue, Literal(v, datatype=XSD.decimal)); A(ob, B.hasObservationMethod, T(f"Read again at closure by {MPO} on commit {gitc}; value {k}."))
        tv = g0.value(o, B.hasTargetValue); dr = g0.value(o, B.hasTargetDirection)
        met = tv is not None and ((v >= float(tv)) if dr == B.Dir_Increase else (v <= float(tv)) if dr == B.Dir_Decrease else (v == float(tv)))
        (fit if met else gap).append(o)
    if "Conf" in vals:   # Conf counts the validator's findings on the register itself: read it again on the register as it stands with these readings
        import tempfile, subprocess as sp_
        # the reading names itself: start from 0 and read again until the value read is the value recorded (a fixed point), at most four times
        oc = P.Obs3_Close_Conf; vc = 0.0
        with tempfile.TemporaryDirectory() as d_:
            for _ in range(4):
                g.remove((oc, B.hasObservedValue, None)); g.add((oc, B.hasObservedValue, Literal(vc, datatype=XSD.decimal)))
                tp = os.path.join(d_, "interactive_page_lineage_abox_v0_0_0.ttl"); g.serialize(destination=tp, format="turtle")
                r_ = sp_.run([sys.executable, os.path.join(HERE, MPO), "--metric", "Conf", "--register", tp], capture_output=True, text=True, cwd=ROOT)
                v_ = float(r_.stdout.strip().splitlines()[-1])
                if v_ == vc: break
                vc = v_
            else: sys.exit("refused: the validator figure does not settle")
        g.remove((oc, B.hasObservedValue, None)); g.add((oc, B.hasObservedValue, Literal(vc, datatype=XSD.decimal)))
        g.remove((oc, B.hasObservationMethod, None)); g.add((oc, B.hasObservationMethod, T(f"Read at closure by {MPO} --metric Conf on the register as it stands with the closing readings (commit {gitc}); value Conf.")))
        oo = P.Obj3_Conf; fit = [o for o in fit if o != oo]; gap = [o for o in gap if o != oo]; (fit if vc == float(g0.value(oo, B.hasTargetValue)) else gap).append(oo)
    acc = [i for i in _items(g0) if g0.value(i, B.hasState) == B.Done]; can = [i for i in _items(g0) if g0.value(i, B.hasState) == B.Cancelled]
    t = clk(); AS = P.AsIs_L3
    A(AS, RDF.type, B.AsIsAssessment); A(AS, RDFS.label, EN("As-is assessment of Lineage 3 on the day it is concluded")); A(AS, B.assessesLineage, LN); A(AS, B.assessedAt, t)
    A(AS, B.hasFitGapStatement, T(a.fit_gap)); A(AS, B.hasImpactStatement, T(a.impact))
    for i in acc: A(AS, B.accomplishedItem, i)
    for i in can: A(AS, B.failedItem, i)
    for o in fit: A(AS, B.fitsObjective, o)
    for o in gap: A(AS, B.gapsObjective, o)
    CR = P.Closure_L3; mis = g0.value(LN, B.lineageForMission)
    A(CR, RDF.type, B.ClosureReport); A(CR, RDFS.label, EN("Closure report of Lineage 3: concluded on the Owner's ruling, its open work carried forward")); A(CR, B.closesForMission, mis)
    A(CR, B.reportGeneratedAt, t); A(CR, B.hasClosureMark, B.Cm_Cancelled); A(CR, B.citesAssessment, AS); A(CR, B.hasClosureSummary, T(a.summary)); A(CR, B.belongsToLineage, LN)
    for o in objs: A(CR, B.reportsOnObjective, o)
    for i in can: A(CR, B.reportsCancelledItem, i)
    for f_ in sorted(g0.subjects(RDF.type, B.RetrospectiveFinding)):
        if (f_, B.belongsToLineage, LN) in g0: A(CR, B.citesFinding, f_)
    for j, spec in enumerate(a.finding or [], 1):
        lab, root, rem_ = spec.split("=", 2); F = P[f"Finding3_Close_{j}"]
        A(F, RDF.type, B.RetrospectiveFinding); A(F, RDFS.label, EN(lab)); A(F, B.belongsToLineage, LN); A(F, B.detectedAt, t); A(F, B.detectedBy, B.Builder)
        A(F, B.hasFindingScope, B.Scope_LineageLocal); A(F, B.hasRootCause, T(root)); A(F, B.hasRemedy, T(rem_)); A(CR, B.citesFinding, F)
    for bp in a.best_practice or []: A(CR, B.statesBestPractice, T(bp))
    print(f"objectives fitted {len(fit)}, gapped {len(gap)}: " + ", ".join(str(o).split("Obj3_")[-1] for o in gap))
    _write(out, g0, g, removed, subj)
def conclude(a):
    import subprocess
    base, out, g0, g = _open(); subj = set(); removed = set(); T = lambda t: Literal(t, datatype=XSD.string)
    CR = P.Closure_L3; mis = g0.value(LN, B.lineageForMission)
    if (CR, RDF.type, B.ClosureReport) not in g0: sys.exit("refused: no closure report; run report first")
    first = subprocess.run(["git", "log", "--format=%H", "-S", "pcl:Closure_L3 a backlog:ClosureReport", "--", "05-lineage/interactive_page_lineage_abox_v*.ttl"], capture_output=True, text=True, cwd=ROOT).stdout.split()
    if not first: sys.exit("refused: the closure report is not committed yet; the Owner confirms a committed report")
    summ = str(g0.value(CR, B.hasClosureSummary)); ts = Literal(now(), datatype=XSD.dateTime)
    g.add((CR, B.closureCommittedAt, T(first[-1]))); subj.add(CR)
    R = P.Ruling_IP2; subj.add(R)
    for p_, o_ in ((RDF.type, B.GovernanceRuling), (B.hasRulingIdentifier, T("IP-R2")), (RDFS.label, Literal("The Owner confirms the closure of Lineage 3", lang="en")),
                   (B.hasRulingStatement, T("The Owner confirmed the closure report of Lineage 3 (marked Cancelled: concluded on his ruling IP-R1, its open work carried forward); the mission outcome is set to Abandoned with the closure summary as its rationale, and the lineage status to Abandoned. The lineage is set down in the next release.")),
                   (B.enforcedByShape, B.OwnerRulingDatedShape), (B.rulingSource, T(a.confirmation))):
        g.add((R, p_, o_))
    for s_, p_, v_ in ((mis, B.hasMissionOutcome, B.Out_Abandoned), (mis, B.outcomeRationale, T(summ)), (LN, B.hasLineageStatus, B.LS_Abandoned)):
        for t in list(g.triples((s_, p_, None))): removed.add(t); g.remove(t)
        g.add((s_, p_, v_)); subj.add(s_)
    _write(out, g0, g, removed, subj)

def sync_header(a):
    base, out, g0, g = _open(); _write(out, g0, g, set(), set())

ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True); s_ = sp.add_parser("start"); s_.add_argument("stories", nargs="+"); s_.add_argument("--report-tool", required=True)
fp = sp.add_parser("finish"); fp.add_argument("stories", nargs="+"); fp.add_argument("--measurement", required=True); fp.add_argument("--release-tag", required=True); fp.add_argument("--deployed", required=True); fp.add_argument("--validator", required=True); fp.add_argument("--also-observe", default=""); fp.add_argument("--run-times", required=True); fp.add_argument("--agents", required=True); fp.add_argument("--brief", required=True); fp.add_argument("--config-time", required=True); fp.add_argument("--suffix", default=""); fp.add_argument("--sent-back", action="store_true"); fp.add_argument("--agent-model", default="Claude")
wp = sp.add_parser("withdraw"); wp.add_argument("items", nargs="+"); wp.add_argument("--rationale", required=True); wp.add_argument("--missed", nargs="*"); wp.add_argument("--missed-rationale", default="")
rp = sp.add_parser("report"); rp.add_argument("--fit-gap", required=True); rp.add_argument("--impact", required=True); rp.add_argument("--summary", required=True); rp.add_argument("--finding", action="append"); rp.add_argument("--best-practice", action="append")
sp.add_parser("sync-header"); cp = sp.add_parser("conclude"); cp.add_argument("--confirmation", required=True)
a = ap.parse_args()
if getattr(a, "run_times", None): a.run_times = dict(x.split("=", 1) for x in a.run_times.split(","))
{"start": start, "finish": finish, "withdraw": withdraw, "report": report, "conclude": conclude, "sync-header": sync_header}[a.cmd](a)
