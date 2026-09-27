# Skills — Master Index

These are the amalgamated, AI-agnostic skills from the `main` branch. Any AI can use any skill here by reading the SKILL.md file and following the instructions.

---

## Available Skills

| Skill | Purpose | Trigger |
|-------|---------|---------|
| [`check-branch`](check-branch/SKILL.md) | Verify current branch, maintain BRANCHES.md, document PRs/Actions | Every session start, before every push |
| [`bounty-report-quality`](bounty-report-quality/SKILL.md) | STAR×6-component quality gate for bug bounty reports | Before writing any bounty report section |
| [`revenue-first`](revenue-first/SKILL.md) | Budget + revenue-first decision filter | Before every technical decision, tool choice, or feature design |
| [`deploy-server`](deploy-server/SKILL.md) | Deploy to AliCloud ECS via RunCommand | When deploying the Super Agent OS |
| [`qa-review`](qa-review/SKILL.md) | Final quality check before any submission, deployment, or delivery | Before any deliverable |
| [`task-execute`](task-execute/SKILL.md) | End-to-end agent task execution: discover → classify → assign → execute → verify | When running an agent task |
| [`deep-research`](deep-research/SKILL.md) | Fan-out web research, source verification, cited synthesis | When deep multi-source research is needed |
| [`h1-respond`](h1-respond/SKILL.md) | Write complete HackerOne report responses and triage comments | When responding to H1 reports |
| [`pm-kanban-todo`](pm-kanban-todo/SKILL.md) | Visible todo + kanban + milestones + progress + hourly ledger + snapshot (evidence gates) | When planning/tracking/executing a multi-step coding project, any agent |
| [`one-go-orchestrated-pm`](one-go-orchestrated-pm/SKILL.md) | One-go orchestrated execution fused with PM; coding + non-coding agents; loop/hallucination guards | When orchestrating execution end-to-end with full visible context |
| [`intent-aware-skill-router`](intent-aware-skill-router/SKILL.md) | OpenRouter-faithful skill router: classify intent → share-of-success → tier/fallbacks → components + auto-seed board | When an agent must route a task to the right skills/intent |
| [`genuine-audit`](genuine-audit/SKILL.md) | Serious auditing: claims verified, never lie; verdicts SUPPORTED/REFUTED/UNVERIFIED | Before accepting any agent's done/works claim or shipping a deliverable |

---

## How to Use

**Claude Code (via CLI):**
Skills in `.claude/skills/` are auto-loaded. Use `/SKILL_NAME` to invoke.

**Any other AI:**
Copy the content of the relevant SKILL.md file into your system prompt or instruction set. The skills are written in plain text and work with any instruction-following AI.

**Inject at session start:**
For always-on skills (check-branch, revenue-first), add them to your AI's persistent instructions or system prompt so they apply to every message.

---

## Source Attribution

All skills in this directory are the amalgamated result of contributions from registered agents (see `../AGENTS.md`). Original authoring AI is noted at the bottom of each SKILL.md.
