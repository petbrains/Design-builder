---
name: ipad
description: iPad app design reference (iPadOS 18/26 windowing, menu bar, tiling, Liquid Glass)
platform: ios
---

# iPad app design reference for iPadOS 18 and iPadOS 26

This is a working reference for SwiftUI and UIKit developers building iPad apps that target **iPadOS 18** (current) and **iPadOS 26** (shipping since September 2025, currently on 26.4). iPadOS 26 introduced the most significant windowing rework in the platform's history — universal window resize, a persistent menu bar, Exposé, window tiling, traffic-light window controls, and Liquid Glass — and it deprecates several assumptions every iPad app has relied on since iOS 9. Adopt the new APIs now; in the release after iPadOS 26, `UIRequiresFullScreen` will be ignored, the `UIScene` life cycle will be mandatory, and all apps must support arbitrary resizing. The sections below cover each subsystem with working code, iPad‑vs‑iPhone behavior tables, anti‑patterns, and WWDC session references.

---

## 1. Sidebar navigation with NavigationSplitView

`NavigationSplitView` (iOS/iPadOS 16+) is the canonical container for iPad two‑ and three‑column layouts. It automatically collapses into a stack on compact width (iPhone, Slide Over, narrow Stage Manager tiles). **Never wrap a `NavigationSplitView` in a `NavigationStack` at the root** — they are mutually exclusive; nest a `NavigationStack` *inside* the detail column instead.

### 1.1 Two‑ vs three‑column choice

| Pattern | Example apps | When to use |
|---|---|---|
| **Two‑column** `sidebar:detail:` | Settings, Notes (flat), simple readers | Single‑level grouping → item detail |
| **Three‑column** `sidebar:content:detail:` | Mail (mailboxes → messages → body), Files (sources → files → preview) | Hierarchical: collection → items → item |

```swift
// Two-column
NavigationSplitView {
    List(items, selection: $selection) { item in
        NavigationLink(item.name, value: item)
    }
} detail: {
    if let selection { DetailView(item: selection) }
    else { ContentUnavailableView("Select an item", systemImage: "square.dashed") }
}

// Three-column
NavigationSplitView {
    SidebarView(selection: $folder)
} content: {
    MessageListView(folder: folder, selection: $message)
} detail: {
    if let message { MessageDetailView(message: message) }
    else { Text("Select a message") }
}
```

### 1.2 Style, width, visibility

`.navigationSplitViewStyle(_:)` has three options:

| Style | Behavior on iPad |
|---|---|
| `.automatic` | System default. Landscape → effectively `.balanced`; portrait → `.prominentDetail` (sidebar overlays). |
| `.balanced` | Sidebar/content push detail; detail shrinks. |
| `.prominentDetail` | Detail keeps full width at all times; sidebar slides over it. |

```swift
@State private var columnVisibility: NavigationSplitViewVisibility = .automatic

NavigationSplitView(columnVisibility: $columnVisibility) {
    SidebarList()
        .navigationSplitViewColumnWidth(min: 200, ideal: 240, max: 320)
} content: {
    ContentList()
        .navigationSplitViewColumnWidth(280)
} detail: {
    DetailView()
}
.navigationSplitViewStyle(.balanced)
```

`NavigationSplitViewVisibility` cases: `.automatic`, `.all`, `.doubleColumn` (content + detail, hides sidebar), `.detailOnly`. The binding is two‑way — the system updates it when the user toggles, and you can mutate it programmatically for deep links.

**Apply `.navigationSplitViewColumnWidth(...)` *inside* the column's root view**, not to the outer `NavigationSplitView`. The split view may ignore the width based on available space — it's a preference, not a guarantee.

### 1.3 Sidebar toolbar customization (iOS 17+)

```swift
NavigationSplitView {
    SidebarList()
        .toolbar(removing: .sidebarToggle)   // removes the default toggle
        .toolbar {
            ToolbarItemGroup(placement: .navigation) {
                Button("New Folder", systemImage: "folder.badge.plus") { newFolder() }
            }
        }
        .listStyle(.sidebar)                 // rounded-pill sidebar highlights
} detail: {
    Detail()
}
```

### 1.4 iPadOS 18 tab + sidebar unification (WWDC24 session 10147)

iPadOS 18's `TabView` can render as a **floating top tab bar or a sidebar**, with the user toggling between them. This is the modern replacement for the "tab bar on phone, sidebar on iPad" conditional pattern.

```swift
@AppStorage("MyTabViewCustomization") private var customization: TabViewCustomization

TabView {
    Tab("Watch Now", systemImage: "play", value: .watchNow) { WatchNowView() }
        .customizationID("Tab.watchNow")
        .customizationBehavior(.disabled, for: .sidebar, .tabBar)

    Tab("Library", systemImage: "books.vertical") { LibraryView() }
        .customizationID("Tab.library")

    TabSection("Collections") {
        ForEach(MyCollectionsTab.allCases) { tab in
            Tab(tab.title, systemImage: tab.icon) { tab.view }
                .customizationID(tab.customizationID)
        }
    }
    .customizationID("Tab.collections")
    .sectionActions {
        Button("New Collection", systemImage: "plus") { }
    }

    Tab(role: .search) { NavigationStack { SearchView() } }
}
.tabViewStyle(.sidebarAdaptable)          // user toggles tab bar ↔ sidebar
.tabViewCustomization($customization)     // persists drag-reorder + hide
```

`Tab` customization options: `.defaultVisibility(.hidden, for: .tabBar)`, `.customizationBehavior(.disabled, for: ...)`, `.dropDestination(for:action:)` on tab for collection drop targets.

### 1.5 Collapsing on iPhone and narrow iPad windows

On **compact horizontal size class** — iPhone portrait, iPad Slide Over, narrow Stage Manager tiles — `NavigationSplitView` collapses automatically into a push‑based stack starting at the sidebar. This means you **do not need a separate `NavigationStack`‑based root view for iPhone**; the same `NavigationSplitView` adapts. Do provide a `ContentUnavailableView` placeholder in the detail column — on iPad the detail column is visible on launch with `selection == nil`.

### 1.6 Deep linking with NavigationPath

```swift
@State private var selection: Item?
@State private var detailPath = NavigationPath()

NavigationSplitView {
    List(Item.all, selection: $selection) { NavigationLink($0.name, value: $0) }
} detail: {
    NavigationStack(path: $detailPath) {
        if let selection {
            ItemDetailView(item: selection)
                .navigationDestination(for: Route.self) { route in /* ... */ }
        } else {
            ContentUnavailableView("Pick an item", systemImage: "square.dashed")
        }
    }
}
.onOpenURL { url in
    if let item = Item.parse(url) {
        selection = item
        detailPath = NavigationPath([Route.item(item)])
    }
}
```

### 1.7 iPadOS 26 additions

Recompile with Xcode 26 and the sidebar floats over content as **Liquid Glass**. New modifiers:

```swift
TabView { /* ... */ }
    .tabBarMinimizeBehavior(.onScrollDown)       // floating tab bar shrinks
    .tabViewBottomAccessory { NowPlayingBar() }  // floats above tab bar

ContentView()
    .backgroundExtensionEffect()                 // extends artwork under glass
```

UIKit `UISplitViewController` gained **first‑class inspector column support** and **interactive separator resizing** in iPadOS 26 (WWDC25 session 282).

**Anti‑patterns:** wrapping `NavigationSplitView` in a `NavigationStack`; using `UIDevice.current.userInterfaceIdiom == .pad` to pick layout; forcing `.compact` size class to preserve iPhone‑style tabs (causes Liquid Glass glitches); omitting a detail placeholder; applying `.inspectorColumnWidth` outside the inspector closure; hard‑coding fixed sidebar widths that ignore Dynamic Type.

**WWDC sessions:** WWDC22 "The SwiftUI cookbook for navigation" (10054); WWDC22 "SwiftUI on iPad: Organize your interface" (110320); WWDC24 "Elevate your tab and sidebar experience in iPadOS" (10147); WWDC25 "What's new in SwiftUI" (256); WWDC25 "Build a SwiftUI app with the new design" (323); WWDC25 "Make your UIKit app more flexible" (282).

---

## 2. Pointer interactions (trackpad and mouse on iPad)

iPad with Magic Keyboard, Magic Trackpad, or Magic Mouse is now a primary input mode. **Ignoring pointer hover states is a top iPad anti‑pattern.**

### 2.1 SwiftUI hover effects

`.hoverEffect(_:)` has been available since iPadOS 13.4. `Button`, `NavigationLink`, `Toggle`, and most system controls get an effect automatically; apply the modifier explicitly to **custom** views.

