---
name: design-system-ios-pipeline
description: iOS output pipeline for /design system. Emits xcassets color sets, SwiftUI Color extensions, Typography struct, Spacing enum, Motion presets, HIG-compliant spec.
---

# iOS Pipeline

Consumes: style/palette/font_pair (from designlib, `platform="ios"`) + interview answers.
Emits: HIG-compliant Swift code + asset catalog entries + spec markdown.

**Guiding rule:** Apple-native first. Prefer semantic colors over raw hex, SF fonts as fallback, system spacing/materials where appropriate. designlib tokens augment — they don't replace — Apple's semantic layer. See `references/ios/color.md`, `references/ios/layout.md`, `references/ios/materials.md` for the HIG rules.

## Output bundle

### 1. Asset catalog — `Assets.xcassets/DesignSystem/`

For each palette role, create a `.colorset` with:

- **Universal** variant: base color
- **Dark** variant: dark mode color
- **High Contrast** variants: for both light & dark (higher WCAG targets)

```
Assets.xcassets/
└── DesignSystem/
    ├── Contents.json
    ├── Background.colorset/
    │   ├── Contents.json  (references: Any + Dark + HC Any + HC Dark)
    ├── Surface.colorset/
    ├── Border.colorset/
    ├── TextPrimary.colorset/
    ├── TextSecondary.colorset/
    └── AccentColor.colorset/   (Xcode-recognized AccentColor — drives system tint)
```

**AccentColor** must be the palette primary accent — iOS uses this as `.tint()` default system-wide. See `references/ios/color.md`.

Include `"color-space": "display-p3"` in each `Contents.json` for wide-gamut devices; iOS falls back to sRGB on non-P3 displays automatically.

### 2. `Theme/Color+DesignSystem.swift`

```swift
import SwiftUI

extension Color {
    // Semantic — prefer these in views
    static let dsBackground     = Color("Background",     bundle: .main)
    static let dsSurface        = Color("Surface",        bundle: .main)
    static let dsBorder         = Color("Border",         bundle: .main)
    static let dsTextPrimary    = Color("TextPrimary",    bundle: .main)
    static let dsTextSecondary  = Color("TextSecondary",  bundle: .main)
    // AccentColor picked up automatically via .tint() — do not alias here

    // System-tinted semantics (prefer these over raw colors for chrome)
    static let dsChromeFill     = Color(.systemBackground)
    static let dsGroupedBg      = Color(.systemGroupedBackground)
    static let dsSeparator      = Color(.separator)
    static let dsLabel          = Color(.label)
    static let dsSecondaryLabel = Color(.secondaryLabel)
}
```

**Rule:** on iOS 26, for primary actions on Liquid Glass surfaces, use `.glassEffect(.regular.tint(.accentColor))` rather than filling with accent. See `references/ios/color.md` § Liquid Glass.

### 3. `Theme/Typography.swift`

```swift
import SwiftUI

enum DS {
    enum Font {
        // Display — custom from designlib font_pair.heading
        static func display(_ size: Size, weight: Weight = .bold) -> SwiftUI.Font {
            .custom("<heading.family>", size: size.rawValue, relativeTo: size.textStyle)
                .weight(weight)
        }
        // Body — prefer SF if font_pair says "system"; else custom
        static func body(_ size: Size, weight: Weight = .regular) -> SwiftUI.Font {
            .custom("<body.family>", size: size.rawValue, relativeTo: size.textStyle)
                .weight(weight)
        }
        // Mono — SF Mono usually; only override if font_pair.mono specified
        static func mono(_ size: Size) -> SwiftUI.Font {
            .system(size: size.rawValue, design: .monospaced)
        }

        enum Size: CGFloat {
            case caption2 = 11, caption = 12, footnote = 13, subheadline = 15
            case callout = 16, body = 17, headline = 17
            case title3 = 20, title2 = 22, title1 = 28
            case largeTitle = 34, display = 48

            var textStyle: SwiftUI.Font.TextStyle {
                switch self {
                case .caption2: return .caption2
                case .caption:  return .caption
                case .footnote: return .footnote
                case .subheadline: return .subheadline
                case .callout:  return .callout
                case .body, .headline: return .body
                case .title3:   return .title3
                case .title2:   return .title2
                case .title1:   return .title
                case .largeTitle, .display: return .largeTitle
                }
            }
        }
    }
}
```

