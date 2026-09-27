#!/usr/bin/env python3
"""
pmkanban — full visual project-management backbone for coding agents.

Stdlib-only. Source of truth is pm/state.json + an authoritative project doc.
TODO.md, KANBAN.md, PROGRESS.md, LEDGER.md, SNAPSHOT.md are rendered views,
always in sync — never hand-edited.

Extras beyond the plain board:
  * milestones + linear progress bar to the end
  * official-doc source of truth (no assumptions): plan items derive from the
    authority doc, not guesses
  * amplify: extract the full build structure from the authority doc(s) into
    cards + milestones + an execution chain
  * hourly ledger: every action auto-logs; agents add meaning per hour
  * sequence chain: ordered start-to-finish execution plan
  * snapshot: one-pass photographic capture of the whole board (99.99% in a
    single read, no back-and-forth)

Lanes: BACKLOG READY IN_PROGRESS BLOCKED QA DONE
A card may move to DONE only with a real evidence path on disk.

Usage:
  pmkanban init [--project NAME] [--doc <path>]   create scaffold; record authority doc
  pmkanban auth <path>                            set the authoritative project doc
  pmkanban new "<title>" [--owner X] [--dep ID] [--done "<accept>"] [--lane L]
  pmkanban move <ID> <LANE>                       transition (enforces gates)
  pmkanban block <ID> "<reason>"
  pmkanban done <ID> <evidence_path>
  pmkanban log <ID> "<note>"
  pmkanban hr "<note>"                            record a meaningful hourly ledger entry
  pmkanban milestone <ID> <pct>        MS-001..    set milestone progress (0-100)
  pmkanban progress                              print linear progress bar + live %
  pmkanban chain                                print the start-to-finish sequence
  pmkanban amplify [--doc <path>]                build cards+ms+chain from authority docs
  pmkanban snapshot                              dump full board for one-pass capture
  pmkanban ls                                    TODO + KANBAN
"""
import argparse, json, os, re, sys
from datetime import datetime, timezone

PM = "pm"; STATE = "pm/state.json"
TODO, KANBAN, PROGRESS = "pm/TODO.md", "pm/KANBAN.md", "pm/PROGRESS.md"
LEDGER, SNAP = "pm/LEDGER.md", "pm/SNAPSHOT.md"
EVID = "pm/evidence"
LANES = ["BACKLOG", "READY", "IN_PROGRESS", "BLOCKED", "QA", "DONE"]
NOW = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
HOUR = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:00Z")

def _fail(m):
    print("ERROR: " + m, file=sys.stderr); sys.exit(1)

# ---------------- state I/O ----------------
def _load():
    if not os.path.isfile(STATE): _fail("no project here - run: pmkanban init")
    return json.load(open(STATE))

def _all_docs(st):
    return [d for d in st["meta"].get("docs", []) if os.path.isfile(d)]

def _save(st, note):
    os.makedirs(PM, exist_ok=True)
    json.dump(st, open(STATE, "w"), indent=2)
    _ledger_append(note)
    _render(st)

def _ledger_append(note):
    os.makedirs(PM, exist_ok=True)
    hh = HOUR()
    entries = []
    if os.path.isfile(LEDGER):
        entries = [l for l in open(LEDGER).read().splitlines()]
    # ensure an hour header exists before noting
    had_header = any(l == "### " + hh for l in entries)
    with open(LEDGER, "a") as f:
        if not had_header:
            f.write("### " + hh + "\n")
        f.write("- [" + datetime.now(timezone.utc).strftime("%H:%M") + "] " + note + "\n")

def _render(st):
    rows = st["cards"]
    # existing views
    with open(TODO, "w") as f:
        f.write("# TODO register (source: official docs only, no assumptions)\n_generated {0} - edit via pmkanban_\n\n".format(NOW()))
        for lane in LANES:
            f.write("## {0}\n\n".format(lane))
            items = sorted((r for r in rows.values() if r["lane"] == lane), key=lambda r: r["id"])
            if not items: f.write("_(empty)_\n\n")
            for r in items:
                box = "[x]" if lane == "DONE" else "[ ]"
                owner = (" -- owner: " + r["owner"]) if r["owner"] else ""
                dep = (" -- dep: " + r["dep"]) if r["dep"] else ""
                acc = (" -- done: " + r["done"]) if r["done"] else ""
                rt = (" -- ref: " + r["ref"]) if r.get("ref") else ""
                f.write("- {0} {1} - {2}{3}{4}{5}{6}\n".format(box, r["id"], r["title"], owner, dep, acc, rt))
                for n in r["notes"]: f.write("    " + n + "\n")
            f.write("\n")
    with open(KANBAN, "w") as f:
        f.write("# KANBAN - move cards only on a real event; DONE needs evidence\n_generated {0}_\n\n".format(NOW()))
        for lane in LANES:
            items = sorted((r for r in rows.values() if r["lane"] == lane), key=lambda r: r["id"])
            f.write("## {0}\n".format(lane))
            if not items: f.write("_(empty)_\n\n")
            for r in items:
                f.write("- {0} {1}{2}\n".format(r["id"], r["title"], (" ["+r["owner"]+"]") if r["owner"] else ""))
            f.write("\n")
    # progress view
    _render_progress(st)
    # snapshot view
    _render_snapshot(st)