| Style | Use for |
|---|---|
| `.automatic` | Default; system picks based on shape |
| `.highlight` | Larger views / list rows — pointer stays visible, region tints |
| `.lift` | Compact tappable items ≤ ~175pt — pointer morphs into shape, scales up, drops shadow |

```swift
Text("Lift").padding().hoverEffect(.lift)
Text("Highlight").padding().hoverEffect(.highlight)
Button("No Hover") { }.hoverEffectDisabled()
```

### 2.2 `pointerStyle(_:)` (iOS 17+) — customize the cursor shape

```swift
VStack {
    Text("Link").pointerStyle(.link)
    Text("Editable").pointerStyle(.text)
    Rectangle().frame(width: 4, height: 60).pointerStyle(.columnResize)
    Rectangle().frame(width: 60, height: 4).pointerStyle(.rowResize)
    Rectangle().frame(width: 80, height: 80)
        .pointerStyle(.frameResize(position: .bottomTrailing))
    Color.gray.frame(width: 60, height: 60)
        .pointerStyle(.image(Image(systemName: "paintbrush"), hotSpot: .center))
    Text("Grab me")
        .pointerStyle(isDragging ? .grabbing : .grab)
}
.pointerVisibility(.hidden)   // hide the pointer in immersive regions
```

Full variant set: `.default`, `.link`, `.text`, `.horizontalText`, `.verticalText`, `.zoomIn`, `.zoomOut`, `.grab`, `.grabbing`, `.columnResize`, `.rowResize`, `.frameResize(position:directions:)`, `.move`, `.image(_:hotSpot:)`.

### 2.3 UIKit — `UIPointerInteraction`

More customization than SwiftUI; use when you need custom regions or animations.

```swift
final class HoverableTile: UIView, UIPointerInteractionDelegate {
    override init(frame: CGRect) {
        super.init(frame: frame)
        addInteraction(UIPointerInteraction(delegate: self))
    }
    required init?(coder: NSCoder) { fatalError() }

    func pointerInteraction(_ interaction: UIPointerInteraction,
                            regionFor request: UIPointerRegionRequest,
                            defaultRegion: UIPointerRegion) -> UIPointerRegion? {
        UIPointerRegion(rect: bounds.insetBy(dx: -8, dy: -8))
    }

    func pointerInteraction(_ interaction: UIPointerInteraction,
                            styleFor region: UIPointerRegion) -> UIPointerStyle? {
        guard let view = interaction.view else { return nil }
        let preview = UITargetedPreview(view: view)
        let effect: UIPointerEffect = .lift(preview)
        let shape: UIPointerShape = .roundedRect(view.bounds, radius: 12)
        return UIPointerStyle(effect: effect, shape: shape)
    }

    func pointerInteraction(_ interaction: UIPointerInteraction,
                            willEnter region: UIPointerRegion,
                            animator: UIPointerInteractionAnimating) {
        animator.addAnimations { self.transform = .init(scaleX: 1.04, y: 1.04) }
    }
}
```

`UIPointerEffect` cases: `.automatic(_)`, `.highlight(_)`, `.lift(_)`, `.hover(_, preferredTintMode:, prefersShadow:, prefersScaledContent:)`. `UIPointerShape` factories: `.path(_)`, `.roundedRect(_, radius:)`, `.verticalBeam(length:)`, `.horizontalBeam(length:)`. `UIPointerStyle.hidden()` hides the cursor; `.system()` returns the default arrow.

**When to customize vs defaults.** System controls (`UIButton`, `Button`, `Toggle`, list rows, `UIBarButtonItem`) already have the right effect — don't stack custom effects on top. Use `.lift` for small icon tiles, `.highlight` for list/collection rows, custom `pointerStyle` for resize handles, text surfaces, and draggable grips.

**Anti‑patterns:** ignoring pointer entirely; `.lift` on huge (>175pt) views — pointer disappears; pointer styles used non‑semantically (e.g., `.link` everywhere); stacking custom effects on controls that already hover.

**WWDC:** WWDC20 "Design for the iPadOS pointer" (10640); WWDC20 "Build for the iPadOS pointer" (10093); WWDC20 "Handle trackpad and mouse input" (10094); WWDC24 "What's new in SwiftUI" (10144) introduced SwiftUI `PointerStyle`.

---

## 3. Keyboard support

On iPad with a hardware keyboard, users expect standard shortcuts and Tab/arrow navigation. **Shipping an iPad app without keyboard shortcuts is a missed table‑stakes feature**; iPadOS 26's persistent menu bar makes the gap far more visible.

### 3.1 `keyboardShortcut`

```swift
Button("Save")      { save() }.keyboardShortcut("s")                      // ⌘S
Button("Save As…")  { saveAs() }.keyboardShortcut("s", modifiers: [.command, .shift])
Button("Cancel")    { dismiss() }.keyboardShortcut(.cancelAction)          // ⎋
Button("OK")        { commit() }.keyboardShortcut(.defaultAction)          // ⏎
Button("Top")       { scrollTop() }.keyboardShortcut(.upArrow, modifiers: .command)
```

Default modifier is `.command`. `KeyEquivalent` includes `.upArrow`, `.downArrow`, `.leftArrow`, `.rightArrow`, `.escape`, `.return`, `.tab`, `.delete`, `.deleteForward`, `.home`, `.end`, `.pageUp`, `.pageDown`, `.space`, `.clear`. **Gotcha:** a shortcut on a toolbar button only appears in the discoverability HUD if the button has a label and uses `.labelStyle(.titleAndIcon)`.

### 3.2 Focus system — `@FocusState`, `focused`, `focusable`, `focusSection`

```swift
struct LoginForm: View {
    enum Field: Hashable { case email, password }
    @FocusState private var focus: Field?
    @State private var email = "", password = ""

    var body: some View {
        Form {
            TextField("Email", text: $email).focused($focus, equals: .email)
            SecureField("Password", text: $password).focused($focus, equals: .password)
            Button("Sign in") { focus = nil; signIn() }
                .keyboardShortcut(.defaultAction)
        }
        .onSubmit {
            switch focus {
            case .email: focus = .password
            case .password: signIn()
            default: break
            }
        }
        .onAppear { focus = .email }
    }
}
```

`focusSection()` groups focusable children so Tab moves between sections and arrow keys navigate within. `focusable(_:interactions:)` (iOS 17+) takes `.activate`, `.edit`, or both. `focusEffectDisabled()` suppresses the blue focus halo on custom views.

### 3.3 Tab and arrow navigation

- **Tab** moves focus between focusable areas and `focusSection` groups — handled automatically by the iPadOS focus engine (WWDC21 session 10260).
- **Arrow keys** navigate selection in `List`/`Table` with a bound `selection:`; **Return** triggers the primary action. No code required.
- Don't eat Tab/arrows unless you absolutely must; let the system drive.

### 3.4 `.searchable` and ⌘F

`.searchable` does not bind ⌘F automatically. Wire it manually:

```swift
@State private var searchText = ""
@FocusState private var searchFocused: Bool

var body: some Scene {
    WindowGroup {
        NavigationStack { NotesList() }
            .searchable(text: $searchText)
            .searchFocused($searchFocused)    // iOS 17+
    }
    .commands {
        CommandGroup(after: .textEditing) {
            Button("Find…") { searchFocused = true }
                .keyboardShortcut("f")         // ⌘F
        }
    }
}
```

### 3.5 Menu bar (iPadOS 16+ discoverability HUD; iPadOS 26 visible menu bar)

Attach `.commands { }` to a `Scene` — on iPadOS 16+ it populates the ⌘‑hold HUD; on iPadOS 26 it produces the always‑on visible menu bar at the top of the screen.

```swift
@main
struct EditorApp: App {
    @State private var calibrate = true

    var body: some Scene {
        WindowGroup { ContentView() }
            .commands {
                CommandMenu("Tools") {
                    Button("Joystick…") { }
                        .keyboardShortcut("j", modifiers: [.command, .option])
                    Divider()
                    Toggle("Calibrate Automatically", isOn: $calibrate)
                }
                CommandGroup(replacing: .newItem) {
                    Button("New Document")       { newDoc() }.keyboardShortcut("n")
                    Button("New From Template…") { newFromTemplate() }
                        .keyboardShortcut("n", modifiers: [.command, .shift])
                }
                CommandGroup(after: .pasteboard) {
                    Button("Paste and Match Style") { pasteMatch() }
                        .keyboardShortcut("v", modifiers: [.command, .option, .shift])
                }
                SidebarCommands()
                ToolbarCommands()
                TextEditingCommands()
                TextFormattingCommands()
                InspectorCommands()           // iOS 17+
            }
    }
}
```

