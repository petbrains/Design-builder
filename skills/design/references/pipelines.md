# Pipelines — Lifecycle Runbooks

Five pipelines organize the 22+ atomic commands into the natural flow of a design project: **start → make → refine → review → ship**. Each pipeline is a sequence of atomic commands with checkpoints and a mandatory pass through [Layer 2 filters](architecture.md) after every step.

## Universal contract

Every pipeline obeys the same rules:

1. **Pre-check** — before the first step, confirm the prerequisites listed under that pipeline. If missing, offer to run the pipeline that produces them (e.g. `start` before `make`).
2. **Step ordering** — steps run sequentially. Do not parallelize unless the pipeline explicitly says so.
3. **Filter pass** — after each step, the output is checked against Layer 2 filters (Design Direction, Dials, Aesthetics, Anti-Patterns, Output Rules). Failures route back to the step with tightened constraints.
4. **Checkpoints** — at every `→ CHECKPOINT` line, pause and show the user what was produced before moving on. They can redirect, skip, or stop.
5. **Flags** — pipelines accept:
   - `--platform web|ios|cross` — passed through to every step
   - `--from <step>` — resume from a named step (skip earlier ones)
   - `--skip <step>` — run everything except the named step
   - `--dry-run` — print the plan (which atomics will run, in what order) without executing
   - `--step` — interactive: confirm each step before running it
6. **Post-validation** — the final output of the pipeline is re-scanned against Layer 2 as a whole, not just step-by-step, to catch cross-step drift.

---

## `/design start` — New project foundation

**Purpose:** establish design context, generate a design system, and prepare brand artifacts so every later pipeline has something to pull from.

**Pre-check:** none. This is the first pipeline.

**Steps:**

1. `teach` — capture Design Context (audience, use cases, tone, platform) into `.impeccable.md`.
   → CHECKPOINT: show the captured context; user confirms or corrects.
2. `system [--platform]` — run the structured interview, propose 3 variations, emit tokens. Delegates to `design-system-architect` in Claude Code; runs inline in Cursor. Same output either way.
   → CHECKPOINT: show the 3 variations with differentiation hooks; user picks one.
   → FILTER PASS: emitted tokens must not contain Anti-Pattern colors (no lila/cyan-on-dark), must honor Design Dials.
3. `shape [--platform]` — plan the top-level UX/UI before any code is written. Produces brief with layout, states, interactions, content strategy, open questions.
   → CHECKPOINT: present the brief; user approves or lists revisions.
4. `extract [--platform]` *(optional, only if user supplied reference screenshots/URLs)* — pull reusable components and tokens from references.
5. `brand` *(optional)* — derive voice, visual identity, messaging frameworks from the Design Context.

<!-- PIPELINE-STEP-EXTENSION: start -->

**Output:** `.impeccable.md` populated · design-system tokens committed · UX brief · (optional) brand artifacts.

**Hand-off:** `make` can now run against a complete system.

---

## `/design make` — Build the interface

**Purpose:** turn design context + tokens + UX brief into working code.

**Pre-check:** design system exists (tokens committed, `.impeccable.md` has Design Context). If not, suggest running `start` first.

**Entry variants:**
- **Code-first (default)** — user wants working code built from scratch.
- **Figma-URL entry** — user provides `figma.com/design/:fileKey/...?node-id=X-Y`. Route via [`references/figma/README.md`](figma/README.md) — `ios-swiftui.md` for iOS, `implement-design/` for web. The Figma frame acts as the page-level spec; steps 2–5 still apply post-implementation.
- **Figma-output variant of `craft`** — user wants the screen built **in Figma** using the published DS, not in code. Routes to `references/figma/generate-design/` + `skills/figma-use/`. Skip steps 2–5 (they target code).

**Steps:**

1. `craft [--platform]` — build the interface from scratch using project tokens. Gathers page-level context, makes design decisions, emits working code.
   → FILTER PASS: mandatory. Every component checked against Anti-Patterns (no 3-column card grids, no side-stripe borders, no gradient text, etc.).
2. `typeset [--platform]` — fix typography if the interface needs per-surface adjustments (scale, weight, hierarchy, readability).
3. `colorize [--platform]` — apply strategic color if the interface is still monochrome after `craft`.
4. `layout [--platform]` — tune spacing, rhythm, composition, hierarchy.
5. `animate [--platform]` — add purposeful motion with designer-weighting (Emil/Jakub/Jhey). Honors `MOTION_INTENSITY` dial.
   → CHECKPOINT: preview interactions before committing motion code.
   → FILTER PASS: motion anti-patterns (animating layout properties, bounce easing, unrespected Reduce Motion) must be zero.

<!-- PIPELINE-STEP-EXTENSION: make -->

**Output:** production-quality interface code, matching tokens and Design Direction, free of Anti-Patterns.

**Hand-off:** `refine` for further tuning, or `review` for quality pass.

---

## `/design refine` — Iterative adjustment

**Purpose:** course-correct a built interface toward the desired character. Used when `make` output is *correct* but not *right*.

**Pre-check:** there is something to refine (code exists).

**Steps:**

1. `critique [--platform]` — Nielsen heuristics scoring · AI-slop detection · persona walkthroughs. Delegates to `design-critic`.
   → CHECKPOINT: present critique report with P0–P3 severity.
