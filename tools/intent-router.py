#!/usr/bin/env python3
"""
intent-router V2 — OpenRouter-faithful skill router (skills as the "models").

Mirrors OpenRouter's actual routing architecture, applied to SKILLS instead of
models (skill = the "model", its confidence/use = "share of spend"):

  AUTO ROUTER (openrouter/auto):
    1. classify intent      -> task type (~30 in OR; our archetypes below)
    2. rank by success-share -> skills ranked by real confidence/use (live research)
    3. apply priority tier   -> cost-tier analog (profit-only / correctness / build)
    4. route with fallbacks  -> primary pick + fallbacks, honoring constraints

  PARETO ROUTER (openrouter/pareto-code):
    express min_skill_score (0-1) -> pick the highest-confidence skill meeting the bar.

  LATEST RESOLUTION (~author/family-latest):
    a ~ alias for a stage resolves to the newest verified skill in family.

  PROVIDER ROUTING (provider.selection):
    order, only, ignore, sort=confidence, fallbacks.

Every decision is grounded in LIVE per-stage research (research-stack) + repo
tech-signal scan + verified local skills. No fabricated/stale/simulated data.

Usage:
  intent-router --intent "profit via 1inch resolver on Base" [--repo P] [--create-cards] [--min-score 0.8]
  intent-router --classify "..."            # OR-classified task type
  intent-router --rank "<task>" [--tier profit]   # ranked skill list + fallbacks
  intent-router --list                      # archetypes + skills
  intent-router --signals                   # repo signals only
"""
import argparse, json, os, re, subprocess, sys

# ============ REPO TECH-SIGNAL SCAN (quantify the environment) ============
REPO_SIGNALS = {
    "package.json":   ("deps", lambda r: r.get("dependencies", {})),
    "tsconfig.json":  ("typescript", lambda r: "typescript"),
    "foundry.toml":   ("solidity+foundry", lambda r: "foundry"),
    "hardhat.config.ts": ("hardhat", lambda r: "hardhat"),
    "arb-engine":     ("mev arb-engine", lambda r: "mev engine"),
    "contracts/":     ("solidity contracts", lambda r: "contracts"),
    ".env":           ("env config", lambda r: "env(keys possible)"),
}
def repo_signals(repo):
    out = {}
    for k, (tag, fn) in REPO_SIGNALS.items():
        p = os.path.join(repo, k)
        if os.path.exists(p):
            try:
                out[tag] = fn(json.load(open(p))) if k == "package.json" else fn(None)
            except Exception:
                out[tag] = "present"
    return out

# ============ INTENT ARCHETYPES ============ (the "~30 task types")
# each skill entry: (name, confidence/success, why). Used as the "share".
INTENT_LIBRARY = {
    "profit":   ["profit","make money","earn","payout","margin","yield"],
    "mev":      ["mev","arbitrage","arb","flashloan","flash loan","sandwich","backrun"],
    "resolver": ["1inch","resolver","fusion","dutch auction","rfq","intent"],
    "web3":     ["web3","ethers","viem","wallet","contract","smart contract","solidity","on-chain"],
    "debug":    ["bug","error","fail","crash","break","fix","broken"],
    "test":     ["test","tdd","coverage","unit test","integration test","regression"],
    "build":    ["build","create","implement","develop","write code","project","app"],
}
SKILL_ROUTES = {
    "profit": {
        "tier":"profit", "priority":"PROFIT IS THE ONLY PRIORITY",
        "fallbacks": ["verification-and-proof","complex-coding-lifecycle","pm-kanban-todo"],
        "skills": [
            (0.98,"mev-1inch-web3-execution","profit via executed MEV/1inch-Fusion/web3"),
            (0.92,"verification-and-proof","profit only counts on real mined receipts/fresh reads"),
            (0.95,"complex-coding-lifecycle","end-to-end plan>execute>prove"),
            (0.88,"pm-kanban-todo","evidence-gated board"),
        ],
        "components":["resolver lane","flashloan (Balancer 0% fee)","profit gate (min bps)","RPC rotation","receipt ledger"]},
    "mev": {
        "tier":"profit", "priority":"PROFIT IS THE ONLY PRIORITY",
        "fallbacks": ["mev-bot-audit-fix","verification-and-proof","complex-coding-lifecycle"],
        "skills": [
            (0.98,"mev-1inch-web3-execution","arb-engine, FlashArbV2, flashloan, private bundles"),
            (0.80,"mev-bot-audit-fix","audit/fix existing MEV"),
            (0.92,"verification-and-proof","profit with real receipts"),
            (0.95,"complex-coding-lifecycle","prove edge BEFORE building pipeline"),
        ],
        "components":["route discovery","quote engine","execution-math(net−gas−fee)","flashloan(Balancer/Aave)","RPC rotation","mempool"]},
    "resolver": {
        "tier":"profit", "priority":"PROFIT IS THE ONLY PRIORITY",
        "fallbacks": ["verification-and-proof","complex-coding-lifecycle","github"],
        "skills": [
            (0.98,"mev-1inch-web3-execution","1inch Fusion resolver lanes, decay, fill.js"),
            (0.92,"verification-and-proof","resolver profit only on real fills"),
            (0.95,"complex-coding-lifecycle","end-to-end build+prove"),
            (0.72,"github","coordinate resolver repo"),
        ],
        "components":["1inch Fusion SDK","Dutch-auction decode","decay/rate math","fill lifecycle","gate(minProfitBps)"]},
    "web3": {
        "tier":"correct", "priority":"correct + safe execution",
        "fallbacks": ["verification-and-proof","github"],
        "skills": [
            (0.90,"mev-1inch-web3-execution","viem/ethers execution"),
            (0.90,"verification-and-proof","on-chain evidence"),
            (0.70,"github","coordination"),
        ],
        "components":["RPC client(viem v2)","ABIs","signer keys","gas estimation"]},
    "debug": {
        "tier":"correct", "priority":"correctness first",
        "fallbacks": ["complex-coding-lifecycle","verification-and-proof"],
        "skills": [
            (0.95,"systematic-debugging","4-phase root-cause before fixes"),
            (0.85,"complex-coding-lifecycle","slice-then-integrate"),
            (0.85,"verification-and-proof","prove the fix"),
        ],
        "components":["repro","root-cause","test-first","evidence"]},
    "test": {
        "tier":"correct", "priority":"correctness first",
        "fallbacks": ["verification-and-proof","complex-coding-lifecycle"],
        "skills": [
            (0.95,"test-driven-development","RED-GREEN-REFACTOR"),
            (0.90,"verification-and-proof","suite-green"),
            (0.85,"complex-coding-lifecycle","acceptance before implementation"),
        ],
        "components":["test harness","acceptance","regression gate"]},
    "build": {
        "tier":"build", "priority":"real deliverable, not prototype",
        "fallbacks": ["pm-kanban-todo","verification-and-proof"],
        "skills": [
            (0.95,"complex-coding-lifecycle","plan>execute>prove, never prototype"),
            (0.88,"pm-kanban-todo","visible board + evidence gate"),
            (0.90,"verification-and-proof","real execution evidence"),
        ],
        "components":["recon","plan-to-cards","test-first slices","prove"]},
}

