---
name: layout
description: iOS layout & spacing reference (safe areas, size classes, margins, readable content, Dynamic Type)
platform: ios
---

# iOS layout and spacing — a professional reference for iOS 18 and iOS 26

Apple's iOS layout system is a three-way negotiation between **device geometry** (safe areas, size classes, window sizes), **content semantics** (layout margins, readable content guide, spacing scales), and **developer intent** (SwiftUI layout primitives, UIKit constraints). Getting it right means your app looks correct on an iPhone SE in landscape, an iPadOS 26 freeform window resized to 480 pt wide, a Dynamic-Type-AX5 user's screen, and everything in between.

This reference synthesizes Apple's official documentation, WWDC sessions from 2014–2025, and empirical community findings (Use Your Loaf, Hacking with Swift, objc.io, Swift by Sundell, Swift with Majid, Point-Free) into a working guide targeted at iOS 18 (stable) and iOS 26 (current, released September 2025). Two ideas run through every section: **never hardcode device assumptions**, and **prefer semantic APIs over geometry**. When Apple's documentation is sparse, community empirical findings are flagged.

---

## 1. Safe areas

The safe area is the portion of a view unobscured by bars (status, nav, tab, toolbar), device hardware (notch, Dynamic Island, rounded corners), and system affordances (home indicator, software keyboard). It replaced iOS 10's `topLayoutGuide`/`bottomLayoutGuide` in iOS 11 (**WWDC 2017 · Session 412 "UIKit: Apps for Every Size and Shape"**).

### Device inset reference (portrait, no bars)

| Device | top | bottom | landscape left/right |
|---|---|---|---|
| iPhone SE / 8 (home button) | 20 | 0 | 0 |
| iPhone X/XS/11 Pro (notch) | 44 | 34 | 44 |
| iPhone 11–14 (notch) | 47 | 34 | 47 |
| iPhone 14 Pro / 15 / 16 (Dynamic Island) | 59 | 34 | 59 |
| iPhone 16 Pro / 16 Pro Max | 62 | 34 | 62 |
| iPhone 17 / 17 Pro / 17 Pro Max | 62 | 34 | **62 + 20 top** (new regression) |
| iPhone Air (6.5″) | 68 | 34 | 68 |
| iPad (all, no bars) | 24 | 20 | 0 |

**iPhone 17 in landscape reintroduces a 20-pt top inset** — a novel behavior versus prior Dynamic Island devices — undocumented by Apple and reported by Use Your Loaf in September 2025. Never hardcode `34` or `59`.

### ASCII — iPhone 17 Pro, portrait

```
┌────────────────────────┐ ← y = 0
│    ▓ Dynamic Is. ▓     │ ← top inset = 62 pt
├─ - - - - - - - - - - ──┤ ← safeAreaLayoutGuide.top
│                        │
│     SAFE AREA          │
│                        │
├─ - - - - - - - - - - ──┤ ← safeAreaLayoutGuide.bottom
│       ▬▬▬▬▬            │   bottom inset = 34 pt
└────────────────────────┘
```

### UIKit API

```swift
// UIView
var safeAreaInsets: UIEdgeInsets            // readonly
var safeAreaLayoutGuide: UILayoutGuide      // constrain against this
func safeAreaInsetsDidChange()              // override

// UIViewController
var additionalSafeAreaInsets: UIEdgeInsets  // push content in further
func viewSafeAreaInsetsDidChange()          // override
```

```swift
final class ArticleVC: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        additionalSafeAreaInsets = .init(top: 16, left: 0, bottom: 0, right: 0)

        let g = view.safeAreaLayoutGuide
        NSLayoutConstraint.activate([
            body.topAnchor.constraint(equalTo: g.topAnchor),
            body.leadingAnchor.constraint(equalTo: g.leadingAnchor),
            body.trailingAnchor.constraint(equalTo: g.trailingAnchor)
        ])
    }
}
```

**Propagation (empirical, not formally documented):** a child's `safeAreaInsets` reflects only the portion of the child intersecting an unsafe root region. A child entirely inside the root safe area reports `.zero`; children past the root's unsafe edge have insets **clamped** to the root's insets — they don't continue growing outward.

### SwiftUI API

```swift
// iOS 14+
.ignoresSafeArea(_ regions: SafeAreaRegions = .all, edges: Edge.Set = .all)
// SafeAreaRegions: .container, .keyboard, .all

// iOS 15+
.safeAreaInset(edge: .bottom) { ActionBar() }        // shrinks safe area

// iOS 17+
.safeAreaPadding(.horizontal, 20)                    // extends SA without content

// iOS 26+
.safeAreaBar(edge: .bottom) { ActionBar() }          // like safeAreaInset + Liquid Glass blur
```

```swift
struct ArticleView: View {
    var body: some View {
        ScrollView { Text(longBody) }
            .safeAreaInset(edge: .bottom) {
                HStack { Button("Like"){}; Button("Share"){} }
                    .padding().background(.thinMaterial)
            }
            .background {
                LinearGradient(colors: [.blue,.purple], startPoint: .top, endPoint: .bottom)
                    .ignoresSafeArea()               // background only — NEVER the whole view
            }
    }
}
```

### Keyboard safe area — the biggest UIKit/SwiftUI divergence

**SwiftUI**: the keyboard is a safe-area region. `TextField` activation shrinks `.container` height so content slides up automatically. Opt out with `.ignoresSafeArea(.keyboard, edges: .bottom)` for fixed backgrounds. Community gotcha: opt-out only works when the content has compressible vertical space; wrap in `ScrollView` if it doesn't.

**UIKit**: no automatic avoidance. Observe `UIResponder.keyboardWillChangeFrameNotification`, convert the frame, and adjust `additionalSafeAreaInsets.bottom`:

```swift
NotificationCenter.default.addObserver(
    forName: UIResponder.keyboardWillChangeFrameNotification,
    object: nil, queue: .main
) { [weak self] note in
    guard let self,
          let end = note.userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? CGRect
    else { return }
    let local = view.convert(end, from: nil)
    let overlap = max(0, view.bounds.maxY - local.minY)
    additionalSafeAreaInsets.bottom = overlap
}
```

### iOS 26 / Liquid Glass changes

Tab bars and toolbars are **lifted into Liquid Glass** and float above content, with the new **scroll-edge effect** blurring content beneath them. Two new APIs:

