# Motion — Designer Perspectives & Audit Toolkit

Deep motion references for web. Entry point is [`../motion-design.md`](../motion-design.md) — the hub with core rules and routing. This folder covers the philosophy/audit layer.

**Scope:** web only (framer-motion, CSS `@property`, `linear()`, scroll-driven). For iOS motion see [`../../ios/motion.md`](../../ios/motion.md).

---

## The Three Perspectives

| Designer | Philosophy | Best For |
|----------|-----------|----------|
| **Emil Kowalski** | Restraint & speed | Productivity tools, high-frequency interactions |
| **Jakub Krehel** | Production polish | Shipped consumer apps, professional refinement |
| **Jhey Tompkins** | Playful experimentation | Kids apps, portfolios, creative contexts |

These are **context-dependent lenses, not universal rules**. A kids' app prioritizes Jakub + Jhey (polish + delight), not Emil's productivity-focused speed rules.

### Context-to-Perspective Mapping

| Project Type | Primary | Secondary | Selective |
|--------------|---------|-----------|-----------|
| Productivity tool (Linear, Raycast) | Emil | Jakub | Jhey (onboarding) |
| Kids app / Educational | Jakub | Jhey | Emil (game interactions) |
| Creative portfolio | Jakub | Jhey | Emil (high-freq) |
| Marketing / landing | Jakub | Jhey | Emil (forms, nav) |
| SaaS dashboard | Emil | Jakub | Jhey (empty states) |
| Mobile app | Jakub | Emil | Jhey (delighters) |
| E-commerce | Jakub | Emil | Jhey (product showcase) |

### When to Use Each

| Emil | Jakub | Jhey |
|------|-------|------|
| "Should this animate?" | "Is this subtle enough?" | "What could this become?" |
| Frequency-based decisions | Blur + opacity + translateY | CSS custom properties |
| High-frequency tools | Production polish | Learning & exploration |

**Synthesis**: Use Emil's framework to decide IF you should animate. Use Jakub's techniques for HOW to animate in production. Use Jhey's approach for learning and experimentation.

---

## File Index

**Designer philosophies:**
- [`emil-kowalski.md`](emil-kowalski.md) — Restraint, frequency rule, Sonner/Vaul patterns, clip-path mastery
- [`jakub-krehel.md`](jakub-krehel.md) — Enter/exit recipes, shadows vs borders, optical alignment, shared layout
- [`jhey-tompkins.md`](jhey-tompkins.md) — `@property`, `linear()`, scroll-driven, 3D CSS, playful experimentation

**Audit workflow:**
- [`audit-checklist.md`](audit-checklist.md) — Systematic review guide for existing motion
- [`motion-gaps.md`](motion-gaps.md) — Finding *missing* animations (conditional renders without AnimatePresence)
- [`output-format.md`](output-format.md) — Audit report template with per-designer sections

**Topical deep-dives:**
- [`technical-principles.md`](technical-principles.md) — Enter/exit, easing, clip-path, springs, `@property`, scroll-driven
- [`common-mistakes.md`](common-mistakes.md) — Anti-patterns per designer + general motion mistakes
- [`performance.md`](performance.md) — `will-change`, GPU layers, gradient animation, properties-to-avoid
- [`accessibility.md`](accessibility.md) — `prefers-reduced-motion`, functional vs decorative, vestibular safety

---

## How Commands Use This

**`/design animate` (web)**
1. Reconnaissance → propose weighting (Primary/Secondary/Selective)
2. Confirm with user via `AskUserQuestion`
3. Load 1-2 designer files based on weighting
4. Implement using recipes from [`technical-principles.md`](technical-principles.md)
5. Mandatory [`accessibility.md`](accessibility.md) check before finishing

**`/design audit` (web)**
1. Load [`audit-checklist.md`](audit-checklist.md) as systematic guide
2. Run Motion Gap Analysis per [`motion-gaps.md`](motion-gaps.md)
3. Review existing animations against [`common-mistakes.md`](common-mistakes.md)
4. Emit motion section using [`output-format.md`](output-format.md) template

**`/design polish` (web)**
- Flag anti-patterns from [`common-mistakes.md`](common-mistakes.md): `scale(0)`, bounce easing, layout-property animation, missing reduced-motion.

---

## Core Cross-Cutting Principles

### The Golden Rule (Jakub)
> "The best animation is that which goes unnoticed."

If users comment "nice animation!" on every interaction, it's too prominent for production. Exception: kids apps and playful contexts where delight IS the goal.

### The Frequency Rule (Emil)
Animation appropriateness depends on interaction frequency:

| Frequency | Recommendation |
|-----------|----------------|
| Rare (monthly) | Delightful, morphing animations welcome |
| Occasional (daily) | Subtle, fast animations |
| Frequent (100s/day) | No animation or instant transitions |
| Keyboard-initiated | Never animate |

### Accessibility is Not Optional
Always honor `prefers-reduced-motion`. No exceptions. See [`accessibility.md`](accessibility.md).
