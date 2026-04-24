# SuperDesign — Claude Code Plugin

Unified design skill for Claude Code. Build distinctive production-grade interfaces on **web** and **iOS** (iOS 18 + iOS 26 Liquid Glass), organized around **5 lifecycle pipelines** on top of 22+ atomic commands, enforced by a three-layer architecture.

Built on top of five open-source projects: [Impeccable](https://github.com/pbakaus/impeccable), [Emil Kowalski Design Skill](https://emilkowal.ski/skill), [Taste Skill](https://github.com/Leonxlnx/taste-skill), [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), and [Design Motion Principles](https://github.com/kylezantos/design-motion-principles). See [NOTICE.md](NOTICE.md) for full attribution.

## Install

SuperDesign is distributed as a Claude Code plugin. Install it via the plugin marketplace:

```
/plugin marketplace add petbrains/superdesign
/plugin install superdesign@superdesign-marketplace
```

The `marketplace.json` at the repo root lets you add the repo itself as a marketplace source — no separate marketplace repo needed.

Alternatively, clone the repo into your project's plugin search path.

No `npm install` or `pip install` required. All scripts use standard library only.

### Install in Cursor

SuperDesign also runs in Cursor via the root `plugin.json`. Copy or clone the repo into Cursor's plugins directory; Cursor auto-discovers the manifest and loads `skills/design/` plus the shared `.mcp.json` (designlib + figma MCP servers).

```
git clone https://github.com/petbrains/superdesign.git ~/.cursor/plugins/superdesign
```

Sub-agents in `agents/` are Claude Code–only. In Cursor, each `/design` command runs inline in the main context — same logic, same references, same output.

## How it works — three-layer architecture

```
Layer 3: PIPELINES         →  start · make · refine · review · ship
Layer 2: DESIGN FILTERS    →  Direction · Dials · Aesthetics · Anti-Patterns · Output Rules
Layer 1: KNOWLEDGE BASE    →  Project · MCP (designlib, figma) · CSV · iOS HIG refs
```

**The rule:** every design decision flows top-down. Pipelines call atomic commands; every atomic's output is gated through Layer 2 filters; all facts come from Layer 1 sources in a fixed order (project → MCP → CSV → HIG → free-gen). Skipping Layer 2 is the #1 cause of generic "AI slop" output, so the skill enforces it.

Full architecture: [`skills/design/references/architecture.md`](skills/design/references/architecture.md).

## The 5 Pipelines (start here)

| Pipeline | When to use | What it composes |
|---|---|---|
| **`/superdesign:design start`** | New project — need context, tokens, brand foundation | `teach` → `system` → `shape` → `extract` (opt) → `brand` (opt) |
| **`/superdesign:design make`** | Build an interface from scratch with a system in place | `craft` → `typeset` → `colorize` → `layout` → `animate` |
| **`/superdesign:design refine`** | Interface built but needs character tuning | `critique` → `bolder` \| `quieter` \| `distill` \| `overdrive` \| `delight` → `clarify` → `polish` |
| **`/superdesign:design review`** | Formal quality gate before shipping | `audit` → `critique` → `polish --fix` |
| **`/superdesign:design ship`** | Final production pass | `harden` → `optimize` → `adapt` |

Every pipeline supports `--platform web\|ios\|cross`, `--from <step>`, `--skip <step>`, `--dry-run`, `--step` (interactive). Detailed runbooks: [`skills/design/references/pipelines.md`](skills/design/references/pipelines.md).

## Quick Start

```
/superdesign:design start         Kick off a new project (runs teach → system → shape)
/superdesign:design make          Build an interface (runs craft → typeset → colorize → layout → animate)
/superdesign:design review        Quality gate (runs audit → critique → polish --fix)
/superdesign:design search query  BM25 search across 161 products, 67 styles, 57 fonts, …
```

Power users and single-task work can still invoke any atomic command directly — pipelines are the recommended entry for newcomers and standard lifecycle work.

## Atomic Commands (all 22+ still available)

| Category | Commands | Usually called via |
|---|---|---|
| Foundational | `system`, `teach`, `shape`, `extract` | `start` |
| Craft | `craft` | `make` |
| Targeted refinement | `animate`, `typeset`, `colorize`, `layout`, `clarify` | `make`, `refine` |
| Intensity modifiers | `bolder`, `quieter`, `distill`, `overdrive`, `delight` | `refine` |
| Review & quality | `audit`, `critique`, `polish`, `redesign` | `refine`, `review` |
| Production | `harden`, `optimize`, `adapt` | `ship` |
| Brand & assets | `brand`, `logo`, `cip`, `banner`, `slides` | standalone |
| Utility | `search` | standalone |

All commands accept `--platform web\|ios\|cross` (or infer from project).

## What's Inside

- **`skills/design/SKILL.md`** — main skill definition: architecture, pipelines, atomic commands, filters
- **`agents/`** — 6 Claude Code sub-agents (`design-auditor`, `design-critic`, `motion-auditor`, `design-system-architect`, `brand-agent`, `polish-fixer`) that own the heavy review and generation logic in isolated contexts
- **`plugin.json`** + **`.mcp.json`** at repo root — Cursor manifest and shared MCP server config
- **`skills/design/references/architecture.md`** — three-layer model + extension points
- **`skills/design/references/pipelines.md`** — lifecycle pipeline runbooks
- **`skills/design/data/`** — CSV databases (161 products, 67 styles, 161 colors, 57 fonts, 99 UX guidelines, 25 chart types, 15 tech stacks)
- **`skills/design/references/web/`** — typography, color, spatial, motion, interaction, responsive, style presets
- **`skills/design/references/web/motion/`** — designer perspectives (Emil Kowalski, Jakub Krehel, Jhey Tompkins), audit workflow, motion gap analysis
- **`skills/design/references/ios/`** — 18 HIG-sourced refs covering every iOS subsystem (color, layout, materials, motion, gestures, haptics, controls, navigation, modals, toolbar, icons, accessibility, ui-writing, first-run-states, ambient-surfaces, style-families, ipad, non-iphone-platforms)
- **`skills/design/scripts/`** — BM25 search engine (Python), design system generator (Python), anti-pattern detector (Node.js)
- **`skills/design/templates/`** — starter templates (iOS SwiftUI theme: Color, Typography, Spacing, Motion, Haptics; web CSS/Tailwind/shadcn)

## Optional: designlib MCP

For authoritative style/palette/font/domain tokens across web + iOS, connect the designlib MCP server:

```
claude mcp add --transport http designlib https://designlib-production.up.railway.app/mcp
```

Without it, the plugin falls back to the local CSV databases (still covers 161 products × 67 styles × 57 fonts).

## License

MIT. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).
