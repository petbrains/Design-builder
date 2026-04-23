---
name: non-iphone-platforms
description: Apple non-iPhone platforms starter (watchOS, visionOS, tvOS with Liquid Glass)
platform: ios
---

# Apple non-iPhone platforms: a starter reference

> Target releases: **watchOS 11** (WWDC 2024) with **watchOS 26 / Liquid Glass** addenda (WWDC 2025); **visionOS 2** with **visionOS 26 / Liquid Glass** addenda; **tvOS 18** with **tvOS 26 / Liquid Glass** addenda. Scope is "enough to start designing," not exhaustive. Code samples are SwiftUI-first. Deep links point to the Apple Human Interface Guidelines (HIG), Apple developer docs, and WWDC session pages.

*Note: I was unable to write directly to `/mnt/user-data/outputs/` (no filesystem tool available in this environment). The complete markdown is below — copy it into a `.md` file to save locally.*

---

# watchOS

Apple Watch is a **glanceable, wrist-worn companion**, not a miniature phone. Design for 1–5-second interactions, let the Smart Stack, complications, and Live Activities do most of the work, and lean on the Digital Crown + Double Tap to move through content with minimal tapping. watchOS 11 added Live Activities, Training Load, and the Vitals app; watchOS 26 brought **Liquid Glass**, wrist-flick dismissal, Controls on the watch, and year-matched numbering.

## Design principles

**Glanceable first, interactive second.** Every screen should answer the user's question in one look. Put the single most important piece of information largest and nearest the top; push controls to secondary screens or Digital Crown scroll. Apple's canonical surfaces — **watch face complications, Smart Stack widgets, notifications, Live Activities** — are all part of the experience; a standalone watch app that ignores them is incomplete.

**Celebrate the shape of the display.** Use `.containerBackground(...)` (watchOS 10+) to extend color and imagery to the rounded edges, and `.scenePadding()` to keep critical text away from the corner clip. Minimize horizontal padding — the hardware bezel provides visual margin. Keep hierarchy **2–3 levels deep max**; deeper stacks disorient on a 2-inch screen.

**Default font is SF Compact** (SF Compact Rounded for complications). Rely on `Font.TextStyle` (`.largeTitle`, `.title`, `.headline`, `.body`, `.caption`) so Dynamic Type works — watchOS scales aggressively and users depend on it.

**Respect the Always-On state.** Series 5+, Ultra, and Series 10 dim to ~1 Hz refresh when the wrist lowers. Hide sensitive content, suppress continuous animation, and branch on `@Environment(\.isLuminanceReduced)` to strip chrome without losing the primary data point.

### Screen sizes

All point values are @2x (physical pixels ÷ 2). Corners are tightly rounded since Series 7; use `.scenePadding()` or `.containerBackground()` rather than pinning controls to the raw edge.

| Model | Case | Physical px | Points (pt) | PPI | Always-On |
|---|---|---|---|---|---|
| Apple Watch Series 10 | 42 mm | 374 × 446 | **187 × 223** | 326 | Yes |
| Apple Watch Series 10 | 46 mm | 416 × 496 | **208 × 248** | 326 | Yes |
| Apple Watch Ultra / Ultra 2 / Ultra 3 | 49 mm | 410 × 502 | **205 × 251** | 338 | Yes |
| Apple Watch Series 9 (context) | 41 / 45 mm | 352 × 430 / 396 × 484 | 176 × 215 / 198 × 242 | 326 | Yes |
| Apple Watch SE (2nd gen) | 40 / 44 mm | 324 × 394 / 368 × 448 | 162 × 197 / 184 × 224 | 326 | **No** |

### Complication families (WidgetKit)

watchOS 9+ consolidated ClockKit's ~12 complication slots into **four WidgetKit families**. Same family names power iOS Lock Screen widgets, so one widget can target both surfaces.

| Family | What it's for | Appears in |
|---|---|---|
| `.accessoryRectangular` | Multi-line text, small charts, progress bars | Watch faces (large slot), iOS Lock Screen, Smart Stack |
| `.accessoryCircular` | Brief info, gauges, progress rings | Watch face corners/bezel/round slots, iOS Lock Screen, Smart Stack |
| `.accessoryInline` | Single line of text + optional SF Symbol (system-colored / system-font) | Curved inline dial slot; above the time on iOS Lock Screen |
| `.accessoryCorner` | Small circle + optional curved auxiliary arc; **watchOS-only** | Infograph/Infograph-style corner slots |

## Key SwiftUI APIs

