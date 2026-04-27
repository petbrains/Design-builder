# inspiration_pages — schema map for the skill

> What this is: a digestible map of the `inspiration_pages` table that the `designlib` MCP server exposes via `list_inspiration_pages` / `get_inspiration_page` / `list_inspiration_page_facets`. The skill loads this when any command resolves `type='page'` through `get_design_reference()`.
>
> 405 records, sourced from land-book screenshots.

## When to consult

Load this file when:

- A command (typically `/create`) is about to filter `inspiration_pages` and you need to know which `page_type` / `mood` / `style_family` values are valid.
- You need to interpret an MCP response field — e.g. what does `palette.role_intent.primary_accent` mean, or what's in `sections[]`.
- You're deciding which fields to project into the user-facing description.

## Coverage at a glance (405 rows)

| page_type           | rows |
|---------------------|-----:|
| marketing_landing   | 73   |
| about               | 44   |
| portfolio           | 43   |
| product_listing     | 38   |
| careers             | 37   |
| ecommerce_home      | 35   |
| blog_post           | 35   |
| signup              | 34   |
| blog_index          | 23   |
| pricing             | 23   |
| product_page        | 20   |

**appearance:** light 266 / mixed 93 / dark 46.
**density:** comfortable 292 / spacious 98 / compact 15.
**style_family:** ~50 commonly-used values surfaced by the facets endpoint (out of more in the table). Always call `list_inspiration_page_facets()` to get the live vocabulary.
**industry:** ~50 commonly-used values via facets (top: fintech 37, creative_agency 20, beauty 14, saas 11, food_beverage 11, home_goods 11, healthcare 9, wellness 9, ecommerce 9, developer_tools 7, ...).

## Primary filter triad (recommended for `/create`)

**The MCP filters are SINGULAR strings, not arrays.** `list_inspiration_pages` accepts one `mood`, one `signature`, one `keyword`, etc. To "filter by 2-3 moods", call the tool multiple times and dedupe by `id`.

The combination most likely to return a small, relevant set:

- `page_type` — single value from the 11 above. Always set when calling `get_design_reference(type='page')`.
- `mood` — pick ONE value per call. Source: `list_inspiration_page_facets()` → `moods`. Records carry 2-6 mood tags each (returned as array IN responses), but the filter takes one. To narrow by multiple moods, call repeatedly and intersect.
- `style_family` — pick ONE value per call. Source: `list_inspiration_page_facets()` → `style_families`. Use as a secondary narrowing dimension.

If results are empty or too few (<2): drop `style_family` first, then `mood` (keep `page_type`). If still empty, the resolver falls back to `landing_patterns` (see `layer1-resolvers.md`) and logs the fallback.

## Vocab (live values from `list_inspiration_page_facets`)

### `moods` (19 values)
`confident`, `editorial`, `approachable`, `calm`, `warm`, `minimal`, `playful`, `energetic`, `elegant_luxury`, `techy`, `organic`, `futuristic`, `moody`, `clinical`, `maximalist`, `retro_vintage`, `brutalist`, `cool`, `mysterious`.

### `visual_signatures` (selection)
`no_gradients_on_surfaces`, `sticky_top_nav_thin`, `rounded_card_corners`, `tag_eyebrow_labels`, `sectioned_color_bands`, `pill_cta_buttons`, `warm_desaturated_palette`, `serif_display_hero`, `full_bleed_hero_imagery`, `huge_wordmark_footer`, `oversized_tight_tracking`, `editorial_spaced_paragraph_breaks`, `soft_card_shadows`, `marquee_logo_strip`, `data_heavy_table_grid`, `monochrome_photography`, `retro_editorial_photography`, `vintage_illustrated_characters`, `case_study_long_scroll`, `mono_accent_typography`, `gradient_text_hero`, `neobrutalist_hard_shadow`, `inline_form_single_field`, `split_diagonal_sections`, `glassmorphism`. Note: `gradient_text_hero` is a recorded SIGNATURE in the catalog but is **also a Layer 2 BAN 2** (gradient text). If a candidate has this signature, regenerate via different filters — don't accept it.

### `good_for_stages` (12 values)
`whole_page` (403), `color_system` (249), `hero_section` (226), `typography_system` (174), `photography_direction` (166), `feature_blocks` (107), `list_view` (72), `form_design` (47), `cta_band` (37), `data_display` (34), `footer_only` (14), `micro_interactions` (2).

### `good_for_product_types` (selection)
`b2b_saas`, `subscription_service`, `creative_agency`, `startup_generic`, `consumer_app`, `design_studio`, `enterprise_generic`, `marketplace`, `ecommerce_home_goods`, `editorial_publication`, `ecommerce_beauty`, `developer_tool`, `media_company`, `ecommerce_food_beverage`, `ai_tool`, `data_platform`, `fintech_app`, `hardware_product`, `healthcare`, `ecommerce_fashion`, `personal_portfolio`, `booking_service`, `nonprofit`, `education`, `government`.

## Platform note

inspiration_pages are **web-only**. The MCP returns `meta.platform: null` and there is no `platform` filter parameter. For iOS or cross requests, the resolver should fall back to `landing_patterns` or iOS HIG references. Document this in `design/system.md` if `/setup` is run for iOS — make the user aware that the inspiration source pool is currently web-only.

## `good_for_stages` and "parts"

