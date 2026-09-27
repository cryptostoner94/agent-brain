# Intent-Aware Skill Router + PM Platform (agent-brain edition)

A portable, AI-agnostic platform that fuses **intent-aware skill routing**, **project management**, and **genuine auditing**. Any AI can inject it and route the right skills for a user's intent, then build/track/prove/audit end-to-end — coding OR non-coding work — with full visible context (plan, progress, kanban) on desktop or phone.

## Skills in this registry (deduplicated, AI-agnostic)

| Skill | Purpose |
|-------|---------|
| `skills/pm-kanban-todo` | Visible todo + kanban + milestones + progress + hourly ledger + snapshot; evidence gates |
| `skills/one-go-orchestrated-pm` | One-go execution fused with PM; coding + non-coding agents; loop/hallucination guards |
| `skills/intent-aware-skill-router` | OpenRouter-faithful skill router: classify intent → rank by share-of-success → tier/fallbacks → components + auto-seed board |
| `skills/genuine-audit` | Serious auditing: every claim verified, never lie; verdicts SUPPORTED/REFUTED/UNVERIFIED |
| `skills/task-execute` (existing) | Generic discover→classify→assign→execute→verify (enriched) |
| `skills/qa-review`, `skills/revenue-first`, `skills/deep-research` (existing) | Cross-cutting quality / revenue-first / research gates |

## Portable tools (`tools/`, stdlib-only Python)

- `bds.py` — **ONE-COMMAND LAUNCHER**: `bds start [dir]` initializes the project, auto-seeds the pipeline cards, and starts the live board server. `bds status` / `bds stop` too.
- `pmkanban.py` — the board CLI (state → TODO/KANBAN/PROGRESS/LEDGER/SNAPSHOT, evidence gates)
- `intent-router.py` — OpenRouter-faithful skill router (classify/rank/min-score/tier/live/create-cards)
- `research-stack.py` — live per-stage skill research from SkillsMP
- `boardserve.py` — responsive board server (desktop + phone), reads `pm/state.json`
- `pmaudit.py` — genuine audit of DONE claims vs evidence
- `board.html` — the responsive board UI

## How to inject into ANY agent or project

1. **Copy skills** — copy the relevant `skills/<name>/SKILL.md` content into the agent's system prompt / instruction set. Plain text, no AI-specific format. Per-agent selection: see `TRAINING.md` (coding / non-coding / research / audit loads).
2. **Install tools** — `git clone https://github.com/cryptostoner94/agent-brain.git` then symlink `tools/*.py` to `/usr/local/bin`. Uses in any project: `init` → `route` → `seed` → `serve` → `audit`.
   ```bash
   git clone https://github.com/cryptostoner94/agent-brain.git
   for f in agent-brain/tools/*.py; do chmod +x "$f"; ln -sf "$(realpath $f)" /usr/local/bin/$(basename "$f" .py); done
   ```
   **Launch everything in ONE command** — `bds start` (init + seed + serve all visuals):
   ```bash
   cd <your-project>
   bds start --intent "MEV resolver profit"   # init project, seed pipeline, serve board+all views on a free port (16888)
   # open http://<host>:16888/ on desktop or phone · audit with pmaudit
   ```
3. **Always-on** — inject `one-go-orchestrated-pm` + `pm-kanban-todo` + `genuine-audit` (mindset + visible board + not-lie) into the agent's persistent instructions so every session starts with the visible board and honest-execution posture.

## How it works together

intent → `intent-router` classifies + ranks skills (share-of-success) + scans repo → auto-seeds the 7-stage pipeline as kanban cards → `pmkanban` tracks/proves each (evidence gates) with visible progress → `complex-coding` lifecycle / technical PM builds + proves → `pmaudit` genuinely audits every DONE → `boardserve` shows the whole plan+progress on desktop/phone → hourly ledger + snapshot give full backtrack context.

## Source attribution

All skills authored by Hermes Agent (Nous Research) and contributed vetted to this registry. Merged/deduplicated per the 79% rule.
