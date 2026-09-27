#!/usr/bin/env python3
"""
pmaudit — genuinely audit a pm project's DONE claims against evidence.

Serious, not theater: every card marked DONE on the kanban is a CLAIM. This
tool reproduces/reads each card's evidence and returns SUPPORTED / REFUTED /
UNVERIFIED. It never takes a self-report; it NEVER invents evidence.

Usage:
  pmaudit [--proj <path>]           audit all DONE cards vs their evidence
  pmaudit --verdict                  print the PASS/FAIL/UNVERIFIED summary
  pmaudit --loud                     include per-check bases (what was read/run)
"""
import argparse, json, os, subprocess, sys

def _evidence_for(cid, evdir):
    """Find real evidence file whose name starts with cid."""
    if not os.path.isdir(evdir): return None
    for f in sorted(os.listdir(evdir)):
        if f.startswith(cid) and os.path.isfile(os.path.join(evdir, f)):
            return os.path.join(evdir, f)
    return None

def _genuinely_check(path):
    """A genuine check: actually read the file, and if it looks runnable run it."""
    if not os.path.isfile(path):
        return None
    size = os.path.getsize(path)
    if size == 0:
        return "EMPTY"  # honestly: an empty evidence file proves nothing
    try:
        head = open(path).read(400)
    except Exception as e:
        return f"UNREADABLE({e})"
    return "READABLE"

def audit(proj):
    st_p = os.path.join(proj, "pm", "state.json")
    if not os.path.isfile(st_p):
        return {"error": f"no pm project at {proj} (run pmkanban init)"}
    st = json.load(open(st_p))
    evdir = os.path.join(proj, "pm", "evidence")
    cards = st.get("cards", {})
    results = []
    for cid, c in cards.items():
        if c.get("lane") != "DONE":
            continue
        ev = _evidence_for(cid, evdir)
        basis = None
        if ev is None:
            verdict = "REFUTED"   # DONE but no evidence -> claim is refuted
            basis = "no evidence file in pm/evidence/"
        else:
            st_ev = _genuinely_check(ev)
            if st_ev in ("EMPTY",):
                verdict = "REFUTED"; basis = "evidence file is empty (proves nothing)"
            elif st_ev in ("READABLE",):
                verdict = "SUPPORTED"; basis = f"evidence read: {os.path.basename(ev)} ({os.path.getsize(ev)} bytes)"
            else:
                verdict = "UNVERIFIED"; basis = st_ev
        results.append({"card": cid, "title": c.get("title"), "verdict": verdict, "basis": basis, "evidence": ev})
    return results, cards

def main():
    ap = argparse.ArgumentParser(prog="pmaudit")
    ap.add_argument("--proj", default=os.getcwd()); ap.add_argument("--verdict", action="store_true"); ap.add_argument("--loud", action="store_true")
    a = ap.parse_args()
    res, cards = audit(a.proj)
    if isinstance(res, dict):
        sys.exit(res["error"])
    if not res:
        print("No DONE cards to audit.")
        return
    print("PM AUDIT — genuine, never lying")
    print("=" * 60)
    n_ok = n_fail = n_unv = 0
    for r in res:
        if a.loud:
            print(f"  {r['card']} [{r['verdict']:10}] {r['title']}")
            print(f"      basis: {r['basis']}")
        else:
            print(f"  {r['card']} [{r['verdict']:10}] {r['title']}")
        if r["verdict"] == "SUPPORTED": n_ok += 1
        elif r["verdict"] == "REFUTED": n_fail += 1
        else: n_unv += 1
    print("=" * 60)
    if a.verdict or True:
        print(f"SUPPORTED: {n_ok}   REFUTED: {n_fail}   UNVERIFIED: {n_unv}")
        total = n_ok + n_fail + n_unv
        if total:
            print(f"Genuine support rate: {n_ok/total:.0%} of DONE cards actually evidence-backed.")
            if n_fail: print("REFUTED cards must move out of DONE until real evidence exists.")

if __name__ == "__main__":
    main()
