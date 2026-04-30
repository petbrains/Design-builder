# design-builder — design plugin for Claude Code

Build distinctive production-grade interfaces on **web** and **iOS** through 6 user-facing commands. Spec-first: `/design_page` and `/design_screen` produce a markdown design spec; `/build` vendors it into source code. A knowledge-base skill (anti-patterns, motion, HIG, BM25 search) backed by `designlib` MCP (palettes, fonts, **inspiration_pages**, landing_patterns, icons) does the heavy lifting.

Built on top of five open-source projects: [Impeccable](https://github.com/pbakaus/impeccable), [Emil Kowalski Design Skill](https://emilkowal.ski/skill), [Taste Skill](https://github.com/Leonxlnx/taste-skill), [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), and [Design Motion Principles](https://github.com/kylezantos/design-motion-principles). See [NOTICE.md](NOTICE.md).

## The 6 commands

| Command | What it does | When to use |
|---|---|---|
| `/design-builder:setup` (alias `start`) | Interview → reference discovery → 2-3 direction candidates → HTML preview → emit `design-system.md`, `style-guide.md`, `content-library.md`, `tokens.css`, `preview.html`. | New project. You don't have a design foundation yet. |
| `/design-builder:design_page <name>` | Reads the foundation → pulls inspiration_pages → user picks → writes a design spec to `design/pages/<name>.md` (no code). | You want to plan a web page before shipping code. |
| `/design-builder:design_screen <name>` | Same, for app screens. Uses landing_patterns + iOS HIG. Spec adds Navigation context, Gestures, Safe areas. Writes to `design/screens/<name>.md`. | You want to plan an iOS / native screen before shipping code. |
| `/design-builder:build [target]` | Reads spec(s) from `design/pages/` and/or `design/screens/` → writes code to your source tree. Supports single (`build landing`), batch (`build all`), glob, or interactive multi-select. | After one or more specs exist and you want production code. |
| `/design-builder:improve [target]` | Light audit of code / Figma / screenshots → list of concrete fixes → apply mechanical ones (`Edit`). | Existing design. Something feels off. You want quick wins. |
| `/design-builder:review [target]` | Strict critique by `design-auditor` agent: composition, typography, color/WCAG, motion, AI-slop, anti-patterns, accessibility. P0-P3 report → `design/reviews/`. | Before shipping, or when `/improve` finished and you want full validation. |

Every command ends with a `Next:` block telling you what to do next.

## Install

```
/plugin marketplace add petbrains/design-builder
/plugin install design-builder@design-builder-marketplace
```

The `marketplace.json` at the repo root lets you add the repo as a marketplace source — no separate marketplace repo needed.

No `npm install` or `pip install` required. Scripts use stdlib only.

## Project output — `design/` folder

`/setup`, `/design_page`, `/design_screen`, `/build`, and `/review` write to `<your-project>/design/`:

```
design/
  design-system.md     # design system (palette, typography, spacing, mood, anti-patterns)
  style-guide.md       # a11y floor, platform constraints, density, motion, anti-patterns, states
  content-library.md   # voice & tone, UI states, forms, notifications
  tokens.css           # CSS variables (or tokens.json for non-web)
  preview.html         # visual preview of the system / page
  pages/               # design specs for web pages (markdown), one per page
  screens/             # design specs for app screens (markdown), one per screen
  references/          # your reference URLs + downloaded screenshots
  screenshots/         # YOU drop screenshots here for /review (later: playwright auto)
  reviews/             # P0-P3 audit reports (review-YYYY-MM-DD-HHMM.md)
  .cache/              # debug context for cross-command state (gitignored — interview.json, stack.json, ...)
```

**Recommended `.gitignore`:**
```
design/references/downloaded/
design/screenshots/
design/.cache/
```
(Version `design-system.md`, `style-guide.md`, `content-library.md`, `tokens.css`, `pages/`, `screens/`, `reviews/`. The downloaded binaries and `.cache/` debug state are noise.)

## Three-layer architecture

```
COMMANDS         →  /setup · /design_page · /design_screen · /build · /improve · /review
SKILL (rules)    →  Layer 2 filters · Layer 1 resolvers · knowledge base
LAYER 1 SOURCES  →  Project tokens · designlib MCP (inspiration_pages, palettes, ...) · CSV · iOS HIG · free
```

Every command's output is gated through six Layer 2 filters (Direction, Dials, Aesthetics, Anti-Patterns, Distinctiveness Gate, Output Rules) before emit. Skipping Layer 2 = "AI slop". Detail: [`skills/design/references/architecture.md`](skills/design/references/architecture.md).

## inspiration_pages — the new whole-page reference

`designlib` MCP exposes 405 inspiration_pages (sourced from land-book): full-page references with palette / typography / sections / mood / generation_prompt. `/design_page` uses them as the primary seed for new page specs; `/build` then vendors the spec into code. Future: `inspiration_parts` (hero / CTA / paywall / pricing_table) — interface reserved.

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

- `commands/` — 6 user-facing slash commands (+ `start.md` alias for `setup`)
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