2. **Direction modifier** *(pick one based on critique + user preference)*:
   - `bolder` — amplify safe/boring designs
   - `quieter` — tone down overstimulating
   - `distill` — strip to essence
   - `overdrive` — push past conventions (proposes 2–3 directions, gets approval first)
   - `delight` — add moments of joy
3. `clarify [--platform]` — improve UX copy if critique flagged content issues.
4. `polish [--platform]` — final quality pass: alignment, spacing, consistency, typography, color, interaction states, micro-interactions, edge cases.
   → FILTER PASS: post-polish re-run Anti-Pattern detector.

<!-- PIPELINE-STEP-EXTENSION: refine -->

**Output:** same interface, tuned toward its intended character, validated through critique + polish.

**Hand-off:** `review` for formal quality gate, or back to `make` if critique revealed structural issues.

---

## `/design review` — Quality gate

**Purpose:** verify a built interface is ready for production. Produces a scored report, not just a vibe-check.

**Pre-check:** interface is built and refined to the team's satisfaction.

**Steps:**

1. `audit [--platform]` — technical quality across 5 dimensions. Delegates to `design-auditor`; motion findings delegate further to `motion-auditor`.
   - **Web:** WCAG AA accessibility, Core Web Vitals, theming, responsive, Anti-Patterns
   - **Web motion:** Motion Gap Analysis (conditional renders without `AnimatePresence`, ternary swaps, dynamic styles without transition)
   - **iOS:** Dynamic Type AX5, Reduce Motion, Increase Contrast, Increase Transparency, `.accessibilityLabel/.accessibilityValue` coverage, HIG deviations
   → CHECKPOINT: scored report with P0–P3 severity + prioritized fix plan.
2. `critique [--platform]` — second pass focused on UX heuristics. Delegates to `design-critic`.
3. `polish [--platform]` *(with `--fix`)* — apply the fix plan. Delegates to `polish-fixer` when `--fix` is present.
   → FILTER PASS: post-fix re-run audit to confirm severity counts went down.

<!-- PIPELINE-STEP-EXTENSION: review -->

**Output:** audit report (with before/after if `--fix` was used) · confirmed reduction in P0–P1 issues.

**Hand-off:** `ship` if audit passes. Back to `refine` if critique revealed deeper issues.

---

## `/design ship` — Production readiness

**Purpose:** final pass before the interface goes live. Stress-tests, performance tuning, cross-platform adaptation.

**Pre-check:** `review` passed (or issues found are explicitly accepted).

**Steps:**

1. `harden [--platform]` — stress-test with extreme inputs (long text, emoji, RTL, large numbers), error scenarios (network, API, validation), overflow, i18n, accessibility edge cases.
   → CHECKPOINT: show surfaces that broke; confirm fixes.
2. `optimize [--platform]` — fix UI performance.
   - **Web:** Core Web Vitals, images, JS bundle, CSS, fonts, loading strategy, animations
   - **iOS:** main-thread work, image decoding, list diffing, launch time, hit-testing cost
3. `adapt [--platform]` — responsive/cross-platform.
   - **Web:** per-breakpoint strategy
   - **iOS:** iPhone ↔ iPad size classes ↔ Mac Catalyst ↔ watchOS/visionOS
4. `code-connect` *(optional, Figma MCP available + Org/Enterprise Figma plan + published DS in Figma)* — batch-map the codebase's design-system components to their Figma counterparts via `send_code_connect_mappings`. Load [`references/figma/code-connect-batch.md`](figma/code-connect-batch.md). Skipped silently if any prerequisite is missing.

<!-- PIPELINE-STEP-EXTENSION: ship -->

**Output:** production-ready code with stress-test coverage, performance budget met, adapts across target devices.

**Hand-off:** ship it.

---

## Non-lifecycle atomics (not in any pipeline)

These atomic commands produce *artifacts*, not *lifecycle stages*, so they are not sequenced into pipelines. Call them directly:

- `/design brand` · `/design logo` · `/design cip` · `/design banner` · `/design slides` — brand/asset deliverables
- `/design search` — BM25 lookup across local CSV databases
- `/design redesign` — audit + fix existing projects; this is a shortcut that internally runs `review` + targeted `polish`/`refine`, so you usually want the full pipelines instead

<!-- PIPELINE-EXTENSION -->

---

## Step-to-pipeline reverse index

Which pipeline uses which atomic command:

| Atomic | `start` | `make` | `refine` | `review` | `ship` |
|---|---|---|---|---|---|
| teach | ✓ |  |  |  |  |
| system | ✓ |  |  |  |  |
| shape | ✓ |  |  |  |  |
| extract | ✓ (opt) |  |  |  |  |
| brand | ✓ (opt) |  |  |  |  |
| craft |  | ✓ |  |  |  |
| typeset |  | ✓ | ✓ (via modifier) |  |  |
| colorize |  | ✓ | ✓ (via modifier) |  |  |
| layout |  | ✓ |  |  |  |
| animate |  | ✓ |  |  |  |
| critique |  |  | ✓ | ✓ |  |
| bolder / quieter / distill / overdrive / delight |  |  | ✓ |  |  |
| clarify |  |  | ✓ |  |  |
| polish |  |  | ✓ | ✓ (with `--fix`) |  |
| audit |  |  |  | ✓ |  |
| harden |  |  |  |  | ✓ |
| optimize |  |  |  |  | ✓ |
| adapt |  |  |  |  | ✓ |

Power users can still invoke any atomic directly — pipelines are the recommended entry point for newcomers and for standard lifecycle work.
