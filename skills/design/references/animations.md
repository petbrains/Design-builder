# animations — schema map for the skill

> What this is: a digestible map of the `animations` table that the `designlib` MCP server exposes via `list_animations` / `get_animation` / `list_animation_facets`. The skill loads this when any command resolves `type='animation'` through `get_design_reference()`.
>
> 120 records, all React + library-backed (framer-motion / three / gsap / motion / ogl / lucide-react). Each record carries verbatim TSX in `prompt_text` for vendoring.

## When to consult

Load this file when:

- A command (typically `/create` Phase 4c, or `/improve --restructure` step 4) is about to filter `animations` and you need to know which `category` / `complexity` / `style_tag` values are valid.
- You need to interpret an MCP response field — e.g. what's in `prompt_text`, how `placement[]` differs from `category`.
- You're deciding whether to run the animation-lookup phase at all (gate signals, surface mapping).

## Coverage at a glance (120 rows)

| facet axis        | counts                                                                                  |
|-------------------|-----------------------------------------------------------------------------------------|
| **frameworks**    | react 120                                                                               |
| **categories**    | element 37 · background 37 · hero 19 · text_effect 12 · decoration 8 · overlay 3 · loader 2 · cursor_effect 2 |
| **complexity**    | medium 52 · heavy 39 · light 29                                                         |
| **interactivity** | cursor_track 34 · static 30 · hover 20 · click 17 · scroll 16 · mount_only 3            |
| **top libraries** | framer-motion 31 · three 20 · lucide-react 17 · gsap 15 · motion 10 · ogl 8 · @react-three/fiber 5 |
| **top style_tags**| dark 81 · minimal 60 · 3d 45 · gradient 29 · geometric 25 · organic 23 · futuristic 21 · colorful 19 · glass 14 |
| **top placements**| hero 91 · section 74 · background 53 · inline 23 · fullscreen 15                        |
| **top use_when**  | dark_landing_page 64 · product_showcase 54 · interactive_demo 32 · brand_personality_playful 30 · value_proposition_emphasis 25 |

Always call `list_animation_facets()` before filtering with open-vocab values you're not sure about — open vocabularies (`style_tag`, `placement`, `use_when`, `library`, `keyword`) drift over time as the catalog grows.

## Primary filter triad (recommended for `/create` Phase 4c)

**MCP filters are SINGULAR strings, not arrays.** `list_animations` accepts one `category`, one `library`, one `style_tag`, etc. To "filter by 2-3 style_tags", call multiple times and dedupe by `id`.

The combination most likely to return a small, relevant set:

- `category` — pick the surface (1 of 8 closed-vocab values). Always set when calling `get_design_reference(type='animation')`.
- `complexity` — pick the budget (1 of 3: `light` / `medium` / `heavy`). Map from `MOTION_INTENSITY`: 1-4 → `light`, 5-7 → `medium`, 8-10 → `heavy`.
- `library` — pick the dep (open vocab, top 7 covered above). Constrain to libraries already in the project's `package.json` to avoid forcing a new dep.

Mood-only filtering returns visually-on-brief but performance-spendthrift results — e.g. a brief that asked for "minimal motion" can land on a heavy three.js shader if you only filter by `style_tag='minimal'`. Always couple `style_tag` with `complexity`.

If results are empty or too few (<2): drop `library` first (so you see candidates regardless of dep), then `style_tag`, keep `category` + `complexity`. If still empty, the resolver returns `[]` and the caller must decide whether to skip animation integration entirely or relax the surface gate.

## Vocab (live values from `list_animation_facets`)

### `category` (8 values, closed)
`background`, `hero`, `loader`, `text_effect`, `element`, `cursor_effect`, `overlay`, `decoration`.

### `framework` (2 values, closed)
`react` (currently 120/120), `vanilla_html` (reserved — 0 records today; may grow).

### `interactivity` (6 values, closed)
`static`, `hover`, `click`, `cursor_track`, `scroll`, `mount_only`.

### `complexity` (3 values, closed)
`light`, `medium`, `heavy`.

### `style_tags` (open vocab — selection)
`dark`, `minimal`, `3d`, `gradient`, `geometric`, `organic`, `futuristic`, `colorful`, `glass`, `neon`, `aurora`, `shader`, `wireframe`, `liquid`, `particles`. Live values: `list_animation_facets()`.

### `placement` (open vocab — selection)
`hero`, `section`, `background`, `inline`, `fullscreen`, `footer`, `card`, `button`. Live values: `list_animation_facets()`.

### `use_when` (open vocab — selection)
`dark_landing_page`, `product_showcase`, `interactive_demo`, `brand_personality_playful`, `value_proposition_emphasis`, `enterprise_polish`, `feature_reveal`, `loading_state`, `404_page`. Live values: `list_animation_facets()`.

### `libraries` (open vocab — top 7)
`framer-motion`, `three`, `lucide-react`, `gsap`, `motion`, `ogl`, `@react-three/fiber`. Plus long tail.

### Mood → style_tag map

For `/create` Phase 4c — translate `system.md` mood (from `list_inspiration_page_facets` mood vocab) to an animation `style_tag`:

