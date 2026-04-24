---
name: color
description: iOS color system reference (semantic colors, AccentColor, Liquid Glass tint, WCAG contrast)
platform: ios
---

# iOS color system reference (iOS 18 & iOS 26)

## iOS color rules — moved from SKILL.md in v1.2

- Prefer semantic `Color(.label)` / `Color(.systemBackground)` for chrome
- Brand via `AccentColor.colorset` + `.tint(.accentColor)`
- Dark/light/high-contrast variants in asset catalog
- iOS 26: `.glassEffect(.regular.tint(...))` for primary actions on glass; push brand into content layer otherwise

A dense, scannable developer reference for Apple's color system on iOS. Covers UIKit and SwiftUI APIs on iOS 18, plus Liquid Glass additions in iOS 26. Use it to pick the right semantic color, understand dynamic resolution, wire up asset catalogs, meet WCAG contrast, and adopt Liquid Glass correctly.

**BLUF:** Prefer semantic colors (`label`, `systemBackground`, `secondarySystemGroupedBackground`) over hard-coded RGB; set your brand via the `AccentColor` asset and `.tint(_:)`; let dynamic `UIColor`/`Color` handle light/dark/high-contrast/elevation; never use pure `.black`/`.white` for chrome; on iOS 26 push brand color into the content layer and reserve `.glassEffect(.regular.tint(…))` for primary actions on glass.

---

## 1. Semantic colors (UI element colors)

Every color in this section is a **dynamic** `UIColor`: it resolves differently at runtime based on `UITraitCollection.userInterfaceStyle` (light/dark), `accessibilityContrast` (normal/high), and `userInterfaceLevel` (base/elevated). **Do not cache resolved RGB values.** All were introduced in iOS 13 and are unchanged through iOS 18.

SwiftUI has **no native accessor** (no `Color.label`, no `Color.systemBackground`). Always bridge: `Color(.label)` or `Color(uiColor: .label)` (iOS 15+).

### 1.1 Label colors — foreground text hierarchy

| Token | UIKit | SwiftUI bridge | Role | Light (alpha) | Dark (alpha) |
|---|---|---|---|---|---|
| `label` | `UIColor.label` | `Color(.label)` | Primary text: titles, body copy, cell titles | `#000000` / 1.0 | `#FFFFFF` / 1.0 |
| `secondaryLabel` | `UIColor.secondaryLabel` | `Color(.secondaryLabel)` | Subtitles, supporting text, metadata | `#3C3C43` / 0.60 | `#EBEBF5` / 0.60 |
| `tertiaryLabel` | `UIColor.tertiaryLabel` | `Color(.tertiaryLabel)` | Disabled-adjacent, third-level info | `#3C3C43` / 0.30 | `#EBEBF5` / 0.30 |
| `quaternaryLabel` | `UIColor.quaternaryLabel` | `Color(.quaternaryLabel)` | Watermarks, very subtle hints | `#3C3C43` / 0.18 | `#EBEBF5` / 0.18 |

Hierarchy: **primary → secondary → tertiary → quaternary** is a descending alpha ramp on a single hue so it composites correctly over any background including fills. Do not re-implement with your own hex values — they'd miss the alpha blending.

### 1.2 Text input & link

| Token | UIKit | SwiftUI bridge | Role | Notes |
|---|---|---|---|---|
| `placeholderText` | `UIColor.placeholderText` | `Color(.placeholderText)` | `UITextField`, `UITextView`, `UISearchBar` placeholder | Numerically identical to `tertiaryLabel` but semantically distinct — prefer this for placeholders. |
| `link` | `UIColor.link` | `Color(.link)` | Hyperlinks in attributed strings and data detectors | Tracks `systemBlue` (`#007AFF` light / `#0A84FF` dark). |

### 1.3 Separators

| Token | UIKit | SwiftUI bridge | Use |
|---|---|---|---|
| `separator` | `UIColor.separator` | `Color(.separator)` | Hairline dividers over standard backgrounds (translucent: `#3C3C43` @ 0.29 light / `#545458` @ 0.60 dark). |
| `opaqueSeparator` | `UIColor.opaqueSeparator` | `Color(.opaqueSeparator)` | Dividers over photos / non-standard backgrounds requiring full opacity (`#C6C6C8` light / `#38383A` dark). |

Under **Increase Contrast**, `separator` effectively becomes `opaqueSeparator`.

### 1.4 Fill colors — over content

Designed to **overlay** opaque content (switches, pill shapes, search-field fills). They are intentionally translucent so they blend with whatever's underneath. Don't use them as full-screen backgrounds.

| Token | UIKit | SwiftUI bridge | Suggested shape thickness |
|---|---|---|---|
| `systemFill` | `UIColor.systemFill` | `Color(.systemFill)` | Largest / thickest: big rounded rects, track fills |
| `secondarySystemFill` | `UIColor.secondarySystemFill` | `Color(.secondarySystemFill)` | Medium |
| `tertiarySystemFill` | `UIColor.tertiarySystemFill` | `Color(.tertiarySystemFill)` | Thin: input/search fills |
| `quaternarySystemFill` | `UIColor.quaternarySystemFill` | `Color(.quaternarySystemFill)` | Very thin / large area |

Rule of thumb: **bigger shape → thinner fill**. Base color is always neutral gray at varying alpha (`#787880` family).

### 1.5 Standard (plain) backgrounds — single-plane UI

Use for plain tables, edge-to-edge scroll views, standard screens where content sits on the same plane as the background.

| Token | Light | Dark (base) | Dark (elevated) |
|---|---|---|---|
| `systemBackground` | `#FFFFFF` | `#000000` | `#1C1C1E` |
| `secondarySystemBackground` | `#F2F2F7` | `#1C1C1E` | `#2C2C2E` |
| `tertiarySystemBackground` | `#FFFFFF` | `#2C2C2E` | `#3A3A3C` |

### 1.6 Grouped backgrounds — inset-grouped / settings-style UI

Use for grouped/inset-grouped `UITableView`, Settings-style screens, "card on gray" layouts. Note that in **light mode the first two are inverted** relative to the plain stack: the page is gray, the cells are white.

| Token | Light | Dark (base) |
|---|---|---|
| `systemGroupedBackground` | `#F2F2F7` | `#000000` |
| `secondarySystemGroupedBackground` | `#FFFFFF` | `#1C1C1E` |
| `tertiarySystemGroupedBackground` | `#F2F2F7` | `#2C2C2E` |

**Decision tree — which background do I use?**

```
Does content read as separate "cards" visually?
├─ YES  → systemGroupedBackground (page)
│         └─ secondarySystemGroupedBackground (card/cell)
│              └─ tertiarySystemGroupedBackground (nested content)
└─ NO   → systemBackground (main view)
          └─ secondarySystemBackground (grouped subregion)
               └─ tertiarySystemBackground (nested content)
```

### 1.7 UIKit & SwiftUI snippets

```swift
// UIKit — inset-grouped table
let table = UITableView(frame: .zero, style: .insetGrouped)
table.backgroundColor       = .systemGroupedBackground
cell.backgroundColor        = .secondarySystemGroupedBackground
cell.textLabel?.textColor   = .label
cell.detailTextLabel?.textColor = .secondaryLabel
table.separatorColor        = .separator

textField.attributedPlaceholder = NSAttributedString(
    string: "Search",
    attributes: [.foregroundColor: UIColor.placeholderText])
```