- **`safeAreaBar(edge:)`** (SwiftUI) — equivalent to `safeAreaInset` but applies automatic Liquid Glass scroll-edge blur. As of Xcode 26 beta 2, developers reported behavior identical to `safeAreaInset` (FB18350439) — verify in the current SDK.
- **`scrollEdgeEffectStyle(.soft | .hard, for:)`** — controls the edge blur.
- **`UIBackgroundExtensionView`** (UIKit) — mirrors and blurs content behind sidebars/tab bars so artwork flows behind glass (**WWDC 2025 · Session 284 "Build a UIKit app with the new design"**).

**Known iOS 26 regression** (FB19664903, Aug 2025): `UIToolbar` pinned to `safeAreaLayoutGuide.bottomAnchor` no longer extends its background behind the home indicator as it did on iOS 18 — a white gap appears. Workaround: pin the toolbar's container to `view.bottomAnchor` and pin the toolbar to that container's safe-area bottom.

### Anti-patterns

Do not apply `.ignoresSafeArea()` to outermost containers — it clips tappable UI under the notch. Apply it only to the background inside a `ZStack`. Do not read `view.safeAreaInsets` in `viewDidLoad` / `viewWillAppear` — it's `.zero` until the view is in a window; use `viewSafeAreaInsetsDidChange` or `viewDidLayoutSubviews` and prefer `window.safeAreaInsets` for stable values.

---

## 2. Layout margins (UIKit) and their SwiftUI analogs

`directionalLayoutMargins` defines the internal padding a view prefers around its content. Auto Layout constraints to `layoutMarginsGuide` — and stack views with `isLayoutMarginsRelativeArrangement = true` — inherit this padding. It is distinct from safe areas: the safe area describes what is obscured; margins describe aesthetic content inset.

### System defaults

| Context | `directionalLayoutMargins` |
|---|---|
| Non-root `UIView` | (8, 8, 8, 8) |
| VC root view, compact width (iPhone) | top 0, leading **16**, bottom 0, trailing **16** |
| VC root view, regular width (iPad) | top 0, leading **20**, bottom 0, trailing **20** |
| `UITableViewCell.contentView` | (8, 15/16, 8, 15/16) |

**`systemMinimumLayoutMargins`** is the read-only floor on a VC root view (16 pt iPhone, 20 pt iPad). With `viewRespectsSystemMinimumLayoutMargins = true` (default), assigning smaller values is silently clamped up.

```swift
final class FormVC: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        viewRespectsSystemMinimumLayoutMargins = false
        view.directionalLayoutMargins =
            NSDirectionalEdgeInsets(top: 12, leading: 8, bottom: 12, trailing: 8)

        let card = UIView()
        card.preservesSuperviewLayoutMargins = true          // inherit parent margins
        card.directionalLayoutMargins =
            NSDirectionalEdgeInsets(top: 16, leading: 16, bottom: 16, trailing: 16)

        let stack = UIStackView()
        stack.axis = .vertical
        stack.isLayoutMarginsRelativeArrangement = true
        stack.directionalLayoutMargins = card.directionalLayoutMargins
    }
}
```

### `preservesSuperviewLayoutMargins`

Default `false`. When `true`, if the view overlaps its superview's margin region, its own effective margins are at least the superview's. Common pattern for consistent gutters through a hierarchy:

```swift
tableView.preservesSuperviewLayoutMargins = true
tableView.directionalLayoutMargins = .zero
cell.contentView.preservesSuperviewLayoutMargins = true
```

### Guide comparison

| Guide | Purpose | Responds to |
|---|---|---|
| `safeAreaLayoutGuide` | Avoid hardware/system obscuration | bars, notch, home indicator, `additionalSafeAreaInsets` |
| `layoutMarginsGuide` | Aesthetic gutter inside the safe area | `directionalLayoutMargins` (+ safe area when `insetsLayoutMarginsFromSafeArea = true`) |
| `readableContentGuide` | Comfortable line length for long-form text | margins + Dynamic Type size |

### SwiftUI equivalents (limited)

SwiftUI has **no direct layout-margin API**. The closest approximations:

- `.padding()` with no argument uses system spacing (~16 pt iPhone, ~20 pt iPad).
- `.listRowInsets` for `List` cells.
- Community packages like `tgrapperon/swiftui-layout-guides` expose UIKit's `layoutMarginsGuide` and `readableContentGuide` via environment keys.

### Gotchas

Always prefer `directionalLayoutMargins` over `layoutMargins` (RTL correctness). Setting `viewRespectsSystemMinimumLayoutMargins = false` without also setting margins leaves you at `(0,0,0,0)`. Note: `UITableView.cellLayoutMarginsFollowReadableWidth` default **changed from `true` (iOS 9–11) to `false` in iOS 12** — many older tutorials are wrong.

---

## 3. The readable content guide

`UIView.readableContentGuide` (iOS 9+, **WWDC 2015 · Session 205**) marks the sub-region where long-form text is comfortable to read — roughly **45–75 characters per line**.

### Empirical widths (community-measured; Apple docs do not specify exact values)

| Container width (pt) | `readableContentGuide` width | Inset/side |
|---|---|---|
| iPhone portrait (375–430) | ≈ container minus margins (~360) | 16–20 |
| iPad 10.9″ portrait (820) | **672 pt** | ~74 |
| iPad Pro 11″ landscape (1194) | 672 pt | ~261 |
| iPad Pro 12.9″/13″ landscape (1366) | 672 pt | ~347 |
| iPad Pro 12.9″ at max accessibility Dynamic Type | up to ~896 pt | scales up |

At default Dynamic Type (Large), the target is **~672 pt**. At accessibility sizes the guide widens to accommodate larger glyphs. Apple documentation is ambiguous on the exact formula — developer-community measurements (Use Your Loaf, Manasa M P) establish the figure with minor variance (664 vs 672) depending on test device.

### UIKit

```swift
let rc = view.readableContentGuide
body.font = .preferredFont(forTextStyle: .body)
body.adjustsFontForContentSizeCategory = true

NSLayoutConstraint.activate([
    body.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
    body.leadingAnchor.constraint(equalTo: rc.leadingAnchor),
    body.trailingAnchor.constraint(equalTo: rc.trailingAnchor)
])

// For long-form table rows
tableView.cellLayoutMarginsFollowReadableWidth = true  // iOS 12+ default is false
```

In Interface Builder, Size Inspector → **Follow Readable Width**. The checkbox is ineffective if leading/trailing constraints to the root view already exist — you must constrain to the guide.

### SwiftUI: no native equivalent

Apple has not shipped a SwiftUI readable-content modifier in iOS 18 or iOS 26. Community approaches:

```swift
// Pragmatic (doesn't adapt to Dynamic Type)
extension View {
    func readableWidth() -> some View {
        frame(maxWidth: 672).frame(maxWidth: .infinity)
    }
}

// UIKit-bridged (adapts correctly)
struct ReadableContentWidth: ViewModifier {
    private let probe = UIViewController()
    func body(content: Content) -> some View {
        content.frame(maxWidth: measured()).frame(maxWidth: .infinity)
    }
    private func measured() -> CGFloat {
        probe.view.frame = UIScreen.main.bounds
        return probe.view.readableContentGuide.layoutFrame.width
    }
}
```

Available community packages: `yazio/ReadabilityModifier`, `tgrapperon/swiftui-layout-guides`, `danielctull-playground/ReadableContent`. All are workarounds that bridge to UIKit. iOS 26 SDK did **not** add a native replacement.

**When to use**: article bodies, long descriptions, release notes, "About" screens, form prose. **When not to use**: toolbars, segmented controls, photo grids, full-bleed hero imagery. Never hard-code 672 — Slide Over, iPadOS 26 windows, and accessibility sizes shift the value substantially.

---

## 4. Size classes

`UIUserInterfaceSizeClass` exposes `.compact`, `.regular`, `.unspecified`. Two independent traits — `horizontalSizeClass` and `verticalSizeClass` — describe the **current window/container**, not the device. Two devices of identical hardware can yield different size classes when one is multitasking.

### Complete size-class matrix

| Device / configuration | Horizontal | Vertical |
|---|---|---|
| iPhone SE / mini portrait | compact | regular |
| iPhone SE / mini landscape | compact | compact |
| iPhone standard portrait | compact | regular |
| iPhone standard landscape | compact | compact |
| iPhone Plus / Pro Max portrait | compact | regular |
| **iPhone Plus / Pro Max landscape** | **regular** | **compact** ⚠ |
| iPad (any) full screen | regular | regular |
| iPad non-12.9″ Split 50/50 | **compact** | regular |
| iPad non-12.9″ Split 2/3 primary | regular | regular |
| iPad non-12.9″ Split 1/3 secondary | compact | regular |
| **iPad Pro 12.9″/13″ Split 50/50** | **regular** (both!) | regular |
| iPad Slide Over (iOS ≤18) | compact | regular |
| iPadOS 26 freeform window — narrow | compact | depends on height |

Rules: iPhone's *longest* dimension is regular on Plus/Max, compact otherwise; iPhone landscape always has `vC`; vertical is effectively always regular on iPad.

### Size-class grid

```
                 Horizontal
              Compact        Regular
          ┌───────────────┬───────────────┐
  V    R  │ iPhone port.  │ iPad full     │
  e    e  │ iPad wC split │ iPad 12.9″    │
  r    g  │ Slide Over    │ 50/50 split   │
  t    u  │ narrow iPadOS │ iPad 2/3 pane │
  i    l  │ 26 windows    │               │
  c    a  │               │               │
  a    r  │               │               │
  l       ├───────────────┼───────────────┤
       C  │ iPhone non-   │ iPhone Plus / │
       o  │ Plus landscape│ Pro Max       │
       m  │               │ landscape     │
       p  │               │               │
       a  │               │               │
       c  │               │               │
       t  │               │               │
          └───────────────┴───────────────┘
```

### UIKit (iOS 17+ trait registration)

iOS 17 deprecated `traitCollectionDidChange(_:)` in favor of `registerForTraitChanges` (**WWDC 2023 · Session 10057 "Unleash the UIKit trait system"**):

```swift
override func viewDidLoad() {
    super.viewDidLoad()
    registerForTraitChanges([UITraitHorizontalSizeClass.self, UITraitVerticalSizeClass.self]) {
        (self: Self, previousTraitCollection: UITraitCollection) in
        self.updateLayout()
    }
    updateLayout()  // seed; no guaranteed first-layout callback
}
```

### SwiftUI

```swift
struct ContentView: View {
    @Environment(\.horizontalSizeClass) private var hSize
    var body: some View {
        if hSize == .regular { WideLayout() } else { NarrowLayout() }
    }
}
```

In SwiftUI the type is `UserInterfaceSizeClass?` (optional), not the UIKit enum.

### Decision tree — size class vs ViewThatFits vs GeometryReader

```
Is the decision semantic (phone-shape vs iPad-shape)?
├── YES → horizontalSizeClass / verticalSizeClass
│         (sidebars, 2-col vs stacked, NavigationSplitView)
└── NO → Does it depend on content actually fitting?
     ├── YES → ViewThatFits (iOS 16+), ordered largest → smallest
     └── NO → Do you need pixel measurements (overlays, custom layouts)?
         ├── YES → GeometryReader (sparingly)
         └── NO → Intrinsic sizing + frame modifiers
```

### Anti-patterns

Never branch on `UIDevice.current.userInterfaceIdiom == .pad` — this fails for iPad Slide Over, iPad 1/3 split, iPadOS 26 windowed apps, and Mac Catalyst. Never key layout off `UIScreen.main.bounds` (screen ≠ window). Never use `GeometryReader` to infer "am I on iPad" — you'll miss multitasking cases and reimplement what size classes already give you. Never check `UIDevice.current.orientation.isLandscape` — device orientation ≠ interface orientation ≠ window size.

### Accessibility

When the user selects an accessibility Dynamic Type size, UIKit may promote layouts as if width were more constrained. Several system components re-flow. Combine size-class checks with `dynamicTypeSize.isAccessibilitySize`, or use `ViewThatFits`, which handles both automatically.

---

## 5. SwiftUI layout system

SwiftUI's layout is a **three-step negotiation**: the parent proposes a size (`ProposedViewSize`), the child returns its own size via `sizeThatFits(proposal:)`, and the parent places the child. Children choose their own size — parents cannot force sizes except by inserting an intermediate `frame`. Always respect layout direction with `.leading`/`.trailing` instead of `.left`/`.right`.

### Primitives at a glance

**`Spacer`** claims all available space on the containing stack's major axis. Outside a stack it expands both axes. `Spacer(minLength: 24)` guarantees ≥ 24 pt but grows to fill.

**`frame` — fixed vs flexible.** `frame(width:height:)` forces an exact size. `frame(minWidth:idealWidth:maxWidth:...)` is flexible. The canonical "fill the row" idiom is `frame(maxWidth: .infinity, alignment: .leading)`. The alignment parameter places the original content *within* the new frame — it does not align the frame in its parent.

**`.fixedSize()`** disables flexibility. The classic "let me wrap vertically without being squeezed" is `fixedSize(horizontal: false, vertical: true)`.

**`.padding()`** with no argument is adaptive (~16 pt iPhone, ~20 pt iPad) and preferred over hardcoded 16 for platform correctness.

### GeometryReader — why it's overused