**Rule:** sizes MUST pass `relativeTo:` so Dynamic Type scales. Fonts without SF fallback break AX users. If `font_pair` says use SF — just use `.system()` and skip `.custom()`. See `references/ios/layout.md` § Dynamic Type.

### 4. `Theme/Spacing.swift`

```swift
extension DS {
    enum Space {
        static let xs: CGFloat  = 4
        static let sm: CGFloat  = 8
        static let md: CGFloat  = 12
        static let lg: CGFloat  = 16   // system default
        static let xl: CGFloat  = 20
        static let xxl: CGFloat = 24
        static let xxxl: CGFloat = 32
        static let huge: CGFloat = 48
    }
    enum Radius {
        static let sm: CGFloat = 6
        static let md: CGFloat = 10   // iOS standard card
        static let lg: CGFloat = 16   // iOS 26 Liquid Glass default
        static let xl: CGFloat = 22
        static let capsule: CGFloat = .infinity
    }
}
```

**Rule:** prefer `.layoutMargins` + `readableContentGuide` from UIKit and `.contentMargins` in SwiftUI over hand-rolled inset math. See `references/ios/layout.md`.

### 5. `Theme/Motion.swift`

```swift
import SwiftUI

extension DS {
    enum Motion {
        // iOS 26 prefers springs over curves everywhere
        static let springSnappy = Animation.spring(response: 0.32, dampingFraction: 0.86)
        static let springBouncy = Animation.spring(response: 0.42, dampingFraction: 0.72)
        static let springCalm   = Animation.spring(response: 0.55, dampingFraction: 0.9)

        // Curve fallbacks (only when you need exact duration control)
        static let durInstant: Double = 0.10
        static let durFast:    Double = 0.16
        static let durNormal:  Double = 0.22
        static let durSlow:    Double = 0.32
        static let easeOutQuart = UnitCurve.bezier(startControlPoint: .init(x: 0.25, y: 1),
                                                    endControlPoint: .init(x: 0.5, y: 1))
    }
}
```

**Rule:** ALWAYS scope `.animation(DS.Motion.springSnappy, value: someState)` to a value, never blanket `.animation(_ :)`. See `references/ios/motion.md`. Respect `@Environment(\.accessibilityReduceMotion)` — don't delete animation, substitute it (cross-fade instead of slide).

### 6. `Theme/Haptics.swift` (include only if `haptic_budget != off`)

```swift
import SwiftUI

extension DS {
    enum Haptic {
        // Prefer SwiftUI sensoryFeedback (iOS 17+) — declarative, throttled by system
        // .sensoryFeedback(.success, trigger: value)
        // .sensoryFeedback(.selection, trigger: index)
        // .sensoryFeedback(.impact(weight: .light), trigger: value)

        // UIKit imperative fallback for iOS < 17
        @available(iOS, deprecated: 17, renamed: "sensoryFeedback")
        static func impact(_ style: UIImpactFeedbackGenerator.FeedbackStyle = .medium) {
            let g = UIImpactFeedbackGenerator(style: style)
            g.prepare()
            g.impactOccurred()
        }
    }
}
```

Haptic budget levels (from interview Q15b):
- **off**: skip this file entirely
- **system-only**: only include `sensoryFeedback` reference in spec — no wrappers
- **curated-moments**: include wrappers for `.success`/`.warning`/`.error`/`.selection`
- **expressive**: add Core Haptics pattern builders (see `references/ios/haptics.md`)

### 7. `AppIcon.appiconset` (iOS 18+) or `AppIcon.icon` (iOS 26 Icon Composer)