Standard `CommandGroupPlacement` anchors: `.appInfo`, `.newItem`, `.saveItem`, `.importExport`, `.printItem`, `.undoRedo`, `.pasteboard`, `.textEditing`, `.textFormatting`, `.toolbar`, `.sidebar`, `.windowSize`, `.help`. Apple's design rule (WWDC25 session 208): organize by frequency, **dim inactive items — never hide menus based on context**.

### 3.6 `onKeyPress` (iOS 17+)

```swift
Rectangle()
    .focusable()
    .focused($focused)
    .onKeyPress(keys: [.leftArrow, .rightArrow], phases: [.down, .repeat]) { press in
        x += (press.key == .leftArrow ? -10 : 10)
        return .handled
    }
    .onKeyPress(characters: .alphanumerics, phases: .up) { press in
        handle(press.characters); return .handled
    }
```

Return `.handled` to consume or `.ignored` to bubble up the responder chain.

### 3.7 UIKit — `UIKeyCommand` and `UIMenuBuilder`

```swift
override var keyCommands: [UIKeyCommand]? {
    [
        UIKeyCommand(title: "New",  action: #selector(newDoc),
                     input: "n", modifierFlags: .command),
        UIKeyCommand(title: "Find…", action: #selector(find),
                     input: "f", modifierFlags: .command,
                     discoverabilityTitle: "Find in Document")
    ]
}

// AppDelegate — populate the main menu
override func buildMenu(with builder: UIMenuBuilder) {
    super.buildMenu(with: builder)
    guard builder.system == .main else { return }
    let cmd = UIKeyCommand(title: "Release Notes",
                           action: #selector(showReleaseNotes),
                           input: "r", modifierFlags: [.command, .option])
    let menu = UIMenu(title: "", options: .displayInline, children: [cmd])
    builder.insertSibling(menu, afterMenu: .help)
}
```

Set `wantsPriorityOverSystemBehavior = true` only if you must override Tab/arrows — the focus engine is preferred.

**Anti‑patterns:** shipping without ⌘N / ⌘O / ⌘S / ⌘F / ⌘W / ⌘, / ⌘Z / ⌘⇧Z; rebinding system shortcuts; missing `.labelStyle(.titleAndIcon)`; not setting initial focus; swallowing Tab/arrows.

**WWDC:** WWDC20 "Support hardware keyboards in your app" (10109); WWDC21 "Focus on iPad keyboard navigation" (10260); WWDC21 "Direct and reflect focus in SwiftUI" (10023); WWDC23 "The SwiftUI cookbook for focus" (10162).

---

## 4. Apple Pencil integration

### 4.1 PencilKit canvas

```swift
import PencilKit

final class DrawingViewController: UIViewController, PKCanvasViewDelegate, PKToolPickerObserver {
    private let canvasView = PKCanvasView()
    private var toolPicker: PKToolPicker!

    override func viewDidLoad() {
        super.viewDidLoad()
        canvasView.frame = view.bounds
        canvasView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        canvasView.delegate = self
        canvasView.drawingPolicy = .anyInput   // .default | .anyInput | .pencilOnly
        view.addSubview(canvasView)

        let pencil = UIPencilInteraction()
        pencil.delegate = self
        view.addInteraction(pencil)
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        toolPicker = PKToolPicker()                                // iOS 14+
        toolPicker.setVisible(true, forFirstResponder: canvasView)
        toolPicker.addObserver(canvasView)
        toolPicker.addObserver(self)
        canvasView.becomeFirstResponder()
    }

    func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
        // Debounce-save
    }
    func toolPickerFramesObscuredDidChange(_ toolPicker: PKToolPicker) {
        let obscured = toolPicker.frameObscured(in: view)
        canvasView.contentInset = obscured.isNull ? .zero :
            UIEdgeInsets(top: 0, left: 0,
                         bottom: view.bounds.height - obscured.minY, right: 0)
        canvasView.scrollIndicatorInsets = canvasView.contentInset
    }
}
```

**Drawing policy semantics:** `.default` — Pencil‑only if paired, otherwise finger. `.anyInput` — both. `.pencilOnly` — Pencil required.

**`PKToolPicker` is floating on iPad** (repositionable, minimizable into a puck), docked on iPhone, and an ornament on visionOS.

### 4.2 Serializing drawings

```swift
// Save
let data = canvasView.drawing.dataRepresentation()
try data.write(to: url, options: .atomic)

// Load
canvasView.drawing = try PKDrawing(data: Data(contentsOf: url))

// Export
let image = canvasView.drawing.image(from: canvasView.drawing.bounds,
                                     scale: UIScreen.main.scale)
```

SwiftData‑friendly wrapper:

```swift
@Model final class Design {
    private var drawingData = Data()
    var drawing: PKDrawing {
        get { (try? PKDrawing(data: drawingData)) ?? PKDrawing() }
        set { drawingData = newValue.dataRepresentation() }
    }
}
```

### 4.3 iPadOS 18 configurable tool picker (WWDC24 session 10214)

```swift
let items: [PKToolPickerItem] = [
    PKToolPickerInkingItem(identifier: "pen-black",
                           inkType: .pen, color: .black, width: 2),
    PKToolPickerInkingItem(identifier: "pen-red",
                           inkType: .pen, color: .red, width: 2),
    PKToolPickerInkingItem(identifier: "marker",
                           inkType: .marker, color: .yellow, width: 12),
    PKToolPickerEraserItem(eraserType: .vector),
    PKToolPickerLassoItem(),
    PKToolPickerRulerItem(),
    PKToolPickerScribbleItem(),     // iPadOS 18: handwriting-to-text
    myCustomStampItem
]

let picker = PKToolPicker(toolItems: items)
picker.accessoryItem = UIBarButtonItem(
    image: UIImage(systemName: "textformat"),
    primaryAction: UIAction { [weak self] _ in self?.insertTextBox() })
```

Ink types: `.pen`, `.pencil`, `.marker`, `.monoline`, `.fountainPen`, `.watercolor`, `.crayon`. iPadOS 26 adds a new **reed pen** calligraphy ink (system palette; exposed to apps via `PKInkingTool`).

### 4.4 SwiftUI wrapper

```swift
struct CanvasView: UIViewRepresentable {
    @Binding var drawing: PKDrawing
    let toolPicker: PKToolPicker

    func makeUIView(context: Context) -> PKCanvasView {
        let canvas = PKCanvasView()
        canvas.drawingPolicy = .anyInput
        canvas.delegate = context.coordinator
        canvas.drawing = drawing
        toolPicker.setVisible(true, forFirstResponder: canvas)
        toolPicker.addObserver(canvas)
        DispatchQueue.main.async { canvas.becomeFirstResponder() }
        return canvas
    }
    func updateUIView(_ canvas: PKCanvasView, context: Context) {
        if canvas.drawing != drawing { canvas.drawing = drawing }  // avoid undo reset
    }
    func makeCoordinator() -> Coordinator { Coordinator(self) }

    final class Coordinator: NSObject, PKCanvasViewDelegate {
        var parent: CanvasView
        init(_ p: CanvasView) { parent = p }
        func canvasViewDrawingDidChange(_ cv: PKCanvasView) { parent.drawing = cv.drawing }
    }
}
```

### 4.5 Scribble

`UITextField`, `UITextView`, and SwiftUI `TextField`/`TextEditor` accept Scribble **automatically**. Use `UIScribbleInteraction` only to customize or suppress (e.g., inside a drawing region):

```swift
func scribbleInteraction(_ interaction: UIScribbleInteraction,
                         shouldBeginAt location: CGPoint) -> Bool {
    !drawingRegion.contains(location)
}
```

`UIIndirectScribbleInteraction` lets a non‑text view act as a handwriting target (e.g., an empty annotation region).

### 4.6 Hover, double‑tap, squeeze, barrel roll (Pencil 2 and Pro)

**Hover — SwiftUI:**

```swift
Rectangle()
    .onContinuousHover(coordinateSpace: .local) { phase in
        switch phase {
        case .active(let loc): showPreview(at: loc)
        case .ended: hidePreview()
        }
    }
    .hoverEffect(.lift)
```

**Hover — UIKit** (access tilt, distance, roll):

