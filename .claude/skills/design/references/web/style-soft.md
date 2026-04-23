# Style Preset: Soft (Agency-Tier)

$150k+ agency-level digital experiences. Haptic depth, cinematic spatial rhythm, obsessive micro-interactions, flawless fluid motion. Apple-esque / Linear-tier design language.

## The Variance Mandate

NEVER generate the same layout or aesthetic twice. Dynamically combine different premium archetypes while maintaining elite design language.

## Anti-Patterns (Instant Fail)

- **Banned fonts:** Inter, Roboto, Arial, Open Sans, Helvetica
- **Banned icons:** Standard thick Lucide, FontAwesome, Material — use Phosphor Light, Remix Line
- **Banned borders:** Generic 1px solid gray, harsh dark shadows (`rgba(0,0,0,0.3)`)
- **Banned layouts:** Edge-to-edge sticky navbars, symmetrical 3-column Bootstrap grids
- **Banned motion:** Standard `linear` or `ease-in-out` — always custom cubic-bezier

## Vibe Archetypes (Pick 1 per project)

### Ethereal Glass (SaaS / AI / Tech)
- OLED black (`#050505`), radial mesh gradients (subtle glowing orbs)
- Vantablack cards with `backdrop-blur-2xl` and `white/10` hairlines
- Wide geometric Grotesk typography

### Editorial Luxury (Lifestyle / Real Estate / Agency)
- Warm creams (`#FDFBF7`), muted sage, deep espresso
- High-contrast Variable Serif fonts for massive headings
- CSS noise/film-grain overlay (`opacity-[0.03]`)

### Soft Structuralism (Consumer / Health / Portfolio)
- Silver-grey or pure white backgrounds
- Massive bold Grotesk typography
- Floating components with ultra-diffused ambient shadows

## Layout Archetypes (Pick 1 per project)

### Asymmetrical Bento
Masonry-like CSS Grid with varying card sizes (`col-span-8 row-span-2` + stacked `col-span-4`).
- **Mobile:** Single column, `gap-6`, all `col-span` reset to 1.

### Z-Axis Cascade
Stacked elements with varying depth, slight overlapping, subtle rotation (-2° to 3°).
- **Mobile:** Remove rotations and negative margins below 768px.

### Editorial Split
Massive typography left half (`w-1/2`), interactive content right half.
- **Mobile:** Full-width vertical stack, text on top.

**Universal mobile rule:** All layouts → `w-full`, `px-4`, `py-8` below 768px. Always `min-h-[100dvh]`, never `h-screen`.

## Haptic Micro-Aesthetics

### Double-Bezel (Doppelrand) Architecture
Never place cards flat. Use nested enclosures:
- **Outer shell:** `bg-black/5`, `ring-1 ring-black/5`, `p-1.5`, `rounded-[2rem]`
- **Inner core:** Own background, `shadow-[inset_0_1px_1px_rgba(255,255,255,0.15)]`, `rounded-[calc(2rem-0.375rem)]`

### Button-in-Button Pattern
Primary CTAs: fully rounded pills (`rounded-full`, `px-6 py-3`).
Trailing arrow (`↗`) nested in its own circular wrapper: `w-8 h-8 rounded-full bg-black/5 flex items-center justify-center`.

### Spatial Rhythm
- Macro-whitespace: `py-24` to `py-40` minimum
- Eyebrow tags: `rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em] font-medium`

## Motion Choreography

All motion simulates real-world mass and spring physics. Custom cubic-bezier only: `cubic-bezier(0.32, 0.72, 0, 1)`.

### Fluid Island Nav
- Floating glass pill navbar (`mt-6`, `mx-auto`, `w-max`, `rounded-full`)
- Hamburger morphs to X (rotate-45 / -rotate-45)
- Full-screen overlay: `backdrop-blur-3xl bg-black/80`
- Links: staggered mask reveal (`translate-y-12 opacity-0` → resolved with stagger)

### Magnetic Button Hover
- Scale down on active: `active:scale-[0.98]`
- Inner icon: `group-hover:translate-x-1 group-hover:-translate-y-[1px] scale-105`

### Scroll Entry
- Elements: `translate-y-16 blur-md opacity-0` → `translate-y-0 blur-0 opacity-100` over 800ms+
- Use IntersectionObserver or Framer Motion `whileInView`, never `addEventListener('scroll')`

## Performance

- Animate only `transform` and `opacity`
- `backdrop-blur` only on fixed/sticky elements
- Grain/noise: fixed, `pointer-events-none`, `z-50`
- No arbitrary z-index spam

## Pre-Output Checklist

- [ ] No banned fonts, icons, borders, shadows, or motion patterns
- [ ] Vibe + Layout archetype consciously selected
- [ ] All major cards use Double-Bezel architecture
- [ ] CTAs use Button-in-Button pattern where applicable
- [ ] Section padding ≥ `py-24`
- [ ] All transitions use custom cubic-bezier
- [ ] Scroll entry animations present
- [ ] Layout collapses at 768px to single column
- [ ] Only `transform`/`opacity` animated
- [ ] Overall impression: "$150k agency build"