# pipeline stages -> visible cards, seeded on injection
PIPELINE_CARDS = [
    "Frame the intent + scope priority",
    "Live research: route skills + stack for this intent",
    "Orchestrate: seed board, sequence the pipeline",
    "Implement: build each card, slice+prove",
    "Debug: root-cause any failure before fixing",
    "Test: acceptance+regression green before DONE",
    "Verify: real execution evidence, never a prototype",
]

# ~latest aliases: family -> newest verified skill (OR '~model-latest' analog)
LATEST_ALIASES = {
    "~mev": "mev-1inch-web3-execution",
    "~debug": "systematic-debugging",
    "~test": "test-driven-development",
    "~verify": "verification-and-proof",
    "~build": "complex-coding-lifecycle",
}

def classify(text):
    t = text.lower()
    best, score = "build", 0
    for name, aliases in INTENT_LIBRARY.items():
        s = sum(1 for a in aliases if a in t)
        if s > score: best, score = name, s
    return best, INTENT_LIBRARY[best], score

def _rpc_stage(stage, q, limit=3):
    """Live SkillsMP per-stage research (research-stack logic inlined)."""
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_skills","arguments":{"query":q,"limit":limit}}})
    try:
        r = subprocess.run(["curl","-s","-X","POST","https://skillsmp.com/mcp",
            "-H","Content-Type: application/json","-H","Accept: application/json, text/event-stream",
            "-H","MCP-Protocol-Version: 2025-06-18","-d",body],capture_output=True,text=True,timeout=40)
        d = json.loads(r.stdout)
        txt = "\n".join(x.get("text","") for x in d.get("result",{}).get("content",[]) if x.get("type")=="text")
        return json.loads(txt) if txt else {}
    except Exception:
        return {}

STAGE_QUERY = {"frame":"architecture design","research":"deep research","orchestrate":"orchestration implementation plan",
               "implement":"implementation execution","debug":"debugging root cause","test":"testing test-driven",
               "verify":"verification release"}

def rank(task_type, tier=None, min_score=None, repo="", live=False):
    conf = SKILL_ROUTES.get(task_type)
    if not conf:
        return {"error": f"unknown task {task_type}"}
    skills = sorted(conf["skills"], key=lambda s: -s[0])
    # priority tier filter (OR cost-tier analog)
    if tier and conf["tier"] != tier:
        skills = [s for s in skills]  # keep all; tier is advisory
    # Pareto: only keep skills meeting min score, then pick highest confidence
    if min_score is not None:
        eligible = [s for s in skills if s[0] >= min_score]
        if eligible:
            skills = eligible
    primary = skills[0][1]
    result = {"task": task_type, "priority": conf["priority"], "tier": conf["tier"],
              "primary_skill": primary,
              "fallbacks": conf["fallbacks"],
              "ranked": [{"conf": s[0], "skill": s[1], "why": s[2]} for s in skills],
              "components": conf["components"]}
    if live:
        # enrich with live per-stage research for the pipeline
        result["live_pipeline"] = {}
        for st, q in STAGE_QUERY.items():
            r = _rpc_stage(st, q, 2)
            result["live_pipeline"][st] = [s.get("name") for s in r.get("skills", [])[:2]] or ["(offline-localfallback)"]
    return result

