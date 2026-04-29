---
description: Scaffold design/ folder, detect/confirm project stack, run interview, render foundation. Writes design-system.md, style-guide.md, content-library.md, tokens.css, preview.html.
argument-hint: "[--migrate is NOT a v2.1 flag — fresh setup only]"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, mcp__designlib__list_inspiration_pages, mcp__designlib__get_inspiration_page, mcp__designlib__list_inspiration_page_facets, mcp__designlib__list_palettes, mcp__designlib__list_styles, mcp__designlib__list_font_pairs, mcp__designlib__list_domains, mcp__designlib__list_landing_patterns
---

# /design-builder:setup — establish the design foundation

You are the entry point for a brand-new design project. Activate the `design` skill (`skills/design/SKILL.md`). You produce the artifacts in `design/` that every later command (`/create`, `/improve`, `/review`) relies on. Until you finish, the user has no design system.

## Phase 0 — Scaffold + stack detect (NEW in v2.1)

This phase runs first. No interview question is asked until 0.4 completes.

### 0.1 — Scaffold the `design/` folder

Create the following structure (use `Bash mkdir -p` plus `Write` for the files):

```
design/
  pages/
  screens/
  references/
    README.md
  reviews/
  .cache/
    .gitignore
```

Contents:

- `design/.cache/.gitignore`: a single line `*` — excludes the entire `.cache/` directory from git.
- `design/references/README.md`:
  ```
  # Design references

  Drop reference materials here:
  - URLs and Figma links → add to `urls.md` (one per line, with optional context).
  - Screenshots and reference images → drop into this folder directly. Files prefixed `ref-` are auto-downloads from /setup; everything else is your manual addition.

  /setup, /design_page, and /design_screen all read this folder when relevant.
  ```

After scaffolding, surface this single message to the user:
> "Created `design/`. If you have references — drop URLs/screenshots/Figma links in `design/references/` or paste them here. Ready to start? (`go` / I have references)"

If the user pastes URLs in chat: append them to `design/references/urls.md` (create the file). If they say `go`: continue to 0.2 immediately.

### 0.2 — Detect project stack

Read these files in parallel (with `Read`, `Glob`, or `Bash ls` as appropriate):

- `package.json` (root; if missing → not a JS/TS project)
- `Package.swift`, `*.xcodeproj` (iOS project signals)
- `pubspec.yaml` (Flutter)
- `Cargo.toml`, `go.mod` (signal: probably not a frontend project being designed)
- root `index.html` (when no `package.json` exists → static HTML)

Classification rules:

| Signals | Stack |
|---|---|
| `package.json` deps include `next` | Next.js (then check App Router vs Pages Router by directory presence) |
| `package.json` deps include `react` AND `vite` | Vite + React |
| `package.json` deps include `react` AND no bundler clue | CRA / generic React |
| `package.json` deps include `vue` | Vue |
| `package.json` deps include `svelte` | Svelte |
| `package.json` deps include `@angular/core` | Angular |
| `Package.swift` OR `*.xcodeproj` (with `import SwiftUI` in Sources) | SwiftUI |
| `Package.swift` OR `*.xcodeproj` (UIKit only) | UIKit |
| `pubspec.yaml` | Flutter |
| Only `index.html` | Static HTML |
| None | (empty — ask) |

Also check for styling and component lib:
- `tailwindcss` in deps → Tailwind (check version: v3 vs v4 from `package.json`)
- `styled-components`, `@emotion/*`, `sass` → record
- `components/ui/` directory existence + `components.json` (shadcn config) → shadcn/ui

### 0.3 — Confirm or ask

Three branches based on 0.2:

- **Detected unambiguously:** confirm in one message:
  > "I see **<framework> + <styling> + <component lib if any>**. Right? (`y` / let me correct)"
- **Ambiguous (multiple candidates):** present multiple choice:
  > "Multiple stacks possible. Which is this? (1) <option A>  (2) <option B>  ..."
- **Empty (no stack):** ask:
  > "No stack detected. What are we building? `Next.js` / `Vite + React` / `SwiftUI` / `Flutter` / `static HTML` / `other` (specify)"

Wait for response. Capture chosen stack into a working variable for 0.4.

### 0.4 — Offer scaffold (only if no project initialized)

If 0.3 ended with the user choosing a stack but the project files indicate **no initialized project** (e.g. user picked Next.js but `package.json` doesn't exist, or picked SwiftUI but `Package.swift` doesn't exist):

