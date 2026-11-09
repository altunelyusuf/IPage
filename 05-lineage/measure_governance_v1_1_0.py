#!/usr/bin/env python3
"""Re-runnable measurements for Lineage 4 (IPage's Governance lineage), v1.1.0 (Branches reads through an item's children too: an epic serves the deliverables its decomposition serves), kept in the IPage repository.
   python3 measure_governance_v1_1_0.py --metric KEY [--register FILE]   prints one integer
   python3 measure_governance_v1_1_0.py --all [--register FILE]          prints KEY value for every metric
   python3 measure_governance_v1_1_0.py --selftest                       the counting rules on fixtures with a known answer

Every objective of Lineage 4 counts what is still missing, so each target is 0. The figures follow the goal tree, which
follows the scope tree (Owner's ruling IP-R6); a parent's figure is the sum of its children's:
  Mission      Execution + Handovers + Lifecycle + Roadmap
  Execution    A_Phases + A_Planning + A_Artifacts + X_Order + X_Rules + X_Monitor + X_Deploy
  A_Phases     D7 (stage and ceremony order) + X_Done (D16) + X_Review (D17)
  A_Planning   D9 (packages and a discussed forecast before the first box) + X_Packages (D13) + X_Sprints (D14) + X_TimeBox (D18)
  A_Artifacts  X_Tasks (D15) + X_Trace (D11)
  X_Order D8, X_Rules D10, X_Deploy D19; X_Monitor D12 and its route to correction (a deviation with no route is refused)
  Handovers    H_Epic (D1) + H_Archive (D2) + H_ProfileFormat (D3) + H_PageVersion (D4): each hand-over settled in its recipient's inbox
  Lifecycle    D5 not met, plus every lineage of the live register that is concluded but not set down
  Roadmap      D6 not met: no Delivery lineage queued at Opened with its mission
  Conf         violations of the framework's shapes on the register, plus live lineages of it that do not hold clean
  Contained    files changed since Lineage 4 opened outside the places its deliverables live in
  Product      files of the ontology, its shapes, the page measure, the default format or the page measurement changed since it opened
  Outside      files of the Ontologies monorepo changed by an IPage commit since it opened, other than a hand-over in an inbox
  Branches     work items of Lineage 4 that serve no deliverable of its scope (neither through their parent nor through what they decompose into)
Each figure is used at four moments: driving (each sprint plan: the open figures choose the next work), monitoring (each release:
the gate prints and records every figure), control (each release: Conf, Contained, Product, Outside and Branches must read 0 or
the release stops; a figure that rises is raised as an obstacle with its route to correction) and closure (the last reading: all
0 is achieved, anything else is recorded as missed).

A gate deliverable (D7-D19, D9) is met only when the release gate refuses a planted fault for it: a probe register
05-lineage/probes/probe_<Dn>_*.ttl exists and `release_check --probe FILE` exits 2 (the gate's code for "a governance check
refused this register"). A file or a claim alone does not meet it. A figure that needs a clone it cannot find reads -1, with a
warning on stderr. Every figure is read from files, the register or git, never typed."""
import os, re, sys, glob, subprocess
from rdflib import Graph, RDF, Namespace

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, ".."))
B = Namespace("http://example.org/backlog#"); P = Namespace("http://example.org/rdodi/page-conditions-lineage#")
OPEN_BASE = "dcb3e70"                         # the commit before IPage v1.8.0, the release that opened Lineage 4
OPEN_AT = "2026-11-08T13:05:00Z"              # the Owner accepted its mission at 16:05 Istanbul
vkey = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[-1]]
newest = lambda pat: (sorted(glob.glob(pat), key=vkey) or [""])[-1]
ALLOWED = ("03-tooling/", "04-documentation/", "05-lineage/", "07-handover-inbox/", "README.md", "VERSION.txt", "MANIFEST_SHA256.txt")
PRODUCT = ("01-ontologies/", "02-shacl-safeguards/", "06-page-measure/", "08-default-format/", "05-lineage/measure_page_ontology_", "05-lineage/measure_ipage_home_")
GATE = {"X_Rules": ["D10"], "X_Order": ["D8"], "X_Trace": ["D11"], "X_Monitor": ["D12", "D12route"], "X_Packages": ["D13"], "X_Sprints": ["D14"],
        "X_Tasks": ["D15"], "X_Done": ["D16"], "X_Review": ["D17"], "X_TimeBox": ["D18"], "X_Deploy": ["D19"]}
