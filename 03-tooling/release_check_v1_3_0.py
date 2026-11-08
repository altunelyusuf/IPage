#!/usr/bin/env python3
"""release_check_v1_3_0.py - the gate every IPage release passes before it is committed and pushed.

  python3 03-tooling/release_check_v1_3_0.py                   run every check; exit 0 only if all pass
  python3 03-tooling/release_check_v1_3_0.py --write-manifest  rewrite MANIFEST_SHA256.txt, then run every check

Checks, in order:
  1. one live version: each file name stem in 01-ontologies, 02-shacl-safeguards, 03-tooling, 05-lineage and 06-page-measure has one version
     (a changed file gets a new versioned name and the old one leaves; OE BP-D7);
  2. the ontology conforms to its shapes (pyshacl, T-Box as the ontology graph);
  3. the measurement scripts pass their self-tests (05-lineage and 06-page-measure alike);
  4. Lineage 3's register conforms to the backlog framework's shapes, and the lineage holds clean under them;
  5. every recorded verification in the register reproduces (evidence audit), and every closed stage still holds what it closed on (digest audit);
  6. VERSION.txt names a version that has its changelog;
  7. MANIFEST_SHA256.txt lists every tracked file with its SHA-256, and every hash matches.
The backlog framework is read from BRSF_ROOT or a sibling clone (backlog-roadmap-framework, or ontologies/backlog-roadmap-framework);
the Ontologies monorepo from ONTOLOGIES_ROOT or a sibling clone named ontologies or Ontologies.
v1.1.0 (2026-11-08): a lineage set down in the archive (05-lineage/archive) is still audited: the checks of Lineage 3 (holds clean, evidence,
digests) read the live register together with the newest archive file, because what they check moved there (lineage discipline step 6:
checks of live records must read the archive too). The register as a whole is still validated alone.
v1.2.0 (2026-11-08): every lineage of the register with a recorded stage output is audited, not only Lineage 3: each holds clean under the
current shapes and each closed stage still holds what it closed on (Lineage 4, the Governance lineage, closes its stages from 1.8.0 on).
v1.3.0 (2026-11-08): the evidence and digest audits are found by their name pattern (the newest version), not by a fixed file name.
"""
import os, re, sys, glob, hashlib, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
vk = lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", os.path.basename(p))[-1]]
results = []


def check(name, ok, note=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f" -- {note}" if note else ""))


def brsf():
    for d in (os.environ.get("BRSF_ROOT", ""), os.path.join(ROOT, "..", "backlog-roadmap-framework"), os.path.join(ROOT, "..", "ontologies", "backlog-roadmap-framework"), "/tmp/brsf"):
        if d and glob.glob(os.path.join(d, "03-tooling", "backlog_validate_v*.py")): return d
    return ""


def tracked():
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "--cached", "--others", "--exclude-standard"], capture_output=True, text=True).stdout.split()
    return sorted(f for f in out if f != "MANIFEST_SHA256.txt" and "__pycache__" not in f and os.path.isfile(os.path.join(ROOT, f)))


def sha(f): return hashlib.sha256(open(os.path.join(ROOT, f), "rb").read()).hexdigest()


