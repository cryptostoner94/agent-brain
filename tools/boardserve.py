#!/usr/bin/env python3
"""
boardserve — serve ALL visible SkillMP board views for a pm project.

Serves the responsive board (desktop + phone) AND every visual:
  /                  -> responsive HTML board (6 lanes + progress + milestones)
  /api/board         -> JSON snapshot {cards, meta, milestones, ledger}
  /api/todo          -> TODO register JSON
  /api/ledger        -> hourly ledger JSON
  /api/snapshot      -> one-pass snapshot JSON
  /view/todo         -> rendered TODO.md view
  /view/ledger       -> rendered LEDGER.md view
  /view/snapshot     -> rendered SNAPSHOT.md view

Auto-picks a FREE port: --port is preferred, but if taken it tries +1 until
free. Default 16888.

Usage:
  boardserve [--port 16888] [--proj /path/to/project]
"""
import argparse, json, os, re, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LANES = ["BACKLOG","READY","IN_PROGRESS","BLOCKED","QA","DONE"]

def _read(p):
    try:
        return open(p).read()
    except Exception:
        return None

def _snapshot(proj):
    st_p = os.path.join(proj, "pm", "state.json")
    if not os.path.isfile(st_p):
        return {"cards": [], "meta": {"project": os.path.basename(proj), "docs": [], "progress": 0, "evidence": 0}, "milestones": [], "ledger": []}
    st = json.load(open(st_p))
    cards = [{"id": c["id"], "title": c["title"], "lane": c["lane"], "owner": c["owner"]} for c in st.get("cards", {}).values()]
    done = sum(1 for c in cards if c["lane"] == "DONE"); total = len(cards)
    ms = st.get("milestones", [])
    ms_pct = sum(m.get("pct", 0) for m in ms) / (len(ms) * 100.0) if ms else 0.0
    overall = round(100.0 * (0.6 * (done / total if total else 0) + 0.4 * ms_pct), 1)
    evd = 0; ev = os.path.join(proj, "pm", "evidence")
    if os.path.isdir(ev): evd = len([f for f in os.listdir(ev) if os.path.isfile(os.path.join(ev, f))])
    ledger = []
    led = os.path.join(proj, "pm", "LEDGER.md")
    lt = _read(led)
    if lt: ledger = lt.splitlines()
    return {
        "cards": cards,
        "meta": {"project": st.get("meta", {}).get("project", os.path.basename(proj)),
                 "docs": st.get("meta", {}).get("docs", []), "progress": overall, "evidence": evd},
        "milestones": ms, "ledger": ledger,
    }

def _static_html():
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.path.join(os.path.dirname(here), "web", "index.html"),
              os.path.join(here, "..", "web", "index.html"),
              "/root/pm-boilerplate/web/index.html"):
        if os.path.isfile(p): return open(p).read()
    return "<h1>index.html not found</h1>"

def _find_port(preferred):
    import socket
    if preferred:
        s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("0.0.0.0", preferred)); s.close(); return preferred
        except Exception:
            pass
    for p in range(preferred if preferred else 16888, preferred + 10 if preferred else 16898):
        s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("0.0.0.0", p)); s.close(); return p
        except Exception:
            continue
    return preferred

def _serve(proj, preferred):
    html = _static_html(); port = _find_port(preferred)
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def _json(self, obj):
            b = json.dumps(obj).encode(); self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
        def _text(self, t):
            b = (t or "(empty)").encode(); self.send_response(200); self.send_header("Content-Type","text/plain; charset=utf-8"); self.send_header("X-Accel-Buffering","no"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
        def do_GET(self):
            snap = _snapshot(proj)
            if self.path.startswith("/api/board"):  return self._json(snap)
            if self.path.startswith("/api/todo"):   return self._json({"todo": _read(os.path.join(proj,"pm","TODO.md")) or ""})
            if self.path.startswith("/api/ledger"): return self._json({"ledger": snap["ledger"]})
            if self.path.startswith("/api/snapshot"): return self._json({"snapshot": _read(os.path.join(proj,"pm","SNAPSHOT.md")) or ""})
            if self.path.startswith("/api/progress"): return self._json({"progress": _read(os.path.join(proj,"pm","PROGRESS.md")) or ""})
            if self.path.startswith("/view/todo"):   return self._text(_read(os.path.join(proj,"pm","TODO.md")))
            if self.path.startswith("/view/ledger"): return self._text(_read(os.path.join(proj,"pm","LEDGER.md")))
            if self.path.startswith("/view/snapshot"): return self._text(_read(os.path.join(proj,"pm","SNAPSHOT.md")))
            if self.path.startswith("/view/progress"): return self._text(_read(os.path.join(proj,"pm","PROGRESS.md")))
            if self.path == "/" or self.path.startswith("/?"):
                b = html.encode(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b); return
            self.send_response(404); self.end_headers()
    print(f"BOARD LIVE on :{port}")
    print(f"  /            board (desktop+phone)   http://<host>:{port}/")
    print(f"  /api/board   live JSON")
    print(f"  /api/todo /api/ledger /api/snapshot   JSON")
    print(f"  /view/todo /view/ledger /view/snapshot   plain text views")
    print(f"  /view/snapshot  one-pass capture")
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()

def main():
    ap = argparse.ArgumentParser(prog="boardserve")
    ap.add_argument("--port", type=int, default=16888, help="preferred port (auto-increments if taken; default 16888)")
    ap.add_argument("--proj", default=os.getcwd())
    ap.add_argument("--static", action="store_true")
    a = ap.parse_args()
    _serve(a.proj, a.port)

if __name__ == "__main__":
    main()
