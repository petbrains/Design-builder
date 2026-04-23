---
name: navigation
description: iOS navigation patterns (NavigationStack, Split, Tab, Sheet, iOS 26 tab minimize + zoom transition)
platform: ios
---

# iOS navigation patterns: a complete reference for iOS 18 and iOS 26

**Choose the right container and you have already solved 80% of your app's UX.** This reference consolidates the modern SwiftUI navigation APIs (iOS 16 baseline, iOS 18 tab redesign, iOS 26 Liquid Glass) with UIKit equivalents for legacy codebases. It is organized around one question: *given this content and this user task, which container do I reach for?*

The architectural story is stable: `NavigationStack`, `NavigationSplitView`, `TabView`, `.sheet`, `.fullScreenCover`, `.popover`. What changed in iOS 18 is **type-safe `Tab` construction** with `TabRole.search` and the `sidebarAdaptable` style. What changed in iOS 26 is **Liquid Glass**: translucent navigation surfaces, `tabBarMinimizeBehavior`, `tabViewBottomAccessory`, `ToolbarSpacer`, `navigationSubtitle`, and a refined zoom transition for morphing sheets from their source button. The structural APIs are unchanged — recompile with Xcode 26 and most of the visual refresh is automatic.

This document is long on purpose. Use the decision tree as your entry point; the per-container sections are reference material.

---

## 1. The decision tree

This is the centerpiece. Start here for every navigation decision.

```mermaid
flowchart TD
    Start([What am I presenting?]) --> Q1{Top-level peer<br/>sections of the app?<br/>e.g. Home / Search / Library}
    Q1 -- Yes --> TAB[<b>TabView</b><br/>iOS 18+: Tab{} + role:.search<br/>+ .tabViewStyle(.sidebarAdaptable)<br/>UIKit: UITabBarController + UITab]
    Q1 -- No --> Q2{Hierarchical content<br/>with 2–3 columns<br/>best on iPad/Mac?}
    Q2 -- Yes --> SPLIT[<b>NavigationSplitView</b><br/>two- or three-column<br/>UIKit: UISplitViewController<br/>.doubleColumn/.tripleColumn]
    Q2 -- No --> Q3{Drill-down into<br/>a child of current item?<br/>list → detail → sub-detail}
    Q3 -- Yes --> STACK[<b>NavigationStack</b><br/>+ .navigationDestination for: Type<br/>UIKit: UINavigationController.push]
    Q3 -- No --> Q4{Self-contained task<br/>unrelated to context?<br/>compose / settings / share / filter}
    Q4 -- Yes --> Q5{Partial height OK?<br/>user should see content<br/>behind the panel}
    Q5 -- Yes --> SHEETD[<b>.sheet + presentationDetents</b><br/>.medium / .large / .height / .fraction<br/>UIKit: UISheetPresentationController]
    Q5 -- No --> Q6{Immersive or<br/>blocking flow?<br/>video / onboarding / camera / paywall}
    Q6 -- Yes --> FULL[<b>.fullScreenCover</b><br/>REQUIRES explicit dismiss button<br/>UIKit: modalPresentationStyle = .fullScreen]
    Q6 -- No --> SHEET[<b>.sheet</b> full-height<br/>wrap content in NavigationStack<br/>for multi-step flow]
    Q4 -- No --> Q7{Contextual info<br/>anchored to a control<br/>on iPad/Mac?}
    Q7 -- Yes --> POP[<b>.popover</b><br/>iPhone: add .presentationCompactAdaptation.popover<br/>UIKit: UIPopoverPresentationController]
    Q7 -- No --> Q8{Need persistent<br/>side navigation on iPad<br/>like Mail/Notes/Files?}
    Q8 -- Yes --> SIDE[<b>Sidebar</b> = primary column of<br/>NavigationSplitView, or<br/>TabView.sidebarAdaptable, or<br/>UITabBarController.mode = .tabSidebar]
    Q8 -- No --> STACK

    classDef primary fill:#d4e7ff,stroke:#1e40af,color:#000
    classDef modal   fill:#fff4d4,stroke:#92400e,color:#000
    classDef nav     fill:#d4ffd9,stroke:#166534,color:#000
    class TAB,SIDE primary
    class SHEET,SHEETD,FULL,POP modal
    class STACK,SPLIT nav
```

### Content-to-container quick map

| Content / task | Use | Why |
|---|---|---|
| Email inbox → message → thread | `NavigationStack` (iPhone) / `NavigationSplitView` triple-column (iPad) | Clear parent-child-grandchild hierarchy |
| App-level sections (Home, Search, Library) | `TabView` with `Tab(role: .search)` | Peer destinations, equal weight |
| Compose message, new note, edit contact | `.sheet` wrapped in `NavigationStack` | Orthogonal task, Cancel/Save semantics |
| Settings screen | `.sheet` (never push onto main stack) | Unrelated to current content |
| Video playback, camera capture, scanner | `.fullScreenCover` | Immersive, no distractions |
| Onboarding / paywall | `.fullScreenCover` | Must be completed or deferred |
| Filter panel on a map | `.sheet` with `.height(120), .medium, .large` detents + `.presentationBackgroundInteraction(.enabled(upThrough: .medium))` | Bottom panel over interactive map |
| Formatting menu anchored to a button (iPad) | `.popover` | Contextual, pointed at source |
| Color picker on iPhone | `.popover` with `.presentationCompactAdaptation(.popover)` | Compact, anchored, iPad-style |
| Quick rename / micro-form | `.sheet` with `.presentationDetents([.height(220)])` | Partial height preserves context |
| Music mini-player above tab bar (iOS 26) | `.tabViewBottomAccessory { }` | Persistent accessory, glass-aware |

---

## 2. TabView: top-level navigation

TabView is the **root container for apps whose primary destinations are peer sections**. Apple's HIG is strict: *"Use a tab bar strictly for navigation. Tab bar buttons should not be used to perform actions."*

### 2.1 Limits and the "More" tab

**iPhone shows at most 5 tab items.** If you supply six or more, SwiftUI and UIKit both replace the fifth slot with a system-generated **"More"** tab listing the overflow. The HIG recommends **three to five** tabs on iPhone; a few more are acceptable on iPad. When tabs overflow into "More", any child `NavigationStack` can produce a double navigation bar (Apple Forum 764293) — if you legitimately need more than five top-level destinations, prefer `NavigationSplitView` with a sidebar.

Apple HIG explicitly prohibits hiding the tab bar during in-section navigation ("Don't hide a tab bar when people navigate to different areas in your app"), with the single exception of modal presentations.

### 2.2 The iOS 18 Tab API (WWDC24 session 10147)

The classic `.tabItem` modifier still compiles but is soft-deprecated with a Xcode warning. The new `Tab` struct provides **compile-time type safety** between tab values and the `TabView`'s selection binding — a mismatch is now a compile error.

```swift
enum AppTab: Hashable { case home, messages, settings, search }

struct RootView: View {
    @State private var selection: AppTab = .home
    @State private var query = ""

    var body: some View {
        TabView(selection: $selection) {
            Tab("Home", systemImage: "house", value: AppTab.home) {
                HomeView()
            }
            Tab("Messages", systemImage: "message", value: AppTab.messages) {
                MessagesView()
            }
            .badge(3)                                            // Int or String

            Tab("Settings", systemImage: "gear", value: AppTab.settings) {
                SettingsView()
            }

            // TabRole.search — rendered specially (trailing edge, iOS 26 floating capsule)
            Tab(value: AppTab.search, role: .search) {
                NavigationStack { SearchView(query: $query) }
                    .searchable(text: $query)
            }
        }
    }
}
```