```swift
let hover = UIHoverGestureRecognizer(target: self, action: #selector(handle(_:)))
view.addGestureRecognizer(hover)

@objc func handle(_ g: UIHoverGestureRecognizer) {
    let azimuth  = g.azimuthAngle(in: view)
    let altitude = g.altitudeAngle
    let z        = g.zOffset                // points above screen, iPadOS 16.1+
    let roll     = g.rollAngle              // Pencil Pro only, iPadOS 17.5+
    // ...
}
```

During contact: `touch.preciseLocation(in:)`, `touch.force`, `touch.azimuthAngle(in:)`, `touch.altitudeAngle`, `touch.rollAngle` (Pencil Pro). Apply `touchesEstimatedPropertiesUpdated(_:)` for high‑fidelity updates.

**Double‑tap (Pencil 2 / Pro):**

```swift
func pencilInteractionDidTap(_ interaction: UIPencilInteraction) {
    switch UIPencilInteraction.preferredTapAction {
    case .ignore: break
    case .switchEraser: toggleEraser()
    case .switchPrevious: selectPreviousTool()
    case .showColorPalette: showColorPalette()
    case .runSystemShortcut: break         // never delivered
    @unknown default: break
    }
}
```

**Squeeze (Pencil Pro, iPadOS 17.5+):**

```swift
// UIKit
func pencilInteraction(_ interaction: UIPencilInteraction,
                       didReceiveSqueeze squeeze: UIPencilInteraction.Squeeze) {
    if UIPencilInteraction.preferredSqueezeAction == .showContextualPalette,
       squeeze.phase == .ended {
        let anchor = squeeze.hoverPose?.location ?? .zero
        presentContextualPalette(at: anchor)
    }
}

// SwiftUI
@Environment(\.preferredPencilSqueezeAction) var preferredAction

Canvas { _, _ in }
    .onPencilSqueeze { phase in
        guard preferredAction == .showContextualPalette,
              case let .ended(value) = phase else { return }
        if let anchor = value.hoverPose?.anchor { paletteAnchor = anchor }
        showPalette = true
    }
```

Squeeze phases: `.began`, `.changed`, `.ended`, `.cancelled`. `hoverPose` exposes `location`, `zOffset`, `azimuthAngle`, `altitudeAngle`, `rollAngle`.

**Barrel roll** is surfaced in `UITouch.rollAngle`, `UIHoverGestureRecognizer.rollAngle`, and SwiftUI `PencilHoverPose.roll`. **Use roll only for stroke‑appearance modulation** — don't bind it to sliders or zoom.

**Haptics (Pencil Pro) — use high‑level APIs, not `CHHapticEngine`:**

```swift
// UIKit
let feedback = UICanvasFeedbackGenerator(view: view)
feedback.alignmentOccurred(at: point)
feedback.pathCompleted(at: point)

// SwiftUI
MyCanvas()
    .sensoryFeedback(.alignment,    trigger: aligned)
    .sensoryFeedback(.pathComplete, trigger: snapped)
```

### 4.7 iPadOS 26 — PaperKit (WWDC25 session 285)

New framework that layers markup on top of PencilKit + PDFKit:

```swift
import PaperKit

final class RecipeAnnotationVC: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        let markup = PaperMarkup(bounds: view.bounds)
        let vc = MarkupEditViewController(markup: markup,
                                          latestSupportedFeatureSet: .latest)
        addChild(vc); view.addSubview(vc.view); vc.didMove(toParent: self)
    }
}
```

iPadOS 26 also reduces system‑wide Pencil latency from ~20 ms to ~9 ms — no code changes.

**Anti‑patterns:** `PKToolPicker.shared(for:)` (deprecated iOS 14); re‑assigning `canvasView.drawing` on every SwiftUI state update (resets undo stack); calling `setVisible(true,...)` when canvas isn't first responder; placing critical actions only in `accessoryItem` (hidden when picker minimizes); binding `rollAngle` to UI controls.

**WWDC:** WWDC19 "Introducing PencilKit" (221); WWDC20 "Meet Scribble for iPad" (10106); WWDC20 "Inspect, modify, and construct PencilKit drawings" (10148); WWDC24 "Squeeze the most out of Apple Pencil" (10214); WWDC25 "Meet PaperKit" (285).

---

## 5. Multitasking and multi‑window

### 5.1 Supporting multiple scenes

```xml
<key>UIApplicationSceneManifest</key>
<dict>
  <key>UIApplicationSupportsMultipleScenes</key><true/>
  <key>UISceneConfigurations</key>
  <dict>
    <key>UIWindowSceneSessionRoleApplication</key>
    <array>
      <dict>
        <key>UISceneConfigurationName</key><string>Main Scene</string>
        <key>UISceneDelegateClassName</key>
        <string>$(PRODUCT_MODULE_NAME).SceneDelegate</string>
      </dict>
    </array>
  </dict>
</dict>
```

**`UIScene` life cycle will be mandatory** in the release after iPadOS 26 when building against the new SDK (WWDC25 session 282). Migrate now via TN3187.

### 5.2 UIKit scene lifecycle

```swift
class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?
    var timerModel = TimerModel()

    func scene(_ scene: UIScene,
               willConnectTo session: UISceneSession,
               options connectionOptions: UIScene.ConnectionOptions) {
        let ws = scene as! UIWindowScene
        ws.sizeRestrictions?.minimumSize = CGSize(width: 500, height: 600)
        let window = UIWindow(windowScene: ws)
        window.rootViewController = TimerViewController(model: timerModel)
        window.makeKeyAndVisible()
        self.window = window
    }

    func sceneDidEnterBackground(_ scene: UIScene) { timerModel.pause() }

    func stateRestorationActivity(for scene: UIScene) -> NSUserActivity? {
        let a = NSUserActivity(activityType: "com.example.timer.ui-state")
        a.userInfo = ["selectedTimeFormat": timerModel.selectedTimeFormat]
        return a
    }
    func scene(_ scene: UIScene, restoreInteractionStateWith a: NSUserActivity) {
        if let f = a.userInfo?["selectedTimeFormat"] as? String {
            timerModel.selectedTimeFormat = f
        }
    }
}
```

**Opening a new window programmatically:**

```swift
let options = UIWindowScene.ActivationRequestOptions()
options.preferredPresentationStyle = .prominent

let activity = NSUserActivity(activityType: "com.example.newDocument")
activity.targetContentIdentifier = "doc-xyz"

UIApplication.shared.requestSceneSessionActivation(
    nil, userActivity: activity, options: options,
    errorHandler: { print($0) })
```

### 5.3 SwiftUI scenes

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup { ContentView() }

        WindowGroup(id: "search") { SearchView() }
            .defaultSize(width: 500, height: 500)

        WindowGroup(id: "editor", for: Document.ID.self) { $id in
            EditorView(id: id)
        }
        .handlesExternalEvents(preferring: ["editor"], allowing: ["*"])

        DocumentGroup(newDocument: TextDocument()) { config in
            EditorView(document: config.document)
        }
    }
}

struct SomeView: View {
    @Environment(\.openWindow) var openWindow
    @Environment(\.supportsMultipleWindows) var supportsMultipleWindows

    var body: some View {
        if supportsMultipleWindows {
            Button("Open Search")   { openWindow(id: "search") }
            Button("Open Document") { openWindow(id: "editor", value: doc.id) }
        }
    }
}
```

### 5.4 State restoration

| Mechanism | Scope | Use for |
|---|---|---|
| `@SceneStorage("key")` | Per scene/window | Selected tab, scroll position, inspector open flag |
| `@AppStorage("key")` | App‑wide | Theme, account ID, feature flags |
| `NSUserActivity` | Per scene (UIKit) | Document ID, deep link, editor state |
| `.onContinueUserActivity(_:perform:)` | SwiftUI | Handoff, Spotlight re‑entry |

### 5.5 Stage Manager (iPadOS 16+) and iPadOS 26 interplay

Stage Manager is on M1+ iPads in iPadOS 18 (up to 4 windows + external display). In iPadOS 26 it is **off by default**, layered atop the new universal windowing system, and no longer capped at 4 per stage. Apps must be resilient to arbitrary sizes — don't assume a minimum corresponds to a full‑screen geometry.

**Anti‑patterns:** reading `UIScreen.main.bounds` for window size (`UIScreen.main` is deprecated — use the scene's coordinate space); not declaring `UIApplicationSupportsMultipleScenes = YES`; large `minimumSize` (e.g., 1024×768) that blocks tiling and stage grouping; "open in place" replacing content in the sole window instead of opening a new window per document.

**WWDC:** WWDC22 "Meet desktop-class iPad" and "What's new in iPad app design"; WWDC25 "Elevate the design of your iPad app" (208); WWDC25 "Make your UIKit app more flexible" (282).

---

## 6. Window sizing (iPadOS 18 vs iPadOS 26)

### 6.1 iPadOS 18 baseline

- Split View minimum: apps collapse to **~320pt width**, entering compact horizontal size class.
- Stage Manager windows: typical **~500–768pt** minimum depending on app.
- `UIWindowScene.sizeRestrictions` is honored best‑effort and may be `nil` on devices/configurations where restrictions aren't allowed (e.g., Stage Manager disabled).

```swift
let ws = scene as! UIWindowScene
ws.sizeRestrictions?.minimumSize = CGSize(width: 500, height: 600)
ws.sizeRestrictions?.maximumSize = CGSize(width: 2000, height: 2000)
```

SwiftUI:

```swift
WindowGroup { ContentView().frame(minWidth: 500, minHeight: 400) }
    .defaultSize(width: 900, height: 700)
    .windowResizability(.contentMinSize)
