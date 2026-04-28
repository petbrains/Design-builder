# Color & Contrast

## LILA BAN + DO/DON'T — moved from SKILL.md in v1.2

**THE LILA BAN:** purple/blue AI aesthetic is BANNED. No purple button glows, no neon gradients.

**DO NOT:** gray text on colored backgrounds; pure black (#000) / pure white (#fff); cyan-on-dark; purple-to-blue gradients; dark mode with glowing accents as default.

## Color rules (web) — moved from SKILL.md in v1.2

**Web core rules** → `references/web/color-and-contrast.md`
- OKLCH not HSL. Reduce chroma near white/black. Tint neutrals toward brand hue.
- 60-30-10 rule. Max 1 accent. Saturation <80%.

## Color Spaces: Use OKLCH

**Stop using HSL.** Use OKLCH (or LCH) instead. It's perceptually uniform, meaning equal steps in lightness *look* equal—unlike HSL where 50% lightness in yellow looks bright while 50% in blue looks dark.

The OKLCH function takes three components: `oklch(lightness chroma hue)` where lightness is 0-100%, chroma is roughly 0-0.4, and hue is 0-360. To build a primary color and its lighter / darker variants, hold the chroma+hue roughly constant and vary the lightness — but **reduce chroma as you approach white or black**, because high chroma at extreme lightness looks garish.

The hue you pick is a brand decision and should not come from a default. Do not reach for blue (hue 250) or warm orange (hue 60) by reflex — those are the dominant AI-design defaults, not the right answer for any specific brand.

## Building Functional Palettes

### Tinted Neutrals

**Pure gray is dead.** A neutral with zero chroma feels lifeless next to a colored brand. Add a tiny chroma value (0.005-0.015) to all your neutrals, hued toward whatever your brand color is. The chroma is small enough not to read as "tinted" consciously, but it creates subconscious cohesion between brand color and UI surfaces.

The hue you tint toward should come from THIS project's brand, not from a "warm = friendly, cool = tech" formula. If your brand color is teal, your neutrals lean toward teal. If your brand color is amber, they lean toward amber. The point is cohesion with the SPECIFIC brand, not a stock palette.

**Avoid** the trap of always tinting toward warm orange or always tinting toward cool blue. Those are the two laziest defaults and they create their own monoculture across projects.

### Palette Structure

A complete system needs:

| Role | Purpose | Example |
|------|---------|---------|
| **Primary** | Brand, CTAs, key actions | 1 color, 3-5 shades |
| **Neutral** | Text, backgrounds, borders | 9-11 shade scale |
| **Semantic** | Success, error, warning, info | 4 colors, 2-3 shades each |
| **Surface** | Cards, modals, overlays | 2-3 elevation levels |

**Skip secondary/tertiary unless you need them.** Most apps work fine with one accent color. Adding more creates decision fatigue and visual noise.

### The 60-30-10 Rule (Applied Correctly)

This rule is about **visual weight**, not pixel count:

- **60%**: Neutral backgrounds, white space, base surfaces
- **30%**: Secondary colors—text, borders, inactive states
- **10%**: Accent—CTAs, highlights, focus states

The common mistake: using the accent color everywhere because it's "the brand color." Accent colors work *because* they're rare. Overuse kills their power.

## Contrast & Accessibility

### WCAG Requirements

| Content Type | AA Minimum | AAA Target |
|--------------|------------|------------|
| Body text | 4.5:1 | 7:1 |
| Large text (18px+ or 14px bold) | 3:1 | 4.5:1 |
| UI components, icons | 3:1 | 4.5:1 |
| Non-essential decorations | None | None |

**The gotcha**: Placeholder text still needs 4.5:1. That light gray placeholder you see everywhere? Usually fails WCAG.

### Dark themes — the nav-link / small-mono trap

On dark backgrounds (`#0A0B10` and similar), a single muted-ink token at ~5:1 ratio passes AA on paper but visually washes out on small text — nav links at 12-13px, mono eyebrows with tracking at 11px, footer copy at small sizes. AA is a floor, not a target; "technically AA" reads as dim.

The fix is a **two-tier muted-ink system**, not a single `--ink-muted`:

| Token | Contrast vs `surface_default` | Use for |
|---|---|---|
| `--ink-muted` | 4.5–5.5:1 | Body secondary text ≥14px |
| `--ink-muted-strong` | 6.5–7.0:1 | Nav links, eyebrows, mono labels at 11–13px, footer small copy |

Documented test failure (Lumen v2.0 audit): `--ink-muted: #7A7E8C` on `#0A0B10` was 5.3:1, technically AA, but nav links at 12px read as borderline-invisible against the surface and users reported "switchers wash out".

Alternatives if you don't want a second token:
- Bump `--ink-muted` itself toward `#9095A4` (~6.5–6.8:1) globally and accept that "secondary" body becomes slightly stronger.
- Use accent on hover/focus for nav links (gives them an active state instead of relying on resting contrast).
- Underline-on-hover with `text-decoration-thickness: 1px` and `text-underline-offset: 4px` — gives nav links a structural presence beyond hue.

`/setup` Phase 5 emits `--ink-muted-strong` automatically when `appearance=dark`; if you're authoring tokens by hand, do the same.

### Dangerous Color Combinations

These commonly fail contrast or cause readability issues:

- Light gray text on white (the #1 accessibility fail)
- **Gray text on any colored background**—gray looks washed out and dead on color. Use a darker shade of the background color, or transparency
- Red text on green background (or vice versa)—8% of men can't distinguish these
- Blue text on red background (vibrates visually)
- Yellow text on white (almost always fails)
- Thin light text on images (unpredictable contrast)

### Never Use Pure Gray or Pure Black

Pure gray (`oklch(50% 0 0)`) and pure black (`#000`) don't exist in nature—real shadows and surfaces always have a color cast. Even a chroma of 0.005-0.01 is enough to feel natural without being obviously tinted. (See tinted neutrals example above.)

### Testing

Don't trust your eyes. Use tools:

- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- Browser DevTools → Rendering → Emulate vision deficiencies
- [Polypane](https://polypane.app/) for real-time testing

## Theming: Light & Dark Mode

### Dark Mode Is Not Inverted Light Mode

You can't just swap colors. Dark mode requires different design decisions:

| Light Mode | Dark Mode |
|------------|-----------|
| Shadows for depth | Lighter surfaces for depth (no shadows) |
| Dark text on light | Light text on dark (reduce font weight) |
| Vibrant accents | Desaturate accents slightly |
| White backgrounds | Never pure black—use dark gray (oklch 12-18%) |

In dark mode, depth comes from surface lightness, not shadow. Build a 3-step surface scale where higher elevations are lighter (e.g. 15% / 20% / 25% lightness). Use the SAME hue and chroma as your brand color (whatever it is for THIS project — do not reach for blue) and only vary the lightness. Reduce body text weight slightly (e.g. 350 instead of 400) because light text on dark reads as heavier than dark text on light.

### Token Hierarchy

Use two layers: primitive tokens (`--blue-500`) and semantic tokens (`--color-primary: var(--blue-500)`). For dark mode, only redefine the semantic layer—primitives stay the same.

## Alpha Is A Design Smell

Heavy use of transparency (rgba, hsla) usually means an incomplete palette. Alpha creates unpredictable contrast, performance overhead, and inconsistency. Define explicit overlay colors for each context instead. Exception: focus rings and interactive states where see-through is needed.

---

**Avoid**: Relying on color alone to convey information. Creating palettes without clear roles for each color. Using pure black (#000) for large areas. Skipping color blindness testing (8% of men affected).

## Additional Color Rules

### The 1-Accent Constraint
Maximum 1 accent color per project. Saturation < 80%. Use absolute neutral bases (Zinc/Slate) with high-contrast singular accents (Emerald, Electric Blue, Deep Rose).

### Color Consistency
Stick to one palette for the entire output. Do not fluctuate between warm and cool grays within the same project.

### THE LILA BAN (Expanded)
The "AI Purple/Blue" aesthetic is the most recognizable AI tell after gradient text. Specifically banned:
- Purple button glows
- Neon purple/blue gradients
- Violet-to-cyan transitions
- Any purple as primary accent on dark backgrounds

Replace with: high-contrast neutrals + singular warm or cool accent.