```swift
// SwiftUI — plain content screen
ScrollView {
    VStack(alignment: .leading, spacing: 8) {
        Text("Title").font(.title).foregroundStyle(Color(.label))
        Text("Subtitle").foregroundStyle(Color(.secondaryLabel))
        Text("Footnote").foregroundStyle(Color(.tertiaryLabel))
    }
    .padding()
    .background(Color(.secondarySystemBackground), in: .rect(cornerRadius: 12))
}
.background(Color(.systemBackground))
```

### 1.8 Anti-patterns

```swift
// ❌ Does not adapt to dark mode
label.textColor      = .black
view.backgroundColor = .white
// ✅
label.textColor      = .label
view.backgroundColor = .systemBackground

// ❌ Hard-coded hex loses elevation, high-contrast, language-of-the-platform
view.backgroundColor = UIColor(red: 0.95, green: 0.95, blue: 0.97, alpha: 1)
// ✅
view.backgroundColor = .secondarySystemBackground

// ❌ SwiftUI: assuming a Color.label exists
Text("x").foregroundStyle(Color.label)   // does not compile
// ✅
Text("x").foregroundStyle(Color(.label))
```

---

## 2. System colors (named palette)

Semantic hues available on both `UIColor` and SwiftUI `Color`. All are **dynamic** (light/dark variants baked in). `systemMint`, `systemCyan`, and `systemBrown` were added in **iOS 15**; `systemTeal` was subtly shifted darker in iOS 15 as `systemCyan` took over its previous hue. Apple warns in HIG: **do not hard-code exact RGB values**; resolve through the token so each OS release can retune.

### 2.1 Tint hues

| Token | UIKit / SwiftUI | HIG meaning / convention | Light | Dark | Apple's canonical uses |
|---|---|---|---|---|---|
| `systemRed` / `.red` | Destructive, error, record | `#FF3B30` | `#FF453A` | Delete, Calendar, record indicators |
| `systemOrange` / `.orange` | Warning, attention (non-critical) | `#FF9500` | `#FF9F0A` | Find My warnings, Podcasts |
| `systemYellow` / `.yellow` | Caution, highlight | `#FFCC00` | `#FFD60A` | Notes key color |
| `systemGreen` / `.green` | Success, go, accept | `#34C759` | `#30D158` | Phone accept, Fitness, Messages send |
| `systemMint` (iOS 15+) / `.mint` | Fresh secondary-positive | `~#00C7BE` | `~#66D4CF` | Fitness rings, chart series |
| `systemTeal` / `.teal` | Cool accent / info | `~#30B0C7` (post-iOS-15) | `~#40C8E0` | Maps, Weather |
| `systemCyan` (iOS 15+) / `.cyan` | Cool info/accent | `~#32ADE6` | `~#64D2FF` | Podcasts, Home |
| `systemBlue` / `.blue` | **Default interactive / tint** | `#007AFF` | `#0A84FF` | System default tint; Messages |
| `systemIndigo` / `.indigo` | Rich accent | `#5856D6` | `#5E5CE6` | Home app |
| `systemPurple` / `.purple` | Premium, creative | `#AF52DE` | `#BF5AF2` | Podcasts, Music |
| `systemPink` / `.pink` | Personal, lively | `#FF2D55` | `#FF375F` | Music, heart-rate |
| `systemBrown` (iOS 15+) / `.brown` | Earthy / utility neutral | `~#A2845E` | `~#AC8E68` | Tips, Voice Memos |

### 2.2 System gray scale

All six are neutral grays; choose by **contrast with the background**. `systemGray` is the anchor (same value both modes). Each successive number trends toward the current `systemBackground` — **lighter** in light mode, **darker** in dark mode — so the same token produces the same relative prominence in either mode.

| Token | Light | Dark |
|---|---|---|
| `systemGray` | `#8E8E93` | `#8E8E93` |
| `systemGray2` | `#AEAEB2` | `#636366` |
| `systemGray3` | `#C7C7CC` | `#48484A` |
| `systemGray4` | `#D1D1D6` | `#3A3A3C` |
| `systemGray5` | `#E5E5EA` | `#2C2C2E` |
| `systemGray6` | `#F2F2F7` | `#1C1C1E` |

Uses: `systemGray` for legible secondary icons/text; `systemGray3`–`4` for inactive controls/disabled glyphs; `systemGray5`–`6` for subtle separators/card backgrounds.

### 2.3 Accessibility / contrast notes

System hues are tuned for **consistency and brand coherence, not text legibility**. Tested against `systemBackground` in **light** mode:

| System hue | Approx. contrast | AA body (4.5:1) | AA large (3:1) |
|---|---|---|---|
| `systemYellow` | ~1.5:1 | ❌ | ❌ |
| `systemGreen` | ~1.9:1 | ❌ | ❌ |
| `systemOrange` | ~2.4:1 | ❌ | ❌ |
| `systemBrown` | ~3.5:1 | ❌ | ✅ |
| `systemRed` | ~3.8:1 | ❌ | ✅ |
| `systemPurple` | ~3.7:1 | ❌ | ✅ |
| `systemPink` | ~4.2:1 | ❌ | ✅ |
| `systemBlue` | ~4.0:1 | ❌ (just) | ✅ |
| `systemIndigo` | ~5.4:1 | ✅ | ✅ |

**Practical guidance:** use system hues for tints, icons, and non-text accents — not for body text. Never convey state by color alone.

---

## 3. Tint / accent color

### 3.1 Propagation model

**UIKit.** `UIView.tintColor` walks the superview chain; the first non-default ancestor wins. The effective root is the `UIWindow` (itself a `UIView`). Final fallback: the `AccentColor` asset or `systemBlue`. Setting `tintColor = nil` restores inheritance. `tintAdjustmentMode = .dimmed` dims all inherited tints (used automatically when an alert/sheet is over a view). Override `tintColorDidChange()` in custom views to re-render colors derived from the tint.

**SwiftUI.** `.tint(_:)` (iOS 15+) is the preferred modifier; it applies to the view and descendants and affects `Button`, `Toggle`, `Slider`, `Picker`, `ProgressView`, `Link`, selection highlights, `NavigationLink` chevrons, segmented pickers, tab-bar selected items. `.accentColor(_:)` is **deprecated in iOS 16**. `.tint(_:)` does **not** recolor plain `Text` — use `.foregroundStyle(.tint)` for that.

Resolution order: `view.tintColor → superview chain → UIWindow → AccentColor asset → systemBlue`.

### 3.2 Asset-catalog setup (step by step)

1. Open (or create) `Assets.xcassets`.
2. Right-click → **New Color Set** → name it exactly `AccentColor`. (SwiftUI templates create this for you.)
3. In Attributes Inspector set **Appearances: Any, Dark** (or Any, Light, Dark).
4. Optional: toggle **High Contrast** to add accessibility variants (up to 6 slots).
5. For each slot pick a color (Floating Point, 8-bit, or `#RRGGBB`) and color space (sRGB or Display P3 — see §5).
6. Verify **Build Settings → Asset Catalog Compiler – Options → Global Accent Color Name** is `AccentColor`. Xcode injects `NSAccentColorName` into the built `Info.plist`. **Do not set `Info.plist` manually** — there is no `UIAccentColorName` key; `NSAccentColorName` is the correct (shared) key.

