# Motion Principles Reintegration — Design Spec

**Date:** 2026-04-23
**Status:** Approved for implementation
**Scope:** Integrate `design-motion-principles-main/` content into `.claude/skills/design/` plugin by enhancing existing commands (no new commands).

---

## Goal

Fold the unique content of `design-motion-principles-main/skills/design-motion-principles/` (9 reference files, ~2100 lines) into the existing design plugin so that:

- `/design animate` gains **designer-specific perspectives** (Emil Kowalski / Jakub Krehel / Jhey Tompkins) with context-aware weighting
- `/design audit` gains **Motion Gap Analysis** (finding *missing* animations) and a **structured audit checklist**
- `/design polish` gains deeper **anti-pattern detection** for motion

No new top-level commands are introduced. Designer perspectives are **web-only** (framer-motion / CSS-centric techniques). iOS motion continues to use the existing `references/ios/motion.md` + HIG pipeline.

---

## What's Unique (value being preserved)

Content in `design-motion-principles-main/` not already in the plugin:

1. **Three designer philosophies** — Emil (restraint/speed), Jakub (polish), Jhey (play) as distinct lenses
2. **Context-aware weighting** — project-type → designer Primary/Secondary/Selective mapping
3. **Motion Gap Analysis workflow** — systematic search for conditional UI that lacks animation
4. **Frequency rule** — animation appropriateness by interaction frequency (Emil)
5. **Enter/exit recipes** — opacity + translateY + blur spring combos (Jakub)
6. **Audit report template** — structured per-designer output format

Content with overlap that must be deduplicated:

- Duration guidelines (plugin: 100/300/500 rule; principles: frequency-based) → keep plugin's as default, reference principles' for context-dependent framing
- `prefers-reduced-motion` → short form in hub, deep dive in `motion/accessibility.md`
- GPU optimization → short rule in hub, deep dive in `motion/performance.md`
- Anti-bounce rule → stays in hub; removed from `motion/common-mistakes.md` to avoid duplication

---

## Architecture

### Target file layout

```
.claude/skills/design/references/web/
├── motion-design.md          # HUB — core rules + philosophy entry + routing (grows 170 → ~250 lines)
└── motion/                   # NEW — 10 files (9 adapted + 1 README)
    ├── README.md             # Routing index for the folder
    ├── emil-kowalski.md      # Restraint/speed philosophy
    ├── jakub-krehel.md       # Production polish philosophy
    ├── jhey-tompkins.md      # Playful experimentation philosophy
    ├── audit-checklist.md    # Systematic audit guide
    ├── motion-gaps.md        # Extracted workflow: finding missing animations
    ├── common-mistakes.md    # Anti-patterns (anti-bounce removed, lives in hub)
    ├── performance.md        # GPU/will-change deep dive
    ├── accessibility.md      # prefers-reduced-motion + vestibular guidance
    ├── technical-principles.md # Enter/exit recipes, spring physics
    └── output-format.md      # Audit report template
```

### Why this layout

- `motion/` is nested under `web/` (not at `references/` root) because designer techniques are web-centric. Matches existing `web/` vs `ios/` separation.
- `motion-design.md` stays as the hub — commands enter here, then drill into `motion/` files on demand. Preserves the "lightweight entry → deep ref" pattern the plugin uses elsewhere.
- `motion-gaps.md` is **new** (not a verbatim copy) — extracted from the motion-gap section of `audit-checklist.md` + the motion-gap patterns in the original SKILL.md. Lives as a stand-alone workflow for `/design audit` to load cleanly.

---

## Command Wiring

### `/design animate` (web path)

Updated flow:

1. Enter via `references/web/motion-design.md` (hub)
2. **Reconnaissance**: infer project-type from files (package.json, CLAUDE.md, existing animations) + read `MOTION_INTENSITY` dial
3. **Weighting proposal**: present Primary/Secondary/Selective designer weighting via `AskUserQuestion` (or plain text if unavailable). Table lives in hub:
   - Productivity tool → Emil / Jakub / Jhey (selective)
   - Kids / creative / marketing → Jakub / Jhey / Emil (selective)
   - SaaS dashboard → Emil / Jakub / Jhey (empty states)
   - Mobile / e-commerce → Jakub / Emil / Jhey (delighters)
4. **Wait for user confirmation** before proceeding
5. **Load 1-2 designer files** from `motion/` based on confirmed weighting
6. **Implement** using recipes from `motion/technical-principles.md`
7. **Mandatory accessibility check** via `motion/accessibility.md` before finishing

iOS path of `/design animate` is unchanged — continues to use `references/ios/motion.md`.

### `/design audit` (web path)

New "Motion" sub-workflow:

1. Load `motion/audit-checklist.md` as systematic guide
2. Run Motion Gap Analysis per `motion/motion-gaps.md`:
   - grep `{condition && <Component />}` without `AnimatePresence`
   - grep `{condition ? <A /> : <B />}` without transition
   - grep dynamic inline styles without `transition` property
