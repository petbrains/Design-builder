---
description: Generate a design spec (markdown) for a web page. Spec lands in design/pages/<name>.md. No code emitted — use /build for that.
argument-hint: "[what to design — e.g. 'landing', 'pricing', 'about']"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, mcp__designlib__list_inspiration_pages, mcp__designlib__get_inspiration_page, mcp__designlib__list_inspiration_page_facets, mcp__designlib__list_landing_patterns, mcp__designlib__get_landing_pattern, mcp__designlib__list_palettes, mcp__designlib__list_styles, mcp__designlib__list_font_pairs, mcp__designlib__list_animations, mcp__designlib__get_animation, mcp__designlib__list_animation_facets, mcp__plugin_design-builder_figma__get_design_context, mcp__plugin_design-builder_figma__get_screenshot
---

# /design-builder:design_page — generate a web page spec

You produce a **design specification** (markdown) for a web page. The spec lands in `design/pages/<name>.md`. You do NOT emit code — that's `/design-builder:build`'s job. Activate the `design` skill (`skills/design/SKILL.md`).

The user's argument names the page — e.g. `landing`, `pricing`, `about`, `signup`. Map natural language to a `page_type` value from the 11 valid `inspiration_pages` page_types (`marketing_landing`, `pricing`, `signup`, `about`, `blog_index`, `blog_post`, `portfolio`, `ecommerce_home`, `product_listing`, `product_page`, `careers`).

## Phase 1 — System check (BLOCKING)

Read these three files from `design/`:
- `design/design-system.md`
- `design/style-guide.md`
- `design/content-library.md`

If **any** of the three is missing → stop. Single message:
> "Missing foundation files. Run `/design-builder:setup` first — it produces the three files this command depends on."

If all three exist: read them fully. Capture for use later in this run:
- Stack (from `design-system.md ## Stack`).
- Palette role mappings, typography, motion dial, anti-pattern bans (from `design-system.md`).
- Contrast rules, touch targets, platform constraints (from `style-guide.md`).
- Voice & tone principles, state patterns (from `content-library.md`).

Also read `design/.cache/interview.json` for dial values (DENSITY, MOTION_INTENSITY, VARIANCE).

## Phase 2 — Documentation check

One free-form question to the user:

> "Got documentation / PRD / brief for this page? (paste / file path / Figma URL / Notion URL / nothing)"

Branch on the response:

- **File path:** `Read` the path. Capture the full content as the page's source-of-truth for purpose, features, content.
- **Pasted text:** Capture verbatim from chat.
- **Figma URL:** Call `mcp__plugin_design-builder_figma__get_design_context` and `get_screenshot`. Capture metadata + screenshot.
- **Notion / external URL:** if the URL is not Figma, ask user to paste the relevant content (we don't have generic web-fetch in this command's allowed tools).
- **Nothing:** proceed to Phase 2b (content interview).

If documentation was supplied: **do NOT paraphrase it back to the user**. Use it as input. Skip Phase 2b entirely.

## Phase 2b — Content interview (only if no docs)

One question per message, in order:

1. "What's this page in the product — what's the user's main task on it?"
2. "Key elements / sections it must contain? (free-form list)"
3. "Edge cases — what if the user is logged out / has no data / hits an error / has slow connection?"
4. "Animations / micro-interactions for THIS page? (`none` / `minimal` / `CTA accents` / `hero motion` / `aggressive`) — overrides MOTION_INTENSITY for this page only"

Capture all answers to `design/.cache/page-<slug>-interview.json` as JSON:
```json
{
  "captured_at": "<YYYY-MM-DD HH:MM>",
  "purpose": "...",
  "key_elements": [...],
  "edge_cases": "...",
  "animation_intensity_override": "<one of the 5 options>"
}
```

## Phase 3 — Reference resolution

Use the same Layer 1 / Layer 2 machinery as the v2.0 `/create` command. The relevant phases are:

### 3.1 Map argument → page_type

| User says | page_type |
|---|---|
| "landing", "marketing", "homepage" | `marketing_landing` |
| "pricing", "plans" | `pricing` |
| "signup", "register", "join" | `signup` |
| "about" | `about` |
| "blog list", "blog index", "articles" | `blog_index` |
| "blog post", "article" | `blog_post` |
| "portfolio", "work" | `portfolio` |
| "store", "shop home" | `ecommerce_home` |
| "product list", "catalog" | `product_listing` |
| "product detail", "product page" | `product_page` |
| "careers", "jobs" | `careers` |

Off-list requests (`dashboard`, `settings`, `wizard step`) → ask: "Not in the inspiration_pages set — switch to `/design-builder:design_screen`, or generate freely from your design system without a reference (less anchored)?".

### 3.2 Vocabulary check

Mandatory before any list query. Call `mcp__designlib__list_inspiration_page_facets` once. Map the system's mood/direction language (from `design-system.md ## Direction`) to actual MCP facet values BEFORE building filters. Never invent facet values like `cinematic` or `nocturnal` — translate first.

### 3.3 Structural axis check

