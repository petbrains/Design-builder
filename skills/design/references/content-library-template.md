# content-library.md template

This template defines the structure of `design/content-library.md`. `/setup` Phase 5c consults this file when writing the content library for a project. Voice & tone is **personalized** from the interview mood + brand voice (if collected); patterns below are largely static but their copy examples are rewritten in the project's voice.

Source references for content patterns:
- `references/ux-writing.md` — general UX writing rules
- `references/brand/voice-framework.md` — voice principle vocabulary
- `references/brand/messaging-framework.md` — tone guidance
- `references/ios/ui-writing.md` — iOS-specific copy rules (apply only when stack target includes iOS)

## File header

```
# Content Library — <Project Name>
generated: <YYYY-MM-DD>
voice anchor: <mood label from interview Q6 + brand voice phrase from Q7 if present>
```

## Section 1 — `## Voice & tone`

Source: interview Q6 (mood) + Q7 (brand voice if mentioned in hard constraints) + the chosen direction's mood label.

Generate **3-5 voice principles**, each as:
- Principle name (2-4 words, e.g. "direct, not corporate")
- One-sentence elaboration in the project's actual voice
- One **do** example (snippet of UI copy)
- One **don't** example (snippet that violates the principle)

Anchor every principle to a mood word from interview. Example mapping:
- mood `editorial` → principle `specific over generic`, `confident without flourish`
- mood `playful` → principle `warm, never cute`, `verbs over nouns`
- mood `clinical` → principle `precise, present tense`, `no hedging`
- mood `moody` → principle `restrained vocabulary`, `lowercase by default unless emphasis`

After the principles list, add a `### Anti-examples (project-wide)` block:
- 3-5 specific copy patterns to never use, drawn from the principles.
- Examples: `never "Oops!" in errors`, `no exclamation marks in form validation`, `no marketing-speak verbs in transactional copy`.

## Section 2 — `## UI states`

Static structure across projects; copy examples are rewritten in project voice.

### Empty state
- Structure: `[illustration or icon] → [headline] → [optional 1-2 sentence description] → [primary action button]`
- Headline rule: state what should happen, not what hasn't ("Add your first project" — not "No projects yet").
- Tone: per voice principles. Generate one example per voice principle (3-5 examples).

### Loading state
- Default: skeleton, not spinner. Skeleton mirrors the shape of the expected content (cards, rows, headers).
- Patterns: list, card grid, detail page, form. For each, describe the skeleton blocks (e.g. `list: 5 rows × [40px circle | 60% bar | 40% bar]`).
- Spinner is allowed only for: indeterminate operations < 500ms, or background ops the user initiated (file save, send).

### Error state
- Structure: `[what broke] → [why, if known] → [what to do]`
- Tone rules:
  - Specific failure (`Couldn't reach server` — not `Something went wrong`).
  - No blame on the user (`The link expired` — not `You used an old link`).
  - Always offer a next action (retry, refresh, contact support).
- Generate 3 example errors covering: network, validation, permission.

### Success state
- Inline confirmation > modal. Toast for transient ops, in-place update for persistent ones.
- Patterns:
  - Form submit → inline success message + reset form OR navigate.
  - Async save → toast (3s) + saved indicator persists until next change.
  - Batch operation complete → summary message ("12 items updated, 1 skipped — show details").

### Offline state
- Banner at top: `Offline — changes will sync when you reconnect.`
- What's allowed without network: drafting, reading cached content, queueing actions.
- What's blocked: real-time, sync-required actions; surface with disabled state + "needs internet" hint.

## Section 3 — `## Forms`

### Labels
- Placement: above input on mobile (always); allowed beside input on desktop forms (login, settings).
- Casing: sentence case. No colons.
- Required indicator: `*` after label OR `(required)` for clarity-critical forms (legal, account creation).
- Optional indicator: explicit `(optional)` only when user benefit is unclear.

### Placeholders
- Format hints only (e.g. `john@example.com`, `MM/DD/YYYY`).
- Never duplicate the label.
- Never use placeholder as the only label (a11y violation).

### Validation messages
- Trigger: on `blur`, never on every keystroke (except inline format helpers like password strength).
- Format: `<what's wrong> — <how to fix>`.
- Examples (rewrite in project voice):
  - Required: `<Field> is required.`
  - Min length: `Use at least <N> characters.`
  - Format: `Enter a valid <type> (e.g. <example>).`
  - Uniqueness: `That <thing> is already taken — try another.`

### Helper text
- Below input, above any validation message.
- Use only when the requirement isn't obvious from the label.
- One sentence max.

## Section 4 — `## Notifications`

### Toast
- Auto-dismiss: 3-5 seconds (5s if action included).
- Positioning: bottom-right desktop, top mobile (under safe area).
- Templates (per type, with tone notes):
  - `success`: action verb past tense (e.g. `Saved`, `Sent`, `Copied`). Optional 1-line detail.
  - `warning`: state condition + suggested action (e.g. `Connection slow — saving may take longer.`).
  - `error`: same format as Section 2 errors.
  - `info`: neutral statement, optional inline action link.

### Banner (persistent in-page)
- Use for: status that affects current view, persistent CTAs, system-wide notices.
- Structure: `[icon] [headline] [optional action button]`.
- Dismissable iff non-critical.

### Confirmation dialog
- Destructive:
  - Headline names the target explicitly (`Delete "<filename>"?`).
  - Body explains consequence (`This can't be undone.` — only if true).
  - Action verbs, not OK/Cancel: primary = destructive verb (`Delete`); secondary = preserving verb (`Keep`).
  - Destructive button styled with `--bg-danger` token, secondary as text link.
- Non-destructive:
  - One primary action button; secondary as text link or omitted.
  - Use sparingly — modal interrupts; prefer inline confirm where possible.
