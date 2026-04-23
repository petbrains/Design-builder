# Style Preset: Minimalist

Clean editorial-style interfaces inspired by Notion, Linear, and top-tier workspace platforms. Warm monochrome palette, typographic contrast, flat bento grids, muted pastels. No gradients, no heavy shadows.

## Absolute Constraints

- NO Inter, Roboto, or Open Sans
- NO generic thin-line icons (Lucide, Feather, standard Heroicons)
- NO heavy drop shadows (`shadow-md`, `shadow-lg`, `shadow-xl`) — use ultra-diffuse, low-opacity (< 0.05)
- NO primary colored backgrounds for large sections
- NO gradients, neon colors, or 3D glassmorphism (subtle navbar blur OK)
- NO `rounded-full` for large containers/cards/buttons
- NO emojis — use icons or SVG primitives
- NO generic placeholders ("John Doe", "Lorem Ipsum")
- NO AI clichés ("Elevate", "Seamless", "Unleash")

## Typography

- **Sans-Serif (Body/UI):** `'SF Pro Display', 'Geist Sans', 'Helvetica Neue', 'Switzer', sans-serif`
- **Editorial Serif (Headlines/Quotes):** `'Lyon Text', 'Newsreader', 'Playfair Display', 'Instrument Serif', serif` — tight tracking (-0.02em to -0.04em), line-height 1.1
- **Monospace (Code/Metadata):** `'Geist Mono', 'SF Mono', 'JetBrains Mono', monospace`
- Body text: off-black `#111111` or `#2F3437`, line-height 1.6. Secondary: `#787774`

**Note:** In this preset, serif is appropriate for editorial headlines (exception to the main skill's dashboard serif ban). This is an editorial aesthetic, not a dashboard.

## Color Palette (Warm Monochrome + Spot Pastels)

Color is a scarce resource — semantic meaning or subtle accents only.

| Role | Value |
|------|-------|
| Canvas | `#FFFFFF` or `#F7F6F3` |
| Card surface | `#FFFFFF` or `#F9F9F8` |
| Borders/dividers | `#EAEAEA` or `rgba(0,0,0,0.06)` |
| Pale Red accent | `#FDEBEC` (text: `#9F2F2D`) |
| Pale Blue accent | `#E1F3FE` (text: `#1F6C9F`) |
| Pale Green accent | `#EDF3EC` (text: `#346538`) |
| Pale Yellow accent | `#FBF3DB` (text: `#956400`) |

## Component Specifications

### Bento Grids
- Asymmetrical CSS Grid layouts
- Cards: `border: 1px solid #EAEAEA`, radius 8-12px max
- Generous internal padding (24-40px)

### CTAs
- Solid `#111111` background, `#FFFFFF` text
- Radius 4-6px, no box-shadow
- Hover: subtle shift to `#333333` or `scale(0.98)` on `:active`

### Tags & Badges
- Pill-shaped, `text-xs`, uppercase, tracking `0.05em`
- Background: muted pastels from palette above

### Accordions
- No container boxes — `border-bottom: 1px solid #EAEAEA` only
- Clean `+`/`-` toggle icons

### Keystroke UIs
- `<kbd>` tags: `border: 1px solid #EAEAEA`, `radius: 4px`, `background: #F7F6F3`, monospace

## Motion

Invisible — present but never distracting. Quiet sophistication.

- **Scroll entry:** `translateY(12px)` + `opacity: 0` → resolve over 600ms with `cubic-bezier(0.16, 1, 0.3, 1)`. Use IntersectionObserver.
- **Hover:** Ultra-subtle shadow shift (0 → `0 2px 8px rgba(0,0,0,0.04)` over 200ms). `:active` → `scale(0.98)`.
- **Staggered reveals:** `animation-delay: calc(var(--index) * 80ms)`
- **Ambient:** Optional slow-moving gradient blob (20s+ duration, opacity 0.02-0.04, fixed/pointer-events-none)
- Only `transform` and `opacity` — no layout-triggering properties

## Execution Order

1. Establish macro-whitespace first (`py-24` or `py-32`)
2. Constrain content width (`max-w-4xl` or `max-w-5xl`)
3. Apply typographic hierarchy and monochrome variables
4. Every border: `1px solid #EAEAEA`
5. Add scroll-entry animations
6. Add visual depth (imagery, ambient gradients, subtle textures)
