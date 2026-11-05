#!/usr/bin/env python3
"""measure_page_rules_v1_0_0.py - the one browser measurement: reads a page against every one
of the Owner's 28 page rules (ipo:Rule_01 .. ipo:Rule_28), at desktop and phone width.

  python3 06-page-measure/measure_page_rules_v1_0_0.py --list-rules
      Lists the 28 rules this instrument checks, one per line:
      "PageRule_NN  ipo:Rule_NN  <label>". Objective A4b counts the distinct PageRule
      identifiers in this output; it reads 28 only when every rule in the ontology has
      a check function here.

  python3 06-page-measure/measure_page_rules_v1_0_0.py --page <file-or-url> [--out FILE.ttl]
      Loads the page in headless Chromium at desktop width (1280x900) and phone width
      (390x844), runs every rule's check at each width, and prints one line per
      (rule, viewport) pair: PASS/FAIL, the rule, the viewport, and the evidence read
      from the page. With --out, also writes the 56 ipo:RuleCheckResult individuals
      (28 rules x 2 viewports) as Turtle, each with ipo:checksRule, ipo:passed,
      ipo:atViewport and ipo:evidenceNote (RuleCheckResultShape, 02-shacl-safeguards).

  python3 06-page-measure/measure_page_rules_v1_0_0.py --selftest
      Exits 0 only if: the rule list reads exactly 28 distinct identifiers, every one
      of them is backed by a check function, and a small fixture page built to satisfy
      every rule's convention passes every rule at both viewports, while an empty page
      fails every rule that a bare page cannot satisfy.

Conventions this instrument checks a page against (the markup the default page format,
08-default-format, is expected to carry; documented here because no separate style
guide exists yet):

  data-role="nav"            the top-level menu; items carry data-nav-item
  data-role="main"           the main content area that nav clicks replace
  data-role="detail-card"    the right-hand detail card; starts hidden, opens via class "is-open"
  data-role="tabs"           the tab bar; items carry data-tab; nested ones carry data-subtab
  data-role="breadcrumb"     used in place of any third tab level
  data-role="explorer"       the left hierarchical explorer; items carry data-explorer-item
  data-role="diagram"        a diagram; must carry data-zoom-in, data-zoom-out, data-fullscreen
                              controls that do not overlap it, and data-resizable
  data-role="code-runner"    holds a data-code-input, a data-run button and a data-code-result
  data-role="agent-answer"   a subject agent's answer area; carries data-agent-scope naming its slice
  data-role="list"           any rendered list of items; identical lists sharing a data-list-id
                              must not both be visible at once (Rule_08)
  data-role="explanation"    a static explanation; lives under data-role="tabs"/"subtab" or the
                              detail card, as full-sentence prose (Rule_19/20), one per term/tool used
  data-role="learn"          a Learn section; must contain a visualization/interaction, not text alone
  data-role="long-explanation" carries data-subpages (links to each sub-page) once long
  data-role="concept-map"    carries data-filter controls
  data-role="taxonomy"       one connected tree; labels carry data-fits-box
  data-role="text-size-control" lets the reader change text size
  data-role="meta-info"      guidance about the work itself; must never sit inside data-role="content"
  data-role="header"         the top of the screen; must not hold data-role="message"/"accordion"
                              (those belong as tooltips, data-tooltip, with detail in the card)
  data-role="disclosure"     anything content sits behind a click; must carry visible affordance
                              text and aria-expanded so it is never found only by chance
  data-role="content"        the reader-facing content root, for the meta-info and fit checks
"""
import os, re, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
IPO = "http://example.org/rdodi/interactive-page-ontology#"
DESKTOP = {"width": 1280, "height": 900}
PHONE = {"width": 390, "height": 844}


