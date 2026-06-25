# AI Agents Registry

This file lists all AI agents authorized to work on this project, their branch names, and their specialties.

---

## Registered Agents

### Claude Code (Anthropic)
- **Branch:** `claude` (in agent-brain), `claude/alicloud-ubuntu-deploy-23lirb` (in super-agent-os-replit)
- **Specialty:** Full-stack TypeScript/React/Node.js, Docker deployment, bug bounty execution, skills authoring
- **Skills format:** `.claude/skills/SKILL_NAME/SKILL.md` with YAML frontmatter
- **Session context:** `CLAUDE.md` in repo root
- **Model:** `claude-haiku-4-5` (default), `claude-sonnet-4-6` (complex tasks), `claude-opus-4-8` (max quality)
- **Restrictions:** Cannot create repos outside `cryptostoner94/super-agent-os-replit` scope via GitHub MCP
- **Status:** Active

### Manus AI
- **Branch:** `manus` (in agent-brain), `Manus-AI-Super-Agent-OS` (in LIVE-V1-super-agent-os)
- **Specialty:** Feature modules, UI components, multi-module system builds
- **Skills format:** TBD (Manus uses its own task format)
- **Session context:** Manus maintains its own context
- **Last known action:** Pushed 10-module expansion to `Manus-AI-Super-Agent-OS` branch (2026-06-25)
- **Status:** Active (separate task queue from Claude)

---

## Rules for All Agents

1. **Own-branch-only:** Never commit to another AI's branch or to `main` directly
2. **No secrets in commits:** All credentials go through Doppler or environment variables only
3. **Update BRANCHES.md** after any branch creation, PR, or significant state change
4. **Check CLAUDE.md / session context** before asking the user for information already documented
5. **79% scope rule:** Before adding a skill to main, check if an existing skill covers 79%+ of the same ground. If yes — update the existing skill, don't add a duplicate.

---

## Adding a New Agent

To register a new AI agent:
1. Add an entry to this file following the format above
2. Create a branch named after the AI in this repo: `git checkout -b AGENT_NAME main`
3. Add the agent to BRANCHES.md
4. The agent itself should add its own skills directory and context file on first run

---

## Skill Injection — How Any AI Can Use These Skills

Every skill in `skills/` is plain text. To inject into any AI:

**For Claude Code:**
```
.claude/skills/SKILL_NAME/SKILL.md
```

**For OpenAI / GPT:**
Paste the content of `skills/SKILL_NAME/SKILL.md` into the system prompt or add as a knowledge document.

**For Manus AI:**
Add as a task template or include in the Manus instruction set.

**For any other AI:**
The skills are written in plain English — they work as-is for any instruction-following LLM.
