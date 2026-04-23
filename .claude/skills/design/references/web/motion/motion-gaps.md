# Motion Gap Analysis

Finding UI changes that happen **without any transition** — conditional renders, ternary swaps, and dynamic styles that snap instead of animate. Run this BEFORE reviewing existing animations: missing motion is often worse than poorly-tuned motion.

---

## Why Motion Gaps Matter

Conditional UI changes without animation feel broken to modern users:
- Modals appear/disappear instantly → jarring, disorients the eye
- Mode switches snap content → loses spatial continuity
- Loading → content swaps without transition → feels unresponsive
- Expandable sections show/hide abruptly → users miss that something changed

The fix is usually simple: wrap in `AnimatePresence` or add a `transition` property. Finding them is the hard part.

---

## Search Patterns

### 1. Conditional renders without AnimatePresence

```bash
# Find: {condition && <Component />}
grep -rn "&&\s*<" --include="*.tsx" --include="*.jsx" .

# Find: {condition && (
grep -rn "&&\s*(" --include="*.tsx" --include="*.jsx" .
```

For each hit, check:
- Is it wrapped in `<AnimatePresence>`?
- Does the inner component have `initial`/`animate`/`exit` props?
- If NO to both → **motion gap**

### 2. Ternary UI swaps

```bash
# Find: {condition ? <A /> : <B />}
grep -rn "?\s*<" --include="*.tsx" --include="*.jsx" .
```

Ternary swaps need `<AnimatePresence mode="wait">` around them for smooth transitions between branches.

### 3. Dynamic inline styles without transition

```bash
# Find: style={{ prop: dynamicValue }}
grep -rn "style={{" --include="*.tsx" --include="*.jsx" .
```

For each hit, check:
- Does the element have a `transition` CSS property (inline or className)?
- If style props change on re-render and there's no transition → **motion gap**

### 4. CSS class toggles on dynamic state

```bash
# Find: className={isX ? 'a' : 'b'}
grep -rn "className={.*?.*:" --include="*.tsx" --include="*.jsx" .
```

If the two classes differ in properties that should animate (transform, opacity, colors) and neither has `transition` → **motion gap**.

---

## Common Motion Gap Patterns

### Modal / Drawer / Popover

```jsx
// GAP: Modal appears/disappears instantly
{isOpen && <Modal />}

// FIXED:
<AnimatePresence>
  {isOpen && (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
    >
      <Modal />
    </motion.div>
  )}
</AnimatePresence>
```

### Mode Switch / Tab Content

```jsx
// GAP: Controls swap without transition
{mode === "a" && <ControlsA />}
{mode === "b" && <ControlsB />}

// FIXED:
<AnimatePresence mode="wait">
  {mode === "a" && <motion.div key="a" ...><ControlsA /></motion.div>}
  {mode === "b" && <motion.div key="b" ...><ControlsB /></motion.div>}
</AnimatePresence>
```

### Loading → Content

```jsx
// GAP: Loading state snaps to content
{isLoading ? <Spinner /> : <Content />}

// FIXED: smooth crossfade
<AnimatePresence mode="wait">
  {isLoading
    ? <motion.div key="loading" ...><Spinner /></motion.div>
    : <motion.div key="content" ...><Content /></motion.div>}
</AnimatePresence>
```

### Expandable / Collapsible

```jsx
// GAP: Height changes without CSS transition
<div style={{ height: isExpanded ? 200 : 0 }}>

// FIXED: animate via grid-template-rows (layout-safe)
<div
  style={{
    display: 'grid',
    gridTemplateRows: isExpanded ? '1fr' : '0fr',
    transition: 'grid-template-rows 300ms cubic-bezier(0.16, 1, 0.3, 1)',
  }}
>
  <div style={{ overflow: 'hidden' }}>
    {content}
  </div>
</div>
```

### Toast / Notification

```jsx
// GAP: Toasts appear/disappear instantly
{toasts.map(t => <Toast key={t.id} {...t} />)}

// FIXED: Sonner, or hand-rolled AnimatePresence
<AnimatePresence>
  {toasts.map(t => (
    <motion.div
      key={t.id}
      initial={{ opacity: 0, y: 20, filter: 'blur(4px)' }}
      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      exit={{ opacity: 0, y: -8, filter: 'blur(4px)' }}
    >
      <Toast {...t} />
    </motion.div>
  ))}
</AnimatePresence>
```

### Error / Success States

```jsx
// GAP: Error message pops in without feedback
{error && <ErrorMessage>{error}</ErrorMessage>}

// FIXED:
<AnimatePresence>
  {error && (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
    >
      <ErrorMessage>{error}</ErrorMessage>
    </motion.div>
  )}
</AnimatePresence>
```

---

## Where Motion Gaps Hide

Walk through these areas in a codebase audit:

- **Inspector / settings panels** with mode switches or conditional controls
- **Conditional form fields** (show X when Y is checked)
- **Tab content areas** where the inner content changes on tab switch
- **Expandable / collapsible sections** (accordions, disclosure widgets, tree rows)
- **Toast / notification systems**
- **Loading states** (spinner → content, skeleton → content)
- **Error / success states** (form errors, success messages, validation)
- **Empty states** (list → empty-state illustration or vice versa)
- **Modals, drawers, popovers, tooltips** — if hand-rolled, likely missing exit animations
- **Autocomplete / combobox dropdowns** — mount/unmount patterns

---

## Audit Output

When reporting gaps, use this format (pairs with [`output-format.md`](output-format.md) template):

```
**Motion gaps found**: [N] conditional renders without AnimatePresence

| File | Line | Pattern | Recommendation |
|------|------|---------|----------------|
| src/components/Modal.tsx | 42 | `{isOpen && <Modal />}` | Wrap in AnimatePresence |
| src/pages/Settings.tsx | 87 | Mode switch without transition | Use `mode="wait"` AnimatePresence |
| src/hooks/useExpand.ts | 15 | `height` animated via style | Switch to `grid-template-rows` pattern |
```

---

## When NOT to Add Motion

Not every conditional render is a gap. Skip animation for:

- **Static conditional content** that renders once based on props (not user interaction)
- **Layout scaffolding** that swaps based on viewport (use CSS media queries, not motion)
- **Server-rendered variations** (SSR hydration mismatches with motion libraries)
- **Error boundaries** when rendering the fallback — users want to see the error immediately
- **Auth redirects** — instant transition is correct behavior

Use judgment: would motion here help the user understand what changed, or just slow them down?