### 3.3 Control-level propagation

| Control | UIKit knob | SwiftUI |
|---|---|---|
| `UIButton` (system/filled/tinted/plain) | `tintColor` / Configuration base colors | `Button` inherits `.tint` |
| `UISwitch` | `onTintColor` (on thumb), `tintColor` (off border) | `Toggle` uses `.tint` |
| `UISlider` | `minimumTrackTintColor`, `maximumTrackTintColor`, `thumbTintColor` | `Slider` uses `.tint` |
| `UINavigationBar` | `tintColor` for back chevron & bar items; `UINavigationBarAppearance` for background | `.tint()` on `NavigationStack` |
| `UITabBar` | `tintColor` = selected item; `UITabBarAppearance` for backgrounds | `TabView` uses `.tint` |
| `UISegmentedControl` | `selectedSegmentTintColor` + `tintColor` | `Picker(.segmented)` uses `.tint` |
| `UIProgressView` | `progressTintColor`, `trackTintColor` | `ProgressView` uses `.tint` |
| `UIPageControl` | `pageIndicatorTintColor`, `currentPageIndicatorTintColor` | — |
| `UIAlertController` | Often fails to inherit AccentColor — fix with UIAppearance (below) | `.alert` inherits |

```swift
// Known fix: UIAlertController ignoring the AccentColor asset
UIView.appearance(whenContainedInInstancesOf: [UIAlertController.self])
    .tintColor = UIColor(named: "AccentColor")
```

### 3.4 Code

```swift
// UIKit — app-wide tint
func scene(_ scene: UIScene, willConnectTo s: UISceneSession,
           options: UIScene.ConnectionOptions) {
    guard let ws = scene as? UIWindowScene else { return }
    let window = UIWindow(windowScene: ws)
    window.tintColor = UIColor(named: "AccentColor")
    window.rootViewController = RootVC()
    self.window = window; window.makeKeyAndVisible()
}
```

```swift
// SwiftUI — app-wide + scoped overrides
@main struct MyApp: App {
    var body: some Scene {
        WindowGroup { ContentView().tint(.brandPrimary) }
    }
}

VStack {
    Button("Save") { }              // inherits .brandPrimary
    Toggle("On", isOn: $on).tint(.green)   // local override
}
.tint(.indigo)                       // subtree override
```

### 3.5 Anti-patterns

```swift
// ❌ Deprecated (iOS 16)
.accentColor(.purple)
// ✅
.tint(.purple)

// ❌ Setting NSAccentColorName manually in Info.plist
// ✅ Use the Xcode build setting "Global Accent Color Name"
```

---

## 4. Dynamic colors (resolution at runtime)

### 4.1 Trait dimensions that affect color

| Trait | Type | Values | Source |
|---|---|---|---|
| `userInterfaceStyle` | `UIUserInterfaceStyle` | `.light`, `.dark`, `.unspecified` | System appearance or `overrideUserInterfaceStyle` |
| `accessibilityContrast` | `UIAccessibilityContrast` | `.normal`, `.high` | Settings → Accessibility → Display & Text Size → **Increase Contrast** |
| `userInterfaceLevel` | `UIUserInterfaceLevel` | `.base`, `.elevated` | Modal sheets, popovers, alerts auto-elevate |
| `displayGamut` | `UIDisplayGamut` | `.SRGB`, `.P3` | Display hardware (iPhone 7+ / iPad Pro are P3) |

### 4.2 `UIColor(dynamicProvider:)` — iOS 13+

```swift
let adaptive = UIColor { trait in
    switch (trait.userInterfaceStyle,
            trait.accessibilityContrast,
            trait.userInterfaceLevel) {
    case (.dark, .high, _):       return UIColor(red: 1.00, green: 0.95, blue: 0.60, alpha: 1)
    case (.dark, _, .elevated):   return UIColor(white: 0.22, alpha: 1)
    case (.dark, _, _):           return UIColor(white: 0.15, alpha: 1)
    case (.light, .high, _):      return UIColor(white: 0.00, alpha: 1)
    case (.light, _, .elevated):  return .white
    default:                      return UIColor(white: 0.97, alpha: 1)
    }
}
```

The closure is re-invoked whenever the trait environment changes.

### 4.3 Explicit runtime resolution

`CGColor` is **not** dynamic. If you assign to `CALayer.borderColor`, `CALayer.backgroundColor`, or a `CATextLayer`, resolve manually and refresh on trait changes:

```swift
layer.borderColor = UIColor.separator
    .resolvedColor(with: traitCollection).cgColor
```

Override `traitCollectionDidChange` (iOS ≤16) or register with `registerForTraitChanges` (iOS 17+):

```swift
// iOS 17+ — preferred, traitCollectionDidChange is deprecated
registerForTraitChanges(
    [UITraitUserInterfaceStyle.self,
     UITraitAccessibilityContrast.self,
     UITraitUserInterfaceLevel.self]
) { (self: Self, previous) in
    self.refreshLayerColors()
}
```

`hasDifferentColorAppearance(comparedTo:)` is a quick pre-check across style / gamut / contrast / level.

### 4.4 SwiftUI environment

| Key | Values |
|---|---|
| `@Environment(\.colorScheme)` | `.light`, `.dark` |
| `@Environment(\.colorSchemeContrast)` | `.standard`, `.increased` |
| `@Environment(\.accessibilityReduceTransparency)` | `Bool` |
| `@Environment(\.self)` | Pass to `Color.resolve(in:)` (iOS 17+) |

SwiftUI has **no native** `Color(dynamicProvider:)`. Bridge through UIColor:

```swift
extension Color {
    init(light: UIColor, dark: UIColor) {
        self = Color(uiColor: UIColor { $0.userInterfaceStyle == .dark ? dark : light })
    }
}
```

`Color.resolve(in:)` (iOS 17+) returns a concrete `Color.Resolved` (Float RGBA) — useful when you need raw components:

```swift
@Environment(\.self) private var env
let resolved = Color.accentColor.resolve(in: env)  // Color.Resolved
```

### 4.5 Overriding appearance

| API | Scope |
|---|---|
| `UIWindow.overrideUserInterfaceStyle = .dark` | Window + presented content |
| `UIViewController.overrideUserInterfaceStyle = .dark` | VC + view hierarchy + child VCs |
| `UIView.overrideUserInterfaceStyle = .dark` | Subtree only; child VCs unaffected |
| `Info.plist UIUserInterfaceStyle = Light` | Opts out of dark mode app-wide (discouraged) |
| SwiftUI `.preferredColorScheme(.dark)` | Scene/view tree |

---

## 5. Color sets in Asset Catalog

### 5.1 Create a set

1. File → New → File → **Asset Catalog** (if not already present).
2. In the catalog: bottom-left **+** → **Color Set**, or right-click sidebar → New Color Set.
3. Rename (avoid collisions with system names like `red`, `label`, `green` — Xcode 15+ warns).
4. Select the set → Attributes Inspector.