def _milestone_state(st):
    ms = st.get("milestones", [])
    cards = st["cards"]
    done = sum(1 for c in cards.values() if c["lane"] == "DONE")
    total = len(cards)
    card_pct = (done / total) if total else 0.0
    ms_pct = (sum(m["pct"] for m in ms) / (len(ms) * 100.0)) if ms else 0.0
    # overall: weighted 50/50 between card completion and milestones
    overall = round(100.0 * (0.6 * card_pct + 0.4 * ms_pct), 1)
    return ms, done, total, overall

def _bar(pct, width=24):
    n = int(round(pct / 100.0 * width))
    return "[" + "#" * n + "." * (width - n) + "]"

def _render_progress(st):
    ms, done, total, overall = _milestone_state(st)
    with open(PROGRESS, "w") as f:
        f.write("# MILESTONE & LINEAR PROGRESS\n_generated {0}_\n\n".format(NOW()))
        f.write("OVERALL   {0} {1:5.1f}%  (cards {2}/{3} DONE)\n".format(_bar(overall), overall, done, total))
        cur = "   -- reached only at 100%"
        todo = len([c for c in st["cards"].values() if c["lane"] not in ("DONE",)])
        f.write("REMAINING: {0} open card(s)\n\n".format(todo))
        f.write("## MILESTONES\n")
        if not ms:
            f.write("_(none defined - use `pmkanban milestone MS-001 <pct>`)_\n\n")
        for m in ms:
            done_mark = "DONE" if m["pct"] >= 100 else "in progress" if m["pct"] > 0 else "not started"
            f.write("- {0} {1}  {2} {3:3d}%  [{4}]\n".format(m["id"], m["title"], _bar(m["pct"], 14), m["pct"], done_mark))
        f.write("\n## LIVE % TO FINISH: {0}%\n".format(overall))

def _render_snapshot(st):
    ms, done, total, overall = _milestone_state(st)
    with open(SNAP, "w") as f:
        f.write("# SNAPSHOT - one-pass photographic capture (read once, retain)\n_generated {0}_\n\n".format(NOW()))
        f.write("Project: {0}  |  Authority docs: {1}\n\n".format(
            st["meta"].get("project", "(unnamed)"),
            ", ".join(st["meta"].get("docs", [])) or "(none - set with `pmkanban auth`)")
        )
        f.write("LIVE PROGRESS: {0} {1:5.1f}%  (cards {2}/{3} DONE, {4} milestones)\n\n".format(
            _bar(overall), overall, done, total, len(ms)))
        f.write("## CHAIN (start->finish):\n")
        for cid in _chain_order(st):
            c = st["cards"][cid]
            f.write("   {0} [{1}] {2}{3}\n".format(cid, c["lane"], c["title"], (" [dep "+c["dep"]+"]") if c["dep"] else ""))
        f.write("\n## MILESTONES:\n")
        for m in ms:
            f.write("   {0} {1:3d}%  {2}\n".format(m["id"], m["pct"], m["title"]))
        f.write("\n## BOARD:\n")
        for lane in LANES:
            items = sorted((r for r in st["cards"].values() if r["lane"] == lane), key=lambda r: r["id"])
            f.write("   {0:<11} {1}\n".format(lane, ", ".join(i["id"]+" "+i["title"] for i in items) or "(empty)"))
        f.write("\n## LEDGER (last 12 hours):\n")
        if os.path.isfile(LEDGER):
            lines = [l for l in open(LEDGER).read().splitlines()]
            f.write("\n".join(lines[-18:]) + "\n")
        else:
            f.write("_(no ledger yet)_\n")