| `system.md` mood       | preferred `style_tag`             |
|------------------------|-----------------------------------|
| `moody`, `mysterious`  | `dark`                            |
| `confident`, `editorial` | `minimal`                       |
| `futuristic`, `techy`  | `3d` OR `futuristic`              |
| `playful`, `energetic` | `colorful` OR `gradient`          |
| `minimal`, `calm`, `clinical` | `minimal`                  |
| `organic`, `warm`      | `organic`                         |
| `maximalist`           | `gradient` OR `3d`                |
| `brutalist`            | `geometric`                       |
| `elegant_luxury`       | `glass` OR `minimal`              |
| `retro_vintage`        | `geometric` (fallback — caller may need to skip animation-lookup) |
| `cool`, `approachable` | `minimal`                         |

When the table doesn't have a clean mapping (e.g. `retro_vintage` — the catalog is light on retro motion), it's better to skip Phase 4c for that page than to force a mismatched animation.

## Platform note

Animations are **React-only**. The MCP returns `framework='react'` for all 120 current records; there is no `platform` filter parameter. For iOS / cross / Vue / static-HTML callers, the resolver returns `[]` — Phase 4c skips entirely and the page generates without an animation integration. Do not silently fall back to "render a CSS keyframes animation inline" — Phase 4c not running is the correct behaviour, not a fallback opportunity.

## Field-by-field reference

> **List vs deep-fetch:** `list_animations` returns a SUBSET of fields (`id`, `title`, `description`, `category`, `framework`, `complexity`, `style_tags`). To get `prompt_text`, `libraries`, `placement[]`, `use_when[]`, `keyword[]`, `interactivity`, `component_filename`, `source_file`, you MUST call `get_animation(animation_id=...)`. The list response does NOT truncate `description` (animations carry short 1-2 sentence descriptions).

### Top-level identity (in list response)
- `id` — `animation_<filename_kebab_to_snake>`. Stable. Use for `get_animation(animation_id=<id>)` deep-fetch. **The param is named `animation_id`, not `id`.**
- `title` — short human label.
- `description` — 1-2 sentences, max ~250 char. Not truncated in list response (unlike `inspiration_pages`).

### Classification (in list response)
- `category` — see vocab.
- `framework` — see vocab.
- `complexity` — see vocab.
- `style_tags` — array of 2-6 tags in the response; filter param `style_tag` is singular.

### Classification (only in deep-fetch)
- `interactivity` — see vocab. Single value.
- `libraries` — array of npm package names. Use this to check `package.json` before vendoring.
- `placement` — array of placement tags. Filter param `placement` is singular.
- `use_when` — array of situational tags. Filter param `use_when` is singular.
- `keyword` — array of 5-10 free-form search terms. Filter param `keyword` is singular.

### Component data (only in deep-fetch)
- `component_filename` — e.g. `aurora-background.tsx`. Use as the destination filename when vendoring into `src/components/animations/`.
- `prompt_text` — markdown blob. Structure: stack notes → install block → verbatim TSX inside fenced code blocks → demo → notes. **Caller must extract the first ` ```tsx ` or ` ```jsx ` fenced block when vendoring**; do not write the whole markdown into a `.tsx` file.
- `source_file` — provenance pointer (where the prompt came from in the source repo).
- `source_index`, `sort_order` — stable ordering hints.

## Critical contract notes

- **Filter values are SINGULAR.** `list_animations(style_tag='dark')` is fine; `list_animations(style_tags=['dark','3d'])` is not. Multi-value = multi-call + dedupe by `id`. (Same convention as `inspiration_pages`.)
- **Deep-fetch param is `animation_id`, not `id`.** `get_animation(id=...)` will fail. (Same kind of footgun as `get_inspiration_page(page_id=...)`.)
- **`prompt_text` is markdown — extract the TSX block before writing.** Look for the first fenced block tagged `tsx` or `jsx`; the rest of the markdown is install instructions, demo wiring, and notes that don't belong in a component file.
- **Library deps are not in the project's `package.json` by default.** The caller MUST check `animation.libraries` against the project's deps before vendoring. Missing libraries go into a `Risks taken & gaps` block — never auto-`npm install`.
- **Animations are React-only.** iOS / Vue / vanilla projects get `[]` from the resolver. The caller skips Phase 4c entirely; do not improvise an inline CSS animation as a "fallback".
- **No screenshot.** `screenshot_url` is null on `DesignReference` for animations — the preview is the verbatim TSX. When the resolver normalises the row, leave `screenshot_url=null` and let the caller render a textual card instead of a visual one.

## Known issues

(Empty placeholder — populate as MCP-side issues surface. As of 2026-04-28, no broken records or stale image references reported.)

## Future extensions (KB-EXTENSION)

- **`framework='vanilla_html'` records** — reserved in the closed vocab; 0 records today. When records arrive, refresh the §"Coverage at a glance" framework counts and the §"Field-by-field reference" classification notes. Resolver dispatch needs no change — `framework` is just another singular filter on the same MCP tool.
- **iOS-native motion catalog** — separate sibling entity if it ships (`mcp__designlib__list_ios_motion`). Different schema (Core Animation / SwiftUI `withAnimation`), different resolver type. Not a `framework='swift'` row on `animations`. The schema map for that catalog will live in a sibling file `ios_motion.md`. Until then: iOS callers skip Phase 4c.

<!-- KB-EXTENSION: add new framework / catalog row here -->
