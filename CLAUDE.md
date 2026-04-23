# SuperDesign Plugin

This repository is a Claude Code plugin: `superdesign`. It bundles the `design` skill and supporting assets.

Plugin manifest lives at `.claude-plugin/plugin.json`. The skill is at `skills/design/SKILL.md`. When the plugin is installed, users invoke it as `/superdesign:design <command>` (e.g. `/superdesign:design system`, `/superdesign:design craft`).

## Structure

- `.claude-plugin/plugin.json` — plugin manifest (name, version, author, keywords)
- `.claude-plugin/marketplace.json` — single-plugin marketplace manifest (so the repo itself is installable as a marketplace source)
- `skills/design/SKILL.md` — main skill definition (22+ commands)
- `skills/design/data/` — CSV databases for BM25 search
- `skills/design/references/` — deep design documentation (100+ files, including `web/motion/` with designer perspectives)
- `skills/design/scripts/` — BM25 search engine, design system generator, anti-pattern detector
- `skills/design/templates/` — starter templates (iOS SwiftUI theme, web CSS/Tailwind)
- `NOTICE.md` — attribution for 5 source open-source projects
- `LICENSE` — MIT
- `docs/superpowers/specs/` — integration specs (e.g. motion-principles reintegration)

## Scripts

Python scripts (`search.py`, `core.py`, `design_system.py`) use stdlib only — no pip install needed.
Node.js anti-pattern detector works in `--fast` mode without npm dependencies.

## Plugin installation (for end users)

```
/plugin marketplace add petbrains/design-plugin
/plugin install superdesign@superdesign-marketplace
```

Then invoke `/superdesign:design teach` to set up project context, or go straight to `/superdesign:design system` / `craft` / `audit`.
