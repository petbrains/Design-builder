# Motion Accessibility

**This is not optional.** Motion can cause discomfort, nausea, or distraction for many users. Vestibular disorders affect roughly 35% of adults over 40.

---

## Respect User Preferences

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

**What this does**: Effectively disables animations while preserving final states (so layouts don't break).

### Per-Component Alternative (Preferred)

Blanket overrides can break functional motion. Provide crossfades instead of motion for critical elements:

```css
.card {
  animation: slide-up 500ms ease-out;
}

@media (prefers-reduced-motion: reduce) {
  .card {
    animation: fade-in 200ms ease-out;  /* Crossfade instead of spatial motion */
  }
}
```

---

## Functional vs. Decorative Motion

| Type | Purpose | Reduced Motion Behavior |
|------|---------|------------------------|
| **Functional** | Indicates state changes, spatial relationships, orientation | May need alternative (instant state change, no transition) |
| **Decorative** | Pure delight, visual interest | Can be fully removed |

**The test**: Does removing this animation break the user's ability to understand what happened? If yes, it's functional.

### What to Preserve Under Reduced Motion

Even with motion disabled, these should still work (but without spatial movement):
- Progress bars (show progress, but don't bounce)
- Loading spinners (slow them down, or replace with a static "Loading…" indicator)
- Focus indicators (keep the visual state change, drop the transition)
- Skeleton loaders (keep the shimmer subtle or replace with static gray blocks)
- State changes (show old → new, but without animated interpolation)

### What to Remove Under Reduced Motion

- Parallax scrolling (strong vestibular trigger)
- Large-scale zoom / scale animations
- Full-screen page transitions
- Decorative ambient animations (floating shapes, pulsing gradients, etc.)
- Auto-rotating carousels (also remove the auto-rotation, not just the transition)

---

## Motion Sensitivity Considerations

- Avoid large-scale motion (full-screen transitions, parallax)
- Avoid continuous or looping animations that can't be paused
- Provide pause controls for any ambient animation
- Be especially careful with vestibular triggers: zooming, spinning, parallax, perspective shifts

### Vestibular Trigger Patterns

High-risk patterns that deserve extra caution:
- **Parallax scrolling** — different depths moving at different speeds
- **Full-viewport zoom** — entire screen scaling in or out
- **3D rotations** — perspective transforms, flipping cards
- **Scroll-driven animations** that move large elements across the viewport
- **Dramatic spring oscillations** — high bounce values on large elements

For these, an explicit `prefers-reduced-motion` check is mandatory — blanket `transition-duration: 0.01ms` is not enough because the animations may still trigger mid-flight.

---

## Implementation Checklist

- [ ] Tested with `prefers-reduced-motion: reduce` enabled (DevTools → Rendering → Emulate CSS media)
- [ ] No vestibular triggers (excessive zoom, spin, parallax) without reduced-motion alternative
- [ ] Looping animations can be paused
- [ ] Functional animations have non-motion alternatives (crossfade, instant state change)
- [ ] Users can complete all tasks with animations disabled
- [ ] Parallax and scroll-driven effects explicitly disabled under reduced-motion
- [ ] Auto-rotating carousels: auto-rotation disabled under reduced-motion (not just transitions)

---

## JavaScript Detection

When you need to conditionally skip JS-driven motion:

```javascript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (!prefersReducedMotion) {
  // Start ambient animation
}

// Framer Motion: use useReducedMotion hook
import { useReducedMotion } from "motion/react";

const shouldReduceMotion = useReducedMotion();
const animationProps = shouldReduceMotion
  ? { opacity: 1 }
  : { opacity: 1, y: 0, scale: 1 };
```

---

## Related

- [`../motion-design.md`](../motion-design.md) — Short-form reduced-motion rule in the hub
- Web spatial design → safe-area patterns for motion that respects viewport
- iOS: see [`../../ios/accessibility.md`](../../ios/accessibility.md) for Reduce Motion / Reduce Transparency / Increase Contrast
