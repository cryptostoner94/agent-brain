#!/usr/bin/env python3
"""
bds — one-command launcher for the visible SkillMP board platform.

`bds start [dir]` does EVERYTHING to get the visible, live board running:
  1. init the pm project  (pmkanban init --project <name> --doc docs/SPEC.md if found)
  2. auto-seed pipeline cards if none exist  (intent-router --create-cards)
  3. start the responsive board server  (boardserve on :8181, desktop + phone)
  4. print the URL + how to audit

Usage:
  bds start [dir] [--port 8181] [--intent "our goal"]   << the main command
  bds status [dir]       show board state + audit DONE claims
  bds stop                stop the board server

Subcommands are the board operations; `start` is the everything-launcher.
"""
import argparse, json, os, signal, subprocess, sys, time

def _tool(name):
    # prefer on-PATH, else the repo tools dir
    from shutil import which
    p = which(name)
    return p or (os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py"))

def _find_pm(proj):
    """Return the real project dir that holds pm/state.json, or proj itself."""
    if os.path.isfile(os.path.join(proj, "pm", "state.json")):
        return proj
    for root, dirs, files in os.walk(proj):
        if "pm" in dirs and os.path.isfile(os.path.join(root, "pm", "state.json")):
            return root
    return proj

def _start(args):
    proj = os.path.abspath(args.dir)
    if not os.path.isdir(proj):
        sys.exit(f"ERROR: not a directory: {proj}")
    real = _find_pm(proj)

    # 1. init if missing
    init_needed = not os.path.isfile(os.path.join(real, "pm", "state.json"))
    if init_needed:
        spec = os.path.join(real, "docs", "SPEC.md")
        doc = [spec] if os.path.isfile(spec) else []
        print("→ init project")
        cmd = [_tool("pmkanban"), "init"]
        if args.intent: cmd += ["--project", args.intent[:40]]
        if doc: cmd += ["--doc", doc[0]]
        subprocess.run(cmd, cwd=real)

    # 2. seed pipeline cards if the board is empty of PM cards
    st_p = os.path.join(real, "pm", "state.json")
    needs_seed = False
    if os.path.isfile(st_p):
        try:
            st = json.load(open(st_p))
            if not st.get("cards"): needs_seed = True
        except Exception:
            needs_seed = True
    if needs_seed:
        print("→ auto-seed pipeline cards")
        subprocess.run([_tool("intent-router"), "--create-cards", real], cwd=real)

    # 3. start the board server (free the port if a stale server holds it)
    import urllib.request
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{args.port}/", timeout=1)
        print(f"→ port {args.port} already serves a board; reusing it")
        # point any stale boardserve pid at this project (best-effort)
        subprocess.run(["pkill","-f","boardserve"], check=False)
        time.sleep(0.6)
    except Exception:
        pass
    print(f"→ starting board server (port {args.port})")
    svc = subprocess.Popen(
        [_tool("boardserve"), "--port", str(args.port), "--proj", real],
        cwd=real)
    # persist pid for bds stop
    pidfile = os.path.join(real, "pm", ".boardserve.pid")
    os.makedirs(os.path.join(real, "pm"), exist_ok=True)
    open(pidfile, "w").write(str(svc.pid))

    # wait for it to be ready
    for _ in range(20):
        time.sleep(0.3)
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{args.port}/api/board", timeout=1)
            break
        except Exception:
            continue

    print("\n✅ Board LIVE")
    print(f"   Desktop/phone:  http://<host>:{args.port}/")
    print(f"   API:            http://127.0.0.1:{args.port}/api/board")
    print(f"   Project:        {real}")
    print("\n   Next:  audit claims  →  pmaudit --proj " + real)
    print(f"   Stop:   bds stop (or kill $(cat {pidfile}))")

def _status(args):
    proj = os.path.abspath(args.dir); real = _find_pm(proj)
    print(f"Board: {real}")
    subprocess.run([_tool("pmkanban"), "ls"], cwd=real)
    print("\n-- audit --")
    subprocess.run([_tool("pmaudit"), "--proj", real])

def _stop(args):
    proj = os.path.abspath(args.dir); real = _find_pm(proj)
    pidfile = os.path.join(real, "pm", ".boardserve.pid")
    if os.path.isfile(pidfile):
        pid = int(open(pidfile).read().strip())
        try:
            os.kill(pid, signal.SIGTERM); print(f"stopped board server pid {pid}")
        except ProcessLookupError:
            print("server already stopped")
        os.remove(pidfile)
    else:
        print("no board server pid found (start with: bds start)")

def main():
    ap = argparse.ArgumentParser(prog="bds")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("start", help="init + seed + serve (do everything)")
    p.add_argument("dir", nargs="?", default=os.getcwd()); p.add_argument("--port", type=int, default=8181); p.add_argument("--intent")
    p.set_defaults(fn=_start)
    p = sub.add_parser("status"); p.add_argument("dir", nargs="?", default=os.getcwd()); p.set_defaults(fn=_status)
    p = sub.add_parser("stop"); p.add_argument("dir", nargs="?", default=os.getcwd()); p.set_defaults(fn=_stop)
    a = ap.parse_args(); a.fn(a)

if __name__ == "__main__":
    main()
