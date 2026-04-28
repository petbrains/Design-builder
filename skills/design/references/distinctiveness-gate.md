---
name: distinctiveness-gate
description: Layer-2 filter that runs BEFORE emit on creative steps (system / craft / intensity modifiers). Catches "could-have-come-out-of-ChatGPT-without-the-plugin" outputs that pass the Anti-Pattern checks but have no character. Hard mode for `system` (cheap to regenerate 3 candidates), soft mode for `craft` (expensive to regenerate full pages).
---

# Distinctiveness Gate

This is the filter the skill runs **before** showing creative output to the user. It is **not** a self-grade for the user — the model answers these questions itself, then routes the output based on the answers.

The Anti-Pattern filter catches *technical* AI-slop (3-column card rows, gradient text, side-stripe borders). This gate catches *character* AI-slop: outputs that are technically clean but indistinguishable from what someone would get from a generic LLM in 30 seconds without the plugin.

**Both filters must pass before emit.**

---

## When this runs

| Step | Mode | What "fail" means |
|---|---|---|
| `system` (3-variation generation) | **HARD** — regenerate without showing the user | The variant that fails is silently replaced with a fresh one. Three candidates are *cheap*. The user only ever sees variants that passed. |
| `/create` (page from `inspiration_pages`) | **HARD with 1 retry**, then SOFT | First failure: regenerate ONCE with different inputs (different reference from the top-3, dropped `style_family`, swapped `mood`, or an explicit risk pulled from the brief). Second failure: emit with a `Risks taken & gaps` block. Rationale: `/create` ships boring output otherwise — a single regenerate is cheap; re-fetching from MCP is not. |
| `craft` — refining user code (`/improve`) | **SOFT** — annotate, ask user to keep / refine / discard | Output is shown WITH a `Risks taken & gaps` block listing failed questions. User decides whether to invoke a bolder pass or accept. Regenerating the user's whole file unprompted is hostile. |
| Intensity modifiers (`bolder` / `quieter` / `distill` / `overdrive` / `delight`) | **SOFT** | Same as `craft`. |
| `polish` | **SKIP** | Polish is precision, not character. Don't regenerate for distinctiveness. |
| `audit` / `critique` / `review` | **SKIP** | These already include slop scoring; running this on top would double-count. |

---

## The 7 questions

Answer in order. **Do not paraphrase**. Each question requires a *concrete* answer — a noun, a number, a named element. Adjectives alone do not pass.

### Q1 · The one-line takeaway

*"If the user closed the preview right now and described it to a friend, what is the ONE concrete detail they would mention first?"*

- **Pass example:** "the 220px Playfair display with a terracotta dot anchored to the baseline of the italic tagline"
- **Pass example:** "the forest-green block that fills 60% of the hero, with the only saturated color on screen being the terracotta CTA"
- **Fail example:** "warm editorial vibe" / "premium feel" / "modern but not sterile"

If you cannot answer this in one sentence with one specific element, the output is **generic**. Fail.

### Q2 · The 30-second-without-context test

*"Take a no-context user (no brief, no audience, no anti-references). Ask any modern LLM 'design me a [SaaS / landing / app screen]'. Could the output you're about to emit plausibly be that LLM's response?"*

- **Pass:** "No — the [specific element] is a deliberate choice that requires the brief to land. Without the audience/tone/anti-reference, no LLM defaults to it."
- **Fail:** "Yes, probably" / "It's a clean editorial style, anyone could have made it"

### Q3 · The risk inventory

*"Name at least one decision that took the output *off* the safe path. What would a timid designer have done instead, and why is your choice better given the brief?"*

