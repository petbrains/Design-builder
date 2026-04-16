# Design Plugin for Claude Code

Unified design skill for Claude Code with 30 commands covering the full design lifecycle -- from UX planning to production polish.

Built on top of four open-source projects: [Impeccable](https://github.com/pbakaus/impeccable), [Emil Kowalski Design Skill](https://emilkowal.ski/skill), [Taste Skill](https://github.com/Leonxlnx/taste-skill), and [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill). See [NOTICE.md](NOTICE.md) for full attribution.

## Installation

Copy the `.claude/skills/design/` folder into your project:

```bash
# Clone and copy the skill into your project
git clone https://github.com/anthropics/design-plugin.git /tmp/design-plugin
cp -r /tmp/design-plugin/.claude/skills/design your-project/.claude/skills/design
rm -rf /tmp/design-plugin
```

Or clone this repository directly and open it in Claude Code.

No `npm install` or `pip install` required. All scripts use standard library only.

## Quick Start

Once installed, use `/design` commands in Claude Code:

```
/design craft          Build a distinctive interface from scratch
/design shape          Plan UX/UI with structured discovery
/design audit          Audit accessibility, performance, theming, responsive, anti-patterns
/design search query   Search 161 product types, 67 styles, 57 font pairings
/design style          Apply style presets (minimalist, brutalist, soft)
/design system         Generate a complete design token system
/design brand          Create brand voice, identity, and messaging
/design logo           Generate logos (55+ styles)
/design slides         Create strategic HTML presentations
/design ui             Build with shadcn/ui + Tailwind CSS
```

Run `/design teach` first to set up your project's design context.

## All Commands

| Category | Commands |
|---|---|
| Core Design | `craft`, `shape`, `teach`, `extract`, `search` |
| Review & Quality | `audit`, `critique`, `polish` |
| Targeted Refinement | `animate`, `typeset`, `colorize`, `layout`, `clarify` |
| Intensity | `bolder`, `quieter`, `distill`, `overdrive`, `delight` |
| Production | `harden`, `optimize`, `adapt` |
| Style & System | `style`, `redesign`, `system` |
| Brand & Assets | `brand`, `logo`, `cip`, `banner`, `slides` |
| UI Implementation | `ui` |

## What's Inside

- **SKILL.md** -- main skill definition with 30 commands and design guidelines
- **data/** -- CSV databases for BM25 search (styles, colors, typography, products, UX guidelines, 16 framework-specific guides)
- **references/** -- 90+ deep reference documents on typography, color, spatial design, motion, interaction, responsive design, brand systems, design tokens, and more
- **scripts/** -- BM25 search engine (Python), design system generator, anti-pattern detector (Node.js)
- **templates/** -- starter templates for brand guidelines

## License

MIT. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).
