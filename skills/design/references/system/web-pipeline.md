---
name: design-system-web-pipeline
description: Web output pipeline for /design system. Emits CSS tokens, Tailwind config, shadcn theme, markdown spec.
---

# Web Pipeline

Consumes: style/palette/font_pair picked via `interview.md` + designlib MCP.
Emits: production-ready token files + spec markdown.

## Output bundle

Create all of the following in the project:

### 1. `tokens.css` — primitive + semantic CSS custom properties

```css
/* Primitive — raw values. Never use directly in components. */
:root {
  /* Color primitives in OKLCH. Each scale 50→950. */
  --neutral-50:  oklch(0.985 0.003 <hue>);
  --neutral-100: oklch(0.965 0.005 <hue>);
  /* ... through 950 */

  --accent-50:   oklch(...);
  /* ... */

  /* Type scale — fluid via clamp */
  --text-xs:    clamp(0.75rem, 0.72rem + 0.15vw, 0.8125rem);
  --text-sm:    clamp(0.875rem, 0.84rem + 0.175vw, 0.9375rem);
  --text-base:  clamp(1rem, 0.96rem + 0.2vw, 1.0625rem);
  --text-lg:    clamp(1.125rem, 1.075rem + 0.25vw, 1.1875rem);
  --text-xl:    clamp(1.25rem, 1.19rem + 0.3vw, 1.375rem);
  --text-2xl:   clamp(1.5rem, 1.42rem + 0.4vw, 1.75rem);
  --text-3xl:   clamp(1.875rem, 1.77rem + 0.53vw, 2.25rem);
  --text-4xl:   clamp(2.25rem, 2.12rem + 0.65vw, 2.75rem);
  --text-5xl:   clamp(3rem, 2.82rem + 0.9vw, 3.75rem);
  --text-6xl:   clamp(3.75rem, 3.5rem + 1.25vw, 4.75rem);

  /* Spacing — 4pt scale */
  --space-0: 0;
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-24: 6rem;

  /* Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;

  /* Motion */
  --ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
  --ease-out-quint: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-in-out:    cubic-bezier(0.65, 0, 0.35, 1);
  --dur-instant:    100ms;
  --dur-fast:       160ms;
  --dur-normal:     220ms;
  --dur-slow:       320ms;
}

/* Semantic — what components consume. Light theme */
:root {
  --color-background: var(--neutral-50);
  --color-surface:    var(--neutral-100);
  --color-border:     var(--neutral-200);
  --color-text:       var(--neutral-900);
  --color-text-muted: var(--neutral-600);
  --color-accent:     var(--accent-600);
  --color-accent-hover: var(--accent-700);
  /* ... */
}

/* Dark theme */
@media (prefers-color-scheme: dark) {
  :root {
    --color-background: var(--neutral-950);
    /* ... */
  }
}

/* Explicit toggle — for user preference override */
[data-theme='dark'] {
  --color-background: var(--neutral-950);
  /* ... */
}
```

Fill `<hue>` + concrete OKLCH values from designlib `get_palette` response.

### 2. `tailwind.config.*` OR `tailwind.css` (v4)

**Tailwind v4** (preferred — use `@theme`):

```css
@import "tailwindcss";

@theme {
  --color-background: var(--color-background);
  --color-surface:    var(--color-surface);
  --color-accent:     var(--color-accent);
  /* ... semantic mappings only */

  --font-display: "<heading font from designlib>", ui-serif, serif;
  --font-body:    "<body font from designlib>", ui-sans-serif, system-ui, sans-serif;
  --font-mono:    "<mono font from designlib>", ui-monospace, monospace;
}
```

**Tailwind v3**:

```js
export default {
  theme: {
    extend: {
      colors: {
        background: 'var(--color-background)',
        surface: 'var(--color-surface)',
        accent: 'var(--color-accent)',
      },
      fontFamily: {
        display: ['<heading>', 'ui-serif', 'serif'],
        body: ['<body>', 'ui-sans-serif', 'system-ui'],
      },
      transitionTimingFunction: {
        'out-quart': 'cubic-bezier(0.25, 1, 0.5, 1)',
      },
    },
  },
}
```

### 3. `theme.json` (if shadcn project)

Write to `components.json` colors section. Use semantic names.

### 4. Font loading

- Google Fonts → `<link rel="preload">` + `font-display: swap`
- Self-hosted → `@font-face` with `font-display: swap`, `unicode-range` for Latin-only subsetting
- Include `<body>` weight 400/500 + `<display>` weight 600/700 minimum

### 5. `design-system.md` — spec document

```markdown
# <Product> Design System — Web

**Generated:** <date>
**Source:** designlib style=<id> · palette=<id> · font_pair=<id>

## Tokens

- [`tokens.css`](./tokens.css) — primitive + semantic CSS variables
- [`tailwind.config.*`](./tailwind.config.ts) — Tailwind mapping

## Color

<palette role map + contrast ratios table>

## Typography

<font stack + type scale table + example renders>

## Space & Radius

<4pt scale + radius scale>

## Motion

<durations + easings + "when to animate" decision matrix>

## Dials

- DESIGN_VARIANCE: <n>
- MOTION_INTENSITY: <n>
- VISUAL_DENSITY: <n>

## Anti-patterns to avoid

<pull from SKILL.md — relevant subset for this aesthetic>
```

## Integration order

1. Write `tokens.css` first — it's the source of truth
2. Wire Tailwind config/theme to reference `tokens.css` vars
3. Update shadcn `components.json` if present
4. Add font loading to `_document.tsx` / `<head>` / `app/layout.tsx`
5. Write `design-system.md`
6. Verify by running `npm run dev` and inspecting a component in the browser

## Do NOT

- Hardcode hex values in components — always reference semantic tokens
- Create a third layer "component tokens" unless >3 components share overrides (YAGNI)
- Include the full primitive scale in Tailwind — only what's used semantically
- Add shadcn theme variables *and* Tailwind *and* tokens.css with diverging values — pick one source (tokens.css) and make others reference it
