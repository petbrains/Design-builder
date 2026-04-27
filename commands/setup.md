---
description: Establish the project's design foundation through interview + reference discovery + visual preview. Writes to design/.
argument-hint: ""
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, mcp__designlib__list_inspiration_pages, mcp__designlib__get_inspiration_page, mcp__designlib__list_inspiration_page_facets, mcp__designlib__list_palettes, mcp__designlib__list_styles, mcp__designlib__list_font_pairs, mcp__designlib__list_domains, mcp__designlib__list_landing_patterns
---

# /design-builder:setup — establish the design foundation

You are the entry point for a brand-new design project. Activate the `design` skill (`skills/design/SKILL.md`). You produce the artifacts in `design/` that every later command (`/create`, `/improve`, `/review`) relies on. Until you finish, the user has no design system.

## Phase 1 — Discovery (mandatory; one question at a time)

Collect the following. Ask **one question per message**, prefer multiple-choice when possible, accept open-ended when it fits.

1. "Share your references — URLs, screenshots, Figma files (any quantity, any combination). Or skip if none."
2. "Got documentation? PRD, brief, brand guidelines, business goals — drop the file paths or paste the content."
3. "Want me to walk through your code? I'll read existing tokens, components, and pages to understand context. (yes/no/skip)"
4. "Target audience — who uses this, in what context?"
5. "Industry / domain?"
6. "Three words for the mood you want — concrete, not generic ('confident editorial' over 'premium')."
7. "Any hard constraints? Brand colors that must appear, technical limits, accessibility floor (WCAG AA / AAA), forbidden patterns."

Capture every answer to `design/interview.md` with a timestamp as you go. Use `Write` (first answer) or `Edit` (subsequent) to append.

If the user said yes to walking the code: use `Glob` for `tailwind.config.*`, `tokens.css`, `**/*.xcassets`, `package.json`, then `Read` the most informative ones; record findings in `design/interview.md` under `## Code walk findings`.

If the user supplied URLs to references: ask whether to download screenshots (default yes); record URLs to `design/references/urls.md`; if downloading, save to `design/references/downloaded/<safe_filename>`.

## Phase 2 — Synthesis (Layer 1 + Layer 2)

Resolve direction candidates through `get_design_reference()` (see `skills/design/references/layer1-resolvers.md`). **MCP filters are SINGULAR strings — to use multiple moods, call multiple times and dedupe by `id`.**

Also **inspiration_pages are web-only** — if the project is iOS or cross, the resolver auto-falls-back to `landing_patterns` for page references; surface this in the user-facing card.

1. Call `get_design_reference(type='palette', filters={industry, mood: <one>, audience}, limit=4)`.
2. Call `get_design_reference(type='font_pair', filters={industry, mood: <one>}, limit=4)`.
3. Call `get_design_reference(type='page', filters={page_type='marketing_landing', mood: <one>, style_family: <one or omitted>}, limit=6)` — to ground in real examples. If you want to mix moods, call this 2-3 times with different `mood` values and dedupe by `id`.

From these, assemble **2-3 direction candidates**. Each candidate combines:

- a palette (with `role_intent.primary_accent` + `role_intent.ink`),
- a font pair (use `open_source_equivalents` for actual fonts),
- a spacing scale (default `4 / 8 / 16 / 24 / 40 / 64` unless project signals otherwise),
- a mood label (1-3 words),
- 2-4 inspiration_page IDs as named references.

For richer candidates, **deep-fetch** each anchor via `mcp__designlib__get_inspiration_page(page_id=<id>)` to access full `palette.role_intent`, `typography.character`, `sections`, and `why_it_works` (the list response truncates these).

Run **all six Layer 2 filters** on each candidate (Design Direction, Dials, Aesthetics, Anti-Patterns, Distinctiveness Gate (HARD mode), Output Rules). Regenerate any candidate that fails Distinctiveness silently — the user only sees passing candidates.

## Phase 3 — Verbose presentation

For each surviving candidate, output the following block (no compression, no abbreviation):

```
▸ <Candidate Name>
  Description: <2-3 sentences describing how it looks. Concrete: name fonts, hex anchors, layout move.>
  Why for you: <2-3 sentences tying back to interview answers — audience, mood, constraints.>
  Sources: <comma-separated inspiration_page IDs and palette/font IDs used. Mark fallback sources explicitly: "page_xyz (landing_pattern_fallback)".>
```

Do not use prose-only narratives for variants; the per-candidate block above is required.

## Phase 4 — Preview gate (mandatory)

Ask: "Want me to assemble a basic HTML preview with palette + fonts + spacing? You'll see how they work together before committing." Default: yes.

If yes: generate `design/preview.html` containing all surviving candidates with a 1/2/3 keyboard switcher. Use `templates/system-preview.html` as a starting shell if it suits. Print the absolute path to the user with one short message:

> "Preview ready: `<absolute path>`. Open in your browser, press 1/2/3 to switch, then tell me your pick."

Wait for the user's pick. Skippable only on explicit user instruction ("pick for me", "skip preview"). A long brief is not an implicit skip.

## Phase 5 — Emit (only after pick)

Write the chosen direction to:

- `design/system.md` — full system spec: direction name, mood, palette with role assignments, typography pairs, spacing scale, motion baseline, the four Anti-Pattern bans (BAN 1-4), `not_recommended_for` notes from the source inspiration_pages.
- `design/tokens.css` — CSS custom properties for all palette + typography + spacing. Use `templates/web/` starters if the platform is web. For iOS, write `design/tokens.json` instead and create SwiftUI theme files per `templates/ios/Theme/`.
- `design/interview.md` — append a `## Final decision` section with timestamp, chosen candidate name, source IDs, and any user customisations.

Confirm files written by listing them with their byte sizes.

## Phase 6 — Next-step block

Output a final block (1-2 sentences) recommending what to do next. Examples (use the one matching state):

- "✓ Design system ready: `design/system.md`. **Next:** `/design-builder:create landing` — let's build the first page on this system."
- (User declined preview) "✓ System captured at `design/system.md`, but no visual preview generated. **Next:** `/design-builder:create landing`, or come back and ask 'assemble HTML preview' to see it in markup before generating real code."
- (iOS / cross — fell back to landing_patterns) "✓ Design system ready (note: inspiration_pages is web-only, so iOS direction was anchored on landing_patterns + HIG). **Next:** `/design-builder:create <screen-name>` to generate the first SwiftUI view."

## Failure modes to avoid

- **Skipping the interview because "the brief looks complete".** A pasted brief is input to discovery, not a license to jump to synthesis. Walk through the questions even if you can pre-fill some.
- **Describing variants in prose only.** The per-candidate block in Phase 3 is mandatory; the HTML preview in Phase 4 is mandatory unless explicitly skipped. No A/B/C narrative without rendering.
- **Writing files before the user picks.** Phase 5 only fires after Phase 4's pick. Don't pre-emit.
- **Generic candidates.** Distinctiveness Gate is HARD here. If you find yourself producing candidates that "any LLM would generate" — regenerate with tighter filters (more specific mood, narrower industry, named visual_signatures).
- **Treating MCP filters as arrays.** They're singular. Multi-mood filtering is multi-call + dedupe.
- **Calling `get_inspiration_page` with `id=...`.** The param is `page_id=...`.