**Rules for `TabRole.search`:** exactly one per `TabView`; the system supplies the magnifying-glass symbol and title; placement is pinned on the trailing side of the bar on iPad and (on iOS 26) rendered as a floating Liquid Glass capsule that expands into a search field on tap.

### 2.3 Sidebar adaptation and sections

`.tabViewStyle(.sidebarAdaptable)` makes the same `Tab` declarations render as a bottom tab bar on iPhone, a floating top tab bar (toggleable to sidebar) on iPad, and a sidebar on macOS — from a single source of truth. `TabSection` groups tabs for sidebar presentation only; on iPhone they flatten into regular tabs.

```swift
TabView(selection: $selection) {
    Tab("Watch Now", systemImage: "play", value: .watchNow) { WatchNowView() }
    Tab("Library",   systemImage: "books.vertical", value: .library) { LibraryView() }

    TabSection("Collections") {
        Tab("Cinematic", systemImage: "list.and.film", value: .cinematic) { CinematicView() }
        Tab("Nature",    systemImage: "leaf",          value: .nature)    { NatureView() }
    }
    .sectionActions {
        Button("Add Collection", systemImage: "plus") { addCollection() }
    }

    Tab(value: .search, role: .search) { SearchView() }
}
.tabViewStyle(.sidebarAdaptable)
```

### 2.4 User customization

`TabViewCustomization` persists reorder/hide state through `@AppStorage`. **Every customizable tab and section must have a unique `.customizationID`** — without it the tab is silently opted out.

```swift
struct RootView: View {
    @AppStorage("MyTabViewCustomization") private var customization: TabViewCustomization

    var body: some View {
        TabView {
            Tab("Home", systemImage: "house") { HomeView() }
                .customizationID("tab.home")
                .customizationBehavior(.disabled, for: .sidebar, .tabBar)  // pin it

            Tab("Profile", systemImage: "person") { ProfileView() }
                .customizationID("tab.profile")

            Tab("Notifications", systemImage: "bell") { NotificationsView() }
                .customizationID("tab.notifications")
                .defaultVisibility(.hidden, for: .tabBar)                  // sidebar only
        }
        .tabViewStyle(.sidebarAdaptable)
        .tabViewCustomization($customization)
    }
}
```

### 2.5 iOS 26 Liquid Glass tab bar (WWDC25 sessions 323, 256)

Recompile against Xcode 26 and the tab bar floats above content as translucent glass that refracts what scrolls beneath it. Two new first-class modifiers unlock the full experience:

```swift
TabView(selection: $selection) {
    Tab("Home",    systemImage: "house", value: 0)          { HomeView() }
    Tab("Library", systemImage: "books.vertical", value: 1) { LibraryView() }
    Tab(value: 99, role: .search)                           { SearchView() }
}
.tabBarMinimizeBehavior(.onScrollDown)  // .automatic / .never / .onScrollDown / .onScrollUp
.tabViewBottomAccessory {               // persistent above-tab accessory (mini-player style)
    NowPlayingView()
}
```

Inside an accessory, read the environment to adapt to collapsed layout:

```swift
struct NowPlayingView: View {
    @Environment(\.tabViewBottomAccessoryPlacement) private var placement
    var body: some View {
        switch placement {
        case .expanded: FullPlayer()        // sits above tab bar
        case .inline:   CompactPlayer()     // inline with minimized bar
        default:        EmptyView()
        }
    }
}
```

**iOS 26 gotchas (filed bugs, verified via Apple Forums):** conditional content like `if selectedTab == 2 { ... }` inside `.tabViewBottomAccessory` leaves an empty pill in 26.0–26.1 (FB18479195). Prefer `tabViewBottomAccessory(isEnabled:content:)` (iOS 26.2+) or a state-driven stable accessory. `tabBarMinimizeBehavior` is iPhone-only and requires the tab content to actually overlay scrollable content; in 26 beta 7 it triggered unreliably when the tab root was a `NavigationStack(path:)` (forum 799604).

### 2.6 UIKit equivalent: UITabBarController

The classic UIKit pattern uses `viewControllers` and `UITabBarItem`. iOS 18 introduced a parallel, modern API with `UITab`, `UITabGroup`, and `UISearchTab` — functionally aligned with SwiftUI's new `Tab`.

```swift
final class AppTabController: UITabBarController {
    override func viewDidLoad() {
        super.viewDidLoad()

        // iOS 18+ declarative tabs
        self.tabs = [
            UITab(title: "Home", image: UIImage(systemName: "house"),
                  identifier: "tab.home") { _ in
                UINavigationController(rootViewController: HomeVC())
            },
            UITab(title: "Library", image: UIImage(systemName: "books.vertical"),
                  identifier: "tab.library") { _ in LibraryVC() },

            UITabGroup(title: "Collections",
                       image: UIImage(systemName: "folder"),
                       identifier: "group.collections",
                       children: [
                UITab(title: "Cinematic", image: UIImage(systemName: "film"),
                      identifier: "tab.cinematic") { _ in CinematicVC() },
                UITab(title: "Nature", image: UIImage(systemName: "leaf"),
                      identifier: "tab.nature") { _ in NatureVC() }
            ]) { _ in UIHostingController(rootView: BrowseRoot()) },

            UISearchTab { _ in
                UINavigationController(rootViewController: SearchVC())
            }
        ]

        self.mode = .tabSidebar                 // iPad: sidebar toggleable

        // iOS 26 accessory + minimize-on-scroll
        self.bottomAccessory = UITabAccessory(contentView: MiniPlayerView())
        self.tabBarMinimizeBehavior = .onScrollDown
    }
}
```

**Watch out:** with the new iOS 18 tab UI, the classic `tabBar(_:didSelect:)` delegate callback is *not* invoked (Apple Forum 764504). Use the new `tabBarController(_:didSelectTab:previousTab:)` or `tabBarController(_:visibilityDidChangeFor:)` instead.

### 2.7 SwiftUI ↔ UIKit tab mapping

| Concept | SwiftUI | UIKit (iOS 18+) |
|---|---|---|
| Tab container | `TabView` | `UITabBarController` |
| Single tab | `Tab(_:systemImage:value:content:)` | `UITab(...)` / `UITabBarItem` |
| Search tab | `Tab(role: .search)` | `UISearchTab` |
| Group (sidebar) | `TabSection { ... }` | `UITabGroup` |
| Sidebar/tab adaptive | `.tabViewStyle(.sidebarAdaptable)` | `tabBarController.mode = .tabSidebar` |
| Customization persistence | `@AppStorage` + `TabViewCustomization` + `.customizationID` | `UITab.identifier` + `allowsHiding` + `preferredPlacement` |
| Badge | `.badge(3)` / `.badge("!")` | `tab.badgeValue = "3"` |
| Minimize on scroll (iOS 26) | `.tabBarMinimizeBehavior(.onScrollDown)` | `tabBarMinimizeBehavior = .onScrollDown` |
| Bottom accessory (iOS 26) | `.tabViewBottomAccessory { ... }` | `UITabAccessory(contentView:)` + `bottomAccessory` |

