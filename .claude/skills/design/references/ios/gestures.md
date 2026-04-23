---
name: gestures
description: iOS gesture system (system gestures, SwiftUI primitives, swipe actions, drag-and-drop, Liquid Glass feedback)
platform: ios
---

# The iOS gesture system: a developer reference for iOS 18 and iOS 26

**Apple's gesture model is now unified across UIKit and SwiftUI, renamed in places, and extended in iOS 26 with richer drag-and-drop and Liquid Glass feedback — but the core rule has not changed since 2017: every gesture is a shortcut, never a replacement, and every custom interaction needs a visible, accessible alternative.** This reference consolidates the current API surface for iOS 18 and iOS 26 across system gestures, SwiftUI primitives, swipe actions, drag-and-drop, pointer interactions, UIKit recognizers, and accessibility, with a gesture-compatibility matrix, idiomatic code, anti-patterns, and WWDC source citations. The emphasis is practical: what to use, what to avoid, and what the system will fight you on.

The gesture story has evolved in three recent waves. **iOS 16** introduced `Transferable` and the declarative `.draggable`/`.dropDestination` pair, retiring most `NSItemProvider` boilerplate. **iOS 17** renamed `MagnificationGesture → MagnifyGesture` and `RotationGesture → RotateGesture`, added `SpatialTapGesture`, and unified hover effects across iPadOS and visionOS. **iOS 18** unified the UIKit and SwiftUI gesture systems (cross-framework `require(toFail:)`, `UIGestureRecognizerRepresentable`). **iOS 26** (WWDC 2025) layered on Liquid Glass interactive feedback, a major SwiftUI drag-and-drop upgrade (`dragContainer`, `DragConfiguration`), iPadOS 26 windowing gestures (flick-to-tile, swipe-down menu bar, double-swipe-home), and `NSGestureRecognizerRepresentable` — but no new primary 2D gesture primitive.

---

## 1. System gestures that must never be overridden

System gestures are pre-empted by SpringBoard before your app sees the touches, and every iPhone user since 2017 relies on them identically in every app. Overriding them breaks muscle memory, violates Apple's HIG, and typically fails anyway because system recognizers run at higher priority. Apple's guidance (*Inputs → Touchscreen gestures*) is blunt: **"Avoid interfering with systemwide screen-edge gestures. People rely on these gestures to work in every app."**

**Edge-back swipe** pops the top `UIViewController` from a `UINavigationController` via the private `interactivePopGestureRecognizer` — short swipe from the left edge in LTR locales, right edge in RTL. It is the only discoverable back affordance on edge-to-edge iPhones; replacing it confuses users and breaks VoiceOver's escape semantics. Disabling it is legitimate only on a root canvas (`navigationController.interactivePopGestureRecognizer?.isEnabled = false`). **Home-indicator swipe** from the bottom edge returns to Home; a pause mid-swipe opens the App Switcher. **Notification Center** appears on a swipe from the top-left/status-bar region, and **Control Center** appears on a swipe from the top-right on Face ID devices (bottom on home-button devices).

Immersive apps (games, video players, drawing canvases) can *defer* — not override — these gestures using **edge protect**: the first swipe goes to your recognizer, the second swipe invokes the system. HIG: *"If you must enable custom screen-edge gestures, use edge protect sparingly."* UIKit uses `preferredScreenEdgesDeferringSystemGestures`; SwiftUI exposes `.defersSystemGestures(on:)` (iOS 16+). On Face ID devices you cannot fully block the Home gesture — the system only delays it.

```swift
// UIKit: defer bottom (Home) and top (Notification/Control Center) edges
final class GameViewController: UIViewController {
    override var preferredScreenEdgesDeferringSystemGestures: UIRectEdge { [.bottom, .top] }
    override var prefersHomeIndicatorAutoHidden: Bool { true }

    func enterImmersive() {
        setNeedsUpdateOfScreenEdgesDeferringSystemGestures()
        setNeedsUpdateOfHomeIndicatorAutoHidden()
    }
}

// SwiftUI equivalent (iOS 16+)
GameCanvas()
    .defersSystemGestures(on: [.bottom, .top])
    .persistentSystemOverlays(.hidden)
```

`UIScreenEdgePanGestureRecognizer` (iOS 7+) is the public API for **app-private** edge pans — use it only on edges the system doesn't already own, and only alongside a deferred system gesture. **iOS 18 and iOS 26 did not change these contracts.** iOS 26 beta reports (Apple Developer Forums thread 794212) indicate stricter arbitration between `ScrollView` and custom `DragGesture` — a behavior change, not a semantic one.

## 2. SwiftUI gestures: the modern primary surface

All SwiftUI gesture primitives conform to the `Gesture` protocol and attach via `.gesture(_:)`, `.highPriorityGesture(_:)`, or `.simultaneousGesture(_:)`. State lives in `@State` (persistent) or `@GestureState` (auto-resets when the gesture ends; only writable inside `.updating`).

**TapGesture** (iOS 13+) takes a `count` for double/triple taps: `TapGesture(count: 2).onEnded { … }`. **LongPressGesture** (iOS 13+) takes `minimumDuration` (default 0.5s) and `maximumDistance` (10pt). **DragGesture** (iOS 13+) exposes `location`, `startLocation`, `translation`, `velocity` (iOS 17+), `predictedEndLocation`, and a `coordinateSpace` that can be `.local`, `.global`, or `.named("id")`. Set `minimumDistance: 0` to behave like `touchesBegan`.

