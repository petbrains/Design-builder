# Style Preset: Brutalist

Raw mechanical interfaces fusing Swiss typographic print with military terminal aesthetics. Rigid grids, extreme type scale contrast, utilitarian color, analog degradation effects. For data-heavy dashboards, portfolios, or editorial sites that need to feel like declassified blueprints.

## Visual Archetypes

**Pick ONE per project. Do not mix.**

### Swiss Industrial Print (Light Mode)
1960s corporate identity + heavy machinery blueprints.
- High-contrast light mode on newsprint/off-white substrates
- Monolithic heavy sans-serif typography
- Unforgiving structural grids with visible dividing lines
- Oversized viewport-bleeding numerals
- Heavy use of primary red as accent

### Tactical Telemetry / CRT Terminal (Dark Mode)
Classified military databases + aerospace HUDs.
- Dark mode exclusively
- High-density tabular data
- Monospaced typography dominance
- Technical framing (ASCII brackets, crosshairs)
- Simulated hardware limitations (phosphor glow, scanlines)

## Typography

Extreme variance in scale, weight, and spacing. Typography IS the structure.

### Macro-Typography (Structural Headers)
- **Fonts:** Neue Haas Grotesk (Black), Inter (Extra Bold/Black), Archivo Black, Monument Extended
- **Scale:** Massive fluid type — `clamp(4rem, 10vw, 15rem)`
- **Tracking:** Extremely tight, negative (-0.03em to -0.06em)
- **Leading:** Compressed (0.85 to 0.95)
- **Case:** UPPERCASE exclusively

**Note:** In brutalist context, Inter is permitted for structural macro-typography at Black weight — this is a deliberate exception to the main skill's font ban, as massive uppercase Inter Black reads as industrial, not generic.

### Micro-Typography (Data/Telemetry)
- **Fonts:** JetBrains Mono, IBM Plex Mono, Space Mono, VT323
- **Scale:** Fixed small (10-14px)
- **Tracking:** Generous (0.05em to 0.1em) — mechanical typewriter feel
- **Case:** UPPERCASE exclusively

### Textural Contrast (Rare)
- High-contrast serif (Playfair Display, EB Garamond, Times New Roman)
- Heavily post-processed: halftone filters, 1-bit dithering
- Used exceedingly sparingly for artistic disruption

## Color System

No gradients, soft shadows, or translucency. Colors simulate physical media or primitive displays.

### Swiss Industrial Print
| Role | Value |
|------|-------|
| Background | `#F4F4F0` or `#EAE8E3` (matte unbleached paper) |
| Foreground | `#050505` to `#111111` (carbon ink) |
| Accent | `#E61919` or `#FF2A2A` (aviation/hazard red) — ONLY accent |

### Tactical Telemetry
| Role | Value |
|------|-------|
| Background | `#0A0A0A` or `#121212` (deactivated CRT, not pure black) |
| Foreground | `#EAEAEA` (white phosphor) |
| Accent | `#E61919` or `#FF2A2A` (same red) |
| Terminal green | `#4AF626` — OPTIONAL, max 1 element |

## Layout

Mathematically engineered. Visible compartmentalization.

- **Blueprint Grid:** Strict CSS Grid. Elements anchored to grid tracks.
- **Visible borders:** Solid 1-2px borders delineate zones. `<hr>` spans full width.
- **Bimodal density:** Extreme data density + vast negative space framing macro-typography.
- **Zero border-radius.** All corners exactly 90 degrees.

## UI Components

Standard web conventions replaced with utilitarian industrial elements:
- **ASCII framing:** `[ DELIVERY SYSTEMS ]`, `< RE-IND >`, `>>>`, `///`
- **Industrial markers:** `®`, `©`, `™` as geometric elements
- **Technical assets:** Crosshairs (`+`) at grid intersections, barcodes, warning stripes, random strings (`REV 2.6`, `UNIT / D-01`)

## Textural Effects

Simulated analog degradation via CSS/SVG:
- **Halftone/dithering:** Dot-matrix patterns via `mix-blend-mode: multiply` + SVG radial dots
- **CRT scanlines:** `repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px)`
- **Mechanical noise:** Global low-opacity SVG static filter on DOM root

## Engineering

1. `display: grid; gap: 1px;` with contrasting bg colors for razor-thin dividers
2. Semantic tags: `<data>`, `<samp>`, `<kbd>`, `<output>`, `<dl>`
3. CSS `clamp()` exclusively for macro-typography
