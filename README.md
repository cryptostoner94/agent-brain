# Agent Brain — Central AI Skills Registry

**What this is:** A single source of truth for all AI agent skills, configs, and session context. Every AI agent working on this project has its own branch here. The `main` branch is the clean, deduplicated amalgamation of all of them.

**Live deployment:** https://portal.commetai.ca  
**Primary project repo:** `cryptostoner94/super-agent-os-replit`

---

## For Non-Coders — Plain English Guide

### What is a branch?
A branch is like a separate notebook for each AI. Claude writes in the `claude` branch. Manus AI writes in the `manus` branch. They don't overwrite each other. When both have written something useful, a human (or the AI) combines the best of both into `main`.

### What is `main`?
Main is the final, clean version. It only contains skills that have been reviewed, deduplicated, and confirmed working. Think of it as the "published edition" — the branches are the drafts.

### What is a skill?
A skill is a set of instructions that tells an AI how to handle a specific type of task — writing a bug report, deploying code, reviewing quality, etc. Skills live in the `skills/` folder. Any AI can read and use a skill from `main`.

### What is the 79% rule?
If two AI agents have a skill that does the same job (more than 79% topic overlap), they get merged into one combined skill in `main` rather than keeping two near-identical versions. This prevents bloat and keeps main clean.

---

## Repository Structure

```
main branch
├── README.md              ← You are here
├── BRANCHES.md            ← Index of all active branches, PRs, Actions
├── AGENTS.md              ← Registered AI agents + their branch names
├── MERGE-RULES.md         ← How skills graduate from branch → main
└── skills/                ← Amalgamated, AI-agnostic skills
    ├── README.md
    ├── check-branch/
    ├── bounty-report-quality/
    ├── revenue-first/
    ├── deploy-server/
    ├── qa-review/
    ├── task-execute/
    ├── deep-research/
    └── h1-respond/

claude branch (everything in main, plus):
├── .claude/
│   └── skills/            ← Claude Code CLI format (frontmatter + SKILL.md)
└── CLAUDE.md              ← Claude's full session context

manus branch (everything in main, plus):
└── manus-config/          ← Manus AI format
```

---

## How to Add a New AI Agent

1. Create a branch named after the AI: `git checkout -b manus main`
2. Add the AI to `AGENTS.md`
3. Update `BRANCHES.md`
4. Add the AI's skills to its branch in whatever format that AI uses
5. When ready to share skills with others: open a PR to `main`

## How to Inject Skills into Any AI

Every skill in `skills/` is written in plain text — no AI-specific format. To use a skill:
- Copy the content of `skills/SKILL_NAME/SKILL.md` into the AI's instruction/system prompt
- Or reference the raw GitHub URL as a skill source

---

## Current AI Agents

| Agent | Branch | Specialty | Status |
|-------|--------|-----------|--------|
| Claude Code | `claude` | Full-stack dev, deploy, bounty execution | Active |
| Manus AI | `manus` | Feature development, module building | Active (Manus-AI-Super-Agent-OS branch in LIVE-V1) |

---

## Maintenance

This repo is maintained automatically. Each AI updates its own branch after every session. `main` is updated by merge when skills are stable.
