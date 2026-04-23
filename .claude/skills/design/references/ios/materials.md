---
name: materials
description: Apple classic materials & blur (UIBlurEffect, UIVibrancyEffect, SwiftUI Material) on iOS 18/26
platform: ios
---

# Apple's classic materials and blur on iOS

> **Scope note.** This document covers Apple's **classic materials and blur system** (`UIBlurEffect`, `UIVisualEffectView`, `UIVibrancyEffect`, SwiftUI `Material`) on iOS 18 and iOS 26. It **complements — does not replace —** existing Liquid Glass documentation. Liquid Glass (iOS 26+, `glassEffect`, `UIGlassEffect`, `GlassEffectContainer`) is a **new, additional** layer that lives on top of the classic system; both APIs continue to ship and Apple explicitly directs developers to keep using classic materials for everything that is not "navigation-layer chrome." Where Liquid Glass interactions matter (sheets, bars, fallback strategies), they are summarized here, but for a deep treatment of `glassEffect` itself, refer to your existing Liquid Glass document.

Classic materials remain the default for content-layer surfaces, full-bleed scrims, large overlay panels, widget backgrounds, sheets on iOS ≤ 25, and any UI that must back-deploy below iOS 26. They are first-class APIs in iOS 26 — none deprecated. The system handles Reduce Transparency, Increase Contrast, and Differentiate Without Color automatically as long as you use the system materials and the system vibrancy/foreground hierarchy.

---

## 1. The five thicknesses, side-by-side

Apple ships five adaptive thickness levels plus two specialty styles. They are **identical in look** across UIKit and SwiftUI — `.ultraThinMaterial` in SwiftUI is the same surface as `UIBlurEffect(style: .systemUltraThinMaterial)` in UIKit. They adapt automatically to light/dark mode (you sample the ambient `colorScheme` / `UITraitCollection`), and they apply a saturation bump to colors showing through so that wallpaper hues remain perceptible.

| Thickness | SwiftUI | UIKit `UIBlurEffect.Style` | Visual character | Primary use |
|---|---|---|---|---|
| **Ultra thin** | `.ultraThinMaterial` | `.systemUltraThinMaterial` | Mostly translucent; you can clearly see the content beneath. | Tiny glass overlays on photos/video, badge backgrounds, hint chips. |
| **Thin** | `.thinMaterial` | `.systemThinMaterial` | More translucent than opaque; subtle frosting. | Lightweight panels, hover affordances, secondary chrome. |
| **Regular** | `.regularMaterial` | `.systemMaterial` | Balanced — system default; legible but still translucent. | Cards, default sheets, background layers, popovers. |
| **Thick** | `.thickMaterial` | `.systemThickMaterial` | More opaque than translucent; strong legibility for fine text/icons. | Navigation-style bars, sidebars, dense content panels. |
| **Ultra thick** | `.ultraThickMaterial` | *no exact UIKit style — use `.systemThickMaterial` + a tint, or `.systemChromeMaterial`* | Mostly opaque; barely lets the backdrop through. | Alerts, action sheets, Control-Center-style panels, sensitive overlays. |
| **Chrome (UIKit only)** | — | `.systemChromeMaterial` | Tuned to match status-bar / toolbar chrome. | Custom UIKit toolbars and chrome surfaces. |
| **Bar (SwiftUI only)** | `Material.bar` | — | Matches system toolbar/tab-bar appearance. | Custom SwiftUI bars where you want a system-bar feel. |

**Quantitative notes.** Apple does not publish blur radii, opacity, or saturation values — they are private implementation details of `CABackdropLayer` / `CAFilter`. Reverse-engineered estimates (≈30–60 px radius depending on device class) circulate in design blogs, but you should not depend on them. The **only** stable way to think about thicknesses is the order: ultraThin < thin < regular < thick < ultraThick.

**Light/dark behavior.** All five `.system*Material` variants are adaptive. UIKit also exposes locked variants (`.systemThinMaterialLight`, `.systemThinMaterialDark`, etc.) that ignore the ambient appearance — useful when a surface always sits over the same imagery. SwiftUI has no locked variants; force one by setting `.environment(\.colorScheme, .dark)` on the container.

---

## 2. UIVisualEffectView, UIBlurEffect, UIVibrancyEffect

### 2.1 The view + effect model

`UIVisualEffectView` (iOS 8+) is a container that applies a `UIVisualEffect` (a blur, a vibrancy, or both) to **the content behind it** — never to its own subviews. Two structural rules:

