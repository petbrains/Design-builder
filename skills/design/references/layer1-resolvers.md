# Layer 1 resolvers — `get_design_reference()`

> What this is: the typed contract for resolving design facts (palettes, fonts, pages, etc.) through Layer 1. Every command in `commands/` calls into this resolver instead of going to MCP / CSV / HIG directly. The resolver enforces the fixed source order; commands stay agnostic of where facts came from.

## The resolver call

```
get_design_reference(
  type:   'page' | 'animation' | 'palette' | 'style' | 'font_pair' | 'icon'
        | 'landing_pattern' | 'chart_type' | 'domain'
        # future, KB-EXTENSION:
        | 'hero' | 'cta' | 'paywall' | 'pricing_table',
  filters: object,           # see "Filter shape" below
  limit:   number = 3,
  include_screenshot: bool = true
) → DesignReference[]
```

### `DesignReference` (normalised return shape)

Common shape over all source entities. Commands work with this; they never deal with raw MCP shapes.

```
{
  id:              string,         # entity ID from source (e.g. "page_xyz", "pal_001")
  type:            string,         # echoes the input type
  title:           string,         # short human label (derive from id slug or industry+style)
  description:     string,         # 2-4 sentence neutral description (truncated in list, full in deep-fetch)
  why_it_works:    string,         # 2-4 sentence UX insight (only after deep-fetch for type='page')
  screenshot_url?: string,         # absolute URL or local path; may be missing
  source:          string,         # 'designlib_mcp' | 'landing_pattern_fallback' | 'csv' | 'hig' | 'free' | 'project_tokens'
  raw:             object          # original entity JSON for deep use; do not project to user
}
```

**Note on `type='page'`:** `list_inspiration_pages` returns a SUBSET of fields. Full payload (palette, typography, sections, generation_prompt, why_it_works, generation_constraints, inspiration_metadata) requires a follow-up `get_inspiration_page(page_id=<id>)`. The resolver normalises the LIST response into `DesignReference[]`; deep-fetch is the caller's responsibility (e.g. `/create` deep-fetches after the user picks).

## Resolution order (strict, do not reorder)

```
1. project tokens     (only for type ∈ {palette, font_pair} when caller explicitly wants them)
1a. iOS short-circuit  (type='page' + platform='ios' → skip MCP, fall to landing_patterns/HIG)
2. designlib MCP      (primary source for most types; SINGULAR filter values per call)
2b. landing_pattern fallback (only for type='page' when step 2 returns empty)
3. local CSV          (BM25 over skills/design/data/, for types present in CSV)
4. iOS HIG            (only when filters.platform == 'ios')
5. free generation    (last resort, mark source='free' and pass through Layer 2 filters)
```

### Pseudocode

```
def get_design_reference(type, filters, limit=3):
    # 1. project tokens — narrow case
    if type in ('palette', 'font_pair') and project_has_tokens():
        if caller_wants_existing(filters):
            return project_tokens_as_reference()

    # 1a. iOS: skip inspiration_pages (web-only entity); jump to landing_patterns
    if type == 'page' and filters.get('platform') == 'ios':
        fb = mcp__designlib__list_landing_patterns(narrow_filters(filters), limit=limit)
        return [normalize(r, source='landing_pattern_fallback') for r in fb] if fb else hig_or_free(filters, limit)

    # 2. designlib MCP — call with SINGULAR filter values (one mood, one signature, one keyword)
    mcp_tool = MCP_TOOL_MAP[type]
    if mcp_tool is not None:
        response = mcp_tool(**select_singular(filters), limit=limit)
        # response shape: { items: [...], total_count, limit, offset, meta }
        items = response.get('items', [])
        if items:
            return [normalize(r, source='designlib_mcp') for r in items]

    # 2b. fallback for type='page' → landing_patterns (web)
    if type == 'page':
        fb = mcp__designlib__list_landing_patterns(narrow_filters(filters), limit=limit)
        if fb:
            return [normalize(r, source='landing_pattern_fallback') for r in fb]

    # 3. local CSV
    if type in CSV_TYPES:
        csv_results = bm25_search(type, filters, limit=limit)
        if csv_results:
            return [normalize(r, source='csv') for r in csv_results]

    # 4. iOS HIG
    if filters.get('platform') == 'ios':
        hig = read_hig_refs(type, filters, limit=limit)
        if hig:
            return [normalize(r, source='hig') for r in hig]

    # 5. free generation
    return free_generate(type, filters, limit=limit, source='free')
```

### Multi-value filters (singular at MCP, multi-call at resolver)

Most MCP filters take a SINGLE string. To filter by multiple moods or multiple signatures:

