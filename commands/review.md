---
description: Strict design critique — composition, typography, color, accessibility, AI-slop, anti-patterns. Delegates to design-auditor agent. Writes report to design/reviews/.
argument-hint: "[target — file path, directory, Figma URL, 'screenshots', or empty for project-wide]"
allowed-tools: Task, Read, Glob, Grep, Bash, Write, mcp__plugin_figma_figma__get_design_context, mcp__plugin_figma_figma__get_screenshot, mcp__plugin_figma_figma__get_metadata
---

# /design-builder:review — strict design critique

You audit a piece of design and produce a P0-P3 report with actionable findings. You do NOT fix anything (that's `/improve`'s job).

Activate the `design` skill (`skills/design/SKILL.md`).

## Phase 1 — Determine input mode

Parse the argument:
- Figma URL → **mode = `visual` (Figma)**.
- `screenshots` (literal) or path under `design/screenshots/` → **mode = `visual` (screenshots)**.
- File path / directory / empty → check if visual is available:
  - `design/screenshots/` has files matching the target → **mode = `mixed`**.
  - No visual → **mode = `code_only`**.

Capture the chosen mode for the report.

## Phase 2 — Delegate to design-auditor

Before dispatching, read the project's three foundation files so the auditor has correct context:
- `design/design-system.md` — design intent, direction, token decisions
- `design/style-guide.md` — typography scale, color palette, spacing, accessibility floor (contrast table)
- `design/content-library.md` — voice & tone principles, copy patterns

Use the `Task` tool to invoke the `design-auditor` sub-agent (see `agents/design-auditor.md`). Pass:
- `project_path` — the resolved target root
- `platform` — `web` / `ios` / `cross` (infer from project: SwiftUI present → ios; tailwind/React → web; both → cross)
- `mode` — `visual` / `code_only` / `mixed` (from Phase 1)
- `scope` — glob if user narrowed (e.g. `src/pages/landing.tsx`)
- `figma_url` — if applicable
- `screenshot_paths` — list of screenshot files if applicable

The agent returns a JSON object with `status`, `report_path`, `findings`, `fixable_count`, `mode`, `layer2_checklist`. The agent also writes the full report to `design/reviews/review-YYYY-MM-DD-HHMM.md`.

If the `Task` tool / Agent infrastructure is unavailable for some reason: execute the audit logic inline by reading `agents/design-auditor.md` and following its dimensions, severity rubric, AI-slop detector criteria, and Layer 2 checklist. Output the same shape.

## Phase 3 — Surface results

Print to the user:
- The report path: `design/reviews/review-YYYY-MM-DD-HHMM.md`
- Counts: P0 / P1 / P2 / P3
- `fixable_count` (how many of P0+P1 are mechanically fixable by `/improve`)
- The mode used
- If `mode='code_only'`, the explicit caveat: "Visual aspects (composition, balance, focal point, rhythm, mood-fit) were NOT evaluated. Drop screenshots in `design/screenshots/` or supply a Figma URL and rerun for the full picture."

## Phase 4 — Next-step block

End with a `Next:` block:

- Found P0/P1: "✓ Report at `<path>`: <X> P0, <Y> P1, <Z> P2. **Next:** `/design-builder:improve <target>` — auto-fixes <fixable_count> of <X+Y> (P0+P1 with `fixable=true`); the rest need manual rework."
- All clean: "✓ <P0=0, P1=0>, <P2/P3 only>. **Next:** design is ready for human review — open Figma/code and walk through it; or `/design-builder:design_page <name>` to spec the next page."
- Code-only mode used: "✓ Code-only review at `<path>`. **Next:** drop screenshots in `design/screenshots/` and rerun for the full picture, or `/design-builder:improve` based on what we found."

## Future hooks (interfaces present, not implemented in v2.0)

- **playwright auto-screenshots (web).** Will populate `design/screenshots/` from project routes. For v2.0: tell the user "I can't capture screenshots automatically yet; please drop them in `design/screenshots/`."
- **Mobile screenshot pipeline.** For v2.0: tell the iOS user "drop App Store-format screenshots from your iOS Simulator into `design/screenshots/`."

## Failure modes to avoid

- **Editing code.** Review never edits. If the user wants edits, point them at `/improve`.
- **Hiding the code-only caveat.** When `mode='code_only'`, the caveat MUST appear in the user-facing summary, not just in the report file.
- **Skipping the report file.** Even short reviews must write to `design/reviews/` so the user has a paper trail.
