#!/usr/bin/env python3
"""The test that attests a story of Lineage 3. Exit 0 only if it PASSES; it can fail.
   l3_check_v1_0_0.py MEASUREMENTS.json KEY SHA256
   KEY is one or several objective keys separated by commas (A1a, A1b, ...); ALL must pass: the measured value meets its target in the direction the objective states.
   The measurement must be of the file whose SHA-256 is named (a measurement of another state attests nothing)."""
import sys, json
UP = {"A1a", "A2", "A3a", "A3b", "A3c", "A4a", "A4b", "A6b", "A7a", "A7b", "A8a", "A8b", "A10", "Mission"}   # keys whose value must reach or pass the target; all others must equal it (decrease to target)
def check(m, key, commit):
    if m.get("sha256") != commit: return False, f"measurement is of {str(m.get("sha256"))[:12]}, not {commit[:12]}"
    if key not in m["values"]: return False, f"no value for {key}"
    v, t = m["values"][key], m["targets"][key]
    return (v >= t if key in UP else v == t), f"{key} reads {v}, target {t}"
if __name__ == "__main__":
    m = json.load(open(sys.argv[1])); ok = True
    for k in sys.argv[2].split(","):
        r, msg = check(m, k, sys.argv[3]); print(("PASS " if r else "FAIL ") + msg); ok &= r
    sys.exit(0 if ok else 1)
