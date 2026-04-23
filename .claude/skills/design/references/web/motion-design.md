# Motion Design (Web)

Hub for web motion design. Core rules live here; designer perspectives, audit workflow, and deep dives live in [`motion/`](motion/).

For iOS, see [`../ios/motion.md`](../ios/motion.md).

---

## Philosophy Entry Point

Before tuning durations and easing, decide IF and HOW to animate.

### The Frequency Rule (Emil Kowalski)

Animation appropriateness depends on interaction frequency:

| Frequency | Recommendation |
|-----------|----------------|
| Rare (monthly) | Delightful, morphing animations welcome |
| Occasional (daily) | Subtle, fast animations |
| Frequent (100s/day) | No animation or instant transitions |
| Keyboard-initiated | Never animate |

### The Golden Rule (Jakub Krehel)

> "The best animation is that which goes unnoticed."

If users comment "nice animation!" on every interaction, it's too prominent for production. Exception: kids apps and playful contexts where delight IS the goal.

### Context-to-Perspective Mapping

Three designer lenses; pick weighting based on project type. Deep philosophy in [`motion/emil-kowalski.md`](motion/emil-kowalski.md), [`motion/jakub-krehel.md`](motion/jakub-krehel.md), [`motion/jhey-tompkins.md`](motion/jhey-tompkins.md).

| Project Type | Primary | Secondary | Selective |
|--------------|---------|-----------|-----------|
| Productivity tool (Linear, Raycast) | Emil | Jakub | Jhey (onboarding) |
| Kids app / Educational | Jakub | Jhey | Emil (game interactions) |
| Creative portfolio | Jakub | Jhey | Emil (high-freq) |
| Marketing / landing | Jakub | Jhey | Emil (forms, nav) |
| SaaS dashboard | Emil | Jakub | Jhey (empty states) |
| Mobile app | Jakub | Emil | Jhey (delighters) |
| E-commerce | Jakub | Emil | Jhey (product showcase) |

**When `/design animate` runs**: propose weighting → confirm with user (via `AskUserQuestion`) → load 1-2 designer files → implement.

---

## Duration: The 100/300/500 Rule

Operational defaults for most UI (context-dependent per designer lens — see [`motion/`](motion/) for frequency-based framing):

| Duration | Use Case | Examples |
|----------|----------|----------|
| **100-150ms** | Instant feedback | Button press, toggle, color change |
| **200-300ms** | State changes | Menu open, tooltip, hover states |
| **300-500ms** | Layout changes | Accordion, modal, drawer |
| **500-800ms** | Entrance animations | Page load, hero reveals |

**Exit animations are faster than entrances** — use ~75% of enter duration.

**Emil's override**: for productivity tools, keep UI animations under 300ms. 180ms feels more responsive than 400ms.

---

## Easing: Pick the Right Curve

**Don't use `ease`.** It's a compromise that's rarely optimal. Instead:

| Curve | Use For | CSS |
|-------|---------|-----|
| **ease-out** | Elements entering | `cubic-bezier(0.16, 1, 0.3, 1)` |
| **ease-in** | Elements leaving | `cubic-bezier(0.7, 0, 0.84, 0)` |
| **ease-in-out** | State toggles (there → back) | `cubic-bezier(0.65, 0, 0.35, 1)` |

**For micro-interactions, use exponential curves** — they feel natural because they mimic real physics (friction, deceleration):

```css
/* Quart out - smooth, refined (recommended default) */
--ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);

/* Quint out - slightly more dramatic */
--ease-out-quint: cubic-bezier(0.22, 1, 0.36, 1);

/* Expo out - snappy, confident */
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
```

**Avoid bounce and elastic curves** in production UI. They were trendy in 2015 but now feel tacky and amateurish. Real objects decelerate smoothly rather than bouncing. Overshoot effects draw attention to the animation itself rather than the content.

**Exception**: kids apps and playful brand contexts where energy is part of the identity. See [`motion/jhey-tompkins.md`](motion/jhey-tompkins.md) for `linear()` syntax that unlocks bounce/elastic in pure CSS.

