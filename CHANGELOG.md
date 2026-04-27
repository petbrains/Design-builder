# Changelog

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
