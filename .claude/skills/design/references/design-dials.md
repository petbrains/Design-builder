# Design Dials — Detailed Reference

Three tunable parameters that adjust output character. Set in chat or `.impeccable.md`. Default: (8, 6, 4).

## DESIGN_VARIANCE (1-10)

Controls layout symmetry and compositional risk.

| Level | Behavior |
|-------|----------|
| 1-3 (Predictable) | Flexbox `justify-center`, strict 12-column symmetrical grids, equal paddings |
| 4-7 (Offset) | `margin-top: -2rem` overlapping, varied image aspect ratios (4:3 next to 16:9), left-aligned headers over centered data |
| 8-10 (Asymmetric) | Masonry layouts, CSS Grid with fractional units (`grid-template-columns: 2fr 1fr 1fr`), massive empty zones (`padding-left: 20vw`) |

**MOBILE OVERRIDE (levels 4-10):** Any asymmetric layout above `md:` MUST aggressively fall back to single-column (`w-full`, `px-4`, `py-8`) on viewports < 768px to prevent horizontal scrolling.

**Anti-Center Bias:** When DESIGN_VARIANCE > 4, centered Hero/H1 sections are discouraged. Prefer split screen (50/50), left-aligned content/right-aligned asset, or asymmetric whitespace.

## MOTION_INTENSITY (1-10)

Controls animation complexity and expressiveness.

| Level | Behavior |
|-------|----------|
| 1-3 (Static) | No automatic animations. CSS `:hover` and `:active` states only |
| 4-7 (Fluid CSS) | `transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1)`. Animation-delay cascades for load-ins. Strictly `transform` and `opacity`. `will-change: transform` sparingly |
| 8-10 (Advanced Choreography) | Complex scroll-triggered reveals or parallax. Framer Motion hooks. NEVER use `window.addEventListener('scroll')` |

**CSS-Only Threshold:** At MOTION_INTENSITY < 4, limit to CSS-only transitions. No Framer Motion, no JS animation libraries.

**Spring Physics Threshold:** At MOTION_INTENSITY > 5, spring physics (`type: "spring", stiffness: 100, damping: 20`) for all interactive elements.

**Perpetual Micro-Interactions:** At MOTION_INTENSITY > 5, embed continuous micro-animations (Pulse, Typewriter, Float, Shimmer, Carousel) in components. Must be memoized and isolated in own Client Components.

## VISUAL_DENSITY (1-10)

Controls whitespace and information packing.

| Level | Behavior |
|-------|----------|
| 1-3 (Art Gallery) | Lots of whitespace. Huge section gaps. Everything feels expensive and clean |
| 4-7 (Daily App) | Normal spacing for standard web apps |
| 8-10 (Cockpit) | Tiny paddings. No card boxes — 1px lines to separate data. Everything packed. Monospace (`font-mono`) for all numbers |

**Dashboard Hardening:** At VISUAL_DENSITY > 7, generic card containers are BANNED. Use `border-t`, `divide-y`, or negative space. Data metrics breathe without boxes unless z-index hierarchy is functionally required.

## Combining Dials

The dials interact:
- High VARIANCE + Low DENSITY = Editorial magazine layout (asymmetric + airy)
- Low VARIANCE + High DENSITY = Enterprise dashboard (grid + packed)
- High MOTION + Low DENSITY = Portfolio/showcase (animated + spacious)
- High everything = Maximalist creative site (use with caution)

## Setting Dials

Users can set dials in several ways:
1. **In chat:** "Set motion to 3" or "Make it more dense"
2. **In `.impeccable.md`:** Add a `## Design Dials` section
3. **Implicitly:** "Make it feel more alive" → raise MOTION_INTENSITY. "Too busy" → lower VISUAL_DENSITY

When no dials are set, use defaults: DESIGN_VARIANCE=8, MOTION_INTENSITY=6, VISUAL_DENSITY=4.
