---
description: Improve an existing design — light audit + apply concrete fixes to user code or Figma. Does not write to design/.
argument-hint: "[target — file path, directory, Figma URL, or 'screenshots' to scan design/screenshots/]"
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, mcp__plugin_figma_figma__get_design_context, mcp__plugin_figma_figma__get_screenshot, mcp__plugin_figma_figma__get_metadata
---

# /design-builder:improve — improve an existing design

You take a piece of existing design and make it concretely better. You DON'T produce a P0-P3 audit report (that's `/review`'s job); you produce specific, mechanical fixes and apply them.

Activate the `design` skill (`skills/design/SKILL.md`).

## Phase 1 — Resolve target

Parse the argument:
- File path or directory (e.g. `src/pages/landing.tsx`, `src/components/`) — read with `Read` / `Glob` + `Read`.
- Figma URL (`figma.com/design/...?node-id=...`) — call `mcp__plugin_figma_figma__get_design_context` and `get_screenshot`.
- `screenshots` (literal) — list `design/screenshots/`, treat the latest screenshots as the target.
- Combination: argument may include multiple, separated by spaces.

If no argument: ask the user what to improve. Don't scan the whole repo by default — too noisy.

Read `design/system.md` if it exists. The fixes must use the system's tokens; do not invent new ones unless explicitly requested.

## Phase 2 — Light audit (no full report)

Walk the target through these dimensions and capture concrete fixable items only:

1. **Tokens.** Hardcoded hex / font-family / spacing values that should reference tokens.
2. **Anti-patterns** (BAN 1-4 from `SKILL.md`). Any side-stripe borders, gradient text, AI-color (cyan-on-dark, purple-blue gradient), 3-equal-card rows.
3. **Accessibility — fixable subset.** Missing alt on `<img>`, missing `aria-label` on icon-only buttons, missing focus state, contrast under WCAG AA where token swap fixes it.
4. **Typography hierarchy.** Heading levels skipped (h1 → h3), inconsistent display/body pairing relative to `design/system.md`.
5. **Motion.** `window.addEventListener('scroll')` (replace with IntersectionObserver), animations on properties other than `transform`/`opacity` (web).
6. **Distinctiveness Gate** — only the items that have mechanical fixes (e.g. swap a generic Inter-only stack for the system's font pair).

**Skip pure judgment calls** (composition rebalancing, focal point reweighting, copy rewrites that need brand voice). Those go in the residuals list and are deferred to `/review` + manual rework.

## Phase 3 — Plan fixes

Print the fix list to the user:

```
Found <N> fixable items. Plan:

1. <file:line> — <what's wrong> → <what to change>
2. ...
N. ...

Apply all? (yes / pick / skip)
```

Wait for confirmation. If "pick", let the user select indices (e.g. "1, 3, 5-7").

## Phase 4 — Apply

For each approved fix:
- File-based: use `Edit` with exact `old_string` / `new_string`. Confirm read of the file first if not already read.
- Figma-based: generate a textual patch description (don't write to Figma in v2.0 — that requires `figma-use` skill and explicit user authorisation; future task).

After each fix is applied, briefly note "✓ <file:line> — <what changed>".

## Phase 5 — Verify

After all fixes applied:
- Re-read affected files.
- Confirm no syntax errors (eyeball; if a build/lint config is present, mention "consider running your linter to verify").
- Run `node skills/design/scripts/detect-antipatterns.mjs --fast <project_root>` if the file scope is web → confirm the anti-pattern count dropped.

## Phase 6 — Next-step block

End with a `Next:` block:
- "✓ Applied <N> fixes in <files>. **Next:** `/design-builder:review` — verify the fixes haven't broken composition."
- (Some fixes deferred) "✓ Applied <X> of <Y> fixes; <Y-X> need design judgment (see residuals list above). **Next:** `/design-builder:review <target>` for the full picture, then handle residuals manually."

## Failure modes to avoid

- **Producing a P0-P3 report.** That's `/review`. You produce mechanical fixes.
- **Editing files you didn't read first.** `Edit` will fail; even if it works, you might miss surrounding context.
- **Inventing tokens.** Use `design/system.md` tokens; if a fix needs a token that doesn't exist, flag it as a residual ("propose adding `--color-warning` to system, then return to apply").
- **Touching Figma via `use_figma`.** Out of scope for v2.0 (see spec §6 open-question 4).