```

`.windowResizability` options: `.automatic` (system default), `.contentSize` (window matches content exactly), `.contentMinSize` (min from content, free to grow). `.windowStyle`, `.windowToolbarStyle`, `.defaultPosition` are macOS‑only and ignored on iPad.

### 6.2 iPadOS 26 universal windowing

iPadOS 26 introduced **resize handles on every app**, a persistent **menu bar**, **Exposé**, **window tiling**, and **traffic‑light window controls** in the top‑left. Apple Newsroom (June 9, 2025): *"An entirely new powerful and intuitive windowing system … close, minimize, resize, or tile."*

**Deprecations and mandates:**

| Deprecation | Impact |
|---|---|
| `UIRequiresFullScreen` | Console warning now; **ignored** in the release after iPadOS 26 |
| Orientation locking app‑wide | Support for all orientations will be required |
| Non‑scene app lifecycle | `UIScene` becomes mandatory in next major release when built with the new SDK |
| Automatic letterboxing | Once built with iOS 26 SDK, the system no longer scales or letterboxes for new screen sizes |

**New control style hook:**

```swift
func preferredWindowingControlStyle(
    for scene: UIWindowScene
) -> UIWindowScene.WindowingControlStyle {
    return .unified
}
```

**Layout guide that avoids the traffic‑light controls:**

```swift
let guide = containerView.layoutGuide(for: .margins(cornerAdaptation: .horizontal))
NSLayoutConstraint.activate([
    contentView.topAnchor.constraint(equalTo: guide.topAnchor),
    contentView.leadingAnchor.constraint(equalTo: guide.leadingAnchor),
    contentView.bottomAnchor.constraint(equalTo: guide.bottomAnchor),
    contentView.trailingAnchor.constraint(equalTo: guide.trailingAnchor)
])
```

If you don't adopt, the system inserts a compatibility safe area above your toolbar — wastes vertical space.

**Observe live geometry efficiently:**

```swift
func windowScene(_ windowScene: UIWindowScene,
                 didUpdateEffectiveGeometry previousGeometry: UIWindowScene.Geometry) {
    let g = windowScene.effectiveGeometry
    let size = g.coordinateSpace.bounds.size
    if !g.isInteractivelyResizing && size != previousSceneSize {
        previousSceneSize = size
        gameAssetManager.updateAssets(sceneSize: size)
    }
}
```

New `UIWindowScene.Geometry` properties: `isInteractivelyResizing`, `isInterfaceOrientationLocked`, `coordinateSpace.bounds`.

**Per‑view orientation lock** (for games / camera flows) replaces `UIRequiresFullScreen`:

```swift
class RaceViewController: UIViewController {
    override var prefersInterfaceOrientationLocked: Bool { isDriving }

    var isDriving = false {
        didSet {
            if isDriving != oldValue {
                setNeedsUpdateOfPrefersInterfaceOrientationLocked()
            }
        }
    }
}
```

**New SwiftUI scene modifier** (iOS/iPadOS/macOS 26):

```swift
TabView(selection: $selection.animation()) { /* ... */ }
    .windowResizeAnchor(.top)   // tailors origin of resize animation
```

**iPadOS 26 adoption checklist:**

1. Remove `UIRequiresFullScreen` from Info.plist (migrate via TN3192).
2. Adopt `UIScene` life cycle (TN3187).
3. Support all orientations.
4. Set conservative `sizeRestrictions?.minimumSize` — or none.
5. Add `.commands { }` to populate the menu bar.
6. Verify `NavigationSplitView` columns hide/show cleanly at every width.
7. Adopt `.margins(cornerAdaptation: .horizontal)` layout guide so toolbars wrap around traffic‑light controls.
8. Gate expensive re‑renders behind `!isInteractivelyResizing`.
9. Open a new window per document (additive windowing); provide descriptive window titles.
10. Remove custom sheet backgrounds so Liquid Glass can render.

### 6.3 iPadOS 18 vs iPadOS 26 windowing at a glance

| Feature | iPadOS 18 | iPadOS 26 |
|---|---|---|
| Split View / Slide Over | Yes, via `•••` menu | Replaced by universal windowing; Slide Over restored in 26.1 as single resizable panel |
| Stage Manager | M1+ only, 4 max | All supported iPads, no hard 4‑cap, off by default |
| Free window resize | Stage Manager only | **Universal** via bottom‑right handle |
| Window controls | System overlay | **Traffic‑light** in top‑left |
| Menu bar | ⌘‑hold HUD | Always‑on visible menu bar |
| Exposé | — | **New** |
| Tiling | — | **New** — halves, thirds, quarters |
| `UIRequiresFullScreen` | Respected | **Deprecated** |
| `UIScene` lifecycle | Optional | Mandatory next major release |
| `.windowResizeAnchor` | — | **New** |
| `preferredWindowingControlStyle(for:)` | — | **New** |
| `isInteractivelyResizing` | — | **New** |
| Remembered last size/position | No | Yes — system restores |

---

## 7. Adaptive layouts

**Use size classes, not idiom.** A user in Slide Over on a 13" iPad Pro sees `.pad` idiom but `.compact` horizontal size class — they want the iPhone layout.

```swift
@Environment(\.horizontalSizeClass) var hSize
@Environment(\.verticalSizeClass)   var vSize
```

| Case | Preferred approach |
|---|---|
| Column count, stack axis, paddings | Size class |
| Platform features (Pencil, pointer, keyboard) | Idiom OK |
| Window geometry in Stage Manager | Size class |

### 7.1 Branch (different views) vs reflow (same view, responsive)

**Reflow** whenever the same structure works at multiple sizes — use `ViewThatFits`, adaptive grids, `containerRelativeFrame`, `Grid`, `HStack`/`VStack` + `Spacer`. **Branch** only when the fundamental structure differs (sidebar vs tab bar).

```swift
// Reflow via ViewThatFits — picks first child that fits
ViewThatFits {
    HStack { Avatar(); Name(); BioText() }     // widest
    VStack { Avatar(); Name(); BioText() }
    VStack { Avatar(); Name() }                 // fallback
}

// Adaptive grid — more columns on iPad automatically
private var columns: [GridItem] {
    let min: CGFloat = hSize == .regular ? 180 : 110
    return [GridItem(.adaptive(minimum: min, maximum: 260), spacing: 12)]
}
LazyVGrid(columns: columns, spacing: 12) {
    ForEach(photos) { PhotoCell(photo: $0) }
}
```

### 7.2 `containerRelativeFrame` (iOS 17+)

```swift
ScrollView(.horizontal) {
    LazyHStack(spacing: 16) {
        ForEach(articles) { article in
            ArticleCard(article: article)
                .containerRelativeFrame(.horizontal, count: 3, span: 1, spacing: 16)
        }
    }
}

// Cap reading width at 600 regardless of device
Text(body)
    .containerRelativeFrame(.horizontal) { width, _ in min(width * 0.9, 600) }
```

### 7.3 Full compact → regular example

```swift
struct AdaptiveApp: View {
    @Environment(\.horizontalSizeClass) private var hSize
    @State private var selection: Folder?