```swift
GeometryReader { proxy in
    Rectangle().frame(width: proxy.size.width * 0.5)
}
```

Issues: it greedily accepts all proposed space (like `Spacer`), collapsing intrinsic sizes of children; it doesn't participate in parent sizing; in scroll views it can trigger re-renders every frame. Prefer (in order): `.frame(maxWidth: .infinity)`, `.containerRelativeFrame()` (iOS 17+), `.onGeometryChange()` (iOS 18, back-deployed to iOS 16), `matchedGeometryEffect`, custom `Layout`.

### onGeometryChange — iOS 18, back-deployed to iOS 16

Observes geometry without becoming a greedy container:

```swift
.onGeometryChange(for: CGSize.self, of: \.size) { newSize in
    size = newSize
}
// Or with old+new values
.onGeometryChange(for: CGSize.self) { $0.size } action: { old, new in
    print("resized \(old) → \(new)")
}
```

### containerRelativeFrame — iOS 17+

Replaces most GeometryReader-for-sizing cases:

```swift
// Full-width paging cards
ScrollView(.horizontal) {
    LazyHStack(spacing: 0) {
        ForEach(items) { item in
            CardView(item: item).containerRelativeFrame(.horizontal)
        }
    }
}
.scrollTargetBehavior(.paging)

// 4-column grid, each card spans 3
Rectangle().containerRelativeFrame(.horizontal, count: 4, span: 3, spacing: 10)
```

### ViewThatFits — iOS 16+

Tries candidate subviews in order, renders the first whose ideal size fits:

```swift
ViewThatFits(in: .horizontal) {
    HStack { Label("Add to Cart", systemImage: "cart"); Spacer(); Text("$49.99") }
    VStack(alignment: .leading) { Label("Add to Cart", systemImage: "cart"); Text("$49.99") }
    Label("Add", systemImage: "cart")  // icon-only fallback
}
```

This is an accessibility superpower: SwiftUI picks whichever variant fits Dynamic Type and localization without manual measurement.

### Layout protocol — iOS 16+ (WWDC 2022 · Session 10056)

```swift
struct RadialLayout: Layout {
    struct Cache { var sizes: [CGSize] = [] }
    func makeCache(subviews: Subviews) -> Cache {
        Cache(sizes: subviews.map { $0.sizeThatFits(.unspecified) })
    }
    func updateCache(_ cache: inout Cache, subviews: Subviews) {
        cache.sizes = subviews.map { $0.sizeThatFits(.unspecified) }
    }
    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout Cache) -> CGSize {
        proposal.replacingUnspecifiedDimensions()
    }
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize,
                       subviews: Subviews, cache: inout Cache) {
        let radius = min(bounds.width, bounds.height) / 2
        let step = (2 * .pi) / Double(subviews.count)
        let center = CGPoint(x: bounds.midX, y: bounds.midY)
        for (i, sv) in subviews.enumerated() {
            let angle = step * Double(i) - .pi / 2
            let p = CGPoint(x: center.x + cos(angle) * (radius - cache.sizes[i].width / 2),
                            y: center.y + sin(angle) * (radius - cache.sizes[i].height / 2))
            sv.place(at: p, anchor: .center, proposal: .unspecified)
        }
    }
}
```

### AnyLayout — animated layout swaps

```swift
struct AdaptiveStack<Content: View>: View {
    @Environment(\.horizontalSizeClass) var size
    @Environment(\.dynamicTypeSize) var typeSize
    @ViewBuilder let content: () -> Content
    var body: some View {
        let useHorizontal = size == .regular && !typeSize.isAccessibilitySize
        let layout: AnyLayout = useHorizontal
            ? AnyLayout(HStackLayout(spacing: 16))
            : AnyLayout(VStackLayout(alignment: .leading, spacing: 12))
        layout { content() }
            .animation(.default, value: useHorizontal)
    }
}
```

`AnyLayout` preserves view identity across layout changes — unlike `if/else` branches, which rebuild the tree and lose state.

### Grid / GridRow — iOS 16+

Non-lazy 2-D layout aligning columns across rows (spreadsheet feel). Use `Grid` for layout; use `LazyVGrid` for data.

```swift
Grid(alignment: .leading, horizontalSpacing: 12, verticalSpacing: 8) {
    GridRow { Text("Name").bold(); Text("Score").bold().gridColumnAlignment(.trailing) }
    Divider().gridCellColumns(2)
    GridRow { Text("Ada");   Text("42") }
    GridRow { Text("Grace"); Text("108") }
}
```

### Spacer vs frame(maxWidth:.infinity) vs padding

| Goal | Spacer | `.frame(maxWidth:.infinity)` | `.padding()` |
|---|---|---|---|
| Push sibling to trailing edge | ✅ idiomatic | ⚠ creates two frames | ❌ wrong tool |
| Make item fill row for tap target | ⚠ requires gymnastics | ✅ idiomatic | ❌ doesn't expand |
| Consistent gutters in a card | ❌ awkward | ❌ not semantic | ✅ correct |
| Distribute N items evenly | ✅ interleave `Spacer()`s | ⚠ equal frames each | ❌ no |
| Reserve minimum gap that may grow | ✅ `Spacer(minLength:)` | ⚠ two frames | ❌ no |

Semantic mantra: `Spacer` = "give me whatever's left along the axis"; `frame(maxWidth:.infinity)` = "this view itself should occupy the row"; `padding` = "inset my contents".

---

## 6. Spacing values — the 8 pt grid

Apple's HIG has informally followed an **8-point grid** since the original iPhone: even numbers scale cleanly at @1x/@2x/@3x, humans perceive multiples of 8 as rhythmic, and the grid matches SF font cap heights and SF Symbols sizing.

**Standard scale:** 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64. Use 4 pt for tight glyph-to-text spacing, 2 pt sparingly for micro-adjustments, 16–24 pt for section gutters, 32+ pt for page-level groupings.

```
┌────────────────────── 24 ─────────────────────┐
│  ┌─────────────── card ───────────────────┐   │
│  │ Title                        │ 16      │   │
│  │ ──────── 8 ─────────                    │   │
│  │ Subtitle line                │ 8       │   │
│  │ ─────── 16 ──────────                   │   │
│  │ ┌ icon 24×24 ┐  8  Body text            │   │
│  │ └────────────┘                          │   │
│  └───── 16 padding all sides ──────────────┘   │
└────────────────────────────────────────────────┘
```

**SwiftUI defaults**: `HStack()`/`VStack()` with no `spacing:` use a context-dependent adaptive default typically around 8 pt — but larger between text baselines, to respect font line-spacing. `nil` spacing ≠ 0; it means "system default". There is **no `.spacing()` modifier** — spacing is configured at the container: `HStack(spacing: 16)`, `LazyVGrid(columns:, spacing:)`, `Grid(horizontalSpacing:, verticalSpacing:)`.

