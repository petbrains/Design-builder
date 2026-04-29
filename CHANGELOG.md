# Changelog

## v2.1.0 — 2026-04-29

### Added
- **`/setup` Phase 0** — scaffolds `design/` folder structure (`pages/`, `screens/`, `references/`, `.cache/`) before any interview question. Detects project stack (Next.js / Vite / SwiftUI / Flutter / static HTML, plus Tailwind / shadcn variants), confirms with the user, suggests scaffold command if no project is initialized.
- **`/setup` Phase 5 emits three foundation files** instead of one:
  - `design/design-system.md` (tokens + Stack section)
  - `design/style-guide.md` (a11y values with numerical contrast computed via `compute_contrast.py`, touch targets, platform constraints, density/motion rules, full anti-pattern prose, component states required)
  - `design/content-library.md` (voice & tone, UI states, forms, notifications)
- **`/design_page <name>`** — new command. Produces a design spec (markdown) for a web page at `design/pages/<name>.md`. Documentation-aware (asks for PRD/brief/Figma URL up front, doesn't paraphrase). Animation choice fixed in spec; `/build` vendors the file later. Final gate offers Figma export, another spec, or `/build`.
- **`/design_screen <name>`** — new command. Same as `/design_page` for app screens. Uses `landing_patterns` + iOS HIG (inspiration_pages is web-only). Spec adds Navigation context, Gestures, Safe areas. Animation specs are HIG springs (catalog is React-only).
- **`/build [target]`** — new universal code generator. Reads spec(s) from `design/pages/` and/or `design/screens/`, writes code to source tree. Supports single (`build landing`), batch (`build all`), glob (`build pages/onboarding-*`), or interactive multi-select (`build` with no arg). Sequential, continue-on-fail. Stack-aware path conventions.
- `compute_contrast.py` — stdlib WCAG 2.1 contrast calculator. CLI: stdin JSON → stdout JSON.
- New references: `style-guide-template.md`, `content-library-template.md`, `page-spec-format.md`, `screen-spec-format.md`.

### Changed
- `/setup` no longer writes `design/interview.md` — captures live in `design/.cache/interview.json` (debug context, gitignored, not for users).
- `/improve`, `/review`, `agents/design-auditor.md` — read the three new foundation files; a11y findings cross-reference `style-guide.md` contrast table; voice findings cross-reference `content-library.md` principles.
- `skills/design/SKILL.md` — command map updated to 6 commands; Layer 1 source order extended (spec is primary Layer 1 source for `/build`).
- `references/architecture.md` — three-layer rule documents the spec as intermediate artefact between `/design_page` (synthesis) and `/build` (emit).
- `references/commands.md` — rewritten for the v2.1 command set.
- `.claude-plugin/plugin.json` — version 2.1.0, description updated.
- `design/references/` no longer has a `downloaded/` subfolder; reference images go directly into `design/references/` with `ref-` filename prefix for auto-downloads.

### Removed
- **`/create` command** — deleted. Hard cut from v2.0. The "design + emit code in one step" flow conflated planning and execution; v2.1 separates them with `/design_page` / `/design_screen` (planning) + `/build` (execution). For new v2.1 projects, run `/setup` then `/design_page <name>` then `/build <name>`.
- `design/interview.md` (was a v2.0 output) — data now lives in `design/.cache/interview.json`.

### Migration

No `--migrate` flag, no automated migration tooling. v2.1 is a hard cut for the project author (single user at this point). For older projects pinned to v2.0, stay on commit `4d331cc` until manually re-running `/setup` on v2.1.

## 2.0.0 — 2026-04-27

**Full rebrand to `design-builder`. Command-based architecture replaces pipeline/atomic model.**

### Added
- 4 user-facing commands: `/design-builder:setup` (alias `/start`), `/design-builder:create`, `/design-builder:improve`, `/design-builder:review`.
- `inspiration_pages` as the primary Layer 1 source for whole-page references (405 records via designlib MCP).
- Typed `get_design_reference(type, filters)` resolver in `skills/design/references/layer1-resolvers.md`.
- Standard project output folder `design/` with documented structure (system.md, tokens.css, interview.md, preview.html, references/, screenshots/, reviews/).
- AI-slop detector and code-only mode in `agents/design-auditor.md`.
- Mandatory `Next:` block at the end of every command output.

### Changed
- `agents/design-auditor.md` audit criteria expanded; output adds `mode: visual | code_only | mixed`.
- `skills/design/SKILL.md` slimmed: pipeline/atomic descriptions removed, knowledge base preserved.
- `skills/design/references/architecture.md` rewritten for command-based model.
- README and CLAUDE.md fully rewritten.

### Removed
- 22+ atomic commands (`/design system`, `/design craft`, `/design audit`, ...) — replaced by the 4 new commands.
- 5 lifecycle pipelines (`start`, `make`, `refine`, `review`, `ship`) — pipeline orchestration is gone.
- `.cursor-plugin/` — Cursor support dropped (may return in v2.x).
- `skills/design/references/pipelines.md`.

### Migration from 1.2
Hard cut, no aliases. Users on 1.2 should pin to commit `f43fdcc` (last v1.2 commit) until they migrate.

## 1.2.0 and earlier
See git history.