### 5.2 Appearance matrix

- **Appearances**: `None` / `Any, Dark` / `Any, Light, Dark`.
- **High Contrast** toggle: doubles the slots (Any/Light/Dark × Normal/High Contrast = up to 6).

`Any` is the legacy/fallback slot (used on iOS 12 or when trait is unspecified) — usually mirror it to Light.

### 5.3 Color space

| Space | When to use |
|---|---|
| **sRGB** | Default. Smaller, identical across all displays, maximum compatibility. |
| **Display P3** | Saturated brand colors; photography/video chrome; visibly richer on iPhone 7+, iPad Pro, M-series Macs. App Slicing delivers the right variant per device. |
| Extended Range sRGB / Extended Linear sRGB / Gray Gamma 2.2 / Extended Linear Gray | Specialty: HDR interchange, Metal/CoreGraphics pipelines, grayscale. |

Rule: **sRGB unless your brand color genuinely uses values outside sRGB gamut.**

### 5.4 Referencing in code

```swift
// Stringly-typed (works on every iOS since 11)
let c  = UIColor(named: "BrandPrimary")                       // Optional<UIColor>
let c2 = UIColor(named: "BrandPrimary", in: .module,
                 compatibleWith: traitCollection)             // resolves at call site
Text("Hi").foregroundStyle(Color("BrandPrimary"))
```

```swift
// Xcode 15+ generated asset symbols (default ON).
// Xcode writes GeneratedAssetSymbols.swift with:
//   extension ColorResource { static let brandPrimary = ... }
//   extension SwiftUI.Color { static let brandPrimary = Color(.brandPrimary) }
//   extension UIKit.UIColor { static let brandPrimary = UIColor(resource: .brandPrimary) }
view.backgroundColor = UIColor(resource: .brandPrimary)       // iOS 17+ initializer
view.backgroundColor = .brandPrimary                          // extension shortcut
Text("Hi").foregroundStyle(.brandPrimary)                     // SwiftUI
```

```swift
// Extension pattern (pre-Xcode-15 / SPM public exposure)
extension UIColor { static let brand = UIColor(named: "BrandPrimary")! }
extension Color   { static let brand = Color("BrandPrimary") }
```

Named colors are designer-editable, automatically pick up dark/contrast/gamut variants, and give compile-time type safety via generated symbols. Generated symbols are `internal` by default — **Swift Packages** still require a manual `public` wrapper to export.

### 5.5 Anti-patterns

```swift
// ❌ Runtime-undefined if the asset is missing
UIColor(named: "Brand")!            // crashes in production
// ✅ Generated symbol: compile-time checked, no force-unwrap
UIColor(resource: .brand)

// ❌ Naming a color asset "red" — collides with generated symbol
// ✅ Use branded names: "BrandPrimary", "SurfaceElevated", "OnPrimary"
```

---

## 6. Elevation in dark mode

### 6.1 Philosophy

Apple's iOS dark-mode system uses **color, not shadows**, to imply elevation. From WWDC 2019 Session 214 / "Implementing Dark Mode on iOS": the base level is dimmer and recedes; the elevated level is brighter and advances. Shadows disappear on black — lighter grays do not.

This is the opposite of Material Design, which layers translucent whites and stacks shadows.

### 6.2 Why pure `#000000` chrome is usually wrong

- **No depth headroom** — a modal above black cannot elevate visually if both are black.
- **Harsh edges** against colorful content cause eye fatigue and banding (Mach bands on gradients).
- **OLED smearing** during scrolling is more visible against true black.
- **Low-vision legibility** — Apple's "Dark Interface" evaluation criteria warn gray-on-black is harder to read for low-vision users.

Apple therefore ships a gray ladder for chrome: `#1C1C1E`, `#2C2C2E`, `#3A3A3C`, `#48484A`, `#636366`, `#8E8E93`. Only the absolute base `systemBackground` / `systemGroupedBackground` is `#000000` — chrome above it lifts.

### 6.3 Base vs elevated appearance

`UITraitCollection.userInterfaceLevel` flips from `.base` to `.elevated` automatically in modally presented content (sheets, popovers, alerts, iPad form sheets). Every semantic background color then resolves **one step lighter** in dark mode, while labels stay constant. This is why a modal sheet over a dark screen appears as a lifted gray card with no extra code.

Asset Catalogs **cannot** express elevation directly; to react to elevation in a custom color use a `UIColor(dynamicProvider:)` closure.

### 6.4 Materials

**SwiftUI (iOS 15+).** Adaptive materials, ordered thinnest → thickest:

- `.ultraThinMaterial`, `.thinMaterial`, `.regularMaterial`, `.thickMaterial`, `.ultraThickMaterial`, `.bar`

```swift
Text("Visit Tokyo")
    .padding()
    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
```

**UIKit.** `UIBlurEffect.Style` adaptive family (iOS 13+): `.systemUltraThinMaterial`, `.systemThinMaterial`, `.systemMaterial`, `.systemThickMaterial`, `.systemChromeMaterial`. Each has fixed `Light`/`Dark` variants if you need to pin appearance.

```swift
let blur = UIBlurEffect(style: .systemThinMaterial)
let view = UIVisualEffectView(effect: blur)

// Nested vibrancy — text reads correctly through blur
let vibrancy = UIVibrancyEffect(blurEffect: blur, style: .secondaryLabel)
let vview    = UIVisualEffectView(effect: vibrancy)
view.contentView.addSubview(vview)
vview.contentView.addSubview(label)   // add labels to the inner contentView
```

Vibrancy styles: `.label`, `.secondaryLabel`, `.tertiaryLabel`, `.quaternaryLabel`, `.fill`, `.secondaryFill`, `.tertiaryFill`, `.separator`.

### 6.5 Correct vs incorrect

```swift
// ✅ Adapts across light/dark/elevation automatically
view.backgroundColor = .systemBackground
cell.backgroundColor = .secondarySystemGroupedBackground

// ❌ Flat UI in modals, no elevation response
view.backgroundColor = .black
label.textColor      = .white
```

---

## 7. Color contrast (WCAG)

### 7.1 Thresholds

| Level | Normal text | Large text (≥18pt, or ≥14pt bold) | Non-text UI |
|---|---|---|---|
| **AA** | 4.5:1 | 3:1 | 3:1 |
| **AAA** | 7:1 | 4.5:1 | — |

Apple's App Store Connect "Sufficient Contrast" evaluation cites AA (4.5:1 / 3:1) and requires it in **both** light and dark modes.

### 7.2 Semantic pairings — compliance at a glance

| Pairing | Light | Dark | AA normal | AAA |
|---|---|---|---|---|
| `label` on `systemBackground` | ~21:1 | ~21:1 | ✅ | ✅ |
| `secondaryLabel` on `systemBackground` | ~4.54:1 | ~4.59:1 | ✅ (just) | ❌ |
| `tertiaryLabel` on `systemBackground` | ~2.3:1 | ~2.3:1 | ❌ | ❌ |
| `quaternaryLabel` on `systemBackground` | ~1.5:1 | ~1.5:1 | ❌ | ❌ |
| `placeholderText` on `systemBackground` | ~2.3:1 | ~2.3:1 | ❌ (matches tertiary) | ❌ |

