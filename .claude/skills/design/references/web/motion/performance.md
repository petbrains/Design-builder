# Motion Performance

Deep dive on `will-change`, GPU layers, gradient animation, and properties to avoid animating. Short-form rules live in [`../motion-design.md`](../motion-design.md) — this file covers the "why" and edge cases.

---

## will-change Explained

A hint to the browser: "I'm about to animate these properties, please prepare."

```css
/* Good — specific properties that will animate */
.animated-button {
  will-change: transform, opacity;
}

/* Bad — too broad, wastes resources */
* { will-change: auto; }
.element { will-change: all; }
```

**Properties that benefit from will-change**:
- `transform`
- `opacity`
- `filter` (blur, brightness)
- `clip-path`
- `mask`

**Why it matters**: Without the hint, the browser promotes elements to GPU layers only when animation starts, causing first-frame stutter. With `will-change`, it pre-promotes during idle time.

**When NOT to use**:
- On elements that won't animate
- On too many elements (each GPU layer uses memory)
- As a "fix" for janky animations (find the real cause)

### When to add and remove

```javascript
// Add before animation starts
element.style.willChange = 'transform, opacity';

// Remove after animation ends
element.addEventListener('transitionend', () => {
  element.style.willChange = 'auto';
}, { once: true });
```

Leaving `will-change` on after animation completes keeps the GPU layer allocated, which wastes memory on long-lived elements.

---

## Gradient Animation Performance

**Cheap to animate (GPU-accelerated)**:
- `background-position`
- `background-size`
- `opacity`

**Expensive to animate**:
- Color stops (`background: linear-gradient(...)` where stop colors change)
- Adding/removing gradient layers
- Switching gradient types

**Tip**: Animate a pseudo-element overlay or use CSS variables that transition indirectly:

```css
.button {
  position: relative;
  background: linear-gradient(45deg, #blue, #purple);
}

.button::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, #purple, #pink);
  opacity: 0;
  transition: opacity 300ms ease;
}

.button:hover::before {
  opacity: 1;
}
```

This crossfades two fixed gradients instead of interpolating color stops.

---

## Animation Performance Budget

Rough guide:
- **0-3 elements** with `will-change`: fine
- **4-10 elements**: careful, test on low-end devices
- **10+ elements**: reconsider approach — use virtualization, stagger, or canvas/WebGL

Each GPU layer consumes memory (width × height × 4 bytes). A full-screen layer on a 1440p display is ~14MB. Ten of them is 140MB — enough to cause memory pressure on older devices.

---

## Properties to Avoid Animating

These trigger layout recalculation (expensive):
- `width`, `height`
- `top`, `left`, `right`, `bottom`
- `margin`, `padding`
- `font-size`

**Always prefer**:
- `transform: translate()` instead of `top`/`left`
- `transform: scale()` instead of `width`/`height`
- `opacity` for visibility changes

### Height animation exception

When you genuinely need to animate height (accordions, collapsibles), use `grid-template-rows` with `0fr → 1fr`:

```css
.collapsible {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 300ms cubic-bezier(0.16, 1, 0.3, 1);
}

.collapsible.expanded {
  grid-template-rows: 1fr;
}

.collapsible > * {
  overflow: hidden;
}
```

This gives native-feeling height animation without triggering layout recalc on every frame.

---

## Composite-Only Animations

The browser pipeline has three stages: **layout → paint → composite**. Animating `transform` and `opacity` skips the first two, running entirely on the GPU compositor thread. This is why they stay smooth even when the main thread is busy.

Test path: open DevTools → Performance panel → record a 5-second interaction → check the "Main" flame chart for layout/paint work during animation. Ideally: zero.

---

## Performance Checklist

- [ ] `will-change` used sparingly and specifically (not `*` or `all`)
- [ ] `will-change` removed after animation completes (via `transitionend` listener)
- [ ] Animations use `transform` / `opacity` (not layout properties)
- [ ] Tested on low-end devices (or DevTools CPU throttling × 4-6)
- [ ] No continuous animations without purpose
- [ ] GPU layer count is reasonable (< 10 animated elements at once)
- [ ] Gradient animations crossfade overlays, don't interpolate color stops
- [ ] Height animations use `grid-template-rows: 0fr → 1fr` pattern
- [ ] DevTools Performance: no layout/paint work during interaction animations

---

## Related

- [`emil-kowalski.md`](emil-kowalski.md) § Performance Principles — 60fps target, composite rendering
- [`jakub-krehel.md`](jakub-krehel.md) § will-change — original source of this content
- [`common-mistakes.md`](common-mistakes.md) — red flags in code review