- **Add subviews to `contentView`,** never directly to the effect view. Direct children render incorrectly.
- **Vibrancy is layered inside blur:** create the `UIBlurEffect`, wrap it in a `UIVisualEffectView`, then add a *second* `UIVisualEffectView` configured with `UIVibrancyEffect(blurEffect:style:)` to the blur view's `contentView`. Place your text/symbols in the vibrancy view's `contentView`.

### 2.2 Blur styles, all variants

```swift
// Adaptive system materials (iOS 13+, recommended)
.systemUltraThinMaterial   .systemThinMaterial   .systemMaterial
.systemThickMaterial       .systemChromeMaterial

// Locked light/dark variants (iOS 13+) — five pairs
.systemUltraThinMaterialLight / .systemUltraThinMaterialDark
.systemThinMaterialLight      / .systemThinMaterialDark
.systemMaterialLight          / .systemMaterialDark
.systemThickMaterialLight     / .systemThickMaterialDark
.systemChromeMaterialLight    / .systemChromeMaterialDark

// Legacy styles (iOS 8–10) — do NOT adapt; avoid in new code
.extraLight  .light  .dark  .extraDark  .regular  .prominent
```

### 2.3 Vibrancy styles

`UIVibrancyEffectStyle` (iOS 13+) gives you eight pre-tuned color transforms grouped into three families:

- **Label hierarchy:** `.label`, `.secondaryLabel`, `.tertiaryLabel`, `.quaternaryLabel` — primary to lowest-contrast.
- **Fill hierarchy:** `.fill`, `.secondaryFill`, `.tertiaryFill` — for filled shapes behind content.
- **Separator:** `.separator` — for dividers.

A frequent gotcha: when a `UILabel` or `UIImageView` is inside a vibrancy view's `contentView`, **its `textColor` / `tintColor` is ignored**. The vibrancy effect computes the rendered color itself. Templated symbol images work; full-color raster images do not.

### 2.4 Production-ready blur + vibrancy (UIKit)

```swift
let blur = UIBlurEffect(style: .systemThinMaterial)
let blurView = UIVisualEffectView(effect: blur)
view.addSubview(blurView)

let vibrancy = UIVibrancyEffect(blurEffect: blur, style: .secondaryLabel)
let vibrancyView = UIVisualEffectView(effect: vibrancy)
blurView.contentView.addSubview(vibrancyView)         // INSIDE the blur

let label = UILabel()
label.text = "Visit Singapore"
label.font = .preferredFont(forTextStyle: .largeTitle)
vibrancyView.contentView.addSubview(label)            // INSIDE the vibrancy

blurView.layer.cornerRadius = 16
blurView.layer.cornerCurve = .continuous
blurView.layer.masksToBounds = true
```

### 2.5 When to choose UIKit over SwiftUI materials

