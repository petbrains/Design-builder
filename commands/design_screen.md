---
description: Generate a design spec (markdown) for an app screen (iOS / native). Spec lands in design/screens/<name>.md. No code emitted — use /build for that.
argument-hint: "[what to design — e.g. 'onboarding', 'home', 'profile', 'paywall']"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, mcp__designlib__list_landing_patterns, mcp__designlib__get_landing_pattern, mcp__designlib__list_palettes, mcp__designlib__list_styles, mcp__designlib__list_font_pairs, mcp__designlib__list_animations, mcp__designlib__get_animation, mcp__plugin_design-builder_figma__get_design_context, mcp__plugin_design-builder_figma__get_screenshot
---

# /design-builder:design_screen — generate an app screen spec

Identical structure to `/design-builder:design_page` with iOS / native specifics. Spec lands in `design/screens/<name>.md`. Activate the `design` skill.

The user's argument names the screen — e.g. `onboarding`, `home`, `profile`, `paywall`, `feed`, `detail`, `settings`. Map to a screen-type vocab:

| User says | screen_type |
|---|---|
| "onboarding", "first run" | `onboarding` |
| "home", "main", "feed entry" | `home_screen` |
| "feed", "list", "timeline" | `feed` |
| "detail", "view", "show" | `detail_view` |
| "settings", "preferences" | `settings` |
| "paywall", "upgrade" | `paywall` |
| "profile", "account" | `profile` |
| "tab root", "tab bar" | `tab_bar_root` |
| "modal", "sheet" | `modal_sheet` |

Off-list → ask user to pick the closest or generate freely.

## Phase 1 — System check (BLOCKING)

Same as `/design_page` Phase 1 — read `design-system.md`, `style-guide.md`, `content-library.md`, `.cache/interview.json`. Block on any missing.

Confirm stack is iOS-compatible (`stack.target == "ios"` or `cross`). If stack is web-only: redirect to `/design_page` and stop.

## Phase 2 — Documentation check

Same as `/design_page` Phase 2 — single free-form ask. Use docs as input, never paraphrase.

## Phase 2b — Content interview (only if no docs)

Same questions as `/design_page` Phase 2b plus one screen-specific addition (Q5):
1. (same as design_page Q1) — main user task on this screen.
2. (same as design_page Q2) — key elements/sections.
3. (same as design_page Q3) — edge cases.
4. (same as design_page Q4) — animation intensity override.
5. **NEW:** "How does the user reach this screen and how do they leave? (`tab switch` / `push from <parent>` / `modal present` / `sheet (detents: <list>)` / `crossfade`)" — captured for `## Navigation context`.

Capture to `design/.cache/screen-<slug>-interview.json` (same JSON shape as page interview, plus `navigation_context` field).

## Phase 3 — Reference resolution

inspiration_pages is **web-only** — do not query it. Use:

### 3.1 Map argument → reference type

For the screen_type vocab above, route to `landing_patterns` filtered by `app_screen` category. If `landing_patterns` returns nothing: fall back to free generation from the design system + iOS HIG references in `references/ios/`.

### 3.2 Build filters

Call `get_design_reference(type='landing_pattern', filters={category='app_screen', screen_type, mood}, limit=3)`. Singular filters as always.

### 3.3 Present cards

Same card format as `/design_page` Phase 3.5, but `source` line shows `landing_patterns` (or `ios_hig_fallback` if empty).

### 3.4 Deep-fetch picked reference

`mcp__designlib__get_landing_pattern(landing_pattern_id=picked.id)`.

### 3.5 Per-section anchor resolution

If the screen has internal sections (e.g. onboarding has multiple steps; settings has grouped lists), repeat the per-section anchor pattern using `landing_patterns` filtered by `good_for_stage` analogues for app screens. If no per-section data available, proceed with page-level anchor only (note this in Risks).

### 3.6 Animation lookup

Animation catalog is React-only. For SwiftUI / native iOS — DO NOT call the animations MCP. Instead, for each section that warrants motion, derive a HIG-compliant spring/transition spec from `references/ios/motion.md` and write it directly into `## Animations` in the format `<descriptive name> — spring(response: <s>, dampingFraction: <d>), trigger: <event>`.

## Phase 4 — Spec generation

Write `design/screens/<slug>.md` in the format defined by [`skills/design/references/screen-spec-format.md`](../skills/design/references/screen-spec-format.md). Sections 1-9 from page-spec-format.md plus the iOS-specific 4a (Navigation context), 4b (Gestures), 4c (Safe areas).

For 4a: from Phase 2b Q5 (or supplied docs).
For 4b: derive from screen_type — feeds get pull-to-refresh, lists get swipe-to-action, detail views get swipe-back, modals/sheets get swipe-to-dismiss; defaults are always called out as `Standard navigation gestures only` if nothing custom.
For 4c: from `style-guide.md ## Platform constraints` iOS block.

If the slug already exists: ask before overwriting (same as `/design_page`).

## Phase 5 — Final gate

Same as `/design_page` Phase 5 — four options. The Figma offer in option (1) is platform-aware: for iOS specs, the Figma frames generated would be at iPhone artboard sizes.

## Failure modes to avoid

- **Querying inspiration_pages.** Web-only entity. Returns nothing for `app_screen` semantics. Use `landing_patterns` / iOS HIG.
- **Vendoring React animations into iOS specs.** Animation catalog is React-only. iOS gets HIG spring specs in markdown form.
- **Skipping `## Navigation context` / `## Gestures` / `## Safe areas`.** All three are mandatory per `screen-spec-format.md`. `/build` errors if missing.
- (Plus all `/design_page` failure modes that apply equally — Phase 1 system check, doc paraphrasing, etc.)
