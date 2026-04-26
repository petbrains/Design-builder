---
name: design-system-interview
description: Structured interview for /design system command. Platform-aware (web / ios / cross). Produces the brief fed into designlib MCP + local context.
---

# Design System Interview

This is the script for `/design system <web|ios|cross>`. Follow it **in order**, **one question per message**. After interview → propose 3 variations → on pick → emit tokens via the appropriate pipeline (`web-pipeline.md` or `ios-pipeline.md`).

## Hard rule

**Do NOT skip questions.** If the user says "just pick something," keep at least sections 1, 2, 3 — product, context, personality. Without those designlib domain picks and local style matching degrade to hallucination.

## What "propose 3 variations" means

It does **not** mean: write three paragraphs in chat describing each option. That is the failure mode of this command and it is what the visual preview script exists to prevent.

It means:
1. Build 3 candidate JSON objects matching `scripts/generate_system_preview.py`'s schema.
2. Run them through `references/distinctiveness-gate.md` in HARD mode (regenerate failures).
3. Call `python scripts/generate_system_preview.py --candidates <tmp.json> --project "<name>" --platform <web|ios|cross>`.
4. Hand the user the absolute HTML path the script prints. The user opens it, presses 1/2/3, picks A/B/C.

Steps 1–3 are internal and produce no chat messages. Step 4 is one short message containing one path. **Anything else — paragraphs of A/B/C copy, hex lists, font lists, "I can render previews if you want" — is wrong.** Detailed protocol: `skills/design/SKILL.md` under `/design system`.

## Section 0 — Platform confirm

Argument parsing: `/design system web` → web pipeline only · `/design system ios` → iOS only · `/design system cross` → both, aligned · `/design system` (no arg) → ask:

> "This builds a design system tailored to platform. Pick: **web** / **ios** / **cross** (web + iOS aligned)."

Record choice as `PLATFORM`.

## Section 1 — Product (what & who)

Ask these, one per message. Accept short answers; push back only on generic ones.

1. **What is this product?** One sentence. *"A scheduling app for solo creators" — not "a SaaS for productivity".*
2. **Primary audience?** Who uses it, in what context (at desk / on phone between meetings / on tv at home / on watch during runs). This constrains density + touch-target + dark-mode posture.
3. **Top 3 jobs-to-be-done?** What are the first three things a user does? This determines which screens are load-bearing — and what your style must serve first.

If the answers are generic ("everyone," "productivity," "be fast") — **stop and reframe**. A design system made for everyone is made for no one. Ask for the most specific persona they'd reluctantly narrow to.

## Section 2 — Context (existing material)

4. **Do you have a `.impeccable.md` or design brief in the repo?** If yes, read it now — skip any question it already answers.
5. **Existing design system / tokens?** Check:
   - Web: `tailwind.config.*`, `tokens.css`, CSS custom properties in `:root`, existing shadcn theme
   - iOS: `*.xcassets/Colors`, `AccentColor.colorset`, `Assets.xcassets/AppIcon.appiconset`, any `Typography.swift` / `Theme.swift`
   - If found: ask *"extend these, or start fresh?"*
6. **Reference projects?** Apps/sites the user admires (URLs or names). Note: *reference* ≠ *clone*. These inform tone, not tokens.
7. **Anti-references?** Products they explicitly **don't** want to look like. These are often more useful than references — they reveal negative space in the brief.
8. **Figma / design files?** Link or path. If so, offer to run figma tools in parallel later.

## Section 3 — Personality

9. **Pick 3 words for voice/tone.** Not "modern" or "elegant" — dead categories. Push for specific: *"reverent · patient · unhurried"* or *"kinetic · defiant · raw"*. If they give weak words, propose 3 sharper alternatives.
10. **What absolutely should NOT feel like this?** Forces contrast. *"not startup-y, not playful, not crypto-native."*

## Section 4 — Platform-specific constraints

### If PLATFORM includes **web**:

