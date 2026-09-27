#!/usr/bin/env python3
"""
research-stack — live per-stage skill research for the intent router.

This is the research/curation layer that keeps the skill router CURRENT instead
of hardcoded-generic. For each execution stage it queries SkillsMP live and
returns top verified skills (name, source, stars) + the best-known local
Hermes skill as a fallback opener. No simulated or stale data.

Stages: frame=1, research=2, orchestrate=3, implement=4, debug=5, test=6, verify=7

Usage:
  research-stack --stage implement
  research-stack --all
  research-stack --compose "<intent>"   # full pipeline research, all 7 stages
"""
import argparse, json, os, re, subprocess, sys

SKILLSMP = "https://skillsmp.com/mcp"
# local (Hermes) high-confidence opener per stage — grounded, not generic
LOCAL = {
    "frame":      ("complex-coding-lifecycle", "PM framing: recon baseline, plan-to-cards, risk-first"),
    "research":   ("skill-directory",          "route + skillsmp search; grounded-citations for answers"),
    "orchestrate":("pm-kanban-todo",           "visible board + evidence gate to run the pipeline"),
    "implement":  ("mev-1inch-web3-execution", "web3/MEV execution (when web3); else lifecycle"),
    "debug":      ("systematic-debugging",     "4-phase root-cause debugging before fixes"),
    "test":       ("test-driven-development",  "RED-GREEN-REFACTOR; acceptance test first"),
    "verify":     ("verification-and-proof",   "real execution evidence, never a prototype"),
}
STAGE_QUERIES = {
    "frame":        "architecture design",
    "research":     "deep research",
    "orchestrate":  "orchestration implementation plan",
    "implement":    "implementation execution",
    "debug":        "debugging root cause",
    "test":         "testing test-driven",
    "verify":       "verification release",
}

def _rpc_call(method, params):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":method,"arguments":params}})
    try:
        r = subprocess.run(["curl","-s","-X","POST",SKILLSMP,
            "-H","Content-Type: application/json",
            "-H","Accept: application/json, text/event-stream",
            "-H","MCP-Protocol-Version: 2025-06-18",
            "-d",body], capture_output=True, text=True, timeout=40)
        if r.returncode != 0: return {}
        d = json.loads(r.stdout)
        txt = "\n".join(x.get("text","") for x in d.get("result",{}).get("content",[]) if x.get("type")=="text")
        return json.loads(txt) if txt else {}
    except Exception as e:
        return {"_err": str(e)}

def _query_stage(stage, limit=3):
    q = STAGE_QUERIES.get(stage, stage)
    res = _rpc_call("search_skills", {"query": q, "limit": limit})
    out = []
    for s in res.get("skills", [])[:limit]:
        out.append({
            "name": s.get("name"), "author": s.get("author"),
            "desc": (s.get("description") or "")[:90],
            "stars": s.get("stars"), "github": s.get("githubUrl"),
            "skill": s.get("skillUrl"),
        })
    return {"stage": stage, "query": q, "live": out, "local_opener": LOCAL[stage],
            "_err": res.get("_err")}

def _local_stage(stage):
    name, why = LOCAL[stage]
    return {"stage": stage, "query": STAGE_QUERIES[stage], "live": [],
            "local_opener": (name, why)}

def _compose(intent):
    stages = ["frame","research","orchestrate","implement","debug","test","verify"]
    results = []
    for st in stages:
        r = _query_stage(st)
        if r.get("_err"):
            r = _local_stage(st)  # graceful fallback to grounded local if network down
        results.append(r)
    return {"intent": intent, "stages": results}

def main():
    ap = argparse.ArgumentParser(prog="research-stack")
    ap.add_argument("--stage", help="one stage: frame|research|orchestrate|implement|debug|test|verify")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--compose", help="do live research for ALL pipe stages for an intent")
    ap.add_argument("--offline", action="store_true", help="use grounded local openers only (no network)")
    a = ap.parse_args()

    if a.compose:
        if a.offline:
            res = {"intent": a.compose, "stages": [_local_stage(s) for s in ["frame","research","orchestrate","implement","debug","test","verify"]]}
        else:
            res = _compose(a.compose)
        print("LIVE PER-STAGE SKILL RESEARCH for intent: %r" % a.compose)
        for st in res["stages"]:
            print("\n[%s]  (queried: %s)" % (st["stage"], st.get("query")))
            print("  local opener: %s — %s" % st["local_opener"])
            for s in st["live"]:
                print("  ★ %-6s %-24s %s  [%s]" % (str(s["stars"] or "?"), s["name"], "| "+s["desc"],
                    (s["author"] or "")))
        return

    stage = a.stage
    if stage == "all" or a.all:
        for st in ["frame","research","orchestrate","implement","debug","test","verify"]:
            r = _query_stage(st) if not a.offline else _local_stage(st)
            print("[%s] local: %s | live: %s" % (st, r["local_opener"][0], ", ".join(s["name"] for s in r["live"]) or "(offline)") )
        return
    if stage:
        r = _query_stage(stage) if not a.offline else _local_stage(stage)
        print("STAGE: %s  (query: %s)" % (r["stage"], r.get("query")))
        print("  local opener: %s — %s" % r["local_opener"])
        for s in r["live"]:
            print("  ★ %-6s %-24s %s" % (str(s["stars"] or "?"), s["name"], s["desc"]))
        return
    print(__doc__)

if __name__ == "__main__":
    main()
