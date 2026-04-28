---
description: Create a page / screen / section based on the project's design system. Pulls inspiration_pages from designlib MCP. Writes code to the project source tree.
argument-hint: "[what to create — e.g. 'landing', 'pricing page', 'signup screen']"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, mcp__designlib__list_inspiration_pages, mcp__designlib__get_inspiration_page, mcp__designlib__list_inspiration_page_facets, mcp__designlib__list_landing_patterns, mcp__designlib__get_landing_pattern, mcp__designlib__list_palettes, mcp__designlib__list_styles, mcp__designlib__list_font_pairs, mcp__designlib__list_animations, mcp__designlib__get_animation, mcp__designlib__list_animation_facets, mcp__plugin_figma_figma__get_design_context, mcp__plugin_figma_figma__get_screenshot
---

# /design-builder:create — generate a page or screen

You generate real, working code for a new page/screen/section. You do NOT scaffold a foundation; that's `/setup`'s job. Activate the `design` skill (`skills/design/SKILL.md`).

The user's argument tells you what to build — e.g. "landing", "pricing page", "signup screen", "about page". Map natural language to a `page_type` value from `inspiration_pages.md`'s vocab (the 11 valid `page_type` values).

## Phase 1 — System check (BLOCKING)

Read `design/system.md` from the project root.

- **If present:** read it fully. Capture: chosen direction name, palette role mappings, font pair, spacing scale, mood, anti-pattern notes. This is your design law for the rest of the run.
- **If missing:** stop. Ask the user one question:

  > "I don't see `design/system.md` — no design system in this project yet. What should I anchor on? Options:
  > 1. Give me a URL / screenshot / Figma link as a one-shot reference.
  > 2. Point me to existing code that should set the style.
  > 3. Run `/design-builder:setup` first (~10 minutes; produces a foundation we can reuse for every later page)."

Wait for response. If they pick (3), suggest they run `/setup` and stop. If (1) or (2), capture the reference into context for this run only — do not write `design/system.md` (that's `/setup`'s job).

## Phase 2 — Page type and filters

Pick `page_type` from the user's argument. Map natural language:

| User says                                | `page_type`        |
|------------------------------------------|--------------------|
| "landing", "marketing", "homepage"       | `marketing_landing`|
| "pricing", "plans"                       | `pricing`          |
| "signup", "register", "join"             | `signup`           |
| "about"                                  | `about`            |
| "blog list", "blog index", "articles"    | `blog_index`       |
| "blog post", "article"                   | `blog_post`        |
| "portfolio", "work"                      | `portfolio`        |
| "store", "shop home"                     | `ecommerce_home`   |
| "product list", "catalog"                | `product_listing`  |
| "product detail", "product page"         | `product_page`     |
| "careers", "jobs"                        | `careers`          |

If the request doesn't map (e.g. "dashboard", "settings page", "wizard step") — those page_types aren't covered by inspiration_pages. Ask the user: "I don't have inspiration_pages for that. Want me to use `landing_pattern` (broader categories) or generate freely from your design system?"

If ambiguous between the 11 types, ask the user to clarify with the list above.

Build filters from `design/system.md`. **Filters are SINGLE VALUES per call** — to mix moods, call the resolver multiple times and dedupe by `id`.

- `mood` — pick the system's primary mood (single value). If you want 2-3 moods covered, call resolver multiple times and intersect/union results.
- `style_family` — single value if the system declares one; omit otherwise.
- `appearance` — derive from system (`light` / `dark` / `mixed`).
- `industry` — single value from `design/interview.md` if you have it.

**Vocabulary check (mandatory before query).** Call `mcp__designlib__list_inspiration_page_facets` once to surface the live values for `mood`, `signature`, `good_for_stage`, `style_family`. Map the system's mood/direction language to actual facet values BEFORE building filters — never invent values like `cinematic` or `nocturnal` and pass them to MCP.

**Structural axis (mandatory at VARIANCE ≥ 7).** Read `design/interview.md` for the VARIANCE dial. If `VARIANCE >= 7`, the filter MUST include at least one structural axis — `signature` (e.g. `off_grid`, `asymmetric`, `scroll_narrative`, `editorial_layout`) OR `good_for_stage` matched to the page's anchor section. Mood-only filtering at high VARIANCE returns visually-on-brief but structurally-typical pages, which then ship as classic linear landings — the #1 cause of "the system looked bold but the page looks like every dark-mode SaaS."

If the user explicitly asked for "non-typical structure" / «нестандартная структура» / similar in `interview.md` Q7 (Hard constraints), treat that as `VARIANCE = 10` regardless of the dial — structural axis is non-negotiable.