def _chain_order(st):
    """Topological order of cards by dependency (start->finish)."""
    cards = st["cards"]
    order, visited = [], set()
    def visit(cid):
        if cid in visited: return
        visited.add(cid)
        c = cards[cid]
        if c.get("dep") and c["dep"] in cards and c["dep"] not in visited:
            visit(c["dep"])
        order.append(cid)
    for cid in sorted(cards, key=lambda k: ("DONE" not in (cards[k]["lane"],), k)):
        visit(cid)
    return order

# ---------------- commands ----------------
def init(a):
    os.makedirs(EVID, exist_ok=True)
    if not os.path.isfile(STATE):
        docs = [os.path.abspath(a.doc)] if a.doc else []
        _save({"meta": {"project": a.project or "(unnamed)", "docs": docs}, "cards": {}, "seq": 0, "milestones": []},
              "init")
    print("scaffold ready: {0}/ (state.json + TODO/KANBAN/PROGRESS/LEDGER/SNAPSHOT.md)".format(PM))

def auth(a):
    st = _load()
    p = os.path.abspath(a.doc)
    if not os.path.isfile(p): _fail("authority doc not found on disk: " + p)
    if p not in st["meta"]["docs"]: st["meta"]["docs"].append(p)
    _save(st, "auth: set authority doc " + p)
    print("authority doc set: " + p + "  (plan items must derive from it)")

def new(a):
    st = _load()
    if not a.done: _fail("every card needs --done '<acceptance>' before it can be READY")
    lane = (a.lane or "BACKLOG").upper()
    if lane not in LANES: _fail("invalid lane " + lane)
    title = re.sub(r"\s+", " ", a.title).strip() or _fail("title required")
    if a.dep and a.dep.upper() not in st["cards"]: _fail("dep " + a.dep + " does not exist")
    st["seq"] += 1; cid = "PM-{:03d}".format(st["seq"])
    st["cards"][cid] = {"id": cid, "title": title, "lane": lane,
                        "owner": (a.owner or "").strip(), "dep": (a.dep or "").upper(),
                        "done": re.sub(r"\s+", " ", a.done).strip(),
                        "ref": (a.ref or "").strip(), "notes": []}
    _save(st, "new {0} [{1}] {2}".format(cid, lane, title))
    print("created {0} [{1}] {2}".format(cid, lane, title))

def move(a):
    st = _load(); cid, lane = a.id.upper(), a.lane.upper()
    if cid not in st["cards"]: _fail("no such card " + cid)
    if lane not in LANES: _fail("invalid lane " + lane)
    cur = st["cards"][cid]
    if lane == "DONE":
        has_ev = os.path.isdir(EVID) and any(f.startswith(cid) and os.path.isfile(os.path.join(EVID, f)) for f in os.listdir(EVID))
        if not has_ev: _fail("DONE requires an evidence file in pm/evidence/ first (use 'done')")
        if cur["dep"] and st["cards"].get(cur["dep"], {}).get("lane") != "DONE":
            _fail(cid + " depends on " + cur["dep"] + " which is not DONE")
    if lane == "IN_PROGRESS" and cur["dep"]:
        if st["cards"].get(cur["dep"], {}).get("lane") != "DONE":
            _fail(cid + " dep " + cur["dep"] + " not DONE yet - move the dependency first")
    if lane == "IN_PROGRESS" and lane != cur["lane"] and not cur["done"]:
        _fail("card has no acceptance criterion; decompose before starting")
    old = cur["lane"]; cur["lane"] = lane
    _save(st, "move {0} {1}->{2}".format(cid, old, lane))
    print("moved {0}: {1} -> {2}".format(cid, old, lane))

def block(a):
    st = _load(); cid = a.id.upper()
    if cid not in st["cards"]: _fail("no such card " + cid)
    st["cards"][cid]["lane"] = "BLOCKED"
    st["cards"][cid]["notes"].append("[{0}] BLOCKED: {1}".format(NOW(), a.reason))
    _save(st, "block {0}: {1}".format(cid, a.reason))
    print("blocked " + cid + ": " + a.reason)

def done(a):
    st = _load(); cid = a.id.upper()
    if cid not in st["cards"]: _fail("no such card " + cid)
    if not os.path.isfile(a.evidence_path): _fail("evidence not found on disk: " + a.evidence_path)
    st["cards"][cid]["lane"] = "DONE"
    st["cards"][cid]["notes"].append("[{0}] DONE evidence: {1}".format(NOW(), a.evidence_path))
    _save(st, "done {0} evidence={1}".format(cid, a.evidence_path))
    print("done {0}; evidence = {1}".format(cid, a.evidence_path))