AREAS = {"A_Phases": (["D7"], ["X_Done", "X_Review"]), "A_Planning": (["D9"], ["X_Packages", "X_Sprints", "X_TimeBox"]), "A_Artifacts": ([], ["X_Tasks", "X_Trace"])}
EXECUTION = ["A_Phases", "A_Planning", "A_Artifacts", "X_Order", "X_Rules", "X_Monitor", "X_Deploy"]
CONCLUDED = {B.LS_Achieved, B.LS_Abandoned}
ITEM_TYPES = {B.Epic, B.Story, B.Feature, B.Task, B.ExecutionTask, B.Bug, B.Spike}


def _arg(k):
    return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else ""


def _mono():
    for d in (os.environ.get("ONTOLOGIES_ROOT", ""), os.path.join(REPO, "..", "ontologies"), os.path.join(REPO, "..", "Ontologies")):
        if d and os.path.isdir(os.path.join(d, "backlog-roadmap-framework", "07-handover-inbox")):
            if subprocess.run(["git", "-C", d, "rev-parse", "--is-shallow-repository"], capture_output=True, text=True).stdout.strip() == "true":
                print(f"warning: {d} is a shallow clone; the figures that read its history read -1", file=sys.stderr); return ""
            return os.path.abspath(d)
    print("warning: no Ontologies monorepo clone (set ONTOLOGIES_ROOT); its figures read -1", file=sys.stderr); return ""


def _brsf():
    for d in (os.environ.get("BRSF_ROOT", ""), os.path.join(REPO, "..", "backlog-roadmap-framework"), "/tmp/brsf"):
        if d and glob.glob(os.path.join(d, "03-tooling", "backlog_validate_v*.py")): return d
    return ""


# ---- counting rules (pure, so the self-test can feed them fixtures) ----
def pending_has(pending, key):
    return any(key in f for f in pending)


def handovers(ipage_pending, ipage_settled, brsf_inbox):
    """D1-D4: 1 for each not met, as a dict. Each argument is a list of file names."""
    d1 = not (not pending_has(ipage_pending, "epic-closure") and any("epic-closure" in f and "ipage" in f.lower() for f in brsf_inbox))
    d2 = not any("archive-tool" in f and "ipage" in f.lower() for f in brsf_inbox)
    d3 = pending_has(ipage_pending, "programming-subject-default-page-format") or not pending_has(ipage_settled, "programming-subject-default-page-format")
    d4 = pending_has(ipage_pending, "page-version-follows-the-page") or not pending_has(ipage_settled, "page-version-follows-the-page")
    return {"H_Epic": int(d1), "H_Archive": int(d2), "H_ProfileFormat": int(d3), "H_PageVersion": int(d4)}


def lifecycle(g, archive_g):
    d5 = not ((P.Lineage02, B.hasLineageStatus, B.LS_Archived) in g and archive_g is not None and (P.Lineage02, B.lineageArchived, None) in archive_g)
    held = [L for L in g.subjects(RDF.type, B.Lineage) if g.value(L, B.hasLineageStatus) in CONCLUDED]
    return int(d5) + len(held)


def queued(g):
    """Delivery lineages recorded in the queue: at Opened, ordinal after 4, with a mission."""
    return [L for L in g.subjects(RDF.type, B.Lineage) if g.value(L, B.hasLineageStatus) == B.LS_Opened
            and int(g.value(L, B.lineageOrdinal) or 0) > 4 and g.value(L, B.lineageForMission) is not None]


def outside(paths, allowed):
    return sorted(p for p in paths if not any(p == a or (a.endswith("/") and p.startswith(a)) for a in allowed))


def inside(paths, prefixes):
    return sorted(p for p in paths if any(p.startswith(a) for a in prefixes))


def branches(g, lineage):
    dels = {d for d in g.subjects(B.deliverableForArea, None)}
    def own(i): return any(d in dels for d in g.objects(i, B.satisfiesDeliverable))
    def up(i, seen=()):
        if own(i): return True
        par = g.value(i, B.hasParentItem) or next(iter(g.subjects(B.decomposesInto, i)), None)
        return par is not None and par not in seen and up(par, seen + (i,))
    def down(i, seen=()):
        return any(own(c) or (c not in seen and down(c, seen + (i,))) for c in g.objects(i, B.decomposesInto))
    def serves(i): return up(i) or down(i)
    items = [i for t in ITEM_TYPES for i in g.subjects(RDF.type, t) if (i, B.belongsToLineage, lineage) in g]
    return sum(1 for i in set(items) if not serves(i))


