# SuperDesign — Claude Code Plugin

Unified design skill for Claude Code. 22+ commands covering the full design lifecycle — UX planning, design-system generation, craft, audit, polish, brand, assets. Web + iOS (iOS 18 + iOS 26 Liquid Glass). Backed by BM25 search, iOS HIG references, designer motion perspectives (Emil Kowalski / Jakub Krehel / Jhey Tompkins), and 30+ anti-pattern checks.

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

## Quick Start

Once installed, invoke with the plugin namespace:

```
/superdesign:design teach         Set up your project's design context (run first)
/superdesign:design system        Generate a complete design token system (web/iOS/cross)
/superdesign:design craft         Build a distinctive interface from scratch
/superdesign:design shape         Plan UX/UI with structured discovery before code
/superdesign:design audit         Accessibility, performance, theming, anti-patterns, motion gaps
/superdesign:design animate       Add purposeful motion with designer-weighting (Emil/Jakub/Jhey)
/superdesign:design search query  BM25 search across 161 products, 67 styles, 57 fonts, and more
```

## All Commands

| Category | Commands |
|---|---|
| Foundational | `system`, `teach`, `shape`, `extract` |
| Craft | `craft` |
| Review & Quality | `audit`, `critique`, `polish`, `redesign` |
| Targeted Refinement | `animate`, `typeset`, `colorize`, `layout`, `clarify` |
| Intensity Modifiers | `bolder`, `quieter`, `distill`, `overdrive`, `delight` |
| Production | `harden`, `optimize`, `adapt` |
| Brand & Assets | `brand`, `logo`, `cip`, `banner`, `slides` |
| Utility | `search` |

All commands accept `--platform web|ios|cross` (or infer from project).

## What's Inside

- **`skills/design/SKILL.md`** — main skill definition with 22+ commands and design guidelines
- **`skills/design/data/`** — CSV databases for BM25 search (161 products, 67 styles, 161 colors, 57 fonts, 99 UX guidelines, 25 chart types, 15 tech stacks)
- **`skills/design/references/web/`** — typography, color, spatial, motion, interaction, responsive, style presets
- **`skills/design/references/web/motion/`** — designer perspectives (Emil Kowalski, Jakub Krehel, Jhey Tompkins), audit workflow, motion gap analysis
- **`skills/design/references/ios/`** — 19 HIG-sourced refs covering every iOS subsystem (color, layout, materials, motion, gestures, haptics, controls, navigation, modals, toolbar, icons, accessibility, ui-writing, first-run-states, ambient-surfaces, style-families, ipad, non-iphone-platforms)
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