- **iOS 18 floor:** ship 3 × 1024×1024 PNGs (Default · Dark · Tinted Grayscale)
- **iOS 26 floor:** build one layered `.icon` in Icon Composer — generates 6 appearances automatically

If floor = iOS 26, generate Icon Composer-friendly layer brief:
- Background layer
- Foreground layer (single glyph, centered, safe margin)
- Highlight layer (optional — specular)

See `references/ios/icons.md` for geometry + appearance rules.

### 8. `design-system.md` — iOS spec

```markdown
# <Product> Design System — iOS

**Generated:** <date>
**iOS floor:** <17 | 18 | 26>
**Framework:** <SwiftUI | SwiftUI + UIKit | UIKit>
**Source:** designlib style=<id> · palette=<id> · font_pair=<id>
**Style family:** <from ios style-families>

## Color

- Asset catalog: `Assets.xcassets/DesignSystem/`
- Swift API: `Color.ds*`
- Semantic: `Color(.label)`, `Color(.systemBackground)` etc.
- AccentColor → `AccentColor.colorset`
- Liquid Glass tint (iOS 26): reserve for primary actions on glass

See `references/ios/color.md`.

## Typography

- API: `DS.Font.display/body/mono(_:weight:)`
- Dynamic Type: all sizes scale relative to `UIFont.TextStyle`
- AX floor: AX5 tested

See `references/ios/layout.md` § Dynamic Type.

## Spacing & Radius

- `DS.Space.xs/sm/md/lg/xl/xxl/xxxl/huge`
- `DS.Radius.sm/md/lg/xl/capsule`

See `references/ios/layout.md`.

## Motion

- `DS.Motion.springSnappy/springBouncy/springCalm`
- Scope animations to values (never blanket)
- Reduce Motion: substitute, don't remove

See `references/ios/motion.md`.

## Haptics

- Budget: <off | system-only | curated-moments | expressive>
- Prefer SwiftUI `.sensoryFeedback` (iOS 17+)

See `references/ios/haptics.md`.

## Platform surfaces enabled

<from interview Q14b>

- [ ] Widgets
- [ ] Live Activities
- [ ] Dynamic Island
- [ ] Lock Screen
- [ ] Control Center
- [ ] App Shortcuts
- [ ] Apple Watch app
- [ ] iPad tiling/menu bar
- [ ] Mac Catalyst
- [ ] visionOS

For each checked: link to the relevant section in `references/ios/ambient-surfaces.md` / `references/ios/ipad.md` / `references/ios/non-iphone-platforms.md`.

## Accessibility floor

- Dynamic Type: AX5
- Increase Contrast: honored via HC asset variants
- Reduce Motion: animation substitution wired
- Reduce Transparency: Materials → solid fills automatically
- VoiceOver: pending per-view audit

## Dials

- DESIGN_VARIANCE: <n>
- MOTION_INTENSITY: <n>
- VISUAL_DENSITY: <n>
```

## Integration order

1. Create `Assets.xcassets/DesignSystem/` and all `.colorset` entries
2. Create `AccentColor.colorset` (or update existing)
3. Add `Theme/` group with `Color+DesignSystem.swift`, `Typography.swift`, `Spacing.swift`, `Motion.swift`, optionally `Haptics.swift`
4. Configure `.tint(.accentColor)` at app root (or per scene)
5. Set custom font loading in `Info.plist` → `UIAppFonts`
6. Write `design-system.md`
7. Verify on simulator with Dynamic Type slider maxed + Dark Mode + Increase Contrast

## Do NOT

- Hardcode hex in views — always `Color.ds*` or semantic `Color(.label)`
- Use `Color.white` / `Color.black` for chrome — use semantic (`Color(.systemBackground)`, `Color(.label)`)
- Apply `.glassEffect` everywhere on iOS 26 — reserve for navigation chrome + primary actions
- Delete animations for Reduce Motion — substitute with cross-fade
- Skip the P3 color space declaration
- Use custom fonts without `relativeTo:` — breaks Dynamic Type