`secondaryLabel` is **on the edge of AA**. In elevated modals the background becomes `#1C1C1E` — verify in context. `tertiaryLabel` and `quaternaryLabel` are intentional "inactive / decorative" colors exempted by WCAG 1.4.3 from contrast requirements; do not use them for readable body copy.

### 7.3 System hues on `systemBackground`

Almost all system tints **fail AA for body text** on white (see §2.3 table). `systemIndigo` passes; `systemRed`/`systemBlue`/`systemPurple`/`systemPink`/`systemBrown` pass AA only for large text; `systemYellow`/`systemGreen`/`systemOrange`/`systemTeal`/`systemCyan`/`systemMint` fail both.

### 7.4 Increase Contrast setting

Triggered at **Settings → Accessibility → Display & Text Size → Increase Contrast**. Effects:

- `UITraitCollection.accessibilityContrast == .high` / SwiftUI `colorSchemeContrast == .increased`.
- Tints darken in light mode, brighten in dark mode.
- `separator` behaves as `opaqueSeparator` (solid).
- Asset Catalog **High Contrast** slots on your custom sets are selected automatically.

### 7.5 Tools

- **Xcode Accessibility Inspector → Audit** flags insufficient contrast with WCAG math.
- **Environment Overrides** button in Xcode's debug bar toggles light/dark/contrast/sizes at runtime.
- **Paciello Colour Contrast Analyser**, **Stark** (Figma/browser/macOS), **WebAIM Contrast Checker**, **Contrast.app**, **Sim Daltonism** (colorblind simulation).

Always test the four permutations: **Light / Dark × Normal / Increase Contrast**.

---

## 8. SwiftUI vs UIKit APIs

### 8.1 Color instantiation

| Purpose | UIKit | SwiftUI (iOS 18) |
|---|---|---|
| Semantic system color | `UIColor.systemBackground` | `Color(.systemBackground)` / `Color(uiColor: .systemBackground)` |
| Named asset | `UIColor(named: "Brand")` | `Color("Brand")` |
| Generated asset symbol (Xcode 15+) | `UIColor(resource: .brand)` / `.brand` | `Color(.brand)` / `.brand` |
| RGB | `UIColor(red: … alpha: …)` | `Color(red: … )` |
| Dynamic 3-dimension | `UIColor { traits in … }` | Bridge `Color(uiColor: UIColor { … })` |
| Primary label (semantic) | `UIColor.label` | `Color(.label)` (absolute) **or** `Color.primary` (relative ShapeStyle) |

**Critical distinction.** `Color.primary` / `Color.secondary` are `HierarchicalShapeStyle` values that resolve **relative to the current foreground** (so they dim whatever foreground is set above). `Color(.label)` / `Color(.secondaryLabel)` are **absolute semantic RGBAs** that always produce the iOS system gray family regardless of ancestor `foregroundStyle`.

```swift
VStack {
    Text("A").foregroundStyle(.secondary)             // dimmed red (relative)
    Text("B").foregroundStyle(Color(.secondaryLabel)) // iOS gray (absolute)
}
.foregroundStyle(.red)
```

### 8.2 Tint / accent

| API | iOS | Status |
|---|---|---|
| `view.tintColor = …` | all | UIKit canonical |
| `UIColor.tintColor` | 15+ | Resolver for current view's tint |
| `.accentColor(_:)` | 13–15 | **Deprecated iOS 16** |
| `.tint(_:)` | 15+ | Preferred |
| `.tint(ShapeStyle)` overload | 16+ | Accepts hierarchical/material styles |

### 8.3 Hierarchical ShapeStyle

Static levels of the current foreground:

| Style | iOS | Role |
|---|---|---|
| `.primary` | 15+ | Main text, titles |
| `.secondary` | 15+ | Subtitles, captions, metadata |
| `.tertiary` | 15+ | Disabled/placeholder |
| `.quaternary` | 15+ | Subtle decoration |
| `.quinary` | **16+** | Barely-visible backgrounds, separators |

iOS 17+ also allows **instance** hierarchical styles on any `ShapeStyle` (e.g., `Color.red.tertiary`, `.tint.secondary`, `.background.secondary`). Use these for layered backgrounds and tinted chart series.

### 8.4 `foregroundStyle` vs `foregroundColor`

| Modifier | iOS | Accepts | Status |
|---|---|---|---|
| `.foregroundColor(Color)` | 13+ | Only `Color` | **Deprecated iOS 17** |
| `.foregroundStyle(S: ShapeStyle)` | 15+ | Any ShapeStyle (Color, gradient, material, hierarchical) | Preferred |
| `.foregroundStyle(primary, secondary [, tertiary])` | 16+ | Multi-tone SF Symbols | Preferred for palette symbols |

```swift
// ✅ Modern
Text("Subtle").foregroundStyle(.secondary)
Text("Glass").foregroundStyle(.ultraThinMaterial)
Text("Grad").foregroundStyle(
    LinearGradient(colors: [.red, .orange],
                   startPoint: .leading, endPoint: .trailing))
Image(systemName: "exclamationmark.triangle.fill")
    .foregroundStyle(.yellow, .red)   // two-tone

// ❌ Deprecated — also can't express gradients or materials
Text("Hello").foregroundColor(.red)
```

### 8.5 Consolidated comparison

| Concern | UIKit | SwiftUI (iOS 18) |
|---|---|---|
| Dark mode check | `traitCollection.userInterfaceStyle == .dark` | `@Environment(\.colorScheme)` |
| Contrast check | `traitCollection.accessibilityContrast == .high` | `@Environment(\.colorSchemeContrast)` |
| Elevation check | `traitCollection.userInterfaceLevel == .elevated` | *No direct API*; wrap a `UIViewRepresentable` |
| Override appearance | `overrideUserInterfaceStyle = .dark` | `.preferredColorScheme(.dark)` |
| Material | `UIBlurEffect(style: .systemThinMaterial)` | `.background(.thinMaterial)` |
| Vibrancy | Nested `UIVibrancyEffect` | Automatic when using materials + hierarchical styles |
| Refresh CGColor on trait change | `traitCollectionDidChange` / `registerForTraitChanges` | Use `Color` ShapeStyle; resolved in layout |

---

## 9. Brand color integration

### 9.1 As the app accent

Define one `AccentColor` set with `Any / Dark` + optional `High Contrast` variants. Set it once (`.tint(.brandPrimary)` / `window.tintColor`) and every standard control inherits.

**Pros:** single source of truth; zero-cost brand consistency; automatic dark/contrast/gamut adaptation; iOS 26 feeds the same accent into Liquid Glass tinting.

**Cons:** conflicts with semantic meaning (red/green/orange brand vs destructive/success/warning); must test every control; widgets in **Tinted Rendering Mode** (iOS 18+) collapse accent-colored assets to white unless you use `.widgetAccentable()`.

### 9.2 As foreground text

Must meet WCAG AA (4.5:1 body, 3:1 large) against every background you'll place it on, in both modes. A saturated "logo blue" like `#0A4E9C` that passes on white typically drops below 2:1 on dark `systemBackground` (`#000`). Solution: **ship a lighter dark variant** — this is exactly what Apple does (`systemBlue` light `#007AFF` / dark `#0A84FF`).

