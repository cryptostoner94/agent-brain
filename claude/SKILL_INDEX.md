# Claude Code — Skill Index

All skills available to Claude Code in this project. Each is a `.claude/skills/SKILL_NAME/SKILL.md` file with YAML frontmatter.

---

## Active Skills

| Skill | Trigger | Location |
|-------|---------|----------|
| `check-branch` | Every session start, before every push | `.claude/skills/check-branch/SKILL.md` |
| `bounty-report-quality` | Before any bounty report section | `.claude/skills/bounty-report-quality/SKILL.md` |
| `revenue-first` | Before every technical decision | `~/.claude/skills/revenue-first/SKILL.md` (global) |
| `deploy-server` | When deploying to AliCloud ECS | `.claude/skills/deploy-server/SKILL.md` |
| `qa-review` | Before any submission or delivery | bundled |
| `task-execute` | When running marketplace tasks | bundled |
| `deep-research` | When deep multi-source research needed | bundled |
| `h1-respond` | When responding to H1 reports | bundled |
| `code-review` | When reviewing code changes | bundled |
| `security-review` | Before any security-sensitive change | bundled |

---

## Skill Invocation

**In Claude Code CLI:** Type `/SKILL_NAME` to invoke explicitly.  
**Auto-triggered:** Skills with "every session start" or "before every X" triggers fire automatically when those conditions are met.

---

## Adding a New Skill

1. Create `.claude/skills/NEW_SKILL/SKILL.md` with this header:
```yaml
---
name: skill-name
description: One sentence describing when and why to use this skill
---
```
2. Write the skill content (see existing skills as examples)
3. Add to this index
4. Add to `agent-brain/skills/` in portable format
5. Check against MERGE-RULES.md — if 79%+ overlap with existing skill, update instead of adding

---

## Skill Sources

- **Bundled** — built into Claude Code, available via `/SKILL_NAME`
- **Project** — `.claude/skills/` in this repo
- **Global** — `~/.claude/skills/` on the machine running Claude Code
- **agent-brain** — `agent-brain/skills/` — portable versions shared across all AIs