Use `UIVisualEffectView` when you need explicit vibrancy styles (SwiftUI doesn't expose `.fill` / `.separator` analogs), when you must lock to a light or dark variant, when you need a `UIViewRepresentable` bridge to back-deploy below iOS 15, or when you need to mask the blur with a `CAShapeLayer` for non-rectangular shapes that `Shape` can't express. Otherwise, prefer SwiftUI materials — they are shorter, more declarative, and integrate with hierarchical foreground styles automatically.

---

## 3. SwiftUI Material APIs

`Material` (iOS 15+, not on watchOS) is a `ShapeStyle`. Because of that single fact, every place that takes a `ShapeStyle` — `.background`, `.foregroundStyle`, `Shape.fill`, `.backgroundStyle`, `.overlay` — accepts a material.

### 3.1 The shape-style trick

```swift
extension ShapeStyle where Self == Material {
    public static var ultraThinMaterial:  Material { get }   // iOS 15+
    public static var thinMaterial:       Material { get }
    public static var regularMaterial:    Material { get }
    public static var thickMaterial:      Material { get }
    public static var ultraThickMaterial: Material { get }
    public static var bar:                Material { get }
}
```

That extension is why `.background(.ultraThinMaterial)` works without spelling out the type.

### 3.2 The four idiomatic uses

```swift
// 1. As a background, full-rectangle
Text("Hi").padding().background(.ultraThinMaterial)

// 2. As a background clipped to a shape
Text("Hi").padding()
    .background(.thinMaterial, in: Capsule())

// 3. As a Shape fill
RoundedRectangle(cornerRadius: 20, style: .continuous)
    .fill(.regularMaterial)

// 4. As the default container background (iOS 16+)
GroupBox("Details") { Text("…") }
    .backgroundStyle(.ultraThinMaterial)
```

### 3.3 Vibrancy comes for free via the foreground hierarchy

The SwiftUI equivalent of `UIVibrancyEffectStyle` is the **hierarchical foreground style**. Any `View` placed over a `Material`-backed background automatically renders with vibrancy when its foreground style is `.primary`, `.secondary`, `.tertiary`, or `.quaternary`. Setting an explicit color (`.foregroundStyle(.white)`) **disables vibrancy** — that's the most common legibility regression we see in production apps.

```swift
VStack(alignment: .leading) {
    Text("Title").foregroundStyle(.primary)        // vibrant primary
    Text("Subtitle").foregroundStyle(.secondary)   // vibrant secondary
    Divider()                                       // vibrant separator
}
.padding()
.background(.thinMaterial, in: RoundedRectangle(cornerRadius: 12))
```

`Material.bar` is the SwiftUI counterpart of `UIBlurEffect.Style.systemChromeMaterial`. Use it for custom toolbar surfaces that should match system bars.

---

## 4. SwiftUI ↔ UIKit, paired

| Capability | UIKit | SwiftUI |
|---|---|---|
| Apply blur behind content | `UIVisualEffectView(effect: UIBlurEffect(style: .systemThinMaterial))` | `.background(.thinMaterial)` |
| Material clipped to shape | `view.layer.cornerRadius = r; layer.masksToBounds = true` | `.background(.thinMaterial, in: RoundedRectangle(cornerRadius: r))` |
| Material as a fill | `CAShapeLayer` mask on the effect view | `Shape().fill(.regularMaterial)` |
| Vibrancy: secondary label | `UIVibrancyEffect(blurEffect: blur, style: .secondaryLabel)` | `.foregroundStyle(.secondary)` on material |
| Vibrancy: separator | `UIVibrancyEffect(blurEffect: blur, style: .separator)` | `Divider()` (automatic) |
| Lock to light/dark | `.systemThinMaterialLight` / `…Dark` | `.environment(\.colorScheme, .light)` on container |
| Chrome / bar look | `.systemChromeMaterial` | `Material.bar` |
| Bridge to other framework | `UIHostingController` for SwiftUI inside UIKit | `UIViewRepresentable` wrapping `UIVisualEffectView` |

Bridge snippet — drop SwiftUI into a project where you need a UIKit blur with an explicit style:

```swift
struct VisualEffectBlur: UIViewRepresentable {
    var style: UIBlurEffect.Style = .systemMaterial
    func makeUIView(context: Context) -> UIVisualEffectView {
        UIVisualEffectView(effect: UIBlurEffect(style: style))
    }
    func updateUIView(_ v: UIVisualEffectView, context: Context) {
        v.effect = UIBlurEffect(style: style)
    }
}
```

---

## 5. Materials vs Liquid Glass — when classic still wins

Apple was unusually direct at WWDC25. From session 219 *Meet Liquid Glass*: **"Liquid Glass is best reserved for the navigation layer that floats above the content of your app."** From session 284 *Build a UIKit app with the new design*: **"Liquid Glass is distinct from other visual effects, like UIBlurEffect… limit Liquid Glass to the most important elements of your app."** The classic materials are not legacy — they are the recommended choice for content-layer and full-bleed surfaces in iOS 26 apps.

### 5.1 Decision matrix

| UI scenario | iOS 26 recommendation | Pre-iOS 26 equivalent |
|---|---|---|
| Nav / tab / toolbar background | **Liquid Glass (automatic on Xcode 26 recompile)** | `.systemMaterial` via `UINavigationBarAppearance.backgroundEffect` |
| Floating action button / pill | `.glassEffect(.regular.interactive())` | `.background(.ultraThinMaterial, in: Capsule())` |
| Sheet at partial detent | Automatic Liquid Glass — **do not** set `presentationBackground` | `.presentationBackground(.ultraThinMaterial)` |
| Large overlay panels, settings sheets | **Classic `.regularMaterial` / `.thickMaterial`** (Liquid Glass is for controls, not large surfaces) | Same |
| Full-bleed scrim over media | **Classic `.ultraThinMaterial`** (place Liquid Glass *only* on the controls floating above) | `.ultraThinMaterial` |
| Control-Center-style panel | **Classic `.ultraThickMaterial`** | `.ultraThickMaterial` |
| Card / list-row background | **Solid system color** (`Color(.secondarySystemBackground)`) — never glass | Same |
| Widget background | `.containerBackground(for: .widget)` (system applies appropriate rendering) | Same (iOS 17+ API) |

### 5.2 The two rules that cover most mistakes

**Never glass-on-glass.** Stacking translucent layers — whether two materials, two glass effects, or a glass effect over a material — muddies hierarchy and multiplies render cost. For elements layered on top of glass, use solid fills, transparency, and vibrancy.

**Never replace system bar/sheet backgrounds when targeting iOS 26.** From WWDC25 session 284: *"Remove any background customization from your navigation and toolbars. Using `UIBarAppearance` or `backgroundColor` interferes with the glass appearance."* If you previously set `appearance.backgroundEffect = UIBlurEffect(...)` to opt into iOS 13+ frosted bars, gate that behind `#available(iOS, ..., 25.x)` so iOS 26 takes the system path.

### 5.3 Backward-compatibility wrappers

```swift
// SwiftUI — Liquid Glass on iOS 26+, ultraThinMaterial fallback otherwise
extension View {
    @ViewBuilder
    func adaptiveGlass<S: Shape>(in shape: S = Capsule()) -> some View {
        if #available(iOS 26, *) {
            self.glassEffect(.regular, in: shape)
        } else {
            self.background(.ultraThinMaterial, in: shape)
                .overlay(shape.stroke(.white.opacity(0.18), lineWidth: 0.5))
        }
    }
}

// UIKit equivalent
func makeAdaptiveGlass() -> UIVisualEffectView {
    if #available(iOS 26, *) {
        return UIVisualEffectView(effect: UIGlassEffect())
    } else {
        return UIVisualEffectView(effect: UIBlurEffect(style: .systemUltraThinMaterial))
    }
}
```

For teams that need extra time, Apple ships an Info.plist opt-out: **`UIDesignRequiresCompatibility = YES`** forces the pre-Liquid-Glass appearance on iOS 26. It is documented as temporary and is expected to be removed in iOS 27 — treat it as a migration runway, not a long-term solution.

---

## 6. Legibility on materials

The Human Interface Guidelines are explicit: *"Help ensure legibility by using only vibrant colors on top of materials."* That single rule prevents most readability failures.

### 6.1 The vibrancy hierarchy in both frameworks

| Level | SwiftUI | UIKit | When |
|---|---|---|---|
| Primary | `.foregroundStyle(.primary)` | `UIVibrancyEffectStyle.label` | Body text, titles |
| Secondary | `.foregroundStyle(.secondary)` | `.secondaryLabel` | Subtitles, metadata |
| Tertiary | `.foregroundStyle(.tertiary)` | `.tertiaryLabel` | Placeholders |
| Quaternary | `.foregroundStyle(.quaternary)` | `.quaternaryLabel` | Decorative — **never on `.ultraThin` or `.thin`** |

### 6.2 SF Symbols

Prefer **monochrome** or **hierarchical** rendering modes on materials — both compose correctly with vibrancy. **Palette** mode is fine when the chosen palette colors are system semantics. **Multicolor** symbols use Apple-defined fixed hues and can clash with material backdrops; test in both light and dark and with Increase Contrast on.

```swift
Image(systemName: "heart.fill")
    .symbolRenderingMode(.hierarchical)
    .foregroundStyle(.primary)
```

### 6.3 When materials fail

- **Busy photo backgrounds.** Frosted glass over a high-frequency photo blends label color with photo color. Add a 20–40% black dim layer underneath the material, or move up to `.thickMaterial`.
- **Low-contrast scenes** (light on light, dark on dark). Vibrancy has nothing to amplify.
- **Strong complementary colors** bleeding through (red text over a material whose backdrop has saturated green).
- **Live video / camera feed** behind a thin material — per-frame vibrancy recomputation hitches scrolls.
- **Very small text** (caption2-and-below). Vibrancy edges soften; use a thicker material or an opaque background.

### 6.4 Overlays on photos and video — the canonical recipe

Use a gradient to dim the bottom of the hero image, lay a material band over the dimmed region, place vibrant labels inside. Apple uses this pattern in Photos, Music, and the Lock Screen.

```swift
ZStack(alignment: .bottom) {
    Image("hero").resizable().scaledToFill()
    LinearGradient(colors: [.black.opacity(0.5), .clear],
                   startPoint: .bottom, endPoint: .top)
        .frame(height: 160)
    HStack {
        Text("Now Playing").foregroundStyle(.primary)
        Spacer()
        Image(systemName: "play.fill")
    }
    .padding()
    .background(.ultraThinMaterial)
}
```

---

## 7. Performance

Materials are **GPU-bound, not CPU-bound.** A single `UIBlurEffect` issues roughly five GPU passes (content render → capture → horizontal Gaussian → vertical Gaussian → upscale + tint). `UIVibrancyEffect` adds two more offscreen passes plus an expensive compositing filter — effectively doubling the cost. On modern hardware (A15 / M1 and up) full-screen blurs are absorbed comfortably; on older devices and Apple Watch they cannot hit 60 fps. Liquid Glass uses the same compositor pipeline and Apple describes its impact as "negligible" on A15+, with automatic frosted-material fallback on older hardware.

### 7.1 Do

- Constrain blur bounds tightly — render cost scales with pixel count.
- Use system bars (`UINavigationBar`, `UITabBar`, `UIToolbar`) — Apple's private implementations only blur the dirty region.
- Coalesce adjacent glass elements in a single `GlassEffectContainer` (iOS 26).
- Snapshot truly static blurred content with `layer.shouldRasterize = true; rasterizationScale = UIScreen.main.scale` (cache evicts after 100 ms unused; max 2.5× screen size).
- Keep `UIVibrancyEffect` scoped to small label/icon regions.
- Set `shadowPath` on layers with shadows to avoid an offscreen pass per frame.

### 7.2 Don't

- Nest `UIVisualEffectView` inside another one.
- Apply blur to scrolling collection or table cells individually — put one blur behind a transparent collection view instead.
- Apply `UIVibrancyEffect` to large or full-screen areas.
- Animate `blurRadius` continuously or cross-fade `effect` every frame; switch between two pre-built views instead.
- Reimplement Gaussian blur on the CPU with `CIGaussianBlur` on live frames — it stalls the main thread.
- Toggle `shouldRasterize` on dynamically-resized layers; every change invalidates the cache.

### 7.3 Instruments and Simulator workflow

Open **Instruments → Core Animation**. Run on device, then enable Debug Options one at a time:

- **Color Blended Layers** — green = opaque, red = blended. Reduce red in scrolling rows.
- **Color Offscreen-Rendered Yellow** — every yellow region is an extra GPU pass. Bars and shadows-without-`shadowPath` glow yellow expectedly; everywhere else is suspect.
- **Color Hits Green / Misses Red** — validates `shouldRasterize`.
- **Color Copied Images (cyan)** — CPU is reformatting images per frame; pre-convert to 8-bpc BGRA.
- **Flash Updated Regions** — yellow flashes mark redraws.

The same toggles live in the Simulator under **Debug ▸ Color …** and in Xcode's **View Debugger**. The **Animation Hitches** template (Instruments 12+) surfaces render-phase hitches caused by blur. Apple's WWDC 2014 session 419 *Advanced Graphics and Animations for iOS Apps* remains the canonical performance reference.

---

## 8. Accessibility — Reduce Transparency, Increase Contrast, Differentiate Without Color

When the user enables **Settings ▸ Accessibility ▸ Display & Text Size ▸ Reduce Transparency**, iOS automatically swaps every system material for a mostly-opaque fill that approximates the wallpaper tint. Liquid Glass also defers — the WWDC25 session calls it "frostier and obscures more of the content." **Increase Contrast** raises target contrast to 7:1 and adds borders to translucent surfaces; iOS 26.1 made Increase Contrast also force Reduce Transparency on (per Six Colors, Nov 2025). **Reduced Motion** disables Liquid Glass's elastic morphing.

You get all of this **for free** if you use system materials, system bars, system sheets, and system foreground colors. Your job is only to handle custom translucent UI and to verify that your layouts still read when the material becomes opaque.

### 8.1 SwiftUI — detect and respond

```swift
struct CardView: View {
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
    @Environment(\.colorSchemeContrast) private var contrast
    @Environment(\.accessibilityDifferentiateWithoutColor) private var dwc

    var body: some View {
        Text("Now Playing")
            .padding()
            .background {
                if reduceTransparency {
                    Color(.secondarySystemBackground)
                } else {
                    Rectangle().fill(.ultraThinMaterial)
                }
            }
            .clipShape(RoundedRectangle(cornerRadius: 16))
            .overlay {
                if contrast == .increased {
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(.primary, lineWidth: 1)
                }
            }
    }
}
```

### 8.2 UIKit — detect and respond

```swift
final class BlurHeader: UIView {
    private let blur = UIVisualEffectView()
    private let solid = UIView()

    override init(frame: CGRect) {
        super.init(frame: frame)
        addSubview(solid); addSubview(blur)
        solid.backgroundColor = .secondarySystemBackground
        apply()
        NotificationCenter.default.addObserver(
            self, selector: #selector(apply),
            name: UIAccessibility.reduceTransparencyStatusDidChangeNotification,
            object: nil)
    }
    required init?(coder: NSCoder) { fatalError() }

    @objc private func apply() {
        if UIAccessibility.isReduceTransparencyEnabled {
            blur.effect = nil
            solid.isHidden = false
        } else {
            blur.effect = UIBlurEffect(style: .systemMaterial)
            solid.isHidden = true
        }
    }
}
```

Relevant flags and notifications:

| Setting | UIKit flag | Notification |
|---|---|---|
| Reduce Transparency | `UIAccessibility.isReduceTransparencyEnabled` | `reduceTransparencyStatusDidChangeNotification` |
| Increase Contrast | `UIAccessibility.isDarkerSystemColorsEnabled` | `darkerSystemColorsStatusDidChangeNotification` |
| Reduce Motion | `UIAccessibility.isReduceMotionEnabled` | `reduceMotionStatusDidChangeNotification` |
| Differentiate Without Color | `UIAccessibility.shouldDifferentiateWithoutColor` | `differentiateWithoutColorDidChangeNotification` |

### 8.3 Testing

The **Environment Overrides** HUD in the Simulator (icon between simulator window controls) toggles all four settings live. **Accessibility Inspector** (Xcode ▸ Open Developer Tool) does the same on a device, runs contrast audits, and exposes the vibrancy color stack. In UI tests, `app.performAccessibilityAudit()` (Xcode 15+) flags contrast and material legibility issues automatically.

---

## 9. Real-world patterns

### 9.1 Navigation bar with classic material (iOS 13–25)

```swift
// UIKit
let appearance = UINavigationBarAppearance()
appearance.configureWithTransparentBackground()
appearance.backgroundEffect = UIBlurEffect(style: .systemUltraThinMaterial)
navigationController?.navigationBar.standardAppearance = appearance
navigationController?.navigationBar.scrollEdgeAppearance = appearance
```

```swift
// SwiftUI
NavigationStack { ScrollView { /* ... */ } }
    .toolbarBackground(.ultraThinMaterial, for: .navigationBar)
    .toolbarBackground(.visible, for: .navigationBar)
```

On iOS 26, **remove** these customizations so Liquid Glass applies automatically; gate the legacy code behind `#available(iOS, ..., 25.x)`.

### 9.2 Sheets

```swift
// SwiftUI — pre-iOS 26
.sheet(isPresented: $show) {
    InfoView()
        .presentationDetents([.medium, .large])
        .presentationBackground(.ultraThinMaterial)
        .presentationCornerRadius(28)
}

// SwiftUI — iOS 26: omit presentationBackground; system applies Liquid Glass
.sheet(isPresented: $show) {
    InfoView().presentationDetents([.medium, .large])
}
```

```swift
// UIKit — works on iOS 15+
if let sheet = vc.sheetPresentationController {
    sheet.detents = [.medium(), .large()]
    sheet.prefersGrabberVisible = true
}
present(vc, animated: true)
```

### 9.3 Popovers, toolbars, tab bars

Popovers, `UIToolbar`, and `UITabBar` accept `UIBlurEffect` via their `standardAppearance` (`UITabBarAppearance.backgroundEffect`, `UIToolbarAppearance.backgroundEffect`). SwiftUI handles popovers through `.popover` and toolbars through `.toolbarBackground`. On iOS 26 you remove the customization for system Liquid Glass — but Apple's classic-material customization remains available for iPad sidebars, custom side toolbars, or apps that explicitly want a frosted-but-not-glass aesthetic.

### 9.4 Control-Center-style panels

There is no public API to host the system Control Center. To replicate the look in your own app, use `.ultraThickMaterial` (SwiftUI) or `UIBlurEffect(style: .systemThickMaterial)` plus a tint (UIKit). This is one of the explicit "still use classic materials" cases on iOS 26 — the panel is a large content surface, not a navigation-layer control.

### 9.5 Media-viewer overlays

Dim the media with a gradient, then float a thin material band carrying vibrant controls. On iOS 26 only the **controls** float on Liquid Glass (use the `.clear` variant when the underlying media is bold and bright); the dim+material backdrop stays classic.

### 9.6 Search bars

`UISearchController.searchBar` inherits the navigation bar's material on iOS 13+; it needs no extra blur setup. On iOS 26, `searchToolbarBehavior(.minimized)` (SwiftUI) and `navigationItem.searchBarPlacementBarButtonItem` (UIKit) place search inside the bottom Liquid Glass toolbar.

### 9.7 Widget backgrounds

Widgets cannot blur the Home Screen wallpaper — there is no live blur API. Use `.containerBackground(for: .widget) { ... }` (iOS 17+) with a solid color, image, or material. iOS 26's tinted/clear Home Screen modes apply Liquid Glass rendering automatically; ship images with `.widgetAccentedRenderingMode(.desaturated)` so they tint correctly.

```swift
struct MyWidgetView: View {
    var body: some View {
        VStack { /* content */ }
            .containerBackground(for: .widget) {
                Color.blue.opacity(0.2)
            }
    }
}
```

---

## 10. Decision trees

### 10.1 Which thickness, by what's behind it

```
What's behind the surface?
├── Photo / video / rich imagery
│   ├── Need maximum legibility for body text → .thickMaterial or .ultraThickMaterial
│   └── Brief glyph-only chip                 → .ultraThinMaterial (with a dim layer)
├── Scrolling list or feed
│   ├── Large nav/tab/toolbar → .regularMaterial (or system Liquid Glass on iOS 26)
│   └── Inline overlay        → .thinMaterial
├── Solid / static color
│   └── Don't use material — switch to a system fill color
└── Live camera or video
    └── Use .thickMaterial; consider an opaque fallback for performance
```

### 10.2 By element size

```
Element size?
├── Small pill / chip / control   → .ultraThinMaterial / .thinMaterial
├── Toolbar / tab bar / nav bar   → .regularMaterial    (iOS 26: Liquid Glass)
├── Sheet / popover / menu        → .thickMaterial      (iOS 26: Liquid Glass for system sheets)
├── Sidebar (iPad/Mac)            → .regularMaterial    (iOS 26: Liquid Glass)
└── Full-screen modal / panel     → .ultraThickMaterial or opaque
```

### 10.3 By foreground content

```
What sits on top?
├── Vibrant body text     → .regularMaterial + .foregroundStyle(.primary)
├── Vibrant secondary     → .regularMaterial + .foregroundStyle(.secondary)
├── Decorative quaternary → MUST use .regularMaterial or thicker — never .ultraThin/.thin
├── SF Symbol             → .symbolRenderingMode(.hierarchical) + .primary
├── Multicolor symbol     → .thickMaterial; test light + dark + Increase Contrast
└── Custom-color text     → Avoid; you forfeit vibrancy. If unavoidable, dim layer + opaque background.
```

### 10.4 By motion behind the surface

```
Behind the material…
├── Static               → Cache: layer.shouldRasterize on UIKit; system handles SwiftUI
├── Scrolls              → Live system material (UIVisualEffectView / Material)
└── Animates every frame → Constrain bounds aggressively; consider opaque + a single static image blur
```

---

## 11. Anti-patterns

**Glass-on-glass / stacked materials.** WWDC25 session 219 calls it out by name: stacking translucent layers — two materials, two glass effects, or a glass effect over a material — destroys hierarchy and multiplies render cost. For elements layered on top of glass or a material, use solid fills with transparency and vibrancy.

**Materials over solid or static backgrounds.** Materials are a *depth* device. Over a flat color they become a gray smear that adds no information and costs GPU. The same applies to widgets (no blur source available) and to test fixtures with a single solid color behind the material — they will look fine in development and wrong in production.

**Ultra-thin material with low-contrast text or tiny type.** The HIG explicitly says thicker materials provide better contrast for fine features. Pairing `.quaternary` foreground with `.ultraThinMaterial` is the textbook regression — it passes a glance test on a flat preview background and fails over real wallpapers and photos. The PSPDFKit case study of an App-Store-rejected tab is the canonical story here.

**Never testing Reduce Transparency, Increase Contrast, or Differentiate Without Color, and rolling your own blur.** Custom blurs (private `CAFilter`, manual `CIGaussianBlur`, SwiftUI `.blur(radius:)` masquerading as a material) bypass the entire accessibility pipeline. Reduce Transparency does not frost them, Increase Contrast does not add borders, Reduced Motion does not damp morphing. Always prefer system materials.

**Applying material customization to system bars and sheets on iOS 26.** Setting `UIBarAppearance.backgroundEffect` or `.toolbarBackground` / `.presentationBackground` on iOS 26 actively interferes with Liquid Glass. Gate any custom material chrome behind `#available(iOS, ..., 25.x)`.

---

## 12. WWDC session map

**WWDC 2014 — Session 419, "Advanced Graphics and Animations for iOS Apps."** The original performance reference for `UIVisualEffectView`. Documents the five-pass blur pipeline, vibrancy's two-pass cost, and the GPU-bound nature of materials. Still architecturally accurate; only the absolute frame-time numbers have aged.

**WWDC 2014 — Session 221, "Creating Custom iOS User Interfaces."** First introduction of `UIVisualEffectView`, `UIBlurEffect`, `UIVibrancyEffect`.

**WWDC 2018 — Session 803, "Designing Fluid Interfaces."** Source for the elasticity, response, and damping principles that later informed Liquid Glass; Apple cited it as a Liquid Glass lineage reference at WWDC25.

**WWDC 2018 — Session 230, "Deliver an Exceptional Accessibility Experience."** Documents Reduce Transparency behavior across system surfaces.

**WWDC 2020 — Session 10052, "Build with iOS pickers, menus and actions"** (paired with **Session 10205, "Design with iOS pickers, menus and actions"**). Covers system menus as material-backed surfaces; the practical takeaway is to prefer system menus over custom blurred overlays.

**WWDC 2021 — Session 10018, "What's new in SwiftUI."** Debut of SwiftUI's `Material` type and the automatic vibrancy through `.foregroundStyle(.secondary)` on top of materials.

**WWDC 2022 — "What's new in SwiftUI" (iOS 16).** Adds `toolbarBackground`, `toolbarColorScheme`, and `backgroundStyle` for material integration with bars.

**WWDC 2024 — Session 10151, "Create custom visual effects with SwiftUI."** Introduced `ScrollTransition` and `VisualEffect`, enabling scroll-driven blur. Apple's caution: visual effects should remain pleasant after the novelty wears off.

**WWDC 2025 — Session 219, "Meet Liquid Glass."** The reference text for Liquid Glass design principles, glass-on-glass avoidance, Regular vs Clear variants, automatic accessibility behavior, and the navigation-layer-only rule.

**WWDC 2025 — Session 356, "Get to know the new design system."** Companion to session 219 covering visual design and information architecture under the new system.

**WWDC 2025 — Session 323, "Build a SwiftUI app with the new design."** Recompile-with-Xcode-26 path; introduces `.glassEffect`, `GlassEffectContainer`, `backgroundExtensionEffect`.

**WWDC 2025 — Session 284, "Build a UIKit app with the new design."** UIKit counterparts: `UIGlassEffect`, `UIGlassContainerEffect`, `UIBackgroundExtensionView`, plus the explicit "remove your bar background customization" guidance.

**WWDC 2025 — Sessions 256 ("What's new in SwiftUI") and 243 ("What's new in UIKit").** Cover scroll-edge effects, container backgrounds, and how classic materials and Liquid Glass coexist in updated APIs.

---

## 13. Conclusion — what should change in your code

If your app supports iOS 18 and earlier, almost nothing should change: classic materials remain the right answer for cards, sheets, popovers, bars, full-bleed scrims, and overlays. Use the SwiftUI `.background(.ultraThinMaterial)` family for new code, fall back to `UIVisualEffectView` only when you need explicit vibrancy styles, locked light/dark variants, or non-rectangular masking. Use the foreground-style hierarchy for vibrant text and SF Symbols. Never set custom colors on text over materials unless you are providing your own contrast guarantee.

If you are recompiling for iOS 26, the largest practical change is **what to remove**: clear out custom `UIBarAppearance.backgroundEffect`, `.toolbarBackground`, and `.presentationBackground` calls so Liquid Glass takes over. Move custom floating controls behind an `#available(iOS 26, *)` wrapper that uses `.glassEffect` on iOS 26 and `.ultraThinMaterial` on older versions. Keep classic materials for everything else — content-layer surfaces, large overlay panels, full-bleed scrims over media, widget backgrounds — exactly as Apple's design team instructed at WWDC25. The two systems are complementary, not competitive, and they will continue to coexist for the foreseeable future.

The single mental model that holds it all together: **classic materials describe surfaces; Liquid Glass describes controls.** When you're building a surface, reach for a material. When you're building a control that floats above content on iOS 26, reach for glass. When in doubt, ship with the classic material — it has nine years of accessibility, performance, and rendering work behind it, and it remains the system's correct answer for most of your app.