`ViewSpacing` (advanced) is the mechanism behind adaptive spacing; custom `Layout`s receive it via `subviews[i].spacing`.

**Baseline alignment** — for rows mixing text sizes:

```swift
HStack(alignment: .firstTextBaseline) {
    Text("42").font(.largeTitle)
    Text("points").font(.body).foregroundStyle(.secondary)
}
```

---

## 7. Adaptive layouts — one layout, all sizes

The iOS world runs layouts across a continuum: iPhone portrait 375–430 pt, iPhone landscape compact-vertical, iPad split halves and thirds, iPadOS 26 freeform windows of any size. Strategies:

**Branch on size class** for coarse structural decisions (sidebar vs stack, 2-col vs 1-col). Use `AnyLayout` with `HStackLayout`/`VStackLayout` for animated transitions that preserve identity. **Use `ViewThatFits`** for content-driven fallbacks (full toolbar → compact toolbar → icon-only), which automatically handle Dynamic Type. **Use `GeometryReader`** only when you truly need geometry in the same view — never for "am I wide?" decisions.

### NavigationSplitView vs NavigationStack

`NavigationStack` — strictly hierarchical push/pop navigation; primary on iPhone. `NavigationSplitView` — master/detail or 3-pane source-list UIs; auto-collapses in compact horizontal size class (behaves like `NavigationStack`). Don't nest split inside a stack; do put a `NavigationStack` inside each column for intra-column drill-down.

```swift
struct ThreeColumn: View {
    @State private var folder: Folder?
    @State private var message: Message?
    @State private var columnVisibility: NavigationSplitViewVisibility = .all
    @State private var preferredCompact = NavigationSplitViewColumn.detail

    var body: some View {
        NavigationSplitView(columnVisibility: $columnVisibility,
                            preferredCompactColumn: $preferredCompact) {
            List(folders, selection: $folder) { Text($0.name).tag($0) }
                .navigationSplitViewColumnWidth(min: 180, ideal: 220)
        } content: {
            if let folder {
                List(folder.messages, selection: $message) { Text($0.subject).tag($0) }
            } else { Text("Choose a folder") }
        } detail: {
            if let message { MessageView(message: message) } else { Text("No message selected") }
        }
        .navigationSplitViewStyle(.balanced)
    }
}
```

UIKit equivalent — `UISplitViewController` with `.tripleColumn` style and `.compact` view controller for collapsed iPhone UI:

```swift
let split = UISplitViewController(style: .tripleColumn)
split.preferredDisplayMode = .twoBesideSecondary
split.preferredSplitBehavior = .tile
split.setViewController(SidebarVC(),     for: .primary)
split.setViewController(SupplementVC(),  for: .supplementary)
split.setViewController(DetailVC(),      for: .secondary)
split.setViewController(CompactRootVC(), for: .compact)
```

When the trait collection becomes horizontally compact, the split controller automatically swaps to the `.compact` view controller.

---

## 8. Window sizing — iOS 26's arbitrary iPad windows

At **WWDC 2025 · Session 208 "Elevate the design of your iPad app"** and **Session 282 / "Make your UIKit app more flexible"**, Apple introduced the largest multitasking overhaul since iOS 9. Previously, iPad windows were constrained to fixed fractions (1/3, 1/2, 2/3) via Split View/Slide Over, or to Stage Manager's limited resize range. In iPadOS 26, apps resize to **essentially any size** via a corner grab handle, can be moved freely, tiled into halves/thirds/quadrants, minimized, and closed — with Mac-style red/yellow/green "traffic-light" controls and a per-app menu bar revealed by swiping from the top edge.

**Split View and Slide Over have been removed** as distinct modes. The system has three user-selectable modes: Full Screen Apps, Windowed Apps (new default on supported hardware), and Stage Manager. Stage Manager is now available on every iPadOS 26-compatible iPad (3rd-gen iPad Air+, 5th-gen iPad mini+, 8th-gen iPad+); external-display Stage Manager still requires M1+.

### Key iOS 18 → iPadOS 26 differences

| Behavior | iOS 18 | iPadOS 26 |
|---|---|---|
| Default multitasking | Full screen + Split View + Slide Over | Full Screen / Windowed Apps / Stage Manager |
| Window sizes | Fixed fractions | Arbitrary, continuous + tiling presets |
| Window chrome | None | Traffic-light controls + swipe-down menu bar |
| `UIRequiresFullScreen` | Honored | **Deprecated**; will be ignored |
| UIScene lifecycle | Recommended | Mandatory in the release after iOS 26 when building with latest SDK |
| `UISceneSizeRestrictions` | `nil` outside Stage Manager | Honored as best-effort on iPad |
| Auto-scaling for new iPads | Applied | Not applied when built against iOS 26 SDK |
| Visual design | Pre-Liquid Glass | Liquid Glass chrome |

### SwiftUI

```swift
@main
struct DocsApp: App {
    var body: some Scene {
        WindowGroup("Document", for: Document.ID.self) { $id in
            DocumentView(id: id)
        }
        .defaultSize(width: 1100, height: 780)
        .windowResizability(.contentSize)          // honor min and max from content

        WindowGroup("Inspector", id: "inspector") {
            InspectorView()
                .frame(minWidth: 280, idealWidth: 320, maxWidth: 480,
                       minHeight: 360, idealHeight: 600)
        }
        .windowResizability(.contentMinSize)       // only min enforced
    }
}

struct Toolbar: View {
    @Environment(\.openWindow) private var openWindow
    var body: some View {
        Button("Open Inspector") { openWindow(id: "inspector") }
        Button("Open Document")  { openWindow(value: Document.ID(UUID())) }
    }
}
```

`.contentSize` limits the window to both min and max of content; `.contentMinSize` only enforces the minimum; `.automatic` (the default) lets users resize freely — typically what you want on iPad.

### UIKit

```swift
final class WindowSceneDelegate: UIResponder, UIWindowSceneDelegate {
    func scene(_ scene: UIScene, willConnectTo session: UISceneSession,
               options: UIScene.ConnectionOptions) {
        guard let ws = scene as? UIWindowScene else { return }

        ws.sizeRestrictions?.minimumSize = CGSize(width: 480, height: 640)
        ws.sizeRestrictions?.maximumSize = CGSize(width: 2000, height: 2000)
        ws.sizeRestrictions?.allowsFullScreen = true

        let window = UIWindow(windowScene: ws)
        window.rootViewController = RootVC()
        window.makeKeyAndVisible()
    }

    // Smooth interactive resize: avoid expensive work per-frame
    func windowScene(_ ws: UIWindowScene,
                     didUpdate prev: UICoordinateSpace,
                     interfaceOrientation: UIInterfaceOrientation,
                     traitCollection: UITraitCollection) {
        if ws.isInteractivelyResizing { return }
        rebuildExpensiveAssets(for: ws.coordinateSpace.bounds.size)
    }
}
```