```
def get_design_reference_multi(type, filters_with_lists, limit=3):
    # filters_with_lists allows e.g. moods=['warm','editorial']
    moods = filters_with_lists.pop('moods', [None])
    signatures = filters_with_lists.pop('signatures', [None])
    seen = {}
    for mood in moods:
        for sig in signatures:
            f = {**filters_with_lists}
            if mood: f['mood'] = mood
            if sig: f['signature'] = sig
            for ref in get_design_reference(type, f, limit=limit):
                seen.setdefault(ref['id'], ref)
    return list(seen.values())[:limit]
```

Use this pattern in `/setup` and `/create` when the user's brief implies more than one mood. Document the de-dup behaviour in the user-facing card.

## `MCP_TOOL_MAP`

| `type`              | MCP tool                                              | Notes                                              |
|---------------------|-------------------------------------------------------|----------------------------------------------------|
| `'page'`            | `mcp__designlib__list_inspiration_pages`              | Plus `mcp__designlib__get_inspiration_page(page_id=...)` for deep-fetch by ID. **Web-only**. |
| `'animation'`       | `mcp__designlib__list_animations`                     | Plus `mcp__designlib__get_animation(animation_id=...)` for deep-fetch by ID. **Web/React-only** (iOS/Vue/vanilla → resolver returns `[]`, no fallback). 120 records; verbatim TSX in `prompt_text`. See `references/animations.md`. |
| `'palette'`         | `mcp__designlib__list_palettes`                       | -                                                  |
| `'style'`           | `mcp__designlib__list_styles`                         | -                                                  |
| `'font_pair'`       | `mcp__designlib__list_font_pairs`                     | -                                                  |
| `'icon'`            | `mcp__designlib__list_icons`                          | -                                                  |
| `'landing_pattern'` | `mcp__designlib__list_landing_patterns`               | Also reused by step 2b as fallback for `type='page'` |
| `'chart_type'`      | `mcp__designlib__list_chart_types`                    | -                                                  |
| `'domain'`          | `mcp__designlib__list_domains`                        | -                                                  |

### Future entries (KB-EXTENSION — not yet served by MCP)

| `type`             | MCP tool (when shipped)                                |
|--------------------|--------------------------------------------------------|
| `'hero'`           | `mcp__designlib__list_inspiration_parts(part='hero')`  |
| `'cta'`            | `mcp__designlib__list_inspiration_parts(part='cta')`   |
| `'paywall'`        | `mcp__designlib__list_inspiration_parts(part='paywall')` |
| `'pricing_table'`  | `mcp__designlib__list_inspiration_parts(part='pricing_table')` |

When these arrive, add the rows above without touching command code — commands already pass `type` through opaquely. Until then: filter `inspiration_pages` by `good_for_stage='hero_section' | 'cta_band' | 'feature_blocks' | 'form_design' | 'list_view' | 'data_display' | 'footer_only'` for the partial-page case.

<!-- KB-EXTENSION: add new resolver type here -->

## Filter shape (per `type`)

### Common (any `type`)
- `industry?: string`
- `mood?: string` — **single value**. To filter by N moods, call resolver N times and dedupe by `id` (or use `get_design_reference_multi`).
- `style_family?: string`
- `audience?: string`
- `appearance?: 'light' | 'dark' | 'mixed'`
- `platform?: 'web' | 'ios' | 'cross'`

### `type='page'` (additions)
- `page_type: 'marketing_landing' | 'about' | 'portfolio' | 'product_listing' | 'careers' | 'ecommerce_home' | 'blog_post' | 'signup' | 'blog_index' | 'pricing' | 'product_page'` — **always set** when calling `type='page'`.
- `density?: 'compact' | 'comfortable' | 'spacious'`
- `signature?: string` — **single value**. Maps to MCP `signature` param (one of `visual_signatures` facet values).
- `good_for_stage?: string` — **single value**. Use to find pages that excel as a particular surface (e.g. `'hero_section'`, `'cta_band'`).
- `good_for_product_type?: string`
- `keyword?: string` — **single value**. Free-form BM25-style narrowing.

inspiration_pages are web-only; for `platform='ios'` the resolver auto-falls-back to `landing_patterns` or HIG (see step 1a in pseudocode).

(See `inspiration_pages.md` for vocab and field semantics.)

### `type='animation'` (additions)

All filter values are **single strings** (multi-value = multi-call + dedupe by `id`).

