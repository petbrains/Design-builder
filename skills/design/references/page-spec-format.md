# page-spec-format.md

Defines the structure of `design/pages/<name>.md`. `/design_page` writes specs in this format. `/build` parses them. Changing this format is a breaking change — existing specs in user repos must be re-generated or migrated.

## File location and naming

- Path: `design/pages/<slug>.md`
- Slug: kebab-case, derived from the page argument (`landing` → `landing.md`, `pricing page` → `pricing.md`, `about us` → `about.md`).
- Conflicts: if `design/pages/<slug>.md` exists, `/design_page` asks before overwriting.

## Frontmatter (none)

This file format does not use YAML frontmatter — the metadata lives in markdown sections so it's human-editable without parser concerns.

## Required sections (in this order)

### 1. Title block
```
# <Page Name>
generated: <YYYY-MM-DD>
source_inspiration: <comma-separated inspiration_page IDs from picks>
```

### 2. `## Purpose`
One paragraph (2-4 sentences). Either lifted from supplied documentation (Phase 2 docs path) or composed from Phase 2b interview Q1.

### 3. `## Reference anchor`
- `Primary:` `<inspiration_page id> — <title> — <screenshot_url>`
- `Per-section anchors:` bullet list mapping each section in `## Sections` to the `inspiration_page` id that informed it. Format per line: `- <section name> ← <id>`.
- `why_it_works (lifted):` triple-quoted block, verbatim from `inspiration_page.why_it_works` of the primary anchor.
- `generation_prompt (lifted):` triple-quoted block, verbatim from the primary anchor.

### 4. `## Layout posture`
One sentence describing the page's layout sequence (e.g. `hero → asymmetric-feature-grid → testimonial-strip → pricing → footer`).
One sentence naming any layout breaks used (e.g. `Layout break used: asymmetric-feature-grid (off-grid, breaks default linear posture)`). Required when DesignSystem.md `## Layout posture` declares a non-default posture.

### 5. `## Sections`

One subsection per page section, numbered. Each subsection follows this exact template:

```
### <N>. <Section Name>
- **Composition:** <one-line layout description; reference grid columns, alignment, asymmetry, mobile collapse>
- **Elements:** <ordered list of elements in the section's flow, e.g. eyebrow → H1 → subhead → CTA>
- **Content slots:** <bullet list, one per slot>
  - <slot name>: <slot — constraints, e.g. "verb-led, 2-3 words", "6-12 words, structural rule from generation_prompt">
- **Tokens:** <comma-separated token mappings: bg = surface-default, text = ink-primary, accent = primary-accent>
- **Animation:** <none | text description for hand-rolled CSS | "vendored from animations catalog: <filename>, library: <library>">
- **States:** <comma-separated state coverage notes: e.g. "loading skeleton, reduced-motion fallback (static gradient)">
```

If a section has no animation, write `- **Animation:** none` (do not omit the line).
If a section needs no special states beyond the design-system defaults, write `- **States:** default per style-guide.md`.

### 6. `## Edge cases`
Bullet list, one per relevant edge case (drawn from Phase 2b Q3 if interview, or invented from common cases if docs):
- `Empty state: <reference to content-library.md pattern + page-specific instantiation>`
- `Error state: <…>`
- `Loading state: <skeleton structure if non-default>`
- `Offline state: <fallback if relevant>`

If a state is not relevant to the page (e.g. a static landing page has no offline state), omit it.

### 7. `## Components needed`
Stack-aware list, derived from `design-system.md ## Stack` + the page's section requirements.

```
- <Component lib name>: Button, Card, Badge (only those actually used)
- Custom: <list of custom components needed; one line each>
- Vendored from animations catalog: <list of animation component filenames>
```

### 8. `## Animations`
For each vendored animation:
- `<descriptive name>` — `<animation.id>`, library: `<library list>`, surface: `<section name>`
- Hand-rolled animations (CSS keyframes for hover micro-interactions) listed similarly but marked `(hand-rolled, transform-only)`.

If the page has no animations, this section reads simply `None.` (one word).

### 9. `## Risks taken & gaps` (optional)
Present only if Distinctiveness Gate retry forced a change OR a fallback was used (landing_pattern_fallback for non-page references, library deps not yet installed, etc.).

Format same as `/improve` and `/build` Risks block:
```
─ <risk description>: <concrete instruction or note>
─ ...
```

## Validation rules `/build` enforces when parsing

- All 8 mandatory sections present (Risks is optional).
- `## Sections` has at least one numbered subsection.
- Each section subsection has all six bullet points (`Composition`, `Elements`, `Content slots`, `Tokens`, `Animation`, `States`) — `/build` errors with "spec malformed: section <N> missing <field>" if any is missing.
- `## Components needed` references actual components from the project's component library (cross-checked against `package.json` shadcn config / similar).
- Vendored animation component filenames cross-checked against the animations catalog (must resolve to a known `animation.id`).