- **Pass:** "Hero copy is asymmetric — H1 spans 18ch, sits at top-left, the demo card breaks the right margin into the gutter. Timid version would center on a 12-column grid with equal padding. Brief said 'aimed at people who already abandoned 3 apps' — generic centering signals 'one more SaaS', off-grid signals 'this one is not like those'."
- **Fail:** "Used Playfair instead of Inter" (font choice alone is not a risk, it's a parameter). "Made it dark" (single attribute, not a structural decision).

### Q4 · The named reference, not the adjective

*"What specific designed thing (real product / publication / studio / book) is this output's spiritual neighbour? It must be a NAMED reference, not a category."*

- **Pass:** "Sits between Sweetgreen.com (the way they let big photographs and forest-green typography carry the brand) and the Are.na editorial layout."
- **Pass:** "Closer to Linear's marketing site than to Notion's — denser type, less whitespace, no gradient washes."
- **Fail:** "modern editorial websites" / "good SaaS landings" / "Apple-like clarity"

If the model cannot name a concrete reference, the design has no taste anchor.

### Q5 · The user's specific brief, applied

*"Find one element in the output that *only* exists because of something the user said in the brief. Quote the brief detail and point to the element it shaped."*

- **Pass:** "The brief said 'audience already burned out by 2-3 apps' → the comparison table is honest about Duolingo's strengths instead of trashing it. Most landings would be hostile to competitors; this one earns trust by acknowledging them."
- **Pass:** "Brief said 'tone with a bit of humour, no corporate-speak' → the H1 reads 'Netflix is fun. Duolingo is school. Kora is the cheat code.' instead of 'Master a new language with AI'."
- **Fail:** "Used the colors the user picked" — that's parameter-passing, not a brief-shaped decision.

### Q6 · Differentiation across the three (system step only)

*"Are A, B, C three genuinely different aesthetic directions, or three flavours of the same idea?"*

- **Pass:** "A is light/literary (cream paper, italic display), B is dark/confident (forest blocks, large CTA), C is publication-style (single column, no display divergence). Different layout grammars, not just different palettes."
- **Fail:** "A, B, C all use the same warm palette and serif headline, just with different accent intensities."

If the three variants share the same layout posture and the same type-pairing posture, you've shipped one variant in three skins. Fail and regenerate.

### Q7 · The "remove this and the design dies" element

*"Identify a single element such that removing it would collapse the design's identity. If you cannot, the design has no load-bearing distinctiveness."*

- **Pass:** "Remove the asymmetric hero (H1 + off-grid demo card) and it becomes a generic centered-hero SaaS. The asymmetry IS the brand here."
- **Pass:** "Remove the 60% forest block and the terracotta CTA loses its singular-saturated-element status — design becomes a normal cream landing with terra accents."
- **Fail:** "Remove the heading and there's no heading" — every design needs a heading; that's not load-bearing distinctiveness.

---

## How the model uses this

### Hard mode (`system` / 3 variations)

1. Generate variant.
2. Answer Q1, Q2, Q3, Q4, Q6, Q7 silently. (Q5 may be deferred to `craft` since `system` is brief-driven but not surface-specific.)
3. If any answer fails: **discard the variant, regenerate.** Do not show the user.
4. Repeat until all three variants pass.
5. Show the preview HTML. Tell the user: *"Three variants generated. The hooks below are the load-bearing detail of each — pick the one that aligns with the product."*

The user never sees the failed candidates. The 3-variation pick is supposed to be a real choice between three real directions, not three variations of the same default.

### Hard-with-1-retry (`/create`)

1. Generate the page from the picked `inspiration_pages` reference.
2. Answer Q1, Q2, Q4, Q5, Q7 silently. (Q3 and Q6 are not load-bearing here — Q3 is captured by the user's brief context, Q6 only applies to multi-variant generation.)
3. **First failure:** discard the candidate and regenerate ONCE. On regenerate, change at least one input — different reference from the deep-fetched top-3, drop `style_family`, swap `mood`, or layer in an explicit named precedent or anti-reference from the brief.
4. **Second failure:** emit with a `Risks taken & gaps` block (same shape as soft mode below). Tell the user which question failed and recommend a concrete next move (`/design-builder:improve` with bolder filters, or `/create` again with different filters).

The point: `/create` runs once per request and writes real source files. SOFT-only allowed boring output to ship; HARD-with-no-retry would be too expensive (re-fetching MCP, re-walking sections). One retry is the right tax.

### Soft mode (`craft` / intensity modifiers)

1. Generate output (page / component / refined surface).
2. Answer all 7 questions.
3. Emit the output AS-IS, but also append a `Risks taken & gaps` block to the response:

```
Risks taken & gaps
──────────────────
✓ Q1 takeaway:   220px Playfair + terra dot under italic tagline
✓ Q2 30s test:   structural asymmetry + comparison-table honesty wouldn't survive a generic prompt
✓ Q3 risk:       hero is off-grid; user can dial back via `/design quieter`
✗ Q4 reference:  could not anchor to a named precedent — output may be too generic on this axis
✓ Q5 brief tie:  comparison table reflects "user burned out by 3 apps"
✓ Q7 load-bearing: asymmetric hero is the spine
```

The user sees what risks were taken and what gaps remain. They can keep, refine, or discard.

### Don't pretend

If the model answers a question with adjectives because nothing concrete was actually decided, **the output is generic** — that's the point of the gate. Do not fake-pass by inventing references after the fact. Either go back and make a real choice, or admit the gap and let the user decide.

---

## Why this exists

The Anti-Pattern filter (BAN 1–4 in `SKILL.md`) catches CSS-level slop. It will not catch a perfectly-coded landing that happens to look like every other "premium editorial SaaS" generated this year. That output is **technically clean and creatively forgettable**.

This gate is the second pass: it asks the model to point at *something specific* the user would remember, *something risky* the model chose, *some named precedent* the design lives next to. If none of those exist, the output earned its slot in the pile of generic AI design.

The fix is almost always either:
- regenerate (cheap, in `system`), or
- bolt on a real risk via `/design bolder` / `/design overdrive` (in `craft`),

not "polish what's already there." Polish doesn't add character.