---

## 3. NavigationStack: hierarchical drill-down

Introduced at WWDC22 session 10054 ("The SwiftUI cookbook for navigation"), `NavigationStack` replaces the stack role of `NavigationView` on iOS 16+. Its conceptual shift is **value-based, data-driven navigation** instead of embedding destination views inside every link.

### 3.1 Three initializers

```swift
NavigationStack { RootView() }                    // stack owns its state
NavigationStack(path: $pathArray) { RootView() }  // homogeneous, type-safe
NavigationStack(path: $navPath)   { RootView() }  // heterogeneous, type-erased
```

Where `pathArray` is a typed `[Route]` and `navPath` is a `NavigationPath`.

### 3.2 Value-based destinations — the canonical pattern

```swift
enum Route: Hashable {
    case product(Product)
    case relatedProduct(Product)
    case search(String)
}

struct Shop: View {
    @StateObject private var store = Store()
    @State private var path: [Route] = []

    var body: some View {
        NavigationStack(path: $path) {
            List(store.products) { product in
                NavigationLink(product.title, value: Route.product(product))
            }
            .navigationDestination(for: Route.self) { route in
                switch route {
                case .product(let p):        ProductView(product: p)
                case .relatedProduct(let p): ProductView(product: p.similar[0])
                case .search(let q):         SearchView(query: q)
                }
            }
            .toolbar {
                Button("Pop to root") { path.removeAll() }
            }
        }
    }
}
```

Programmatic operations: `path.append(x)` pushes, `path.removeLast()` pops, `path.removeAll()` (or `path = NavigationPath()`) returns to root, `path = [a, b, c]` deep-links to an exact stack.

### 3.3 Placement rules for `.navigationDestination`

These three rules account for almost every runtime warning developers hit.

**Rule 1 — inside the stack.** The modifier must be attached to a view inside the same `NavigationStack` it targets. A modifier outside the stack triggers: *"A NavigationLink is presenting a value of type 'X' but there is no matching navigation destination visible from the location of the link."*

**Rule 2 — not inside a lazy container that scrolls away.** WWDC22 is explicit: *"By attaching the modifier outside the ScrollView, I ensure that the NavigationStack can see this navigationDestination regardless of the scroll position."* A destination placed inside a `List` row, `LazyVStack`, or `LazyHGrid` that scrolls off-screen can be discarded, and navigation will silently fail.

**Rule 3 — one handler per type per stack.** Two siblings with `.navigationDestination(for: MyID.self)` produce undefined behavior plus a runtime warning. Consolidate into a single `Route` enum and branch inside one modifier.

### 3.4 NavigationLink: value vs destination

```swift
// Preferred (iOS 16+): lazy, decoupled
NavigationLink("Open", value: product)      // + matching navigationDestination(for: Product.self)

// Eager (allowed but not data-driven)
NavigationLink("Open") { ProductView(product: product) }
```

The old binding-based initializers (`NavigationLink(destination:isActive:)`, `NavigationLink(destination:tag:selection:)`) are **deprecated in iOS 16**. Replacements:

```swift
// iOS 16+: boolean-driven push
.navigationDestination(isPresented: $showDetail) { DetailView() }

// iOS 17+: optional-item-driven push
.navigationDestination(item: $selectedItem) { item in DetailView(item: item) }
```

### 3.5 Migration from NavigationView to NavigationStack

| Old (iOS 13–15) | New (iOS 16+) |
|---|---|
| `NavigationView { ... }` | `NavigationStack { ... }` (single column) or `NavigationSplitView` (multi-column) |
| `.navigationViewStyle(.stack)` | Remove — default in `NavigationStack` |
| `.navigationViewStyle(.columns)` | `NavigationSplitView` |
| `NavigationLink(destination:isActive:$b)` | `.navigationDestination(isPresented: $b) { V() }` |
| `NavigationLink(destination:tag:selection:$sel)` | `.navigationDestination(item: $sel) { V(item: $0) }` |
| Hidden `NavigationLink` + bool flag | `@State path` + `path.append(...)` |

Key migration caveats: `NavigationView` silently chose sidebar layout on iPad — `NavigationStack` is always single-column, so use `NavigationSplitView` when you want iPad sidebars. Nesting `NavigationStack`s inside each other is discouraged; the one legitimate exception is a modal sheet that gets its own internal stack.

### 3.6 UIKit equivalent: UINavigationController

```swift
let nav = UINavigationController(rootViewController: HomeVC())

// Push / pop
nav.pushViewController(DetailVC(item: item), animated: true)
nav.popViewController(animated: true)
nav.popToRootViewController(animated: true)
nav.setViewControllers([HomeVC(), DetailVC(), SubDetailVC()], animated: false)  // deep link

// Bar buttons on the child VC
navigationItem.rightBarButtonItems = [
    UIBarButtonItem(systemItem: .add,  primaryAction: UIAction { _ in /* ... */ }),
    UIBarButtonItem(systemItem: .edit, primaryAction: UIAction { _ in /* ... */ })
]

// iOS 15+ appearance — set ALL THREE to guarantee consistency
let appearance = UINavigationBarAppearance()
appearance.configureWithOpaqueBackground()
appearance.backgroundColor = .systemBlue
nav.navigationBar.standardAppearance   = appearance
nav.navigationBar.compactAppearance    = appearance
nav.navigationBar.scrollEdgeAppearance = appearance
```

### 3.7 API mapping

| SwiftUI | UIKit |
|---|---|
| `NavigationStack` | `UINavigationController` |
| `NavigationLink(value:)` | `pushViewController(_:animated:)` |
| `path.removeLast()` | `popViewController(animated:)` |
| `path.removeAll()` | `popToRootViewController(animated:)` |
| `path = [a, b, c]` | `setViewControllers([a, b, c], animated:)` |
| `.navigationTitle` | `navigationItem.title` |
| `.navigationBarBackButtonHidden(true)` | `navigationItem.hidesBackButton = true` |
| `.toolbar { ToolbarItem(.topBarTrailing) { ... } }` | `navigationItem.rightBarButtonItem = ...` |

---

## 4. NavigationSplitView: iPad sidebars

`NavigationSplitView` is the multi-column container. It renders as 2 or 3 columns in regular width (iPad landscape, Mac) and **collapses to a single `NavigationStack` in compact width** (iPhone, iPad Slide Over).

### 4.1 Two- and three-column layouts

```swift
// Two-column: sidebar + detail (Mail-style on iPhone scaled up)
NavigationSplitView {
    SidebarView()
} detail: {
    DetailView()
}

// Three-column: sidebar + content + detail (Mail on iPad, Notes on iPad)
NavigationSplitView {
    SidebarView()          // accounts
} content: {
    InboxList()            // messages list
} detail: {
    MessageDetail()        // message body
}
```

### 4.2 Selection flow across columns

The idiomatic pattern binds `List(selection:)` in the sidebar, which auto-updates the content column; content selection drives the detail column.