3. Review existing animations against `motion/common-mistakes.md`
4. Emit motion section of audit report using `motion/output-format.md` template

### `/design polish` (web path)

- Motion-related sub-check loads `motion/common-mistakes.md` to flag: `scale(0)` starts, bounce/elastic easing, animating layout properties (width/height/padding), missing `prefers-reduced-motion`.

### `/design critique`, `/design delight`, `/design overdrive`

Not modified in this reintegration. Future work if needed.

---

## SKILL.md Edits (`.claude/skills/design/SKILL.md`)

Scope-limited edits only:

**Edit 1 — Motion section (~line 154-163):** add paragraph on frequency rule + golden rule as cross-cutting principles; add one-liner pointer to `references/web/motion/`.

**Edit 2 — `/design animate` row in command table (~line 306):** update deep-ref column to `web: motion-design.md + motion/ (designer lenses) · ios: ios/motion.md`.

**Edit 3 — `/design audit` description (~line 281-286):** add bullet mentioning Motion Gap Analysis with path to `motion/motion-gaps.md`.

**Edit 4 — Reference Index → Web table (~line 404-408):** add row for `references/web/motion/` pointing to its `README.md`.

No other SKILL.md changes. Design Dials, Anti-Patterns section, iOS references, commands outside animate/audit/polish — all untouched.

---

## Hub File Evolution (`references/web/motion-design.md`)

Final shape (~250 lines):

**Retained sections (unchanged):**
- Duration: 100/300/500 rule
- Easing curves with CSS variables
- "Only animate transform and opacity"
- Staggered animations
- Reduced Motion (short form — 1 paragraph)
- Perceived Performance (short form)
- Anti-bounce rule

**New sections:**
- "Philosophy Entry Point" at top: frequency rule (Emil), golden rule (Jakub), context-to-perspective mapping table
- "When to load deeper references" routing block:
  - Context reconnaissance + designer weighting → `motion/README.md`
  - Per-designer techniques → `motion/{emil-kowalski,jakub-krehel,jhey-tompkins}.md`
  - Reviewing existing code → `motion/audit-checklist.md`
  - Finding missing animations → `motion/motion-gaps.md`
  - Enter/exit recipes → `motion/technical-principles.md`
  - Anti-patterns deep dive → `motion/common-mistakes.md`
  - Full accessibility → `motion/accessibility.md`
  - Audit report format → `motion/output-format.md`

**Deduplication rules applied:**
- Duration — keep hub version; add note "context-dependent per designer lens — see motion/"
- `prefers-reduced-motion` — short form in hub; vestibular stats, what-to-preserve, functional-vs-decorative → `motion/accessibility.md` only
- GPU optimization — short rule in hub; will-change + compositor-layer detail → `motion/performance.md` only
- Anti-bounce — stays in hub only; removed from `motion/common-mistakes.md`

---

## Cleanup & Attribution

### `design-motion-principles-main/` folder

Remove from repo root after integration is verified. Currently sits as an untracked folder (not in git history).

### Attribution

Update `NOTICE.md` to credit:

- **Kyle Zantos** — author of the original `design-motion-principles` skill (MIT license, kylezantos/design-motion-principles)
- **Emil Kowalski** — emilkowal.ski, animations.dev, Sonner, Vaul
- **Jakub Krehel** — jakub.kr
- **Jhey Tompkins** — jhey.dev, @jh3yy

Include MIT license text reference. A standalone LICENSE copy of the source repo is not needed — permissive license text in NOTICE.md is sufficient.

### Search index

`scripts/search.py` and `data/*.csv` are **not** modified. The BM25 index targets products/styles/palettes/fonts/UX-guidelines — not long prose refs. Motion files are loaded via `Read` tool directly by command routing.

### Anti-pattern detector

`scripts/detect-antipatterns.mjs` is **not** modified. It targets CSS/React structural patterns, not motion philosophy.

---

## Verification

Plugin has no pip/npm dependencies, so verification is visual + manual:

1. File-level diff of `motion-design.md` and new `motion/` folder vs original content
2. Manual run of `/design animate` on a test project (confirm weighting dialog appears, correct designer file loads)
3. Manual run of `/design audit` on a project with known motion gaps (confirm grep-driven gap analysis fires)
4. Read-through of all 4 SKILL.md edits for coherence

No automated test suite required for this reintegration.

---

## Out of Scope

- iOS adaptation of designer perspectives (web-only this pass)
- New commands (e.g. standalone `/design motion-audit`) — explicitly rejected in favor of enhancing existing commands
- BM25 indexing of motion files
- Changes to `/design critique`, `/design delight`, `/design overdrive`
- Cross-platform mapping of framer-motion recipes to SwiftUI
- Changes to `design-dials.md` — `MOTION_INTENSITY` dial stays orthogonal to designer lenses; no merge attempted
