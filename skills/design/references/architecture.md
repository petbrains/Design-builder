# Architecture

SuperDesign is built as a **three-layer system**. Every command — whether called standalone or as a step inside a pipeline — MUST respect this layering. The layers exist to prevent the skill from producing generic "AI slop" output: they force every design decision to be gated against filters and grounded in authoritative sources before emitting.

```
┌──────────────────────────────────────────────────────────────────┐
│  Layer 3: PIPELINES  (orchestration — how we work)               │
│  /design start · make · refine · review · ship                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │ each step invokes atomic commands
                             │ and MUST pass output through ↓
┌──────────────────────────────────────────────────────────────────┐
│  Layer 2: DESIGN FILTERS  (gating — what we will not emit)       │
│  • Design Direction (purpose · tone · differentiation)           │
│  • Design Dials (variance · motion · density)                    │
│  • Frontend Aesthetics (typography · color · layout · motion …)  │
│  • Anti-Patterns (AI Slop Test — absolute bans, visual tells)    │
│  • Output Rules (no placeholders, no "for brevity")              │
└────────────────────────────┬─────────────────────────────────────┘
                             │ facts/tokens resolved via ↓
┌──────────────────────────────────────────────────────────────────┐
│  Layer 1: KNOWLEDGE BASE  (informing — where facts come from)    │
│  1. Project tokens  (.impeccable.md, tailwind.config, xcassets)  │
│  2. MCP servers     (designlib · figma)                          │
│  3. Local CSV       (data/*.csv via scripts/search.py)           │
│  4. iOS HIG refs    (references/ios/)                            │
│  5. Free generation (last resort, always labeled)                │
└──────────────────────────────────────────────────────────────────┘
```

## The Rule

**No pipeline step and no atomic command may emit a design decision without first resolving facts through Layer 1 and gating output through Layer 2, in that order.**

If a filter rejects the candidate output, the step must either:
- re-query Layer 1 with tighter constraints, or
- ask the user to relax the filter (e.g. raise a Design Dial), or
- mark the output as "generated freely — no authoritative source" and continue with extra caveats.

Silently skipping a filter is the single most common way this skill produces "AI slop." Do not do it.

## Layer responsibilities

### Layer 1 — Knowledge Base

Provides **facts**: tokens, palettes, font pairings, component references, HIG rules; MCP-served charts / landing patterns / icons; BM25 search over local UX guidelines, tech-stack specifics, anti-patterns. Resolution order is fixed (project → MCP → CSV → HIG refs → free). See [`SKILL.md` § Layer 1](../SKILL.md#layer-1-knowledge-base--where-we-get-facts) for the full sourcing protocol.

### Layer 2 — Design Filters

Provides **gates**: every candidate output is checked against the project's declared Design Direction, current Design Dials, platform aesthetics rules, the Anti-Patterns list, and the Output Rules. Filters are **mandatory** — they are what makes this skill distinct from raw generation. Source files:

- Design Direction + Dials → `SKILL.md` § Layer 2
- Web aesthetics → `references/web/` (typography.md, color-and-contrast.md, spatial-design.md, motion-design.md, interaction-design.md, responsive-design.md)
- iOS aesthetics → `references/ios/` (color.md, layout.md, materials.md, motion.md, gestures.md, haptics.md, controls.md, navigation.md, modals.md, toolbar.md, icons.md, accessibility.md, ui-writing.md, …)
- Anti-Patterns → `SKILL.md` § Layer 2 > Anti-Patterns + automated detector at `scripts/detect-antipatterns.mjs`

### Layer 3 — Pipelines

Provides **orchestration**: 5 lifecycle pipelines (`start`, `make`, `refine`, `review`, `ship`) that call atomic commands in sequence with checkpoints between steps. Pipelines never own design rules of their own — they only sequence existing atomics and ensure each step's output passes through Layer 2 before the next step begins. See [`pipelines.md`](pipelines.md) for step-by-step runbooks.

## Extension points

New capabilities are added **additively**, never by rewriting existing layers:

- `<!-- KB-EXTENSION: add new source here -->` — a new MCP server, a new CSV table, a new reference folder
- `<!-- FILTER-EXTENSION: add new filter here -->` — a new aesthetics rule, a new anti-pattern, a new Output Rule
- `<!-- PIPELINE-STEP-EXTENSION: <pipeline-name> -->` — a new step inside an existing pipeline (e.g. adding a visual-eval step to `review`)
- `<!-- PIPELINE-EXTENSION -->` — a new lifecycle pipeline (rare — only if it genuinely does not fit the existing 5)

Markers live inside `pipelines.md` and `SKILL.md` so any future contribution can slot in without touching unrelated sections.

## What this architecture is NOT

- Not a workflow engine — there is no runtime, no DAG; pipelines are prompt-level orchestration described in markdown that Claude follows step by step.
- Not a DSL — atomic commands stay as plain `/design <verb>` invocations; pipelines are also plain `/design <verb>` invocations, just higher-level.
- Not a replacement for atomic commands — power users and single-task calls still invoke atomics directly. Pipelines exist for lifecycle clarity, not to replace the surface area.
