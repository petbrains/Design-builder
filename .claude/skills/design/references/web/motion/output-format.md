# Audit Report Output Format

Template for the motion section of a `/design audit` report. Structure with visual hierarchy for easy scanning. Do not summarize — users want full per-designer perspectives.

---

## Quick Summary (Show First)

Start every motion audit with a summary box:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MOTION AUDIT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical: [X]  |  Important: [X]  |  Opportunities: [X]
Motion gaps: [X] conditional renders without AnimatePresence
Primary perspective: [Designer(s)] ([context reason])
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Overall Assessment

One paragraph: Does the motion design feel polished? Too much? Too little? What's working, what's not? Reference the confirmed designer weighting.

---

## Per-Designer Sections

Use decorated headers and grouped findings for each designer in the weighting.

### Emil's Section

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EMIL'S PERSPECTIVE — Restraint & Speed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

*Weight based on context. Heavy for productivity tools, light for creative/kids apps.*

**What to Check:**
- High-frequency interactions that might not need animation
- Keyboard-initiated actions that animate (generally shouldn't)
- Durations **if this is a productivity context** (Emil prefers under 300ms)
- Animations starting from `scale(0)` (should be 0.9+)
- Transform-origin on dropdowns/popovers
- CSS keyframes that should be transitions (for interruptibility)

**Body format:**

**What's Working Well**
- [Observation] — `file.tsx:line`

**Issues to Address**
- [Issue] — `file.tsx:line`
  [Brief explanation]

**Emil would say**: [1-2 sentence summary]

---

### Jakub's Section

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JAKUB'S PERSPECTIVE — Production Polish
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What to Check:**
- Enter animations (opacity + translateY + blur?)
- Exit animations (subtler than enters? Or missing entirely?)
- **Motion gaps** — conditional renders without AnimatePresence (from gap analysis)
- **Layout transitions** — size/position changes that snap instead of animate
- Shadow vs border usage on varied backgrounds
- Optical alignment (buttons with icons, play buttons)
- Hover state transitions (150-200ms minimum)
- Icon swap animations (opacity + scale + blur)
- Spring usage (`bounce: 0` for professional, higher for playful)

**Body format:**

**What's Working Well**
- [Observation] — `file.tsx:line`

**Issues to Address**
- [Issue] — `file.tsx:line`
  [Brief explanation]

**Jakub would say**: [1-2 sentence summary]

---

### Jhey's Section

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JHEY'S PERSPECTIVE — Experimentation & Delight
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What to Check:**
- Could `@property` enable smoother animations?
- Could `linear()` provide better easing curves?
- Are stagger effects using optimal techniques?
- Could scroll-driven animations improve the experience?
- What playful touches would enhance engagement?
- Are there celebration moments that need more delight? (streaks, achievements, etc.)

**Body format:**

**What's Working Well**
- [Observation] — `file.tsx:line`

**Opportunities**
- [Idea] — `file.tsx:line`
  [Brief explanation]

**Jhey would say**: [1-2 sentence summary]

---

## Combined Recommendations

Use severity indicators for quick scanning:

**Critical (Must Fix)**

| Issue | File | Action |
|-------|------|--------|
| [Issue] | `file:line` | [Fix] |

**Important (Should Fix)**

| Issue | File | Action |
|-------|------|--------|
| [Issue] | `file:line` | [Fix] |

**Opportunities (Could Enhance)**

| Enhancement | Where | Impact |
|-------------|-------|--------|
| [Enhancement] | `file:line` | [Impact] |

---

## Motion Gaps Table

List findings from [`motion-gaps.md`](motion-gaps.md) workflow:

| File | Line | Pattern | Recommendation |
|------|------|---------|----------------|
| `src/components/Modal.tsx` | 42 | `{isOpen && <Modal />}` | Wrap in AnimatePresence |
| `src/pages/Settings.tsx` | 87 | Mode switch without transition | Use `mode="wait"` AnimatePresence |

---

## Designer Reference Summary

End every motion audit with:

> **Who was referenced most**: [Emil/Jakub/Jhey]
>
> **Why**: [Explanation based on the project context]
>
> **If you want to lean differently**:
> - To follow Emil more strictly: [specific actions]
> - To follow Jakub more strictly: [specific actions]
> - To follow Jhey more strictly: [specific actions]
