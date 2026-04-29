---
description: Universal code generator. Reads spec(s) from design/pages/ or design/screens/ and writes code to the project source tree. Single, batch, or glob targets.
argument-hint: "[target — spec name (e.g. 'landing'), 'all', or glob (e.g. 'pages/onboarding-*'); empty = pick from list]"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, mcp__designlib__get_animation
---

# /design-builder:build — generate code from spec(s)

You read one or more design specs (`design/pages/<name>.md` and/or `design/screens/<name>.md`) and emit code to the user's source tree. You do NOT design — that's `/design-builder:design_page` and `/design-builder:design_screen`. Activate the `design` skill.

## Phase 1 — Resolve target

Parse `$ARGUMENTS`:

- **Empty arg:** list all spec files in `design/pages/` and `design/screens/`. Present multi-select prompt:
  > "Available specs:
  >  - [ ] pages/landing
  >  - [ ] pages/pricing
  >  - [ ] screens/onboarding
  > Pick one or more (numbers, comma-separated; or `all`)"
- **Single name (e.g. `landing`):** search `design/pages/<name>.md` first, then `design/screens/<name>.md`. If both exist: prefer `pages/`, warn user that `screens/<name>.md` was also found.
- **Explicit path (`pages/landing` or `screens/onboarding`):** treat as the path.
- **`all`:** glob `design/pages/*.md` + `design/screens/*.md`.
- **Glob (`pages/onboarding-*`):** literal glob.

If 0 spec files resolved: stop with:
> "No specs found. Run `/design-builder:design_page <name>` or `/design-builder:design_screen <name>` first."

If exactly 1 spec: single-spec mode. If N > 1: batch mode (Phase 4 batch behavior).

## Phase 2 — Stack & system check (BLOCKING)

Read in order:
1. `design/.cache/stack.json` (Phase 0.5 of `/setup`).
2. `design/design-system.md` (`## Stack` section if `.cache/stack.json` is missing — fallback for migrated v2.0 projects, but log a warning that stack.json was missing).
3. `design/style-guide.md` (tokens, contrast rules, motion rules, anti-patterns full prose).
4. `design/content-library.md` (voice & tone, state patterns).

If `stack.json` says `project_initialized: false`:
> "Project not initialized. Per `design-system.md ## Stack`, run the scaffold command first (it was suggested in `/setup` Phase 0.4). Re-run `/build` after scaffolding."

If foundation files (design-system, style-guide, content-library) are missing → stop and point to `/setup`.

## Phase 3 — Per-spec build (loop)

For each spec in the resolved list (in order; sequential):

### 3.1 Read and parse the spec

Read the spec file (`design/pages/<name>.md` or `design/screens/<name>.md`) per the format in `skills/design/references/page-spec-format.md` (or `screen-spec-format.md`).

Validate per the format file's validation rules. On error:
- Single spec mode: stop with `spec malformed: <error>`. Do not proceed.
- Batch mode: log the error to the run's `Risks taken & gaps` block, skip this spec, continue.

Extract: title, sections (with composition / elements / slots / tokens / animation / states), components needed, animations, edge cases, navigation/gestures/safe-areas (if screen).

### 3.2 Vendor animations

For each entry in `## Animations` that references a catalog `animation.id`:
1. Determine target file: `src/components/animations/<component_filename>` (or framework-equivalent).
2. If file already exists at that path → skip (cache hit).
3. If not → call `mcp__designlib__get_animation(animation_id=<id>)`. From `prompt_text`, extract the **first** ` ```tsx ` or ` ```jsx ` fenced block. Write **verbatim** to the target path. Do not edit, do not retoken, do not rewrite imports.
4. Read `package.json` (web). For each library in `animation.libraries`:
   - Already in `dependencies` or `devDependencies` → continue.
   - Missing → record into the run's `Risks taken & gaps`. **Do NOT auto-install** (lockfile / CI / monorepo concerns are user's call).

For hand-rolled animations (lines marked `(hand-rolled, transform-only)` in the spec) → no vendoring; you'll write them inline in the page code in Phase 3.3.

For HIG spring animations (iOS specs only) → no vendoring; you'll write inline in the SwiftUI view in Phase 3.3.

### 3.3 Generate page/screen code

Determine output path from `stack.json`:

| Stack | Output path |
|---|---|
| Next.js App Router | `app/<slug>/page.tsx` |
| Next.js Pages Router | `pages/<slug>.tsx` |
| Vite + React | `src/pages/<slug>.tsx` |
| CRA / generic React | `src/pages/<slug>.tsx` |
| Vue (Vite) | `src/views/<Slug>View.vue` |
| Svelte | `src/routes/<slug>/+page.svelte` (Kit) or `src/<Slug>.svelte` (vanilla) |
| SwiftUI | `Sources/Views/<Slug>View.swift` (or project-specific) |
| Static HTML | `<slug>.html` + `<slug>.css` (in repo root unless project structure suggests otherwise) |

If the path convention is unclear (e.g. user has a custom Next.js setup with non-standard `app/` location): **ask before writing**, do not invent paths.

Generate the actual code:
- Walk the spec's `## Sections` in order. For each section, render the composition / elements / slot fills.
- All colors / typography / spacing reference `tokens.css` variables (web) or SwiftUI Theme (iOS) — no raw hex, no hardcoded font names.
- Slot markers in the spec (`<slot — verb-led, 2-3 words>`) get filled with project-voice copy from `content-library.md ## Voice & tone` principles.
- For animations: import vendored components and place them per Phase 4c.5 of v2.0 `/create` (HeroAnimation wraps section content, BackgroundAnim sits absolute behind, MagneticButton replaces plain button, etc.).