11a. **Framework?** (React/Next, Svelte, Vue, Astro, plain HTML). Determines output format.
12a. **App shape?** (marketing page · dashboard · data-heavy SaaS · editorial · e-commerce · other). Drives density + layout patterns.
13a. **Dark/light/both?** If both — which is primary?
14a. **Any tokens must map to existing libraries?** (shadcn, Radix, MUI, Chakra).

### If PLATFORM includes **ios**:

11b. **iOS version floor?** (iOS 17 · iOS 18 · iOS 26). iOS 26 unlocks Liquid Glass + new Icon Composer.
12b. **Framework?** (SwiftUI only · SwiftUI+UIKit mix · pure UIKit legacy).
13b. **Which iOS visual-style family fits?** Pick from 10 in `references/ios/style-families.md`, or say *"help me choose"*. Options (preview):
   - `productive_neutral` · `editorial_content` · `fitness_vitality` · `finance_trust` · `creator_expressive` · `utility_tool` · `social_warmth` · `gaming_playful` · `academia_classical` · `luxury_refined`
14b. **Which platform surfaces matter?** Check all that apply: widgets · Live Activities · Dynamic Island · Lock Screen · Control Center · App Shortcuts · Apple Watch app · iPad app (tiling/menu bar) · Mac Catalyst · visionOS.
15b. **Haptic budget?** (off · system-only · curated-moments · expressive). Informs `sensoryFeedback` wiring.
16b. **Accessibility floor?** Dynamic Type to AX5 assumed; confirm Increase Contrast + Reduce Motion + Reduce Transparency support expected (it is — default yes).

## Section 5 — Design dials

17. **DESIGN_VARIANCE** (default 8) — *"asymmetry & spatial drama: 1 strict grid ↔ 10 masonry + fractional units"*
18. **MOTION_INTENSITY** (default 6) — *"0 static ↔ 10 scroll-driven parallax + springs everywhere"*
19. **VISUAL_DENSITY** (default 4) — *"1 art-gallery whitespace ↔ 10 cockpit packed data"*

Accept defaults if user declines — but always show them first.

---

## After interview: call designlib

Once sections 1–5 are captured:

```text
1. list_domain_facets()           → learn valid audience/tone enums
2. list_domains(audience=<q2 mapped>, tone=<q9 mapped>, category_id=<q12 mapped>)
3. get_domain(domain_id=<best match>, platform=<PLATFORM or "web"/"ios">, top_n=3)
```

If PLATFORM = `cross`: run `get_domain` twice (once per platform), then pick a domain shared across both.

If designlib unavailable: fall back to `scripts/search.py --platform <PLATFORM> --domain product "<q1 + q9 keywords>"` → hydrate from local CSV.

## Propose 3 variations

Each variation = {style, palette, font_pair, motion_intensity preset, density}. Present side-by-side:

| Variation | Style | Palette mood | Heading/body | Motion | Why this feels right |
|---|---|---|---|---|---|
| A | ... | ... | ... | ... | ... |
| B | ... | ... | ... | ... | ... |
| C | ... | ... | ... | ... | ... |

For each, show **1-line "what makes it unforgettable"** (per design principles — the differentiation hook).

Ask: *"Pick A / B / C, or ask me to remix."* — DO NOT emit tokens until chosen.

## On pick

- Call `get_style`, `get_palette`, `get_font_pair` for final IDs.
- Hand off to:
  - `web-pipeline.md` if PLATFORM includes web
  - `ios-pipeline.md` if PLATFORM includes iOS
- For `cross`: run both pipelines; ensure palette family + font tone align between outputs (they will diverge in specifics — SF vs webfont, semantic-color mapping).

## Anti-patterns during interview

- Don't batch questions ("Tell me about the product, audience, and tone") — this produces shallow answers
- Don't accept "modern / clean / elegant / minimal" without a counter-reframe — they are category-dead words
- Don't start proposing styles before section 3 completes — you will anchor on wrong tokens
- Don't offer `cross` as a default — it doubles work; offer it only when the user explicitly has both web AND iOS surfaces
