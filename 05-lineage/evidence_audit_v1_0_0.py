#!/usr/bin/env python3
"""evidence_audit_v1_0_0.py - re-runs every recorded verification of Lineage 3's register and fails unless each one reproduces.

  python3 evidence_audit_v1_0_0.py REGISTER.ttl [--workspace DIR ...]
  python3 evidence_audit_v1_0_0.py --selftest REGISTER.ttl

Each test evidence records the command that verified it, "python3 SPEC MEASUREMENT KEY SHA256 exited 0", with SPEC and MEASUREMENT relative
to the root of the repository that held them. Evidence recorded while the lineage lived in the Ontologies monorepo names monorepo paths; evidence
recorded in IPage names IPage paths. Each piece is re-run, through the framework's evidence bridge, in the first workspace that holds both of its
files: this repository first, then the monorepo clone (--workspace, ONTOLOGIES_ROOT, or a sibling folder named ontologies or Ontologies).
A hand-written "verified" flag does not pass: the bridge re-runs the command. Adapted from rdodi-ecosystem's lineage_disk_audit v1.5.0 (--evidence).
"""
import os, re, sys, glob, subprocess, tempfile
from rdflib import Graph, RDF, URIRef, Literal

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
B = "http://example.org/backlog#"
vk = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)\.", p)[-1]]
PAT = re.compile(r"^python3 (\S+) (\S+) (\S+) ([0-9a-f]{64}) exited 0$")


def brsf():
    for d in (os.environ.get("BRSF_ROOT", ""), os.path.join(ROOT, "..", "backlog-roadmap-framework"), os.path.join(ROOT, "..", "ontologies", "backlog-roadmap-framework"), "/tmp/brsf"):
        if d and glob.glob(os.path.join(d, "03-tooling", "backlog_evidence_bridge_v*.py")): return d
    sys.exit("no backlog-roadmap-framework clone found (set BRSF_ROOT)")


def workspaces(extra):
    ws = [ROOT] + extra + [os.environ.get("ONTOLOGIES_ROOT", ""), os.path.join(ROOT, "..", "ontologies"), os.path.join(ROOT, "..", "Ontologies")]
    out = []
    for w in ws:
        if w and os.path.isdir(w) and os.path.abspath(w) not in out: out.append(os.path.abspath(w))
    return out


def audit(path, ws):
    br = sorted(glob.glob(os.path.join(brsf(), "03-tooling", "backlog_evidence_bridge_v*.py")), key=vk)[-1]
    g0 = Graph(); g0.parse(path, format="turtle")
    EV, V, M = URIRef(B + "TestEvidence"), URIRef(B + "evidenceVerified"), URIRef(B + "hasVerificationMethod")
    groups, bad, n = {}, [], 0
    for e in g0.subjects(RDF.type, EV):
        n += 1; nm = str(e).split("#")[-1]; m = PAT.match(str(g0.value(e, M) or ""))
        if str(g0.value(e, V)) != "true": bad.append((nm, "not verified")); continue
        if not m: bad.append((nm, "records no reproducible command")); continue
        home = next((w for w in ws if os.path.isfile(os.path.join(w, m.group(1))) and os.path.isfile(os.path.join(w, m.group(2)))), None)
        if not home: bad.append((nm, "no workspace holds " + m.group(1) + " and " + m.group(2))); continue
        groups.setdefault((home, m.group(2), m.group(4)), []).append(e)
    for (home, meas, sha), evs in groups.items():
        out = tempfile.NamedTemporaryFile(suffix=".ttl", delete=False); out.close()
        subprocess.run([sys.executable, br, path, "--workspace", home, "-o", out.name, "--test-command", f"python3 {{spec}} {meas} {{id}} {sha}"], capture_output=True, text=True)
        g1 = Graph()
        try: g1.parse(out.name, format="turtle")
        except Exception: pass
        os.unlink(out.name)
        for e in evs:
            if str(g1.value(e, V)) != "true": bad.append((str(e).split("#")[-1], "did not reproduce in " + home))
    return n, bad


def selftest(path, ws):
    res = []
    def run(name, mut, want_ok):
        g = Graph(); g.parse(path, format="turtle"); mut(g)
        t = tempfile.NamedTemporaryFile(suffix=".ttl", delete=False); t.close(); g.serialize(t.name, format="turtle")
        n, bad = audit(t.name, ws); os.unlink(t.name); res.append((name, (not bad) == want_ok and n > 0))
    evs = sorted(Graph().parse(path, format="turtle").subjects(RDF.type, URIRef(B + "TestEvidence")), key=str)
    e = evs[0]
    run("the register as it is passes", lambda g: None, True)
    run("a command naming a missing measurement is caught", lambda g: g.set((e, URIRef(B + "hasVerificationMethod"), Literal(re.sub(r" (\S+\.json) ", " no/such/measurement.json ", str(g.value(e, URIRef(B + "hasVerificationMethod"))))))), False)
    run("evidence with no recorded command is caught", lambda g: g.remove((e, URIRef(B + "hasVerificationMethod"), None)), False)
    run("evidence recorded as unverified is caught", lambda g: g.set((e, URIRef(B + "evidenceVerified"), Literal(False))), False)
    for nm, ok in res: print(("PASS " if ok else "FAIL ") + nm)
    return all(ok for _, ok in res)


if __name__ == "__main__":
    a = sys.argv[1:]; extra = [a[i + 1] for i, x in enumerate(a) if x == "--workspace"]
    files = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] != "--workspace")]
    ws = workspaces(extra)
    if "--selftest" in a: sys.exit(0 if selftest(files[0], ws) else 1)
    n, bad = audit(files[0], ws)
    print(f"  {n} evidence record(s) re-run; {len(bad)} not reproduced" + "".join(f"\n    {b[0]}: {b[1]}" for b in bad))
    print("EVIDENCE AUDIT: " + ("PASS -- every recorded verification reproduces" if not bad else "FAIL"))
    sys.exit(0 if not bad else 1)
