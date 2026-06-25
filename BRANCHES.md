# Branch Index

_Last updated: 2026-06-25 by Claude Code_

---

## Active Branches

| Branch | Owner AI | Purpose | Last Updated | Status |
|--------|----------|---------|--------------|--------|
| `main` | All AIs | Amalgamated skills, no duplicates, production-ready | 2026-06-25 | Live |
| `claude` | Claude Code | All Claude skills, CLAUDE.md session context, deploy configs | 2026-06-25 | Active |
| `manus` | Manus AI | Manus AI modules and feature branches | 2026-06-25 | Pending creation |

### In `super-agent-os-replit`

| Branch | Purpose | Status |
|--------|---------|--------|
| `claude/alicloud-ubuntu-deploy-23lirb` | Primary dev + deploy branch (Claude Code) | **Active — HEAD at `7a1bdf4`** |
| `replit-CLAUDE-agent-os` | Old base branch from Replit setup | Archived, closed PR |
| `main` | Default repo branch | Exists but deploy target is LIVE-V1 |

### In `LIVE-V1-super-agent-os`

| Branch | Purpose | Status |
|--------|---------|--------|
| `main` | **Canonical production branch** — server pulls and deploys from here | **Live on server** |
| `Manus-AI-Super-Agent-OS` | Manus AI feature expansion (10 modules) | Pending review |

---

## Open Pull Requests

| Repo | # | Title | Branch → Target | Status |
|------|---|-------|----------------|--------|
| `super-agent-os-replit` | — | None open | — | Clean |
| `LIVE-V1-super-agent-os` | — | None open | — | Clean |

> PRs #1 and #2 in super-agent-os-replit were closed on 2026-06-25 — they were stale/conflicting and deployment is handled directly via server RunCommand, not PR merges.

---

## GitHub Actions (Automated Tasks)

| Repo | Workflow | Trigger | What It Does | Status |
|------|----------|---------|--------------|--------|
| All | None configured | — | No CI/CD yet | Not set up |

> Note: Deployment is currently manual via AliCloud RunCommand. No GitHub Actions needed until the project requires automated testing.

---

## Branch Ownership Rules

Each AI ONLY commits to its own branch:
- Claude Code → `claude/alicloud-ubuntu-deploy-23lirb` (in super-agent-os-replit)
- Manus AI → `Manus-AI-Super-Agent-OS` (in LIVE-V1-super-agent-os)
- Neither AI force-pushes to main/another AI's branch without explicit user instruction

---

## Plain English Notes for Non-Coders

**What is a PR?**  
A Pull Request (PR) is a formal proposal to merge one branch into another. It shows a diff of what changed, allows comments/review, then gets approved and merged — or rejected and closed. For this project, PRs are rarely needed since deployment happens via server command directly.

**What is a GitHub Action?**  
A GitHub Action is an automated script that runs when code is pushed. Common uses: run tests, check code style, deploy automatically. This project doesn't use them yet — deployment is done manually.

**What does "HEAD at X" mean?**  
HEAD is the name for the current latest commit. `7a1bdf4` is a short identifier (hash) for a specific commit. If you see this in the table, it means that's exactly which version of the code is live.

**Why close PRs instead of merging them?**  
For this project, merging a PR to `main` in super-agent-os-replit doesn't deploy anything — the server reads from LIVE-V1. Stale PRs that conflict with the current branch are more dangerous than useful, so they get closed.
