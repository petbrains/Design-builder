---
description: Create a page / screen / section based on the project's design system. Pulls inspiration_pages from designlib MCP. Writes code to the project source tree.
argument-hint: "[what to create — e.g. 'landing', 'pricing page', 'signup screen']"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, mcp__designlib__list_inspiration_pages, mcp__designlib__get_inspiration_page, mcp__designlib__list_inspiration_page_facets, mcp__designlib__list_landing_patterns, mcp__designlib__get_landing_pattern, mcp__designlib__list_palettes, mcp__designlib__list_styles, mcp__designlib__list_font_pairs, mcp__plugin_figma_figma__get_design_context, mcp__plugin_figma_figma__get_screenshot
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

## Phase 5 — Generate

Generate code for the page. Follow this order:

1. **Detect stack.** Read `package.json` (web), `Package.swift` / `*.xcodeproj` (iOS). Pick output format: React+Tailwind / Vue / SwiftUI / static HTML / etc. If ambiguous, ask.
2. **Anchor on the prose triad** — `generation_prompt`, `use_when`, `why_it_works` from the deep-fetched payload. `generation_prompt` is the base instruction (structural posture + load-bearing element + risk taken). `use_when` tells you the situational call, so you don't drift the reference into a context it wasn't meant for. `why_it_works` is the UX rationale to preserve. These three together are what makes the output non-generic; treat them as load-bearing context for sections 3-4 below, not as flavor text.
3. **Walk sections in order** (`sections[]` from the picked page). For each section: pick the appropriate component pattern, apply the system's tokens (no raw hex, no hardcoded font names — reference `design/tokens.css` variables or SwiftUI theme).
4. **Apply `generation_constraints.hard_rules`** if present. Soft guidance can be overridden by user request from earlier turns; ask if unclear.
5. **Run all six Layer 2 filters** on the candidate output. **Distinctiveness Gate runs HARD on first attempt** — if any of Q1/Q2/Q4/Q5/Q7 fails (see `skills/design/references/distinctiveness-gate.md`), regenerate ONCE before showing the user. On regenerate, change at least one input: pick a different reference from the top-3 deep-fetched results, OR drop `style_family` and re-fetch with a different `mood`, OR layer in an explicit risk from the brief (anti-reference, audience hook, named precedent). Only on the second failure fall back to SOFT — emit with a `Risks taken & gaps` block and tell the user which question failed and why a riskier choice would help (`/design-builder:improve` with bolder filters, or rerun `/create`).

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