### Info.plist (recommended iPadOS 26 baseline)

```xml
<key>UIApplicationSceneManifest</key>
<dict>
    <key>UIApplicationSupportsMultipleScenes</key><true/>
    <key>UISceneConfigurations</key>
    <dict>
        <key>UIWindowSceneSessionRoleApplication</key>
        <array>
            <dict>
                <key>UISceneConfigurationName</key><string>Default</string>
                <key>UISceneDelegateClassName</key>
                <string>$(PRODUCT_MODULE_NAME).WindowSceneDelegate</string>
            </dict>
        </array>
    </dict>
</dict>
<!-- DO NOT SET: deprecated, ignored in a future release -->
<!-- <key>UIRequiresFullScreen</key><true/> -->
<key>UISupportedInterfaceOrientations~ipad</key>
<array>
    <string>UIInterfaceOrientationPortrait</string>
    <string>UIInterfaceOrientationPortraitUpsideDown</string>
    <string>UIInterfaceOrientationLandscapeLeft</string>
    <string>UIInterfaceOrientationLandscapeRight</string>
</array>
```

### iPadOS 26 layout modes

```
 FULL SCREEN            WINDOWED APPS (new)       TILED HALVES
 +------------+         +------------------+      +------+------+
 |            |         |  ┌─────────┐     |      |      |      |
 |   App A    |         |  │  App A  │     |      |   A  |   B  |
 |            |         |  └─────────┘     |      |      |      |
 |            |         |      ┌──────┐    |      |      |      |
 |            |         |      │  B   │    |      |      |      |
 +------------+         +------+──────┘----+      +------+------+

 TILED QUADRANTS        STAGE MANAGER
 +------+------+        +--+--------------+
 |  A   |  B   |        |R |  ┌────────┐  |
 +------+------+        |ec|  │ Center │  |
 |  C   |  D   |        |en|  │ Stage  │  |
 +------+------+        |ts|  └────────┘  |
                        +--+--------------+
```

### Multitasking mode reference

| Mode | Size class (typical 11–13″ iPad) |
|---|---|
| Full Screen | Regular × Regular |
| Windowed (large) | Regular × Regular |
| Windowed (narrow window <~500 pt) | Compact width, height-dependent |
| Tiled halves | Typically Regular until <~500 pt |
| Stage Manager center (small) | Compact × Regular |
| External display windows | Regular × Regular |

Size classes do not map 1:1 to physical sizes — they reflect the **window**, not the device. Under arbitrary resizing, expect abrupt Compact/Regular transitions as the user drags.

### Migration checklist (iOS 18 → iPadOS 26)

Remove `UIRequiresFullScreen`. Declare all four iPad orientations. Adopt the UIScene lifecycle now (Apple TN3187). Set a sensible `sizeRestrictions.minimumSize` — e.g., 480×640. Purge `UIScreen.main.bounds`, `UIDevice` idiom branching, and hardcoded 1/3-1/2-2/3 layout code. Rebuild chrome for Liquid Glass (rebuilding with Xcode 26 gets most of it automatically). Add a menu bar via SwiftUI `.commands { }` or UIKit `UIMenuBuilder`. Test interactive resize using the iPadOS 26 simulator's grab handle. Re-audit accessibility at extreme window sizes.

### Confirmed vs speculative (April 2026)

Apple has confirmed arbitrary window resizing; Split View/Slide Over removal; Stage Manager expansion; `UIRequiresFullScreen` deprecation; `.windowResizability(.contentSize / .contentMinSize / .automatic)`; Liquid Glass on window chrome; the new `splitViewControllerLayoutEnvironment` trait; `isInteractivelyResizing`. The "up to 8 windows on external display" figure is widely reported in press but phrased by Apple as "more windows at once, with practical limits set by device." No public API was documented for **enforcing window aspect ratios** on iPadOS 26 — developers wanting fixed-ratio content should letterbox internally.

---

## 9. Scroll behaviors

### ScrollView vs List — the performance divide

`List` is backed by `UICollectionView` (iOS 16+) and recycles cells; memory is bounded even with 100K items. `ScrollView { VStack { … } }` instantiates every child view eagerly — huge layout cost and memory for large data. `ScrollView { LazyVStack { … } }` creates views on demand but doesn't recycle — once created, kept.

| Container | Lazy | Recycle | Memory (10K rows) | Best for |
|---|---|---|---|---|
| `ScrollView + VStack` | ❌ | ❌ | Very high | <30 items |
| `ScrollView + LazyVStack` | ✅ | ❌ | Grows | Custom feeds, carousels |
| `List` | ✅ | ✅ | Bounded | Long uniform lists |
| `UICollectionView` | ✅ | ✅ | Bounded | Complex grids, compositional layouts |

Decision:

```
Homogeneous rows with system chrome?
├── YES → List (free swipe actions, separators, selection, search)
│         .plain for pinned headers, .insetGrouped for settings
└── NO → ScrollView
     ├── >~30 views or unknown length? → LazyVStack/LazyHStack
     └── Small fixed content?          → Plain VStack/HStack inside ScrollView
```

### Content insets

UIKit:

```swift
scrollView.contentInsetAdjustmentBehavior = .automatic  // default
scrollView.contentInset = UIEdgeInsets(top: 16, …)
print(scrollView.adjustedContentInset)  // system + developer combined
```

SwiftUI (iOS 17+):

```swift
ScrollView { … }
    .contentMargins(.horizontal, 20, for: .scrollContent)
    .contentMargins(.vertical, 10, for: .scrollIndicators)
    .scrollDismissesKeyboard(.interactively)
    .safeAreaPadding(.top, 44)
```

### Scroll-edge effects — iOS 26 Liquid Glass

Under Liquid Glass, bars float above content. To keep them legible, scroll views render a **scroll-edge effect**: the region where content slides under a glass element dissolves/blurs. The effect is automatic for `ScrollView`, `List`, `Form` when content passes under a nav bar, tab bar, toolbar, or `safeAreaBar`.

Two styles: `.soft` — progressive fade/blur (default under translucent bars); `.hard` — crisp dividing line. Don't stack soft + hard; don't use either when no floating UI is present.

**SwiftUI:**

