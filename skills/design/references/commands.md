# Commands

The plugin ships six user-facing commands plus one alias. Short forms used in flow examples: `/design_page`, `/design_screen`, `/build`, `/improve`, `/review`, `/setup`.

| Command | Purpose | Output |
|---|---|---|
| `/design-builder:setup` | Establish the design foundation (Phase 0 scaffold + stack detect, Phase 1-4 interview + reference picks, Phase 5 emit) | `design/design-system.md`, `design/style-guide.md`, `design/content-library.md`, `design/tokens.css`, `design/preview.html`, `design/pages/`, `design/screens/`, `design/references/`, `design/.cache/` |
| `/design-builder:start` | Alias for `/setup` | (same) |
| `/design-builder:design_page <name>` | Generate a design spec for a web page (markdown) | `design/pages/<name>.md` |
| `/design-builder:design_screen <name>` | Generate a design spec for an app screen (markdown) | `design/screens/<name>.md` |
| `/design-builder:build [target]` | Generate code from a spec (one / batch / glob) | Source files at stack-appropriate paths (e.g. `app/<name>/page.tsx`, `Sources/Views/<Name>View.swift`) |
| `/design-builder:improve [target]` | Light audit + apply concrete mechanical or restructure fixes | Patches to user files via Edit; no writes to `design/` |
| `/design-builder:review [target]` | Strict design critique (P0-P3) by the design-auditor sub-agent | `design/reviews/review-YYYY-MM-DD-HHMM.md` |

## Typical flows

**Brand-new project:**
`/setup` → `/design_page landing` → review the spec → `/design_page pricing` → review → ... → `/build all` → `/review` on key pages

**Existing project, single new page:**
`/design_page <name>` → review spec → `/build <name>` → `/review <name>`

**Existing page that needs polish:**
`/improve <path>` (mechanical) or `/improve <path> --restructure` (composition rebuild) — or re-spec with `/design_page <name>` and then `/build <name>` to fully regenerate.

**Audit pass:**
`/review <path>` → results inform `/improve <path>` next steps, or a full `/design_page <name>` → `/build <name>` cycle if structural issues are too deep for `/improve`.

## What was removed in v2.1

- `/design-builder:create` — removed. The "design + emit code in one step" flow caused two issues: (1) for non-landing apps, building screens one at a time as code is wrong (designers plan multiple screens before code); (2) stack detection happened too late and frequently fell through to plain HTML. Replaced by spec-first split: `/design_page` / `/design_screen` produce specs, `/build` produces code.