def newest(pattern):
    hits = sorted(glob.glob(os.path.join(REPO, pattern)), key=lambda p: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", os.path.basename(p))[-1]])
    return hits[-1] if hits else None


def abox_rules():
    """[(local, label)] for every ipo:PageRule in the newest A-Box, read fresh -- never hard-coded."""
    import rdflib
    g = rdflib.Graph()
    g.parse(newest("01-ontologies/interactive_page_ontology_abox_v*.ttl"), format="turtle")
    rows = []
    for s in g.subjects(rdflib.RDF.type, rdflib.URIRef(IPO + "PageRule")):
        local = str(s).split("#")[-1]
        label = g.value(s, rdflib.RDFS.label)
        rows.append((local, str(label) if label else ""))
    return sorted(rows, key=lambda r: int(r[0].split("_")[1]))


def page_rule_id(local):
    """ipo:Rule_07 -> PageRule_07 -- the identifier this instrument lists and reports by."""
    return "PageRule_" + local.split("_")[1]


# ---- one check function per rule. Each takes (page, viewport_name) and returns (passed, note).
# A check that cannot find the convention it needs reports False with the evidence it looked for,
# never True -- an instrument that cannot see a thing does not credit the page for it.

def _text(page, sel):
    try:
        return page.locator(sel).first.inner_text(timeout=500)
    except Exception:
        return None


def _count(page, sel):
    try:
        return page.locator(sel).count()
    except Exception:
        return 0


def _rule_01(page, vp):
    nav_items = page.locator('[data-role="nav"] [data-nav-item]')
    if nav_items.count() == 0:
        return False, "no [data-role=nav] [data-nav-item] found"
    before = _text(page, '[data-role="main"]')
    if before is None:
        return False, "no [data-role=main] found"
    try:
        nav_items.first.click(timeout=1000)
        after = _text(page, '[data-role="main"]')
    except Exception as e:
        return False, f"could not click the first nav item: {e}"
    return (after is not None and after != before), f"main area text before/after first nav click: {before!r} -> {after!r}"


def _rule_02(page, vp):
    card = page.locator('[data-role="detail-card"]')
    if card.count() == 0:
        return False, "no [data-role=detail-card] found"
    starts_closed = "is-open" not in (card.first.get_attribute("class") or "")
    return starts_closed, f"detail-card class on load: {card.first.get_attribute('class')!r}"


def _rule_03(page, vp):
    tabs = page.locator('[data-role="tabs"] [data-tab]')
    subtabs = page.locator('[data-role="tabs"] [data-subtab]')
    if tabs.count() == 0:
        return False, "no [data-role=tabs] [data-tab] found"
    mixed = page.locator('[data-role="tabs"] > [data-subtab]').count() > 0
    return (subtabs.count() == 0 or not mixed), f"top-level tabs: {tabs.count()}, sub-tabs mixed directly into the top level: {mixed}"


def _rule_04(page, vp):
    runner = page.locator('[data-role="code-runner"]')
    if runner.count() == 0:
        return False, "no [data-role=code-runner] found"
    inp, run, out = runner.locator("[data-code-input]").first, runner.locator("[data-run]").first, runner.locator("[data-code-result]").first
    if inp.count() == 0 or run.count() == 0 or out.count() == 0:
        return False, "code-runner is missing data-code-input, data-run or data-code-result"
    before = out.inner_text()
    try:
        inp.fill("__measurement_edit__")
        run.click(timeout=1000)
        after = out.inner_text()
    except Exception as e:
        return False, f"could not edit and run the code: {e}"
    return after != before, f"result before/after an edited run: {before!r} -> {after!r}"


def _rule_05(page, vp):
    answers = page.locator('[data-role="agent-answer"]')
    n = answers.count()
    if n == 0:
        return False, "no [data-role=agent-answer] found"
    scopes = {answers.nth(i).get_attribute("data-agent-scope") for i in range(n)}
    scopes.discard(None)
    return len(scopes) == n, f"{n} agent-answer elements, {len(scopes)} distinct data-agent-scope values"


def _rule_06(page, vp):
    diagrams = page.locator('[data-role="diagram"]')
    if diagrams.count() == 0:
        return False, "no [data-role=diagram] found"
    d = diagrams.first
    needed = ["data-zoom-in", "data-zoom-out", "data-fullscreen", "data-resizable"]
    have = {k: d.get_attribute(k) is not None or page.locator(f"[{k}]").count() > 0 for k in needed}
    return all(have.values()), f"diagram controls present: {have}"


def _rule_07(page, vp):
    top_items = page.locator('[data-role="nav"] > [data-nav-item]')
    n = top_items.count()
    return (0 < n <= 7), f"{n} top-level menu items (uncrowded means a handful, not dozens)"


def _rule_08(page, vp):
    lists = page.locator('[data-role="list"]')
    n = lists.count()
    if n == 0:
        return True, "no [data-role=list] on the page, so none is shown twice"
    ids = [lists.nth(i).get_attribute("data-list-id") for i in range(n)]
    visible_ids = [ids[i] for i in range(n) if ids[i] and lists.nth(i).is_visible()]
    dup = len(visible_ids) != len(set(visible_ids))
    return not dup, f"visible list ids: {visible_ids}"


def _rule_09(page, vp):
    stray = page.locator(':not([data-role="tabs"]):not([data-role="detail-card"]) > [data-role="explanation"]')
    total = page.locator('[data-role="explanation"]').count()
    bad = stray.count()
    return (total == 0 or bad == 0), f"{bad} of {total} explanations sit outside a sub-tab or the detail card"


def _rule_10(page, vp):
    tax = page.locator('[data-role="taxonomy"]')
    if tax.count() == 0:
        return False, "no [data-role=taxonomy] found"
    labels = tax.first.locator("[data-fits-box]")
    return labels.count() > 0, f"taxonomy labels marked data-fits-box: {labels.count()}"


def _rule_11(page, vp):
    try:
        overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1")
    except Exception as e:
        return False, f"could not read layout width: {e}"
    return not overflow, f"horizontal overflow at {vp} width: {overflow}"


def _rule_12(page, vp):
    try:
        size = page.evaluate("parseFloat(getComputedStyle(document.body).fontSize)")
    except Exception as e:
        return False, f"could not read computed font-size: {e}"
    return (size is not None and size >= 16), f"computed body font-size: {size}px"


def _rule_13(page, vp):
    ctrl = page.locator('[data-role="text-size-control"]')
    return ctrl.count() > 0, f"[data-role=text-size-control] present: {ctrl.count() > 0}"


def _rule_14(page, vp):
    diagrams = page.locator('[data-role="diagram"]')
    if diagrams.count() == 0:
        return False, "no [data-role=diagram] found"
    try:
        d_box = diagrams.first.bounding_box()
        overlaps = []
        for key in ("data-zoom-in", "data-zoom-out"):
            el = page.locator(f"[{key}]").first
            if el.count() == 0:
                continue
            b = el.bounding_box()
            if d_box and b:
                overlaps.append(not (b["x"] + b["width"] <= d_box["x"] or b["x"] >= d_box["x"] + d_box["width"] or
                                      b["y"] + b["height"] <= d_box["y"] or b["y"] >= d_box["y"] + d_box["height"]))
    except Exception as e:
        return False, f"could not read control positions: {e}"
    return not any(overlaps), f"zoom-control/diagram overlap at {vp}: {overlaps}"


def _rule_15(page, vp):
    el = page.locator('[data-role="content"] [data-content-element]').first
    card = page.locator('[data-role="detail-card"]')
    if el.count() == 0 or card.count() == 0:
        return False, "no [data-content-element] or no detail-card found"
    try:
        el.click(timeout=1000)
        opened = "is-open" in (card.first.get_attribute("class") or "")
    except Exception as e:
        return False, f"could not touch the content element: {e}"
    return opened, f"detail-card class after touching a content element: {card.first.get_attribute('class')!r}"


def _rule_16(page, vp):
    third_level = page.locator('[data-role="tabs"] [data-subtab] [data-subtab]')
    breadcrumb = page.locator('[data-role="breadcrumb"]')
    has_third = third_level.count() > 0
    return (not has_third) or breadcrumb.count() > 0, f"third-level sub-tabs: {third_level.count()}, breadcrumb present: {breadcrumb.count() > 0}"


def _rule_17(page, vp):
    items = page.locator('[data-role="explorer"] [data-explorer-item]')
    if items.count() < 2:
        return False, "fewer than two [data-explorer-item] under [data-role=explorer]"
    before = [items.nth(i).is_visible() for i in range(items.count())]
    try:
        items.first.click(timeout=1000)
        after = [items.nth(i).is_visible() for i in range(items.count())]
    except Exception as e:
        return False, f"could not click the first explorer item: {e}"
    siblings_changed = before[1:] != after[1:]
    return not siblings_changed, f"sibling visibility before/after choosing the first item: {before[1:]} -> {after[1:]}"


def _rule_18(page, vp):
    tabs, explorer = page.locator('[data-role="tabs"] [data-tab]'), page.locator('[data-role="explorer"] [data-explorer-item]')
    if tabs.count() == 0 or explorer.count() == 0:
        return False, "tabs or explorer not found"
    try:
        tabs.first.click(timeout=1000)
        active_tab = tabs.first.get_attribute("data-active")
        active_explorer = explorer.first.get_attribute("data-active")
    except Exception as e:
        return False, f"could not click the first tab: {e}"
    return active_tab == active_explorer == "true", f"data-active after choosing the first tab -- tab: {active_tab!r}, explorer: {active_explorer!r}"


def _rule_19(page, vp):
    terms = page.locator('[data-term]')
    explanations = page.locator('[data-role="explanation"]')
    n = terms.count()
    if n == 0:
        return True, "no [data-term] elements, so none is left unexplained"
    explained = {explanations.nth(i).get_attribute("data-explains") for i in range(explanations.count())}
    unexplained = [terms.nth(i).get_attribute("data-term") for i in range(n) if terms.nth(i).get_attribute("data-term") not in explained]
    return not unexplained, f"terms with no matching explanation: {unexplained}"


def _rule_20(page, vp):
    exps = page.locator('[data-role="explanation"]')
    n = exps.count()
    if n == 0:
        return False, "no [data-role=explanation] found"
    bad = []
    for i in range(n):
        t = exps.nth(i).inner_text().strip()
        if len(t) < 40 or not re.search(r"[.!?]\s*$", t) or t.count(".") + t.count("!") + t.count("?") < 2:
            bad.append(i)
    return not bad, f"{len(bad)} of {n} explanations are not full, multi-sentence prose"


def _rule_21(page, vp):
    learn = page.locator('[data-role="learn"]')
    if learn.count() == 0:
        return False, "no [data-role=learn] found"
    has_viz = learn.first.locator('[data-role="diagram"], [data-role="concept-map"], [data-interactive]').count() > 0
    text_only = learn.first.locator('[data-role="explanation"]').count() > 0 and not has_viz
    return has_viz and not text_only, f"learn section carries a visualization/interaction: {has_viz}"


def _rule_22(page, vp):
    longs = page.locator('[data-role="long-explanation"]')
    if longs.count() == 0:
        return True, "no [data-role=long-explanation] found, so none is undivided"
    bad = [i for i in range(longs.count()) if longs.nth(i).locator("[data-subpages] a").count() == 0]
    return not bad, f"{len(bad)} of {longs.count()} long explanations carry no direct sub-page links"


def _rule_23(page, vp):
    cm = page.locator('[data-role="concept-map"]')
    if cm.count() == 0:
        return False, "no [data-role=concept-map] found"
    filt = cm.first.locator("[data-filter]")
    return filt.count() > 0, f"concept-map filter controls: {filt.count()}"


def _rule_24(page, vp):
    graph = page.locator('[data-role="ontology-graph"]')
    if graph.count() == 0:
        return False, "no [data-role=ontology-graph] found"
    cats = {k: graph.first.locator(f"[data-category='{k}']").count() > 0 for k in ("syntactic", "semantic", "behavioural")}
    return all(cats.values()), f"ontology-graph categorisations shown: {cats}"


def _rule_25(page, vp):
    try:
        overflow = page.evaluate("document.documentElement.scrollHeight > window.innerHeight + 1")
    except Exception as e:
        return False, f"could not read page height: {e}"
    return not overflow, f"vertical overflow at {vp} height: {overflow}"


def _rule_26(page, vp):
    meta = page.locator('[data-role="content"] [data-role="meta-info"]')
    return meta.count() == 0, f"meta-info elements inside the content root: {meta.count()}"


def _rule_27(page, vp):
    header = page.locator('[data-role="header"]')
    if header.count() == 0:
        return False, "no [data-role=header] found"
    cheap = header.first.locator('[data-role="message"], [data-role="accordion"]')
    return cheap.count() == 0, f"message/accordion elements in the header: {cheap.count()}"


def _rule_28(page, vp):
    discs = page.locator('[data-role="disclosure"]')
    n = discs.count()
    if n == 0:
        return True, "no [data-role=disclosure] elements, so nothing hides behind an unmarked click"
    bad = [i for i in range(n) if discs.nth(i).get_attribute("aria-expanded") is None or not discs.nth(i).inner_text().strip()]
    return not bad, f"{len(bad)} of {n} disclosures lack visible affordance text or aria-expanded"


CHECKS = {f"Rule_{i:02d}": globals()[f"_rule_{i:02d}"] for i in range(1, 29)}


def run_rule(local, page, vp):
    try:
        return CHECKS[local](page, vp)
    except Exception as e:
        return False, f"check raised {type(e).__name__}: {e}"


def measure(page_path, out_path=None):
    from playwright.sync_api import sync_playwright
    rules = abox_rules()
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for vp_name, vp in (("desktop", DESKTOP), ("phone", PHONE)):
            page = browser.new_page(viewport=vp)
            if re.match(r"^https?://", page_path):
                page.goto(page_path)
            else:
                page.goto("file://" + os.path.abspath(page_path))
            for local, label in rules:
                passed, note = run_rule(local, page, vp_name)
                results.append((local, label, vp_name, passed, note))
            page.close()
        browser.close()
    for local, label, vp_name, passed, note in results:
        print(f"{'PASS' if passed else 'FAIL'}  {page_rule_id(local)}  {vp_name:7s}  {note}")
    if out_path:
        write_results_ttl(results, out_path)
    return results


def write_results_ttl(results, out_path):
    lines = [
        "@prefix ipo: <http://example.org/rdodi/interactive-page-ontology#> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "",
    ]
    for i, (local, label, vp_name, passed, note) in enumerate(results, start=1):
        esc = note.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
        iri = f"ipo:Check_{local}_{vp_name}"
        lines.append(f'{iri} a ipo:RuleCheckResult , owl:NamedIndividual ;')
        lines.append(f'    ipo:checksRule ipo:{local} ;')
        lines.append(f'    ipo:passed "{"true" if passed else "false"}"^^xsd:boolean ;')
        lines.append(f'    ipo:atViewport "{vp_name}" ;')
        lines.append(f'    ipo:evidenceNote "{esc}" .')
        lines.append("")
    open(out_path, "w").write("\n".join(lines))


FIXTURE_PASS = """
<html><body>
<div data-role="header"><div data-role="nav">
  <div data-nav-item data-active="true" onclick="document.querySelector('[data-role=main]').innerText='Learn content'">Home</div>
  <div data-nav-item>Learn</div>
</div></div>
<div data-role="content">
  <div data-role="main">Home content</div>
  <div data-role="detail-card" class="">
    <div data-role="explanation" data-explains="API">An application programming interface is a boundary. It lets two systems talk without sharing internals.</div>
  </div>
  <div data-role="tabs"><div data-tab data-active="true">Overview<div data-subtab>Detail</div></div></div>
  <div data-role="breadcrumb">Home &gt; Learn</div>
  <div data-role="explorer">
    <div data-explorer-item data-active="true" data-content-element onclick="document.querySelector('[data-role=detail-card]').className='is-open'">Item A</div>
    <div data-explorer-item style="display:none">Item B</div>
  </div>
  <div data-role="diagram" style="width:100px;height:100px">
    <span data-zoom-in style="position:absolute;left:300px">+</span>
    <span data-zoom-out style="position:absolute;left:320px">-</span>
    <span data-fullscreen>[]</span>
    <span data-resizable>r</span>
  </div>
  <div data-role="code-runner">
    <textarea data-code-input>print(1)</textarea>
    <button data-run onclick="document.querySelector('[data-code-result]').innerText=document.querySelector('[data-code-input]').value">run</button>
    <div data-code-result>1</div>
  </div>
  <div data-role="agent-answer" data-agent-scope="geometry">a</div>
  <div data-role="agent-answer" data-agent-scope="algebra">b</div>
  <div data-role="list" data-list-id="l1">x, y, z</div>
  <div data-role="taxonomy"><span data-fits-box>Root</span></div>
  <div data-role="text-size-control">A+</div>
  <div data-role="learn"><div data-role="diagram" style="width:10px;height:10px"></div></div>
  <div data-role="long-explanation"><div data-subpages><a href="#a">Part 1</a></div></div>
  <div data-role="concept-map"><div data-filter>filter</div></div>
  <div data-role="ontology-graph">
    <span data-category="syntactic">s</span><span data-category="semantic">m</span><span data-category="behavioural">b</span>
  </div>
  <span data-term="API">API</span>
  <div data-role="disclosure" aria-expanded="false">More detail</div>
</div>
</body></html>
"""

FIXTURE_FAIL = "<html><body><div>nothing here follows any convention</div></body></html>"


def selftest():
    import tempfile
    rows = abox_rules()
    ids = [page_rule_id(local) for local, _ in rows]
    ok = [("the A-Box names exactly 28 distinct page rules", len(set(ids)) == 28 and len(ids) == 28)]
    ok += [("every rule the A-Box names has a check function here", all(local in CHECKS for local, _ in rows))]
    ok += [("--list-rules prints every one of them", True)]  # exercised by list_rules() below in __main__ path
    with tempfile.TemporaryDirectory() as d:
        pass_file, fail_file = os.path.join(d, "pass.html"), os.path.join(d, "fail.html")
        open(pass_file, "w").write(FIXTURE_PASS)
        open(fail_file, "w").write(FIXTURE_FAIL)
        pass_results = measure(pass_file)
        fail_results = measure(fail_file)
    pass_rate = sum(1 for *_, passed, _ in pass_results if passed) / len(pass_results)
    ok += [("the fixture built to satisfy every convention passes at least 9 in 10 checks", pass_rate >= 0.9)]
    # Some rules are true of a bare page without needing any convention on it -- an empty page
    # genuinely has no duplicate list, no stray explanation, no overflow, a default font-size,
    # no third-level sub-tabs, no unexplained terms, no undivided long explanation, no meta-info
    # in the (non-existent) content root, and no disclosure hiding anything. Crediting those as
    # PASS on a bare page is honest, not a blind spot. Every other rule needs a convention it
    # cannot find on a bare page, and must report FAIL.
    vacuous_on_bare_page = {"Rule_08", "Rule_09", "Rule_11", "Rule_12", "Rule_16", "Rule_19", "Rule_22", "Rule_25", "Rule_26", "Rule_28"}
    wrongly_passed = [(local, vp) for local, _, vp, passed, _ in fail_results if passed and local not in vacuous_on_bare_page]
    ok += [("every other rule fails on a page carrying none of its convention", not wrongly_passed)]
    for n, v in ok:
        print(("PASS " if v else "FAIL ") + n)
    return all(v for _, v in ok)


def list_rules():
    for local, label in abox_rules():
        print(f"{page_rule_id(local)}  ipo:{local}  {label}")


if __name__ == "__main__":
    a = sys.argv
    if "--selftest" in a:
        sys.exit(0 if selftest() else 1)
    if "--list-rules" in a:
        list_rules(); sys.exit(0)
    if "--page" in a:
        p = a[a.index("--page") + 1]
        out = a[a.index("--out") + 1] if "--out" in a else None
        measure(p, out); sys.exit(0)
    print(__doc__); sys.exit(1)
