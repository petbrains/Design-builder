# Architecture — three-layer model

`design-builder` is a three-layer plugin. Every command — whether the user invokes it directly (`/design-builder:setup`, `/create`, `/improve`, `/review`) — must respect the layering.

```
┌──────────────────────────────────────────────────────────────────┐
│  COMMANDS (commands/*.md)                                         │
│  /design-builder:setup · start · create · improve · review        │
│  Thin scenarios. Each = "what to ask, what to emit, where to put it." │
└────────────────────────────┬─────────────────────────────────────┘
                             │ activates ↓
┌──────────────────────────────────────────────────────────────────┐
│  SKILL (skills/design/SKILL.md)                                   │
│  Knowledge base + filters + Layer 1 resolvers.                    │
│  Source of truth for rules; does not execute commands.            │
└────────────────────────────┬─────────────────────────────────────┘
                             │ enforces ↓
┌──────────────────────────────────────────────────────────────────┐
│  Layer 2: DESIGN FILTERS  (gating)                                │
│  Direction · Dials · Aesthetics · Anti-Patterns ·                 │
│  Distinctiveness Gate · Output Rules                              │
│  All six always run before emit.                                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │ pulls facts via ↓
┌──────────────────────────────────────────────────────────────────┐
│  Layer 1: KNOWLEDGE BASE                                          │
│  Project tokens · designlib MCP (incl. inspiration_pages) ·       │
│  local CSV · iOS HIG · free generation                            │
│  Resolved via get_design_reference(type, filters).                │
└──────────────────────────────────────────────────────────────────┘
```

## The rule

No command may emit a design decision without first:

1. **Resolving facts through Layer 1** in the fixed source order (project → MCP → CSV → HIG → free).
2. **Gating output through all six Layer 2 filters**, in order.

Silently skipping Layer 2 is the single most common way this plugin produces "AI slop". Don't.

## Layer responsibilities

### Commands (entry points)
- Hold the user-facing scenario: what to ask, what to do with answers, where to write output.
- Activate the skill (this skill is the rules engine).
- Enforce their own `Next:` block at the end.

### Skill (knowledge base + rules)
- Hold the rules: filter definitions, source order, command map, anti-pattern catalogue.
- Hold the references: `web/`, `ios/`, `brand/`, `motion/` — deep documentation that commands load on demand.
- **Do not execute.** Wait until a command activates it.

### Layer 2 (filters)
Six filters, all mandatory before emit:

1. **Design Direction** — purpose, tone, differentiation.
2. **Design Dials** — VARIANCE / MOTION / DENSITY (1-10 each).
3. **Frontend Aesthetics** — typography, color, layout, motion, interaction (per-platform refs).
4. **Anti-Patterns** — BAN 1-4 (side-stripe / gradient text / AI palette / 3-equal-card row) + technical rules.
5. **Distinctiveness Gate** — 7 questions; HARD on `/setup`, SOFT on `/create`, evaluator inside `/review`.
6. **Output Rules** — no `// ...`, no "for brevity", no skeletons.

Detail: [`distinctiveness-gate.md`](distinctiveness-gate.md), [`design-dials.md`](design-dials.md), `web/`, `ios/`.

### Layer 1 (knowledge base)
Sources resolved via `get_design_reference(type, filters)`:

1. Project tokens — `design/tokens.css`, `design/system.md`, etc.
2. designlib MCP — palettes, fonts, **inspiration_pages**, landing_patterns, icons, charts, domains. **Filters are SINGULAR** — for multi-value (multiple moods etc.) call multiple times and dedupe.
3. Local CSV — `data/` (UX guidelines, tech stacks, anti-patterns).
4. iOS HIG — `references/ios/` (when `platform='ios'`).
5. Free generation — last resort.

Full contract: [`layer1-resolvers.md`](layer1-resolvers.md). inspiration_pages schema: [`inspiration_pages.md`](inspiration_pages.md). Per-command contracts live in `commands/*.md` themselves.

## Extension points

Extensions are additive — they never rewrite existing layers. Markers in `SKILL.md`:

- `<!-- KB-EXTENSION: add new source here -->` — new MCP tool, CSV table, reference folder. Add the row to `MCP_TOOL_MAP` in `layer1-resolvers.md`.
- `<!-- FILTER-EXTENSION: add new filter here -->` — new aesthetic rule, anti-pattern, or output rule. Add to the filter section in `SKILL.md`.

(Pipeline extension markers from v1.2 are gone — there are no pipelines in v2.0.)

## What changed in v2.0 (vs v1.2)

| v1.2                                                  | v2.0                                                                  |
|-------------------------------------------------------|------------------------------------------------------------------------|
| 5 lifecycle pipelines (`start`/`make`/`refine`/`review`/`ship`) | Pipelines removed. 4 user-facing commands instead.                |
| 22+ atomic commands (`/design system`, `/design craft`, ...) | Atomic commands removed. The 4 commands cover the same ground.   |
| `landing_patterns` only for whole-page references     | `inspiration_pages` (405 records) is primary; `landing_patterns` is fallback. |
| Layer 1 documented prosaically in SKILL.md            | Layer 1 has a typed resolver: `get_design_reference()`.               |
| `.cursor-plugin/` for Cursor support                  | Cursor support dropped.                                                |
| Output written to ad-hoc paths                        | Output standardised to `<project>/design/`.                            |
