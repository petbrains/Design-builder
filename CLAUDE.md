# SuperDesign Plugin

This repository is a Claude Code plugin: `superdesign`. It bundles the `design` skill and supporting assets.

Plugin manifest lives at `.claude-plugin/plugin.json`. The skill is at `skills/design/SKILL.md`. When the plugin is installed, users invoke it as `/superdesign:design <command>` (e.g. `/superdesign:design system`, `/superdesign:design craft`).

## Structure

- `.claude-plugin/plugin.json` — Claude Code manifest (name, version, author, keywords)
- `.claude-plugin/marketplace.json` — single-plugin marketplace manifest (so the repo itself is installable as a marketplace source)
- `.cursor-plugin/plugin.json` — **Cursor manifest** (points at the same `skills/` and `.mcp.json`)
- `.mcp.json` — shared MCP server config (designlib + figma), read by both CC and Cursor
- `agents/` — **1 Claude Code sub-agent**: `design-auditor`. Used by `/design audit` and `/design review` step 1. The earlier v1.2 plugin shipped six agents; the others were collapsed back into inline SKILL.md logic in v1.2.x because they introduced delegation unpredictability without saving context. CC + Cursor both run the same inline logic everywhere except `/design audit`.
- `skills/design/SKILL.md` — main skill: three-layer architecture, agent-delegation block, 5 lifecycle pipelines, 22+ atomic commands, filters
- `skills/design/references/architecture.md` — three-layer model (Pipelines → Filters → Knowledge Base) + extension points
- `skills/design/references/pipelines.md` — lifecycle pipeline runbooks
- `skills/design/data/` — CSV databases for BM25 search
- `skills/design/references/` — deep design documentation (100+ files, including `web/motion/` with designer perspectives)
- `skills/design/scripts/` — BM25 search engine, design system generator, anti-pattern detector
- `skills/design/templates/` — starter templates (iOS SwiftUI theme, web CSS/Tailwind)
- `NOTICE.md` — attribution for 5 source open-source projects
- `LICENSE` — MIT
- `docs/superpowers/specs/` — integration specs (e.g. v1.2 design at `2026-04-24-v1.2-design.md`)
- `docs/superpowers/plans/` — implementation plans

## Scripts

Python scripts (`search.py`, `core.py`, `design_system.py`) use stdlib only — no pip install needed.
Node.js anti-pattern detector works in `--fast` mode without npm dependencies.

## Plugin installation (for end users)

```
/plugin marketplace add petbrains/superdesign
/plugin install superdesign@superdesign-marketplace
```

Then invoke `/superdesign:design start` to kick off a new project (runs teach → system → shape), or use any other pipeline: `make` / `refine` / `review` / `ship`. Power users can still call atomics directly (`system`, `craft`, `audit`, ...).

## Architecture (three-layer rule)

Every command — atomic or pipeline — must: (1) resolve facts through Layer 1 in the fixed order (project tokens → designlib MCP → local CSV → iOS HIG refs → free generation), (2) pass candidate output through Layer 2 filters (Design Direction, Dials, Aesthetics, Anti-Patterns, Output Rules), (3) emit. Silently skipping Layer 2 is the #1 cause of generic "AI slop" output. When adding features, use the extension markers (`KB-EXTENSION`, `FILTER-EXTENSION`, `PIPELINE-STEP-EXTENSION`, `PIPELINE-EXTENSION`) so changes are additive.

## Agent delegation (v1.2+)

In Claude Code, the main skill delegates one heavy operation to a sub-agent in `agents/`:

- audit / review step 1 → `design-auditor`

Every other command runs **inline** in the main skill. The earlier v1.2 plugin had six agents (`design-system-architect`, `design-critic`, `motion-auditor`, `polish-fixer`, `brand-agent`); they were removed because Claude doesn't reliably auto-delegate, and the rules still had to live inline anyway for Cursor / non-CC environments. Keeping them in two places caused drift. `design-auditor` survives because it's the only command with both qualities of a useful sub-agent: heavy multi-file reads and a structured P0–P3 report.

`design-auditor` loads its own references, enforces the Layer 2 checklist before emit, and returns a structured result (`status`, `report_path`, `findings`, `fixable_count`, `layer2_checklist`). In Cursor the same audit logic runs inline.
