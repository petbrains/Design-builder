# Design Plugin

This repository is a Claude Code design skill plugin. The skill is defined in `.claude/skills/design/SKILL.md`.

## Structure

- `.claude/skills/design/SKILL.md` -- main skill definition (30 commands)
- `.claude/skills/design/data/` -- CSV databases for BM25 search
- `.claude/skills/design/references/` -- deep design documentation (90+ files)
- `.claude/skills/design/scripts/` -- search engine, design system generator, anti-pattern detector
- `.claude/skills/design/templates/` -- starter templates
- `NOTICE.md` -- attribution for 4 source open-source projects

## Scripts

Python scripts (`search.py`, `core.py`, `design_system.py`) use stdlib only -- no pip install needed.
Node.js anti-pattern detector works in `--fast` mode without npm dependencies.
