# Commands — what the skill knows about each entry point

> What this is: the skill's view of the 4 user-facing commands. Each command file (`commands/*.md`) holds the actual user-facing scenario; this doc gives the skill cross-cutting context (filter emphasis, output folder, fallback behaviour) so the skill can answer correctly when a command activates it.

## The four commands

| Command                                | Purpose                                          | Output target                                  |
|----------------------------------------|--------------------------------------------------|------------------------------------------------|
| `/design-builder:setup` (alias `start`) | Establish the project's design foundation        | Writes to `<project>/design/` (system, tokens, interview, preview, references) |
| `/design-builder:create [what]`        | Generate a page / screen / section               | Writes code into the user's source tree (per stack); does NOT write to `design/` except optional `preview.html` |
| `/design-builder:improve [target]`     | Light audit + apply concrete fixes               | Patches user files (Edit / Figma MCP); does NOT write to `design/` |
| `/design-builder:review [target]`      | Strict audit; delegates to `agents/design-auditor` | Writes report to `<project>/design/reviews/review-YYYY-MM-DD-HHMM.md` |

## Layer 2 emphasis per command

All 6 filters (Design Direction, Dials, Aesthetics, Anti-Patterns, Distinctiveness Gate, Output Rules) **always run** before emit. The list below names which are most load-bearing for that command — i.e. which a reviewer should scrutinise hardest.

- `/setup` — Design Direction, Distinctiveness Gate (HARD), Anti-Patterns. Reason: this is where character is set. Generic "premium SaaS" coming out of `/setup` poisons every later command.
- `/create` — Design Direction (must apply the system from `design/system.md`), Dials, Distinctiveness Gate (SOFT — show `Risks taken & gaps`), Anti-Patterns, Output Rules. Reason: this generates real code; partial output or generic templates show up here.
- `/improve` — Anti-Patterns, Distinctiveness Gate, Output Rules. Reason: improvement that adds new generic patterns is worse than no improvement.
- `/review` — Distinctiveness Gate runs as an EVALUATOR (the auditor applies its 7 questions to as-built surfaces); Anti-Patterns + Output Rules verified against the report itself.

## Layer 1 source emphasis per command

- `/setup` — interview is the dominant source; designlib MCP supplies palette / font_pair / style candidates; inspiration_pages used to ground "direction" choices in real examples.
- `/create` — `inspiration_pages` (via `get_design_reference(type='page', ...)`) is the primary source. Project tokens (read from `design/system.md` + `design/tokens.css`) are layered on top.
- `/improve` — reads user files first; consults knowledge base (anti-patterns, web/ios refs) for fix recipes.
- `/review` — reads user files + visual artifacts (Figma URL, screenshots in `design/screenshots/`); knowledge base used for evaluation criteria.

## Project state expectations

- `/setup` — assumes nothing. Creates `design/` from scratch.
- `/create` — assumes `design/system.md` exists. If not: stop, ask user to either run `/setup` or supply explicit reference (URL/screenshot/code).
- `/improve` — assumes target (file path / Figma URL / screenshot) supplied. Falls back to repo-wide if no target.
- `/review` — same as `/improve` for input. Falls back to code-only mode if no visual.

## Mandatory `Next:` block

**Every command, on completion, must end its output with a `Next:` block — 1-2 sentences recommending the next concrete action.** This is contextual based on what just happened (e.g. clean review → suggest next page; review with P0s → suggest `/improve`). The block format:

```
**Next:** <one-sentence recommendation referring to a specific command or action>.
```

This is enforced as the last instruction in each `commands/*.md` body.

## Output folder convention

All command output that's not user-source-code goes to `design/` in the user's project root. Commands MUST NOT write to arbitrary locations. The folder layout:

```
design/
  system.md            # /setup output: design system spec (markdown, human-readable)
  tokens.css           # /setup output: CSS variables (or tokens.json for non-web)
  interview.md         # /setup output: interview answers + decisions w/ timestamps
  preview.html         # /setup or /create output: visual preview
  references/
    urls.md            # /setup: user-supplied reference links
    downloaded/        # /setup: downloaded screenshots
  screenshots/         # /review input: user-supplied screenshots (later: playwright)
  reviews/
    review-YYYY-MM-DD-HHMM.md   # /review output: P0-P3 + fixable_count + mode
```

User-facing recommendation in README: version `system.md` / `tokens.css` / `interview.md` / `reviews/`; gitignore `references/downloaded/` and `screenshots/` if you don't want binaries in the repo.