**MagnifyGesture** (iOS 17+) replaced **MagnificationGesture** (iOS 13–16). The rename is soft — the old type still compiles — but Apple documentation and sample code use the new name uniformly from iOS 17 onward. Its `Value` still exposes `magnification: CGFloat`. Likewise, **RotateGesture** (iOS 17+) replaced **RotationGesture**, with `Value.rotation: Angle`. **SpatialTapGesture** (iOS 17+) finally gives you the **tap location** — closing a long-standing gap where developers faked taps with `DragGesture(minimumDistance: 0)`.

```swift
struct GesturePlayground: View {
    @GestureState private var drag = CGSize.zero
    @State private var offset = CGSize.zero
    @State private var scale: CGFloat = 1
    @State private var baseScale: CGFloat = 1
    @State private var angle: Angle = .zero
    @State private var baseAngle: Angle = .zero

    var body: some View {
        Image("photo")
            .scaleEffect(scale)
            .rotationEffect(angle)
            .offset(x: offset.width + drag.width, y: offset.height + drag.height)
            .gesture(
                DragGesture(minimumDistance: 5, coordinateSpace: .local)
                    .updating($drag) { v, s, _ in s = v.translation }
                    .onEnded { v in
                        offset.width  += v.translation.width
                        offset.height += v.translation.height
                    }
            )
            .simultaneousGesture(
                MagnifyGesture()                         // iOS 17+
                    .onChanged { scale = baseScale * $0.magnification }
                    .onEnded   { _ in baseScale = scale }
            )
            .simultaneousGesture(
                RotateGesture(minimumAngleDelta: .degrees(3))   // iOS 17+
                    .onChanged { angle = baseAngle + $0.rotation }
                    .onEnded   { _ in baseAngle = angle }
            )
            .gesture(
                SpatialTapGesture(count: 2)              // iOS 17+
                    .onEnded { v in print("Double-tapped at \(v.location)") }
            )
    }
}
```

Combined gestures use three operators: **`.simultaneously(with:)`** recognizes both at once, **`.sequenced(before:)`** requires the first to succeed before the second arms (classic press-then-drag), and **`.exclusively(before:)`** prefers the first and only fires the second if the first fails. The composed value type nests — e.g. a `SequenceGesture` value exposes `.first(_)` and `.second(_, _)` cases.

```swift
let longThenDrag = LongPressGesture(minimumDuration: 0.4)
    .sequenced(before: DragGesture())
    .updating($state) { value, state, _ in
        switch value {
        case .first(true):                         state = .pressing
        case .second(true, let drag?):             state = .dragging(drag.translation)
        default:                                   state = .inactive
        }
    }
```