    var body: some View {
        if hSize == .regular {
            NavigationSplitView {
                FolderList(selection: $selection)
            } detail: {
                if let selection {
                    NavigationStack { ItemsView(folder: selection) }
                } else {
                    ContentUnavailableView("Select a folder", systemImage: "folder")
                }
            }
        } else {
            NavigationStack {
                FolderList(selection: $selection)
                    .navigationDestination(for: Folder.self) { ItemsView(folder: $0) }
            }
        }
    }
}
```

### 7.4 "Stretched iPhone" anti‑pattern

Apple explicitly calls this out in HIG "Designing for iPadOS." Symptoms to fix:

- Single full‑width column of list rows on iPad regular → replace with sidebar + detail or a grid
- Sheets pinned to phone width with huge margins → use `.presentationSizing(.form)` / `.page`
- Fixed iPhone layout with no multi‑column path → branch on size class
- Same app ignores Pencil, pointer, keyboard shortcuts
- `UIRequiresFullScreen=YES` to avoid multitasking → remove it

---

## 8. Inspector pattern

`.inspector(isPresented:content:)` (iOS 17+) is the right surface for **long‑lived metadata or property controls shown alongside the current content**. On iPad regular, it renders as a trailing column; on iPhone and narrow iPad windows it renders as a sheet.

```swift
struct PhotoEditor: View {
    @State private var inspectorShown = true
    @State private var photo: Photo = .sample

    var body: some View {
        NavigationStack {
            PhotoCanvas(photo: $photo)
                .toolbar {
                    ToolbarItem(placement: .primaryAction) {
                        Button {
                            inspectorShown.toggle()
                        } label: {
                            Label("Inspector", systemImage: "slider.horizontal.3")
                        }
                    }
                }
        }
        .inspector(isPresented: $inspectorShown) {
            PhotoInspector(photo: $photo)
                .inspectorColumnWidth(min: 220, ideal: 280, max: 420)
                .presentationDetents([.medium, .large])           // iPhone sheet
                .presentationBackgroundInteraction(.enabled)
        }
    }
}
```

Apply the modifier **as high in the hierarchy as possible** — typically to the root or the `NavigationSplitView` — so column positioning is correct. Apply `.inspectorColumnWidth(...)` to the view *inside* the inspector closure; it has no effect on a sheet presentation.

| Surface | Best for |
|---|---|
| **Inspector** | Metadata / edit controls for the currently shown content; kept open while working |
| **Detail pane** | The primary content itself (what you're reading/editing) |
| **Sheet** | Self‑contained modal task (compose, share, onboarding) |
| **Popover** | Short‑lived, anchored controls (format picker from a toolbar button) |

Heuristic: *metadata about the current content, visible while editing* → inspector. *Self‑contained sub‑task* → sheet. *Anchored to a control* → popover.

**iPadOS 26 UIKit:** `UISplitViewController` gained first‑class inspector support with resizable separators (WWDC25 session 282):

```swift
let split = UISplitViewController(style: .tripleColumn)
split.setViewController(sidebarVC,   for: .primary)
split.setViewController(contentVC,   for: .supplementary)
split.setViewController(detailVC,    for: .secondary)
split.setViewController(inspectorVC, for: .inspector)   // iPadOS 26+
split.show(.inspector)
```

---

## 9. Drag and drop

On iPad, cross‑app drag and drop is one of the platform's defining features. The modern path is `Transferable` (iOS 16+); the UIKit path remains `UIDragInteraction` / `UIDropInteraction` with `NSItemProvider`.

### 9.1 `Transferable` — declare once, works for drag, copy/paste, share, PhotosPicker

```swift
import CoreTransferable
import UniformTypeIdentifiers

extension UTType {
    static let profile = UTType(exportedAs: "com.example.app.profile")
}

struct Profile: Codable, Identifiable {
    var id = UUID()
    var name: String
    var bio: String
    var portraitURL: URL?
}

extension Profile: Transferable {
    static var transferRepresentation: some TransferRepresentation {
        CodableRepresentation(contentType: .profile)   // full fidelity
        ProxyRepresentation(exporting: \.name)          // plain-text fallback
    }
}
```

**Representation choices** — order matters; first matching wins:

| Type | Use when |
|---|---|
| `CodableRepresentation(contentType:)` | Both sides are your app, model is `Codable` |
| `DataRepresentation(contentType:exporting:importing:)` | In‑memory binary (PNG, custom blob) |
| `FileRepresentation(contentType:exporting:importing:)` | Large on‑disk payload (video, PDF) |
| `ProxyRepresentation(exporting:)` | Fallback to another Transferable type |

**Critical ordering:** declare `FileRepresentation` *before* `ProxyRepresentation(URL)`, or "Save to Files" may save a `.txt` of the URL string instead of the file.

```swift
struct Video: Transferable {
    let file: URL
    static var transferRepresentation: some TransferRepresentation {
        FileRepresentation(contentType: .mpeg4Movie) { video in
            SentTransferredFile(video.file)
        } importing: { received in
            let dest = try FileManager.default.url(for: .moviesDirectory,
                in: .userDomainMask, appropriateFor: nil, create: true)
                .appendingPathComponent(received.file.lastPathComponent)
            try FileManager.default.copyItem(at: received.file, to: dest)
            return Video(file: dest)
        }
        ProxyRepresentation(exporting: \.file)
    }
}
```

### 9.2 SwiftUI `.draggable` / `.dropDestination`

```swift
@State private var photos: [Profile] = sampleProfiles
@State private var isDropTargeted = false

LazyVGrid(columns: [.init(.adaptive(minimum: 120))]) {
    ForEach(photos) { profile in
        PortraitCell(profile: profile)
            .draggable(profile) {
                PortraitCell(profile: profile).frame(width: 80, height: 80)
            }
    }
}
.dropDestination(for: Profile.self) { items, location in
    photos.append(contentsOf: items)
    return true
} isTargeted: { isDropTargeted = $0 }
.background(isDropTargeted ? Color.accentColor.opacity(0.15) : .clear)
```

### 9.3 UIKit drag and drop

```swift
final class PhotoVC: UIViewController,
                     UIDragInteractionDelegate,
                     UIDropInteractionDelegate {

    @IBOutlet var imageView: UIImageView!

    override func viewDidLoad() {
        super.viewDidLoad()
        imageView.isUserInteractionEnabled = true        // required
        imageView.addInteraction(UIDragInteraction(delegate: self))
        view.addInteraction(UIDropInteraction(delegate: self))
    }

    func dragInteraction(_ interaction: UIDragInteraction,
                         itemsForBeginning session: UIDragSession) -> [UIDragItem] {
        guard let image = imageView.image else { return [] }
        let item = UIDragItem(itemProvider: NSItemProvider(object: image))
        item.localObject = image
        return [item]
    }

    // Multi-item drag (iPad): add items from other views to the same session
    func dragInteraction(_ interaction: UIDragInteraction,
                         itemsForAddingTo session: UIDragSession,
                         withTouchAt point: CGPoint) -> [UIDragItem] {
        guard let image = imageView.image else { return [] }
        return [UIDragItem(itemProvider: NSItemProvider(object: image))]
    }

    func dropInteraction(_ interaction: UIDropInteraction,
                         canHandle session: UIDropSession) -> Bool {
        session.canLoadObjects(ofClass: UIImage.self)
    }

    func dropInteraction(_ interaction: UIDropInteraction,
                         sessionDidUpdate session: UIDropSession) -> UIDropProposal {
        UIDropProposal(operation: session.localDragSession == nil ? .copy : .move)
    }

    func dropInteraction(_ interaction: UIDropInteraction,
                         performDrop session: UIDropSession) {
        session.loadObjects(ofClass: UIImage.self) { [weak self] items in
            if let image = items.first as? UIImage {
                self?.imageView.image = image
            }
        }
    }
}
```

### 9.4 Spring loading (iPad)

`UISpringLoadedInteraction` lets drag hover activate a target (e.g., tab button) so the user can navigate mid‑drag.

```swift
myButton.isSpringLoaded = true  // works on any UIControl subclass

let spring = UISpringLoadedInteraction { interaction, context in
    self.navigateToFolder()
}
view.addInteraction(spring)
```

**Anti‑patterns:** missing a plain‑text `ProxyRepresentation` fallback — pastes into Mail/WhatsApp become useless; `FileRepresentation` declared after `ProxyRepresentation(URL)`; blocking the main thread in `performDrop` / `loadObjects` completion; forgetting `isUserInteractionEnabled = true` on image views and labels (they default to `false`).

**WWDC:** WWDC17 "Introducing Drag and Drop" (203); WWDC17 "Mastering Drag and Drop" (223); WWDC20 "Drag and drop in SwiftUI" (10105); WWDC22 "Meet Transferable" (10062).

---

## 10. Context menus and previews

Context menus are **accelerators, not the only path** — always expose the same actions in the main UI (toolbar, inspector, detail view). On iPad they're triggered by long‑press (touch), two‑finger trackpad click, right‑click (mouse), or Control‑click; iPadOS 26 also supports the hardware menu key when focused.

### 10.1 SwiftUI

```swift
PhotoCell(photo: photo)
    .contextMenu {
        Button("Share")   { share(photo) }
        Button("Add to…") { add(photo) }
        Menu("Move To") {
            Button("Inbox")   { move(.inbox) }
            Button("Archive") { move(.archive) }
        }
        Divider()
        Button(role: .destructive) { delete(photo) }
        label: { Label("Delete", systemImage: "trash") }
    } preview: {
        AsyncImage(url: photo.fullURL) { $0.resizable().scaledToFit() }
            placeholder: { ProgressView() }
            .frame(width: 320, height: 320)
    }