def log(a):
    st = _load(); cid = a.id.upper()
    if cid not in st["cards"]: _fail("no such card " + cid)
    st["cards"][cid]["notes"].append("[{0}] {1}".format(NOW(), a.note))
    _save(st, "log {0}: {1}".format(cid, a.note))
    print("logged on " + cid)

def hr(a):
    st = _load()
    if not a.note: _fail("note required")
    # append ledger note without changing state
    _ledger_append("HR-note: " + a.note)
    print("hourly ledger note added: " + a.note)

def milestone(a):
    st = _load()
    ms = st.get("milestones", [])
    cid = a.id.upper()
    try: pct = int(a.pct)
    except: _fail("pct must be an integer 0-100")
    if not (0 <= pct <= 100): _fail("pct must be 0-100")
    if cid.startswith("MS-"):
        m = next((m for m in ms if m["id"] == cid), None)
        if pct >= 100 and m and not m.get("evidence"):
            has_ev = os.path.isdir(EVID) and any(f.startswith("MS") for f in os.listdir(EVID))
            if not has_ev:
                _fail("MS-100% requires an evidence file in pm/evidence/ (any MS* file)")
        if not m:
            m = {"id": cid, "title": a.title or "Milestone " + cid, "pct": pct, "evidence": None}
            ms.append(m)
        else:
            m["pct"] = pct
        if pct >= 100: m["evidence"] = "pm/evidence"
    else:
        _fail("milestone id must be MS-001 style")
    st["milestones"] = ms
    _save(st, "milestone {0} -> {1}%".format(cid, pct))
    print("milestone {0} -> {1}%".format(cid, pct))

def progress(a):
    st = _load()
    ms, done, total, overall = _milestone_state(st)
    print("\nLIVE PROGRESS: {0} {1:5.1f}%   cards {2}/{3} DONE   ({4} milestones)".format(
        _bar(overall), overall, done, total, len(ms)))
    for m in ms:
        print("  {0} {1} {2:3d}%".format(m["id"], _bar(m["pct"], 14), m["pct"]))
    print("  remaining open: " + str(len([c for c in st["cards"].values() if c["lane"] not in ("DONE",)])))
    print("  view: " + PROGRESS)

def chain(a):
    st = _load()
    print("\nEXECUTION CHAIN (start -> finish), dependency-ordered:")
    for i, cid in enumerate(_chain_order(st), 1):
        c = st["cards"][cid]
        print("  {0:>2}. {1} [{2}] {3}{4}".format(i, cid, c["lane"], c["title"], (" [dep "+c["dep"]+"]") if c["dep"] else ""))
    print("\n  view: " + SNAP)

def snapshot(a):
    st = _load()
    _render(st)  # regenerate snapshot from current state
    print("one-pass capture written to {0} — read it once, retain, no re-crawls.".format(SNAP))

