# Redesign Workflow

Upgrade existing websites and apps to premium quality. Audit, diagnose, and fix without breaking functionality.

## Process

1. **Scan** — Read the codebase. Identify framework, styling method, current design patterns.
2. **Diagnose** — Run through the audit below. List every generic pattern, weak point, missing state.
3. **Fix** — Apply targeted upgrades with the existing stack. Do not rewrite from scratch.

## Design Audit Checklist

### Typography
- Browser default fonts or Inter everywhere → replace with character fonts
- Headlines lack presence → increase size, tighten letter-spacing, reduce line-height
- Body text too wide → limit to ~65ch, increase line-height
- Only Regular/Bold weights → introduce Medium (500), SemiBold (600)
- Numbers in proportional font → use monospace or `font-variant-numeric: tabular-nums`
- Orphaned words → fix with `text-wrap: balance` or `text-wrap: pretty`

### Color & Surfaces
- Pure `#000000` background → off-black (`#0a0a0a`, `#121212`, tinted dark)
- Oversaturated accents → saturation < 80%
- More than one accent color → pick one, remove rest
- Mixing warm and cool grays → stick to one family
- Purple/blue "AI gradient" → neutral bases + single accent
- Generic `box-shadow` → tint shadows to match background hue
- Random dark section in light page → consistent tone or full dark mode
- Empty flat sections → add imagery, patterns, ambient gradients

### Layout
- Everything centered → break symmetry with offsets, mixed ratios
- Three equal card columns → 2-column zig-zag, asymmetric grid, horizontal scroll
- `height: 100vh` → `min-height: 100dvh`
- Complex flexbox math → CSS Grid
- No max-width container → add 1200-1440px constraint
- No overlap or depth → negative margins for layering
- Missing whitespace → double the spacing
- Buttons not bottom-aligned in card groups → pin to bottom

### Interactivity & States
- No hover states → add background shift, scale, or translate
- No active/pressed feedback → `scale(0.98)` or `translateY(1px)`
- No transitions → 200-300ms on all interactive elements
- Missing focus ring → visible focus indicators (accessibility requirement)
- No loading states → skeleton loaders matching layout
- No empty states → composed "getting started" view
- No error states → clear inline error messages

### Content
- Generic names → diverse, realistic names
- Fake round numbers → organic data
- AI copywriting clichés → plain, specific language
- Lorem Ipsum → real draft copy

### Component Patterns
- Generic card (border + shadow + white bg) → simplify or remove
- Pill-shaped badges everywhere → vary formats
- Accordion FAQ → side-by-side list, searchable help
- 3-card carousel testimonials → masonry wall, embedded posts
- Modals for everything → inline editing, slide-over panels

## Fix Priority Order

Apply in this order for maximum impact, minimum risk:

1. **Font swap** — biggest instant improvement
2. **Color palette cleanup** — remove clashing/oversaturated
3. **Hover and active states** — makes interface feel alive
4. **Layout and spacing** — proper grid, max-width, consistent padding
5. **Replace generic components** — swap clichés for modern alternatives
6. **Add loading/empty/error states** — makes it feel finished
7. **Polish typography scale** — the premium final touch

## Upgrade Techniques

### Typography
- Variable font animation (weight/width on scroll/hover)
- Outlined-to-fill text transitions on scroll entry
- Text mask reveals (typography as window to video/image)

### Layout
- Broken grid / asymmetry — deliberate column structure ignoring
- Whitespace maximization — force focus on single element
- Parallax card stacks — sticky sections stacking on scroll

### Motion
- Staggered entry — cascade with slight delays
- Spring physics — replace linear easing
- Scroll-driven reveals — expanding masks, wipes, SVG paths

### Surfaces
- True glassmorphism (1px inner border + inner shadow + blur)
- Spotlight borders (dynamic cursor illumination)
- Grain/noise overlays (fixed, pointer-events-none)
- Colored/tinted shadows

## Rules

- Work with existing tech stack — no framework migration
- Do not break existing functionality — test after every change
- Check `package.json` before importing new libraries
- Check Tailwind version (v3 vs v4) before modifying config
- Keep changes reviewable and focused — small targeted improvements
