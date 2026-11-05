#!/usr/bin/env python3
"""Re-runnable measurements for Lineage 3 (one ontology of interactive pages), v2.0.0, kept in the IPage repository.
   python3 measure_page_ontology_v2_0_0.py --metric KEY [--register FILE] [--monorepo ONTOLOGIES_CLONE]   prints one integer
   python3 measure_page_ontology_v2_0_0.py --all [--register FILE] [--monorepo ONTOLOGIES_CLONE]          prints KEY value for every metric
   python3 measure_page_ontology_v2_0_0.py --selftest                                                     the counting rules on fixtures with a known answer
v2.0.0 (2026-11-05, the move to IPage): the ontology figures are read from this repository; the figures about RDODI's own surface (the exclusions,
the out-scoped page work) are read from a clone of the Ontologies monorepo with its history (not shallow: some figures read git history), given by
--monorepo or ONTOLOGIES_ROOT, or found as a sibling folder named ontologies or Ontologies. A figure that needs the monorepo reads -1 without it.
The browser measurement and the default page format are looked for in this repository (06-page-measure, 08-default-format).
Every figure is read from files, the register or a browser, never typed."""
import os, re, sys, glob, subprocess, importlib.util
from rdflib import Graph, RDF, RDFS, OWL, Namespace, URIRef
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, ".."))
def _mono():
    a = sys.argv
    c = [a[a.index("--monorepo") + 1]] if "--monorepo" in a else []
    c += [os.environ.get("ONTOLOGIES_ROOT", "")] + [os.path.join(REPO, "..", n) for n in ("ontologies", "Ontologies")]
    return next((os.path.abspath(d) for d in c if d and os.path.isdir(os.path.join(d, "rdodi-ecosystem"))), "")
MONO = _mono(); ECO = os.path.join(MONO, "rdodi-ecosystem") if MONO else ""; SURF = os.path.join(ECO, "28-interactive-html-surface") if MONO else ""
OLD = os.path.join(SURF, "17-page-conditions-lineage") if MONO else ""
BRSF = os.environ.get("BRSF_ROOT") or next((d for d in (os.path.join(REPO, "..", "backlog-roadmap-framework"), os.path.join(MONO, "backlog-roadmap-framework") if MONO else "", "/tmp/brsf") if d and os.path.isdir(os.path.join(d, "03-tooling"))), "")
vkey = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[-1]]
newest = lambda pat: sorted(glob.glob(pat), key=vkey)[-1]
BASE_COMMIT = "a897c8f4"   # the release that closed this lineage's Scope stage (1.243.0)
IPO = "http://example.org/rdodi/interactive-page-ontology#"; SH = Namespace("http://www.w3.org/ns/shacl#"); P = "http://example.org/rdodi/page-conditions-lineage#"
def _old():
    if not OLD: return None
    s = importlib.util.spec_from_file_location("old", newest(f"{OLD}/measure_page_conditions_v*.py")); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def _mono_metric(o, name, *args):
    return (lambda: getattr(o, name)(*args)) if o else (lambda: -1)
def standalone(kind):
    """The newest stand-alone page-ontology file of a role (tbox, abox, shacl), outside archives, vendored copies and registrant deposits; None when there is none."""
    fs = [f for f in glob.glob(f"{REPO}/0[12]-*/interactive_page_ontology_{kind}_v*.ttl") if not re.search(r"archive|vendored|registrant-deposits|fixtures", f)]
    return sorted(fs, key=vkey)[-1] if fs else None
def graph(path):
    g = Graph()
    if path: g.parse(path, format="turtle")
    return g
def page_classes():
    """(graph, classes): the stand-alone T-Box when it exists, otherwise the interactive-page module inside the ecosystem T-Box."""
    f = standalone("tbox"); g = graph(f)
    return g, {s for s in g.subjects(RDF.type, OWL.Class) if str(s).startswith(IPO)}
def count_unlinked(g, cls):
    linked = set()
    for c in cls:
        for o in g.objects(c, RDFS.subClassOf):
            if o in cls: linked |= {c, o}
        for o in g.objects(c, OWL.equivalentClass):
            if o in cls: linked |= {c, o}
    for p in g.subjects(RDF.type, OWL.ObjectProperty):
        d, r = g.value(p, RDFS.domain), g.value(p, RDFS.range)
        if d in cls and r in cls: linked |= {d, r}
    for r in g.subjects(RDF.type, OWL.Restriction):
        for pr in (OWL.someValuesFrom, OWL.allValuesFrom, OWL.onClass):
            f = g.value(r, pr)
            if f in cls: linked |= {f} | {sc for sc in g.subjects(RDFS.subClassOf, r) if sc in cls}
    return len(cls - linked)