```swift
NavigationStack {
    List(1..<101, id: \.self) { Text("Row \($0)") }
        .scrollEdgeEffectStyle(.hard, for: .top)
        .scrollEdgeEffectStyle(.soft, for: .bottom)
        // .scrollEdgeEffectStyle(nil, for: .all)   // opt out
}
```

`ScrollEdgeEffectStyle`: `.automatic`, `.hard`, `.soft`.

**UIKit** (iOS 26):

```swift
scrollView.topEdgeEffect.style    = .soft
scrollView.bottomEdgeEffect.style = .hard

// Mark a floating header so scroll view fades under it
let interaction = UIScrollEdgeElementContainerInteraction()
interaction.scrollView = collectionView
interaction.edge = .top
floatingHeaderView.addInteraction(interaction)
```

Known beta issues (verify on shipping SDK): `UIScrollEdgeElementContainerInteraction` on `WKWebView` was unreliable in late iOS 26 betas (Apple Forums 795816); header/cell z-order in `UITableView` can render oddly (thread 799254).

### Pinned headers

**SwiftUI:**

```swift
ScrollView {
    LazyVStack(spacing: 0, pinnedViews: [.sectionHeaders, .sectionFooters]) {
        ForEach(sections) { section in
            Section {
                ForEach(section.items) { ItemRow($0) }
            } header: {
                Text(section.title).frame(maxWidth: .infinity).background(.bar)
            }
        }
    }
}
```

`List(.plain)` pins section headers automatically.

**UIKit compositional layout:**

```swift
let header = NSCollectionLayoutBoundarySupplementaryItem(
    layoutSize: .init(widthDimension: .fractionalWidth(1),
                      heightDimension: .estimated(44)),
    elementKind: UICollectionView.elementKindSectionHeader,
    alignment: .top)
header.pinToVisibleBounds = true
section.boundarySupplementaryItems = [header]
```

`UITableView.Style.plain` pins by default; `.grouped` and `.insetGrouped` do not.

### iOS 17+ scroll APIs (WWDC 2023 · Session 10159 "Beyond scroll views")

```swift
ScrollView(.horizontal) {
    LazyHStack(spacing: 16) {
        ForEach(cards) { CardView($0).containerRelativeFrame(.horizontal) }
    }
    .scrollTargetLayout()                // marks children as snap targets
}
.scrollTargetBehavior(.viewAligned)      // or .paging
.contentMargins(.horizontal, 32, for: .scrollContent)
.scrollIndicators(.hidden)
```

Custom snap behavior:

```swift
struct SnapToThird: ScrollTargetBehavior {
    func updateTarget(_ target: inout ScrollTarget, context: TargetContext) {
        let step = context.containerSize.width / 3
        target.rect.origin.x = (target.rect.origin.x / step).rounded() * step
    }
}
```

**Scroll position — iOS 17 id-based:**

```swift
@State private var topID: Int?
ScrollView {
    LazyVStack { ForEach(0..<1000, id: \.self) { Text("\($0)").id($0) } }
        .scrollTargetLayout()
}
.scrollPosition(id: $topID)
Button("Jump to 500") { topID = 500 }
```

**Scroll position — iOS 18 `ScrollPosition` type:**

```swift
@State private var position = ScrollPosition(edge: .top)
ScrollView { … }.scrollPosition($position)
Button("Top")       { position.scrollTo(edge: .top) }
Button("To y=500")  { position.scrollTo(point: CGPoint(x: 0, y: 500)) }
Button("To item 42"){ position.scrollTo(id: 42, anchor: .center) }
```

### iOS 18 geometry observers — replacing GeometryReader hacks

```swift
.onScrollGeometryChange(for: CGFloat.self) { geo in
    geo.contentOffset.y + geo.contentInsets.top
} action: { _, new in scrollY = new }

.onScrollVisibilityChange(threshold: 0.5) { visible in
    if visible { analytics.log(.impressed(card.id)) }
}

.onScrollPhaseChange { old, new in
    if new == .idle { snapshotter.capture() }
}
```

### Migration — iOS 17 GeometryReader → iOS 18 onScrollGeometryChange

**Before** (coordinate-space plumbing, preference keys, duplicated updates):

```swift
ScrollView {
    LazyVStack { … }.background(GeometryReader { g in
        Color.clear.preference(key: OffsetKey.self,
                               value: g.frame(in: .named("scroll")).minY)
    })
}
.coordinateSpace(name: "scroll")
.onPreferenceChange(OffsetKey.self) { offset = $0 }
```

**After:**

```swift
ScrollView { LazyVStack { … } }
    .onScrollGeometryChange(for: CGFloat.self,
                            of: { $0.contentOffset.y },
                            action: { _, new in offset = new })
```

### API availability cheat sheet

| API | First available |
|---|---|
| `contentInsetAdjustmentBehavior` | iOS 11 |
| `List` swipe actions, styles | iOS 15 |
| `.scrollDismissesKeyboard`, `.scrollIndicators` | iOS 16 |
| `ViewThatFits`, `Layout`, `Grid`, `AnyLayout` | iOS 16 |
| `.scrollTargetBehavior`, `.scrollTargetLayout`, `.scrollPosition(id:)`, `.scrollClipDisabled`, `.scrollBounceBehavior`, `.contentMargins`, `.scrollTransition`, `containerRelativeFrame`, `.safeAreaPadding` | **iOS 17** |
| `onScrollGeometryChange`, `onScrollVisibilityChange`, `onScrollPhaseChange`, `ScrollPosition` type, `onGeometryChange` (back-deployed to iOS 16) | **iOS 18** |
| `scrollEdgeEffectStyle`, `safeAreaBar`, `UIScrollEdgeEffect`, `UIScrollEdgeElementContainerInteraction`, `UIBackgroundExtensionView`, `ConcentricRectangle`, `ToolbarSpacer`, `.glassEffect()` | **iOS 26** |

---

## 10. Anti-patterns — a consolidated list

Across all the sections above, a handful of mistakes show up repeatedly. Consolidated here as a checklist:

- **Device branching**: `UIDevice.current.userInterfaceIdiom == .pad`, `UIDevice.current.orientation.isLandscape`, or `UIScreen.main.bounds.width > 768`. All fail on iPad Slide Over, iPad 1/3 split, iPadOS 26 freeform windows, and Mac Catalyst. Use traits (`horizontalSizeClass`) or window geometry (`view.window?.windowScene?.coordinateSpace.bounds`).
- **Hardcoded safe-area values**: `34`, `44`, `59`. Dynamic Island devices are 59/62/68; iPhone 17 landscape reintroduces a 20 pt top inset. Read `safeAreaInsets` or constrain to `safeAreaLayoutGuide`.
- **Hardcoded pixel widths** for content columns: especially 672 for readable width. The guide widens with Dynamic Type and narrows in windowed modes.
- **Fixed `frame(height:)` on text**: Dynamic Type can more than double line heights at AX5. Use `minHeight:` for tap targets (≥ 44 pt per HIG). Use `@ScaledMetric` for values that should grow with type size.
- **`.font(.system(size: 17))`** — doesn't scale. Use `.font(.body)` or `.font(.system(size: 17, relativeTo: .body))`.
- **GeometryReader for everything**: to read size → use `onGeometryChange`; for fractional sizing → use `containerRelativeFrame`; for size-class decisions → use `horizontalSizeClass`; for scroll offset → use `onScrollGeometryChange`.
- **`Spacer` abuse** where `frame(maxWidth: .infinity, alignment:)` is cleaner — especially two stacked `Spacer()`s around centered content.
- **`ScrollView { VStack { … } }`** with large data — wrap in `LazyVStack`.
- **`List` inside `ScrollView`** — double scrolling, broken cell reuse.
- **`.ignoresSafeArea()` on the root** — clips tappable UI under the notch/home indicator. Apply only to backgrounds inside a `ZStack`.
- **`UIRequiresFullScreen = YES`** — deprecated on iPadOS 26; use `UISceneSizeRestrictions` for a minimum instead.
- **Expensive work during interactive resize** — check `windowScene.isInteractivelyResizing` and defer.
- **Top-left corner interactive controls on iPadOS 26** — that's where traffic lights live.
- **`UITableView.cellLayoutMarginsFollowReadableWidth = true`** from an iOS 10 tutorial — the default **flipped to `false` in iOS 12**; older advice is wrong.
- **Reading `view.safeAreaInsets` in `viewDidLoad`/`viewWillAppear`** — always `.zero` until attached to a window; use `viewSafeAreaInsetsDidChange` or read `window.safeAreaInsets`.

---

## 11. Accessibility implications — recurring themes

Accessibility is not a separate section — it intersects every topic. The recurring principles:

**Dynamic Type is not optional.** Use semantic fonts (`.body`, `.headline`) or `@ScaledMetric` for custom values. Never clip text with fixed heights; use `minHeight:` and let text grow. `UIFontMetrics.default.scaledFont(for:)` scales custom fonts. `label.adjustsFontForContentSizeCategory = true` in UIKit.

**ViewThatFits is an accessibility superpower.** Order candidates largest to smallest — when the user picks AX5, SwiftUI automatically falls back to a denser layout with no explicit Dynamic Type checks.

**Size classes interact with Dynamic Type.** Some iPhone models in landscape are *promoted to compact* when accessibility sizes are selected, to prevent truncation. Combine size-class checks with `dynamicTypeSize.isAccessibilitySize`.

**Safe area margins grow** with system bars that grow for Dynamic Type (large titles, accessibility-size nav bars). Always use guide anchors; never cache inset values.

**Readable content guide widens** with accessibility Dynamic Type (up to ~896 pt on iPad Pro). This is the one UIKit guide whose existence is primarily about accessibility.

**VoiceOver on windowed iPadOS 26** needs window titles — `WindowGroup("Document — Budget.xlsx")` instead of "Window 3".

**Reduce Motion** affects scroll-edge animations, parallax headers, `scrollTransition(.animated)`, and window-resize animations. Respect `@Environment(\.accessibilityReduceMotion)`.

**Tap targets** minimum 44×44 pt per HIG — use `frame(minHeight: 44)`.

**Liquid Glass and accessibility**: with Reduce Transparency or Increase Contrast, Liquid Glass falls back to solid materials; safe-area geometry is unchanged.

---

## 12. Conclusion — working rules for 2026

Apple's layout system in 2026 rewards developers who think **semantically**, not geometrically. The shift is clearest in three places: the complete removal of fixed iPad multitasking fractions in iPadOS 26 (forcing continuous responsive design); the rapid expansion of semantic SwiftUI APIs (`containerRelativeFrame`, `onGeometryChange`, `onScrollGeometryChange`, `ViewThatFits`, `Layout`, `AnyLayout`) that make `GeometryReader` almost always the wrong tool; and the consistent deprecation of device-identity APIs (`UIRequiresFullScreen`, idiom checks, `UIScreen.main.bounds`) in favor of trait- and scene-based reasoning.

Six working rules distill the whole reference:

1. **Read from the window and traits, not the device or screen.** Every hardcoded device check is a bug waiting for a new iPad form factor, a Slide Over, or an iPadOS 26 freeform window.
2. **Prefer semantic layout APIs over geometry.** `ViewThatFits`, `containerRelativeFrame`, `onGeometryChange`, and `Layout` cover cases that once required `GeometryReader` — with better performance and accessibility behavior.
3. **Design for a continuum, not a fixed set of widths.** iPadOS 26 turned "1/3 / 1/2 / 2/3 / full" into "anything from 480 pt to native." Branch on size class for structural decisions, and let `ViewThatFits` and intrinsic sizing handle the rest.
4. **Stick to the 8-pt grid, deviate with intent.** Use 4 pt for tight glyph spacing, 16 pt for gutters, 24+ pt for section separation. Use `@ScaledMetric` when values should scale with Dynamic Type.
5. **Accessibility is layout, not decoration.** Dynamic Type, VoiceOver rotors, Reduce Motion, and Increase Contrast are not separate concerns — they shape size classes, readable widths, safe area insets, and scroll effects. `ViewThatFits`, `minHeight`, `@ScaledMetric`, and semantic fonts are the primary tools.
6. **Adopt iOS 26 primitives where they exist, but understand the fallbacks.** Liquid Glass chrome, `scrollEdgeEffectStyle`, `safeAreaBar`, `ConcentricRectangle`, and `UIBackgroundExtensionView` are the new idioms. Rebuild against the iOS 26 SDK to get most of the visual refresh automatically; audit touch points (window controls location, toolbar spacers, safe-area-bar migration) individually.

The single mental model that ties everything together: your app's UI is a continuous function of `(ProposedViewSize, TraitCollection, SafeAreaInsets, DynamicTypeSize)`. Every piece of code in this reference — UIKit or SwiftUI — is either *reading* one of those inputs or *describing the function* in terms of them. The code that looked cleverest in 2019 (reading `UIScreen.main.bounds`, branching on `UIDevice`, stuffing a `GeometryReader` at the root) is exactly the code that breaks on iPadOS 26. The semantic APIs Apple has shipped 2022–2025 aren't new features — they're the language needed to describe UIs that work in the world Apple now ships.