```

Selection‑based menus on `List`/`Table`:

```swift
List(notes, selection: $selection) { NoteRow(note: $0) }
    .contextMenu(forSelectionType: Note.ID.self) { ids in
        if ids.isEmpty {
            Button("New Note", systemImage: "plus") { create() }
        } else if ids.count == 1, let id = ids.first {
            Button("Open") { open(id) }
            Button("Rename") { rename(id) }
            Button(role: .destructive) { delete([id]) }
            label: { Label("Delete", systemImage: "trash") }
        } else {
            Button(role: .destructive) { delete(Array(ids)) }
            label: { Label("Delete \(ids.count)", systemImage: "trash") }
        }
    } primaryAction: { ids in
        open(ids.first!)    // double-click / double-tap / Return
    }
```

### 10.2 UIKit

```swift
func contextMenuInteraction(_ interaction: UIContextMenuInteraction,
                            configurationForMenuAtLocation location: CGPoint)
-> UIContextMenuConfiguration? {
    UIContextMenuConfiguration(identifier: nil) {
        let vc = UIHostingController(rootView: CardPreview(card: self.card))
        vc.preferredContentSize = CGSize(width: 320, height: 480)
        return vc
    } actionProvider: { _ in
        UIMenu(children: [
            UIAction(title: "Edit",  image: UIImage(systemName: "pencil"))  { _ in },
            UIAction(title: "Share", image: UIImage(systemName: "square.and.arrow.up")) { _ in },
            UIMenu(title: "Move To", image: UIImage(systemName: "folder"), children: [
                UIAction(title: "Inbox")   { _ in },
                UIAction(title: "Archive") { _ in }
            ]),
            UIAction(title: "Delete",
                     image: UIImage(systemName: "trash"),
                     attributes: .destructive) { _ in }
        ])
    }
}

// Shape the highlight for rounded cards so corners aren't square
func contextMenuInteraction(_ interaction: UIContextMenuInteraction,
                            previewForHighlightingMenuWithConfiguration configuration: UIContextMenuConfiguration)
-> UITargetedPreview? {
    let p = UIPreviewParameters()
    p.visiblePath = UIBezierPath(roundedRect: bounds, cornerRadius: 16)
    return UITargetedPreview(view: self, parameters: p)
}
```

Use `UIDeferredMenuElement.uncached { completion in … }` for asynchronously populated submenus.

**iPad vs iPhone:**

| | iPhone | iPad |
|---|---|---|
| Trigger | Long press | Long press / right‑click / 2‑finger trackpad click / menu key |
| Preview size | Modest | Larger — design assets accordingly |
| Open latency | Standard | Faster with pointer |
| Hover sneak‑peek | — | Yes when pointer attached |

**Anti‑patterns:** action *only* in the context menu; 15+ items in one flat menu (break into `Section`s and `Menu` submenus); long‑press trigger *and* a primary tap that fights it; square highlight on rounded cards (fix with `UIPreviewParameters.visiblePath`); heavy sync work in the preview provider (use `UIDeferredMenuElement`).

**WWDC:** WWDC19 "Modernizing Your UI for iOS 13"; WWDC22 "What's new in iPad app design" (10009); WWDC22 "Adopt desktop-class editing interactions" (10071).

---

## 11. Toolbar density on iPad

iPad has far more toolbar real estate than iPhone — **hiding actions in an overflow `•••` menu when the bar is 80% empty is a classic anti‑pattern.** `.toolbarRole(.editor)` / `.toolbarRole(.browser)` unlocks the center of the bar.

### 11.1 Placements

| Placement | iPad behavior |
|---|---|
| `.automatic` | System picks (usually trailing) |
| `.principal` | Center — use for short titles or compact pickers only |
| `.navigationBarLeading` / `.topBarLeading` | Leading |
| `.navigationBarTrailing` / `.topBarTrailing` | Trailing |
| `.primaryAction` | Most prominent action; trailing; iOS 26 gets prominent glass |
| `.secondaryAction` | Center when `toolbarRole(.editor)` / `.browser` is set; otherwise `•••` |
| `.confirmationAction` | "Done" — trailing, prominent glass in iOS 26 |
| `.cancellationAction` | "Cancel" — leading |
| `.bottomBar` | Bottom — great for two‑handed iPad use |
| `.status` | Center of bottom bar |
| `.keyboard` | Above the software keyboard |

### 11.2 `.toolbarRole` — the iPad density lever

```swift
NoteEditor()
    .toolbar { /* primary + secondary actions */ }
    .toolbarRole(.editor)          // iPad regular: title leading, .secondaryAction items center
```

Apply only on iPad regular — compact widths ignore it and keep the centered title.

### 11.3 Customizable toolbars (iOS 16+)

```swift
NoteEditor()
    .toolbar(id: "noteEditor") {
        ToolbarItem(id: "save", placement: .primaryAction) {
            Button("Save", systemImage: "tray.and.arrow.down") { save() }
        }
        ToolbarItem(id: "favorite", placement: .secondaryAction, showsByDefault: true) {
            Toggle(isOn: $isFavorite) { Label("Favorite", systemImage: "heart") }
        }
        ToolbarItem(id: "share", placement: .secondaryAction) {
            ShareLink(item: note.url)
        }
        ToolbarItem(id: "lock", placement: .secondaryAction, showsByDefault: false) {
            Button("Lock", systemImage: "lock") { lock() }
                .customizationBehavior(.disabled, for: .popover)
        }
    }
    .toolbarRole(.editor)
    .toolbarTitleMenu {
        Button("Rename…")   { rename() }
        Button("Move…")     { move() }
        Button("Duplicate") { duplicate() }
        Divider()
        Button(role: .destructive) { delete() }
        label: { Label("Delete", systemImage: "trash") }
    }
```

IDs must be unique and stable — SwiftUI persists user customization by ID. `showsByDefault: false` hides an item until the user adds it. `ToolbarTitleMenu` adds a chevron next to the navigation title — perfect for rename/move/duplicate without crowding the bar.

### 11.4 iOS 26 — ToolbarSpacer, DefaultToolbarItem, prominent glass

```swift
.toolbar {
    ToolbarItemGroup(placement: .topBarTrailing) {
        Button("Filter", systemImage: "line.3.horizontal.decrease.circle") { }
        Button("Sort",   systemImage: "arrow.up.arrow.down") { }
    }
    ToolbarSpacer(.fixed, placement: .topBarTrailing)    // splits capsules
    ToolbarItem(placement: .topBarTrailing) {
        Button("Add", systemImage: "plus") { }
    }
}
```

Standard toolbars automatically gain Liquid Glass when recompiled with Xcode 26. Provide SF Symbols for every toolbar action — symbol‑only buttons are emphasized in the new design. `DefaultToolbarItem(kind: .search, placement: .bottomBar)` participates in the iPadOS 26 toolbar↔search morph. Use `.sharedBackgroundVisibility(.hidden)` on a toolbar item to detach it from the shared glass capsule.

### 11.5 UIKit equivalents

```swift
let new = UIBarButtonItem(systemItem: .add,
                          primaryAction: UIAction { _ in create() })
new.title = "New"
new.menu  = UIMenu(children: [
    UIAction(title: "Note")   { _ in newNote() },
    UIAction(title: "Folder") { _ in newFolder() }
])
navigationItem.rightBarButtonItems = [new]
navigationItem.style = .editor                // iPadOS 16+ — same intent as .toolbarRole
navigationItem.titleMenuProvider = { suggested in
    UIMenu(children: suggested + [UIAction(title: "Rename") { _ in }])
}

