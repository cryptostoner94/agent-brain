# Merge Rules — How Skills Graduate from Branch to Main

The `main` branch is the clean, deduplicated master registry. Skills don't go directly to main — they earn their way in.

---

## The 79% Rule

Before adding or updating a skill in `main`, check: **does an existing skill in main already cover 79% or more of the same ground?**

**How to evaluate 79% overlap:**
- Do both skills trigger on the same kind of task?
- Do they share the same core purpose (e.g. both check quality, both handle deployment)?
- Would following one skill and then the other produce redundant instructions?

If YES to 2 or more of the above → they are candidates for merging.

**What to do when two skills overlap:**
1. Read both in full
2. Identify what each one has that the other doesn't
3. Write a single combined skill that captures ALL unique instructions from both
4. Credit both source AIs in the skill's frontmatter: `source: claude + manus`
5. Delete the two originals from main — only the combined version survives

---

## Path from Branch to Main

```
AI agent's branch
      │
      │  AI develops and tests the skill
      │  Skill is stable and working
      ▼
  Scope check
      │
      ├─ 79%+ match with existing main skill?
      │        YES → Combine, update existing entry, proceed
      │        NO  → New entry, proceed
      ▼
  Add to main/skills/SKILL_NAME/SKILL.md
      │
      │  Update BRANCHES.md (note what was merged)
      │  Update skills/README.md index
      ▼
  Main branch updated
```

---

## What Belongs in Main

**Yes:**
- Skills that are task-agnostic (work across multiple projects)
- Skills that have been tested and proven in real use
- Skills that any AI can use regardless of format

**No:**
- Project-specific config (Doppler tokens, server IPs, API keys) — these go in CLAUDE.md
- Half-finished skills — only stable, tested skills
- Duplicate functionality — if it's already covered, extend don't duplicate

---

## Attribution Format

Every skill in `main` must have attribution. Use this header format:

```
Source: AGENT_NAME
Last updated: YYYY-MM-DD
Combined from: AGENT1 + AGENT2  (only if merged)
```

---

## When Main Gets Messy — Cleanup Protocol

If main accumulates near-duplicate skills over time:
1. List all skills by trigger type (deployment, quality, research, etc.)
2. Group by overlap (same trigger + same purpose = candidates)
3. For each group: read all, write one combined version, delete the rest
4. Run a final check: can you explain each remaining skill in one sentence without overlapping another?

---

## No Force-Pushes to Main

Main is always built through merge, never force-pushed. This preserves the history of what was combined and when. If history is lost, the source of truth for each skill is lost with it.
