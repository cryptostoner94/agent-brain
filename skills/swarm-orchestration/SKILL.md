---
name: "swarm-orchestration"
description: "Run multi-agent swarms on the server: 5-agent beta testing, pre-deployment audits, and orchestrated deploys. Spawn agents in one go, let them fan out to sub-agents, stay scope-locked, move fast without losing quality. Trigger: beta test, pre-deploy audit, swarm, multi-agent run, e2e test."
---

# Skill: swarm-orchestration

**Purpose:** Execute test / audit / deploy work as a multilayer swarm of agents that stays
locked to scope and requirements, finishes fast, and never compromises quality.
**Trigger:** User asks for beta testing, a pre-deployment audit, or multi-agent execution.
**Source:** Jett (Muse)
**Last updated:** 2026-10-11

---

## Layer 0 — SSH: the execution plane

All swarm work runs on the user's server. This machine is only the launcher.

```bash
ssh -i ~/.ssh/id_ed25519 -o ConnectTimeout=15 root@161.97.77.153 '<command>'
```

- Plain `ssh root@161.97.77.153` may fail with "Permission denied" — retry with the explicit key above.
- Host key is already accepted. Never print secrets, keys, or env values; list key NAMES only.
- Server inventory: Docker 29.x; 13 agent CLIs — aider, opencode, cline, kilocode,
  openclaw, codex, claude (Claude Code), openhands, command-code, openai, ollama,
  dropstone (+ hermes host-only). `CONTEXT_DEV_API_KEY` set in both env `.env`
  files for context.dev documentation search. Removed 2026-10-12: fx, codeaf, grok, t3, qodo,
  coderabbit, taskmarket, coder-studio, cua-driver, spawn, adal, omp, polygraph, junie,
  tiny-agents, agent-canvas. Full registry: `/root/agent-env/AGENTS.md`.
- **BYOK rule (no exceptions except noted):** every agent uses ONLY the shared
  `OPENROUTER_API_KEY`. Exceptions: command-code and opencode may use their own
  subscriptions. Enforcement: `load.sh` (ENV 1) and `/etc/profile.d/byok.sh` (ENV 2)
  map provider keys onto the OpenRouter key and point base URLs at OpenRouter.
  No subscription credentials exist in either environment — agents fail closed
  rather than charging.
- **Two environments, same agents, same keys:**
  - **ENV 1 — server normal:** run CLIs as root directly. `source /root/agent-env/load.sh`
    exports the shared `OPENROUTER_API_KEY` (mode 600).
  - **ENV 2 — docker sandbox** (`/root/beta-sandbox/`, dev/testing only): isolated
    container with the full curated agent list + Chromium; agents work in `./workspace`
    (mounted at `/workspace`), never in live project folders.
    `docker compose up -d` → `docker compose exec sandbox bash`.
    Scale to parallel swarms: `docker compose up --scale sandbox=3 -d`.
- Prefer existing server agents over installing new ones. Use Docker for isolation:
  disposable test envs, heavy multi-swarm execution, anything that could pollute the host.

## Layer 1 — the 5-agent beta testing protocol

Proven 2026-10-11 against a live web app. Same shape every round:

1. **One prompt, five testers.** Write ONE core test prompt; give it unchanged to 5
   agents with different methodology personas:
   - `opencode` style — terminal-native loop, fast iterative parallel probes, terse reporting
   - `hermes` style — latency-obsessed, snappiness and responsiveness under rapid interaction
   - `cline` style — meticulous step-by-step, verifies every UI state transition
   - `aider` style — diff-oriented, cross-checks every UI claim against underlying API data
   - `openhands` style — systematic coverage sweep with small verification scripts
   Variation comes from independent exploration, not different instructions.
2. **Human POV, never backend-only.** Real browser (server: `/root/.hermes/bin/browser-use`;
   cloud fallback: browser-use skill). Desktop AND mobile viewport. Every page, every
   button, every flow. Measure: page loads, interaction latency — flag anything >3s.
3. **3–5 realistic end-to-end tasks** per tester, judged as a human: smooth? clear? correct?
   Plus resilience: reload mid-flow, bad input, rapid clicks, back/forward, session persistence.
4. **Safety (no exceptions):** paper / read-only only. Never sign or submit on-chain
   transactions, never connect a real wallet, never enter private keys or seeds, never
   spend funds. Report-only: document bugs, never fix without explicit instruction.
5. **Independent reports + synthesis.** Each tester writes
   `~/workspace/beta-tests/<project>/<persona>-report.md`: environment+method,
   PASS/FAIL with evidence (URLs, timings, exact error text), performance numbers,
   console errors, issues rated P0 (broken core flow) / P1 (degraded) / P2 (polish),
   one-paragraph human verdict. Then ONE synthesis: cross-tester agreement, verified
   claims only — never present an agent's self-report as established fact; re-verify
   load-bearing claims through an independent channel first.

## Layer 2 — pre-deployment audit with 5 agents

Same swarm shape, different checklist. Give all 5 the same audit prompt:

- Config & secrets: every required env present, no secrets in repo/logs, templates have blanks
- Health & wiring: health endpoints green, pages/routes resolve, API contracts match UI calls
- Data safety: migrations reversible, backups exist, rollback path tested or documented
- Failure modes: bad input, downstream outage, restart recovery — what breaks, what survives
- Docs: README/runbook accurate against the ACTUAL deployed state (verify, don't trust docs)
- Report format: same as Layer 1 (evidence + P0/P1/P2 + verdict: ship / ship-with-fixes / block)

## Layer 3 — orchestration mechanics

- **Fan out in one go:** spawn all top-level agents in a single block with minimal,
  self-contained briefs (task, outcome, constraints, facts needed). No coordinator
  unless the task genuinely needs one; never nest coordinators (token cost explodes —
  each spawn inherits full context).
- **Agents may spawn sub-agents** for parallel sub-tasks (max depth 2). The parent owns
  verifying the child's load-bearing claims before reporting upward.
- **Scope lock:** restate scope + requirements at the top of EVERY brief. Out-of-scope
  findings get parked in the report, never executed. Two modes, stated explicitly:
  `report-only` (test/audit) vs `execute` (deploy) — never mix them in one brief.
- **Verify, don't trust:** an agent's "done" proves liveness, not correctness. Check
  claims via independent reads: on-chain state, server config, file hashes, test exits.
- **Speed without quality loss:** parallel-first; human-paced request rates against small
  servers (no load-test floods); targeted re-verification instead of re-sending context;
  stop at evidence — don't gold-plate.

## Operating rules

1. Server first: use installed agents + Docker before installing anything anywhere.
2. Same prompt to all testers/auditors in a round — independence creates the variation.
3. Secrets stay sealed: used only with their intended service, never printed or logged.
4. Nothing goes live / no real funds move without the user's explicit instruction —
   explicit instruction is then honored without repeated blocking rounds.
5. When done, the synthesis (not the raw reports) is the deliverable the user sees.
