#!/usr/bin/env python3
"""measure_ipage_home_v1_1_0.py - objective A11 of Lineage 3: is the page work at home in the IPage repository?

  measure_ipage_home_v1_1_0.py [--ipage IPAGE_CLONE] [--monorepo ONTOLOGIES_CLONE]   prints the count (0 to 4)
v1.1.0 (kept in IPage): the IPage clone defaults to the repository this file sits in; the monorepo clone to ONTOLOGIES_ROOT or a sibling folder
named ontologies or Ontologies.
  measure_ipage_home_v1_1_0.py --selftest

Counts four conditions, each 1 when it holds:
  1. IPage holds the page ontology (01-ontologies/interactive_page_ontology_tbox_v*.ttl);
  2. IPage holds Lineage 3's register (05-lineage/interactive_page_lineage_abox_v*.ttl naming Lineage03);
  3. IPage holds the lineage's tools (05-lineage: a step script, the check and the measurement script);
  4. the monorepo copy of the package says it moved to IPage (its README names the IPage repository).
A missing clone counts as nothing held. The figure can fall: removing any file lowers it.
"""
import os, sys, glob, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
IPAGE = os.path.abspath(os.path.join(HERE, ".."))
MONO = next((os.path.abspath(d) for d in (os.environ.get("ONTOLOGIES_ROOT", ""), os.path.join(IPAGE, "..", "ontologies"), os.path.join(IPAGE, "..", "Ontologies")) if d and os.path.isdir(os.path.join(d, "rdodi-ecosystem"))), "")
L3 = "http://example.org/rdodi/page-conditions-lineage#Lineage03"


def conditions(ipage, mono):
    ok = []
    ok.append(bool(ipage and glob.glob(os.path.join(ipage, "01-ontologies", "interactive_page_ontology_tbox_v*.ttl"))))
    regs = glob.glob(os.path.join(ipage, "05-lineage", "interactive_page_lineage_abox_v*.ttl")) if ipage else []
    ok.append(any(L3 in open(r, encoding="utf-8").read() or "pcl:Lineage03" in open(r, encoding="utf-8").read() for r in regs))
    tools = [glob.glob(os.path.join(ipage, "05-lineage", p)) if ipage else [] for p in ("l3_steps_v*.py", "l3_check_v*.py", "measure_page_ontology_v*.py")]
    ok.append(all(tools))
    rd = os.path.join(mono, "interactive-page-ontology", "README.md")
    ok.append(os.path.isfile(rd) and "github.com/altunelyusuf/IPage" in open(rd, encoding="utf-8").read())
    return ok


def measure(ipage, mono): return sum(1 for c in conditions(ipage, mono) if c)


def selftest():
    t = tempfile.mkdtemp(); ip = os.path.join(t, "ipage"); mo = os.path.join(t, "mono")
    res = [("an empty pair of clones reads 0", measure(ip, mo) == 0)]
    os.makedirs(os.path.join(ip, "01-ontologies")); open(os.path.join(ip, "01-ontologies", "interactive_page_ontology_tbox_v1_0_0.ttl"), "w").write("x")
    res.append(("the ontology alone reads 1", measure(ip, mo) == 1))
    os.makedirs(os.path.join(ip, "05-lineage")); open(os.path.join(ip, "05-lineage", "interactive_page_lineage_abox_v0_1_0.ttl"), "w").write("pcl:Lineage03 a x .")
    for f in ("l3_steps_v1_0_0.py", "l3_check_v1_0_0.py", "measure_page_ontology_v1_0_0.py"): open(os.path.join(ip, "05-lineage", f), "w").write("")
    res.append(("ontology, register and tools read 3", measure(ip, mo) == 3))
    os.makedirs(os.path.join(mo, "interactive-page-ontology")); open(os.path.join(mo, "interactive-page-ontology", "README.md"), "w").write("Moved to https://github.com/altunelyusuf/IPage")
    res.append(("all four read 4", measure(ip, mo) == 4))
    os.remove(os.path.join(ip, "05-lineage", "l3_check_v1_0_0.py"))
    res.append(("removing a tool lowers the figure", measure(ip, mo) == 3))
    for n, v in res: print(("PASS " if v else "FAIL ") + n)
    return all(v for _, v in res)


if __name__ == "__main__":
    a = sys.argv
    if "--selftest" in a: sys.exit(0 if selftest() else 1)
    ip = a[a.index("--ipage") + 1] if "--ipage" in a else IPAGE
    mo = a[a.index("--monorepo") + 1] if "--monorepo" in a else MONO
    print(measure(ip, mo))
