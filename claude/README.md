# Claude Code — Branch README

This is Claude Code's branch of the `agent-brain` central skills registry. It contains all skills in Claude Code CLI format plus the full session context.

---

## What's in This Branch

```
claude/
├── README.md          ← You are here
├── SKILL_INDEX.md     ← Index of all skills with triggers
└── skills/            ← Mirrored from .claude/skills/ in super-agent-os-replit
    ├── check-branch/SKILL.md
    ├── bounty-report-quality/SKILL.md
    ├── deploy-server/SKILL.md
    └── cli-first/SKILL.md
```

Skills in `../skills/` (main branch) are the portable versions.  
Skills here are the Claude Code CLI format with YAML frontmatter.

---

## Claude's Working Branch

**Repo:** `cryptostoner94/super-agent-os-replit`  
**Branch:** `claude/alicloud-ubuntu-deploy-23lirb`  
**Session context:** `CLAUDE.md` in repo root

Claude Code does NOT commit to `main` or other AI branches. Only to `claude/alicloud-ubuntu-deploy-23lirb`.

---

## Skill Format (Claude Code)

```
.claude/skills/SKILL_NAME/SKILL.md

---
name: skill-name
description: One sentence describing trigger and purpose
---

[Skill content in plain English]
```

Invoke with `/skill-name` in Claude Code CLI, or skills auto-trigger based on conditions defined in each skill.

---

## Updating Skills

When a skill is updated in `.claude/skills/` in the working repo:
1. Update the same skill here in `agent-brain/claude/skills/`
2. Check if the portable version in `agent-brain/skills/` also needs updating
3. Apply the 79% rule — if this creates a duplicate in `main`, merge instead