### Digital Crown

The modifier order matters: **`.focusable()` must come before `.digitalCrownRotation(...)`**. Crown input is delivered to whatever view currently has focus.

```swift
struct VolumeView: View {
    @State private var volume: Double = 50
    @FocusState private var isFocused: Bool

    var body: some View {
        Text("\(Int(volume))")
            .font(.system(size: 48))
            .focusable()
            .focused($isFocused)
            .digitalCrownRotation(
                $volume,
                from: 0, through: 100, by: 1,
                sensitivity: .medium,
                isContinuous: false,
                isHapticFeedbackEnabled: true
            )
            .onAppear { isFocused = true }
    }
}
```

Sensitivity is `.low | .medium | .high` (default `.high`). Lists and `ScrollView` consume crown input automatically — no `focusable()` needed. `@FocusState` + `focusScope(_:)` + `prefersDefaultFocus(_:in:)` let you shift crown ownership between custom views. `Docs:` [digitalCrownRotation](https://developer.apple.com/documentation/swiftui/view/digitalcrownrotation(_:from:through:by:sensitivity:iscontinuous:ishapticfeedbackenabled:)).

### Navigation — stacks, split views, vertical pages

```swift
TabView {
    NowPlayingView().navigationTitle("Now Playing")
    QueueView().navigationTitle("Up Next")
    LibraryView().navigationTitle("Library")
}
.tabViewStyle(.verticalPage)   // watchOS 10+, pairs with Digital Crown
```

Use `NavigationStack` for drill-down (keep depth ≤ 3). Use `NavigationSplitView` for source-list→detail patterns (Weather-style). Use `TabView` with **`.verticalPage`** for a flat set of peer screens; the system pulls each tab's `navigationTitle` into the header automatically. **Do not** nest a scrolling `List` inside vertical-page tabs except in the last tab — users will change pages while trying to scroll.

### Double Tap and hand gesture shortcuts

Supported on **Series 9, Series 10, Series 11, Ultra 2, Ultra 3**. watchOS 11 auto-scrolls lists, scroll views, and `.verticalPage` tab views under Double Tap with zero code. Designate one **primary action** per screen with `handGestureShortcut`:

```swift
Button { toggleCall() } label: {
    Label("Answer", systemImage: "phone.fill")
}
.buttonStyle(.borderedProminent)
.handGestureShortcut(.primaryAction)
```

Only `.primaryAction` is supported — other gestures are reserved for AssistiveTouch. The system outlines the matching control before firing; `.clipShape` customizes the highlight. `Docs:` [Enabling Double Tap](https://developer.apple.com/documentation/watchos-apps/enabling-double-tap).

### Haptics — `WKHapticType`

watchOS uses a **single call into `WKInterfaceDevice`**, not iPhone's `UIFeedbackGenerator` family. Nine fixed cases; no `prepare()`, no custom patterns.

```swift
import WatchKit

WKInterfaceDevice.current().play(.success)
// Also available: .notification .directionUp .directionDown .failure
//                 .retry .start .stop .click
```

Apple Watch haptics are audibly tactile (the Taptic Engine clicks), unlike the silent iPhone haptics. Prefer the cross-platform `.sensoryFeedback(.success, trigger: counter)` modifier (watchOS 10+) when building shared SwiftUI views.

### Smart Stack relevance and Live Activities

iOS Live Activities mirror to the watch automatically (WidgetKit `ActivityConfiguration`). Branch on `@Environment(\.activityFamily)` and opt into `supplementalActivityFamilies([.small])` to design the wrist layout. For Smart Stack promotion, provide App Intent `RelevantContext` (watchOS 11) or `RelevanceConfiguration` via the new **RelevanceKit** (watchOS 26) — contexts include date, sleep, fitness, location, and MapKit POI categories.

### Documentation anchors

- HIG — [Designing for watchOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos)
- [watchOS Developer hub](https://developer.apple.com/watchos/) · [What's new in watchOS](https://developer.apple.com/watchos/whats-new/)
- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack) · [TabView](https://developer.apple.com/documentation/swiftui/tabview) · [WidgetFamily](https://developer.apple.com/documentation/widgetkit/widgetfamily)
- [handGestureShortcut](https://developer.apple.com/documentation/SwiftUI/View/handGestureShortcut(_:isEnabled:)) · [Converting a ClockKit App](https://developer.apple.com/documentation/WidgetKit/Converting-A-ClockKit-App)

## Anti-patterns

**Do not port the iPhone app.** If a screen requires reading a paragraph, doing a complex form, or navigating four levels deep, it belongs on the phone. Keep the hero interaction to one tap or one crown scroll.

**Avoid dense UIs and iPhone-sized targets.** One dominant data point per screen. Never cram more than three tap targets side-by-side. List rows size themselves correctly — resist squeezing them.

**Don't animate continuously.** It kills battery and is illegible in Always-On dim state. Hide chrome and suppress motion via `@Environment(\.isLuminanceReduced)`.

**Don't place critical content in the corners.** Series 7+ rounded masking will clip it. Use `.scenePadding()` for any hand-positioned view outside a `List`.

**Don't surface sensitive content in the ambient state** without explicit user opt-in — the Always-On display is visible to anyone glancing at the wrist.

**Don't substitute custom fonts for SF Compact** in running text. Dynamic Type and small-size tuning both suffer.

## Gotchas

**Always-On is hardware-gated.** Series 5+, Ultra, Ultra 2/3 — but **no SE model** has it. Test both paths.

**Double Tap hardware eligibility is not uniform.** Series 9, 10, 11 and Ultra 2/3 only. Ultra 1, Series 8 and earlier, SE — no. `handGestureShortcut` is a no-op there; design the screen to work without it.

**`digitalCrownRotation` modifier order is fragile.** Swap `.focusable()` and `.digitalCrownRotation(...)` and the crown stops working silently.

**Vertical-page `TabView` + inner scrolling is ambiguous.** Place scrolling content in the last page only, or tab changes hijack scroll gestures.

**ClockKit is deprecated.** New apps should use WidgetKit for complications; migrate existing code via Apple's [migration guide](https://developer.apple.com/documentation/WidgetKit/Converting-A-ClockKit-App).

**Wrist Flick (watchOS 26) has no third-party API** as of April 2026. It dismisses notifications/alarms system-wide on Series 9+ but you cannot bind app actions to it.

**watchOS 11 drops Series 4/5 and SE (1st gen).** watchOS 26 minimum device is iPhone 11+ on iOS 26; Apple Intelligence–powered Workout Buddy requires a paired iPhone 15 Pro or 16-class device.

**Complication previews in `recommendations()`:** return `[]` from the method on watchOS 26 to mark a widget as user-configurable in the Smart Stack.

## WWDC references

**watchOS 11 (2024)** — [10205 What's new in watchOS 11](https://developer.apple.com/videos/play/wwdc2024/10205/) · [10098 Design Live Activities for Apple Watch](https://developer.apple.com/videos/play/wwdc2024/10098/) · [10068 Bring your Live Activity to Apple Watch](https://developer.apple.com/videos/play/wwdc2024/10068/) · [10157 Extend your app's controls across the system](https://developer.apple.com/videos/play/wwdc2024/10157/).

**watchOS 26 / Liquid Glass (2025)** — [334 What's new in watchOS 26](https://developer.apple.com/videos/play/wwdc2025/334/) · [219 Meet Liquid Glass](https://developer.apple.com/videos/play/wwdc2025/219/) · [278 What's new in widgets](https://developer.apple.com/videos/play/wwdc2025/278/) · [361 Create icons with Icon Composer](https://developer.apple.com/videos/play/wwdc2025/361/).

**Foundational (2022–2023)** — [10138 Design and build apps for watchOS 10](https://developer.apple.com/videos/play/wwdc2023/10138/) · [10309 Design widgets for the Smart Stack](https://developer.apple.com/videos/play/wwdc2023/10309/) · [10029 Build widgets for the Smart Stack](https://developer.apple.com/videos/play/wwdc2023/10029/) · [10050 Complications and widgets: Reloaded](https://developer.apple.com/videos/play/wwdc2022/10050/).

---

# visionOS

visionOS is the design reference for Apple's broader **Liquid Glass** language — the refractive, lighting-aware material was the visionOS default from day one and was then generalized to iOS/macOS/watchOS/tvOS in 2025. Build for **eye + pinch** as the primary input, start in the **Shared Space**, and treat immersion as a user-escalated privilege rather than a default. visionOS 2 expanded enterprise APIs and raised hand tracking to 90 Hz; visionOS 26 added spatial widgets, enhanced Personas, shared nearby experiences, and PS VR2/stylus accessories.

## Design principles

**Three scene types with distinct jobs.** **Windows** (flat SwiftUI on a glass panel) carry 2D content. **Volumes** are bounded 3D boxes viewable from all sides — use for a globe, a mechanism, a chess board. **Immersive Spaces** replace or extend the world; they're the only place ARKit hand tracking and scene reconstruction are available. Launch into the **Shared Space** so the user's other apps coexist; let the user escalate to `.progressive` or `.full` immersion when the experience warrants it.

**Design around gaze and pinch.** The primary interaction is indirect: eyes target, a pinch confirms. **Gaze data is never exposed to your app** for privacy — the system applies the hover effect automatically and you only learn about a look at the moment of pinch. That constraint shapes everything: rely on standard controls so hover styling just works; use `.hoverEffect` on custom views; never try to infer "what the user is looking at."

**Comfort is a hard requirement.** Place interactive content roughly an arm's length to ~2 m away. Never anchor UI to the head — vestibular/visual disagreement causes nausea ("vection"). Prefer world-anchored or slow body-anchored lag-follow. Large moving surfaces must be semi-transparent. Respect `@Environment(\.accessibilityReduceMotion)`.

**Glass material is the design system.** Use `glassBackgroundEffect(in:)` for custom panels, and push toolbars/palettes outside window bounds via the `.ornament` modifier — that's how system `TabView` and `.toolbar` already render. Liquid Glass in 2025 refines (rather than replaces) the existing material; visionOS 26 widgets expose new **texture tokens** (`.paper`, `.glass`) and **mounting styles** (elevated, recessed).

## Key SwiftUI APIs

### Scenes — window, volume, immersive

```swift
@main struct SpatialApp: App {
    @State private var style: ImmersionStyle = .mixed

    var body: some Scene {
        WindowGroup(id: "main") { ContentView() }           // window

        WindowGroup(id: "globe") { GlobeView() }            // volume
            .windowStyle(.volumetric)
            .defaultSize(width: 0.6, height: 0.6, depth: 0.6, in: .meters)

        ImmersiveSpace(id: "space") { ImmersiveView() }     // immersive space
            .immersionStyle(selection: $style, in: .mixed, .progressive, .full)
            .upperLimbVisibility(.automatic)
    }
}
```

Open/close from any view via `@Environment(\.openWindow)`, `@Environment(\.openImmersiveSpace)`, and `@Environment(\.dismissImmersiveSpace)`. visionOS 2 adds `.progressive(0.2...1.0, initialAmount: 0.8)` for custom dial ranges; visionOS 26 adds `.immersiveEnvironmentBehavior(.coexist)`, `RemoteImmersiveSpace` (Mac-hosted), and scene persistence APIs.

### Ornaments and glass

```swift
// Toolbar-like palette extending outside the window
MainView()
    .ornament(visibility: .visible,
              attachmentAnchor: .scene(.bottom),
              contentAlignment: .center) {
        HStack {
            Button("New",  systemImage: "pencil") {}
            Button("Save", systemImage: "square.and.arrow.down") {}
        }
        .labelStyle(.iconOnly)
        .padding()
        .glassBackgroundEffect()
    }

// Custom glass panel
VStack { Text("Controls") }
    .padding(16)
    .glassBackgroundEffect(in: .rect(cornerRadius: 24),
                           displayMode: .always)
```

`displayMode` is `.always | .never | .implicit`. Glass renders correctly on rounded shapes (RoundedRectangle, Capsule, Circle); arbitrary paths fall back to a flat rectangle without specular edges.

### Hover and focus

```swift
Button("Play") {}.hoverEffect()
Text("Item").hoverEffect(.highlight)
Image("cover").hoverEffect(.lift)

// visionOS 2+: custom animation
MyView().hoverEffect { effect, isActive, _ in
    effect.scaleEffect(isActive ? 1.05 : 1.0)
          .animation(.easeInOut(duration: 0.2), value: isActive)
}

// Define hit shape independent of visual bounds
Thumbnail()
    .contentShape(.hoverEffect, RoundedRectangle(cornerRadius: 20))
```

Use `.focusable()` on views that need keyboard / game controller focus. RealityKit entities need a `HoverEffectComponent` plus `InputTargetComponent` + `CollisionComponent` to participate.

### 3D content — Model3D and RealityView

```swift
// Simple case: load a USDZ asynchronously
Model3D(named: "Flower-Pot") { model in
    model.resizable().aspectRatio(contentMode: .fit)
} placeholder: {
    ProgressView()
}

// Full control: entities, components, gestures
import RealityKit
import RealityKitContent

struct ImmersiveView: View {
    @State private var enlarge = false
    var body: some View {
        RealityView { content in
            if let scene = try? await Entity(named: "Scene",
                                             in: realityKitContentBundle) {
                content.add(scene)
            }
        } update: { content in
            content.entities.first?.scale = enlarge ? [1.3,1.3,1.3] : [1,1,1]
        }
        .gesture(TapGesture()
            .targetedToAnyEntity()
            .onEnded { _ in enlarge.toggle() })
    }
}
```

**Asset pipeline.** Model in Blender/Maya → export USD/USDZ → compose scenes and materials in **Reality Composer Pro** (bundled with Xcode). RCP is not a modeler; it's a scene/material/component authoring tool. Every visionOS project template includes a `RealityKitContent` package wired up to RCP.

visionOS 26 adds `ManipulationComponent` (built-in drag/rotate/scale), `MeshInstancesComponent` (GPU instancing), `EnvironmentBlendingComponent`, and post-processing on `RealityView`.

### Documentation anchors

- HIG — [Designing for visionOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos)
- [visionOS Developer hub](https://developer.apple.com/visionos/) · [What's new](https://developer.apple.com/visionos/whats-new/) · [WWDC25 visionOS guide](https://developer.apple.com/wwdc25/guides/visionos/)
- [ImmersiveSpace](https://developer.apple.com/documentation/swiftui/immersivespace) · [windowStyle](https://developer.apple.com/documentation/swiftui/view/windowstyle(_:)) · [ornament](https://developer.apple.com/documentation/swiftui/view/ornament(visibility:attachmentanchor:contentalignment:ornament:)) · [glassBackgroundEffect](https://developer.apple.com/documentation/swiftui/view/glassbackgroundeffect(in:displaymode:))
- [RealityView](https://developer.apple.com/documentation/realitykit/realityview) · [Model3D](https://developer.apple.com/documentation/realitykit/model3d) · [ARKit on visionOS](https://developer.apple.com/documentation/arkit/arkit_in_visionos)
- [Enterprise APIs](https://developer.apple.com/documentation/visionos/building-spatial-experiences-for-business-apps-with-enterprise-apis) · [GroupActivities](https://developer.apple.com/documentation/groupactivities)

## Anti-patterns

**Small targets.** Apple's minimum usable target is **~60 pt** (≈2.5° of visual angle, ≈4.4 cm at 1 m). A 28 pt visual control is fine if padded to a 60 pt hit area. Keep ≥ 16 pt between stacked buttons and ≥ 4 pt between list rows to avoid overlapping hover states.

**Rapid motion filling the field of view.** Large, opaque, moving surfaces trigger vection. Make big moving elements semi-transparent and anchor them to the world, not the head.

**Bright full-field content.** White full-immersion backgrounds strain the eyes, especially in darkened rooms. Use the system environment brightness as a ceiling.

**Head-locked UI.** Breaks vestibular agreement. Even HUDs should lag-follow (body-anchored) rather than strictly head-lock.

**Defaulting to full immersion.** Launch into Shared Space; let the user escalate. Full immersion is for experiences that genuinely need to replace the world.

**Poor depth choices.** Don't scatter interactive content across radically different depths — constant vergence changes fatigue the eyes. Keep peripheral content passive; primary actions go near center.

**Over-customizing hover.** Hover effects that change size, color, and shape at once create visual noise; pick one treatment per interaction class.

## Gotchas

**ARKit is Immersive-Space-only.** Hand tracking, scene reconstruction, plane/image/object anchors — none of it is available in the Shared Space.

**Gaze is never exposed.** You can't build "look-to-preview" by reading eye direction. You can build it via `.hoverEffect` visuals that the system applies; your app sees the hit only on pinch.

**Ornaments don't always render on `.plain` WindowGroups.** Community testing has found edge cases — verify in your target immersion style.

**Enterprise APIs require entitlement + license file** (managed distribution via Apple Business Manager or in-house). Main Camera, passthrough recording, spatial barcode scanning, and ANE access are not App Store–distributable. visionOS 26 promoted UVC and ANE access to general availability without entitlement.

**Spatial Persona SharePlay caps at 5.** Up to 33 participants total via GroupActivities; only 5 can share spatial context. Beyond that, Personas show as video tiles.

**visionOS 26 widgets persist across sessions** at fixed real-world size. Design them like objects in the room (wall clock, poster), not like iOS widgets — include LOD at proximity and sensible material tokens (`.paper` vs `.glass`).

**90 Hz hand tracking was default as of visionOS 26** (versus 30 Hz historic, 90 Hz opt-in on visionOS 2). Prediction mode trades ~20 ms latency for slightly noisier poses — fine for UI attachment, risky for precise drawing.

**Liquid Glass on visionOS is an evolution, not a migration.** Unlike iOS 26, there is no disruptive "adopt Liquid Glass" pass — standard controls automatically refresh; the API surface is still `glassBackgroundEffect` plus new widget texture/mount tokens.

## WWDC references

**visionOS 2 (2024)** — [10086 Design great visionOS apps](https://developer.apple.com/videos/play/wwdc2024/10086/) · [10096 Design interactive experiences for visionOS](https://developer.apple.com/videos/play/wwdc2024/10096/) · [10139 Introducing enterprise APIs for visionOS](https://developer.apple.com/videos/play/wwdc2024/10139/) · [10101 Explore object tracking for visionOS](https://developer.apple.com/videos/play/wwdc2024/10101/) · [10103 Discover RealityKit APIs](https://developer.apple.com/videos/play/wwdc2024/10103/) · [10201 Customize spatial Persona templates in SharePlay](https://developer.apple.com/videos/play/wwdc2024/10201/).

**visionOS 26 / Liquid Glass (2025)** — [317 What's new in visionOS 26](https://developer.apple.com/videos/play/wwdc2025/317/) · [219 Meet Liquid Glass](https://developer.apple.com/videos/play/wwdc2025/219/) · [290 Set the scene with SwiftUI in visionOS](https://developer.apple.com/videos/play/wwdc2025/290/) · [287 What's new in RealityKit](https://developer.apple.com/videos/play/wwdc2025/287/) · [255 Design widgets for visionOS](https://developer.apple.com/videos/play/wwdc2025/255/) · [303 Design hover interactions for visionOS](https://developer.apple.com/videos/play/wwdc2025/303/) · [289 Explore spatial accessory input](https://developer.apple.com/videos/play/wwdc2025/289/) · [318 Share visionOS experiences with nearby people](https://developer.apple.com/videos/play/wwdc2025/318/).

**Foundational (2023)** — [10078 Design considerations for vision and motion](https://developer.apple.com/videos/play/wwdc2023/10078/) · [10111 Go beyond the window with SwiftUI](https://developer.apple.com/videos/play/wwdc2023/10111/) · [10034 Create accessible spatial experiences](https://developer.apple.com/videos/play/wwdc2023/10034/) · [10075 Design spatial SharePlay experiences](https://developer.apple.com/videos/play/wwdc2023/10075/).

---

# tvOS

Apple TV is a **focus-driven, 10-foot, media-first** platform. There is no cursor, no touch, and no hover — the Siri Remote moves focus and presses activate. Design for cinematic, full-bleed content with a small amount of chrome on top, and let `AVPlayerViewController` do the playback heavy lifting. tvOS 18 added InSight, Enhance Dialogue, and automatic subtitles; tvOS 26 brought **Liquid Glass**, an Apple Account login API for tvOS apps, and Apple TV app redesigns.

## Design principles

**Focus is the UI.** Build with large cards, generous spacing, and strong focused-state feedback (lift + scale + parallax + soft shadow). The Focus Engine picks the next target based on directional adjacency; supplement with `focusSection()` and `prefersDefaultFocus(_:in:)` to nudge behavior. Use `.buttonStyle(.card)` for poster-style targets — it provides the standard lift and directional tilt for free.

**Legibility at 10 feet.** Use San Francisco at medium-or-heavier weight, favor generous sizes (body text ~29 pt and up; headlines 48 pt+), and avoid hairline strokes — HDMI compression and motion blur eat them. Pair every focus state with motion, not color alone.

**Cinematic, full-bleed, chrome-minimal.** Lead with full-width artwork and video; push controls to overlays that dismiss when the user isn't interacting. `AVPlayerViewController` supplies the transport bar, content tabs (Info / Chapters / Subtitles / Audio), skip intro, and system Enhance Dialogue — don't rebuild it.

**Extend to the Home screen.** Parallax app icons (layered `.lsr`) and a Top Shelf extension are first-class surfaces. A Top Shelf that personalizes (recently played, resume, new content) is a genuine user win, not marketing.

**Respect the remote's invariants.** Menu/Back always goes back (or, at the app's top level, to Home). TV/Home is system-owned — you cannot intercept it.

### Layout safe areas (HD canvas, 1920 × 1080 pt)

| Edge | Margin | Notes |
|---|---|---|
| Top / bottom | **60 pt** | Historical HIG; confirmed empirically via `safeAreaInsets` |
| Left / right | **80 pt** | HIG range is 80–90 pt |
| Focused element clearance | Leave room for ~1.1× lift | Enough breathing room that parallax doesn't clip neighbors |

### Parallax icons & Top Shelf assets

| Asset | Size (@1x) | Notes |
|---|---|---|
| App Store icon (large) | 1280 × 768 | Layered `.lsr`, 2–5 layers, opaque background |
| Home Screen icon (small) | 400 × 240 | @2x: 800 × 480; safe zone 370 × 222 |
| Top Shelf static image | 3840 × 1440 | Optional wide variant 4640 × 1440; never transparent |
| Top Shelf dynamic | via extension | `TVTopShelfContentProvider` → sectioned or inset style |

## Key SwiftUI APIs

### Focus — focusable, @FocusState, scopes, sections

```swift
struct Hub: View {
    enum Field: Hashable { case play, browse, settings }
    @FocusState private var focus: Field?
    @Namespace private var ns

    var body: some View {
        HStack(spacing: 80) {
            Button("Play")     {}.focused($focus, equals: .play)
                                 .prefersDefaultFocus(true, in: ns)
            Button("Browse")   {}.focused($focus, equals: .browse)
            Button("Settings") {}.focused($focus, equals: .settings)
        }
        .focusScope(ns)
        .onAppear { focus = .play }
    }
}
```

`focusable(_:interactions:)` (tvOS 15+) lets a non-interactive view accept focus with `.activate` or `.edit` interactions. `focusSection()` is the SwiftUI replacement for UIKit's `UIFocusGuide` — it lets focus jump diagonally into a group of children that wouldn't otherwise be adjacent. For UIKit bridging (e.g., `UICollectionView`), override `preferredFocusEnvironments`. Reset focus with `@Environment(\.resetFocus) var resetFocus; resetFocus(in: ns)`.

### Remote commands — play/pause, arrows, back

```swift
struct PlayerScreen: View {
    @State private var isPlaying = false
    var body: some View {
        VideoSurface()
            .focusable()
            .onPlayPauseCommand { isPlaying.toggle() }
            .onMoveCommand { dir in
                switch dir {
                case .left:  seek(-10)
                case .right: seek(+10)
                default: break
                }
            }
            .onExitCommand { dismiss() }
    }
}
```

`MoveCommandDirection` is `.up | .down | .left | .right`. `onExitCommand` handles the Menu/Back button. These handlers only fire when the attached view has focus.

### Card buttons and tvOS `TabView`

```swift
Button { play() } label: {
    VStack {
        artwork.resizable().aspectRatio(16/9, contentMode: .fit)
        Text(title).font(.headline)
    }
}
.buttonStyle(.card)                 // tvOS-only; lift + parallax tilt
```

`TabView` on tvOS renders as a **top tab bar** (not a bottom bar like iOS). Focus lives on the tab bar; swiping down moves focus into content, and the bar auto-hides while users are engaged with content below. For poster shelves use `ScrollView { LazyVGrid { ... } }` with each cell wrapped in a `.card`-style button — there is no dedicated `.grid` `ListStyle` on tvOS.

### Documentation anchors

- HIG — [Designing for tvOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-tvos) · [Focus and selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection) · [Remotes](https://developer.apple.com/design/human-interface-guidelines/remotes) · [Top shelf](https://developer.apple.com/design/human-interface-guidelines/top-shelf)
- [focusable](https://developer.apple.com/documentation/swiftui/view/focusable(_:)) · [FocusState](https://developer.apple.com/documentation/swiftui/focusstate) · [focusSection](https://developer.apple.com/documentation/swiftui/view/focussection()) · [CardButtonStyle](https://developer.apple.com/documentation/swiftui/cardbuttonstyle)
- [onPlayPauseCommand](https://developer.apple.com/documentation/swiftui/view/onplaypausecommand(perform:)) · [onMoveCommand](https://developer.apple.com/documentation/swiftui/view/onmovecommand(perform:)) · [onExitCommand](https://developer.apple.com/documentation/swiftui/view/onexitcommand(perform:))
- [AVPlayerViewController (tvOS)](https://developer.apple.com/documentation/avkit/avplayerviewcontroller) · [TVTopShelfContentProvider](https://developer.apple.com/documentation/tvservices/tvtopshelfcontentprovider)

## Anti-patterns

**Tiny text and hairline strokes.** Minimum effective body text is about 29 pt; headlines want 48 pt and up. Anything thinner than SF Medium at those sizes disappears under HDMI compression.

**Hover-only affordances.** There is no hover state on tvOS. Don't port iPad tooltips, hover reveals, or "point to preview" mechanics.

**Heavy text entry and complex forms.** The on-screen Siri Remote keyboard is slow. Use the Continuity keyboard on iPhone, Sign in with Apple, passkeys, or the new Apple Account login API (tvOS 26) to skip it entirely.

**Dense grids.** Five to seven large cards beats twenty cramped thumbnails. Generous spacing is a feature, not wasted space — it gives the focus lift room to breathe.

**Reassigning system buttons.** Menu/Back must always go back or exit; TV/Home is system-owned. Play/Pause should control playback, nothing destructive.

**Ads on the Top Shelf** or prominent prices. HIG explicitly forbids it.

**Building a custom video player.** `AVPlayerViewController` integrates content tabs, Enhance Dialogue, automatic subtitles, AirPlay, HDR/spatial audio, and system remote behavior. Custom players lose all of that.

## Gotchas

**Screen canvas is fixed at 1920 × 1080 pt** (2× on 4K). Unlike iOS, you don't size for device variety — you size for viewing distance.

**TVML/TVMLKit is being wound down.** Apple published "Migrate your TVML app to SwiftUI" at WWDC24. New work should be SwiftUI-first.

**`onMoveCommand` has a known first-press bug** on tvOS 18 with 2nd/3rd-gen Siri Remote — the first directional press after a focus change is sometimes swallowed (Apple Developer Forum threads #764582, #794820). Workaround: re-arm state on focus change.

**InSight is Apple TV+ only.** There is no third-party developer API for providing cast/soundtrack overlays. Similarly, **Enhance Dialogue** is a system-level setting with no per-app AVFoundation parameter.

**21:9 cinema mode (tvOS 18.2+) is a projector-aware display setting**, not a letterboxing API — your video just plays; the user picks the aspect in Settings.

**Liquid Glass adoption on tvOS 26 is opt-in through tvOS 27.** Existing apps keep their current appearance; Apple is not enforcing redesign yet. Use the 2025–2026 window to migrate intentionally.

**New tvOS 26 Apple Account login API** links in-app sign-in to the user's Apple Account so new devices auto-sign into streaming apps — major UX win for media apps; worth adopting early.

**`onExitCommand` does not fire at the app root** — the system takes the Back press and returns to Home. Don't try to trap exit at the top level.

## WWDC references

**tvOS 18 (2024)** — WWDC24 Keynote 101 and Platforms State of the Union 102 (InSight, Enhance Dialogue, subtitle automation). "Migrate your TVML app to SwiftUI" covers the modernization path. (Apple did not publish a dedicated "What's new in tvOS 18" developer session; coverage lives in cross-platform SwiftUI/AVKit tracks.)

**tvOS 26 / Liquid Glass (2025)** — [219 Meet Liquid Glass](https://developer.apple.com/videos/play/wwdc2025/219/) and the WWDC25 "Build a SwiftUI app with the new design" track, plus the WWDC25 Platforms State of the Union (tvOS Apple Account login API; Apple TV redesign).

**Foundational** — [WWDC20 10042 Build SwiftUI apps for tvOS](https://developer.apple.com/videos/play/wwdc2020/10042/) · [WWDC21 10023 Direct and reflect focus in SwiftUI](https://developer.apple.com/videos/play/wwdc2021/10023/) · [WWDC21 10191 Deliver a great playback experience on tvOS](https://developer.apple.com/videos/play/wwdc2021/10191/) · [WWDC23 10162 The SwiftUI cookbook for focus](https://developer.apple.com/videos/play/wwdc2023/10162/) · Tech Talks — [Designing for Apple TV](https://developer.apple.com/videos/play/techtalks-apple-tv/2/).

---

## A note on accuracy

Several specific figures in this document were cross-checked against Apple's public docs but some HIG pages are JavaScript-rendered and could not be fully text-extracted; values like the watchOS point dimensions, tvOS safe-area margins, and the visionOS 60 pt minimum hit-target come from WWDC sessions and Apple Support tech-spec pages cross-referenced with the HIG. The "60 pt between focusable elements" figure on tvOS is a community rule of thumb rather than an explicit Apple number — plan spacing by the lift/parallax clearance rule instead. When in doubt, measure at runtime (`WKInterfaceDevice.current().screenBounds` on watchOS; `UIScreen.overscanCompensationInsets` on tvOS) and consult the WWDC 2025 design sessions for the latest Liquid Glass guidance.