### 3.4 Apply tokens (mandatory)

Cross-check that all generated tokens reference `tokens.css` (web) or theme types (iOS). If a token reference results in a contrast pair that fails `style-guide.md` Section 1's table (the ❌ rows): swap to a passing pair (e.g. replace `--ink-muted` with `--ink-muted-strong` for nav text). Document the swap in Risks block.

### 3.5 Apply touch targets and motion durations

- Touch targets: every interactive element gets the platform minimum from `style-guide.md ## Touch targets` (44×44 web mobile, 44×44pt iOS, etc.).
- Motion durations: every transition/animation duration is one of the allowed scale values from `style-guide.md ## Motion rules`. No custom durations.
- prefers-reduced-motion: every CSS transition / framer-motion animation has the corresponding fallback per `style-guide.md`.

### 3.6 Apply content patterns

For each entry in spec's `## Edge cases`:
- Empty/error/success/loading/offline states use the structures from `content-library.md ## UI states`, instantiated with project-voice copy.
- Form validation messages use the templates from `content-library.md ## Forms ### Validation messages`.
- Notifications (toast/banner/dialog) use the format from `content-library.md ## Notifications`.

### 3.7 Run all six Layer 2 filters

Direction, Dials, Aesthetics, Anti-Patterns, **Distinctiveness Gate (HARD-with-1-retry)**, Output Rules.

The Distinctiveness Gate runs in **spec-honoring mode** here, not in spec-replacement mode: the Gate verifies the code preserves what the spec committed to (Layout posture honored, structural breaks present, anti-pattern bans respected). If the code drifted from the spec — regenerate ONCE.

If the Gate fails for reasons rooted in the spec itself (the spec was generic) — emit with `Risks taken & gaps` block noting that the spec needs revision via `/design-builder:design_page <slug>` (a re-design, not a re-build). Don't attempt to fix a generic spec inside `/build`.

### 3.8 Write the file(s)

Use `Write` for new files, `Edit` for surgical changes to existing files.

Single-spec progress message:
> "✓ Wrote `<path>` (<bytes> B)"

## Phase 4 — Batch mode behavior

When N > 1:

- Run sequentially (not parallel — shared source tree, potential path conflicts).
- Per-spec progress line: `[2/5] ✓ wrote app/landing/page.tsx (8.2 KB)`.
- If a spec fails (parse error, Distinctiveness Gate second-failure, path collision) → continue, don't abort. Aggregate failures into a single `Risks taken & gaps` block printed at the end.
- Vendored animation cache: when two specs reference the same `animation.id` with the same `component_filename`, copy once. Track copied filenames in a run-local set.
- If two specs vendor different animations to the same filename (rare collision): keep the first; surface the collision in Risks.
- Final summary line: `✓ Generated <N>/<N_total> specs. <skipped count> skipped — see Risks above.`

## Phase 5 — Stack-aware tweaks (inline reference)

| Stack | Notable rules |
|---|---|
| Next.js App Router | `'use client'` directive at top of any file with state/motion (anything using `useState`, `useEffect`, framer-motion's `motion.*`, etc.). RSC by default for static sections. |
| Next.js Pages Router | No `'use client'` directive (entire pages render on both sides). Wrap motion in `dynamic(... { ssr: false })` if SSR breakage observed. |
| Vite/CRA React | All client; no special directive. |
| SwiftUI | `@Observable` macro for view models on iOS 17+ (read minimum target from `Package.swift`); `ObservableObject` + `@Published` for older targets. Use `NavigationStack` (iOS 16+) over deprecated `NavigationView`. |
| shadcn/ui present | Don't reimplement `Button`, `Card`, etc. — import from `@/components/ui/<name>`. |
| Tailwind v4 | Tokens go in `@theme` block in `tokens.css` (CSS-first config). No `tailwind.config.js`. |
| Tailwind v3 | Tokens go in `tailwind.config.js` `theme.extend`. `tokens.css` augments with CSS custom properties. |
| Static HTML | One `<slug>.html` (full document, no bundler) + one `<slug>.css`. No JS framework imports. |

## Phase 6 — Next-step block

Pick variant matching state:

- Single, clean: "✓ Generated `<paths>`. **Next:** open the dev server, click through, then `/design-builder:review <slug>`."
- Batch, clean: "✓ Generated <N>/<N> specs cleanly. **Next:** dev server + click-through. `/design-builder:review` on one of them as a sanity check."
- With Risks: "✓ Generated with caveats (see Risks block above). **Next:** address them, or rerun the affected spec via `/design-builder:design_<page|screen> <name>` if the spec itself needs reshaping."
- Spec malformed (single-spec abort): "✗ Spec malformed: `<error>`. Fix the spec at `<path>` or regenerate via `/design-builder:design_<page|screen> <name>`."

## Failure modes to avoid

- **Auto-installing missing libraries.** Phase 3.2 surfaces missing deps in Risks. `npm install` is the user's call.
- **Editing vendored animation components.** Apply tokens to wrappers only; the vendored component is verbatim.
- **Writing code with raw hex / font-family / spacing.** Always reference tokens.
- **Inventing path conventions.** Phase 3.3 mandates asking when unclear.
- **Re-designing inside /build.** If Distinctiveness Gate's second failure is rooted in the spec being generic, that's a re-design (`/design_page` again), not a `/build` fix.
- **Parallelizing batch builds.** Sequential only — shared source tree.
- **Skipping the spec format validation.** Validation rules in `page-spec-format.md` and `screen-spec-format.md` are enforced; malformed spec stops single-spec mode and skips in batch mode.