def amplify(a):
    """Extract the full build structure from authority docs into cards+ms+chain."""
    st = _load()
    docs = _all_docs(st)
    if a.doc:
        p = os.path.abspath(a.doc)
        if not os.path.isfile(p): _fail("doc not found: " + p)
        if p not in st["meta"]["docs"]: st["meta"]["docs"].append(p)
        docs = [p]
    if not docs: _fail("no authority doc set - run `pmkanban auth <path>` or --doc")
    text = ""
    for d in docs:
        try: text += "\n=== {0} ===\n".format(d) + open(d).read()
        except Exception as e: _fail("cannot read {0}: {1}".format(d, e))
    # extract structure candidates: markdown headings, checklist lines, TODO/step markers
    candidates = []
    for m in re.finditer(r"^#{1,4}\s+.*$", text, re.M):
        candidates.append(re.sub(r"^#+\s*", "", m.group(0)).strip())
    for m in re.finditer(r"^[-*]\s+\[[ x]\]\s+.*$", text, re.M):
        candidates.append(re.sub(r"^[-*]\s+\[[ x]\]\s*", "", m.group(0)).strip())
    for m in re.finditer(r"^\s*(?:TODO|FIXME|NEXT|STEP\s*\d+)[:\-]?\s+.*$", text, re.M):
        candidates.append(re.sub(r"^\s*(?:TODO|FIXME|NEXT|STEP\s*\d+)[:\-]?\s*", "", m.group(0)).strip())
    seen, added = set(), 0
    # structural heading fragments that are not actionable tasks
    STRUCT = {"milestones", "task list", "table of contents", "contents", "overview", "introduction", "setup"}
    for c in candidates:
        title = re.sub(r"\s+", " ", c).strip(" :#-").strip()
        if not title or len(title) < 4: continue
        if title.strip().lower() in STRUCT: continue
        # a heading that is just a section label (no verb, ends up being noise)
        if title.strip().lower().startswith(("see ", "note ", "section ", "chapter ")): continue
        # drop fragments that look like pure numbering "1.", "2." or bullets with no content
        if re.match(r"^[\d\w]{1,3}\.?$", title): continue
        key = title.lower()
        if key in seen: continue
        seen.add(key); st["seq"] += 1
        cid = "PM-{:03d}".format(st["seq"])
        st["cards"][cid] = {"id": cid, "title": title, "lane": "BACKLOG", "owner": "",
                            "dep": "", "done": "verify against the authority doc",
                            "ref": d, "notes": ["[%s] sourced from %s" % (NOW(), d)]}
        added += 1
    st["milestones"] = st.get("milestones", []) or [{"id": "MS-001", "title": "Build complete per authority doc", "pct": 0, "evidence": None}]
    _save(st, "amplify: extracted {0} cards from {1} docs".format(added, len(docs)))
    print("amplify: extracted {0} cards from authority docs ({1})".format(added, ", ".join(docs)))
    print("  -> set an authority doc with `pmkanban auth`, then `pmkanban chain` to see the start->finish order.")
    print("  -> NOTE: cards exist to structure the work; assign owners/acceptance/lanes before starting.")

def ls(a):
    st = _load(); rows = st["cards"]
    print("=== TODO register ===")
    for lane in LANES:
        items = sorted((r for r in rows.values() if r["lane"] == lane), key=lambda r: r["id"])
        print("\n## {0}  ({1})".format(lane, len(items)))
        if not items: print("  (empty)")
        for r in items:
            dep = (" [dep "+r["dep"]+"]") if r["dep"] else ""; own = " " + r["owner"] if r["owner"] else ""
            acc = ("  done="+r["done"]) if r["done"] else ""
            print("  {0} {1}{2}{3}{4}".format(r["id"], r["title"], own, dep, acc))
    print("\n=== KANBAN board ===")
    for lane in LANES:
        items = sorted((r for r in rows.values() if r["lane"] == lane), key=lambda r: r["id"])
        print("  {0:<12} {1}".format(lane, ", ".join(i["id"]+" "+i["title"] for i in items) or "(empty)"))
    ms, done, total, overall = _milestone_state(st)
    print("\nLIVE PROGRESS: {0} {1:5.1f}%".format(_bar(overall), overall))

def main():
    ap = argparse.ArgumentParser(prog="pmkanban")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("--project"); p.add_argument("--doc"); p.set_defaults(fn=init)
    p = sub.add_parser("auth"); p.add_argument("doc"); p.set_defaults(fn=auth)
    p = sub.add_parser("new"); p.add_argument("title"); p.add_argument("--owner"); p.add_argument("--dep")
    p.add_argument("--done"); p.add_argument("--lane"); p.add_argument("--ref"); p.set_defaults(fn=new)
    p = sub.add_parser("ls"); p.set_defaults(fn=ls)
    p = sub.add_parser("move"); p.add_argument("id"); p.add_argument("lane"); p.set_defaults(fn=move)
    p = sub.add_parser("block"); p.add_argument("id"); p.add_argument("reason"); p.set_defaults(fn=block)
    p = sub.add_parser("done"); p.add_argument("id"); p.add_argument("evidence_path"); p.set_defaults(fn=done)
    p = sub.add_parser("log"); p.add_argument("id"); p.add_argument("note"); p.set_defaults(fn=log)
    p = sub.add_parser("hr"); p.add_argument("note"); p.set_defaults(fn=hr)
    p = sub.add_parser("milestone"); p.add_argument("id"); p.add_argument("pct"); p.add_argument("--title"); p.set_defaults(fn=milestone)
    p = sub.add_parser("progress"); p.set_defaults(fn=progress)
    p = sub.add_parser("chain"); p.set_defaults(fn=chain)
    p = sub.add_parser("snapshot"); p.set_defaults(fn=snapshot)
    p = sub.add_parser("amplify"); p.add_argument("--doc"); p.set_defaults(fn=amplify)
    a = ap.parse_args(); a.fn(a)

if __name__ == "__main__":
    main()
