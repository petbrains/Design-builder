---
name: designlib-mcp
description: designlib MCP — authoritative catalog of styles, palettes, font pairs, domain recommendations (web + iOS). Primary token source for /design system and /design craft.
---

# designlib MCP

**Server (hosted):** `https://designlib-production.up.railway.app/mcp` (HTTP, read-only)
**Catalog:** 67 styles · 100 palettes · 34 font pairs · 134 domains · web + iOS

designlib is a curated, hand-maintained source of truth for design tokens. It replaces LLM guessing (invented hex codes, random font pairings) with retrieval. When available, it is the **primary** source for styles/palettes/fonts/domain recommendations in this skill.

## Token sourcing priority

When any `/design` command needs tokens, resolve in this order:

1. **Project tokens** — `.impeccable.md`, existing `tailwind.config`, `tokens.css`, `AccentColor.colorset`, or other in-repo design system
2. **designlib MCP** — if tool list contains `mcp__*designlib*` or similar, prefer it for styles/palettes/fonts/domain picks. Always pass `platform="web"` or `platform="ios"` explicitly.
3. **Local CSV** (`data/`, `scripts/search.py`) — covers UX guidelines (99), charts (25), landing patterns, icons, tech-stack specifics, anti-patterns — things designlib does NOT cover
4. **Free generation** — last resort; if you reach this step, note explicitly in output: *"no authoritative source, generated freely"*

## Setup check

Before using designlib tools, verify availability:
- Tool list contains `mcp__<prefix>__list_styles` or similar — proceed
- Not in tool list — fall back to `scripts/search.py` with equivalent CSV queries and tell the user: *"designlib MCP not connected; using local CSV fallback. Install: `claude mcp add --transport http designlib https://designlib-production.up.railway.app/mcp`"*

## Tools (12, all read-only)

All responses: `{items, total_count, limit, offset, meta: {schema_version, platform, entity_type, truncated}}`.
Unknown IDs: `{error_code: "NOT_FOUND", message, field, suggest_tool}`.

| Tool | Key args | Purpose |
|---|---|---|
| `list_style_facets` | `platform` | Valid family/tone/density/appearance/tag values |
| `list_styles` | `platform`, `family?`, `appearance?`, `tone?`, `density?`, `tags?`, `limit=50`, `offset=0` | Shortlist styles |
| `get_style` | `style_id`, `include_cross_links=true`, `cross_links_limit=5` | Full token bundle + cross-links |
| `list_palette_facets` | `platform` | Valid family/mood/appearance/tag |
| `list_palettes` | `platform`, `family?`, `appearance?`, `mood?`, `tags?`, `limit`, `offset` | Shortlist palettes |
| `get_palette` | `palette_id` | Full role mapping + contrast pairs |
| `list_font_pair_facets` | `platform` | Valid category/style_fit/tag |
| `list_font_pairs` | `platform`, `category_id?`, `style_fit?`, `tags?`, `limit`, `offset` | Shortlist font pairs |
| `get_font_pair` | `font_pair_id` | Heading/body/mono specs + weights + fallbacks |
| `list_domain_facets` | — | Valid category/audience/tone |
| `list_domains` | `category_id?`, `audience?`, `tone?`, `limit`, `offset` | Platform-agnostic domain catalog |
| `get_domain` | `domain_id`, `platform`, `top_n=5` | Domain + top-N style/palette/font recs per platform |

## Canonical workflows

### Domain-first (preferred for `/design system` interview)

```
1. list_domain_facets()                                  → audience/tone options
2. list_domains(audience=<from interview>, tone=<...>)   → shortlist
3. get_domain(domain_id=<picked>, platform="web"|"ios", top_n=3)
       → 3 styles + their palettes + font pairs, ranked
4. Present 3 variations to user (style+palette+fonts+motion-intensity per variant)
5. On pick: get_style(<picked>) + get_palette(<picked>) + get_font_pair(<picked>)
       → full tokens for implementation
```

### Style-first (when user has aesthetic in mind)

```
1. list_style_facets(platform="ios")                    → families available
2. list_styles(platform="ios", family="fitness_vitality", limit=5)
3. get_style(style_id=<picked>)                          → tokens + cross_links
```

### Platform-split (for `/design system cross`)

Run the domain-first workflow twice — once with `platform="web"`, once with `platform="ios"`. Then align: pick a web style and an iOS style that share palette family and tone, even if the specific palette_id differs (iOS goes through a separate median pipeline preserving SF family + system spacing).

## Prompt patterns that work

- *"Find a style for a fintech dashboard on web and give me the palette + typography"* → `list_domains(audience="fintech")` → `get_domain(..., platform="web")` → `get_palette` → `get_font_pair`
- *"Show me all iOS-native styles in the fitness_vitality family"* → `list_styles(platform="ios", family="fitness_vitality")`
- *"What are the tokens for academia_classical?"* → `get_style(style_id="academia_classical")`

**Rule:** when you don't know valid enum values for `family`/`tone`/`audience`, call `list_*_facets` first. Otherwise you will hallucinate filters and get `NOT_FOUND`.

## Payload limits

Responses >25 000 chars are truncated with `meta.truncated=true`. Only happens on wide `list_*` calls — lower `limit` or paginate via `offset`.

## When to skip designlib

- Existing mature project design system — use their tokens, don't override
- Brand-specific assets (logos, illustrations, custom icons) — not in catalog
- Writable storage needed — this server is read-only
- Offline / no MCP connection — fall back to `scripts/search.py` + CSVs

## Complementary references

| Need | Use |
|---|---|
| Web UX guidelines, charts, landing patterns, icons, anti-patterns | local CSV (`scripts/search.py`) |
| iOS-native HIG details (materials, haptics, gestures, Liquid Glass specifics) | `references/ios/` |
| Brand identity, logos, CIP, slides, banners | `references/brand/`, `references/design/`, `references/slides/` |
| Tokens for a concrete product domain/platform | **designlib MCP** (this doc) |