```swift
struct MailRoot: View {
    @State private var folder: Folder?
    @State private var message: Message?

    var body: some View {
        NavigationSplitView {
            List(Folder.all, id: \.self, selection: $folder) { f in
                NavigationLink(f.name, value: f)
            }
        } content: {
            if let folder {
                List(messages(in: folder), id: \.self, selection: $message) { m in
                    NavigationLink(m.subject, value: m)
                }
            } else {
                ContentUnavailableView("Pick a folder", systemImage: "folder")
            }
        } detail: {
            if let message {
                MessageDetail(message: message)
            } else {
                ContentUnavailableView("Pick a message", systemImage: "envelope")
            }
        }
    }
}
```

### 4.3 Visibility, compact column, and style

```swift
@State private var visibility: NavigationSplitViewVisibility = .all
@State private var compactColumn: NavigationSplitViewColumn = .detail

NavigationSplitView(
    columnVisibility: $visibility,
    preferredCompactColumn: $compactColumn
) {
    Sidebar()
} content: {
    Content()
} detail: {
    Detail()
}
.navigationSplitViewStyle(.balanced)   // .automatic / .balanced / .prominentDetail
```

`NavigationSplitViewVisibility` cases: `.automatic`, `.all`, `.doubleColumn`, `.detailOnly`. Set `visibility = .detailOnly` to programmatically hide the sidebar (a "Focus" button). `preferredCompactColumn` (iOS 17+) selects which column shows on top after the iPhone collapse; requesting a non-existent column (e.g., `.content` in a two-column view) falls back to `.sidebar`.

`NavigationSplitViewStyle`:
- `.automatic` — iPhone collapses to `prominentDetail`; iPad landscape ≈ balanced; iPad portrait ≈ prominentDetail.
- `.balanced` — leading columns take space from the detail.
- `.prominentDetail` — detail stays full size; other columns slide over on top.

### 4.4 Detail column: replace vs embed a NavigationStack

Two idioms, each correct for different scenarios. **Replace** means the detail view changes wholesale on selection (no inner push history):

```swift
} detail: {
    if let item = selected { ItemDetail(item: item) }
    else { Text("No selection") }
}
```

**Embed** means the detail owns its own push stack so drill-down happens inside it. WWDC22 recommends this for mail-style apps:

```swift
} detail: {
    NavigationStack(path: $detailPath) {
        ItemDetail(item: selected)
            .navigationDestination(for: SubItem.self) { SubItemView(sub: $0) }
    }
}
```

On iPhone collapse, SwiftUI automatically merges the detail's inner stack into the outer stack so back navigation traverses both naturally.

### 4.5 UIKit equivalent: UISplitViewController

```swift
let split = UISplitViewController(style: .tripleColumn)   // or .doubleColumn
split.preferredDisplayMode   = .twoBesideSecondary
split.preferredSplitBehavior = .tile

split.setViewController(SidebarVC(),       for: .primary)
split.setViewController(ContentListVC(),   for: .supplementary)  // .tripleColumn only
split.setViewController(DetailVC(),        for: .secondary)
split.setViewController(CompactRootVC(),   for: .compact)        // shown when collapsed
split.delegate = self

// Delegate controls collapse behavior (SwiftUI's preferredCompactColumn equivalent)
func splitViewController(
    _ svc: UISplitViewController,
    topColumnForCollapsingToProposedTopColumn proposed: UISplitViewController.Column
) -> UISplitViewController.Column {
    .primary
}
```

**Gotcha:** assigning a controller to `.supplementary` in a `.doubleColumn` split view crashes at runtime. Match columns to the chosen style.

### 4.6 Common mistakes specific to split views

Wrapping the sidebar in its own `NavigationStack` causes `.navigationDestination` modifiers to push within the sidebar column instead of targeting the detail. Use `List(selection:)` + the detail closure for cross-column navigation instead. Apple's exact warning text for a misplaced destination: *"A `navigationDestination(isPresented:content:)` is outside an explicit NavigationStack, but inside the detail column of a NavigationSplitView, so it attempts to target the next column. There is no next column after the detail column."* (Apple Forum 715589).

---

## 5. Sheets and detents

A sheet is the default modal presentation: a card that animates up from the bottom. On iPhone it covers the full screen by default or stops at detents you specify (iOS 16+). On iPad it presents as a centered `.formSheet` or full-width `.pageSheet`.

### 5.1 Presentation idioms

Use `sheet(item:)` whenever you're passing data from a list. With `sheet(isPresented:)` plus a separate `@State selected` variable, SwiftUI frequently captures a stale row value because the closure is built before the binding updates. `sheet(item:)` binds the two together.

```swift
struct Person: Identifiable { let id = UUID(); var name: String }

struct PeopleView: View {
    let people: [Person]
    @State private var selection: Person?

    var body: some View {
        List(people) { person in
            Button(person.name) { selection = person }
        }
        .sheet(item: $selection) { person in        // automatically nils on dismiss
            PersonEditor(person: person)
        }
    }
}
```

Dismissal uses `@Environment(\.dismiss)`, which replaces the older `presentationMode` binding. **Critical rule:** read `\.dismiss` inside the *presented* view, not the presenter. Calling `dismiss()` in the presenter's body affects the presenter itself, not the sheet.

### 5.2 Detents (iOS 16+)

```swift
.sheet(isPresented: $show) {
    FilterPanel()
        .presentationDetents([
            .medium,          // ~half screen
            .large,           // full
            .fraction(0.3),   // 30% of available height
            .height(200)      // fixed 200 pt
        ])
}
```

Built-ins: `.large` (default), `.medium` (disabled on iPhone compact-height, i.e., landscape — falls back to `.large`). With a selection binding, programmatic detent changes animate:

```swift
@State private var detent: PresentationDetent = .medium

.presentationDetents([.height(120), .medium, .large], selection: $detent)
```

For context-aware heights, implement `CustomPresentationDetent`:

```swift
struct BottomBarDetent: CustomPresentationDetent {
    static func height(in context: Context) -> CGFloat? {
        if context.dynamicTypeSize.isAccessibilitySize {
            return max(120, context.maxDetentValue * 0.2)
        }
        return max(64, context.maxDetentValue * 0.1)
    }
}
extension PresentationDetent {
    static let bottomBar = Self.custom(BottomBarDetent.self)
}
```

### 5.3 The full sheet customization stack (iOS 16.4+)

```swift
Map()
    .sheet(isPresented: .constant(true)) {
        SearchList()
            .presentationDetents([.height(120), .fraction(0.4), .large])
            .presentationDragIndicator(.visible)                            // show grabber
            .presentationBackground(.thinMaterial)                          // 16.4+
            .presentationBackgroundInteraction(.enabled(upThrough: .fraction(0.4)))
            .presentationContentInteraction(.scrolls)                       // 16.4+
            .presentationCornerRadius(20)                                   // 16.4+
            .interactiveDismissDisabled(hasUnsavedChanges)
    }
```

**`presentationBackgroundInteraction`** is the Maps/Find My/Stocks enabler: the view *behind* the sheet stays tappable and undimmed as long as the sheet is at or below the named detent. **`presentationContentInteraction(.scrolls)`** tells a scroll view inside the sheet to scroll first; the default `.resizes` makes drag gestures anywhere resize the sheet.

### 5.4 Interactive dismiss

```swift
.interactiveDismissDisabled(!hasAcceptedTerms)  // conditional block
```

In iOS 18.1, developers reported intermittent regressions of this modifier (Apple Forum 767377) — defensive testing recommended.

### 5.5 fullScreenCover