- `category?: 'background' | 'hero' | 'loader' | 'text_effect' | 'element' | 'cursor_effect' | 'overlay' | 'decoration'` — closed vocab.
- `framework?: 'react' | 'vanilla_html'` — closed vocab. Default `react` (catalog is 120/120 React today).
- `interactivity?: 'static' | 'hover' | 'click' | 'cursor_track' | 'scroll' | 'mount_only'` — closed vocab.
- `complexity?: 'light' | 'medium' | 'heavy'` — closed vocab. Map from `MOTION_INTENSITY` (1-4 → light, 5-7 → medium, 8-10 → heavy).
- `style_tag?: string` — open vocab (e.g. `dark`, `minimal`, `3d`, `gradient`, `glass`). See `references/animations.md` for the live values + mood→style_tag map.
- `placement?: string` — open vocab (e.g. `hero`, `background`, `inline`, `fullscreen`).
- `use_when?: string` — open vocab situational tags (e.g. `dark_landing_page`, `product_showcase`, `interactive_demo`).
- `library?: string` — open vocab npm package name (`framer-motion`, `three`, `gsap`, ...).
- `keyword?: string` — open vocab; free-form BM25-style narrowing.

Animations are React-only — the resolver returns `[]` for iOS / cross / Vue / static-HTML callers without invoking MCP. There is no fallback (no CSV / HIG / free-generation path for animations); callers should skip the integration phase entirely on `[]`. See `references/animations.md` for vocab + field semantics.

### `type='palette'` (additions)
- `palette_strategy?: string`
- `contrast_character?: string`

### Other types
Inherit only the common filters unless documented otherwise in the corresponding reference (`designlib-mcp.md`, etc.).

## How commands call this

Commands in `commands/` invoke the resolver by stating intent in the command body, not by calling tools directly. Example phrasing inside `commands/create.md`:

> Resolve a page reference via `get_design_reference(type='page', filters={page_type, mood: <one>, style_family: <one>}, limit=3)`. Show the user 2-3 normalised `DesignReference` cards (`title` + `description` + `why_it_works` + screenshot if present). On user pick, deep-fetch full detail via `mcp__designlib__get_inspiration_page(page_id=picked.id)`.

The skill (`SKILL.md`) holds the operational definition of `get_design_reference()`; commands assume it works.

## Logging

Always include `source` from the result in any `Next:` block or report you emit, so the user can see when the fallback fired:

> "Used `landing_pattern_fallback` because no `inspiration_pages` matched `page_type='dashboard'` (or because `platform='ios'`)."

## Layer 2 still applies

The resolver returns candidates. Whatever you do with them, **the candidate output of the command must still pass through all 6 Layer 2 filters** (Design Direction, Dials, Aesthetics, Anti-Patterns, Distinctiveness Gate, Output Rules) before emit. The resolver supplies facts; filters gate output. Don't conflate them.

## VARIANCE-driven structural axis (mandatory at high VARIANCE)

When a caller resolves `type='page'` with `VARIANCE >= 7` (read from `design/interview.md` or explicit user instruction), the filter MUST include at least one structural axis — `signature` (e.g. `off_grid`, `asymmetric`, `scroll_narrative`, `editorial_layout`) or `good_for_stage` matched to the page's anchor section.

Reason (documented v2.0 test failure on Lumen): mood-only filtering at high VARIANCE returned visually-on-brief but structurally-typical pages (xAI welcome + Synapse — both visually distinctive but both linear lengthwise). The system shipped looked bold but `/create` reproduced a classic `hero → stats → 2× feature-split → CTA → footer` chain on top of it. Without a structural axis in the resolver call, the dial never reached layout.

If the user explicitly banned typical structure in `interview.md` Q7, treat it as `VARIANCE = 10` regardless of dial — structural axis is non-negotiable.

Resolver implementations should warn (not block) when called with `VARIANCE >= 7` and no structural axis in `filters`:

> "Warning: VARIANCE=9 but filter lacks `signature` or `good_for_stage`. Result will be mood-only — likely visually-on-brief but structurally-typical pages. Add a structural axis or expect generic layout."

## Per-section anchor pattern

For multi-section page generation (e.g. `/create` on a marketing landing), a single page-level anchor is INSUFFICIENT. After the user picks the page-level anchor, run an additional resolver call per section type:

```python
for section in deep_fetched_page.sections:
    stage = map_section_to_good_for_stage(section)
    section_anchors = get_design_reference(
        type='page',
        filters={'good_for_stage': stage, 'mood': system.mood, 'appearance': system.appearance},
        limit=2
    )
    if section_anchors:
        deep_fetch(section_anchors[0])  # capture composition language
```

Cost: N additional list calls (typically 4-6 for a landing). Without this loop, sections 3-N collapse to defaults — documented as the v2.0 Lumen failure where StatsBand / FinalCTA / FeatureGrid had no per-section anchor and reverted to "3 numerals horizontally" / "headline + button left-aligned" / "4-cell data row". The page-level anchor only carries the hero.
