# TRAINING.md — Individual Agent Training Pack

Per-agent skill loads: each agent gets the skills that fit its role. Inject the listed skills' `SKILL.md` into that agent's prompt/instructions. Plain text, AI-agnostic.

## Choose your agent type

### A. Coding / technical agent (builds, MEV, resolvers, software)
Load these (in this order) into the system prompt:
1. **one-go-orchestrated-pm** — mindset: build in one go, skip redundant dry-runs, official-tool install direct. Loop/hallucination guards.
2. **pm-kanban-todo** — visible board + evidence gates: plan-of-action, progress, milestones, hourly ledger.
3. **intent-aware-skill-router** — route each task/intent to the right skill via classification + share-of-success + fallbacks.
4. **genuine-audit** — after delivery, audit claims genuinely (SUPPORTED/REFUTED/UNVERIFIED).
Also useful: `verification-and-proof`, `complex-coding-lifecycle`, `qa-review`, `revenue-first`.

Invocation card: `bds start` (init → seed → serve ALL visuals on a free port) → `audit` (pmaudit).

### B. Non-coding / day-to-day multi-task agent (scheduling, docs, follow-ups)
Load these:
1. **daily-multitask-pm** — prioritization by consequence, owners, deadlines, capacities, follow-ups (silence ≠ completion).
2. **pm-kanban-todo** — the same visible board, so the non-coding agent sees the same plan/progress as everyone.
Do NOT force coding skills on a non-coding agent — route by the nature of the work.

### C. Research agent (deep multi-source research)
Load these:
1. **deep-research** (existing) — fan-out research + source verification + cited synthesis.
2. **grounded-citations** — cite verifiable sources only.
3. **intent-aware-skill-router** — pick the right research skill for the query type.
4. **one-go-orchestrated-pm** — open-but-not-gullible posture; verify claims, cite truth only.

### D. Audit / QA agent
Load these:
1. **genuine-audit** — the auditor's charter: every claim verified, never lie.
2. **qa-review** (existing) — final quality gate.
3. **verification-and-proof** — evidence per deliverable type.
4. **pm-kanban-todo** — see DONE cards (they are the claims to audit).

## Injecting

**Any AI (no tooling):** copy each `skills/<name>/SKILL.md` content into the agent's system prompt / instruction set.

**Hermes / Claude-Code-style CLI agents:** install tools (see `SKILLMP_PLATFORM.md` Option B: `git clone`, symlink `tools/*.py` to `/usr/local/bin`) and inject the skill contents.

**Always-on mindset (recommended baseline for every agent):** always load `one-go-orchestrated-pm` (honest one-go execution) + `pm-kanban-todo` (visible board + evidence gates) + `genuine-audit` (claims verified, never lie).
