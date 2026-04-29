# style-guide.md template

This template defines the structure of `design/style-guide.md`. `/setup` Phase 5b consults this file when writing the style guide for a project. The output is **personalized** to the chosen direction — every value here is derived from interview answers, the chosen palette, and the project's stack target. Nothing in this file is copied verbatim; it is a slot-and-rule template.

## File header

```
# Style Guide — <Project Name>
generated: <YYYY-MM-DD>
direction: <chosen direction name from design-system.md>
```

## Section 1 — `## Accessibility floor`

Source: interview Q7 (hard constraints). Default: `WCAG AA` if not specified.

Body:
- One-line declaration: `Floor: WCAG AA` (or AAA).
- Required ratios (table; values are WCAG-defined):
  - Body text (< 18pt regular, < 14pt bold): **4.5:1** (or **7:1** for AAA)
  - Large text (≥ 18pt regular, ≥ 14pt bold): **3:1** (or **4.5:1** for AAA)
  - UI components (icon outlines, focus rings, input borders): **3:1**
  - Decorative elements: no minimum
- **Computed contrast table** (this is the personalized part):
  - For every (palette role × ink token) combination — the role × ink products from `design-system.md ## Palette`.
  - Compute ratio via `python skills/design/scripts/compute_contrast.py` (one Bash call, JSON pairs in, JSON results out).
  - Render as a markdown table: `| Pair | Ratio | Threshold | Pass |`.
  - Mark failing pairs with `❌` and add a row note: `consider <ink-muted-strong> for small text on this surface`.
- Focus indicators rule: `visible at 3:1 against background, min 2px outline (or platform-equivalent — iOS: native focus ring; web: outline-color from --ring token)`.
- Motion preference: `respect prefers-reduced-motion (mandatory)`.

## Section 2 — `## Touch targets`

Source: stack target from `design-system.md ## Stack`.

- Web (mobile breakpoint): `44 × 44 CSS px minimum, 8px gap between adjacent targets`.
- iOS: `44 × 44 pt minimum (HIG)`.
- Android (only if cross-platform): `48 × 48 dp minimum`.
- Desktop hover-able: `24 × 24 px minimum`.

Add a note: `Touch targets apply to anything tappable: buttons, icons, links inside dense lists, custom checkboxes, segmented controls.`

## Section 3 — `## Platform constraints`

Source: stack target. Render only the relevant blocks.

**Web block:**
- Safe areas: sticky header height (default `64px`, override if direction signals taller header), mobile bottom nav (default `56px` if app-style, otherwise none).
- Breakpoints: list the system's chosen breakpoints (default `640 / 768 / 1024 / 1280 / 1536` Tailwind defaults — pull from `tokens.css` if customized).
- Browser support floor: `evergreen Chromium / Firefox / Safari latest 2 versions` (default; override if interview Q7 specified IE11 or older).

**iOS block:**
- Safe area insets: respect top (status bar + navigation bar) and bottom (home indicator).
- Dynamic Island clearance: leave `≥ 8pt` gap below the island region for top-aligned content on supported devices.
- Status bar height varies; rely on `safeAreaInsets`, never hardcode.
- Keyboard avoidance: views containing inputs use `.keyboardAvoiding()` / `KeyboardAvoidanceView` patterns.

**Cross-platform:** render both blocks.

## Section 4 — `## Density & spacing rules`

Source: DENSITY dial value from `.cache/interview.json` (range 1-10).

- Render the dial value as one line: `DENSITY dial: <X> / 10`.
- Derived section padding (vertical):
  - dial 1-3 (loose): `padding-y: 96-128px desktop, 56-72px mobile`
  - dial 4-6 (balanced): `padding-y: 64-88px desktop, 40-56px mobile`
  - dial 7-10 (dense): `padding-y: 40-56px desktop, 24-32px mobile`
- Derived component internal padding:
  - dial 1-3: `padding: 24-32px (cards), 16-20px (buttons)`
  - dial 4-6: `padding: 16-24px (cards), 12-16px (buttons)`
  - dial 7-10: `padding: 12-16px (cards), 8-12px (buttons)`

## Section 5 — `## Motion rules`

Source: MOTION_INTENSITY dial value from `.cache/interview.json` (range 1-10).

- Render the dial value as one line: `MOTION_INTENSITY: <X> / 10`.
- Allowed durations (subset of full motion scale, gated by intensity):
  - dial 1-3: `120ms, 200ms only`
  - dial 4-6: `120ms, 200ms, 320ms`
  - dial 7-10: `120ms, 200ms, 320ms, 500ms, 800ms`
- Easing presets (always include all three):
  - `standard: cubic-bezier(0.4, 0.0, 0.2, 1)`
  - `decelerate: cubic-bezier(0.0, 0.0, 0.2, 1)`
  - `accelerate: cubic-bezier(0.4, 0.0, 1.0, 1.0)`
- prefers-reduced-motion fallback rules:
  - Disable hero/background motion entirely.
  - Replace transform-based transitions with opacity-only or no transition.
  - Static gradient or single still image substitutes for animated background.

## Section 6 — `## Anti-patterns to avoid`

Source: BAN 1-4 from `design-system.md ## Anti-pattern bans`. Expand each terse ban into 2-3 sentences of rationale here. Always include the four named bans plus any direction-specific bans surfaced by the chosen inspiration_pages' `not_recommended_for` field.

Format per ban:
```
### BAN <N> — <short label>
Rule: <one-line ban>
Why: <2-3 sentences on why this fails users / brand / a11y / convention>
What to do instead: <one-line replacement pattern>
```

## Section 7 — `## Component states required`

Static across all projects (constraint of having interactive UI):

```
Every interactive element MUST implement these states:

| State | Token source | Notes |
|---|---|---|
| default | --bg-default, --ink-default | resting |
| hover (web/desktop) | --bg-hover, --ink-default | mouse-over only; do not apply on touch |
| active (pressed) | --bg-active, --ink-default | momentary, releases on pointerup |
| focus-visible | --ring (3:1 against bg) | keyboard nav only; never on click |
| disabled | --bg-disabled, --ink-disabled | reduced opacity OR muted tokens, not both |
| loading | inherits default + spinner/skeleton overlay | disable pointer events |
```

Every state references **semantic tokens** from `tokens.css`. Hex literals are forbidden in component code.
