# SuperDesign — Design Plugin for Claude Code & Cursor

Unified design skill for Claude Code **and Cursor**. Build distinctive production-grade interfaces on **web** and **iOS** (iOS 18 + iOS 26 Liquid Glass), organized around **5 lifecycle pipelines** on top of 22+ atomic commands, enforced by a three-layer architecture, with one isolated-context sub-agent for heavy audits.

Built on top of five open-source projects: [Impeccable](https://github.com/pbakaus/impeccable), [Emil Kowalski Design Skill](https://emilkowal.ski/skill), [Taste Skill](https://github.com/Leonxlnx/taste-skill), [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), and [Design Motion Principles](https://github.com/kylezantos/design-motion-principles). See [NOTICE.md](NOTICE.md) for full attribution.

## What's new in v1.2

- **Visual design-system preview** — `/design system` now renders three candidate aesthetic directions as a single HTML file with `1 / 2 / 3` switcher, so you pick visually instead of from a text description. Apply ≠ approve: nothing is written to your project until you choose. Platform-aware (web mocks for web, faux iPhone frame for iOS).
- **Distinctiveness Gate** — new Layer-2 filter that catches generic-but-technically-clean output (the kind that passes anti-pattern checks but reads as "any LLM could have made this"). HARD on `/design system` (failed candidates regenerated silently), SOFT on `/design craft` (output shown with a `Risks taken & gaps` block).
- **Pipeline order is enforced** — for new projects the entry point is always `/design start`, never `/design make`. Free-form briefs in chat no longer auto-route past the variation pick or the UX brief.
- **One sub-agent** — `design-auditor` is the only sub-agent: heavy multi-file reads + structured P0–P3 report. Earlier v1.2 shipped six agents; the others were folded back into inline SKILL.md logic to avoid delegation unpredictability and rule drift between Claude Code and Cursor.
- **Cursor support** — `.cursor-plugin/plugin.json` mirrors the `.claude-plugin/` layout. Skills are shared one-to-one. In Cursor every command runs inline (no agent isolation), but the logic and output are identical.
- **Slimmer SKILL.md** — Frontend-Aesthetics DO/DON'T detail (typography, color, layout, interaction, responsive, haptics, UX writing) lives in the dedicated `references/*.md` files instead of inline. Top-level guard-rails (Absolute Bans, Output Rules, Technical Rules) stay in the main skill.

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

SuperDesign also runs in Cursor via `.cursor-plugin/plugin.json` (mirrors the `.claude-plugin/` layout). Copy or clone the repo into Cursor's plugins directory; Cursor auto-discovers the manifest and loads `skills/design/` plus the shared `.mcp.json` at the repo root (designlib + figma MCP servers).

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

## Sub-agents (Claude Code)

One specialised agent owns the heaviest read-only logic. Claude Code routes the audit commands to it automatically; the agent runs in an isolated context, loads its own references, and returns a compact structured result (`status`, `report_path`, `findings`, `layer2_checklist`).

| Sub-agent | Triggered by | What it does |
|---|---|---|
| `design-auditor` | `/design audit`, `/design review` step 1 | Scored P0–P3 audit: WCAG AA, Core Web Vitals, responsive, theming, anti-patterns, motion gap analysis; on iOS — Dynamic Type AX5, Reduce Motion, Increase Contrast/Transparency, accessibility labels, HIG. |

Every other command runs **inline** in the main skill — `/design system`, `/design craft`, `/design critique`, `/design polish --fix`, `/design brand|logo|cip|banner|slides`. Earlier v1.2 versions shipped six agents; the others were collapsed back inline because Claude doesn't reliably auto-delegate, and the rules had to live inline anyway for Cursor / non-CC environments. Maintaining identical logic in two places caused drift.

The `design-auditor` agent enforces a mandatory **Layer 2 pre-emit checklist** (Direction · Dials · Anti-Patterns · Output Rules · Aesthetics) — a `false` in any slot is treated as a hard failure. In Cursor the same audit logic runs inline through the main skill, with identical output.

## Figma integration

The Figma MCP server ships pre-configured in `.mcp.json` (`https://mcp.figma.com/mcp`). When connected, the skill picks it up automatically and routes Figma URLs through the right workflow:

- **Figma → code** — paste a `figma.com/design/...?node-id=...` URL into `/design make`. The skill loads design context, screenshots, and Code Connect mappings, then adapts the React+Tailwind reference into your project's stack.
- **Code → Figma (build a screen)** — `/design craft` with the Figma branch, when the user wants the screen *in* Figma rather than in code. Discovers your published design system via `search_design_system` and assembles the screen using Figma variables (no raw hex, no hardcoded sizes).
- **Build a Figma library** — `/design system` with the Figma branch creates variables and core components (Button, Input, Card, Nav, Avatar, Badge, Modal, Tabs, Divider, Icon) directly in the user's Figma file. Local tokens stay the source of truth; Figma is a materialisation.
- **Code Connect at scale** — `/design ship` step 4 batch-maps the codebase's design-system components to their Figma counterparts via `send_code_connect_mappings`.
- **Diagrams in FigJam** — board URLs (`figma.com/board/...`) route through `get_figjam` and `generate_diagram`.

Routing details: [`skills/design/references/figma/README.md`](skills/design/references/figma/README.md). Requires Cursor/Claude Code with the Figma MCP authenticated (Dev or Full seat for write actions).

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
- **`agents/`** — 1 Claude Code sub-agent (`design-auditor`) for `/design audit`. Other commands run inline.
- **`.cursor-plugin/plugin.json`** — Cursor manifest (mirrors `.claude-plugin/`)
- **`.mcp.json`** at repo root — shared MCP server config (read by Cursor; Claude Code keeps its `mcpServers` inline in `.claude-plugin/plugin.json`)
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