> "To generate code via `/build` later, the project needs to be initialized. Run this in another terminal:
> ```
> <stack-appropriate scaffold command — see table below>
> ```
> Tell me `done` when ready, or `skip` to keep designing without a project (you'll scaffold later)."

Stack → command:

| Stack | Suggested scaffold command |
|---|---|
| Next.js | `npx create-next-app@latest . --typescript --tailwind --app` |
| Vite + React | `npm create vite@latest . -- --template react-ts` |
| Vue | `npm create vue@latest .` |
| SwiftUI | (Xcode UI: File → New → Project → App; or `xcodegen` if user has it) |
| Flutter | `flutter create .` |
| Static HTML | (no scaffold needed — explain that `/build` will write `<name>.html` + `<name>.css` directly) |

**Never run the scaffold command yourself.** Suggest only — destructive in user's repo.

### 0.5 — Persist the stack

Write `design/.cache/stack.json`:

```json
{
  "framework": "next.js",
  "framework_version": "15",
  "router": "app",
  "language": "typescript",
  "styling": "tailwindcss",
  "styling_version": "v4",
  "component_lib": "shadcn/ui",
  "target": "web",
  "responsive": "mobile-first",
  "project_initialized": true,
  "detected_at": "<YYYY-MM-DD>"
}
```

Set `project_initialized: false` if the user said `skip` in 0.4. The `## Stack` section in `design-system.md` (Phase 5a) is rendered from this file.

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

**Vocabulary check (mandatory before any list query).** Call `mcp__designlib__list_inspiration_page_facets`, `mcp__designlib__list_palette_facets`, `mcp__designlib__list_font_pair_facets` once each. Map the user's mood/direction language from `interview.md` to actual facet values BEFORE building filters. The user's interview language is almost never in the library vocab (e.g. `cinematic`, `nocturnal`, `editorial-luxury` — none of these are MCP facets). Build a mapping table in your scratchpad:

| User's word | MCP-vocab fallback |
|---|---|
| cinematic | moody + confident |
| nocturnal/astral | appearance=dark + mysterious |
| scientific | clinical + techy |

Show the mapping to the user only if the translation is non-obvious or lossy.

1. Call `get_design_reference(type='palette', filters={industry, mood: <one>, audience}, limit=4)`.
2. Call `get_design_reference(type='font_pair', filters={industry, mood: <one>}, limit=4)`.
3. Call `get_design_reference(type='page', filters={page_type='marketing_landing', mood: <one>, style_family: <one or omitted>}, limit=6)` — to ground in real examples. If you want to mix moods, call this 2-3 times with different `mood` values and dedupe by `id`.

**Structural axis (mandatory if user banned typical structure).** If `interview.md` Q7 captured a constraint like "не типичная структура лендинга" / "non-standard layout" / "off-grid" / VARIANCE ≥ 7 in dials, ALSO call `list_inspiration_pages` filtered by `signature` (e.g. `off_grid`, `asymmetric`, `scroll_narrative`, `editorial_layout`) — at least one candidate must be anchored on a structurally distinctive page, not just a visually distinctive one. Otherwise the system you ship will look bold but `/create` will reproduce a classic linear landing on top of it.

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

  **Lift the prose triad from the deep-fetched anchor pages into a `## Structural intent` section.** Quote `why_it_works` and `generation_prompt` from each primary anchor verbatim. These are the load-bearing UX rationale — they tell `/create` later WHY the reference looks the way it does (e.g. "stealth + discovery via section ordering", "tight grid + denser type carries trust"). Without this section, `/create` only sees palette + typography and reverts to default linear posture. Treat this as a hard requirement, not optional flavor text.

  **Add a `## Layout posture` section** if the user banned typical structure or VARIANCE ≥ 7. State the required posture in one sentence (e.g. "section sequence MUST include at least one of: off-grid asymmetric block, scroll-narrative pinned section, or section-order break — never a default hero → 3-col features → CTA chain"). `/create` Phase 5 step 5 reads this as the layout-distinctiveness gate.

- `design/tokens.css` — CSS custom properties for all palette + typography + spacing. Use `templates/web/` starters if the platform is web. For iOS, write `design/tokens.json` instead and create SwiftUI theme files per `templates/ios/Theme/`.

  **Dark-theme nav contrast.** If `appearance=dark`, emit a separate token `--ink-muted-strong` (~6.5-7:1 against `--surface-default`) in addition to `--ink-muted` (~4.5-5.5:1). Annotate in `system.md`: "use `--ink-muted-strong` for nav links, eyebrows ≤13px, footer copy at small sizes; `--ink-muted` only for ≥14px secondary text." Otherwise nav links wash out — documented v2.0 issue from Lumen test where `--ink-muted #7A7E8C` against `#0A0B10` (~5.3:1) read as borderline at 12px.

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
