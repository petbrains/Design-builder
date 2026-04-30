# design-builder

**Production-grade UIs from Claude Code — without the AI-slop look.**

A design plugin for Claude Code that turns AI-generated UI from "obviously AI" into something you'd actually ship. Real references, layered filters, spec-first workflow.

→ [Quickstart](#quickstart) · [The 6 commands](#the-6-commands) · [How it works](#three-layer-architecture)

---

## The problem we keep hitting

Ask Claude Code to design a UI. You get the same purple-to-pink gradient, the same generic card layout, the same "modern minimal" spacing every other AI-coded site has. The output isn't *bad* — it's median. And median is identifiable on sight.

The reason isn't model capability. It is missing inputs:

- No real design references — agents guess hex codes and font pairings
- No filters between concept and code — slop ships unedited
- No separation between *design* and *implementation* — every change re-rolls the dice

`design-builder` fixes the inputs.

---

## What sets it apart

**Real references, not vibes.** 405 `inspiration_pages` sourced from land-book, served via the `designlib` MCP — full pages with palette, typography, sections, mood, and generation prompt. Specs pull from these instead of inventing.

**Six layered filters.** Every command's output is gated through Direction → Dials → Aesthetics → Anti-Patterns → **Distinctiveness Gate** → Output Rules before emit. The Distinctiveness Gate catches most "looks AI-generated" outputs before they reach code.

**Spec-first.** `/design_page` and `/design_screen` write a markdown design spec. `/build` vendors that spec into source code. The spec is the contract — change the spec, regenerate the code.

**Sub-agent for review.** `/review` delegates to `design-auditor`, which loads a11y / perf / HIG / motion / anti-pattern references, runs WCAG checks, and returns a structured P0-P3 report.

---

## Quickstart

Install:

```
/plugin marketplace add petbrains/design-builder
/plugin install design-builder@design-builder-marketplace
```

Then in any project:

```
/design-builder:setup
```

That is it. The interview produces 2-3 direction candidates, you pick one, and you have a design foundation in `design/`. From there:

- **Web page** → `/design-builder:design_page <name>` → `/design-builder:build <name>`
- **iOS screen** → `/design-builder:design_screen <name>` → `/design-builder:build <name>`
- **Existing surface** → `/design-builder:improve` or `/design-builder:review`

No `npm install` or `pip install` required. Scripts use stdlib only.

---

## The 6 commands

| Command | What it does | When to use |
|---|---|---|
| `/design-builder:setup` (alias `start`) | Interview → reference discovery → 2-3 direction candidates → HTML preview → emit `design-system.md`, `style-guide.md`, `content-library.md`, `tokens.css`, `preview.html`. | New project. You do not have a design foundation yet. |
| `/design-builder:design_page <name>` | Reads the foundation → pulls inspiration_pages → user picks → writes a design spec to `design/pages/<name>.md` (no code). | You want to plan a web page before shipping code. |
| `/design-builder:design_screen <name>` | Same, for app screens. Uses landing_patterns + iOS HIG. Spec adds Navigation context, Gestures, Safe areas. Writes to `design/screens/<name>.md`. | You want to plan an iOS / native screen before shipping code. |
| `/design-builder:build [target]` | Reads spec(s) from `design/pages/` and/or `design/screens/` → writes code to your source tree. Single (`build landing`), batch (`build all`), glob, or interactive multi-select. | After one or more specs exist and you want production code. |
| `/design-builder:improve [target]` | Light audit of code / Figma / screenshots → list of concrete fixes → apply mechanical ones (`Edit`). | Existing design. Something feels off. You want quick wins. |
| `/design-builder:review [target]` | Strict critique by `design-auditor` agent: composition, typography, color/WCAG, motion, AI-slop, anti-patterns, accessibility. P0-P3 report → `design/reviews/`. | Before shipping, or when `/improve` finished and you want full validation. |

Every command ends with a `Next:` block telling you what to do next.

---

## Project output — `design/` folder

`/setup`, `/design_page`, `/design_screen`, `/build`, and `/review` write to `<your-project>/design/`:

```
design/
  design-system.md     # palette, typography, spacing, mood, anti-patterns
  style-guide.md       # a11y floor, platform constraints, density, motion, states
  content-library.md   # voice & tone, UI states, forms, notifications
  tokens.css           # CSS variables (or tokens.json for non-web)
  preview.html         # visual preview of the system / page
  pages/               # design specs for web pages (markdown), one per page
  screens/             # design specs for app screens (markdown), one per screen
  references/          # your reference URLs + downloaded screenshots
  screenshots/         # YOU drop screenshots here for /review (later: playwright auto)
  reviews/             # P0-P3 audit reports (review-YYYY-MM-DD-HHMM.md)
  .cache/              # debug context for cross-command state (gitignored)
```

**Recommended `.gitignore`:**

```
design/references/downloaded/
design/screenshots/
design/.cache/
```

Version `design-system.md`, `style-guide.md`, `content-library.md`, `tokens.css`, `pages/`, `screens/`, `reviews/`. The downloaded binaries and `.cache/` debug state are noise.

---

## Three-layer architecture

```
COMMANDS         →  /setup · /design_page · /design_screen · /build · /improve · /review
SKILL (rules)    →  Layer 2 filters · Layer 1 resolvers · knowledge base
LAYER 1 SOURCES  →  Project tokens · designlib MCP (inspiration_pages, palettes, ...) · CSV · iOS HIG · free
```

Every command's output is gated through six Layer 2 filters before emit. Skipping Layer 2 = AI slop.

Detail: [`skills/design/references/architecture.md`](skills/design/references/architecture.md).

---

## inspiration_pages — the whole-page reference

`designlib` MCP exposes 405 `inspiration_pages` (sourced from land-book): full-page references with palette / typography / sections / mood / generation_prompt. `/design_page` uses them as the primary seed for new page specs; `/build` then vendors the spec into code. Future: `inspiration_parts` (hero / CTA / paywall / pricing_table) — interface reserved.

- Schema map: [`skills/design/references/inspiration_pages.md`](skills/design/references/inspiration_pages.md)
- Resolver contract: [`skills/design/references/layer1-resolvers.md`](skills/design/references/layer1-resolvers.md)

---

## Sub-agent: `design-auditor`

`/review` delegates to `agents/design-auditor.md` — a sub-agent that loads many references (a11y, perf, HIG, motion, AI-slop criteria), greps the project, and returns a structured P0-P3 report. Heavy multi-file reads + structured output → an actual win for context isolation.

The audit covers: composition, hierarchy, focal point, rhythm, grid, typography, color, WCAG, motion, **AI-slop detector** (Distinctiveness Gate's 7 questions applied to as-built surfaces), anti-patterns, accessibility. iOS adds Dynamic Type AX5, Reduce Motion, Increase Contrast/Transparency, accessibility labels, HIG checks.

If no visual is available, the auditor runs in **code-only mode** and explicitly flags that composition / focal point / rhythm / mood-fit were not evaluated.

---

## Figma integration

The Figma MCP (`https://mcp.figma.com/mcp`) ships pre-configured. When connected, the plugin routes Figma URLs:

- `/improve <figma-url>` → reads design context + screenshot, plans fixes (writes back to Figma is deferred to a future version).
- `/review <figma-url>` → uses Figma as the visual source for the audit.

Routing detail: [`skills/design/references/figma/README.md`](skills/design/references/figma/README.md). Requires Figma MCP authenticated (Dev or Full seat for write actions in future versions).

---

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

---

## Optional: install `designlib` MCP standalone

Pre-configured in `.mcp.json`. To install standalone:

```
claude mcp add --transport http designlib https://designlib-production.up.railway.app/mcp
```

Without it, the plugin falls back to local CSV (palettes, styles, fonts) and to landing_patterns (no inspiration_pages). Recommended: keep it on.

---

## Part of Pet Brains

`design-builder` is one of three open-source tools we ship for builders who code with AI:

- **[mvp-builder](https://github.com/petbrains/mvp-builder)** — Document-Driven Development for Claude Code. Specs before code, TDD enforced, self-review catches stubs.
- **design-builder** — this repo. Production-grade UIs without the AI-slop look.
- **[designlib-mcp](https://github.com/petbrains/designLib-mcp)** — the design-knowledge MCP that powers design-builder. Works standalone in any MCP client.

Methodology and build films at [petbrains.dev](https://petbrains.dev) · YouTube [@petbrains](https://youtube.com/@petbrains)

---

## Credits

Built on top of five open-source projects: [Impeccable](https://github.com/pbakaus/impeccable), [Emil Kowalski Design Skill](https://emilkowal.ski/skill), [Taste Skill](https://github.com/Leonxlnx/taste-skill), [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), and [Design Motion Principles](https://github.com/kylezantos/design-motion-principles). See [NOTICE.md](NOTICE.md).

## License

MIT. See [LICENSE](LICENSE).