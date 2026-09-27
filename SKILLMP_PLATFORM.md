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

- `pmkanban.py` — the board CLI (state → TODO/KANBAN/PROGRESS/LEDGER/SNAPSHOT, evidence gates)
- `intent-router.py` — OpenRouter-faithful skill router (classify/rank/min-score/tier/live/create-cards)
- `research-stack.py` — live per-stage skill research from SkillsMP
- `boardserve.py` — responsive board server (desktop + phone), reads `pm/state.json`
- `pmaudit.py` — genuine audit of DONE claims vs evidence
- `board.html` — the responsive board UI

## How to inject into ANY agent or project

### Option A — copy the skill content into the agent's prompt
For any instruction-following AI: copy the relevant `skills/<name>/SKILL.md` into its system prompt or instruction set IA-aggressive. Plain text, no AI-specific format.

### Option B — install the tools on a machine
```bash
for f in /path/to/agent-brain/tools/*.py; do
  chmod +x "$f"; ln -sf "$(realpath $f)" /usr/local/bin/$(basename "$f" .py)
done
cp /path/to/agent-brain/tools/board.html /root/pm-boilerplate/web/ 2>/dev/null || true
```
Then in any project:
```bash
pmkanban init --project "my project" --doc docs/SPEC.md   # authoritative docs, no assumptions
intent-router --intent "profit via analyzer on Base" --repo .   # route skills
intent-router --create-cards .     # auto-seed pipeline onto the visible board
boardserve --port 8181 --proj .    # open http://<host>:8181/ on desktop or phone
pmaudit --proj .                   # audit DONE claims genuinely
```

### Option C — inject at session start (always-on)
Add `one-go-orchestrated-pm` (mindset) + `pm-kanban-todo` (board) + `genuine-audit` (not-lie) to the agent's persistent instructions so every session starts with the visible board and the honest-execution posture.

## How it works together

intent → `intent-router` classifies + ranks skills (share-of-success) + scans repo → auto-seeds the 7-stage pipeline as kanban cards → `pmkanban` tracks/proves each (evidence gates) with visible progress → `complex-coding` lifecycle / technical PM builds + proves → `pmaudit` genuinely audits every DONE → `boardserve` shows the whole plan+progress on desktop/phone → hourly ledger + snapshot give full backtrack context.

## Source attribution

All skills authored by Hermes Agent (Nous Research) and contributed vetted to this registry. Merged/deduplicated per the 79% rule.
