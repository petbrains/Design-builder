# design-builder Plugin

This repository is a Claude Code plugin: `design-builder`. It bundles 4 slash commands, the `design` knowledge skill, and the `design-auditor` sub-agent.

Plugin manifest: `.claude-plugin/plugin.json`. Skill: `skills/design/SKILL.md`. Commands: `commands/`. Sub-agent: `agents/design-auditor.md`.

When the plugin is installed, users invoke commands as `/design-builder:<command>` — `setup`, `start` (alias of setup), `create`, `improve`, `review`.

## Structure

- `.claude-plugin/plugin.json` — Claude Code manifest (name, version, mcpServers via `.mcp.json`, commands at `./commands/`)
- `.claude-plugin/marketplace.json` — single-plugin marketplace (so the repo itself is installable as a marketplace source)
- `.mcp.json` — shared MCP server config (`designlib` + `figma`)
- `commands/` — 4 user-facing commands: `setup.md`, `start.md` (alias), `create.md`, `improve.md`, `review.md`
- `agents/design-auditor.md` — sole sub-agent. Used by `/review`. Returns P0-P3 report + JSON contract; supports `visual` / `code_only` / `mixed` modes; runs the AI-slop detector.
- `skills/design/SKILL.md` — knowledge skill: 3-layer model, Layer 2 filters (incl. Distinctiveness Gate), Layer 1 source order, `get_design_reference()` resolver (defined in `references/layer1-resolvers.md`), reference index.
- `skills/design/references/` — deep documentation (architecture, layer1-resolvers, inspiration_pages, commands, distinctiveness-gate, design-dials, designlib-mcp, ux-writing, web/, ios/, figma/, brand/, design/, slides/, system/, design-system/, ui-styling/)
- `skills/design/data/` — CSV databases for BM25 search
- `skills/design/scripts/` — Python (search, design_system, system preview) + Node (anti-pattern detector). Stdlib only.
- `skills/design/templates/` — starters (iOS SwiftUI theme, web CSS/Tailwind/shadcn, brand-guidelines starter)
- `NOTICE.md` — attribution for 5 source open-source projects
- `LICENSE` — MIT
- `CHANGELOG.md` — version history

## Architecture (three-layer rule)

Every command must: (1) resolve facts through Layer 1 in the fixed order (project tokens → designlib MCP → local CSV → iOS HIG → free generation), via `get_design_reference(type, filters)`; (2) pass candidate output through all six Layer 2 filters (Direction, Dials, Aesthetics, Anti-Patterns, Distinctiveness Gate, Output Rules); (3) emit. Silently skipping Layer 2 is the #1 cause of generic "AI slop" output.

Extension markers in code: `KB-EXTENSION` (Layer 1 source), `FILTER-EXTENSION` (new Layer 2 filter). Pipeline markers from v1.2 are removed — there are no pipelines.

## The 4 commands at a glance

| Command                              | Output target                                          |
|--------------------------------------|--------------------------------------------------------|
| `/design-builder:setup`              | `<project>/design/system.md`, `tokens.css`, `interview.md`, `preview.html`, `references/` |
| `/design-builder:create [what]`      | Source code in user's source tree (e.g. `src/pages/landing.tsx`); optional `design/preview.html` |
| `/design-builder:improve [target]`   | Patches user files via `Edit`; no writes to `design/` |
| `/design-builder:review [target]`    | `<project>/design/reviews/review-YYYY-MM-DD-HHMM.md` (delegates to `design-auditor`) |

Every command ends with a `Next:` block recommending the next concrete action.

## inspiration_pages (new in v2.0)

Primary Layer 1 source for whole-page references. 405 records via `mcp__designlib__list_inspiration_pages` / `get_inspiration_page` / `list_inspiration_page_facets`. Schema map: `skills/design/references/inspiration_pages.md`. Resolver contract: `skills/design/references/layer1-resolvers.md`.

**Critical contract notes:**
- MCP filters are SINGULAR strings (one `mood`, one `signature`, one `keyword`). To combine values, call multiple times and dedupe by `id`.
- List response returns a SUBSET of fields; deep-fetch via `get_inspiration_page(page_id=<id>)` for full payload (palette, typography, sections, generation_prompt, why_it_works).
- The deep-fetch param is `page_id`, not `id`.
- inspiration_pages are **web-only**; iOS / cross requests fall back to `landing_patterns` or HIG.

Future: `inspiration_parts` (hero/CTA/paywall/pricing_table) — interface reserved in `MCP_TOOL_MAP`. Until then, partial-page references can be filtered today via `good_for_stage='hero_section' | 'cta_band' | ...` on inspiration_pages.

## Cursor support

Dropped in v2.0. The `.cursor-plugin/` directory is removed. Reason: Cursor doesn't have a slash-command mechanism, and dual-maintaining the logic inline (for Cursor) plus in `commands/` (for Claude Code) caused drift. May return in v2.x if real Cursor users surface.

## Scripts

Python scripts use stdlib only — no `pip install`. Node anti-pattern detector works in `--fast` mode without npm dependencies.

## Plugin installation (for end users)

```
/plugin marketplace add petbrains/design-builder
/plugin install design-builder@design-builder-marketplace
```

Then `/design-builder:setup` for a new project, or any of `/create` / `/improve` / `/review` for existing work.

## v1.2 → v2.0 migration

Hard cut, no aliases. Users on 1.2 should pin to commit `f43fdcc` until they migrate. New install of 2.0 = fresh start with the 4 commands.