**Platform check:** if the project is iOS / cross, inspiration_pages won't return results (web-only entity). The resolver auto-falls-back to `landing_patterns`; surface this to the user in the result card source field.

## Phase 3 — Reference fetch

Call `get_design_reference(type='page', filters={page_type, mood: <one>, style_family: <one>, appearance, industry}, limit=3)` (see `skills/design/references/layer1-resolvers.md`). Filters are single-valued at the MCP layer — to mix moods, call multiple times and dedupe by `id`.

For each result, present a card to the user:

```
▸ <title>  (id: <id>, source: <designlib_mcp | landing_pattern_fallback>)
  Description: <description>  [list response — may be truncated mid-sentence]
  Use when:    <use_when>     [list response — truncated to ~120 chars; the situational call vs. siblings]
  Why it works: <why_it_works if available; otherwise "deep-fetch will load this">
  Screenshot: <screenshot_url if present, else "no screenshot available">
```

The `Use when` line is the deciding signal when 2-3 candidates share the same `(page_type, mood, style_family)` triad — it tells the user (and you on regenerate) which reference is the right call for THIS brief. Don't omit it.

Ask the user to pick one or say "more" / "different filters" / "skip references — generate from system only".

## Phase 4 — Deep-fetch picked reference

Once user picks: `mcp__designlib__get_inspiration_page(page_id=picked.id)`. (Param is `page_id`, not `id`.) Capture the full payload — palette, typography, sections array, primary_cta, `generation_prompt` (now populated for all 11 page_types — use as the base instruction), `generation_constraints` (now populated for all 11 page_types — treat `hard_rules` as MUSTs), `use_when` (full text, vs. the truncated version in the list response), interaction_cues, effects, inspiration_metadata. The list response did NOT include the long-form versions of these fields.

