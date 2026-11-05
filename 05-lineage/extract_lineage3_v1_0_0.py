#!/usr/bin/env python3
"""extract_lineage3_v1_0_0.py - the first IPage version of Lineage 3's register, taken whole from the RDODI register it left.

  python3 extract_lineage3_v1_0_0.py SOURCE_REGISTER.ttl SOURCE_COMMIT OUT.ttl

Keeps every statement whose subject is in Lineage 3's namespace, or is reached from one through a link to a node outside the framework's
vocabulary (the roadmap report run the kick-off activates). Nothing is reworded: the source statements are copied, and only a header is added,
naming the source file and the commit that published it, so the history can be checked against RDODI's register, which keeps all of it.
Refuses unless no statement of Lineage 3 in the source is missing from the output.
"""
import sys
from rdflib import Graph, URIRef, Literal, RDF, RDFS, OWL, XSD, BNode

P = "http://example.org/rdodi/page-conditions-lineage#"
VOCAB = ("http://example.org/backlog#", "http://example.org/core#", "http://www.w3.org/", "http://example.org/agentic-systems#", "http://purl.org/", "http://xmlns.com/")


def main(src, commit, out):
    g = Graph(); g.parse(src, format="turtle")
    keep, todo, seen = Graph(), [s for s in set(g.subjects()) if str(s).startswith(P)], set()
    while todo:
        s = todo.pop()
        if s in seen: continue
        seen.add(s)
        for p, o in g.predicate_objects(s):
            keep.add((s, p, o))
            if (isinstance(o, BNode) or (isinstance(o, URIRef) and not str(o).startswith(VOCAB) and not str(o).startswith(P))) and o not in seen and (o, None, None) in g:
                todo.append(o)
    H = URIRef("http://example.org/rdodi/page-conditions-lineage/register")
    keep.add((H, RDF.type, OWL.Ontology)); keep.add((H, OWL.imports, URIRef("http://example.org/backlog")))
    import re as _re; ver = ".".join(_re.findall(r"_v(\d+)_(\d+)_(\d+)\.ttl$", out)[0])
    keep.add((H, OWL.versionInfo, Literal(ver))); keep.add((H, OWL.versionIRI, URIRef("http://example.org/rdodi/page-conditions-lineage/register/" + ver)))
    keep.add((H, RDFS.comment, Literal(
        "BRSF register of Lineage 3 (one ontology of interactive pages), kept in the IPage repository from 2026-11-05. Its first version here is every statement of "
        f"Lineage 3 in the RDODI register {src.split('/')[-1]}, published by the Ontologies monorepo commit {commit}, copied unchanged; that register keeps "
        "the whole history, and the evidence recorded there is re-run against the monorepo. From here the lineage writes only to this file.", lang="en")))
    for pfx, ns in (("backlog", "http://example.org/backlog#"), ("pcl", P), ("core", "http://example.org/core#"), ("agsys", "http://example.org/agentic-systems#")): keep.bind(pfx, ns)
    lost = [t for t in g if str(t[0]).startswith(P) and t not in keep]
    if lost: sys.exit(f"refused: {len(lost)} statements of Lineage 3 were not carried")
    keep.serialize(destination=out, format="turtle")
    print(f"wrote {out}: {len(keep)} statements ({len(seen)} subjects) from {len(g)} in the source")


if __name__ == "__main__":
    main(*sys.argv[1:4])
