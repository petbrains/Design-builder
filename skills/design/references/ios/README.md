---
name: ios-references-index
description: Index of iOS design & engineering references (iOS 18 baseline, iOS 26 Liquid Glass era)
platform: ios
---

# iOS References

Deep references for designing and building on Apple platforms. All files target **iOS 18** (stable) and **iOS 26** (current, Liquid Glass), with watchOS/visionOS/tvOS/iPadOS deltas called out inline. SwiftUI-first; UIKit equivalents shown.

## Foundations

| File | Covers |
|---|---|
| [style-families.md](style-families.md) | 10 shipping iOS visual-style families — the root reference for style recommendation |
| [color.md](color.md) | Semantic colors, `AccentColor`, dynamic resolution, WCAG, Liquid Glass tint |
| [layout.md](layout.md) | Safe areas, size classes, layout margins, readable content guide, Dynamic Type |
| [materials.md](materials.md) | Classic `UIBlurEffect` / SwiftUI `Material` — complements Liquid Glass |
| [motion.md](motion.md) | SwiftUI springs, Reduce Motion, Liquid Glass morphs |

## Controls & Surfaces

| File | Covers |
|---|---|
| [controls.md](controls.md) | Every standard control family, SwiftUI + UIKit, style variations |
| [navigation.md](navigation.md) | `NavigationStack`, `NavigationSplitView`, `TabView`, sheets, popovers |
| [toolbar.md](toolbar.md) | Every `ToolbarItemPlacement`, iOS 26 tab/bottom bars, keyboard toolbars |
| [modals.md](modals.md) | When to pick alert / confirmation / menu / context menu / sheet / popover |

## Interaction

| File | Covers |
|---|---|
| [gestures.md](gestures.md) | System gestures, SwiftUI primitives, swipe actions, drag-and-drop |
| [haptics.md](haptics.md) | SwiftUI `sensoryFeedback`, `UIFeedbackGenerator`, Core Haptics |

## States & Flows

| File | Covers |
|---|---|
| [first-run-states.md](first-run-states.md) | Launch, onboarding, permissions, sign-in, empty/error/loading, paywalls |
| [ambient-surfaces.md](ambient-surfaces.md) | Widgets, Live Activities, Dynamic Island, StandBy, Control Center, Lock Screen |

## Identity & Writing

| File | Covers |
|---|---|
| [icons.md](icons.md) | iOS 18 three variants, iOS 26 Icon Composer + Liquid Glass + 6 appearances |
| [ui-writing.md](ui-writing.md) | Apple Style Guide voice, capitalization, component-level copy |
| [accessibility.md](accessibility.md) | VoiceOver, Dynamic Type, Reduce Motion, color/contrast, every assistive tech |

## Other Apple Platforms

| File | Covers |
|---|---|
| [ipad.md](ipad.md) | iPadOS 18/26 windowing, menu bar, tiling, traffic-light controls |
| [non-iphone-platforms.md](non-iphone-platforms.md) | watchOS, visionOS, tvOS starters with Liquid Glass addenda |

---

## How these are used

- `/design system ios` — interview routes here for platform facts (valid families, controls, motion budget, Dynamic Type matrix)
- `/design craft` — when platform=ios, these references guide implementation
- `/design audit`, `/design critique` — iOS-specific anti-patterns sourced from here
- `/design search` — BM25 indexable (each file is a retrieval target)

**Canonical pairing**: designlib MCP (web/iOS token catalog) + these references (HIG-sourced Apple-specific rules). designlib says *what tokens*, these say *how to wire them up Apple-natively*.