def main(write):
    if write:
        open(os.path.join(ROOT, "MANIFEST_SHA256.txt"), "w").write("".join(f"{sha(f)}  {f}\n" for f in tracked()))
    # 1
    stems = {}
    for d in ("01-ontologies", "02-shacl-safeguards", "03-tooling", "05-lineage", "06-page-measure"):
        for f in glob.glob(os.path.join(ROOT, d, "*_v*_*_*.*")):
            stems.setdefault((d, re.sub(r"_v\d+_\d+_\d+\.\w+$", "", os.path.basename(f))), []).append(os.path.basename(f))
    dup = {k: v for k, v in stems.items() if len(v) > 1}
    check("one live version of every versioned file", not dup, "; ".join(f"{k[0]}: {', '.join(sorted(v))}" for k, v in dup.items()))
    # 2
    newest = lambda pat: sorted(glob.glob(os.path.join(ROOT, pat)), key=vk)[-1]
    tb, ab, sh = newest("01-ontologies/interactive_page_ontology_tbox_v*.ttl"), newest("01-ontologies/interactive_page_ontology_abox_v*.ttl"), newest("02-shacl-safeguards/interactive_page_ontology_shacl_v*.ttl")
    r = subprocess.run([sys.executable, "-m", "pyshacl", "-s", sh, "-e", tb, ab], capture_output=True, text=True)
    check("the ontology conforms to its shapes", "Conforms: True" in r.stdout)
    # 3
    for d in ("05-lineage", "06-page-measure"):
        for s in sorted(glob.glob(os.path.join(ROOT, d, "measure_*_v*.py"))):
            r = subprocess.run([sys.executable, s, "--selftest"], capture_output=True, text=True)
            check("self-test of " + os.path.basename(s), r.returncode == 0)
    # 4
    reg = newest("05-lineage/interactive_page_lineage_abox_v*.ttl"); fw = brsf()
    arc = sorted(glob.glob(os.path.join(ROOT, "05-lineage", "archive", "*_archive_v*.ttl")), key=vk)
    lreg = reg
    if arc:   # the lineage's records live partly in the archive: audit them together
        import tempfile, rdflib
        gl = rdflib.Graph(); gl.parse(reg, format="turtle"); ga = rdflib.Graph(); ga.parse(arc[-1], format="turtle")
        LS = rdflib.URIRef("http://example.org/backlog#hasLineageStatus")
        for s_ in set(gl.subjects(LS, None)): ga.remove((s_, LS, None))   # a lineage's status is a pointer: the live register's value is the current one
        gm = rdflib.Graph()
        for t in gl: gm.add(t)
        for t in ga: gm.add(t)
        lreg = os.path.join(tempfile.mkdtemp(), "interactive_page_lineage_abox_v0_0_0.ttl"); gm.serialize(destination=lreg, format="turtle")
    import rdflib as _r
    _g = _r.Graph(); _g.parse(lreg, format="turtle"); _B = "http://example.org/backlog#"
    lineages = sorted({str(_g.value(o, _r.URIRef(_B + "belongsToLineage"))).split("#")[-1] for o in _g.subjects(_r.RDF.type, _r.URIRef(_B + "StageOutput")) if _g.value(o, _r.URIRef(_B + "belongsToLineage")) is not None})
    if not fw: check("the register conforms (backlog framework found)", False, "no backlog-roadmap-framework clone; set BRSF_ROOT")
    else:
        v = sorted(glob.glob(os.path.join(fw, "03-tooling", "backlog_validate_v*.py")), key=vk)[-1]
        o = subprocess.run([sys.executable, v, reg], capture_output=True, text=True).stdout
        m = re.search(r"results\s*:\s*(\d+) Violation", o); check("the register conforms to the framework's shapes", bool(m) and m.group(1) == "0", m.group(0) if m else "no result line")
        for ln in lineages:
            o = subprocess.run([sys.executable, v, "--validate-lineage", ln, lreg], capture_output=True, text=True).stdout
            check(f"{ln} holds clean under the current shapes", "holds clean" in o)
    # 5
    r = subprocess.run([sys.executable, newest("05-lineage/evidence_audit_v*.py"), lreg], capture_output=True, text=True)
    check("every recorded verification reproduces", r.returncode == 0, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[-200:])
    for ln in lineages:
        r = subprocess.run([sys.executable, newest("05-lineage/digest_audit_v*.py"), lreg, ln], capture_output=True, text=True)
        check(f"every closed stage of {ln} still holds what it closed on", r.returncode == 0, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[-200:])
    # 6
    ver = open(os.path.join(ROOT, "VERSION.txt")).read().strip()
    check("VERSION.txt has its changelog", os.path.isfile(os.path.join(ROOT, "04-documentation", "CHANGELOG_v" + ver.replace(".", "_") + ".md")), ver)
    # 7
    mf = os.path.join(ROOT, "MANIFEST_SHA256.txt")
    if not os.path.isfile(mf): check("the manifest matches", False, "no MANIFEST_SHA256.txt; run with --write-manifest")
    else:
        rows = dict((l.split("  ", 1)[1].strip(), l.split("  ", 1)[0]) for l in open(mf) if l.strip())
        files = tracked(); missing = [f for f in files if f not in rows]; wrong = [f for f, h in rows.items() if not os.path.isfile(os.path.join(ROOT, f)) or sha(f) != h]
        check("the manifest matches", not missing and not wrong, f"unlisted {missing[:3]}, mismatched {wrong[:3]}" if missing or wrong else f"{len(rows)} files")
    print("RELEASE CHECK: " + ("PASS" if all(results) else "FAIL"))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main("--write-manifest" in sys.argv))
