#!/usr/bin/env python3
"""
boardserve — serve the responsive kanban board (desktop + phone) for a pm project.

Reads ./pm/state.json (rendered by pmkanban) and serves:
  /             -> responsive HTML board (index.html from pm-boilerplate/web)
  /api/board    -> JSON snapshot {cards, meta{project,docs,progress,evidence}, milestones, ledger}

Also supports a static/demo mode: --static embeds a sample snapshot so the
HTML can be opened directly off disk (file:// or ?static) with no server.

Usage:
  boardserve [--port 8181] [--proj /path/to/project] [--static]
"""
import argparse, json, os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LANES = ["BACKLOG","READY","IN_PROGRESS","BLOCKED","QA","DONE"]

def _snapshot(proj):
    state_path = os.path.join(proj, "pm", "state.json")
    if not os.path.isfile(state_path):
        return {"cards": [], "meta": {"project": os.path.basename(proj), "docs": [], "progress": 0, "evidence": 0}, "milestones": [], "ledger": []}
    st = json.load(open(state_path))
    cards = [{"id": c["id"], "title": c["title"], "lane": c["lane"], "owner": c["owner"]}
             for c in st.get("cards", {}).values()]
    done = sum(1 for c in cards if c["lane"] == "DONE")
    total = len(cards)
    # progress: 60% card completion + 40% milestone avg (match pmkanban)
    ms = st.get("milestones", [])
    ms_pct = sum(m.get("pct", 0) for m in ms) / (len(ms) * 100.0) if ms else 0.0
    overall = round(100.0 * (0.6 * (done / total if total else 0) + 0.4 * ms_pct), 1)
    evd = 0
    ev = os.path.join(proj, "pm", "evidence")
    if os.path.isdir(ev): evd = len([f for f in os.listdir(ev) if os.path.isfile(os.path.join(ev, f))])
    return {
        "cards": cards,
        "meta": {"project": st.get("meta", {}).get("project", os.path.basename(proj)),
                 "docs": st.get("meta", {}).get("docs", []), "progress": overall, "evidence": evd},
        "milestones": ms,
        "ledger": [],
    }

def _static_html():
    here = os.path.dirname(os.path.abspath(__file__))
    web = os.path.join(os.path.dirname(here), "web", "index.html")  # pm-boilerplate/web
    alt = os.path.join(here, "..", "web", "index.html")
    for p in (web, alt, "/root/pm-boilerplate/web/index.html"):
        if os.path.isfile(p): return open(p).read()
    return "<h1>index.html not found</h1>"

def _serve(proj, port, static_only):
    html = _static_html()
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def do_GET(self):
            if self.path.startswith("/api/board"):
                snap = _snapshot(proj)
                body = json.dumps(snap).encode()
                self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body); return
            if self.path == "/" or self.path.startswith("/?"):
                body = html.encode()
                self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body); return
            self.send_response(404); self.end_headers()
    if static_only:
        print("STATIC MODE: open /root/pm-boilerplate/web/index.html directly (no server) or:")
    print("Board:  http://<host>:%d/       (desktop or phone)\nAPI:    /api/board" % port)
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()

def main():
    ap = argparse.ArgumentParser(prog="boardserve")
    ap.add_argument("--port", type=int, default=8181)
    ap.add_argument("--proj", default=os.getcwd())
    ap.add_argument("--static", action="store_true", help="static demo snapshot (no live state)")
    a = ap.parse_args()
    _serve(a.proj, a.port, a.static)

if __name__ == "__main__":
    main()