navigationItem.customizationIdentifier = "main"
navigationItem.centerItemGroups = [ /* UIBarButtonItemGroup.fixedGroup / .movableGroup / .optionalGroup */ ]
```

### 11.6 When to show vs collapse

- iPad regular + `.toolbarRole(.editor)`: show all primary + frequent secondary actions in the bar; the center is yours.
- Compact (Slide Over, narrow split, iPhone): collapse to 2–3 visible items + `•••` overflow `Menu`.
- Use `.bottomBar` on iPad only when two‑handed reach matters and the nav bar is genuinely full.

**Anti‑patterns:** 8 actions hidden in `•••` on a 13" iPad; inconsistent placements for the same action across sibling screens; missing `.labelStyle(.titleAndIcon)` (shortcut won't show in the HUD); free‑form `TextField` in `ToolbarItemGroup(placement: .topBarTrailing)` (iPadOS 17.4+ layout regression); bulky custom controls in `.principal`; custom‑drawing your own nav bar instead of `.toolbar` (you lose Liquid Glass, customization, and focus engine).

**WWDC:** WWDC22 "SwiftUI on iPad: Add toolbars, titles, and more" (110343); WWDC22 "SwiftUI on iPad: Organize your interface" (110320); WWDC22 "What's new in iPad app design" (10009); WWDC23 "What's new in SwiftUI" (10148); WWDC25 "Meet Liquid Glass"; WWDC25 "Build a SwiftUI app with the new design" (323).

---

## 12. Cross‑cutting iPad‑vs‑iPhone summary

| Subsystem | iPhone (compact) | iPad (regular) |
|---|---|---|
| Navigation | NavigationStack, tab bar at bottom | NavigationSplitView 2/3‑column, sidebar or floating tab bar (sidebarAdaptable) |
| Hover effects | N/A | Required for polish; default on system controls |
| `pointerStyle` | No effect | Honored with pointer device |
| Keyboard shortcuts | Rare | First‑class; ⌘‑hold HUD; iPadOS 26 visible menu bar |
| Focus engine | Limited | Tab / arrow nav across `focusable` / `focusSection` |
| Pencil | — | PKCanvasView, Scribble, hover, squeeze, barrel roll, haptics |
| Context menus | Long press; modest | Long press / right‑click / 2‑finger trackpad; richer; larger previews |
| Toolbars | Compact, overflow common | `toolbarRole(.editor)` unlocks center; customizable; Liquid Glass capsules |
| Inspector | Sheet | Trailing column |
| Drag and drop | Intra‑app (iOS 15+ cross‑app) | Cross‑app is a platform feature; multi‑item drag |
| Multitasking | N/A | Split View, Stage Manager, universal windowing (iPadOS 26) |
| State restoration | Per scene | Per window/scene — critical with multi‑window |

---

## 13. WWDC session index

| Session | Title | Year |
|---|---|---|
| 10054 | The SwiftUI cookbook for navigation | WWDC22 |
| 110320 | SwiftUI on iPad: Organize your interface | WWDC22 |
| 110343 | SwiftUI on iPad: Add toolbars, titles, and more | WWDC22 |
| 10009 | What's new in iPad app design | WWDC22 |
| 10062 | Meet Transferable | WWDC22 |
| 10071 | Adopt desktop-class editing interactions | WWDC22 |
| 10023 | Direct and reflect focus in SwiftUI | WWDC21 |
| 10260 | Focus on iPad keyboard navigation | WWDC21 |
| 10109 | Support hardware keyboards in your app | WWDC20 |
| 10106 | Meet Scribble for iPad | WWDC20 |
| 10093 | Build for the iPadOS pointer | WWDC20 |
| 10094 | Handle trackpad and mouse input | WWDC20 |
| 10640 | Design for the iPadOS pointer | WWDC20 |
| 10148 | Inspect, modify, and construct PencilKit drawings | WWDC20 |
| 10105 | Drag and drop in SwiftUI | WWDC20 |
| 10162 | The SwiftUI cookbook for focus | WWDC23 |
| 10147 | Elevate your tab and sidebar experience in iPadOS | WWDC24 |
| 10144 | What's new in SwiftUI | WWDC24 |
| 10214 | Squeeze the most out of Apple Pencil | WWDC24 |
| 208 | Elevate the design of your iPad app | WWDC25 |
| 256 | What's new in SwiftUI | WWDC25 |
| 243 | What's new in UIKit | WWDC25 |
| 282 | Make your UIKit app more flexible | WWDC25 |
| 284 | Build a UIKit app with the new design | WWDC25 |
| 323 | Build a SwiftUI app with the new design | WWDC25 |
| 285 | Meet PaperKit | WWDC25 |

Tech notes: **TN3154** (Adopting SwiftUI navigation split view), **TN3187** (Migrating to the UIKit scene‑based life cycle), **TN3192** (Migrating from the deprecated `UIRequiresFullScreen` key).

---

## 14. Consolidated anti‑pattern checklist

The single most important rule: **an iPad app is not a stretched iPhone app.** Specifically avoid:

- Using `UIDevice.current.userInterfaceIdiom == .pad` for layout decisions instead of size classes
- Wrapping `NavigationSplitView` inside a `NavigationStack` at root
- Shipping without keyboard shortcuts (⌘N / ⌘O / ⌘S / ⌘F / ⌘W / ⌘Z / ⌘⇧Z)
- Ignoring pointer hover states on custom views
- Fixed sidebar widths that ignore Dynamic Type or use hardcoded points without min/ideal/max
- Overflow `•••` menus on a 13" iPad when the toolbar is 80% empty — use `.toolbarRole(.editor)`
- Not providing a detail column `ContentUnavailableView` placeholder — iPad launches with detail visible
- `UIRequiresFullScreen = YES` — deprecated iPadOS 26, ignored in the next major release
- Omitting `UIApplicationSupportsMultipleScenes = YES` — blocks multi‑window on iPad
- Reading `UIScreen.main.bounds` for window size — deprecated; use the scene's coordinate space
- Large `minimumSize` (e.g., 1024×768) in `UIWindowScene.sizeRestrictions` — blocks tiling and Stage Manager
- Non‑scene `UIApplicationDelegate` lifecycle — becomes mandatory in the release after iPadOS 26
- Locking orientation app‑wide via `supportedInterfaceOrientations` — support for all orientations will be required; use per‑VC `prefersInterfaceOrientationLocked` for legitimate cases
- Re‑rendering expensive assets during interactive resize — gate on `!geometry.isInteractivelyResizing`
- "Open in place" replacing content in one window instead of opening a new window per document
- Toolbar drawn into the top‑left without using `.margins(cornerAdaptation: .horizontal)` — collides with iPadOS 26 traffic‑light controls
- Applying `.inspectorColumnWidth(...)` outside the inspector closure — no effect
- `PKToolPicker.shared(for:)` — deprecated iOS 14; use `PKToolPicker()` or the iPadOS 18 `init(toolItems:)`
- Re‑assigning `PKCanvasView.drawing` on every SwiftUI state change — resets undo stack
- Binding Pencil Pro `rollAngle` to UI controls (sliders, zoom) — use it only for stroke appearance
- Declaring `ProxyRepresentation(URL)` before `FileRepresentation` in `Transferable` — iOS 16 Save‑to‑Files saves a `.txt` of the URL
- Missing a plain‑text `ProxyRepresentation` fallback — paste into Mail/WhatsApp becomes useless
- `isUserInteractionEnabled` left `false` on `UIImageView`/`UILabel` used as drag sources
- Forcing `.environment(\.horizontalSizeClass, .compact)` on iPad to preserve the old tab bar — causes Liquid Glass glitches in iPadOS 26
- Custom sheet backgrounds that block Liquid Glass material
- Custom‑drawing a "navigation bar" instead of using `.toolbar` — loses Liquid Glass, customization, and focus engine integration
- Missing `.labelStyle(.titleAndIcon)` on toolbar buttons with shortcuts — shortcut won't appear in the ⌘‑HUD

## Conclusion

iPadOS 26 is the forcing function Apple has been telegraphing since Stage Manager shipped in 2022 — apps that don't resize cleanly, don't use the scene life cycle, don't populate a menu bar, and don't support all orientations are now officially on borrowed time. The good news: each subsystem above has a small, well‑defined adoption path. **Make the three deprecations your first pass** — remove `UIRequiresFullScreen`, migrate to `UIScene`, stop locking orientation. Then invest in the four "polish" axes that actually separate native iPad apps from ports: a real multi‑column navigation structure (`NavigationSplitView` or `.tabViewStyle(.sidebarAdaptable)`), complete keyboard and pointer support, Pencil Pro squeeze/barrel‑roll/haptics for creative apps, and a `.toolbarRole(.editor)` toolbar that uses the iPad's width instead of hiding behind `•••`. Apps that do this feel at home on a 13" iPad Pro in full windowing with a trackpad and Pencil — apps that skip it will visibly fall behind as users migrate to the new windowing model.