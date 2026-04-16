# Attribution & Notices

This unified design plugin combines work from four open-source projects. Each contributor's work is credited below.

## Source Projects

### Impeccable (Paul Bakaus)
- **Repository**: https://github.com/pbakaus/impeccable
- **License**: Apache 2.0 (based on Anthropic's frontend-design skill)
- **Contribution**: Core design skill architecture, 18 design commands, anti-pattern detection engine (30+ checks), 7 domain reference documents (typography, color, spatial design, motion, interaction, responsive, UX writing), context gathering protocol
- **Files**: SKILL.md (core structure), references/typography.md, references/color-and-contrast.md, references/spatial-design.md, references/motion-design.md, references/interaction-design.md, references/responsive-design.md, references/ux-writing.md, references/craft.md, references/extract.md, scripts/detect-antipatterns.mjs, scripts/detect-antipatterns-browser.js

### Emil Kowalski Design Engineering Skill
- **Website**: https://emilkowal.ski/skill
- **Course**: https://animations.dev/
- **Contribution**: Animation decision framework (frequency-based), spring physics configuration (Apple approach + traditional physics), custom easing curves, Sonner Principles (from building Sonner, 13M+ weekly downloads), perceived performance insights, CSS transform mastery, gesture/drag interaction patterns, component interaction patterns (button scale, popover origin-awareness, tooltip delay skip, blur masking)
- **Files**: Content merged into references/motion-design.md and references/interaction-design.md

### Taste Skill (Leonxlnx)
- **Repository**: https://github.com/Leonxlnx/taste-skill
- **Website**: https://tasteskill.dev
- **Contribution**: 3-dial parameterization system (DESIGN_VARIANCE, MOTION_INTENSITY, VISUAL_DENSITY), style presets (minimalist, brutalist, soft), redesign workflow, anti-repetition rules, output enforcement rules, LLM laziness research, Google Stitch DESIGN.md export format
- **Files**: references/design-dials.md, references/style-minimalist.md, references/style-brutalist.md, references/style-soft.md, references/redesign-workflow.md, references/design-system/stitch-export.md, anti-pattern rules merged into SKILL.md

### UI UX Pro Max Skill (NextLevelBuilder)
- **Repository**: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- **Website**: https://uupm.cc
- **License**: MIT
- **Contribution**: BM25 search engine over CSV databases, 161 product type rules, 67 UI styles, 161 color palettes, 57 font pairings, 99 UX guidelines, 25 chart types, 15 tech stack guides, brand management system, design token architecture, logo/CIP generation, slide creation, banner design, UI styling (shadcn/Tailwind), CLI installer
- **Files**: data/*.csv, data/stacks/*.csv, scripts/search.py, scripts/core.py, scripts/design_system.py, references/brand/*, references/design-system/*, references/design/*, references/slides/*, references/ui-styling/*, templates/*

## License

This combined work is distributed under the MIT License (see LICENSE). Individual components retain their original licenses as noted above.