**iOS 18 added `UIGestureRecognizerRepresentable`**, which bridges *any* `UIGestureRecognizer` into SwiftUI natively — crucial for multi-finger taps (which SwiftUI's `TapGesture` cannot express), custom subclasses, and cross-framework `require(toFail:)`. **iOS 26 added `NSGestureRecognizerRepresentable`** (AppKit counterpart), RealityKit `Entity`-attached gestures, and — per community reports verified against WWDC25 "What's new in SwiftUI" (session 256) — **introduced no new core 2D gesture types**. Third-party posts claiming "new iOS 26 gesture events" beyond the iOS 17 set are speculative; Apple's shipped APIs remain `Tap`, `LongPress`, `Drag`, `Magnify`, `Rotate`, `SpatialTap`, plus the representable bridges.

```swift
// iOS 18+: bridge a two-finger UITapGestureRecognizer into SwiftUI
struct TwoFingerTap: UIGestureRecognizerRepresentable {
    let action: () -> Void
    func makeUIGestureRecognizer(context: Context) -> UITapGestureRecognizer {
        let g = UITapGestureRecognizer()
        g.numberOfTouchesRequired = 2
        return g
    }
    func handleUIGestureRecognizerAction(_ recognizer: UITapGestureRecognizer, context: Context) {
        if recognizer.state == .ended { action() }
    }
}
```

Three attachment modifiers control precedence. **`.gesture(_:)`** is the default — child views win by default. **`.highPriorityGesture(_:)`** makes the parent win over children. **`.simultaneousGesture(_:)`** recognizes alongside child gestures instead of overriding.

## 3. Swipe actions on List rows

`.swipeActions(edge:allowsFullSwipe:content:)` is iOS 15+ (macOS 12, watchOS 8; `tvOS` unavailable). It only works on rows inside a `List` or a `ForEach` inside a `List`. Declaring swipe actions on a `ForEach` **disables SwiftUI's automatic `.onDelete` synthesis** — you must supply the destructive action yourself.

The `edge` parameter is `HorizontalEdge` — `.leading` (swipe right) or `.trailing` (swipe left, default). You can stack the modifier twice to configure both edges. `allowsFullSwipe` (default `true`) auto-fires the **first** declared action when the user swipes past a threshold. Put reversible actions (archive) or clearly destructive actions (delete) at the outermost position. Use `Button(role: .destructive)` for red system-destructive tinting, and `.tint(_:)` for custom colors. SF Symbols inside swipe actions render in their fill variant automatically.

Apple's HIG does not publish a hard cap, but its own apps (Mail, Messages, Reminders) consistently use **2–3 actions per edge**, and the community convention — echoed by Apple design libraries — is a maximum of three. Beyond that, hit targets become cramped and discoverability suffers. iOS 18 added no new parameters; iOS 26 restyles swipe-action buttons automatically through Liquid Glass when the app is compiled against the iOS 26 SDK, but the API signature is unchanged.

```swift
struct InboxRow: View {
    @Binding var message: Message
    var body: some View {
        HStack {
            if message.isPinned { Image(systemName: "pin.fill") }
            Text(message.subject).fontWeight(message.isRead ? .regular : .bold)
        }
        .swipeActions(edge: .trailing, allowsFullSwipe: true) {
            Button(role: .destructive) { delete() } label: {
                Label("Delete", systemImage: "trash")
            }
            Button { archive() } label: { Label("Archive", systemImage: "archivebox") }
                .tint(.orange)
        }
        .swipeActions(edge: .leading, allowsFullSwipe: false) {
            Button { message.isRead.toggle() } label: {
                Label(message.isRead ? "Unread" : "Read",
                      systemImage: message.isRead ? "envelope.badge" : "envelope.open")
            }.tint(.blue)
            Button { message.isPinned.toggle() } label: {
                Label("Pin", systemImage: "pin")
            }.tint(.yellow)
        }
    }
}
```

Convention matters: users expect **trailing swipe = delete** because Mail, Messages, and Reminders established that pattern. Redefining leading to destructive is a subtle but real accessibility mistake.

## 4. Drag and drop: migrating from NSItemProvider to Transferable

iOS 16 introduced the **`Transferable` protocol** (WWDC 2022 session 10062, *Meet Transferable*) and the declarative pair `.draggable(_:)` / `.dropDestination(for:action:isTargeted:)`. This collapses the pre-iOS-16 dance of encoding to `Data`, creating an `NSItemProvider`, registering type identifiers, and dispatching callbacks to main into a single declarative representation.

A `Transferable` type declares representations via four builders. **`CodableRepresentation(contentType:)`** encodes via `Codable` (JSON) for same-app and domain-aware consumers. **`DataRepresentation(contentType:exporting:importing:)`** wraps raw binary formats. **`FileRepresentation(contentType:exporting:importing:)`** exposes or accepts a file URL with sandbox-safe handoff. **`ProxyRepresentation(exporting:)`** bridges to an already-Transferable type (e.g. expose your model as a `String` or `URL` so unaware apps can still accept it).

```swift
import SwiftUI
import UniformTypeIdentifiers

extension UTType { static let note = UTType(exportedAs: "com.example.app.note") }

struct Note: Codable, Transferable {
    let id: UUID
    var title: String
    var body: String
    static var transferRepresentation: some TransferRepresentation {
        CodableRepresentation(contentType: .note)     // primary: same-app / aware apps
        ProxyRepresentation(exporting: \.body)        // fallback: any text-accepting app
    }
}

struct NoteCard: View {
    let note: Note
    var body: some View { Text(note.title).padding().draggable(note) }
}

struct Inbox: View {
    @State private var dropped: [Note] = []
    @State private var targeted = false
    var body: some View {
        VStack { ForEach(dropped, id: \.id) { Text($0.title) } }
            .frame(minHeight: 200)
            .background(targeted ? .blue.opacity(0.2) : .gray.opacity(0.1))
            .dropDestination(for: Note.self) { items, _ in
                dropped.append(contentsOf: items); return true
            } isTargeted: { targeted = $0 }
    }
}
```

**Migration from NSItemProvider.** The legacy iOS 13.4–15 pattern — `.onDrag { NSItemProvider(item: data, typeIdentifier: "com.example.note") }` and `.onDrop(of:isTargeted:perform:)` with manual `loadDataRepresentation` and `DispatchQueue.main.async` — is still required when supporting iOS 14–15, when integrating with legacy `UITableView`/`UICollectionView` drag delegates, when producing items for `UIActivityViewController` and share extensions, and when working with `PhotosPicker`'s `loadTransferable` (which itself bridges `NSItemProvider` internally). For new code on iOS 16+, use `Transferable`. The two APIs interoperate: `NSItemProvider(object:)` can be constructed from any `Transferable` with a suitable `ProxyRepresentation`.

**UIKit** retains `UIDragInteraction`, `UIDropInteraction`, `UIDragItem`, `UITableViewDragDelegate`/`UITableViewDropDelegate`, and their `UICollectionView` counterparts (all iOS 11+). Cross-app drag on iPad — Split View, Slide Over, Stage Manager, and external-display windows (iPadOS 16.2+) — works wherever both ends implement these interactions; there is no separate cross-app API.

**iPadOS 26 is the first major SwiftUI drag upgrade since iOS 16** (WWDC 2025 session 256). New surface area includes `dragContainer(for:selection:)` for lazily-resolved multi-item drags, `.draggable(containerItemID:)`, `DragConfiguration` (declaring `allowMove`/`allowDelete`), `onDragSessionUpdated` for observing phase transitions, and `dragPreviewsFormation(.stack)` for multi-item preview styles. Drags from iOS 26 SwiftUI apps can leave the app (system trash) without custom `NSItemProvider` plumbing. Early Xcode 26 betas had a bug where `.dropDestination` with a custom `UTType` + `CodableRepresentation` fails to fire — using `.json` as the `contentType` is the reported workaround (forum thread 792586); verify on the shipping SDK before production use.

```swift
// iOS 26 multi-item drag container
PhotoGrid(photos: photos)
    .dragContainer(for: Photo.self, selection: selectedIDs) { ids in
        photos(matching: ids)
    }
    .dragConfiguration(DragConfiguration(allowMove: true, allowDelete: true))
    .onDragSessionUpdated { session in
        if case .ended(.delete) = session.phase {
            let ids = session.draggedItemIDs(for: Photo.ID.self)
            trash(ids)
        }
    }
    .dragPreviewsFormation(.stack)
```

## 5. Pointer interactions on iPad and Mac Catalyst

SwiftUI's `.hoverEffect(_:)` (iOS 13.4+) and UIKit's `UIPointerInteraction` (iOS 13.4+) let views respond to the iPadOS pointer and trackpad. iOS 17+ extends hover to iPhones paired with an external pointing device (Bluetooth trackpad via AssistiveTouch, USB-C on iPhone 15+) — existing hover code "just works" there.

Three pointer styles map 1:1 between SwiftUI and UIKit. **`.automatic`** lets the system pick based on context (usually `.highlight` for button-like targets). **`.highlight`** morphs the pointer into a platter shape behind the view with a subtle directional light — best for dense controls in toolbars and list rows. **`.lift`** scales the view up slightly with a shadow and slides the pointer under it — best for standalone content targets like app icons, photo tiles, and cards. Apple's design guidance (WWDC 2020 session 10640 *Design for the iPadOS pointer*) is explicit: don't mix `.lift` and `.highlight` within a single toolbar or group.

iOS 17 added a closure-based custom-hover-effect API and the `CustomHoverEffect` protocol, unified with visionOS. iOS 18 did not change the surface but Apple emphasized delaying size-changing effects in Liquid Glass contexts. iOS 26 renders `.hoverEffect(.automatic)` through the glass material, producing subtle lensing/refraction without any code change when rebuilt against the iOS 26 SDK; `RemoteImmersiveSpace` (visionOS 26 streamed from Mac) also honors hover effects.

```swift
// SwiftUI
struct ToolbarIcon: View {
    let name: String; let action: () -> Void
    var body: some View {
        Button(action: action) { Image(systemName: name).frame(width: 44, height: 44) }
            .buttonStyle(.plain)
            .hoverEffect(.highlight)          // iOS 13.4+
    }
}

struct ArtworkTile: View {
    let image: Image
    var body: some View {
        image.resizable().aspectRatio(contentMode: .fill)
            .frame(width: 160, height: 160)
            .clipShape(RoundedRectangle(cornerRadius: 14))
            .hoverEffect(.lift)               // iOS 13.4+
    }
}

// iOS 17+: custom closure-based effect
Button("Play") { }
    .hoverEffect { effect, isActive, _ in
        effect.animation(.bouncy) { $0.scaleEffect(isActive ? 1.08 : 1.0) }
    }

// UIKit: opt-in UIButton pointer
let button = UIButton(configuration: .filled())
button.isPointerInteractionEnabled = true     // iOS 13.4+
button.pointerStyleProvider = { btn, _, _ in
    .init(effect: .highlight(UITargetedPreview(view: btn)))
}

// UIKit: custom view with UIPointerInteractionDelegate
final class AlbumTile: UIView, UIPointerInteractionDelegate {
    override init(frame: CGRect) {
        super.init(frame: frame)
        addInteraction(UIPointerInteraction(delegate: self))
    }
    required init?(coder: NSCoder) { fatalError() }
    func pointerInteraction(_ i: UIPointerInteraction,
                            styleFor region: UIPointerRegion) -> UIPointerStyle? {
        UIPointerStyle(effect: .lift(UITargetedPreview(view: self)))
    }
}
```

**`UIHoverGestureRecognizer`** (iOS 13+) gives you raw pointer entry/move/exit for custom cursors in drawing or annotation apps; combine with `UITouch.TouchType.indirectPointer` and the `UIApplicationSupportsIndirectInputEvents` Info.plist key for native (non-synthesized) pointer events. Prefer defaults — the HIG rule is that the system defaults are correct in ~90% of cases.

## 6. UIKit gesture recognizers: when to drop down

`UIGestureRecognizer` is the abstract base; each subclass translates raw `UITouch` events into discrete or continuous state transitions. Discrete gestures go `possible → recognized/failed`; continuous go `possible → began → changed* → ended/cancelled/failed`. Attach via `view.addGestureRecognizer(_:)`.

| Recognizer | Key properties | Purpose |
|---|---|---|
| `UITapGestureRecognizer` | `numberOfTapsRequired`, `numberOfTouchesRequired`, `buttonMaskRequired` (13.4+) | Discrete N-tap, M-touch |
| `UIPanGestureRecognizer` | `minimum/maximumNumberOfTouches`, `allowedScrollTypesMask` | Continuous drag; `translation(in:)`, `velocity(in:)` |
| `UIPinchGestureRecognizer` | `scale`, `velocity` | Two-finger scale |
| `UIRotationGestureRecognizer` | `rotation`, `velocity` | Two-finger rotate |
| `UILongPressGestureRecognizer` | `minimumPressDuration`, `allowableMovement`, `numberOfTapsRequired` | Press-and-hold, continuous |
| `UISwipeGestureRecognizer` | `direction`, `numberOfTouchesRequired` | Discrete directional; one direction per recognizer |
| `UIScreenEdgePanGestureRecognizer` | `edges` (UIRectEdge) | Pan starting at a screen edge |
| `UIHoverGestureRecognizer` | — (indirect pointer only) | Hover enter/move/exit |

**`require(toFail:)`** enforces ordering — a single-tap that waits for a double-tap recognizer to fail is the canonical example. The same relationship can be set declaratively by returning `true` from `gestureRecognizer(_:shouldRequireFailureOf:)` or its inverse.

`UIGestureRecognizerDelegate` has five arbitrating methods: **`gestureRecognizerShouldBegin(_:)`** (default `true`) vetoes recognition; **`gestureRecognizer(_:shouldReceive:)`** (touch/press/event variants) filters per-event — classic use is to reject touches that land on `UIControl` subviews; **`gestureRecognizer(_:shouldRecognizeSimultaneouslyWith:)`** (default `false`) enables two recognizers to fire on the same touch — returning `true` from *either* delegate is sufficient; **`gestureRecognizer(_:shouldRequireFailureOf:)`** and **`gestureRecognizer(_:shouldBeRequiredToFailBy:)`** set dynamic ordering requirements.

```swift
final class Canvas: UIView, UIGestureRecognizerDelegate {
    override init(frame: CGRect) {
        super.init(frame: frame)
        let pinch = UIPinchGestureRecognizer(target: self, action: #selector(onPinch))
        let rotate = UIRotationGestureRecognizer(target: self, action: #selector(onRot))
        let pan = UIPanGestureRecognizer(target: self, action: #selector(onPan))
        [pinch, rotate, pan].forEach { $0.delegate = self; addGestureRecognizer($0) }
    }
    required init?(coder: NSCoder) { fatalError() }

    func gestureRecognizer(_ g: UIGestureRecognizer,
                           shouldRecognizeSimultaneouslyWith o: UIGestureRecognizer) -> Bool {
        true  // classic sticker-manipulator: pinch + rotate + pan together
    }
    func gestureRecognizer(_ g: UIGestureRecognizer, shouldReceive touch: UITouch) -> Bool {
        !(touch.view is UIControl)
    }

    @objc private func onPinch(_ g: UIPinchGestureRecognizer) {
        transform = transform.scaledBy(x: g.scale, y: g.scale); g.scale = 1
    }
    @objc private func onRot(_ g: UIRotationGestureRecognizer) {
        transform = transform.rotated(by: g.rotation); g.rotation = 0
    }
    @objc private func onPan(_ g: UIPanGestureRecognizer) {
        let t = g.translation(in: superview)
        center = CGPoint(x: center.x + t.x, y: center.y + t.y)
        g.setTranslation(.zero, in: superview)
    }
}
```

Drop from SwiftUI to UIKit recognizers when you need: **fine-grained simultaneous recognition** with arbitrary decision logic; **custom state machines** via a `UIGestureRecognizer` subclass overriding `touchesBegan/Moved/Ended/Cancelled`; **multi-finger taps** (SwiftUI's `TapGesture` exposes only count); **hardware-specific input** (`allowedScrollTypesMask`, `buttonMaskRequired`); or **arbitration with `UIScrollView.panGestureRecognizer` or `interactivePopGestureRecognizer`**. On **iOS 18+**, bridge through `UIGestureRecognizerRepresentable`; pre-iOS-18, wrap with `UIViewRepresentable`.

## 7. High-level gesture patterns

**Pull-to-refresh.** SwiftUI's `.refreshable { }` modifier (iOS 15+, async closure) attaches to `List` or `ScrollView` (iOS 16+); the spinner remains until the closure returns. UIKit uses `UIRefreshControl` assigned to `UITableView.refreshControl` or `UIScrollView.refreshControl`, calling `endRefreshing()` when done. iOS 18 did not redesign `.refreshable`, but developers report regressions where custom `DragGesture`s on child views of `ScrollView` interfere with pull-to-refresh (forum FB14205678); the new iOS 18 `onScrollGeometryChange(for:of:action:)` and `scrollPosition` APIs help build custom pull interactions. iOS 26 restyles the spinner through Liquid Glass with no behavioral change.

```swift
List(items, id: \.self) { Text($0) }
    .refreshable { await viewModel.reload() }     // iOS 15+
```

**Swipe-to-dismiss sheets.** SwiftUI exposes `.interactiveDismissDisabled(_:)` (iOS 15+) to veto the gesture, typically bound to an `isDirty` flag, alongside `.presentationDetents` and `.presentationDragIndicator(.visible)` (iOS 16+). To **observe** dismiss attempts you still bridge `UIAdaptivePresentationControllerDelegate` — its `presentationControllerShouldDismiss(_:)` and `presentationControllerDidAttemptToDismiss(_:)` are the UIKit equivalents. Set `isModalInPresentation = true` on a UIViewController to block dismissal gesture entirely.

```swift
EditorView()
    .interactiveDismissDisabled(hasChanges)       // iOS 15+
    .presentationDetents([.medium, .large])       // iOS 16+
    .presentationDragIndicator(.visible)
```

**Pinch-to-zoom on images.** A SwiftUI-only zoom works for simple cases with `MagnifyGesture`, but a production photo viewer needs a focal-point pinch combined with pan-while-zoomed — `UIScrollView` is still the right tool, wrapped with `UIViewRepresentable`. Set `minimumZoomScale`, `maximumZoomScale`, implement `viewForZooming(in:)`, and add a double-tap gesture to reset/zoom-in.

```swift
struct ZoomableImage: View {
    @GestureState private var pinch: CGFloat = 1
    @State private var scale: CGFloat = 1
    var body: some View {
        Image("photo").resizable().scaledToFit()
            .scaleEffect(scale * pinch)
            .gesture(
                MagnifyGesture()                                    // iOS 17+
                    .updating($pinch) { v, s, _ in s = v.magnification }
                    .onEnded { v in scale = max(1, min(scale * v.magnification, 5)) }
            )
            .accessibilityZoomAction { action in                    // iOS 17+
                switch action.direction {
                case .zoomIn:  scale = min(scale + 0.25, 5)
                case .zoomOut: scale = max(scale - 0.25, 1)
                @unknown default: break
                }
            }
    }
}
```

## 8. Gesture conflicts and resolution

SwiftUI resolves conflicts by the **front-most/last-attached-wins** heuristic. Parent gestures are suppressed unless you opt in with `.simultaneousGesture` or `.highPriorityGesture`. The composition operators (`.simultaneously`, `.sequenced`, `.exclusively`) apply to gesture values, not views, and let you encode precise policies.

The second parameter to `.gesture(_:including:)` takes a **`GestureMask`**: `.all` (default, both this and subviews), `.gesture` (only this; subviews disabled for the touch), `.subviews` (only subviews; this disabled), `.none` (neither).

**`ScrollView` vs. `DragGesture` is the most common fight.** The scroll view's internal pan recognizer aggressively claims vertical translation. Adding a naive `DragGesture` to a child often breaks scrolling — especially on iOS 18. Fixes: use `.simultaneousGesture(DragGesture(minimumDistance: 20))` with a direction-check; set `scrollDisabled(true)` (iOS 17+) while your custom drag is active; or drop to UIKit and enable simultaneous recognition with the scroll view's `panGestureRecognizer` via `UIGestureRecognizerDelegate`.

```swift
// Direction-gated horizontal drag inside a vertical List
.simultaneousGesture(
    DragGesture(minimumDistance: 20)
        .onChanged { g in
            guard abs(g.translation.width) > abs(g.translation.height) else { return }
            offset = g.translation.width
        }
)
```

Nested `UIScrollView`s arbitrate via `isDirectionalLockEnabled` — the inner pan wins for the axis where it has content. When directions overlap, call `innerScroll.panGestureRecognizer.require(toFail: outerScroll.panGestureRecognizer)` or implement `shouldRecognizeSimultaneouslyWith`. **iOS 18 unified the cross-framework gesture system** so a UIKit recognizer can fail a SwiftUI gesture and vice versa, eliminating a long-standing integration pain.

### Gesture compatibility matrix

Legend: **✅ Simultaneous** — both can recognize on the same touch stream (delegate opt-in often required); **⚠️ Ordered** — need `require(toFail:)` / `.sequenced` / duration-gating; **❌ Conflict** — consume the same translation data, pick one; **➖ Orthogonal** — different input channel, no interaction.

|  | Tap | Double-Tap | Long-Press | Pan/Drag | Pinch/Magnify | Rotate | Swipe | Hover | Edge-Pan |
|---|---|---|---|---|---|---|---|---|---|
| **Tap** | — | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ | ➖ | ⚠️ |
| **Double-Tap** | ⚠️ | — | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ | ➖ | ⚠️ |
| **Long-Press** | ⚠️ | ⚠️ | — | ✅ (`.sequenced`) | ✅ | ✅ | ❌ | ➖ | ⚠️ |
| **Pan/Drag** | ⚠️ | ⚠️ | ✅ (sequenced) | — | ✅ | ✅ | ❌ | ➖ | ❌ |
| **Pinch/Magnify** | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | ➖ | ✅ |
| **Rotate** | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | ➖ | ✅ |
| **Swipe** | ⚠️ | ⚠️ | ❌ | ❌ | ✅ | ✅ | — (one/direction) | ➖ | ❌ |
| **Hover** | ➖ | ➖ | ➖ | ➖ | ➖ | ➖ | ➖ | — | ➖ |
| **Edge-Pan** | ⚠️ | ⚠️ | ⚠️ | ❌ | ✅ | ✅ | ❌ | ➖ | — (per-edge) |

**Reasoning.** Hover uses indirect-pointer phases disjoint from direct touches, so it's orthogonal to everything. Pan vs swipe, pan vs edge-pan, and swipe vs edge-pan all read the same translation stream — one must fail. Pinch + rotate + pan is the classic "sticker manipulator" and `UIScrollView` itself uses it; simultaneous recognition requires a delegate opt-in. Tap and long-press are duration-gated on the same touch: at `minimumPressDuration` the long-press wins; on an early lift the tap wins — they can coexist safely but one fires at a time.

## 9. Discoverability: HIG guidance

The single overarching rule, quoted from Apple's *Inputs → Touchscreen gestures*: **"Enable shortcut gestures to supplement standard gestures, not to replace them. People need simple, familiar ways to navigate and perform actions, even if it means an extra tap or two."** A navigation back button must be visible even when swipe-from-edge is supported; a delete control must exist in some menu even when swipe-to-delete is supported. This is Apple's progressive-disclosure principle encoded as a hard requirement.

Apple also forbids redefining standard gestures: **"Avoid using a familiar gesture to perform an action that's unique to your app… Avoid using standard gestures to perform nonstandard actions."** Custom gestures are appropriate only in games, drawing apps, and other contexts that already demand learned interaction models — and custom gestures must be **"easy to discover, easy to perform, not easily mistaken for another gesture, and not in conflict with any system gestures."**

**Hidden gestures are acceptable in narrow circumstances**: when they are system-standard (tap, swipe-to-reveal a list-row action, long-press for a context menu, pinch-to-zoom, drag-to-reorder) — because iOS users are culturally familiar with them — and when an equivalent visible control also exists for accessibility and motor-impairment reasons. The canonical hidden-gesture pattern is the **context menu** (`.contextMenu` in SwiftUI, `UIContextMenuInteraction` in UIKit), introduced in iOS 13 to replace 3D Touch and explicitly called out in WWDC 2019 session 224 (*Modernizing Your UI for iOS 13*): *"add contextual menus to every object in your App."* Context menus are acceptably hidden because iOS has trained users to long-press, and because they surface automatically to VoiceOver as the `.showMenu` accessibility action.

For novel custom gestures (onboarding drawing gestures, specialized games), use animated first-run hints, coach-marks, or persistent chevrons as affordances. Never rely on a user discovering a gesture through trial and error if it gates meaningful functionality.

## 10. Accessibility: every gesture needs a non-gesture alternative

Apple's HIG Accessibility guidance is explicit: **"Create alternative ways to perform gesture-based actions"** and **"Make your app's core functionality accessible through more than one type of physical interaction."** The technical reason is that iOS's motor-accessibility features simulate basic gestures but cannot reliably produce custom, path-based, timed, or concurrent gestures at real-time speeds.

**AssistiveTouch** presents a floating menu that simulates hardware buttons and a small library of gestures, and since iOS 13 supports external mice/trackpads. Users can record custom gestures, but playback is modal and sequential — choose finger count from a menu, then perform. This makes pinch-during-drag, timed multi-finger sequences, and concurrent gestures practically unusable. **Switch Control** scans through focusable elements one at a time; a user navigating with one switch **cannot physically perform any gesture** — only tap. Functionality reachable only via gesture is invisible to scanning. **Voice Control** lets users speak element labels (*"Tap Send"*) and **named accessibility actions** (*"Delete"*, *"Zoom in"*). This last point is why every custom gesture needs a named action: it's the single mechanism that simultaneously exposes functionality to the VoiceOver rotor, Switch Control menus, and Voice Control voice commands.

**VoiceOver** reinterprets standard gestures and reserves multi-finger gestures for navigation. Your single-finger gestures will not be delivered to your app when VoiceOver is on — instead, VoiceOver expects specific accessibility actions. The key verbs: single-tap focuses, double-tap activates (`.default`), two-finger double-tap = **Magic Tap** (`.magicTap`, typically play/pause or primary action), two-finger Z-scrub = **Escape** (`.escape`, dismiss a modal), three-finger swipe = Scroll (`.accessibilityScrollAction`), and rotor = custom navigation (`.accessibilityRotor`).

```swift
// SwiftUI: comprehensive accessibility for a gesture-rich view
PhotoViewer(photo: photo)
    .accessibilityAction(.magicTap) { vm.togglePlay() }
    .accessibilityAction(.escape)   { dismiss() }
    .accessibilityActions {                                      // iOS 16+
        Button("Zoom In")  { scale = min(scale + 0.25, 5) }
        Button("Zoom Out") { scale = max(scale - 0.25, 1) }
        Button("Share")    { share() }
        Button("Delete", role: .destructive) { delete() }
    }
    .accessibilityZoomAction { action in                         // iOS 17+
        switch action.direction {
        case .zoomIn:  scale = min(scale + 0.25, 5)
        case .zoomOut: scale = max(scale - 0.25, 1)
        @unknown default: break
        }
    }
    .accessibilityAdjustableAction { direction in                // sliders/steppers
        switch direction {
        case .increment: progress += 0.1
        case .decrement: progress -= 0.1
        @unknown default: break
        }
    }

// SwiftUI custom rotor (iOS 15+)
List(tasks) { Text($0.title) }
    .accessibilityRotor("Incomplete") {
        ForEach(tasks) { t in
            if !t.complete { AccessibilityRotorEntry(t.title, id: t.id) }
        }
    }

// UIKit: custom actions on a cell
cell.accessibilityCustomActions = [
    UIAccessibilityCustomAction(name: "Delete")  { _ in self.delete();  return true },
    UIAccessibilityCustomAction(name: "Archive") { _ in self.archive(); return true }
]
```

### Required accessibility alternative per gesture type

| Shipped gesture | Required non-gesture alternative |
|---|---|
| Tap | Usually automatic for `Button`; for custom views add `.accessibilityAddTraits(.isButton)` + `.accessibilityAction`. |
| Swipe (swipe-to-delete, swipe actions) | Named `accessibilityAction(named:)` — swipe actions on SwiftUI `List` do this automatically. |
| Drag (reorder, slider) | `.accessibilityAdjustableAction` for increments; named "Move Up"/"Move Down" for reorder. |
| Pinch/Magnify | `.accessibilityZoomAction` (iOS 17+), or +/− buttons, or explicit "Zoom In"/"Zoom Out" named actions. |
| Rotate | Named "Rotate Clockwise"/"Counterclockwise" actions, or a slider/stepper. |
| Long-press (context menu) | Use `.contextMenu { }` — SwiftUI surfaces it as `.showMenu` automatically; otherwise add a `.showMenu` action. |
| Primary play/pause/answer | Always add `.accessibilityAction(.magicTap)` in addition to any visible button. |
| Modal swipe-dismiss | `.accessibilityAction(.escape)` so the two-finger Z-scrub works. |

**iOS 17+ Assistive Access** simplifies UI for cognitive disabilities; **iOS 26** introduced the `AssistiveAccess` SwiftUI scene type so apps can present an alternate tap-only layout in that mode (WWDC25 session 238, *Customize your app for Assistive Access*). VoiceOver also gained **drag-and-drop support** in iOS 18 — WWDC24 session 10073 (*Catch up on accessibility in SwiftUI*) covers the drop-point overlay APIs for making `.draggable`/`.dropDestination` usable without sight.

## Anti-patterns to avoid

**Hijacking system gestures.** Adding a custom `UIScreenEdgePanGestureRecognizer` on the left edge inside a `UINavigationController` without coordinating with `interactivePopGestureRecognizer` disables the system back. Fix: disable the system recognizer explicitly, or return `true` from `shouldRecognizeSimultaneouslyWith`, or move the custom gesture off the left edge entirely.

**Undiscoverable-only interactions.** A two-finger long-press to reveal a hidden menu, with no affordance, fails every usability and accessibility test. Fix: add a visible disclosure chevron, a coach-mark on first run, or a tap-accessible menu button.

**Missing accessibility alternatives.** Pinch-to-zoom without `.accessibilityZoomAction`, swipe-to-delete without an Edit button, drag-to-reorder without named "Move Up/Down" actions — all ship regularly and all violate the HIG. Fix: provide named accessibility actions mirroring every gesture.

**Overloading gestures.** Single-tap to select, double-tap to open, long-press to edit, two-finger tap to share, swipe to delete — five actions on one cell exceeds working memory. Fix: reserve long-press for context menus (free accessibility via `.contextMenu`), use tap for the primary action, and surface the rest via a disclosure or menu button.

**Redefining convention.** Leading-swipe to delete (users expect trailing), pinch in a photo viewer that zooms *out*, or a list where pull-to-refresh instead loads older items — all break muscle memory. Fix: follow platform conventions; innovate only where the interaction is genuinely new.

**Horizontal drag inside vertical scroll without gating.** The most common iOS 18 regression. Fix: `.simultaneousGesture(DragGesture(minimumDistance: 20))` with a direction check, or drop to UIKit with proper delegate arbitration.

## WWDC sessions and authoritative references

| Session | Year / ID | URL |
|---|---|---|
| Introducing Drag and Drop | WWDC 2017 / 203 | developer.apple.com/videos/play/wwdc2017/203/ |
| Modern User Interaction on iOS | WWDC 2017 / 219 | developer.apple.com/videos/play/wwdc2017/219/ |
| Modernizing Your UI for iOS 13 (context menus, modern swipe/long-press) | WWDC 2019 / 224 | developer.apple.com/videos/play/wwdc2019/224/ |
| Build for the iPadOS pointer | WWDC 2020 / 10093 | developer.apple.com/videos/play/wwdc2020/10093/ |
| Design for the iPadOS pointer | WWDC 2020 / 10640 | developer.apple.com/videos/play/wwdc2020/10640/ |
| Handle trackpad and mouse input | WWDC 2020 / 10094 | developer.apple.com/videos/play/wwdc2020/10094/ |
| Meet Transferable | WWDC 2022 / 10062 | developer.apple.com/videos/play/wwdc2022/10062/ |
| What's new in SwiftUI (MagnifyGesture / RotateGesture renames) | WWDC 2023 / 10148 | developer.apple.com/videos/play/wwdc2023/10148/ |
| Build accessible apps with SwiftUI and UIKit | WWDC 2023 / 10036 | developer.apple.com/videos/play/wwdc2023/10036/ |
| What's new in SwiftUI (iOS 18, UIGestureRecognizerRepresentable) | WWDC 2024 / 10144 | developer.apple.com/videos/play/wwdc2024/10144/ |
| What's new in UIKit (unified UIKit ↔ SwiftUI gestures) | WWDC 2024 / 10118 | developer.apple.com/videos/play/wwdc2024/10118/ |
| Catch up on accessibility in SwiftUI | WWDC 2024 / 10073 | developer.apple.com/videos/play/wwdc2024/10073/ |
| What's new in SwiftUI (iOS 26, drag containers, NSGestureRecognizerRepresentable) | WWDC 2025 / 256 | developer.apple.com/videos/play/wwdc2025/256/ |
| Elevate the design of your iPad app (iPadOS 26 windowing gestures) | WWDC 2025 / 208 | developer.apple.com/videos/play/wwdc2025/208/ |
| Customize your app for Assistive Access | WWDC 2025 / 238 | developer.apple.com/videos/play/wwdc2025/238/ |

The most frequently requested session — "Modern Gestures" (WWDC 2019) — does not exist under that literal title. The closest canonical gesture handling sessions are **WWDC 2017 session 219** (*Modern User Interaction on iOS*) for iOS-13-era fundamentals and **WWDC 2019 session 224** (*Modernizing Your UI for iOS 13*) for the context-menu-replaces-3D-Touch transition that shapes modern gesture patterns.

## What actually changed in iOS 26, and what didn't

iOS 26's gesture story is narrower than marketing suggests. **What's real and confirmed** at WWDC 2025: `NSGestureRecognizerRepresentable` completes the UIKit/SwiftUI/AppKit bridging trilogy; the multi-item drag-and-drop surface (`dragContainer`, `DragConfiguration`, `onDragSessionUpdated`, `dragPreviewsFormation`) is a substantial SwiftUI upgrade; Liquid Glass provides new interactive material feedback via `.glassEffect(.regular.interactive())` that responds to touch, pointer, and motion in real time; iPadOS 26 adds flick-to-tile, grab-handle resize, top-swipe menu bar (via existing `commands`), double-swipe-home-to-minimize, and replaces the pointer blob with a traditional arrow; the `manipulable()` modifier and `surfaceSnappingInfo` bring visionOS-style 3D manipulation into the SwiftUI vocabulary. **What did not change**: the core 2D gesture primitives (`TapGesture`, `LongPressGesture`, `DragGesture`, `MagnifyGesture`, `RotateGesture`, `SpatialTapGesture`) ship unchanged; `.swipeActions`, `.refreshable`, `.interactiveDismissDisabled`, and the pointer style vocabulary ship unchanged; the HIG's accessibility mandate ships unchanged and was reinforced by the new `AssistiveAccess` scene.

**The practical takeaway for developers targeting both iOS 18 and iOS 26**: write your gesture code against the iOS 17 API set (`MagnifyGesture`, `RotateGesture`, `SpatialTapGesture`, `Transferable`, `.draggable`/`.dropDestination`), adopt `UIGestureRecognizerRepresentable` from iOS 18 where you need UIKit bridging, adopt the new iOS 26 drag containers only behind an availability check, and provide named accessibility actions for everything. The system hasn't moved the goalposts on what good gesture design looks like — it has only made it easier to implement and harder to implement badly.