def count_rootless(g, cls): return sum(1 for c in cls if not any(o in cls for o in g.objects(c, RDFS.subClassOf)))
def m_standalone_classes():
    f = standalone("tbox"); return 0 if not f else len([s for s in graph(f).subjects(RDF.type, OWL.Class) if str(s).startswith(IPO)])
def m_rootless(): g, c = page_classes(); return count_rootless(g, c)
def m_unlinked(): g, c = page_classes(); return count_unlinked(g, c)
def _all_standalone():
    g = Graph()
    for k in ("tbox", "abox", "shacl"):
        f = standalone(k)
        if f: g.parse(f, format="turtle")
    return g
def m_standards_tied(): return len(set(_all_standalone().subjects(URIRef(IPO + "appliesTo"), None)))
def m_rules_recorded(): return len(set(_all_standalone().subjects(RDF.type, URIRef(IPO + "PageRule"))))
def m_rules_tied():
    g = _all_standalone(); need = [URIRef(IPO + x) for x in ("ruleSource", "ofQuality", "onPartKind")]
    return sum(1 for r in set(g.subjects(RDF.type, URIRef(IPO + "PageRule"))) if all(g.value(r, p) is not None for p in need))
def m_rule_shapes():
    f = standalone("shacl"); g = graph(f); return len([s for s in g.subjects(RDF.type, SH.NodeShape) if g.value(s, URIRef(IPO + "forRule")) is not None]) if f else 0
def m_gate_rows():
    if not MONO: return -1
    t = open(newest(f"{ECO}/03-procedure/RDODI_FourStage_Pipeline_Procedure_v*.md")).read()
    return len(set(re.findall(r"PageRule[\w-]*", "\n".join(l for l in t.splitlines() if re.match(r"\|\s*Stage4\.", l) and "RETIRED" not in l))))
def m_rules_measured():
    inst = glob.glob(f"{REPO}/06-page-measure/measure_page_rules_v*.py")
    if not inst: return 0
    out = subprocess.run([sys.executable, sorted(inst, key=vkey)[-1], "--list-rules"], capture_output=True, text=True).stdout
    return len(set(re.findall(r"PageRule[\w-]*", out)))
def m_default_formats(): return len(set(_all_standalone().subjects(RDF.type, URIRef(IPO + "DefaultPageFormat"))))
def m_default_formats_traced():
    g = _all_standalone(); return sum(1 for d in set(g.subjects(RDF.type, URIRef(IPO + "DefaultPageFormat"))) if g.value(d, URIRef(IPO + "builtFrom")) is not None)
def m_default_pages_passing():
    inst = glob.glob(f"{REPO}/06-page-measure/measure_page_rules_v*.py"); pages = glob.glob(f"{REPO}/08-default-format/**/default_page_format*.html", recursive=True)
    if not inst or not pages: return 0
    return sum(1 for pg in pages if subprocess.run([sys.executable, sorted(inst, key=vkey)[-1], pg], capture_output=True).returncode == 0)
def _git(root, *a): return subprocess.run(["git", "-C", root, *a], capture_output=True, text=True).stdout
def m_release_path_bypass():
    """Commits that reached the users without the release path: in the monorepo, a change to rdodi-ecosystem not made by a release commit;
    in IPage, any commit after the first that is neither a release ('IPage vX.Y.Z') nor a hand-over deposit. -1 without the monorepo."""
    if not MONO: return -1
    n = sum(1 for c in _git(MONO, "log", "--format=%h %s", f"{BASE_COMMIT}..HEAD", "--", "rdodi-ecosystem").splitlines() if not c.partition(" ")[2].startswith("rdodi-ecosystem v"))
    ipc = _git(REPO, "log", "--format=%s").splitlines()[:-1]
    return n + sum(1 for s in ipc if not re.match(r"^(IPage v\d+\.\d+\.\d+|Hand-over deposit)", s))
