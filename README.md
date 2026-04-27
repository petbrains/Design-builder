# design-builder — design plugin for Claude Code

Build distinctive production-grade interfaces on **web** and **iOS** through 4 user-facing commands. A knowledge-base skill (anti-patterns, motion, HIG, BM25 search) backed by `designlib` MCP (palettes, fonts, **inspiration_pages**, landing_patterns, icons) does the heavy lifting; you stay in conversation with one of four entry points.

> **v2.0** — full rebrand from `superdesign 1.2`. Command-based architecture replaces the 22+ atomic / 5-pipeline model. See [CHANGELOG.md](CHANGELOG.md). For 1.2, pin to commit `f43fdcc`.

Built on top of five open-source projects: [Impeccable](https://github.com/pbakaus/impeccable), [Emil Kowalski Design Skill](https://emilkowal.ski/skill), [Taste Skill](https://github.com/Leonxlnx/taste-skill), [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), and [Design Motion Principles](https://github.com/kylezantos/design-motion-principles). See [NOTICE.md](NOTICE.md).

## The 4 commands

| Command                              | What it does                                                                                                | When to use                                                              |
|--------------------------------------|-------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| `/design-builder:setup` (alias `start`) | Interview → reference discovery → 2-3 direction candidates → visual HTML preview → emit `design/system.md`, `tokens.css`, `preview.html`. | New project. You don't have a design system yet.                          |
| `/design-builder:create [what]`      | Read your `design/system.md` → pull 2-3 inspiration_pages from the MCP → user picks → generate page code with your tokens. | You have a foundation. You want a new page (`landing`, `pricing`, `signup`, ...). |
| `/design-builder:improve [target]`   | Light audit of code / Figma / screenshots → list of concrete fixes → apply mechanical ones (`Edit`).        | You have an existing design. Something feels off. You want quick wins.   |
| `/design-builder:review [target]`    | Strict critique by `design-auditor` agent: composition, typography, color/WCAG, motion, AI-slop, anti-patterns, accessibility. P0-P3 report → `design/reviews/`. | Before shipping. Or when `/improve` finished and you want full validation. |

Every command ends with a `Next:` block telling you what to do next.

## Install

```
/plugin marketplace add petbrains/design-builder
/plugin install design-builder@design-builder-marketplace
```

The `marketplace.json` at the repo root lets you add the repo as a marketplace source — no separate marketplace repo needed.

No `npm install` or `pip install` required. Scripts use stdlib only.

## Project output — `design/` folder

Every `setup`/`create`/`review` writes to `<your-project>/design/`:

```
design/
  system.md            # design system (palette, typography, spacing, mood, anti-patterns)
  tokens.css           # CSS variables (or tokens.json for non-web)
  interview.md         # captured answers + decisions
  preview.html         # visual preview of the system / page
  references/          # your reference URLs + downloaded screenshots
  screenshots/         # YOU drop screenshots here for /review (later: playwright auto)
  reviews/             # P0-P3 audit reports (review-YYYY-MM-DD-HHMM.md)
```

**Recommended `.gitignore`:**
```
design/references/downloaded/
design/screenshots/
```
(Version `system.md`, `tokens.css`, `interview.md`, `reviews/`. The downloaded binaries are noise.)

## Three-layer architecture

```
COMMANDS         →  /setup · /create · /improve · /review
SKILL (rules)    →  Layer 2 filters · Layer 1 resolvers · knowledge base
LAYER 1 SOURCES  →  Project tokens · designlib MCP (inspiration_pages, palettes, ...) · CSV · iOS HIG · free
```

Every command's output is gated through six Layer 2 filters (Direction, Dials, Aesthetics, Anti-Patterns, Distinctiveness Gate, Output Rules) before emit. Skipping Layer 2 = "AI slop". Detail: [`skills/design/references/architecture.md`](skills/design/references/architecture.md).

## inspiration_pages — the new whole-page reference

`designlib` MCP exposes 405 inspiration_pages (sourced from land-book): full-page references with palette / typography / sections / mood / generation_prompt. `/create` uses them as the primary seed for new pages. Future: `inspiration_parts` (hero / CTA / paywall / pricing_table) — interface reserved.

Schema map: [`skills/design/references/inspiration_pages.md`](skills/design/references/inspiration_pages.md).
Resolver contract: [`skills/design/references/layer1-resolvers.md`](skills/design/references/layer1-resolvers.md).

## Sub-agent: `design-auditor`

`/review` delegates to `agents/design-auditor.md` — a sub-agent that loads many references (a11y, perf, HIG, motion, AI-slop criteria), greps the project, and returns a structured P0-P3 report. Heavy multi-file reads + structured output → an actual win for context isolation.

The audit covers: composition, hierarchy, focal point, rhythm, grid, typography, color, WCAG, motion, **AI-slop detector** (Distinctiveness Gate's 7 questions applied to as-built surfaces), anti-patterns, accessibility. iOS adds Dynamic Type AX5, Reduce Motion, Increase Contrast/Transparency, accessibility labels, HIG checks.

If no visual is available, the auditor runs in **code-only mode** and explicitly flags that composition / focal point / rhythm / mood-fit were not evaluated.

## Figma integration

The Figma MCP (`https://mcp.figma.com/mcp`) ships pre-configured. When connected, the plugin routes Figma URLs:

- `/improve <figma-url>` → reads design context + screenshot, plans fixes (writes back to Figma is deferred to a future version).
- `/review <figma-url>` → uses Figma as the visual source for the audit.

Routing detail: [`skills/design/references/figma/README.md`](skills/design/references/figma/README.md). Requires Figma MCP authenticated (Dev or Full seat for write actions in future versions).

## What's inside

- `commands/` — 4 user-facing slash commands (+ `start.md` alias)
- `skills/design/SKILL.md` — knowledge base, filters, Layer 1 resolvers
- `skills/design/references/` — deep documentation (web, iOS, motion, brand, figma, system, design-system, ui-styling, slides)
- `skills/design/data/` — CSV databases (UX guidelines, tech stacks, anti-patterns)
- `skills/design/scripts/` — BM25 search (Python), design system generator (Python), anti-pattern detector (Node.js)
- `skills/design/templates/` — starters (iOS SwiftUI theme, web CSS/Tailwind/shadcn)
- `agents/design-auditor.md` — sole sub-agent (used by `/review`)
- `.claude-plugin/` — Claude Code manifest + marketplace
- `.mcp.json` — `designlib` + `figma` MCP server config

## Optional: install `designlib` MCP standalone

Pre-configured in `.mcp.json`. To install standalone:

```
claude mcp add --transport http designlib https://designlib-production.up.railway.app/mcp
```

Without it, the plugin falls back to local CSV (palettes, styles, fonts) and to landing_patterns (no inspiration_pages). Recommended: keep it on.

## License

MIT. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).
