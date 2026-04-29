---
description: Improve an existing design — light audit + apply concrete fixes to user code or Figma. Does not write to design/.
argument-hint: "[target — file path, directory, Figma URL, or 'screenshots'] [--restructure]"
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, mcp__designlib__list_inspiration_pages, mcp__designlib__get_inspiration_page, mcp__designlib__list_animations, mcp__designlib__get_animation, mcp__plugin_figma_figma__get_design_context, mcp__plugin_figma_figma__get_screenshot, mcp__plugin_figma_figma__get_metadata
---

# /design-builder:improve — improve an existing design

You take a piece of existing design and make it concretely better. You DON'T produce a P0-P3 audit report (that's `/review`'s job).

Two modes — pick based on the argument:

- **Default (mechanical mode).** Specific, scope-limited fixes: token swaps, anti-pattern removal, contrast bumps, motion-property fixes, accessibility-fixable subset. Composition is preserved.
- **`--restructure` mode.** Composition rebuild for one or more weak sections — replaces a generic section with one anchored on a fresh inspiration_pages reference filtered by `good_for_stage`. Use when an audit's creative P1 recommendation is "thread X through" / "rebuild Y as Z" / "section feels generic". DO NOT use mechanical mode for these — the documented v2.0 failure is gluing decorative fragments onto a generic section instead of rebuilding it.

Activate the `design` skill (`skills/design/SKILL.md`).

## Phase 1 — Resolve target

Parse the argument:
- File path or directory (e.g. `src/pages/landing.tsx`, `src/components/`) — read with `Read` / `Glob` + `Read`.
- Figma URL (`figma.com/design/...?node-id=...`) — call `mcp__plugin_figma_figma__get_design_context` and `get_screenshot`.
- `screenshots` (literal) — list `design/screenshots/`, treat the latest screenshots as the target.
- `--restructure` flag — if present, jump to the `--restructure` branch in Phase 2 instead of the mechanical-fix branch.
- Combination: argument may include multiple, separated by spaces.

If no argument: ask the user what to improve. Don't scan the whole repo by default — too noisy.

Read `design/design-system.md`, `design/style-guide.md`, and `design/content-library.md` if they exist. Fixes must use tokens from `design-system.md`; a11y findings reference rules from `style-guide.md`; voice & tone deviations reference principles from `content-library.md`. Do not invent new tokens unless explicitly requested.

**Mode selection heuristic.** If the user invoked `/improve` after a `/review` that flagged composition / distinctiveness / "section feels generic" / "thread X through" issues — default to suggesting `--restructure` for those specific sections. If user invoked `/improve` on a fresh design (no prior review) — default to mechanical mode. When ambiguous, ask: "Mechanical patches (tokens, anti-patterns, a11y) or restructure (rebuild a section from a fresh reference)?"

## Phase 2 — Light audit (no full report)

### Mechanical mode (default)

Walk the target through these dimensions and capture concrete fixable items only:

1. **Tokens.** Hardcoded hex / font-family / spacing values that should reference tokens.
2. **Anti-patterns** (BAN 1-4 from `SKILL.md`). Any side-stripe borders, gradient text, AI-color (cyan-on-dark, purple-blue gradient), 3-equal-card rows.
3. **Accessibility — fixable subset.** Missing alt on `<img>`, missing `aria-label` on icon-only buttons, missing focus state, contrast under WCAG AA where token swap fixes it (cross-check against design/style-guide.md ## Accessibility floor — the contrast table tells you which token swaps actually pass for THIS palette).
4. **Typography hierarchy.** Heading levels skipped (h1 → h3), inconsistent display/body pairing relative to `design/design-system.md`.
5. **Motion.** `window.addEventListener('scroll')` (replace with IntersectionObserver), animations on properties other than `transform`/`opacity` (web).
6. **Distinctiveness Gate — mechanical subset only.** Token-swap-fixable items (e.g. swap a generic Inter-only stack for the system's font pair, replace `--ink-muted` with `--ink-muted-strong` on small nav text).
7. **Motion gap (web/React only).** If `design/design-system.md` declares `MOTION_INTENSITY >= 6` AND the target file/section has zero animation imports (no `framer-motion`, `motion`, `gsap`, no `<motion.*>` JSX, no Framer hooks, no `useScroll`/`useSpring`/`useTransform`) — surface as a **residual**, not an auto-fix. Format: *"Motion dial is `<X>` but `<file:line>` has no animation. Run `/design-builder:improve <target> --restructure` and pick a `category=hero|background` animation, OR rerun `/design-builder:create <what>` with the dial honored."* Auto-vending an animation into existing user code without rebuild context is the documented v2.0 "gluing decor onto generic sections" anti-pattern — flag the mismatch, do not patch it.

8. **Voice & tone (mechanical subset).** Microcopy that contradicts `design/content-library.md ## Voice & tone` anti-examples (e.g. "Oops!" in error states, exclamation marks in form validation, hedging language in transactional copy). Surface as concrete swaps with the suggested replacement from `content-library.md`.

**Skip pure judgment calls in this mode** (composition rebalancing, focal point reweighting, "thread X through Y", "rebuild Z section"). Those require `--restructure` — surface them with: "These items need composition rebuild. Run `/improve <target> --restructure` for that. Mechanical fixes proceeding now."

### `--restructure` mode

Different shape entirely. You're rebuilding one or more weak sections from a fresh reference, not patching them.

1. **Identify target sections.** Either user named them ("rebuild StatsBand and FinalCTA") or you infer from the prior `/review` report's creative P1 items. List them explicitly and confirm with user.
2. **Per-section anchor resolution.** For each target section, map to a `good_for_stage` value and call `mcp__designlib__list_inspiration_pages(good_for_stage=<stage>, mood=<from design-system.md>, appearance=<from design-system.md>, limit=2)`. Deep-fetch the top result via `get_inspiration_page(page_id=<id>)`.
3. **Constraint check against `design/design-system.md`.** The fresh anchor must respect the system's palette / typography / token rules. If it conflicts (e.g. anchor uses gradients but system bans them), surface the conflict and offer: (a) pick the next anchor, (b) accept the conflict and document, (c) abort the section.
4. **Plan the rebuild.** State for each target section: old composition → new composition (concrete language: "left-aligned 3-column stats" → "off-grid stats with diagonal connecting hairlines, anchor on `page_xyz`"). NEVER plan as decorative addition to the existing composition — that's the documented v2.0 failure where decorative fragments got glued onto generic sections.
4a. **Animation lookup on rebuilt sections (gated).** If the rebuilt section is `hero_section` (always candidate), `cta_band` at `MOTION_INTENSITY >= 7`, or `feature_blocks` at `MOTION_INTENSITY >= 8` — AND the project is React — apply the same animation-vendoring step that `/create` runs in its Phase 4c.3 / 4c.5 (resolve via `mcp__designlib__list_animations`, deep-fetch via `mcp__designlib__get_animation`, extract TSX from `prompt_text`, write to `src/components/animations/`, import into the rebuilt section). The same surface cap applies (max 2 across the whole `--restructure` invocation, even across multiple sections). Library checks and `Risks taken & gaps` block are inherited from the `/create` contract — see `commands/create.md` Phase 4c.5 / 4c.6 for the full integration steps; do not duplicate the logic, follow it.
5. **Distinctiveness Gate runs HARD on the rebuild plan**, not on the current code. If the new composition fails Q1/Q4/Q7, pick a different anchor before proceeding. The Q7 escape-hatch (vendor an animation surface from the catalog) defined in `commands/create.md` Phase 4c.4 is also available here if Q7 is the only failing question.

## Phase 3 — Plan fixes

### Mechanical mode

Print the fix list to the user:

```
Found <N> fixable items. Plan:

1. <file:line> — <what's wrong> → <what to change>
2. ...
N. ...

Apply all? (yes / pick / skip)
```

Wait for confirmation. If "pick", let the user select indices (e.g. "1, 3, 5-7").

### `--restructure` mode

Print the rebuild plan per section:

```
Restructure plan:

§ <section name> (<file:lines>)
  Old: <one-line composition description>
  New: <one-line composition description>
  Anchor: <inspiration_page id> (good_for_stage=<stage>, mood=<m>)
  Why: <one-line — what brief / system constraint this serves>
  Risk: <one-line — what changes for the reader>

§ <next section>
  ...

Proceed all? (yes / pick / skip)
```

Wait for confirmation. If user rejects an anchor, offer the next one from the list query.

## Phase 4 — Apply

### Mechanical mode

For each approved fix:
- File-based: use `Edit` with exact `old_string` / `new_string`. Confirm read of the file first if not already read.
- Figma-based: generate a textual patch description (don't write to Figma in v2.0 — that requires `figma-use` skill and explicit user authorisation; future task).

After each fix is applied, briefly note "✓ <file:line> — <what changed>".

### `--restructure` mode

For each approved section:
- Read the target file fully if not already read.
- Replace the section's composition with the new one (use `Edit` for surgical replacements; use `Write` only if the entire file is being rewritten).
- Apply system tokens (no raw hex, no hardcoded font names — same constraints as `/create`).
- Note "✓ <file> § <section> — rebuilt from anchor <id>".
- After all sections done, run the layout-distinctiveness check from `/create` Phase 5 step 5 against the modified page. If the page still reads as default linear posture, the rebuild was insufficient — flag it.

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
- **Inventing tokens.** Use `design/design-system.md` tokens; if a fix needs a token that doesn't exist, flag it as a residual ("propose adding `--color-warning` to system, then return to apply").
- **Touching Figma via `use_figma`.** Out of scope for v2.0 (see spec §6 open-question 4).
- **Treating a creative P1 audit item as a mechanical fix.** "Thread X through" / "make Y feel like Z" / "section reads as generic" require `--restructure`, not decorative patches. The documented v2.0 failure: gluing zigzag fragments + corner dots onto generic sections after an audit asked to rebuild them. If you find yourself adding decorative SVG elements without changing the section's composition, you are in the wrong mode — stop and propose `--restructure`.
- **Auto-vending an animation in mechanical mode.** Phase 2 item 7 is a residual flag, not a fix. Vendoring `mcp__designlib__list_animations` output into existing user code without rebuild context = same v2.0 anti-pattern as decorative SVG gluing. Animation vendoring belongs in `--restructure` Phase 2 step 4a or in `/design-builder:create`, never in mechanical-mode `Edit`s.