Read VARIANCE from `.cache/interview.json`. If `VARIANCE >= 7` OR `design-system.md ## Layout posture` exists, the filter MUST include a structural axis (`signature` like `off_grid`, `asymmetric`, `scroll_narrative`, OR `good_for_stage` matched to the page's anchor section). Mood-only filtering at high VARIANCE is the documented v2.0 failure mode.

### 3.4 Build filters and fetch

Call `get_design_reference(type='page', filters={page_type, mood, style_family, appearance, industry}, limit=3)`. Filters are SINGULAR; for multi-mood call multiple times and dedupe by `id`.

### 3.5 Present cards

For each result, render the card format used by v2.0 `/create` Phase 3:
```
▸ <title>  (id: <id>, source: <designlib_mcp | landing_pattern_fallback>)
  Description: <description>
  Use when: <use_when>
  Why it works: <why_it_works if available; otherwise "deep-fetch will load this">
  Screenshot: <screenshot_url if present, else "no screenshot available">
```

Ask the user to pick one (by id or number) or say `more` / `different filters` / `skip references — generate from system only`.

### 3.6 Deep-fetch the picked reference

`mcp__designlib__get_inspiration_page(page_id=picked.id)`. Capture: palette, typography, sections array, primary_cta, `generation_prompt`, `generation_constraints`, `use_when` (full text), interaction_cues, effects, inspiration_metadata.

### 3.7 Per-section anchor resolution (mandatory)

For EACH section in `sections[]`:
1. Map to `good_for_stage` (`hero_section` / `cta_band` / `feature_blocks` / `pricing_table` / `testimonials` / `form_design` / `data_display` / `footer_only` / `social_proof` / `faq`).
2. Call `mcp__designlib__list_inspiration_pages(good_for_stage=<stage>, mood=<system primary mood>, appearance=<system>, limit=2)`.
3. If results: deep-fetch top result, capture composition for that section.
4. If no results: explicitly note "no per-section anchor available; falls back to page-level reference."

### 3.8 Animation lookup (gated)

Same gate as v2.0 `/create` Phase 4c — runs only if all of:
1. Stack is React (`package.json` deps include `react`).
2. At least one motion signal: `MOTION_INTENSITY >= 6` (from interview, possibly overridden by Phase 2b Q4) OR (`appearance=dark` AND `page_type ∈ {marketing_landing, portfolio, signup}`).

For each candidate animation surface (max 2 per page):
- Build filters (`category`, `complexity`, `style_tag`, `use_when`).
- Call `get_design_reference(type='animation', filters={...}, limit=3)`.
- Drop-and-retry on empty: drop `style_tag`, then `use_when`. Don't relax `category` or `complexity`.
- Deep-fetch top result; capture `component_filename`, `libraries`, `placement`, `interactivity`, and the first ` ```tsx ` block from `prompt_text`.
- The animation choice is **fixed in the spec** (this command writes the chosen `animation.id`, `component_filename`, and `libraries` into `## Animations`). `/build` will vendor the actual file later — don't vendor here.

## Phase 4 — Spec generation

Write `design/pages/<slug>.md` in the format defined by [`skills/design/references/page-spec-format.md`](../skills/design/references/page-spec-format.md). All 9 sections (Risks taken & gaps optional). Use:

- Title block: page name (Title Case from argument), today's date, picked inspiration_page IDs.
- Purpose: from documentation OR Phase 2b Q1.
- Reference anchor: primary id + per-section anchors from 3.7 + lifted prose triad.
- Layout posture: from `design-system.md ## Layout posture` (if present), applied to this page's section sequence. Required when VARIANCE ≥ 7 — must include at least one of: off-grid asymmetric block, scroll-narrative pinned section, or section-order break.
- Sections: per the template, with all six bullet points filled per section. Animation lines reference the catalog where applicable; tokens reference `tokens.css` variables.
- Edge cases: drawn from `content-library.md ## UI states` patterns, instantiated for this page.
- Components needed: stack-aware list from `.cache/stack.json`.
- Animations: from 3.8 results, listing `<descriptive name> — <animation.id>, library: <list>, surface: <section name>`.
- Risks taken & gaps: include only if 3.7 had no anchor for some section, OR the page hit a Distinctiveness Gate concern that couldn't be fully addressed in the spec.

If the slug already exists at `design/pages/<slug>.md`: ask before overwriting:
> "`design/pages/<slug>.md` already exists. (1) Overwrite (2) Save as `<slug>-v2.md` (3) Cancel?"

## Phase 5 — Final gate

After spec written, present 4 options:

> "✓ Spec ready: `design/pages/<slug>.md`.
>
> **What's next?**
> 1. **Move to Figma** (build frames + text in your Figma project — needs Figma MCP)
> 2. **Already in Figma manually** (skip)
> 3. **Straight to code** — `/design-builder:build <slug>`
> 4. **Another page** — `/design-builder:design_page <name>` (useful if you want to plan multiple pages before building)"

On (1): check whether `mcp__plugin_design-builder_figma__authenticate` is available. If yes, invoke the `design-builder:figma-use` skill via the Skill tool (it handles the actual Figma orchestration). If no Figma MCP wired up: surface the figma-use README path so the user can connect it first.

On (2)/(3)/(4): emit the corresponding next-step pointer and stop.

## Failure modes to avoid

- **Skipping Phase 1 system check.** The three foundation files are mandatory — running without them produces specs that don't honor the project's tokens or anti-patterns.
- **Paraphrasing supplied documentation.** When the user gives docs in Phase 2, USE the docs — don't restate them. Phase 2b only fires when no docs.
- **Mood-only filtering at VARIANCE ≥ 7.** Phase 3.3 mandates a structural axis. Skipping reproduces the v2.0 "system looks bold but page looks linear" failure.
- **Treating the page-level anchor as enough for all sections.** Phase 3.7 is mandatory — without per-section anchors, sections 3-N collapse to defaults.
- **Vendoring the animation in this command.** `/design_page` records the chosen `animation.id` in `## Animations`. `/build` does the actual file vendoring (Phase 4c.5 logic).
- **Writing code.** This command writes a markdown spec only. If the user asks for code, point them at `/design-builder:build`.
- **Calling `get_inspiration_page(id=...)`.** The param is `page_id`.
- **Treating MCP filters as arrays.** They're singular. Multi-value = multi-call + dedupe.