```swift
.fullScreenCover(isPresented: $showOnboarding) {
    NavigationStack {
        OnboardingFlow()
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Skip") { showOnboarding = false }
                }
            }
    }
}
```

`fullScreenCover` has **no swipe-to-dismiss** and removes the presenter from the hierarchy. An explicit dismiss control is mandatory — forgetting it traps the user. Reserve it for onboarding, immersive media playback, camera/scanner flows, and paywalls.

### 5.6 UIKit equivalent: UISheetPresentationController

```swift
let vc = DetailViewController()
vc.modalPresentationStyle = .pageSheet

if let sheet = vc.sheetPresentationController {
    sheet.detents = [.medium(), .large()]                     // iOS 15
    if #available(iOS 16.0, *) {
        let smallID = UISheetPresentationController.Detent.Identifier("small")
        sheet.detents = [
            .custom(identifier: smallID) { ctx in 0.2 * ctx.maximumDetentValue },
            .medium(), .large()
        ]
        sheet.selectedDetentIdentifier = smallID
    }
    sheet.prefersGrabberVisible = true
    sheet.preferredCornerRadius = 24
    sheet.largestUndimmedDetentIdentifier = .medium           // background stays interactive
    sheet.prefersScrollingExpandsWhenScrolledToEdge = false
    sheet.prefersEdgeAttachedInCompactHeight = true
    sheet.widthFollowsPreferredContentSizeWhenEdgeAttached = true
}
// Block interactive dismiss
vc.isModalInPresentation = true
vc.presentationController?.delegate = self                    // UIAdaptivePresentationControllerDelegate

present(vc, animated: true)
```

### 5.7 iOS 26 Liquid Glass sheet behavior

Recompile against Xcode 26 and partial-height sheets become **inset floating glass** panels with display-corner-matched radii; at `.large` they transition to opaque and attach to the edges. WWDC25 session 323 recommends **removing custom `presentationBackground` values** to let the new material render. Under Liquid Glass, `UIPopoverPresentationController.backgroundColor` is ignored unless `UIDesignRequiresCompatibility = YES` in Info.plist (Apple Forum 804346).

### 5.8 Morph-from-button zoom transitions (iOS 18+, polished in iOS 26)

```swift
struct BirdDetail: View {
    @Namespace private var transition
    @State private var showInfo = false

    var body: some View {
        NavigationStack {
            BirdImage()
                .toolbar {
                    ToolbarSpacer(placement: .bottomBar)                   // iOS 26
                    ToolbarItem(placement: .bottomBar) {
                        Button("Info", systemImage: "info") { showInfo = true }
                    }
                    .matchedTransitionSource(id: "info", in: transition)
                }
                .sheet(isPresented: $showInfo) {
                    InfoView()
                        .presentationDetents([.medium, .large])
                        .navigationTransition(.zoom(sourceID: "info", in: transition))
                }
        }
    }
}
```

Known bugs: the zoom transition to a `.medium` detent causes the background to re-dim and source button text to reappear abruptly on iOS 26.0/26.1 (forum 788257, 807208) — test on the exact OS version you target.

---

## 6. Popovers

Popovers are an **iPad- and Mac-first** presentation. On iPhone (compact width) they adapt to a sheet by default — a behavior the HIG explicitly endorses: *"Avoid displaying popovers on iPhones. Generally, popovers should be reserved for use in iPad apps. In iPhone apps, utilize all available screen space by presenting information in a full-screen modal view."*

### 6.1 Basic usage

```swift
@State private var showInfo = false

Button("Info") { showInfo = true }
    .popover(
        isPresented: $showInfo,
        attachmentAnchor: .rect(.bounds),
        arrowEdge: .top
    ) {
        InfoView()
            .frame(minWidth: 300, minHeight: 200)   // required — popovers don't auto-size
    }
```

Missing a frame is the #1 popover bug: it often renders at zero size or off-screen.

### 6.2 Forcing popover appearance on iPhone (iOS 16.4+)

```swift
.popover(isPresented: $show) {
    EmojiPicker()
        .frame(minWidth: 300, maxHeight: 400)
        .presentationCompactAdaptation(.popover)    // overrides default sheet adaptation
}
```

