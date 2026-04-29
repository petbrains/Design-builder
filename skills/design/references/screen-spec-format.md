# screen-spec-format.md

Defines the structure of `design/screens/<name>.md`. `/design_screen` writes specs in this format. `/build` parses them.

The screen spec format is **identical** to the page spec format ([`page-spec-format.md`](page-spec-format.md)) with three additional sections specific to app screens. This file documents only the deltas; sections 1-9 from `page-spec-format.md` apply unchanged.

## File location and naming

- Path: `design/screens/<slug>.md`
- Slug rules same as page-spec-format.md.

## Additional sections (inserted between sections 4 and 5 of page-spec-format.md)

### 4a. `## Navigation context`
- `Position in hierarchy:` one of `tab_root | push (from <parent screen>) | modal | sheet | full-screen-cover`.
- `Entry transitions:` one of `tab-switch (instant) | push (slide from right, native) | modal-present (slide from bottom) | sheet (sheet detents: <list>) | crossfade`.
- `Exit:` mirror of entry, plus any non-default dismiss (swipe-down on sheet, swipe-back gesture support).

### 4b. `## Gestures`
Bullet list, one per supported gesture:
- `Swipe back: <enabled | disabled> — <reason if disabled>` (default enabled for push)
- `Pull-to-refresh: <enabled | disabled> — <data source it reloads>` (only on list/feed screens)
- `Long-press: <action description if any>` (only when used)
- `Swipe-to-action: <left|right swipe action description>` (e.g. delete-on-swipe in lists)
- `Pinch-to-zoom: <enabled if image/map content>` (omit otherwise)

If no special gestures, write `Standard navigation gestures only.` (one line).

### 4c. `## Safe areas`
Source: `design/style-guide.md ## Platform constraints` (iOS section).

- `Top inset:` `respect (status bar + nav bar)` OR `extend under (custom translucent header)`.
- `Bottom inset:` `respect (home indicator + tab bar if present)` OR `extend under (custom blur-backed bar)`.
- `Dynamic Island clearance:` `≥ 8pt below island region for top-aligned content` (default) OR explicit override.
- `Keyboard avoidance:` `enabled (lift content above keyboard)` for screens with inputs; `disabled` for screens without inputs.

## Sections (5-9) inherited from page-spec-format.md

Sections `## Sections`, `## Edge cases`, `## Components needed`, `## Animations`, `## Risks taken & gaps` follow page-spec-format.md unchanged, with these adaptations for iOS/native:

- `## Components needed`: lists native UI components when stack is iOS (e.g. `SwiftUI: NavigationStack, List, Form`) or React Native (`@react-navigation, FlatList`).
- `## Animations`: spring animations and HIG-defined transitions, not the React animations catalog. Format: `<descriptive name> — spring(response: <s>, dampingFraction: <d>), trigger: <event>` for SwiftUI; equivalent for other stacks.

## Validation rules `/build` enforces

All page-spec-format.md validation rules apply, plus:
- Sections 4a, 4b, 4c are mandatory (not optional like Risks).
- For iOS: `## Animations` entries use spring/HIG terminology, not catalog `animation.id` references (those are React-only).