### 9.3 As background

Pick foreground by luminance: `.white` on fills with relative luminance below ~0.5; `.black`/`.primary` otherwise. Works well for hero headers, empty states, promotional cards, launch/splash, CTA fills. Avoid as full-screen backdrop for long-form text.

### 9.4 When brand fails contrast — five strategies

1. **Split tokens.** Keep `Brand` for decoration, define a separate `BrandText` (darkened or lightened) that passes AA.
2. **Asset Catalog variants.** Add `Dark`, `Any High Contrast`, `Dark High Contrast` slots.
3. **Semantic + tint overlay.** Brand tints a semantic fill rather than replacing it.
4. **Accent-only adoption.** Brand only for `.tint()`, selection, chevrons; text uses `.primary`/`.secondary`.
5. **Non-text only.** Logos, illustrations, badges, progress bars — "non-text UI" needs only 3:1.

### 9.5 Code — accessible brand variants

```swift
// Four-slot asset: Any / Dark / Any-HC / Dark-HC
extension Color {
    static let brandPrimary   = Color("BrandPrimary")      // auto-adapts
    static let brandOnPrimary = Color("BrandOnPrimary")    // foreground pair
}

struct HeroCard: View {
    var body: some View {
        Text("Welcome")
            .font(.largeTitle.bold())
            .foregroundStyle(.brandOnPrimary)
            .padding()
            .frame(maxWidth: .infinity)
            .background(Color.brandPrimary)
    }
}
```

```swift
// Code-defined dynamic brand color (when the asset catalog is not enough)
extension Color {
    static let brandAccessible = Color(uiColor: UIColor { trait in
        switch (trait.userInterfaceStyle, trait.accessibilityContrast) {
        case (.dark, .high):  return UIColor(hex: "#7FB8FF")
        case (.dark, _):      return UIColor(hex: "#5AA0F2")
        case (_,   .high):    return UIColor(hex: "#003E82")
        default:              return UIColor(hex: "#0A4E9C")
        }
    })
}
```

Apple's own Messages bubbles fail the bar (blue ~3.5:1, green ~2.1:1) — an explicit cautionary example from App Store Connect's Sufficient Contrast criteria. Don't model your brand on that.

---

## 10. Liquid Glass considerations (iOS 26)

### 10.1 What Liquid Glass is

Announced at **WWDC 2025** (Session **219** *Meet Liquid Glass*) and shipped in iOS 26 / iPadOS 26 / macOS Tahoe 26 in September 2025. Apple describes it as "a new digital meta-material that dynamically bends and shapes light" — a successor to the iOS 7 real-time blur, not just a new variant.

Key behavioral differences from prior `UIBlurEffect` / `.ultraThinMaterial`–`.ultraThickMaterial`:

| Property | Old materials | Liquid Glass |
|---|---|---|
| Optics | Gaussian blur + vibrancy | Lensing — bends/concentrates light per frame |
| Light/dark | Fixed per material | Small elements **flip** foreground color with content luminance beneath |
| Shape | Static | Morphs; can merge with nearby glass |
| Motion | None | Specular highlights react to device motion; touch illuminates adjacent glass |
| Layering rule | Any | **Navigation layer only** — glass must not stack on glass |

Used for: tab bars, navigation bars, toolbars, sidebars (float on iPad/Mac), Control Center, Notification Center, sheets, popovers, menus, alerts, sliders, switches, the Lock Screen clock, and optional "clear" app icons.

### 10.2 Color behavior on glass

- **Shadow adaptivity.** Shadows intensify over busy/text content and fade over solid light backgrounds — Apple's automatic answer to "lift" without you tuning it.
- **Foreground flip.** Small elements (nav/tab glyphs, labels) auto-flip between light and dark based on the luminance of content behind. Large elements (sidebars, menus) adapt but do not flip.
- **Tinting model.** Applying a tint (including your app accent) to glass does **not** produce a flat fill — it generates a tonal range remapped per frame against the background's brightness. Hue/saturation/brightness shift to keep the glass character.
- **Lensing.** Colorful content bleeds/spills onto glass surfaces — most visible on iPad/Mac sidebars.

Implication: brand accent colors on glass generally stay legible automatically, but pale brand colors over pale content can still fail. Test.

### 10.3 New APIs (iOS 26)

**SwiftUI (confirmed from Apple docs + WWDC 323 *Build a SwiftUI app with the new design*):**

| API | Purpose |
|---|---|
| `.glassEffect(_ glass: Glass = .regular, in: Shape = .capsule, isEnabled: Bool = true)` | Apply Liquid Glass to any view |
| `Glass` (struct) | Material config — `.regular`, `.clear`, `.identity` |
| `Glass.tint(_ color: Color)` | Colored glass (tonal range, not flat fill) |
| `Glass.interactive()` | Adds touch-illumination / scale / shimmer |
| `GlassEffectContainer(spacing:) { … }` | Groups multiple glass elements in one sampling region — **required** whenever ≥2 glass elements sit near each other (glass cannot sample other glass) |
| `.glassEffectID(_:in:)` | Namespace ID for morphing transitions |
| `.glassEffectUnion(id:namespace:)` | Manually merge distant glass elements |
| `.glassEffectTransition(_:)` | `.identity` / `.matchedGeometry` / `.materialize` |
| `.buttonStyle(.glass)` | Translucent glass button (secondary) |
| `.buttonStyle(.glassProminent)` | Prominent glass button (primary CTA) |
| `.tabBarMinimizeBehavior(_:)` | `.onScrollDown` / `.automatic` / `.never` |
| `.tabViewBottomAccessory { … }` | Persistent glass view above tab bar |
| `Tab(…, role: .search)` | Floating search glass button |
| `ToolbarSpacer(.fixed, spacing:)` / `ToolbarSpacer(.flexible)` | Group vs split toolbar pills |
| `.sharedBackgroundVisibility(.hidden)` | Detach a toolbar item from shared glass |
| `.backgroundExtensionEffect()` | Extend glass beyond the safe area |

**UIKit (confirmed via Apple Developer Forums thread 791540 and Xcode 26 headers):**

- `UIGlassEffect` — new `UIVisualEffect` subclass; properties include `style` (`.regular` / `.clear`), `tintColor`, `isInteractive`.
- `UIGlassContainerEffect` — SwiftUI's `GlassEffectContainer` equivalent; applied via `UIVisualEffectView`.
- `UIScrollEdgeEffect` — the dissolving effect beneath a floating glass bar.
- `UIViewCornerConfiguration` — concentric corners that match the container.

**Auto-adoption.** Recompile with Xcode 26 and `NavigationStack`, `TabView`, `.toolbar`, sheets, popovers, and `NavigationSplitView` sidebars adopt Liquid Glass with zero code changes. Opt-out is `UIDesignRequiresCompatibility = YES` in `Info.plist` — **expected to be removed in Xcode 27**, so treat it as a short-term migration aid only.

### 10.4 Accent color on glass

`.tint(_:)` now feeds the glass-tinting system. The accent generates a remapped tonal range per frame rather than filling flat. Apple's explicit guidance (WWDC 219): **"Tinting should only be used to bring emphasis to primary elements and actions."** Don't tint every glass element — if everything is tinted, nothing stands out.