def m_handovers():
    return len([f for root in (REPO, MONO) if root for f in glob.glob(f"{root}/**/*", recursive=True) if re.search(r"page.?ontology.*hand.?over|hand.?over.*page.?ontology", os.path.basename(f), re.I) and os.path.isfile(f) and "retired" not in f])
def m_course_classes():
    g, c = page_classes(); return sum(1 for x in c if re.search(r"chapter|exam|lecture|bitcoin|python|syllabus", str(g.value(x, RDFS.label) or ""), re.I))
def m_long_definitions():
    g, c = page_classes(); SKOS = URIRef("http://www.w3.org/2004/02/skos/core#definition"); return sum(1 for x in c if any(len(str(d)) > 600 for d in g.objects(x, SKOS)))
def m_contained(register):
    if not register: return -1
    g = Graph(); g.parse(register, format="turtle"); B = Namespace("http://example.org/backlog#"); L = URIRef(P + "Lineage03")
    return sum(1 for s in g.subjects(RDF.type, B.Story) if (s, B.belongsToLineage, L) in g and g.value(s, B.satisfiesDeliverable) is None)
def m_validator(register):
    v = glob.glob(f"{BRSF}/03-tooling/backlog_validate_v*.py") if BRSF else []
    if not v or not register: return -1
    out = subprocess.run([sys.executable, sorted(v, key=vkey)[-1], "--validate-lineage", "Lineage03", register], capture_output=True, text=True).stdout
    return 0 if "holds clean" in out else len(re.findall(r"\[Violation\]", out)) or 1
def m_home():
    s = importlib.util.spec_from_file_location("home", newest(f"{HERE}/measure_ipage_home_v*.py")); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m.measure(REPO, MONO) if MONO else -1
def metrics(register):
    o = _old()
    if o: o.BASE_COMMIT = BASE_COMMIT
    M = lambda name, *args: _mono_metric(o, name, *args)
    return {"A1a": m_standalone_classes, "A1b": m_rootless, "A1c": m_unlinked, "A2": m_standards_tied, "A3a": m_rules_recorded, "A3b": m_rules_tied, "A3c": m_rule_shapes,
            "A4a": m_gate_rows, "A4b": m_rules_measured, "A5": M("m_pages_failing"), "A6a": M("m_run_profiles_without_page"), "A6b": M("m_profile_page_shapes"), "A7a": m_default_formats, "A7b": m_default_pages_passing,
            "A8a": M("m_chapter_pages_passing"), "A8b": M("m_edited_code_changes_result"), "A9": m_release_path_bypass, "A10": m_handovers, "Contained": lambda: m_contained(register),
            "X1": M("m_outside_changes"), "X2": m_course_classes, "X3": m_long_definitions, "X4": M("m_pin_changes"), "X5": M("m_html_named", r"road.?map.?report|white.?paper|technical.?report"), "X6": M("m_device_claims"),
            "Mission": m_default_formats_traced, "Conf": lambda: m_validator(register), "A11": m_home}
def selftest():
    g = Graph(); N = lambda x: URIRef(IPO + x)
    for x in "ABCD": g.add((N(x), RDF.type, OWL.Class))
    g.add((N("B"), RDFS.subClassOf, N("A"))); cls = {N(x) for x in "ABCD"}
    ok = [("rootless counts A, C and D", count_rootless(g, cls) == 3), ("unlinked counts C and D", count_unlinked(g, cls) == 2)]
    g.add((N("C"), RDFS.subClassOf, N("D"))); ok += [("a new link lowers both figures", count_rootless(g, cls) == 2 and count_unlinked(g, cls) == 0)]
    ok += [("no stand-alone file reads as zero", standalone("nosuchrole") is None)]
    ok += [("a monorepo figure without the monorepo reads -1", _mono_metric(None, "m_outside_changes")() == -1)]
    for n, v in ok: print(("PASS " if v else "FAIL ") + n)
    return all(v for _, v in ok)
if __name__ == "__main__":
    a = sys.argv; reg = a[a.index("--register") + 1] if "--register" in a else None
    if "--selftest" in a: sys.exit(0 if selftest() else 1)
    ms = metrics(reg)
    if "--metric" in a: print(ms[a[a.index("--metric") + 1]]())
    else:
        for k, fn in ms.items(): print(k, fn())