`PresentationAdaptation` options: `.automatic` (default → sheet on iPhone), `.none` (don't adapt), `.popover`, `.sheet`, `.fullScreenCover`.

### 6.3 iOS 18 behavior change

iOS 18 now **strictly honors `arrowEdge`**, where iOS 17 treated it as a hint. This caused regressions (Apple Forum 756873) — popovers that used to auto-reposition can now clip at screen edges. Re-audit arrow edge choices for iOS 18+ targets.

### 6.4 UIKit equivalent: UIPopoverPresentationController

```swift
let pop = OptionsViewController()
pop.modalPresentationStyle = .popover
pop.preferredContentSize   = CGSize(width: 320, height: 240)

if let p = pop.popoverPresentationController {
    p.sourceItem             = barButtonItem           // or sourceView + sourceRect
    p.permittedArrowDirections = .any
    p.delegate               = self                    // required on iPhone for true popover
}
present(pop, animated: true)

// Required: return .none on iPhone to prevent adaptation to full-screen sheet
extension VC: UIPopoverPresentationControllerDelegate {
    func adaptivePresentationStyle(
        for c: UIPresentationController,
        traitCollection: UITraitCollection
    ) -> UIModalPresentationStyle { .none }
}
```

---

## 7. Modal vs push: the decision criteria

HIG on modality: *"Modality is a design technique that presents content in a separate, dedicated mode that prevents interaction with the parent view and requires an explicit action to dismiss."* And: *"Minimize the use of modality."*

| Criterion | Push (NavigationStack) | Modal (sheet / cover / popover) |
|---|---|---|
| Relationship to current view | Child of current content | Orthogonal side task |
| Mental model | "Going deeper" | "Pausing to do X" |
| Data flow | Reading, browsing | Editing, composing, confirming |
| Task length | Any | Short, focused |
| Reversibility | Back button | Cancel / Done / swipe-down |
| Part of main hierarchy? | Yes | No |

Rule of thumb: if the user thinks *"show me more about this"* → push. If they think *"let me do X and come back"* → modal.

**Dismiss gesture comparison:**

| Container | Swipe down | Tap outside | Back button | Explicit button |
|---|---|---|---|---|
| Sheet (iPhone) | ✅ unless disabled | — | — | Required if interactive dismiss disabled |
| Sheet (iPad formSheet) | — | ✅ unless disabled | — | Required if interactive dismiss disabled |
| fullScreenCover | ❌ | ❌ | — | **Mandatory** |
| Popover (iPad/Mac) | — | ✅ | — | Optional |
| Push | — | — | ✅ | — |

---

## 8. Back navigation

### 8.1 System back button behavior

`NavigationStack` automatically renders the back button in the leading toolbar slot of every pushed view. Its label comes from the previous view's `navigationTitle`; tapping it is equivalent to `path.removeLast()` or `dismiss()`. Because `NavigationStack` is implemented atop `UINavigationController` on iOS, the UIKit `interactivePopGestureRecognizer` (the edge-swipe) is inherited for free.

HIG guidance: **preserve the system back button**. It supports the edge-swipe, VoiceOver, Full Keyboard Access, and is the platform's most-memorized gesture.

### 8.2 Custom back button (loses swipe by default)

```swift
struct DetailView: View {
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        content
            .navigationBarBackButtonHidden(true)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {     // iOS 17+ name; .navigationBarLeading pre-17
                    Button {
                        dismiss()
                    } label: {
                        HStack(spacing: 4) {
                            Image(systemName: "chevron.backward")
                            Text("Home")
                        }
                    }
                }
            }
    }
}
```

The edge-swipe stops working once `.navigationBarBackButtonHidden(true)` is set. If you need a custom leading button *and* the gesture, you need UIKit interop — SwiftUI has no native API for this as of iOS 26.

### 8.3 Restoring the swipe-back gesture

The **UIKit bridge** (global) swizzles every navigation controller:

```swift
extension UINavigationController: UIGestureRecognizerDelegate {
    override open func viewDidLoad() {
        super.viewDidLoad()
        interactivePopGestureRecognizer?.delegate = self
    }
    public func gestureRecognizerShouldBegin(_ g: UIGestureRecognizer) -> Bool {
        viewControllers.count > 1                // guard against root freeze bug
    }
}
```

The **per-view enabler** via `UIViewControllerRepresentable`:

```swift
struct SwipeBackEnabler: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        let vc = UIViewController()
        DispatchQueue.main.async {
            vc.parent?.navigationController?
              .interactivePopGestureRecognizer?.delegate = nil
        }
        return vc
    }
    func updateUIViewController(_: UIViewController, context: Context) {}
}

// Attach: SwipeBackEnabler().frame(width: 0, height: 0)
```

### 8.4 Trade-offs

Custom back buttons cost you the gesture and break muscle memory. Prefer keeping the default back button and customize around it: use `.toolbarRole(.editor)` on iOS 16+ to get a compact leading chevron, set `navigationItem.backButtonDisplayMode = .minimal` (UIKit) to hide the label, or set `navigationItem.backBarButtonItem` on the *source* view controller to customize the label shown on the next pushed VC.

---

## 9. Deep linking and state restoration

### 9.1 onOpenURL and URL parsing

```swift
@main
struct MyApp: App {
    @State private var path: [Route] = []

    var body: some Scene {
        WindowGroup {
            RootView(path: $path)
                .onOpenURL { url in
                    path = Route.path(from: url) ?? []
                }
        }
    }
}

enum Route: Hashable, Codable {
    case product(id: String)
    case search(query: String)
    case category(String)

    static func path(from url: URL) -> [Route]? {
        guard url.scheme == "myapp" else { return nil }
        let comps = URLComponents(url: url, resolvingAgainstBaseURL: false)
        switch url.host {
        case "product":
            let id = url.pathComponents.dropFirst().first ?? ""
            return [.product(id: String(id))]
        case "search":
            let q = comps?.queryItems?.first(where: { $0.name == "q" })?.value ?? ""
            return [.search(query: q)]
        case "category":
            let parts = url.pathComponents.dropFirst()
            return parts.map { .category(String($0)) }
        default: return nil
        }
    }
}
```

Register URL schemes in Info.plist under URL Types, or use Universal Links with an associated domain. `onOpenURL` fires for both cold launch (after the initial view appears) and warm open.

### 9.2 Codable NavigationPath for persistence

```swift
// Save
if let repr = path.codable {
    let data = try JSONEncoder().encode(repr)
    // persist
}

// Restore
if let repr = try? JSONDecoder().decode(
    NavigationPath.CodableRepresentation.self, from: data) {
    path = NavigationPath(repr)
}
```

Every type pushed onto the path must conform to `Codable & Hashable`. `NavigationPath.CodableRepresentation` uses Swift's `_mangledTypeName` runtime machinery — meaning **renaming or moving a route type across app versions breaks restored paths**. If you need forward compatibility across releases, use `[Route]` with a `Codable` enum instead of `NavigationPath`; you control the coding keys explicitly.

### 9.3 SceneStorage + full restoration pattern

```swift
struct RootView: View {
    @SceneStorage("nav.path") private var pathData: Data?
    @State private var path: [Route] = []

    var body: some View {
        NavigationStack(path: $path) {
            HomeView()
                .navigationDestination(for: Route.self) { destination(for: $0) }
        }
        .task {
            if let data = pathData,
               let saved = try? JSONDecoder().decode([Route].self, from: data) {
                path = saved
            }
        }
        .onChange(of: path) { _, newPath in
            pathData = try? JSONEncoder().encode(newPath)
        }
        .onOpenURL { url in
            if let newPath = Route.path(from: url) { path = newPath }
        }
    }
}
```

`@SceneStorage` is per-scene, system-managed storage — do not use it for sensitive data, and note the system makes no guarantees about persistence timing. It accepts `RawRepresentable` values, primitives, `URL`, and `Data`. For handoff, wire `.onContinueUserActivity(_:perform:)` to the same route-building function.

---

## 10. Anti-patterns: wrong way vs right way

### 10.1 Double modal (sheet presenting a sheet)

HIG: *"Take care to avoid creating a modal experience that feels like an app within your app."* Stacking modals produces stolen safe area, flickering cards, and confused dismiss stacks. On iPad, sheets over popovers are explicitly disallowed.

```swift
// ❌ WRONG — nested sheets
.sheet(isPresented: $showFirst) {
    VStack {
        Button("More") { showSecond = true }
    }
    .sheet(isPresented: $showSecond) { DetailView() }   // stacked card
}

// ✅ RIGHT — use NavigationStack inside the sheet for drill-down
.sheet(isPresented: $showFirst) {
    NavigationStack {
        List {
            NavigationLink("More", value: Detail.self)
        }
        .navigationDestination(for: Detail.Type.self) { _ in DetailView() }
    }
}
```

If you *must* show two sequential modals, dismiss the first and re-present the second after a transition delay — or chain via `onDismiss:`.

### 10.2 Tab-in-tab (nested tab bars)

Nesting a `TabView` inside another `TabView`'s destination produces two persistent tab bars, breaks state restoration, and under iOS 26 overlaps Liquid Glass materials.

```swift
// ❌ WRONG
TabView {
    NavigationStack {
        List { NavigationLink("Open", value: "x") }
            .navigationDestination(for: String.self) { _ in
                TabView { /* second tab bar */ }
            }
    }.tabItem { Label("Home", systemImage: "house") }
}

// ✅ RIGHT — use a Picker (segmented) for the sub-mode
TabView {
    NavigationStack {
        DetailWithSubModes()
    }.tabItem { Label("Home", systemImage: "house") }
}

struct DetailWithSubModes: View {
    @State private var mode: Mode = .one
    enum Mode: String, CaseIterable, Identifiable { case one, two; var id: Self { self } }
    var body: some View {
        VStack {
            Picker("", selection: $mode) {
                ForEach(Mode.allCases) { Text($0.rawValue).tag($0) }
            }.pickerStyle(.segmented)
            switch mode {
            case .one: OneView()
            case .two: TwoView()
            }
        }
    }
}
```

### 10.3 Sheet when push is correct (list drill-down)

```swift
// ❌ WRONG — drill-down disguised as modal; breaks mental model
List(items) { item in
    Button(item.name) { selected = item }
}
.sheet(item: $selected) { DetailView(item: $0) }

// ✅ RIGHT — hierarchical push
NavigationStack {
    List(items) { item in
        NavigationLink(item.name, value: item)
    }
    .navigationDestination(for: Item.self) { DetailView(item: $0) }
}
```

### 10.4 Push when sheet is correct (settings, compose)

```swift
// ❌ WRONG — settings pushed onto main stack pollutes back history
NavigationStack {
    HomeView().toolbar {
        NavigationLink("Settings") { SettingsView() }
    }
}

// ✅ RIGHT — settings is orthogonal; modal sheet
struct Right: View {
    @State private var showSettings = false
    var body: some View {
        NavigationStack {
            HomeView().toolbar {
                Button { showSettings = true } label: { Image(systemName: "gear") }
            }
        }
        .sheet(isPresented: $showSettings) {
            NavigationStack { SettingsView() }
        }
    }
}
```

### 10.5 Misuse of fullScreenCover

```swift
// ❌ WRONG — trivial rename traps the user full-screen with no obvious exit
.fullScreenCover(isPresented: $editing) { QuickRenameForm() }

// ✅ RIGHT — partial-height sheet preserves context
.sheet(isPresented: $editing) {
    QuickRenameForm()
        .presentationDetents([.height(220)])
        .presentationDragIndicator(.visible)
}
```

### 10.6 Multiple navigationDestination for the same type

```swift
// ❌ WRONG — undefined: SwiftUI picks one, logs a runtime warning
NavigationStack {
    List { NavigationLink("A", value: MyID(1)); NavigationLink("B", value: MyID(2)) }
        .navigationDestination(for: MyID.self) { id in ViewA(id) }
        .navigationDestination(for: MyID.self) { id in ViewB(id) }
}

// ✅ RIGHT — one destination per type; branch via enum
enum Route: Hashable { case a(MyID), b(MyID) }
NavigationStack {
    List {
        NavigationLink("A", value: Route.a(MyID(1)))
        NavigationLink("B", value: Route.b(MyID(2)))
    }
    .navigationDestination(for: Route.self) { route in
        switch route {
        case .a(let id): ViewA(id)
        case .b(let id): ViewB(id)
        }
    }
}
```

### 10.7 navigationDestination outside the stack

```swift
// ❌ WRONG — modifier not inside any NavigationStack
VStack {
    NavigationStack { List { NavigationLink("Go", value: 1) } }
}
.navigationDestination(for: Int.self) { Text("\($0)") }

// ✅ RIGHT — inside the stack, on any descendant of its root view
NavigationStack {
    List { NavigationLink("Go", value: 1) }
        .navigationDestination(for: Int.self) { Text("\($0)") }
}
```

### 10.8 Reading @Environment(\.dismiss) in the presenter

```swift
// ❌ WRONG — dismiss() refers to the presenter, not the sheet
struct Parent: View {
    @Environment(\.dismiss) var dismiss
    @State var show = false
    var body: some View {
        Button("Show") { show = true }
            .sheet(isPresented: $show) {
                Button("Close") { dismiss() }       // no-op on the sheet
            }
    }
}

// ✅ RIGHT — extract a child that reads its own environment
struct Parent: View {
    @State var show = false
    var body: some View {
        Button("Show") { show = true }
            .sheet(isPresented: $show) { Child() }
    }
}
struct Child: View {
    @Environment(\.dismiss) var dismiss
    var body: some View { Button("Close") { dismiss() } }
}
```

### 10.9 Popover without a frame

```swift
// ❌ WRONG — often renders at zero size
.popover(isPresented: $show) { Text("Hello") }

// ✅ RIGHT — provide intrinsic sizing
.popover(isPresented: $show) {
    Text("Hello")
        .padding()
        .frame(minWidth: 200, minHeight: 80)
        .presentationCompactAdaptation(.popover)
}
```

---

## 11. Comparison tables

### 11.1 Sheet vs fullScreenCover vs push

| Attribute | `.sheet` | `.fullScreenCover` | Push (`NavigationStack`) |
|---|---|---|---|
| Coverage | Partial (detents) or ~90% | 100% | Replaces current view |
| Interactive dismiss | ✅ swipe-down (disable via `.interactiveDismissDisabled()`) | ❌ requires button | ✅ edge-swipe back |
| UIKit equivalent style | `.pageSheet` / `.formSheet` | `.fullScreen` / `.overFullScreen` | push on nav controller |
| Presenter visible? | Yes (may dim or stay interactive) | No (removed from hierarchy) | No (pushed off) |
| Built-in nav bar | None unless wrapped in `NavigationStack` | None unless wrapped | Provided |
| Preserves presenter state | ✅ | ❌ | ❌ |
| Best for | Compose, settings, filter, share | Video, onboarding, paywall, camera | Related drill-down |
| iPad adaptation | `.formSheet` centered card | Full screen | Push in detail column |
| macOS | Window-style sheet | Unavailable | Push |

### 11.2 iPhone vs iPad adaptive behavior

| Container | iPhone (compact) | iPad (regular) | iPad (compact / Slide Over) |
|---|---|---|---|
| `.popover` | Adapts to sheet; override with `.presentationCompactAdaptation(.popover)` | True popover anchored to source | Adapts to sheet |
| `UISplitViewController .doubleColumn` | Collapses to nav stack or `.compact` VC | 2 columns tiled | May collapse |
| `UISplitViewController .tripleColumn` | Collapses to stack (start column via delegate) | 3 columns tiled | Supplementary becomes overlay |
| `NavigationSplitView` | Collapses to `NavigationStack` | 2–3 columns per style | Adapts to size class |
| `TabView` + `.sidebarAdaptable` | Bottom tab bar | Sidebar toggleable from top tab bar | Bottom tab bar |
| `UITabBarController.mode = .tabSidebar` | Always tab bar | Sidebar toggleable | Tab bar |
| `.sheet` with `.medium` | Bottom sheet at ~50% | Centered `.formSheet` card | Bottom sheet |
| `.fullScreenCover` | Full screen | Full screen of window | Full screen |

### 11.3 API availability across iOS versions

| Feature | iOS 15 | iOS 16 / 16.4 | iOS 17 | iOS 18 | iOS 26 |
|---|---|---|---|---|---|
| Stack navigation (SwiftUI) | `NavigationView` | **`NavigationStack`**, `NavigationPath`, `.navigationDestination(for:)` | `.navigationDestination(item:)` | unchanged | Liquid Glass automatic |
| Multi-column (SwiftUI) | `NavigationView` | **`NavigationSplitView`** 2/3-col | `preferredCompactColumn` | improved iPad integration | Glass sidebars + `backgroundExtensionEffect` |
| Bottom sheet (UIKit) | **`UISheetPresentationController`** `.medium()/.large()` | 16: `.custom` detents | — | — | Liquid Glass |
| Bottom sheet (SwiftUI) | — | `.presentationDetents`, `.presentationDragIndicator` | — | — | Inset glass cards |
| Sheet customization (SwiftUI) | — | **16.4:** `presentationCornerRadius`, `presentationBackground`, `presentationBackgroundInteraction`, `presentationContentInteraction`, `presentationCompactAdaptation` | Inspector API | — | Glass materials |
| Tab API (SwiftUI) | `.tabItem` + `.tag` | same | same | **`Tab{}`, `TabSection`, `role: .search`, `.sidebarAdaptable`, `TabViewCustomization`** | `.tabBarMinimizeBehavior`, `.tabViewBottomAccessory`, glass |
| Tab API (UIKit) | `viewControllers` + `UITabBarItem` | same | same | **`UITab`, `UITabGroup`, `UISearchTab`, `mode = .tabSidebar`** | `UITabAccessory`, `bottomAccessory`, `tabBarMinimizeBehavior` |
| Zoom morph transition | — | — | — | **`.navigationTransition(.zoom(sourceID:in:))` + `matchedTransitionSource`** | polished |
| Design language | Default | Default | Default | Default | **Liquid Glass**, `ToolbarSpacer`, `navigationSubtitle`, `DefaultToolbarItem`, `.glassProminent`, `.glassEffect` |

---

## 12. WWDC session references

### WWDC 2022 — iOS 16 foundation

**Session 10054 — "The SwiftUI cookbook for navigation"** — Curt Clifton. Introduced `NavigationStack`, `NavigationSplitView`, `NavigationPath`, value-based `NavigationLink`, and the `.navigationDestination(for:)` modifier. Source of the "don't put destinations inside lazy containers" rule. URL: https://developer.apple.com/videos/play/wwdc2022/10054/

**Session 10001 — "Explore navigation design for iOS"** — Sarah McClanahan. Design-oriented companion; the canonical best-practices reference cited by the 2024 tab session. URL: https://developer.apple.com/videos/play/wwdc2022/10001/

**Session 10058 — "SwiftUI on iPad: Organize your interface"** — `NavigationSplitView` column configuration. URL: https://developer.apple.com/videos/play/wwdc2022/10058/

### WWDC 2024 — iOS 18 tab and sidebar

**Session 10147 — "Elevate your tab and sidebar experience in iPadOS"** — Andy Liang. Introduced SwiftUI `Tab`, `TabSection`, `TabRole.search`, `.tabViewStyle(.sidebarAdaptable)`, `TabViewCustomization`; UIKit `UITab`, `UITabGroup`, `UISearchTab`, `.tabSidebar` mode. URL: https://developer.apple.com/videos/play/wwdc2024/10147/

**Session 10144 — "What's new in SwiftUI"** — covered the new `Tab` API overview, `.navigationTransition(.zoom(sourceID:in:))`, floating iPad tab bar. URL: https://developer.apple.com/videos/play/wwdc2024/10144/

**Session 10118 — "What's new in UIKit"** — zoom transitions for navigation/presentation, interruptible and interactive; references 10147. URL: https://developer.apple.com/videos/play/wwdc2024/10118/

### WWDC 2025 — iOS 26 Liquid Glass

**Session 219 — "Meet Liquid Glass"** — Chan Karunamuni, Shubham Kedia, Bruno Canales. Defines Liquid Glass as "a digital meta-material" reserved for the navigation layer above content. URL: https://developer.apple.com/videos/play/wwdc2025/219/

**Session 356 — "Get to know the new design system"** — architectural guidance for applying the new system. URL: https://developer.apple.com/videos/play/wwdc2025/356/

**Session 323 — "Build a SwiftUI app with the new design"** — Franck Ndame Mpouli. Introduced `tabBarMinimizeBehavior`, `tabViewBottomAccessory`, `TabViewBottomAccessoryPlacement`, `ToolbarSpacer`, `.glassEffect`, `GlassEffectContainer`, `backgroundExtensionEffect`, `searchToolbarBehavior(.minimize)`. URL: https://developer.apple.com/videos/play/wwdc2025/323/

**Session 284 — "Build a UIKit app with the new design"** — `UITabBarController.tabBarMinimizeBehavior`, `UITabAccessory`, `bottomAccessory`, `UIBackgroundExtensionView`, Liquid Glass in navigation bars. URL: https://developer.apple.com/videos/play/wwdc2025/284/

**Session 256 — "What's new in SwiftUI"** — recompile-for-new-design message, `ToolbarSpacer`, `navigationSubtitle`, `DefaultToolbarItem`, `.glassProminent` button style. URL: https://developer.apple.com/videos/play/wwdc2025/256/

### Human Interface Guidelines pages

- Tab bars: https://developer.apple.com/design/human-interface-guidelines/tab-bars
- Sidebars: https://developer.apple.com/design/human-interface-guidelines/sidebars
- Navigation bars (merged with Toolbars, June 9 2025): https://developer.apple.com/design/human-interface-guidelines/navigation-bars
- Sheets: https://developer.apple.com/design/human-interface-guidelines/sheets
- Modality: https://developer.apple.com/design/human-interface-guidelines/modality
- Popovers: https://developer.apple.com/design/human-interface-guidelines/popovers
- Liquid Glass: https://developer.apple.com/design/human-interface-guidelines/liquid-glass

### Apple documentation companions

- Migrating to new navigation types: https://developer.apple.com/documentation/SwiftUI/Migrating-to-New-Navigation-Types
- Bringing robust navigation structure to your SwiftUI app: https://developer.apple.com/documentation/swiftui/bringing_robust_navigation_structure_to_your_swiftui_app
- Enhancing your app's content with tab navigation: https://developer.apple.com/documentation/SwiftUI/Enhancing-your-app-content-with-tab-navigation
- Elevating your iPad app with a tab bar and sidebar: https://developer.apple.com/documentation/UIKit/elevating-your-ipad-app-with-a-tab-bar-and-sidebar
- Adopting Liquid Glass (tech overview): https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass

---

## Conclusion: what has actually changed, and what hasn't

The durable lesson across three WWDC cycles is that **navigation structure is stable; navigation appearance is volatile**. `NavigationStack`, `NavigationSplitView`, `TabView`, `.sheet`, `.fullScreenCover`, and `.popover` have the same semantics in iOS 26 as they did in iOS 16. What iOS 18 added was **compile-time safety for tabs** (`Tab{}` + `TabRole.search`) and **one-declaration adaptive sidebars** (`.sidebarAdaptable`). What iOS 26 added is **visual** — Liquid Glass, `tabBarMinimizeBehavior`, `tabViewBottomAccessory`, `ToolbarSpacer`, `navigationSubtitle` — plus two subtle interaction refinements: the polished zoom-morph transition and the scroll-hide tab bar.

Two novel insights emerge from this synthesis. **First**, iOS 26's Liquid Glass has a strict architectural rule embedded in the HIG — *"Liquid Glass is best reserved for the navigation layer that floats above the content of your app"* — which means the content-vs-navigation distinction is no longer just a design principle but a material constraint. Mixing glass with content, stacking glass on glass, or applying `.glassEffect` to non-navigation surfaces breaks Apple's design system. **Second**, the iOS 18 `Tab` API did more than modernize syntax: it moved tab selection from runtime tags to compile-time values, eliminating an entire class of production bugs (mismatched `.tag()` values selecting wrong tabs after refactors). This is a rare example of Apple upgrading an API's *type system*, not just its aesthetics — and it is reason enough to migrate off `.tabItem` even if you don't ship iOS 26.

For new code, the rules are simple: pick the container from the decision tree in §1, match sheet vs push to the user's mental model in §7, respect HIG's modality rule ("minimize it"), and re-audit your toolbar/background customizations when recompiling for iOS 26. For legacy UIKit code, the mapping tables in §2.7, §3.7, and §4.5 let you migrate patterns one at a time without rewriting.