Re-read `inspiration_metadata.standout_qualities` (use to author the user-facing narrative for the generated page) and `inspiration_metadata.not_recommended_for` (if anything in the project's brief contradicts these, flag it before generating).

## Phase 4b — Per-section anchor resolution (mandatory)

The page-level anchor from Phase 4 informs the OVERALL direction. It does NOT supply per-section composition for stats / pricing / cta / testimonials / footer — using it as a single anchor across all sections is what causes sections 3-N to collapse to defaults (StatsBand becomes "3 numerals horizontally", FinalCTA becomes "headline + button left-aligned"; this is the documented v2.0 test failure mode).

For EACH section in `sections[]` from the deep-fetched page, before generating code:

1. Map the section to a `good_for_stage` value: `hero_section` / `cta_band` / `feature_blocks` / `pricing_table` / `testimonials` / `form_design` / `data_display` / `footer_only` / `social_proof` / `faq`.
2. Call `mcp__designlib__list_inspiration_pages(good_for_stage=<stage>, mood=<system primary mood>, appearance=<system>, limit=2)`.
3. If results: deep-fetch the top result via `get_inspiration_page(page_id=<id>)`, extract `sections[]` entries that match the stage, capture their composition language (column count, alignment, asymmetry, signature element).
4. If no results for a stage: explicitly note "no per-section anchor available; fell back to page-level reference." Don't silently default — the user should know which sections are anchored vs. inferred.

This loop costs N MCP calls (one per distinct section type), de-duped by stage. For a typical landing that's 4-6 calls. Worth the latency: this is the difference between a referenced page and a hero-with-generic-tail.

## Phase 4c — Animation lookup (gated)

This phase resolves and vendors animation components from the `animations` catalog when the page warrants motion. It runs after the per-section anchors are captured (Phase 4b) and before code generation (Phase 5). Naming follows the existing `4 / 4b / 4c` sub-phase convention — Phase 5 onwards stays at the same number.

See `skills/design/references/animations.md` for the catalog's vocab, filter contract, and the mood→style_tag map referenced below.

### 4c.1 Trigger gate

This phase runs IF AND ONLY IF **all** of the following hold:

1. **Project is React.** Detected by reading `package.json` and finding `react` in `dependencies` or `devDependencies`. If the project is iOS (`Package.swift` / `*.xcodeproj` present, no `package.json`), Vue (`vue` dep instead of `react`), or static HTML — skip the entire phase silently. Do not announce the skip in chat; do not improvise an inline CSS keyframes animation as a fallback.
2. **At least one of the three motion signals fires:**
   - `MOTION_INTENSITY >= 6` (read from `design/interview.md` — same source Phase 2 uses), OR
   - `appearance == 'dark'` (from `design/system.md`) AND `page_type ∈ {marketing_landing, portfolio, signup}` (these page types in dark mode are the strongest fit for hero/background animations — `dark_landing_page` is the catalog's top `use_when` tag with 64 records), OR
   - The Distinctiveness Gate Q7 escape-hatch in §4c.4 fires after Phase 5 step 6's first failure.

If none of those fire — the page does not need a catalog-vendored animation. Skip Phase 4c silently.

### 4c.2 Surface selection

For each section in `sections[]` from the deep-fetched page (Phase 4), decide whether it's a candidate animation surface:

- `hero_section` → **candidate** (animation `category` = `hero` OR `background`).
- `cta_band` → candidate at high MOTION (`MOTION_INTENSITY >= 7`); animation `category` = `element`, `interactivity` ∈ {`hover`, `click`}.
- `feature_blocks` → candidate ONLY at `MOTION_INTENSITY >= 8`; animation `category` = `element`, `interactivity` ∈ {`scroll`, `hover`}.
- All other section types (`testimonials`, `pricing`, `footer`, `faq`, `social_proof`, `data_display`, `form_design`) → not candidates. Animation in these sections reads as decoration-not-substance — the documented v2.0 anti-pattern.

**Hard cap: 2 animation surfaces per page.** Pages with more than 2 catalog-vendored animations read as a demo reel, not a design.

If after applying these rules the page has 0 candidate surfaces — skip Phase 4c silently. The motion signal fired but the page's section composition has nowhere appropriate for catalog motion.

### 4c.3 Resolve per surface

For each candidate surface (in section order, capped at 2):

1. **Build filters:**
   - `category` from the surface mapping in §4c.2.
   - `complexity` from `MOTION_INTENSITY`: 1-4 → `light`, 5-7 → `medium`, 8-10 → `heavy`.
   - `style_tag` mapped from `system.md` mood via the Mood → style_tag table in `references/animations.md` (e.g. `mood='moody'` → `style_tag='dark'`; `mood='futuristic'` → `style_tag='3d'` or `'futuristic'`). Singular per call.
   - `use_when` from the page's industry / brand personality if a clean mapping exists (e.g. `brand_personality_playful` for playful-mood pages); skip if no clean mapping.
2. **Call** `get_design_reference(type='animation', filters={category, complexity, style_tag?, use_when?}, limit=3)`.
3. **Empty-result drop-and-retry:** if the call returns `[]` — drop `style_tag`, retry. If still `[]` — drop `use_when`, retry (keep `category` + `complexity`). If still `[]` after both drops — skip this surface (do NOT relax `category` or `complexity`; mismatched-category animation is worse than no animation).
4. **Deep-fetch** the top result via `mcp__designlib__get_animation(animation_id=<picked.id>)`. The list response does not include `prompt_text`, `libraries`, `placement`, or `interactivity` — the deep-fetch is mandatory before vendoring.

### 4c.4 Distinctiveness Gate Q7 escape-hatch

This is the integration point with Phase 5 step 6's HARD-with-1-retry Distinctiveness Gate. If — and only if — the Gate's first-attempt failure is **specifically Q7** (load-bearing element) and no other question, the regenerate strategy is **not** "pick a different page reference and re-walk all sections." It is:

1. Loop back into §4c.3 with the failed page's hero section as the surface (force `category='hero'`).
2. Pick the top result and deep-fetch.
3. Vendor it via §4c.5 and re-render the page with the animation in place.
4. Re-run the Gate. If Q7 still fails — fall to SOFT (emit with `Risks taken & gaps` block, same as documented in Phase 5 step 6).

This is the **single** retry path. The escape-hatch does not stack with the standard "swap reference" retry — pick one. Animation-vendoring is the right retry only when Q7 is the lone failure; if Q1/Q2/Q4/Q5/Q8 also failed, the problem is the reference itself, not the absence of motion.

### 4c.5 Vendor + integrate

For each picked animation:

1. **Library check.** Read `package.json`. For each library in `animation.libraries`:
   - Already present in `dependencies` or `devDependencies` → continue.
   - Missing → record into a `Risks taken & gaps` block (see §4c.6). **Do NOT auto-install.** The user runs `npm install` themselves; install is their call (CI / monorepo / lockfile concerns we don't see).
2. **Extract TSX from `prompt_text`.** The field is markdown — find the FIRST fenced code block tagged ` ```tsx ` or ` ```jsx `. That fenced block (without the fences) is the component source. Do not write the entire markdown blob into a `.tsx` file — the markdown also contains stack notes, install instructions, and demo wiring that don't belong in a component.
3. **Write component.** Path: `src/components/animations/<animation.component_filename>` (the catalog provides the filename, e.g. `aurora-background.tsx`). If `src/components/animations/` doesn't exist, create it. **Verbatim** — do not edit the TSX, do not retoken its colors, do not rewrite its imports.
4. **Import + place in section TSX.** In the section's generated TSX (Phase 5 will write this), import the component and render it at the section's intended layer:
   - **Hero animations** wrap the section's content (`<HeroAnimation>{sectionContent}</HeroAnimation>` or sit absolute behind it).
   - **Background animations** sit absolute behind the section (`<div class="relative"><BackgroundAnim class="absolute inset-0 -z-10" />{...}</div>`).
   - **Element animations** replace the section's CTA / accent (e.g. swap a plain `<button>` for `<MagneticButton>`).
5. **Apply project tokens to the wrapper only.** The animation component's internal tokens (its colors, easing, durations) come from its own `prompt_text` — leave them. Apply `design/tokens.css` variables to the surrounding wrapper (background color, text color, container max-width, padding scale) where the animation meets the rest of the page. Editing the animation component itself defeats the verbatim-vendoring contract and is the documented failure mode for this phase.

### 4c.6 Risks block

Append to the `Risks taken & gaps` block (or initialise it if Phase 5 hasn't yet) when ANY of these conditions held during this phase:

- A library was missing from `package.json` → list which libraries to install + the npm command (e.g. `npm install framer-motion three`).
- `complexity == 'heavy'` was picked → note the bundle-size impact (e.g. "`three` adds ~600 KB; consider lazy-loading the section with `dynamic()` or `React.lazy`").
- `interactivity` is `cursor_track` OR `scroll` → note that mobile may degrade or disable these and the user should verify the fallback behaves acceptably.
- The §4c.4 Q7 escape-hatch fired → note that the Distinctiveness Gate forced an animation pick; the user can revert if it doesn't fit the brief.

Block format (matches existing `/create` Phase 5 step 6 convention):

```
Risks taken & gaps
─ Vendored animation: <id> at <surface> (<category>, <complexity>, libraries: <list>).
─ Library deps missing: install with `<npm command>`.
─ Heavy bundle: <library> adds ~<size>; consider lazy-loading.
─ Cursor-tracking interactivity: verify mobile fallback (degrades to `static` automatically).
```

### 4c.7 Logging

Phase 4c emits exactly one user-visible log line before Phase 5:

- Vendored: `Phase 4c — Animations: vendored <N> components for <surfaces>. Sources: <id1>, <id2>.`
- Skipped: `Phase 4c — Animations: skipped (gate not triggered: motion=<X>, appearance=<a>, page_type=<p>).`
- Empty: `Phase 4c — Animations: no catalog match for surface <s> after dropping style_tag and use_when. Skipping animation for that surface.`

Do not narrate the per-surface resolve loop in chat — keep the log to one line of summary.

## Phase 5 — Generate

Generate code for the page. Follow this order:

1. **Detect stack.** Read `package.json` (web), `Package.swift` / `*.xcodeproj` (iOS). Pick output format: React+Tailwind / Vue / SwiftUI / static HTML / etc. If ambiguous, ask.
2. **Anchor on the prose triad** — `generation_prompt`, `use_when`, `why_it_works` from the deep-fetched payload. `generation_prompt` is the base instruction (structural posture + load-bearing element + risk taken). `use_when` tells you the situational call, so you don't drift the reference into a context it wasn't meant for. `why_it_works` is the UX rationale to preserve. These three together are what makes the output non-generic; treat them as load-bearing context for sections 3-4 below, not as flavor text.
3. **Walk sections in order** (`sections[]` from the picked page). For each section: use the per-section anchor captured in Phase 4b (not just the page-level anchor) to drive composition; apply the system's tokens (no raw hex, no hardcoded font names — reference `design/tokens.css` variables or SwiftUI theme).
4. **Apply `generation_constraints.hard_rules`** if present. Soft guidance can be overridden by user request from earlier turns; ask if unclear.
5. **Layout-distinctiveness check (mandatory at VARIANCE ≥ 7).** Before code emit, evaluate the planned section sequence against the default linear posture (hero → stats → 2× feature-split → CTA → footer). If the sequence matches the default posture AND `VARIANCE >= 7`, the layout has not honored the dial — re-plan with at least one of: an off-grid section (asymmetric grid, sections positioned at angles with connecting hairlines), a scroll-narrative section (sticky-pin + scrub), a section-order break (e.g. CTA mid-page, stats AFTER feature-splits, FAQ replacing about). Document the chosen break in the output. Skipping this is the documented v2.0 failure mode where dials evaluated palette / motion / density but not layout.
6. **Run all six Layer 2 filters** on the candidate output. **Distinctiveness Gate runs HARD on first attempt** — if any of Q1/Q2/Q4/Q5/Q7 fails (see `skills/design/references/distinctiveness-gate.md`), regenerate ONCE before showing the user. On regenerate, change at least one input: pick a different reference from the top-3 deep-fetched results, OR drop `style_family` and re-fetch with a different `mood`, OR layer in an explicit risk from the brief (anti-reference, audience hook, named precedent). Only on the second failure fall back to SOFT — emit with a `Risks taken & gaps` block and tell the user which question failed and why a riskier choice would help (`/design-builder:improve --restructure`, or rerun `/create`).

## Phase 6 — Emit code

Write files to the user's source tree, following stack convention:
- React: `src/pages/<name>.tsx` + extracted components in `src/components/`
- SwiftUI: `Sources/Views/<Name>View.swift` (or project-specific path)
- Static HTML: `<name>.html` + `<name>.css`

If unsure of conventions, ask before writing — do not invent paths.

Optionally also generate `design/preview.html` with the rendered page if the user wants a visual confirm before code lands. Default: skip; ask only if relevant.

## Phase 7 — Next-step block

End with a `Next:` block, contextual:

- Clean output: "✓ Generated `<file_paths>`. **Next:** open the preview, then `/design-builder:review <path>` — the critic will find what to tweak before adding more sections."
- Output included a `Risks taken & gaps` block: "✓ Generated with caveats (see Risks block above). **Next:** if the risks aren't worth it, `/design-builder:create <what>` with a different reference; otherwise `/design-builder:review` to validate."
- Used fallback: "✓ Generated using `landing_pattern_fallback` (no inspiration_pages matched, or platform=ios). **Next:** `/design-builder:review` to validate, or refine the system mood/style and rerun for richer references."

## Failure modes to avoid

- **Inventing tokens** when `design/system.md` is missing. Phase 1 blocks this — don't bypass.
- **Hardcoding hex / font-family / spacing.** Always reference tokens.
- **Skipping `generation_constraints.hard_rules`.** They're MUSTs; respect them or pick a different reference.
- **Fabricating section content.** When the source page has rich section structures, mirror them; don't simplify to "hero + features + CTA" by reflex.
- **Treating MCP filters as arrays.** They're singular. Multi-mood filtering is multi-call + dedupe.
- **Calling `get_inspiration_page(id=...)`.** The param is `page_id`.
- **Trusting the list response's `description` as full.** It's truncated — deep-fetch for the full text. Same goes for `use_when` (~120 char cap in list).
- **Ignoring `generation_prompt` / `use_when` because the page_type isn't `marketing_landing`.** Both are now populated for all 11 page_types — the old null-on-9-types assumption is dead. If they're missing, that's a data issue, not the default.
- **Filtering by mood only at high VARIANCE.** Returns visually-on-brief but structurally-typical pages. Phase 2 requires a structural axis (`signature` or `good_for_stage`) at `VARIANCE >= 7`.
- **Treating the page-level anchor as enough for all sections.** Phase 4b is mandatory — without per-section anchors, sections 3-N collapse to defaults regardless of how strong the hero is.
- **Skipping the layout-distinctiveness check at high VARIANCE.** Dials evaluated palette/motion/density historically, not section sequence. If the user explicitly asked for non-typical structure and you ship a default linear sequence, the dial was ignored — Phase 5 step 5 is the gate.
- **Vendoring `prompt_text` as a whole into a `.tsx` file.** The field is markdown (stack notes + install + fenced TSX block + demo + notes). Phase 4c.5 step 2 requires extracting the FIRST ` ```tsx ` / ` ```jsx ` fenced block. Writing the whole markdown produces a broken file — TS will not compile prose.
- **Auto-installing missing animation libraries.** Phase 4c surfaces missing deps in the `Risks taken & gaps` block; running `npm install` from inside the command is out of scope. Lockfile / CI / monorepo concerns are the user's call.
- **Editing the vendored animation component.** Phase 4c.5 step 5 says apply tokens to the WRAPPER only. Editing the animation's internal palette / easing / durations defeats the verbatim-vendoring contract and breaks the catalog's quality guarantee.
- **Ignoring the 2-surface cap.** More than 2 catalog-vendored animations on a page reads as a demo reel, not a design. Phase 4c.2 enforces this; do not bypass when surfaces exist.
- **Improvising an inline CSS keyframes animation when Phase 4c is skipped.** Skipping is the correct behaviour for iOS / Vue / static HTML / pages where the gate doesn't fire. Filling the gap with hand-rolled keyframes is the v2.0 "decor glued onto generic sections" anti-pattern.