The `good_for_stages` facet includes `hero_section`, `cta_band`, `feature_blocks`, `footer_only`, `form_design`, `list_view`, `data_display`, `micro_interactions`, etc. So **partial-page references can be filtered today** by setting `good_for_stage='hero_section'` (singular param) — no need to wait for the future `inspiration_parts` MCP.

When the future `inspiration_parts` entity ships, it will carry just the part rather than a full page that's good as a part. Different shape, additive. For now: use `good_for_stage` on `inspiration_pages`.

## Field-by-field reference

> **List vs deep-fetch:** `list_inspiration_pages` returns a SUBSET of fields (id, page_type, appearance, style_family, industry, mood[], keywords[], screenshot_path, description — and description is truncated). To get `palette`, `typography`, `sections`, `primary_cta`, `why_it_works`, `generation_prompt`, `generation_constraints`, `inspiration_metadata`, `effects`, `interaction_cues`, you MUST call `get_inspiration_page(page_id=...)`.

### Top-level identity (in list response)
- `id` — `page_<slug>`. Stable. Use for `get_inspiration_page(page_id=<id>)` deep-fetch. **The param is named `page_id`, not `id`.**
- `screenshot_path` — `images/<cat>/<file>.jpg`. Locally gitignored at the MCP-server side; might be a public URL once Storage is wired up. **Treat as optional — may be missing or 404.**

### Classification (flat, easy to filter — in list response)
- `page_type` — see triad.
- `style_family`, `industry`, `appearance` — string facets.
- `mood` — array of 2-6 mood tags **in the response**; filter param is singular.
- `keywords` — array of 8-20 free-form tags in the response; filter param `keyword` is singular.

### Classification (only in deep-fetch)
- `landing_pattern_id` — soft-ref to `landing_patterns.id` (NOT a foreign key; only ~34 of these are canonical, the other ~87 are ad-hoc IDs). Useful for cross-linking but don't enforce existence.
- `audience` — string.
- `product_category` — string.
- `density` — `"compact" | "comfortable" | "spacious" | null`.

### Tag arrays (only in deep-fetch)
- `visual_signatures` — distinctive surface treatments.
- `good_for_product_types` — 2-6 product types this layout suits.
- `good_for_moods` — 2-6 moods this layout suits.
- `good_for_stages` — 1-5 stages this layout suits.
- `section_order` — ordered array of section type names.

### Structured (JSONB — deep-fetch only)
- `palette` — `{ role_intent: { primary_accent: "#...", ink: "#..." }, palette_strategy, contrast_character, notes }`. Use `role_intent.primary_accent` as the page's signature accent and `role_intent.ink` as default text color when proposing this page as a base.
- `typography` — heading/body family character + open-source equivalents + treatments + eyebrow_pattern. Use `*.open_source_equivalents[]` as the actual font candidate, not the original (closed-source) family names.
- `primary_cta` — `{ label_example, placements[], style } | null`. Mirror the placement positions when generating; rewrite the label to fit the user's product.
- `sections` — **ordered array of section objects**. Each section has its own type + content schema. When generating, walk sections in order; pull copy + structural intent from each.
- `effects` — animation / parallax / transition cues.
- `interaction_cues` — hover behaviour, scroll triggers.
- `generation_constraints` — `{ hard_rules, soft_guidance } | null`. Non-null only for `page_type ∈ (marketing_landing, signup)`. Treat `hard_rules` as MUSTs; `soft_guidance` as defaults that can be overridden by user request.

### Inspiration metadata (deep-fetch only)
- `inspiration_metadata` — mirror of TEXT[] tags + `standout_qualities` + `not_recommended_for`. Use `standout_qualities` to power the "why_it_works" narrative shown to the user; respect `not_recommended_for` to filter out before showing.
- `reference_for` — `{ styles[], domains[], moods[] }` — what other contexts this page is a good reference for.

### Prose (deep-fetch only)
- `description` — 2-4 sentences, neutral. **The list response truncates this** — re-read from deep-fetch when you need the full text.
- `why_it_works` — 2-4 sentences, UX insight. Use this directly in the variant card shown to the user (after light editing).
- `generation_prompt` — non-null IFF `page_type ∈ (marketing_landing, signup)`. A ready-to-use prompt seed for generation. When present, use it as the base instruction; layer the user's design system on top.
- `notes` — additional hints.

## Known issues

- 143 source JSONs failed validation and are NOT in the table. The MCP will not return them — don't expect `inspiration_pages` to cover every land-book screenshot.
- 2 broken images logged at the source: `landing/joby-aviation-...4c4a6dd5.jpg`, `portfolio/out-of-the-valley-...affinity.jpg`. If `screenshot_path` returns a 404, fall back to a text-only variant card.
- `screenshot_path` is local at the MCP-server side until Supabase Storage public URLs land — treat the field as "may be unavailable in the response payload entirely".

## Future extensions (KB-EXTENSION)

When `designlib` MCP ships `inspiration_parts` tools, this skill will gain `type='hero'`, `type='cta'`, `type='paywall'`, `type='pricing_table'`, etc. The schema map for parts will live in a sibling file `inspiration_parts.md`. The `get_design_reference()` resolver in `layer1-resolvers.md` reserves the dispatch row for these. Until then: use `good_for_stage` on `inspiration_pages` for the partial-page case.