def gate_met(dn, probes_dir, gate):
    pr = sorted(glob.glob(os.path.join(probes_dir, f"probe_{dn}_*.ttl")))
    if not pr or not gate: return False
    return all(subprocess.run([sys.executable, gate, "--probe", p], capture_output=True, text=True).returncode == 2 for p in pr)


# ---- reading the repository ----
def changed_since_open():
    r = subprocess.run(["git", "-C", REPO, "diff", "--name-only", OPEN_BASE], capture_output=True, text=True)
    u = subprocess.run(["git", "-C", REPO, "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True)
    if r.returncode: return None
    return sorted(set(r.stdout.split()) | set(u.stdout.split()))


def measure(reg=None):
    reg = reg or newest(os.path.join(REPO, "05-lineage", "interactive_page_lineage_abox_v*.ttl"))
    g = Graph(); g.parse(reg, format="turtle")
    arc = newest(os.path.join(REPO, "05-lineage", "archive", "*_archive_v*.ttl")); ga = None
    if arc: ga = Graph(); ga.parse(arc, format="turtle")
    mono = _mono(); fw = _brsf(); gate = newest(os.path.join(REPO, "03-tooling", "release_check_v*.py")); probes = os.path.join(REPO, "05-lineage", "probes")
    m = {}
    inbox = os.path.join(REPO, "07-handover-inbox")
    pend = os.listdir(os.path.join(inbox, "pending")) if os.path.isdir(os.path.join(inbox, "pending")) else []
    settled = [f for d in ("accepted", "deferred", "rejected") if os.path.isdir(os.path.join(inbox, d)) for f in os.listdir(os.path.join(inbox, d))]
    if mono:
        bi = [os.path.basename(f) for f in glob.glob(os.path.join(mono, "backlog-roadmap-framework", "07-handover-inbox", "**", "*.md"), recursive=True)]
        h = handovers(pend, settled, bi)
    else:
        h = {k: -1 for k in ("H_Epic", "H_Archive", "H_ProfileFormat", "H_PageVersion")}
    m.update(h); m["Handovers"] = -1 if -1 in h.values() else sum(h.values())
    m["Lifecycle"] = lifecycle(g, ga)
    m["Roadmap"] = int(not queued(g))
    for k, ds in GATE.items():
        m[k] = sum(int(not gate_met(d, probes, gate)) for d in ds)
    for k, (own, kids) in AREAS.items():
        m[k] = sum(int(not gate_met(d, probes, gate)) for d in own) + sum(m[c] for c in kids)
    m["Execution"] = sum(m[k] for k in EXECUTION)
    m["Mission"] = -1 if m["Handovers"] < 0 else m["Handovers"] + m["Lifecycle"] + m["Roadmap"] + m["Execution"]
    if fw:
        v = newest(os.path.join(fw, "03-tooling", "backlog_validate_v*.py"))
        o = subprocess.run([sys.executable, v, reg], capture_output=True, text=True).stdout
        mm = re.search(r"results\s*:\s*(\d+) Violation", o); viol = int(mm.group(1)) if mm else -1
        unclean = 0
        for L in g.subjects(RDF.type, B.Lineage):
            if g.value(L, B.hasLineageStatus) == B.LS_Archived: continue
            o = subprocess.run([sys.executable, v, "--validate-lineage", str(L).split("#")[-1], reg], capture_output=True, text=True).stdout
            unclean += int("holds clean" not in o)
        m["Conf"] = -1 if viol < 0 else viol + unclean
    else:
        print("warning: no backlog-roadmap-framework clone (set BRSF_ROOT); Conf reads -1", file=sys.stderr); m["Conf"] = -1
    ch = changed_since_open()
    m["Contained"] = -1 if ch is None else len(outside(ch, ALLOWED))
    m["Product"] = -1 if ch is None else len(inside(ch, PRODUCT))
    if mono:
        o = subprocess.run(["git", "-C", mono, "log", f"--since={OPEN_AT}", "--grep=IPage", "--name-only", "--format="], capture_output=True, text=True).stdout.split()
        m["Outside"] = len({f for f in o if "/07-handover-inbox/" not in f})
    else:
        m["Outside"] = -1
    m["Branches"] = branches(g, P.Lineage04)
    return m


def selftest():
    ok = True
    def t(name, got, want):
        nonlocal ok
        if got != want: ok = False; print(f"FAIL {name}: got {got}, want {want}")
    tot = lambda d: sum(d.values())
    t("handovers, nothing settled", tot(handovers(["HANDOVER_to_BRSF_epic-closure-cascade_v1_0_0.md", "HANDOVER_x_page-version-follows-the-page_v1.md",
      "HANDOVER_to_IPage_programming-subject-default-page-format_v1_0_0.md"], [], [])), 4)
    t("handovers, all settled", tot(handovers([], ["HANDOVER_to_IPage_programming-subject-default-page-format_v1_0_0.md", "HANDOVER_x_page-version-follows-the-page_v1.md"],
      ["HANDOVER_IPage_to_BRSF_epic-closure-cascade_v1_0_0.md", "HANDOVER_IPage_to_BRSF_archive-tool-flaws_v1_0_0.md"])), 0)
    t("handovers, copy left behind", handovers(["HANDOVER_to_BRSF_epic-closure-cascade_v1_0_0.md"], [], ["HANDOVER_IPage_to_BRSF_epic-closure-cascade_v1_0_0.md"])["H_Epic"], 1)
    g = Graph(); ga = Graph()
    g.add((P.Lineage02, B.hasLineageStatus, B.LS_Archived)); ga.add((P.Lineage02, B.lineageArchived, __import__("rdflib").Literal(True)))
    t("lifecycle, set down", lifecycle(g, ga), 0)
    g.add((P.L9, RDF.type, B.Lineage)); g.add((P.L9, B.hasLineageStatus, B.LS_Abandoned))
    t("lifecycle, one concluded and held", lifecycle(g, ga), 1)
    t("lifecycle, no archive", lifecycle(g, None), 2)
    t("queue empty", len(queued(g)), 0)
    from rdflib import Literal
    g.add((P.L5, RDF.type, B.Lineage)); g.add((P.L5, B.hasLineageStatus, B.LS_Opened)); g.add((P.L5, B.lineageOrdinal, Literal(5)))
    t("queued without a mission", len(queued(g)), 0)
    g.add((P.L5, B.lineageForMission, P.M5)); t("queued with a mission", len(queued(g)), 1)
    t("outside", outside(["05-lineage/a.ttl", "01-ontologies/x.ttl", "README.md", "README.md.bak"], ALLOWED), ["01-ontologies/x.ttl", "README.md.bak"])
    t("product", inside(["05-lineage/measure_page_ontology_v2_2_0.py", "05-lineage/measure_governance_v1_0_0.py", "08-default-format/a.html"], PRODUCT),
      ["05-lineage/measure_page_ontology_v2_2_0.py", "08-default-format/a.html"])
    g.add((P.D1, B.deliverableForArea, P.A1)); g.add((P.S1, RDF.type, B.Story)); g.add((P.S1, B.belongsToLineage, P.Lineage04))
    t("branches, story serving nothing", branches(g, P.Lineage04), 1)
    g.add((P.E1, RDF.type, B.Epic)); g.add((P.E1, B.belongsToLineage, P.Lineage04)); g.add((P.E1, B.satisfiesDeliverable, P.D1)); g.add((P.S1, B.hasParentItem, P.E1))
    t("branches, story serving through its epic", branches(g, P.Lineage04), 0)
    g.add((P.E2, RDF.type, B.Epic)); g.add((P.E2, B.belongsToLineage, P.Lineage04)); g.add((P.E2, B.decomposesInto, P.E1))
    t("branches, parent epic serving through its child epic", branches(g, P.Lineage04), 0)
    g.add((P.E3, RDF.type, B.Epic)); g.add((P.E3, B.belongsToLineage, P.Lineage04))
    t("branches, epic serving nothing", branches(g, P.Lineage04), 1)
    t("gate, no probe", gate_met("D99", "/nonexistent", "x.py"), False)
    print("SELFTEST " + ("PASS" if ok else "FAIL")); return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv: sys.exit(selftest())
    m = measure(_arg("--register") or None)
    if "--metric" in sys.argv: print(m[_arg("--metric")])
    else: [print(k, v) for k, v in m.items()]
