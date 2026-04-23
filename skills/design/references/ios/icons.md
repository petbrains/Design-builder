---
name: icons
description: iOS app icon reference (iOS 18 three variants, iOS 26 Icon Composer + Liquid Glass + 6 appearances)
platform: ios
---

# The complete app icon reference for iOS 18 and iOS 26

**Apple's app icon system changed more in 18 months than in the previous decade.** iOS 18 (2024) introduced three user-selectable appearance variants — Light, Dark, and Tinted — forcing developers to ship three 1024×1024 PNGs instead of one. iOS 26 (2025) replaced that workflow again: a single layered **.icon** file built in the new **Icon Composer** app now generates six appearances (Default, Dark, Clear Light, Clear Dark, Tinted Light, Tinted Dark) rendered through the system's **Liquid Glass** material, with specular highlights that track device motion via the gyroscope. This document is a complete, citable reference covering geometry, variants, Icon Composer, Liquid Glass, per-platform sizes, asset catalog structure, alternate icons, testing, and anti-patterns — with code, tables, and WWDC session references throughout.

---

## 1. Icon grid and geometry

### The 1024 × 1024 master canvas

Every modern Apple app icon is designed on a **1024 × 1024 px** master canvas, exported as flat PNG in sRGB (or Display P3 for wide-gamut), **fully opaque with no alpha channel**, and **with square corners**. Since Xcode 14 you can supply a **single 1024 × 1024 "Any Appearance"** asset and the toolchain generates every smaller runtime size at build time (WWDC22 session 110427, "The craft of asset catalogs"). For watchOS icons authored in Icon Composer the canvas expands to **1088 × 1088 px**, with the circular mask centered inside — this lets designers work on the same golden-ratio grid as rectangular icons and still get a clean circular crop (WWDC25 session 361).

### Why Apple's corners aren't rounded rectangles — the squircle

The mask iOS applies is **not** a plain rounded rectangle. It is a **squircle**, a special case of a superellipse whose curvature is continuous (G2 continuity) rather than suddenly transitioning from straight edge to arc. Early community reverse-engineering by Marc Edwards (bjango) approximated it as |x/a|ⁿ + |y/a|ⁿ = 1 with n ≈ 5; Figma's engineering team later showed ("Desperately seeking squircles") that Apple actually uses a piecewise Bézier approximation. The effective parameters are **~22.37% corner radius** relative to side length with **~60% corner smoothing** (squircle.js.org analysis). The practical implementation on iOS is `UIBezierPath(roundedRect:cornerRadius:)` with `.continuous` corner curve, or SwiftUI's `RoundedRectangle(cornerRadius:style: .continuous)`.

**Apple's rule is absolute: do not pre-round corners.** The HIG says *"Keep icon corners square. The system applies a mask that rounds icon corners automatically."* Pre-rounded art sits inside the system mask and produces a doubly-rounded, too-tight corner — and can trigger App Store rejection. This applies to iOS, iPadOS, tvOS, CarPlay, and (since macOS Big Sur) Mac. watchOS uses a circular mask; design square and let the system crop it.

### The golden ratio icon grid

Apple's official icon template (shipped in the Apple Design Resources for Figma, Sketch, Illustrator, and Photoshop) overlays the 1024 canvas with three nested systems:

1. A **16 × 16 px base unit** subdivision (a 64 × 64 unit grid across the full canvas) for fine element alignment.
2. A set of **concentric circles and rectangles whose proportions follow φ = 1.618**. The defining rectangle is **512 × 320 px** (ratio 1.6 ≈ φ); rotating and inscribing this rectangle generates the nested primary-shape circles — typically a large outer circle at ~80% canvas width and smaller φ-scaled inner circles.
3. The **squircle keyline** — the iOS Home Screen mask — inset inside the canvas. Art that must remain visible after masking should live inside this squircle; the visible keyline leaves a ~10% margin on all four sides, so **content typically occupies about 80% of the canvas**.

Additional geometric progressions (Pentagon Progression → φ; Square Progression → √2) appear in Apple's template as optical references (Design By Geometry's recreation of the grid).

### Optical centering vs geometric centering

**Geometric centering** places an element's bounding box at (width/2, height/2). **Optical centering** places it where it *appears* centered — weight distribution, negative space, asymmetric silhouettes, and contrast all shift the perceived center. Apple's HIG endorses optical alignment: *"parts of the image can extend into [the ~10% margin] for optical alignment, it's best when the image occupies about 80% of the image canvas."* The concentric circles in the grid exist precisely so designers align to the perceived center — classic examples include play-button triangles nudged right of geometric center, and the Apple logo itself which is nudged down.

### Safe zones, keylines, and per-platform notes

The **primary safe zone** is a ~10% inset margin (about 102 px on a 1024 canvas); nothing critical should sit inside that outer band. The **keyline shapes** supplied in Apple's templates include a large circle (~820 px diameter, ~80% of canvas), inner φ-scaled circles, and the squircle mask itself — guides only, never exported. On **watchOS**, work on the 1088 × 1088 canvas but recognize the visible disc is inside it. On **tvOS**, the safe zone is 370 × 222 inside the 400 × 240 small layered icon.

---

## 2. Icon variants in iOS 18

iOS 18 (2024) introduced three user-selectable appearance variants that apply to every Home Screen and widget on the device: **Light** (the traditional default, called "Any Appearance" in Xcode), **Dark**, and **Tinted**. Users pick the mode by long-pressing the Home Screen → Edit → Customize, then choosing Light/Dark/Automatic/Tinted and dragging the **Gradient** (hue) and **Luma** (brightness) sliders.

### WWDC 2024 authoritative source