Idiomatic primary-CTA pattern:

```swift
Button("View Bag") { }
    .buttonStyle(.glassProminent)
    .tint(.brandPrimary)
```

Idiomatic destructive pattern:

```swift
Button("Delete") { /* … */ }
    .padding()
    .glassEffect(.regular.tint(.red).interactive(), in: .capsule)
```

Push brand hue into the **content layer** (cards, hero imagery, illustrations) and keep the navigation layer neutral glass — the inverse of the iOS 7–18 pattern where chrome carried the brand.

### 10.5 Legibility on translucent surfaces

Requirements distilled from WWDC 219 and HIG Materials:

- **Content discipline.** In steady states, do not pin critical content directly under a glass bar — reposition/scale so nothing important intersects.
- **`.clear` only when:** media-rich content underneath, content tolerates dimming, foreground on the glass is bold and bright. Otherwise use `.regular`.
- **Vibrancy is automatic.** Text/icons on `.regular` glass auto-shift saturation/brightness/hue; don't override with manual `.white`/`.black`.
- **No glass on glass.** Use fills, vibrancy, or transparency on top of glass — never nest another glass layer.
- **WCAG still applies.** 4.5:1 after the blur, tested against representative backgrounds.

**Accessibility overrides (automatic — no code):** *Reduce Transparency* frosts glass and attenuates lensing; *Increase Contrast* forces strong black/white with borders; *Reduce Motion* disables elastic/shimmer. **iOS 26.1** added a user-level toggle at Settings → Display & Brightness → **Liquid Glass** → *Clear* or *Tinted*.

### 10.6 Coexistence with prior materials

`.ultraThinMaterial`–`.ultraThickMaterial` and the `UIBlurEffect.system*Material` family are **not deprecated**. They remain appropriate for **content-layer** frosted surfaces (cards, frosted overlays in lists) where glass doesn't belong. Using `.ultraThinMaterial` on a navigation bar in iOS 26 is legal but now visually dated alongside system-provided glass.

### 10.7 Migration checklist

1. Recompile with Xcode 26 — standard chrome adopts glass automatically.
2. Audit custom blur overlays on control-layer UI; replace `.background(.ultraThinMaterial)` with `.glassEffect()`.
3. Wrap adjacent glass in `GlassEffectContainer` (spacing defines the merging threshold).
4. Replace custom button backgrounds with `.buttonStyle(.glass)` / `.glassProminent`.
5. Remove custom `.presentationBackground(…)` on sheets so iOS 26 can apply glass.
6. Remove opaque toolbar backgrounds; let glass show through.
7. Tint only primary actions — not every glass element.
8. QA with Reduce Transparency, Increase Contrast, Reduce Motion all ON.
9. Provide an iOS-18 fallback with `#available(iOS 26, *)`.

### 10.8 Code — Liquid Glass patterns

```swift
// Grouped glass toolbar pill
GlassEffectContainer(spacing: 40) {
    HStack(spacing: 40) {
        Image(systemName: "scribble.variable")
            .font(.system(size: 36)).frame(width: 80, height: 80)
            .glassEffect()
        Image(systemName: "eraser.fill")
            .font(.system(size: 36)).frame(width: 80, height: 80)
            .glassEffect()
    }
}
```

```swift
// Morphing expand/collapse glass menu
struct MorphMenu: View {
    @State private var open = false
    @Namespace private var ns
    var body: some View {
        GlassEffectContainer(spacing: 30) {
            VStack {
                Button(open ? "Close" : "Open") {
                    withAnimation(.bouncy) { open.toggle() }
                }
                .glassEffect().glassEffectID("root", in: ns)
                if open {
                    Button("Edit")  { }.glassEffect().glassEffectID("edit",  in: ns)
                    Button("Share") { }.glassEffect().glassEffectID("share", in: ns)
                }
            }
        }
    }
}
```

```swift
// Collapsible glass tab bar + floating search + persistent accessory
TabView {
    Tab("Home", systemImage: "house") { HomeView() }
    Tab("Library", systemImage: "books.vertical") { LibraryView() }
    Tab("Search", systemImage: "magnifyingglass", role: .search) {
        NavigationStack { SearchView() }
    }
}
.tabBarMinimizeBehavior(.onScrollDown)
.tabViewBottomAccessory { NowPlayingBar() }
```

```swift
// iOS 18 / iOS 26 fallback
extension View {
    @ViewBuilder
    func brandedGlass(in shape: some Shape = Capsule(),
                      interactive: Bool = false,
                      tint: Color? = nil) -> some View {
        if #available(iOS 26.0, *) {
            var glass: Glass = .regular
            if let tint { glass = glass.tint(tint) }
            if interactive { glass = glass.interactive() }
            self.glassEffect(glass, in: shape)
        } else {
            self.background(
                shape.fill(.ultraThinMaterial)
                    .overlay(shape.stroke(.white.opacity(0.2), lineWidth: 1))
            )
        }
    }
}
```

```swift
// UIKit — glass container with two glass items
if #available(iOS 26.0, *) {
    let container = UIGlassContainerEffect()
    container.spacing = 12
    let containerView = UIVisualEffectView(effect: container)

    let g1 = UIVisualEffectView(effect: UIGlassEffect())
    let g2 = UIVisualEffectView(effect: UIGlassEffect())
    g1.layer.cornerRadius = 20; g1.clipsToBounds = true
    g2.layer.cornerRadius = 20; g2.clipsToBounds = true
    containerView.contentView.addSubview(g1)
    containerView.contentView.addSubview(g2)
    view.addSubview(containerView)
}
```

### 10.9 Anti-patterns on glass

```swift
// ❌ Tinting everything — destroys hierarchy
TabBar().glassEffect(.regular.tint(.brandPrimary))
Button("Cancel") { }.glassEffect(.regular.tint(.brandPrimary))
Button("Save")   { }.glassEffect(.regular.tint(.brandPrimary))

// ✅ Tint only primary action
Button("Save") { }
    .buttonStyle(.glassProminent).tint(.brandPrimary)

// ❌ Glass stacked on glass
ZStack {
    Rectangle().glassEffect()
    Text("x").padding().glassEffect()  // breaks the optical model
}

// ❌ Opaque brand fill on nav — loses the glass optic
navigationBar.backgroundColor = .brandPrimary
// ✅ Let glass show through; tint primary items only
```

---

## 11. Decision trees

**Do I need a specific color value?**

```
Is the color standing in for a UIKit semantic role (text / background / fill)?
├─ YES  → Use the semantic token (label, systemBackground, systemFill, …)
└─ NO   → Is it a branded/identity color?
         ├─ YES → Define a Color Set in Assets.xcassets with Any / Dark / HC variants
         └─ NO  → Is it a hue standing in for meaning (destructive, success)?
                 ├─ YES → Use the system hue (.systemRed, .systemGreen, …)
                 └─ NO  → Reconsider — you probably want a semantic token
```

**Which background?**

```
Are the visual groupings "cards on gray" (Settings-style)?
├─ YES → systemGroupedBackground / secondary / tertiary
└─ NO  → systemBackground / secondary / tertiary
```

**Accent color on iOS 26 glass?**