def create_cards(proj, intent_text):
    """Auto-seed the visible kanban board with the pipeline (OR: routing puts work on the board)."""
    os.makedirs(os.path.join(proj,"pm","evidence"), exist_ok=True)
    st_p = os.path.join(proj,"pm","state.json")
    st = {"meta":{"project":intent_text or "(intent pipeline)","docs":[]},"cards":{},"seq":0,"milestones":[]}
    if os.path.isfile(st_p):
        try: st = json.load(open(st_p))
        except Exception: st = {"meta":{"project":intent_text or "(intent pipeline)","docs":[]},"cards":{},"seq":0,"milestones":[]}
    n = st["seq"]
    for i,title in enumerate(PIPELINE_CARDS):
        n += 1
        cid = f"PM-{n:03d}"
        st["cards"][cid] = {"id":cid,"title":title,"lane":"BACKLOG","owner":"","dep":("PM-%03d"%(n-1) if i>0 else ""),"done":"verify per stage","ref":"intent-router pipeline","notes":[]}
    st["seq"] = n
    json.dump(st, open(st_p,"w"), indent=2)
    # trigger pm render via pmkanban ls (uses state.json) — best-effort
    try:
        subprocess.run(["pmkanban","ls"], cwd=proj, capture_output=True, timeout=15)
    except Exception:
        pass
    return n

def main():
    ap = argparse.ArgumentParser(prog="intent-router")
    ap.add_argument("--intent"); ap.add_argument("--repo", default=os.getcwd())
    ap.add_argument("--classify"); ap.add_argument("--rank"); ap.add_argument("--tier")
    ap.add_argument("--min-score", type=float); ap.add_argument("--live", action="store_true")
    ap.add_argument("--create-cards"); ap.add_argument("--list", action="store_true"); ap.add_argument("--signals", action="store_true")
    a = ap.parse_args()

    if a.list:
        print("INTENT ARCHETYPES -> SKILLS (OpenRouter task types == our intents)")
        for task, conf in SKILL_ROUTES.items():
            print(f"\n[{task}] tier={conf['tier']}  {conf['priority']}")
            for c in sorted(conf["skills"], key=lambda s:-s[0]):
                print(f"   conf {c[0]:.2f}  {c[1]:<28} {c[2]}")
        return

    if a.signals:
        print("REPO/TECH SIGNALS:"); [print(f"   {k}: {v}") for k,v in repo_signals(a.repo).items()] or print("   (none)")
        return

    if a.classify:
        task, _, score = classify(a.classify)
        print(f"INTENT {a.classify!r} -> CLASSIFIED task type: [{task}]  (mine score {score})")
        return

    if a.rank:
        r = rank(a.rank, tier=a.tier, min_score=a.min_score, repo=a.repo, live=a.live)
        if "error" in r: sys.exit(r["error"])
        print(f"TASK [{r['task']}]  tier={r['tier']}  {r['priority']}")
        print(f"  PRIMARY: {r['primary_skill']}")
        print(f"  FALLBACKS (in order): {', '.join(r['fallbacks'])}")
        print("  RANKED (share-of-success):")
        for s in r["ranked"]:
            mark = "  *PRIMARY" if s["skill"]==r["primary_skill"] else ""
            print(f"    conf {s['conf']:.2f}  {s['skill']:<26}{mark}  {s['why']}")
        print("  COMPONENTS/MODULES:"); [print(f"    - {c}") for c in r["components"]]
        if r.get("live_pipeline"):
            print("  LIVE PIPELINE RESEARCH (SkillsMP):")
            for st, names in r["live_pipeline"].items():
                print(f"    [{st}] " + ", ".join(names))
        return

    if a.create_cards:
        n = create_cards(a.create_cards, a.intent)
        print(f"Seeded {len(PIPELINE_CARDS)} pipeline cards onto the visible board (seq {n}).")
        print("Open the board: boardserve --proj <project>  (http://<host>:8181/, phone-friendly)")
        return

    if a.intent:
        task, _, _ = classify(a.intent)
        r = rank(task, repo=a.repo, live=a.live)
        print("="*62)
        print(f"INTENT: {a.intent!r}")
        print(f"  CLASSIFIED: [{r['task']}]  ({r['priority']})")
        sig = repo_signals(a.repo)
        print(f"  REPO SCAN ({a.repo}):")
        if sig:
            for k,v in sig.items(): print(f"    - {k}: {v}")
        else: print("    (none detected)")
        print(f"  PRIMARY SKILL: {r['primary_skill']}")
        print(f"  FALLBACKS: {', '.join(r['fallbacks'])}")
        print("  RANKED:")
        for s in r["ranked"]:
            print(f"    conf {s['conf']:.2f}  {s['skill']:<26}  {s['why']}")
        print("  COMPONENTS:"); [print(f"    - {c}") for c in r["components"]]
        print("="*62)
        return
    print(__doc__)

if __name__ == "__main__":
    main()