Apple did **not** release a standalone, dedicated WWDC 2024 session titled "Design app icons for iOS 18." The iOS 18 variants were officially introduced in **WWDC24 Session 102 — "Platforms State of the Union"** (icon segment at ≈ 45:04; ASL version Session 112; 5-minute recap Session 111977). Complementary guidance landed on the HIG "App icons" page and in the WWDC24 Design Guide news article (`/news/?id=s9s75a8k`).

Key quoted guidance from that session: *"App icons and widgets can now appear Light, Dark, or with a Tint … a tinted version of your app icon will automatically be available to your users after they upgrade to iOS 18 … crafted intelligently to preserve your design intent and maintain legibility … Xcode now supports Dark and Tinted app icon variants that you can drop right into your asset catalog."*

### Layer-separation guide — what each variant requires

| Requirement | Light (Any) | Dark | Tinted |
|---|---|---|---|
| Canvas | 1024 × 1024 px square | 1024 × 1024 px | 1024 × 1024 px |
| Background | **Opaque, fills canvas** | **Transparent** (recommended) or custom dark | **Opaque black (#000000)** — system draws gradient on top |
| Foreground | Full-color artwork | Muted foreground, **avoid pure white** | **Grayscale only**; use opacity and gradients for depth |
| Transparency allowed | No | Yes, on background | On foreground only; background must be opaque black |
| Color space | sRGB / Display P3 | sRGB / Display P3 | **Gray Gamma 2.2** |
| System adds | Corner mask only | Dark gradient background (≈ #313131 → #141414) | Dark gradient + user's hue/luma tint |
| Fallback | Used on iOS < 18 | Auto-generated from Light if omitted | Auto-generated from Light if omitted |

### How the system processes tinted icons

The tint pipeline is **luminance-driven**: the system reads the grayscale value of each pixel in your tinted PNG and uses it as a mix factor against the user's chosen hue. Bright pixels receive full tint; dark pixels recede toward the background gradient. The Home Screen customization sheet exposes two sliders — the upper **Gradient slider** selects hue, the lower **Luma slider** adjusts brightness — plus an **eyedropper** that samples a color from the wallpaper.

Because only luminance matters, flat single-value glyphs look dead in tinted mode. Apple and Sketch both recommend **varying opacity and adding gradients** (a 100% → 60% luminance ramp is a common starting point) so the icon has internal depth once tinted. If you don't supply a tinted variant, iOS auto-generates one from the Light PNG using on-device inspection of foreground/background colors — results are inconsistent, so always ship one explicitly.

### Dark variant specifics

The system composites your foreground over a dark gradient that (as measured by Guillem Bruix) runs roughly **#313131 at the top to #141414 at the bottom**. You can either omit the background (transparent PNG, recommended) and let the gradient show through, or ship a full opaque dark icon with your own background if you need tighter brand control. *"Color backgrounds generally offer the greatest contrast in dark icons"* (HIG). Use your Light icon as the starting point, choose complementary colors, avoid excessively bright images, and avoid pure white — it's harsh against the gradient.

---

## 3. Icon Composer and the iOS 26 workflow

At WWDC 2025 Apple introduced **Icon Composer**, a standalone macOS app that builds layered `.icon` files rendered by the system through the Liquid Glass material. It ships with **Xcode 26** and as a free **standalone download** from `developer.apple.com/icon-composer/`. It requires macOS Sequoia or later (macOS 26 Tahoe is recommended so Liquid Glass renders natively). Presented at **WWDC25 Session 361 — "Create icons with Icon Composer"** by Apple designer Lyam, and supported by **Session 220 — "Say hello to the new look of app icons"** (Marie), **Session 219 — "Meet Liquid Glass"**, and **Session 356 — "Get to know the new design system."**

### What changed vs iOS 18

| Aspect | iOS 18 | iOS 26 |
|---|---|---|
| Source artworks | Up to 3 flat PNGs (Light / Dark / Tinted) | Single layered **`.icon`** bundle |
| File format | PNG in `AppIcon.appiconset` | `.icon` package compiled to `iconstack` inside `Assets.car` |
| Layer model | Flat raster per appearance | 1–4 groups, multiple layers per group, per-layer glass controls |
| Material effects | Designer bakes in every shadow, highlight, bevel | System applies specular, blur, shadow, tint at render time |
| Gyro response | None | Specular highlights track device motion |
| Tinted mode | Monochrome tint post-processed over image | Color infused into glass body (Tinted Light) or foreground (Tinted Dark) |
| Canvas | 1024 iOS; free-form Mac | Unified 1024 (iPhone/iPad/Mac) + 1088 (Watch) |
| Authoring tool | None required | Icon Composer (Xcode 26+) |
| Backward compatibility | N/A | `.icon` only supported by Xcode 26+; legacy PNG catalogs still work |

### The layer / group model

From Lyam's session: *"In Icon Composer, groups control how elements stack and receive glass properties. By default, it'll always be one, but you can go all the way up to **four**. We found this number provides the right bounds for how much visual complexity an icon should have."* Multiple layers can sit inside each group (no hard per-group layer cap was stated). Each group can toggle Liquid Glass on or off, independently adjust specular highlights, blur, translucency, opacity, blend mode, and choose between a **neutral shadow** or a **chromatic shadow** that spills color from the artwork onto the background.

```
┌─────────────────────────────────────────────────────────┐
│  SYSTEM MASK (rounded rect 1024 px or circle 1088 px)   │  ← applied at render
├─────────────────────────────────────────────────────────┤
│  SYSTEM-RENDERED MATERIAL LAYER                         │
│   • Specular edge highlight (gyro-responsive on iOS)    │
│   • Frostiness / blur (per-group setting)               │
│   • Shadow (neutral or chromatic)                       │
├─────────────────────────────────────────────────────────┤
│  GROUP 4 (optional)  ← topmost piece of glass           │
│  GROUP 3 (optional)                                     │
│  GROUP 2 (optional)                                     │
│  GROUP 1 (always present)                               │
├─────────────────────────────────────────────────────────┤
│  CANVAS BACKGROUND                                      │
│  (solid color, gradient, or System Light/System Dark)   │
└─────────────────────────────────────────────────────────┘
Per-appearance variants: Default | Dark | Mono
  → renders Default / Dark / Clear-Light / Clear-Dark /
    Tinted-Light / Tinted-Dark
```

### File format, input layers, and export

The `.icon` format is a **macOS bundle / package** containing layered source assets (SVG preferred; PNG for rasters that need custom gradients or textures) plus metadata describing Liquid Glass properties per appearance. When dragged into Xcode 26, the build system compiles it into an **`iconstack`** entry inside `Assets.car` with vector layer data (confirmed via `assetutil` in Apple Developer Forums thread 794485). Do **not** include the corner mask in any layer export; the system applies it. Convert fonts to outlines before exporting SVG.

**Export options.** The primary path is: save the `.icon`, drag it into the Xcode Project Navigator, and set its name in the target's **General → App Icons and Launch Screen → App Icon** field. A project can contain multiple `.icon` files (useful for alternate icons), but only one per target can match the primary App Icon field. A secondary **marketing export** produces flattened PNGs at various sizes and modes for App Store screenshots and promotional use. There is no need to hand-generate size variants — Liquid Glass materials scale automatically.

### Six appearances from three artwork tracks

Inside Icon Composer you annotate only **three** tracks — **Default**, **Dark**, and **Mono** (the former Tinted). From these, the system renders **six** runtime appearances: Default, Dark, Clear Light, Clear Dark, Tinted Light, and Tinted Dark. The Mono artwork produces both Clear and Tinted variants automatically.

### Known issues as of April 2026

Icon Composer was labeled "beta" at WWDC 2025 and continues to receive updates. Reported issues: thin white alpha-channel "fringe" around icons during launch/close transitions in some `.icon`-built apps; occasional alpha-channel validation failures on App Store Connect upload; iMessage extension icons still not natively generated through Icon Composer; visionOS icons still use the older Parallax Previewer workflow; and on Xcode 26 beta builds, `AssetCatalogSimulatorAgent` could inflate build times when `.icon` files are present. Apple's Developer Forums track these under the "Icon Composer" tag.

---

## 4. Liquid Glass icons

Liquid Glass is the cross-platform design language Apple introduced at WWDC 2025 ("Meet Liquid Glass," Session 219) and shipped in iOS 26, iPadOS 26, macOS 26 Tahoe, watchOS 26, tvOS 26, and visionOS 26. For app icons, Apple designer Marie described it (Session 220) as: *"We drew inspiration from the layered icons on visionOS and researched real glass properties to then combine that into this liquid glass material specifically for app icons. The material layers different elements like edge highlights, frostiness, and translucency to not only add a sense of depth, but it really makes it seem as if the icons are lit from within."*

### What the system renders — and what you supply

**System-applied at render time:**
- Edge highlights and specular reflections that respond to the gyroscope on iPhone, iPad, and Apple Watch
- Frostiness (system-grade blur) on layers marked translucent
- Drop shadows (neutral or chromatic), auto-scaled to icon size
- Chromatic response to wallpaper and environment
- Rounded-rectangle or circle mask (you never draw it)
- Automatic scaling to every resolution
- Automatic adaptation across all six appearance modes

**Designer-supplied:**
- Flat, opaque layered source art (SVG or PNG)
- Per-layer fills, opacity, blend modes
- Choice of which layers get glass treatment
- Neutral vs chromatic shadow per group
- Specular highlight on/off per group
- Per-appearance overrides (Default / Dark / Mono)

### Specular highlights and tilt

Specular highlights are **dynamic, real-time edge reflections** rendered on each glass layer's outline. On iPhone, iPad, and Apple Watch they track **gyroscope input** — *"light moving on the edge of the icon, which feels like it's reflecting the world around you"* (Marie). On macOS 26 there's no gyro, so the light angle is currently locked near 45° (a criticism raised by Riccardo Mori). You can disable specular per group, which helps on narrow or pillowy shapes like the date inside the Calendar icon. Apple explicitly recommends **rounded corners over sharp ones** because *"light navigates better on rounded corners."*

### Translucency, refraction, and material treatments

Glass layers let light through, lighting the layers beneath them. In Clear modes, all layers become near-transparent glass and the wallpaper shows through them. Apple describes the technical differentiator as **lensing** — Liquid Glass *bends and concentrates* light in real time, whereas traditional system blur (iOS 7 through iOS 18) *scatters* it. The vocabulary in Icon Composer exposes **glass** (default Liquid Glass) and **frosted** (increased blur + translucency). Metallic looks come from combining specular + chromatic shadow + opaque fills rather than from a dedicated preset.

### New rounder grid and concentricity

iOS 26 uses a **rounder corner radius** on the shared 1024 px iPhone/iPad/Mac grid, deliberately concentric with hardware bezel radii and system UI containers (SwiftUI exposes this via `containerConcentric` shapes). macOS icons are now forced into the rounded rectangle; legacy free-form Mac icons are auto-masked at install time — a change Stephen Hackett (512 Pixels) publicly criticized as "icons in squircle jail."

### Interaction with iOS 18's variants

iOS 18's Light/Dark/Tinted model is preserved and extended, not replaced. Icon Composer's three authored tracks (Default / Dark / Mono) map to six runtime appearances. An app that ships a plain PNG asset catalog still works on iOS 26 — the system will add edge specular and a dark gradient automatically — but won't get per-layer glass effects or gyro-responsive specular.

### Noted refinements post-launch

Stephen Hackett reported that **iOS 26.1 Beta 4** (October 2025) added a **Clear ↔ Tinted toggle** in Settings → Display & Brightness (and System Settings → Appearance on Mac) — the first major system-level refinement to Liquid Glass after launch. No major Liquid Glass changes have been announced since then; in April 2026 Apple updated the Liquid Glass Design Gallery with third-party adopters including AllTrails, Carrot Weather, Fantastical, Kroger, SketchPro, Trello, and Le Monde.

---

## 5. Technical specs — complete size tables

### iPhone (iOS 18 / iOS 26)

| Purpose | Points | @2x (pixels) | @3x (pixels) |
|---|---|---|---|
| Home Screen (iPhone) | 60 pt | 120 × 120 | **180 × 180** |
| Spotlight | 40 pt | 80 × 80 | 120 × 120 |
| Settings | 29 pt | 58 × 58 | 87 × 87 |
| Notifications | 20 pt | 40 × 40 | 60 × 60 |
| iOS 18 "Large" icon mode | 64 pt | 128 × 128 | 192 × 192 |
| App Store / Marketing | — | — | 1024 × 1024 @1x |

### iPad (iPadOS 18 / iPadOS 26)

| Purpose | Points | @1x (pixels) | @2x (pixels) |
|---|---|---|---|
| Home Screen (standard iPad / mini) | 76 pt | 76 × 76 | **152 × 152** |
| Home Screen (iPad Pro) | 83.5 pt | — | **167 × 167** |
| Spotlight (iPadOS 14+) | 40 pt | 40 × 40 | 80 × 80 |
| Settings | 29 pt | 29 × 29 | 58 × 58 |
| Notifications | 20 pt | 20 × 20 | 40 × 40 |
| iOS 18 Large mode (iPad Pro 13″) | 68 pt | — | 136 × 136 |
| App Store | — | — | 1024 × 1024 |

### macOS

| Point size | @1x (pixels) | @2x (pixels) |
|---|---|---|
| 16 pt | 16 × 16 | 32 × 32 |
| 32 pt | 32 × 32 | 64 × 64 |
| 128 pt | 128 × 128 | 256 × 256 |
| 256 pt | 256 × 256 | 512 × 512 |
| 512 pt | 512 × 512 | 1024 × 1024 |
| 1024 pt (App Store) | 1024 × 1024 | — |

Mac icons use a system drop-shadow template and, since macOS Big Sur, a rounded-superellipse mask; macOS 26 Tahoe layers Liquid Glass on top.

### watchOS

| Role | 38/40/41 mm | 42/44/45 mm | 49 mm Ultra |
|---|---|---|---|
| Notification Center (24 pt @2x/@3x) | 48 × 48 | 55 × 55 | 66 × 66 |
| Companion Settings | 58 × 58 | 87 × 87 | — |
| Long Look Notification | 80 × 80 | 88 × 88 | 108 × 108 |
| Home Screen / Short Look | 80 × 80 (40 mm) · 92 × 92 | 100 × 100 (44 mm) · 102 × 102 (45 mm) | 117 × 117 |
| Quick Look (45 mm) | — | 216 × 216 | — |
| Short-Look Full Screen | 172 × 172 | 196 × 196 | 234 × 234 |
| App Store marketing | — | — | 1024 × 1024 |
| Icon Composer master | — | — | **1088 × 1088** |

### tvOS (layered `.imagestack`)

| Asset | Size | Notes |
|---|---|---|
| App Icon — Small (Home Screen) | 400 × 240 | Layered; safe zone 370 × 222; unfocused 300 × 180 |
| App Icon — Large (App Store / focus) | 1280 × 768 | Layered |
| Top Shelf Image (static) | 1920 × 720 | 16:9 fallback |
| Top Shelf Image Wide | 2320 × 720 | Ultra-wide |
| Top Shelf Dynamic | 3840 × 1440 / 4640 × 1440 | Optional |
| Launch Image | 1920 × 1080 | Optional |

### CarPlay

| Purpose | @2x | @3x |
|---|---|---|
| CarPlay App Icon (60 pt) | 120 × 120 | 180 × 180 |

Provide square artwork; the system applies the rounded-rectangle mask.

### App Store marketing icon

**1024 × 1024 px, PNG, sRGB or Display P3, fully opaque, no alpha, square corners.** Required for every submission across iOS, iPadOS, macOS, watchOS, tvOS, and visionOS. Since Xcode 9 / iOS 11 it **must live inside the asset catalog** in the App Store slot; App Store Connect no longer accepts a separate upload for iOS apps.

### Asset catalog structure

```
MyApp/
└── Assets.xcassets/
    ├── Contents.json
    └── AppIcon.appiconset/
        ├── Contents.json
        ├── AppIcon-1024.png         (Any Appearance, opaque)
        ├── AppIcon-1024-dark.png    (iOS 18+ Dark, transparent bg)
        └── AppIcon-1024-tinted.png  (iOS 18+ Tinted, grayscale on black)
```

Modern (iOS 18 / iOS 26) single-size `Contents.json` with appearance variants:

```json
{
  "images" : [
    {
      "idiom" : "universal",
      "platform" : "ios",
      "size" : "1024x1024",
      "filename" : "AppIcon-1024.png"
    },
    {
      "appearances" : [
        { "appearance" : "luminosity", "value" : "dark" }
      ],
      "idiom" : "universal",
      "platform" : "ios",
      "size" : "1024x1024",
      "filename" : "AppIcon-1024-dark.png"
    },
    {
      "appearances" : [
        { "appearance" : "luminosity", "value" : "tinted" }
      ],
      "idiom" : "universal",
      "platform" : "ios",
      "size" : "1024x1024",
      "filename" : "AppIcon-1024-tinted.png"
    }
  ],
  "info" : { "author" : "xcode", "version" : 1 }
}
```

In Xcode 16 and later, select the `AppIcon` set, open the Attributes Inspector (⌥⌘4), set **iOS → Single Size** and **Appearances → Any, Dark, Tinted**, then drop your three 1024s into the wells. In Xcode 26, dragging a `.icon` file into the target replaces the whole workflow and generates all six Liquid Glass appearances automatically.

---

## 6. Marketing icon vs app icon

Historically Apple called the 1024 × 1024 App Store icon the "marketing icon" or "iTunes artwork." Today it's simply the largest entry in your `AppIcon` asset catalog — a flat PNG at 1024 × 1024 that Apple's CDN serves on the App Store product page and that Xcode uses as the master for auto-generating all smaller sizes. **The marketing icon and the app icon should be the same image.** Shipping a visually different App Store icon is both against HIG guidance (the HIG requires visual consistency across contexts) and confusing to users trying to find your app after install.

| Attribute | Requirement |
|---|---|
| Pixel dimensions | **1024 × 1024 px, exact** |
| File format | **PNG**, 24-bit, flat |
| Color space | **sRGB** (`sRGB IEC61966-2.1`) or **Display P3** (wide-gamut) |
| Transparency / alpha | **None — fully opaque** |
| Layers | Flattened |
| Shape | **Square**, no pre-rounded corners |
| Placement | Asset catalog "App Store" slot; no separate upload to App Store Connect |
| Dark variant (iOS 18+) | 1024 × 1024 PNG, transparent background |
| Tinted variant (iOS 18+) | 1024 × 1024 grayscale PNG on opaque black |
| iOS 26 option | Supplied via `.icon` file in Icon Composer; marketing PNGs exported from same source |

The permissible differences are small: you may *simplify* details that survive at 1024 px but read as noise at 29 × 29 (for example, dropping a thin decorative line), but the core silhouette, color palette, and composition must match. Apps in the App Store Product Page Optimization program can A/B test alternate icons declared through `CFBundleAlternateIcons`; industry studies (Storemaven, SplitMetrics) cite conversion-rate deltas of 20–30% from icon iteration alone.

---

## 7. Design principles

Apple's HIG distills app icon design into a short, stubborn list of principles that haven't substantially changed across iOS 7, iOS 18, and iOS 26:

**Embrace simplicity.** *"Simple icons tend to be easiest for people to understand and recognize. An icon with fine visual features might look busy when rendered with system-provided shadows and highlights, and details may be hard to discern at smaller sizes."* Find a single concept that captures your app's essence and express it with a minimal number of shapes.

**Build a recognizable silhouette.** A unique, memorable mark helps people find your app at a glance on a crowded Home Screen. Shape carries more weight than color under iOS 18's Tinted mode (which strips color entirely) and iOS 26's Clear modes (which make everything translucent).

**Avoid text — with one exception.** *"Include text only when it's essential to your experience or brand. Text in icons doesn't support accessibility or localization, is often too small to read easily."* The permitted exception is **logotype brands** whose identity *is* the letterform — Facebook's "f," Gmail's "M," Pinterest's "P." The home screen already shows the app name below the icon; repeating it wastes the canvas.

**Prefer illustration over photography.** *"Photos are full of details that don't work well when displayed in different appearances, viewed at small sizes, or split into layers."* Photos also lose definition the moment the squircle mask crops them.

**Stay consistent with your brand.** Icons should look like they belong to your product across platforms and should not contradict app-store screenshots, launch screens, or the app's primary UI.

**Keep core features consistent across appearances.** *"Keep your icon's core visual features the same in the default, dark, clear, and tinted appearances. Avoid creating custom icon variants that swap elements in and out with each variant."*

**Let the system handle effects.** *"The system dynamically applies visual effects to your app icon layers, so there's no need to include specular highlights, drop shadows between layers, beveled edges, blurs, glows, and other effects."*

### Test at 29 × 29 and 40 × 40 — the sizes that break icons

The two most punishing sizes are **Settings (29 × 29)** and **Spotlight (40 × 40)**. Every design decision should survive these. The practical workflow:

1. Design your 1024 master.
2. Export a 29 × 29 PNG and a 40 × 40 PNG.
3. Place both side-by-side with real iOS chrome (a Settings row, a Spotlight result row).
4. Ask: Is the silhouette readable? Do thin strokes or small text disappear? Does the focal element survive masking?
5. Iterate on the master until the shrunk versions still read.

Design at small sizes *first*; scale up second. A good icon looks inevitable at 29 × 29 and merely finished at 1024.

---

## 8. Alternate icons

The alternate app icon API landed in **iOS 10.3 (2017)** and lets users pick from a developer-defined set of icons bundled with the app. The system provides the confirmation alert (*"You have changed the icon for …"*); everything else is your UI.

### The UIKit API

Three properties and one method on `UIApplication`:

- **`supportsAlternateIcons: Bool`** — always check before exposing UI. Returns `true` only when the device/app combination permits icon changes.
- **`alternateIconName: String?`** — the name of the currently active alternate, or `nil` if the primary is showing.
- **`setAlternateIconName(_:completionHandler:)`** — pass a name to switch, or `nil` to revert. Must be called on the main thread, and not during `didFinishLaunchingWithOptions` (which returns `NSCocoaErrorDomain 3072`).
- **`setAlternateIconName(_:) async throws`** — Swift concurrency variant.

### Asset placement — two workflows

**Modern (Xcode 13+):** Add each alternate as a separate **iOS App Icon** asset inside `Assets.xcassets`. Then either turn on build setting **"Include all app icon assets"** (`ASSETCATALOG_COMPILER_INCLUDE_ALL_APPICON_ASSETS = YES`) or list the asset names in **"Alternate App Icon Sets"** (`ASSETCATALOG_COMPILER_ALTERNATE_APPICON_NAMES`). Xcode injects the correct `CFBundleIcons` / `CFBundleAlternateIcons` entries at build. **This is the only supported path for iOS 18+ Dark and Tinted variants** — each alternate icon set must itself enable all three Appearances.

**Legacy (pre-Xcode 13):** Place files loose at the **app bundle root** (not inside the asset catalog), using `IconName@2x.png` / `IconName@3x.png` naming (plus `~ipad` variants), and hand-write the `Info.plist` keys.

### Info.plist structure

```xml
<key>CFBundleIcons</key>
<dict>
    <key>CFBundlePrimaryIcon</key>
    <dict>
        <key>CFBundleIconFiles</key>
        <array>
            <string>AppIcon</string>
        </array>
        <key>UIPrerenderedIcon</key>
        <false/>
    </dict>
    <key>CFBundleAlternateIcons</key>
    <dict>
        <key>DarkIcon</key>
        <dict>
            <key>CFBundleIconFiles</key>
            <array><string>DarkIcon</string></array>
            <key>UIPrerenderedIcon</key>
            <false/>
        </dict>
        <key>HalloweenIcon</key>
        <dict>
            <key>CFBundleIconFiles</key>
            <array><string>HalloweenIcon</string></array>
            <key>UIPrerenderedIcon</key>
            <false/>
        </dict>
        <key>ProIcon</key>
        <dict>
            <key>CFBundleIconFiles</key>
            <array><string>ProIcon</string></array>
            <key>UIPrerenderedIcon</key>
            <false/>
        </dict>
    </dict>
</dict>

<!-- Required for universal apps — iPad uses its own siblings -->
<key>CFBundleIcons~ipad</key>
<dict>
    <key>CFBundlePrimaryIcon</key>
    <dict>
        <key>CFBundleIconFiles</key>
        <array><string>AppIcon</string></array>
        <key>UIPrerenderedIcon</key>
        <false/>
    </dict>
    <key>CFBundleAlternateIcons</key>
    <dict>
        <key>DarkIcon</key>
        <dict>
            <key>CFBundleIconFiles</key>
            <array><string>DarkIcon</string></array>
            <key>UIPrerenderedIcon</key>
            <false/>
        </dict>
    </dict>
</dict>
```

### Swift — production-ready icon switcher

```swift
import UIKit

enum IconSwitcher {

    enum Icon: String, CaseIterable, Identifiable {
        case primary   = "AppIcon"
        case dark      = "DarkIcon"
        case halloween = "HalloweenIcon"
        case pro       = "ProIcon"

        var id: String { rawValue }

        /// Value to pass to setAlternateIconName — nil means "revert to primary."
        var apiName: String? { self == .primary ? nil : rawValue }
    }

    static var current: Icon {
        if let name = UIApplication.shared.alternateIconName,
           let icon = Icon(rawValue: name) { return icon }
        return .primary
    }

    @MainActor
    static func setIcon(_ icon: Icon) async throws {
        guard UIApplication.shared.supportsAlternateIcons else {
            throw NSError(domain: "IconSwitcher", code: -1,
                          userInfo: [NSLocalizedDescriptionKey:
                                     "Alternate icons are not supported on this device."])
        }
        guard icon.apiName != UIApplication.shared.alternateIconName else { return }
        try await UIApplication.shared.setAlternateIconName(icon.apiName)
    }

    /// Completion-handler variant. Always pass a non-nil handler — nil has been
    /// reported to crash on some iOS versions when the call errors out.
    static func setIcon(_ icon: Icon,
                        completion: ((Result<Void, Error>) -> Void)? = nil) {
        guard UIApplication.shared.supportsAlternateIcons else {
            completion?(.failure(NSError(domain: "IconSwitcher", code: -1)))
            return
        }
        guard icon.apiName != UIApplication.shared.alternateIconName else {
            completion?(.success(())); return
        }
        UIApplication.shared.setAlternateIconName(icon.apiName) { error in
            DispatchQueue.main.async {
                if let error = error { completion?(.failure(error)) }
                else { completion?(.success(())) }
            }
        }
    }
}
```

### SwiftUI picker

```swift
import SwiftUI
import UIKit

@MainActor
final class IconSettings: ObservableObject {
    @Published private(set) var current: IconSwitcher.Icon = IconSwitcher.current
    @Published var errorMessage: String?

    func change(to icon: IconSwitcher.Icon) {
        Task {
            do {
                try await IconSwitcher.setIcon(icon)
                current = icon
            } catch {
                errorMessage = error.localizedDescription
            }
        }
    }
}

struct AppIconPicker: View {
    @StateObject private var settings = IconSettings()

    var body: some View {
        List {
            Section("Choose App Icon") {
                ForEach(IconSwitcher.Icon.allCases) { icon in
                    Button { settings.change(to: icon) } label: {
                        HStack(spacing: 12) {
                            // Note: Image(named:) cannot read App Icon sets, so ship
                            // a matching Image Set with "-Preview" suffix for previews.
                            Image("\(icon.rawValue)-Preview")
                                .resizable()
                                .frame(width: 60, height: 60)
                                .clipShape(RoundedRectangle(cornerRadius: 14,
                                                            style: .continuous))
                            Text(icon.rawValue)
                            Spacer()
                            if settings.current == icon {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundStyle(.tint)
                            }
                        }
                    }
                }
            }
        }
        .navigationTitle("App Icon")
        .alert("Couldn't change icon",
               isPresented: .init(
                 get: { settings.errorMessage != nil },
                 set: { if !$0 { settings.errorMessage = nil } })
        ) {
            Button("OK", role: .cancel) { }
        } message: { Text(settings.errorMessage ?? "") }
    }
}
```

### Common use cases

Theme variants (pre-iOS 18 apps emulating Dark mode), **premium/subscription unlocks** (PDF Viewer by Nutrient, Reddit's OrangeRed for Premium, Tinder Gold), seasonal skins (Halloween, Christmas, Lunar New Year), team/sports fandom variants (scoreboard apps), special event tie-ins (game or movie launches), onboarding personalization (GitHub's Octocat variants, Duolingo, Reddit), and **A/B testing** via App Store Product Page Optimization.

### The confirmation alert — can it be suppressed?

**Officially, no.** Apple Developer Forums thread 723928 explicitly confirms that the system alert is intentional user consent; private selectors like `_setAlternateIconName:completionHandler:` will get the app rejected under Section 5.2 of App Review. The only App Store–safe pattern is to gate the call behind an explicit user tap so the alert feels expected.

### iOS 18+: each alternate icon needs Dark and Tinted

*"Alternate app icons in iOS and iPadOS require their own dark and tinted variants"* (HIG). Because tinting strips color, color-only alternate sets collapse to visual duplicates under Tinted mode — vary **shape**, not just palette, across alternates designed for iOS 18 and later. For iOS 26, Apple's direction is to author each alternate as its own `.icon` file and reference the names through the same `CFBundleAlternateIcons` mechanism.

---

## 9. Common mistakes and anti-patterns

| # | Anti-pattern | Why it fails | Do this instead |
|---|---|---|---|
| 1 | **Photograph as icon** | Hundreds of tones and fine detail become noise at 29 × 29; edges muddy under the squircle mask | Treat it like a logo: one bold symbol, 1–3 colors |
| 2 | **Too much detail** | What reads rich at 1024 vibrates or disappears at 60 | Design at 29 × 29 *first*, then scale up |
| 3 | **Off-center composition** | Geometric centers look tilted inside an asymmetric mask | Nudge for **optical center**; use the grid |
| 4 | **Ignoring Dark variant** | Flat white-on-gradient looks like a cutout; opaque dark icon hides the system gradient | Transparent PNG with muted foreground and no pure white |
| 5 | **Ignoring Tinted variant** | Multi-color logos collapse to a gray blob under tinting | Ship a grayscale image with luminance variation for depth |
| 6 | **Text-heavy icons** | Unreadable below 180 px; home screen label is redundant | Drop the wordmark unless you're a single-letter logotype brand |
| 7 | **Pre-rounding corners** | Sits inside the system mask → ugly double-rounded gap | Ship a square PNG; never pre-mask |
| 8 | **Baked-in drop shadows / gloss** | System layers its own lighting; pre-baked effects stack dirty | Flat artwork, no shadows, no gloss |
| 9 | **UI screenshots as icon** | Tiny toggles and chat bubbles look generic and scammy; HIG bans depictions of Apple UI | Abstract symbol of the app's purpose |
| 10 | **Cloning competitor icons** | Section 5.2 App Review rejection; users read it as a scam | Build a distinct mark from your own brand language |
| 11 | **Poor Dark-mode contrast** | Mid-gray on mid-gray gradient is invisible at small sizes | Brighten focal element; test against both system gradients |
| 12 | **Transparent Light variant** | Composites over black — almost never intended | Light = fully opaque; only Dark and Tinted use transparency |
| 13 | **Thin strokes / 1-px lines** | Vanish on Settings and Spotlight rows | Stroke width ≥ 3% of icon size; prefer filled shapes |
| 14 | **Full-color gradients with no luminance variation** | Converts to flat gray when tinted | Use luminance-driven vertical gradients so tint preserves shape |
| 15 | **Private-API tricks to suppress alert** | App Review rejection | Trigger switches only from explicit user taps |
| 16 | **Color-only alternate icons post-iOS 18** | All alternates look identical in Tinted mode | Vary shape across alternates |
| 17 | **Forgetting `CFBundleIcons~ipad`** (legacy workflow) | Alternates silently fail on iPad | Duplicate the block, or migrate to the asset-catalog workflow |
| 18 | **Mixing bundle-root and catalog alternates** | Lookup breaks | Pick one workflow and commit |
| 19 | **Chasing visual trends** | Re-skinning every 1–2 years erodes brand recognition | Prioritize silhouette and brand over current fashion |
| 20 | **Not testing against busy wallpapers** | Icon disappears on photo backgrounds | Preview on bright, dark, and busy wallpapers |

---

## 10. Testing

### Configure Xcode correctly

Open `Assets.xcassets` → select `AppIcon` → Attributes Inspector (⌥⌘4). For iOS 18, set **iOS → Single Size** and **Appearances → Any, Dark, Tinted**, then drop three 1024 PNGs into the wells. For iOS 26, drag a `.icon` file into the project and set it as the App Icon in target settings. Requires **Xcode 16** (iOS 18) or **Xcode 26** (iOS 26).

### Simulator and device Dark-mode preview

In Simulator, **Features → Toggle Appearance (⇧⌘A)** flips Light/Dark. On a device, Settings → Display & Brightness → Dark (or the Control Center toggle). Always test on both.

### Home Screen appearance preview

On iOS 18/26 devices:

1. Long-press empty Home Screen space (enter jiggle mode).
2. Tap **Edit** → **Customize**.
3. Choose **Light / Dark / Automatic / Tinted**.
4. For Tinted: drag the upper **Gradient** slider (hue), the lower **Luma** slider (brightness); tap the **eyedropper** to sample the wallpaper.
5. Toggle **Small / Large** icon sizes (Large hides labels).
6. Tap the sun icon to dim the wallpaper and recheck contrast.

On iOS 26 additionally try the **Clear ↔ Tinted** toggle in Settings → Display & Brightness (added in iOS 26.1 Beta 4).

### Context-specific previews

- **Spotlight** — swipe down on Home Screen, type app name → confirms 40 × 40 rendering.
- **Settings** — scroll to your app → confirms 29 × 29 rendering (a common failure spot; icons relying on auto-generated Dark often show black boxes here — fix by shipping an explicit Dark variant).
- **Notification Center** — send a local notification → check 38 × 38 rendering in banner and grouped lists.
- **App Library** — swipe past last Home Screen page.
- **Share Sheet / Siri Suggestions** — open a share sheet; confirm the row of app suggestions renders cleanly.
- **TestFlight / App Store** — verify the Light variant is used on the store listing.

### Shipping checklist

- 1024 × 1024 renders crisp on the Light Home Screen
- Dark variant has no black-box artifacts in Settings or Spotlight
- Tinted variant is still readable with the Luma slider at minimum
- Tinted variant isn't blown out with the Luma slider at maximum
- Foreground silhouette reads at 40 × 40 (Spotlight) and 29 × 29 (Settings)
- Colors, glyph placement, and silhouette stay consistent across all variants
- No text is illegible below 60 × 60
- Icon is distinguishable next to Apple's own system icons
- Alternate icons (if any) ship Dark + Tinted variants
- On iOS 26, specular highlights behave correctly on tilt; `.icon` file builds cleanly

### Third-party tools

**Bakery** (Mac app) generates a full AppIcon catalog from SVG/PSD with iOS 18 variant exports. **IconKit** and **Icon Set Creator** (Mac App Store) batch-resize for every Apple platform. **Apply Pixels** ships an iOS 18 Figma/Sketch template with the three-variant grid and safe-zone margins. Apple's own **Design Resources** (developer.apple.com/design/resources/) include official Figma, Sketch, Illustrator, and Photoshop templates for both iOS 18 and iOS 26 grids. **Icon Composer** (Xcode 26+) is now Apple's preferred authoring tool.

---

## WWDC session references

- **WWDC24 Session 102 — Platforms State of the Union** — icon variants introduced at ≈ 45:04. `developer.apple.com/videos/play/wwdc2024/102/`
- **WWDC22 Session 110427 — The craft of asset catalogs** — single-size 1024 icon workflow. `developer.apple.com/videos/play/wwdc2022/110427/`
- **WWDC25 Session 219 — Meet Liquid Glass** — design language overview. `developer.apple.com/videos/play/wwdc2025/219/`
- **WWDC25 Session 220 — Say hello to the new look of app icons** (Marie) — the six appearances, Liquid Glass icons overview. `developer.apple.com/videos/play/wwdc2025/220/`
- **WWDC25 Session 356 — Get to know the new design system** (Maria). `developer.apple.com/videos/play/wwdc2025/356/`
- **WWDC25 Session 361 — Create icons with Icon Composer** (Lyam) — the `.icon` format, groups, glass controls, export. `developer.apple.com/videos/play/wwdc2025/361/`

## Primary authoritative documentation

- **HIG — App icons**: `developer.apple.com/design/human-interface-guidelines/app-icons`
- **Configuring your app icon** (asset catalog, Dark, Tinted): `developer.apple.com/documentation/xcode/configuring-your-app-icon`
- **Creating your app icon using Icon Composer**: `developer.apple.com/documentation/Xcode/creating-your-app-icon-using-icon-composer`
- **Icon Composer tool page**: `developer.apple.com/icon-composer/`
- **Apple Design Resources**: `developer.apple.com/design/resources/`
- **HIG — CarPlay icons and images**: `developer.apple.com/design/human-interface-guidelines/technologies/carplay/icons-and-images`
- **UIApplication APIs**: `setAlternateIconName(_:completionHandler:)`, `supportsAlternateIcons`, `alternateIconName`
- **Info.plist keys**: `CFBundleIcons`, `CFBundlePrimaryIcon`, `CFBundleAlternateIcons`

## Conclusion — what actually changed and what to do now

Two shifts define modern Apple icon design. First, in iOS 18, users — not designers — chose the appearance, so every icon became three icons in one asset catalog, and color-based brand differentiation stopped working under Tinted mode. Shape, silhouette, and luminance structure became the durable design signals. Second, in iOS 26, Apple pushed rendering responsibilities into the system: Liquid Glass means the OS generates specular highlights, translucency, shadows, and gyro-responsive motion at render time from a layered `.icon` source, and designers stop baking those effects into PNGs at all. The mental model for designing an app icon today is less "draw a beautiful tile" and more "compose a minimal layered scene and let the system light it." Teams shipping in April 2026 should default to Icon Composer for new work while keeping PNG asset catalogs as a fallback for apps supporting iOS 18 — and invest design time in a **single, strong silhouette** that survives all six appearance modes, tilts, wallpapers, and the 29 × 29 Settings row that will always be the test that catches everything.