```
Is this the primary action for the screen?
├─ YES → .buttonStyle(.glassProminent).tint(.brandPrimary)
└─ NO  → Is it a critical destructive/emphasized action?
        ├─ YES → .glassEffect(.regular.tint(.red).interactive())
        └─ NO  → Leave neutral; push brand into content layer
```

---

## 12. Quick reference — UIKit ↔ SwiftUI

| Task | UIKit | SwiftUI |
|---|---|---|
| Primary text | `.label` | `Color(.label)` or `.primary` |
| Secondary text | `.secondaryLabel` | `Color(.secondaryLabel)` or `.secondary` |
| Plain bg | `.systemBackground` | `Color(.systemBackground)` |
| Grouped bg | `.systemGroupedBackground` | `Color(.systemGroupedBackground)` |
| Card on grouped | `.secondarySystemGroupedBackground` | `Color(.secondarySystemGroupedBackground)` |
| Fill | `.tertiarySystemFill` | `Color(.tertiarySystemFill)` |
| Separator | `.separator` / `.opaqueSeparator` | `Color(.separator)` |
| Destructive | `.systemRed` | `.red` / `Color(.systemRed)` |
| Success | `.systemGreen` | `.green` |
| Accent | `view.tintColor = …` | `.tint(…)` |
| Named asset | `UIColor(resource: .brand)` | `Color(.brand)` |
| Dark mode check | `traitCollection.userInterfaceStyle` | `@Environment(\.colorScheme)` |
| Contrast check | `traitCollection.accessibilityContrast` | `@Environment(\.colorSchemeContrast)` |
| Force style | `overrideUserInterfaceStyle` | `.preferredColorScheme(_:)` |
| Material | `UIBlurEffect(style: .systemThinMaterial)` | `.background(.thinMaterial)` |
| Glass (iOS 26) | `UIGlassEffect()` in `UIVisualEffectView` | `.glassEffect(.regular, in: .capsule)` |
| Glass container (iOS 26) | `UIGlassContainerEffect` | `GlassEffectContainer { … }` |
| Glass button (iOS 26) | `UIButton.Configuration.glassProminent()` / custom | `.buttonStyle(.glassProminent)` |

---

## 13. References

**Apple (primary):**
- Human Interface Guidelines — Color: https://developer.apple.com/design/human-interface-guidelines/color
- HIG — Dark Mode: https://developer.apple.com/design/human-interface-guidelines/dark-mode
- HIG — Materials: https://developer.apple.com/design/human-interface-guidelines/materials
- UIColor — UI element colors: https://developer.apple.com/documentation/uikit/uicolor/ui-element-colors
- UIColor — Standard colors: https://developer.apple.com/documentation/uikit/uicolor/standard-colors
- SwiftUI Color: https://developer.apple.com/documentation/swiftui/color
- SwiftUI ShapeStyle / HierarchicalShapeStyle: https://developer.apple.com/documentation/swiftui/shapestyle · https://developer.apple.com/documentation/swiftui/hierarchicalshapestyle
- Specifying your app's color scheme (AccentColor): https://developer.apple.com/documentation/xcode/specifying-your-apps-color-scheme
- App Store Connect — Sufficient Contrast criteria: https://developer.apple.com/help/app-store-connect/manage-app-accessibility/sufficient-contrast-evaluation-criteria/
- App Store Connect — Dark Interface criteria: https://developer.apple.com/help/app-store-connect/manage-app-accessibility/dark-interface-evaluation-criteria/
- Adopting Liquid Glass: https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
- Liquid Glass technology overview: https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass
- Applying Liquid Glass to custom views: https://developer.apple.com/documentation/SwiftUI/Applying-Liquid-Glass-to-custom-views
- `Glass` struct: https://developer.apple.com/documentation/swiftui/glass
- Landmarks sample (Liquid Glass): https://developer.apple.com/documentation/SwiftUI/Landmarks-Building-an-app-with-Liquid-Glass

**WWDC sessions (Apple):**
- WWDC 2019 #214 — *What's New in iOS Design*: https://developer.apple.com/videos/play/wwdc2019/214/
- WWDC 2019 #808 — *Implementing Dark Mode on iOS*
- WWDC 2016 #712 — *Working with Wide Color* (P3/gamut)
- WWDC 2025 #219 — *Meet Liquid Glass*: https://developer.apple.com/videos/play/wwdc2025/219/
- WWDC 2025 #323 — *Build a SwiftUI app with the new design*
- WWDC 2025 #356 — *Get to know the new design system*: https://developer.apple.com/videos/play/wwdc2025/356/
- WWDC 2025 #220 — *Say hello to the new look of app icons*
- WWDC 2025 #361 — *Create icons with Icon Composer*
- WWDC 2025 — *Liquid Glass in UIKit*

**Community (secondary, high signal):**
- Paul Hudson / Hacking with Swift — semantic colors, named UIColor, materials, `Color.resolve`: https://www.hackingwithswift.com/
- Sarunw — dark color cheat sheet, tintColor in SwiftUI, AccentColor, asset symbols: https://sarunw.com/
- Swift by Sundell — dynamic colors in Swift: https://www.swiftbysundell.com/articles/defining-dynamic-colors-in-swift/
- Jesse Squires — CGColor pitfalls, dynamic SwiftUI colors: https://www.jessesquires.com/
- Noah Gilmore — empirically extracted dark-mode RGBA values: https://noahgilmore.com/blog/dark-mode-uicolor-compatibility
- PSPDFKit — adopting dark mode: https://pspdfkit.com/blog/2019/adopting-dark-mode-on-ios/
- NSHipster — Dark Mode on iOS 13: https://nshipster.com/dark-mode/
- Nil Coalescing — hierarchical styles, foregroundStyle vs color: https://nilcoalescing.com/
- Use Your Loaf — override dark mode, disabling asset-symbol generation: https://useyourloaf.com/
- Donny Wals — designing custom UI with Liquid Glass: https://www.donnywals.com/designing-custom-ui-with-liquid-glass-on-ios-26/
- Nielsen Norman Group — Liquid Glass usability review: https://www.nngroup.com/articles/liquid-glass/
- conorluddy/LiquidGlassReference (API index): https://github.com/conorluddy/LiquidGlassReference

---

## Conclusion — what to internalize

Treat iOS color as a **token system with resolution context**, not a palette. Pick the semantic token (`label`, `systemBackground`, `systemFill`) first; reach for a hue (`systemRed`, `systemGreen`) only when meaning demands it; fall back to a brand color set only when identity demands it. Let the system resolve light/dark/high-contrast/elevation — that is what makes your app feel native and accessible without extra code.

On iOS 18, the two deprecations worth acting on today are `.accentColor(_:)` (use `.tint(_:)`) and `.foregroundColor(_:)` (use `.foregroundStyle(_:)`). Both unlock materials, hierarchical styles, and gradients you cannot express otherwise.

On iOS 26, the mental model shifts: **chrome is neutral glass, content is branded**. Auto-adoption via Xcode 26 gets most of the way there; the remaining work is pruning custom blurs and tinting from navigation, grouping adjacent glass in `GlassEffectContainer`, and reserving tinted glass for primary actions. With `UIDesignRequiresCompatibility` scheduled to disappear in Xcode 27, Liquid Glass is not an opt-in for long.