Never use `ease-in` for UI animations — it starts slow, making the interface feel sluggish.

### Custom curves for iOS-feel drawers

```css
/* Strong ease-out for UI interactions */
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);

/* Strong ease-in-out for on-screen movement */
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);

/* iOS-like drawer curve (from Vaul) */
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
```

---

## The Only Two Properties You Should Animate

**transform** and **opacity** only — everything else causes layout recalculation. For height animations (accordions), use `grid-template-rows: 0fr → 1fr` instead of animating `height` directly.

Deep dive (including `will-change` usage, GPU layer budget, gradient animation performance): [`motion/performance.md`](motion/performance.md).

---

## Spring Animations

Springs feel more natural than duration-based animations because they simulate real physics. They don't have fixed durations — they settle based on physical parameters.

### When to use springs
- Drag interactions with momentum
- Elements that should feel "alive" (like Apple's Dynamic Island)
- Gestures that can be interrupted mid-animation
- Decorative mouse-tracking interactions

### Spring configuration

**Apple's approach (recommended — easier to reason about):**
```js
{ type: "spring", duration: 0.5, bounce: 0.2 }
```

**Traditional physics (more control):**
```js
{ type: "spring", mass: 1, stiffness: 100, damping: 10 }
```

Keep bounce subtle (0.1-0.3). Avoid bounce in most UI contexts. Use for drag-to-dismiss and playful interactions.

### Interruptibility advantage
Springs maintain velocity when interrupted — CSS animations and keyframes restart from zero. This makes springs ideal for gestures users might change mid-motion.

Deep dive (spring physics parameters, mouse-position springs, Sonner/Vaul patterns): [`motion/emil-kowalski.md`](motion/emil-kowalski.md).

---

## Staggered Animations

Use CSS custom properties for cleaner stagger: `animation-delay: calc(var(--i, 0) * 50ms)` with `style="--i: 0"` on each item.

**Cap total stagger time** — 10 items at 50ms = 500ms total. For many items, reduce per-item delay or cap staggered count.

For "already-in-progress" effects (negative delays), `@property` typed animation, and 3D stagger techniques, see [`motion/jhey-tompkins.md`](motion/jhey-tompkins.md).

---

## Reduced Motion

This is not optional. Vestibular disorders affect ~35% of adults over 40.

```css
/* Provide alternative for reduced motion */
@media (prefers-reduced-motion: reduce) {
  .card {
    animation: fade-in 200ms ease-out;  /* Crossfade instead of motion */
  }
}

/* Or disable entirely */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

**What to preserve**: Functional animations like progress bars, loading spinners (slowed down), and focus indicators should still work — just without spatial movement.

Deep dive (functional vs decorative motion, vestibular trigger patterns, JS detection): [`motion/accessibility.md`](motion/accessibility.md).

---

## Perceived Performance

**Nobody cares how fast your site is — just how fast it feels.** Perception can be as effective as actual performance.

**The 80ms threshold**: Our brains buffer sensory input for ~80ms to synchronize perception. Anything under 80ms feels instant and simultaneous. This is your target for micro-interactions.

**Active vs passive time**: Passive waiting (staring at a spinner) feels longer than active engagement. Strategies to shift the balance:

- **Preemptive start**: Begin transitions immediately while loading (iOS app zoom, skeleton UI). Users perceive work happening.
- **Early completion**: Show content progressively — don't wait for everything. Video buffering, progressive images, streaming HTML.
- **Optimistic UI**: Update the interface immediately, handle failures gracefully. Instagram likes work offline — the UI updates instantly, syncs later. Use for low-stakes actions; avoid for payments or destructive operations.

**Easing affects perceived duration**: Ease-in (accelerating toward completion) makes tasks feel shorter because the peak-end effect weights final moments heavily. Ease-out feels satisfying for entrances, but ease-in toward a task's end compresses perceived time.

**Caution**: Too-fast responses can decrease perceived value. Users may distrust instant results for complex operations (search, analysis). Sometimes a brief delay signals "real work" is happening.

---

## Asymmetric Enter/Exit Timing

Pressing should be slow when deliberate (hold-to-delete: 2s linear), but release should always be snappy (200ms ease-out). Slow where the user decides, fast where the system responds.

Enter/exit animation recipes (opacity + translateY + blur combos, FLIP via `layoutId`): [`motion/technical-principles.md`](motion/technical-principles.md).

---

## The Sonner Principles

From building Sonner (13M+ weekly npm downloads):

1. **Good defaults matter more than options.** Ship beautiful out of the box.
2. **Use transitions, not keyframes, for dynamic UI.** Toasts are added rapidly; keyframes restart from zero on interruption. Transitions retarget smoothly.
3. **Handle edge cases invisibly.** Pause toast timers when tab is hidden. Fill gaps between stacked toasts with pseudo-elements. Users never notice — that's exactly right.
4. **Match motion to mood.** A playful component can be bouncier. A professional dashboard should be crisp and fast.

Full Sonner/Vaul implementation patterns (CSS transitions vs keyframes, direct style updates, pointer capture, momentum-based dismissal): [`motion/emil-kowalski.md`](motion/emil-kowalski.md).

---

## CSS Performance Notes

- CSS animations run off the main thread; Framer Motion uses `requestAnimationFrame` on the main thread
- Framer Motion shorthand props (`x`, `y`, `scale`) are NOT hardware-accelerated — use full `transform` string
- CSS variables are inheritable: changing one on a parent recalculates all children. Update `transform` directly instead
- Use Web Animations API (WAAPI) for programmatic CSS-performance animations

Don't use `will-change` preemptively — only when animation is imminent (`:hover`, `.animating`). For scroll-triggered animations, use Intersection Observer instead of scroll events; unobserve after animating once. Create motion tokens for consistency (durations, easings, common transitions).

**Avoid**: Animating everything (animation fatigue is real). Using >500ms for UI feedback. Ignoring `prefers-reduced-motion`. Using animation to hide slow loading.

---

## When to Load Deeper References

| Need | File |
|------|------|
| Reconnaissance + designer weighting proposal | [`motion/README.md`](motion/README.md) |
| Emil's philosophy (restraint, Sonner/Vaul, clip-path) | [`motion/emil-kowalski.md`](motion/emil-kowalski.md) |
| Jakub's techniques (enter/exit, shadows, optical alignment, FLIP) | [`motion/jakub-krehel.md`](motion/jakub-krehel.md) |
| Jhey's experiments (`@property`, `linear()`, 3D CSS, scroll-driven) | [`motion/jhey-tompkins.md`](motion/jhey-tompkins.md) |
| Reviewing existing code (systematic checklist) | [`motion/audit-checklist.md`](motion/audit-checklist.md) |
| Finding missing animations (grep patterns) | [`motion/motion-gaps.md`](motion/motion-gaps.md) |
| Enter/exit recipes, easing, clip-path, springs | [`motion/technical-principles.md`](motion/technical-principles.md) |
| Anti-patterns deep dive (per-designer + general) | [`motion/common-mistakes.md`](motion/common-mistakes.md) |
| `will-change`, GPU layers, gradient perf | [`motion/performance.md`](motion/performance.md) |
| Full accessibility (vestibular, functional vs decorative) | [`motion/accessibility.md`](motion/accessibility.md) |
| Audit report template | [`motion/output-format.md`](motion/output-format.md) |

---

## Command Integration

- **`/design animate`** (web) — starts here, proposes designer weighting, loads relevant `motion/*` file(s), implements using [`motion/technical-principles.md`](motion/technical-principles.md), closes with [`motion/accessibility.md`](motion/accessibility.md) check
- **`/design audit`** (web) — Motion Gap Analysis via [`motion/motion-gaps.md`](motion/motion-gaps.md) + systematic review via [`motion/audit-checklist.md`](motion/audit-checklist.md) + report via [`motion/output-format.md`](motion/output-format.md)
- **`/design polish`** (web) — anti-pattern scan via [`motion/common-mistakes.md`](motion/common-mistakes.md)
