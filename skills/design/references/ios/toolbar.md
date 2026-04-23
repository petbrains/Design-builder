---
name: toolbar
description: SwiftUI toolbar reference (every ToolbarItemPlacement, iOS 26 Liquid Glass tab/bottom bars)
platform: ios
---

# SwiftUI Toolbar Reference — iOS 18 & iOS 26 (Liquid Glass)

A practical, daily-use reference for SwiftUI's toolbar system, covering every `ToolbarItemPlacement`, the iOS 26 Liquid Glass redesign, tab bars, bottom bars, keyboard toolbars, macOS specifics, and UIKit equivalents. All code samples compile; iOS 26-only APIs are gated with `#available`.

---

## Table of contents

1. [ToolbarItem placements — exhaustive reference](#1-toolbaritem-placements--exhaustive-reference)
2. [Semantic placements and iOS 26 Liquid Glass](#2-semantic-placements-and-ios-26-liquid-glass)
3. [ToolbarItemGroup, ToolbarSpacer and grouping](#3-toolbaritemgroup-toolbarspacer-and-grouping)
4. [Navigation bar specifics — titles, subtitles, back buttons, search](#4-navigation-bar-specifics--titles-subtitles-back-buttons-search)
5. [Tab bar customization (iOS 18 Tab API, iOS 26 minimize)](#5-tab-bar-customization-ios-18-tab-api-ios-26-minimize)
6. [Bottom bar vs tab bar — when each is correct](#6-bottom-bar-vs-tab-bar--when-each-is-correct)
7. [Keyboard toolbar and FocusState](#7-keyboard-toolbar-and-focusstate)
8. [macOS differences — customization, roles, window style](#8-macos-differences--customization-roles-window-style)
9. [Anti-patterns and best practices](#9-anti-patterns-and-best-practices)
10. [Appendix — version cheat sheet, sources](#10-appendix)

---

## 1. ToolbarItem placements — exhaustive reference

`ToolbarItemPlacement` is a **struct** (not an enum) introduced in iOS 14 / macOS 11. Placements fall into two buckets:

- **Semantic** — describe *intent* (`.primaryAction`, `.confirmationAction`, `.cancellationAction`, `.destructiveAction`, `.secondaryAction`, `.principal`, `.navigation`, `.status`, `.automatic`). SwiftUI picks the correct physical location per-platform, size class, role, and surrounding UI.
- **Positional** — describe a *specific location* (`.topBarLeading`, `.topBarTrailing`, `.navigationBarLeading`, `.navigationBarTrailing`, `.bottomBar`, `.keyboard`, `.bottomOrnament`).

**Rule of thumb:** prefer semantic placements. They adapt to RTL layouts, Mac window toolbars, visionOS ornaments, and Liquid Glass grouping automatically. Use positional placements only for iOS/iPadOS-only surfaces where you need precise control.

### 1.1 Visual placement diagram — iPhone (iOS 18, inline title)

```
┌───────────────────────────────────────────────┐
│ [topBarLeading /        ] [principal] [topBarTrailing /   ]│
│  navigationBarLeading /               navigationBarTrailing /
│  cancellationAction /                 primaryAction /
│  navigation            ]              confirmationAction /
│                                       destructiveAction   ]
│                                               │
│                                               │
│                  content                      │
│                                               │
│                                               │
│ [bottomBar ...]      [status]        [...]    │  ← bottom toolbar
└───────────────────────────────────────────────┘
                 ↑
         [keyboard] ← accessory bar above the software keyboard
```

### 1.2 Visual placement diagram — iPhone (iOS 26 Liquid Glass)

```
┌───────────────────────────────────────────────┐
│ ⟨topBarLeading⟩            ⟨topBarTrailing⟩  │   ← floating glass capsules
│                                               │
│  .largeTitle                                  │
│  .largeSubtitle (secondary tone)              │
│                                               │
│                  content                      │
│                                               │
│                                               │
│  ⟨DefaultToolbarItem(.search)⟩  ⟨bottomBar⟩  │   ← floating glass
│   └─capsule─┘  └─spacer─┘  └──capsule──┘      │
└───────────────────────────────────────────────┘
```

### 1.3 Visual placement diagram — iPad (iPadOS 18, `.toolbarRole(.editor)`)

```
┌───────────────────────────────────────────────────────────────┐
│ ← Back │ Title │ [primary group]   [secondary group …] [⋯]    │
├───────────────────────────────────────────────────────────────┤
│                          content                              │
└───────────────────────────────────────────────────────────────┘
```

### 1.4 Per-placement reference

#### `.automatic` — iOS 14+ / macOS 11+ / visionOS 1+
System-chosen location. iPhone: trailing navigation bar. iPad: trailing nav bar (center with `.editor` role). Mac: window toolbar. visionOS: ornament.

```swift
.toolbar {
    ToolbarItem(placement: .automatic) { Button("Add") { } }
}
```

#### `.principal` — iOS 14+ / macOS 11+
Center of the navigation bar (replaces the title slot). Requires `.navigationBarTitleDisplayMode(.inline)` to behave predictably; a `.large` title overrides it. UIKit equivalent: `UINavigationItem.titleView`.

```swift
.toolbar {
    ToolbarItem(placement: .principal) {
        Picker("Mode", selection: $mode) {
            Text("Edit").tag(Mode.edit)
            Text("Preview").tag(Mode.preview)
        }
        .pickerStyle(.segmented)
    }
}
.navigationBarTitleDisplayMode(.inline)
```

#### `.navigation` — iOS 14+ / macOS 11+
Where navigation controls live (typically leading on iOS; pushed to trailing if a system Back button already occupies the slot). UIKit: `UINavigationItem.leftBarButtonItem` / `backBarButtonItem`.

#### `.navigationBarLeading` / `.navigationBarTrailing` — iOS 14+
**Not formally deprecated** in the iOS 26 SDK, but superseded in spirit by `.topBarLeading` / `.topBarTrailing` (iOS 17+). Both still compile and behave identically on iOS/iPadOS. Not available on tvOS or watchOS. UIKit: `UINavigationItem.leftBarButtonItem(s)` / `rightBarButtonItem(s)`.

#### `.topBarLeading` / `.topBarTrailing` — iOS 17+ / macOS 14+ / visionOS 1+
Preferred, platform-neutral replacements for `.navigationBarLeading` / `.navigationBarTrailing`. In compact size classes, **one item max per side** — extras collapse into a `…` overflow menu.

```swift
.toolbar {
    ToolbarItem(placement: .topBarLeading)  { Button("Cancel", role: .cancel) { dismiss() } }
    ToolbarItem(placement: .topBarTrailing) { Button("Save") { save() } }
}
```

#### `.primaryAction` — iOS 14+
The most important action on screen. iPhone/iPad: trailing navigation bar. iPad with `.toolbarRole(.editor)`: visible center slot, never collapses. Mac: leading edge of window toolbar. visionOS: leading ornament. **Liquid Glass (iOS 26):** automatically promoted to `.glassProminent` tinted capsule. UIKit equivalent: `UIBarButtonItem(systemItem: .done)` on the right, bold style.

#### `.secondaryAction` — iOS/iPadOS 16+ / macOS 13+
Items that can collapse into an overflow `…` menu on iPad and be dragged out by the user in customizable toolbars. On iPhone, behaves similarly to `.automatic`.

#### `.confirmationAction` — iOS 14+
Confirm action for a modal (Done/Save/Send). Renders on the trailing edge of a modal's navigation bar, bold. On macOS it's the default push-button of a sheet. **Only reliably appears inside modal sheets / `fullScreenCover`**; outside modals, SwiftUI may drop it. UIKit: `UIBarButtonItem(barButtonSystemItem: .done)` or `.save`.

```swift
.toolbar {
    ToolbarItem(placement: .confirmationAction) {
        Button("Save") { save(); dismiss() }
    }
    ToolbarItem(placement: .cancellationAction) {
        Button("Cancel", role: .cancel) { dismiss() }
    }
}
```

**Liquid Glass:** automatically adopts `.glassProminent`.

#### `.cancellationAction` — iOS 14+
Cancel action for a modal. Leading edge of the modal navigation bar; trailing end on Mac (paired with confirm). Same modal-only caveat as `.confirmationAction`. UIKit: `UIBarButtonItem(barButtonSystemItem: .cancel)`.

#### `.destructiveAction` — iOS 14+
Destructive action inside a modal. Placed near `.confirmationAction`, red-tinted. UIKit: `UIBarButtonItem(barButtonSystemItem: .trash)` or `UIAlertAction(.destructive)`.

#### `.bottomBar` — iOS 14+ / iPadOS 14+ / visionOS 1+ (NOT macOS, tvOS, watchOS)
Bottom toolbar above the home indicator. Single item is centered; multiple lay out left-to-right. **iOS 17 changed default alignment** to leading — use `Spacer()` inside a `ToolbarItemGroup(placement: .bottomBar)` to control it. UIKit: `UIToolbar` via `UINavigationController.isToolbarHidden = false` plus `UIViewController.toolbarItems`.

```swift
.toolbar {
    ToolbarItemGroup(placement: .bottomBar) {
        Button("Edit") { }
        Spacer()
        Button("Share", systemImage: "square.and.arrow.up") { }
    }
}
```

**iOS 26:** bottom bar becomes floating glass capsules. When used alongside the new `TabView`, `.bottomBar` may be obscured by the floating tab bar — prefer `.tabViewBottomAccessory` (see §5).

#### `.status` — iOS 14+ / macOS 11+
Read-only state indicator (e.g., "Updated 5 min ago"). iPhone/iPad: center of the bottom toolbar — if a `.bottomBar` item is also present, the `.bottomBar` item moves leading and `.status` takes center. Mac: centered in window toolbar.

```swift
.toolbar {
    ToolbarItem(placement: .status) {
        Text("Updated 5 min ago").font(.caption2).foregroundStyle(.secondary)
    }
}
```

#### `.keyboard` — iOS 15+ / macOS 12+ (Touch Bar)
Appears above the software keyboard when a text field is first-responder. See §7 for patterns. UIKit: `UITextField.inputAccessoryView`.

#### `.bottomOrnament` — visionOS 1+
Floating bar attached outside a visionOS window in 3D space. Does not obscure the window. UIKit on visionOS: `UIHostingOrnament` / `UIViewController.ornaments`.

```swift
private var placement: ToolbarItemPlacement {
    #if os(visionOS)
    .bottomOrnament
    #else
    .primaryAction
    #endif
}
```

#### iOS 26 additions — `.title`, `.subtitle`, `.largeTitle`, `.largeSubtitle`
New title/subtitle slots that participate in Liquid Glass title morphing. `.largeTitle` requires `.navigationTitle(_:)` to be set (even to an empty string) or the placement is invisible. See §4 for the preferred `.navigationTitle` / `.navigationSubtitle` modifiers, which drive these slots implicitly.

### 1.5 SwiftUI → UIKit placement table

| SwiftUI placement | Availability | iOS location | UIKit equivalent |
|---|---|---|---|
| `.automatic` | iOS 14+ | Varies by platform | system default |
| `.principal` | iOS 14+ | Nav bar center | `UINavigationItem.titleView` |
| `.navigation` | iOS 14+ | Nav bar leading | `UINavigationItem.leftBarButtonItem` / `backBarButtonItem` |
| `.navigationBarLeading` | iOS 14+ (superseded) | Nav bar leading | `UINavigationItem.leftBarButtonItem(s)` |
| `.navigationBarTrailing` | iOS 14+ (superseded) | Nav bar trailing | `UINavigationItem.rightBarButtonItem(s)` |
| `.topBarLeading` | iOS 17+ | Nav bar leading | `UINavigationItem.leftBarButtonItem(s)` |
| `.topBarTrailing` | iOS 17+ | Nav bar trailing | `UINavigationItem.rightBarButtonItem(s)` |
| `.primaryAction` | iOS 14+ | Nav bar trailing | `UIBarButtonItem(systemItem: .done)` |
| `.secondaryAction` | iOS 16+ | Overflow / customization | `UIBarButtonItem` in overflow |
| `.confirmationAction` | iOS 14+ | Modal trailing, bold | `UIBarButtonSystemItem.done` / `.save` |
| `.cancellationAction` | iOS 14+ | Modal leading | `UIBarButtonSystemItem.cancel` |
| `.destructiveAction` | iOS 14+ | Near confirm, red | `UIBarButtonSystemItem.trash` |
| `.bottomBar` | iOS 14+ | Bottom toolbar | `UIToolbar` + `toolbarItems` |
| `.status` | iOS 14+ | Bottom center | Centered `UIBarButtonItem` with custom view |
| `.keyboard` | iOS 15+ | Above keyboard | `UIResponder.inputAccessoryView` |
| `.bottomOrnament` | visionOS 1+ | Ornament below window | `UIHostingOrnament` |
| `.title` / `.subtitle` | iOS 26+ | Title slot | `UINavigationItem.title` / `.subtitle` |
| `.largeTitle` / `.largeSubtitle` | iOS 26+ | Large title area | `prefersLargeTitles` + custom title view |

### 1.6 Common patterns

**Detail view with Save / Cancel (modal):**

```swift
struct EditItemView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var name = ""

    var body: some View {
        NavigationStack {
            Form {
                TextField("Name", text: $name)
            }
            .navigationTitle("Edit Item")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel", role: .cancel) { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") { save(); dismiss() }
                        .disabled(name.isEmpty)
                }
            }
        }
    }

    private func save() { /* persist */ }
}
```

UIKit equivalent:

```swift
navigationItem.leftBarButtonItem  = UIBarButtonItem(
    barButtonSystemItem: .cancel, target: self, action: #selector(cancel))
navigationItem.rightBarButtonItem = UIBarButtonItem(
    barButtonSystemItem: .save,   target: self, action: #selector(save))
navigationItem.rightBarButtonItem?.isEnabled = !name.isEmpty
```

**List view with Add / Edit:**

```swift
struct ItemListView: View {
    @State private var items: [Item] = []
    @State private var editMode: EditMode = .inactive

    var body: some View {
        NavigationStack {
            List($items) { $item in
                Text(item.title)
            }
            .navigationTitle("Items")
            .environment(\.editMode, $editMode)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) { EditButton() }
                ToolbarItem(placement: .primaryAction) {
                    Button("Add", systemImage: "plus") { items.append(.new) }
                }
            }
        }
    }
}
```

---

## 2. Semantic placements and iOS 26 Liquid Glass

### 2.1 What changed at WWDC 2025

From WWDC25 session 323 *"Build a SwiftUI app with the new design"*:

> "Toolbar items are placed on a Liquid Glass surface that floats above your app's content and automatically adapts to what's beneath it. Toolbar items are automatically grouped."

| Concern | iOS 18 and earlier | iOS 26 / iPadOS 26 / macOS 26 |
|---|---|---|
| Bar background | Opaque or `Material` blur, edge-pinned | Floating Liquid Glass capsules |
| Item shape | No visible button shape | Each button gets a glass capsule |
| Grouping | Manual via `ToolbarItemGroup` | **Automatic** — same-placement items merge into one capsule |
| Separator | None | New `ToolbarSpacer(.fixed | .flexible)` |
| Icon color | Often multicolor | **Monochrome by default** in toolbars |
| Scroll edge | `.toolbarBackground(.visible, …)` | Automatic *scroll edge effect*; tunable via `.scrollEdgeEffectStyle` |
| Content under bar | Manual `safeAreaInset` tricks | `.backgroundExtensionEffect()` mirrors/blurs under floating bars |
| Custom bars | `safeAreaInset(edge:)` | New `.safeAreaBar(edge:alignment:spacing:content:)` |
| Search field (iPhone) | Top of nav bar | Floating capsule at **bottom** (one-handed reach) |
| Search field (iPad/Mac) | Top nav or sidebar | Top trailing floating capsule |

**Crucially, recompiling against the iOS 26 SDK adopts the new look automatically** — no migration is strictly required, but you will want to audit custom bar backgrounds, insert `ToolbarSpacer`s where items should be visually separated, and migrate `.bottomBar` usage inside TabViews to `.tabViewBottomAccessory`.

### 2.2 Semantic placements drive *styling* in iOS 26

This is the key insight. In iOS 18 and earlier, `.topBarTrailing` and `.confirmationAction` were visually identical on a modal. **In iOS 26, `.confirmationAction` automatically adopts `.glassProminent`** (filled tinted capsule), while `.topBarTrailing` does not. Semantic placements now communicate both position *and* visual emphasis. Prefer them over positional placements.

### 2.3 Semantic placement → visual position across platforms

| Placement | iPhone (iOS 26) | iPad (iPadOS 26) | Mac (macOS 26) | visionOS 26 |
|---|---|---|---|---|
| `.automatic` | Nav bar trailing capsule | Nav bar trailing | Window toolbar trailing | Ornament |
| `.primaryAction` | Top trailing, bold | Top trailing | Window toolbar leading | Leading ornament |
| `.confirmationAction` | Modal trailing, **glassProminent** | Same | Sheet trailing | Same |
| `.cancellationAction` | Modal leading | Same | Sheet leading/trailing | Same |
| `.navigation` | System back area | Same | Window toolbar leading | Window controls |
| `.principal` | Nav bar center | Same | Window toolbar center | Ornament center |
| `.bottomBar` | Floating glass capsule | Bottom bar (uncommon) | n/a (limited) | Avoid; use `.bottomOrnament` |
| `.keyboard` | Above soft keyboard | Above soft keyboard | Touch Bar | n/a |
| `.title` / `.subtitle` | Title slot | Same | Window title area | n/a |
| `.largeTitle` | Large title area | Same | Limited | n/a |
| Search via `.searchable()` | **Bottom floating** | Top trailing | Top trailing | Top |

### 2.4 Scroll edge effect (iOS 26)

Per WWDC25 session 323:

> "An automatic scroll edge effect keeps controls legible. It is a subtle blur and fade effect applied to content under system toolbars. If your app has any extra backgrounds or darkening effects behind the bar items, make sure to remove them, as these will interfere with the effect."

```swift
// Sharp top edge (dense calendar-style UI)
ScrollView { /* … */ }
    .scrollEdgeEffectStyle(.hard, for: .top)     // iOS 26+

// Soft (default) — gradual blur/fade
ScrollView { /* … */ }
    .scrollEdgeEffectStyle(.soft, for: .top)
```

`ScrollEdgeEffectStyle` cases: `.automatic`, `.hard`, `.soft`. No color or material option.

### 2.5 Toolbar background modifiers

```swift
// Existing (iOS 16+) — still valid
.toolbarBackground(Color.indigo, for: .navigationBar)
.toolbarBackground(.visible,     for: .navigationBar)
.toolbarColorScheme(.dark,       for: .navigationBar)

// New in iOS 26
.toolbarBackgroundVisibility(.visible, for: .navigationBar, .tabBar, .bottomBar)
```

**iOS 26 nuances:**
- Hard-coding `toolbarBackground(.visible, …)` with a solid color fights the new design and disables the scroll edge effect blur. WWDC25 guidance: **remove** custom bar backgrounds you added in iOS 15–18.
- `toolbarColorScheme` only takes effect *while the background is visible*.
- `toolbarBackground` / `toolbarColorScheme` applied to `TabView` has no effect on iOS 26 — apply to per-tab content.

### 2.6 `sharedBackgroundVisibility` — opt out of the glass capsule

Per Apple docs:

> "In certain contexts, such as the navigation bar on iOS and the window toolbar on macOS, toolbar items will be given a glass background effect that is shared with other items in the same logical grouping."

Apply to a single item to render it as a standalone custom view (avatar, progress ring) without the shared glass pill:

```swift
.toolbar {
    ToolbarItem(placement: .topBarTrailing) {
        AvatarView(user: currentUser)
    }
    .sharedBackgroundVisibility(.hidden)    // iOS 26+
}
```

### 2.7 `backgroundExtensionEffect` — mirror content under floating bars

```swift
NavigationSplitView {
    Sidebar()
} detail: {
    Image(.heroBlossom)
        .resizable()
        .scaledToFill()
        .backgroundExtensionEffect()       // iOS 26+
}
```

### 2.8 Liquid Glass button styles

```swift
extension ButtonStyle where Self == GlassButtonStyle {   // iOS 26+
    static var glass: Self { get }
    static var glassProminent: Self { get }
}
```

| Style | Visual | Use for |
|---|---|---|
| `.buttonStyle(.glass)` | Translucent capsule | Secondary buttons in non-toolbar contexts |
| `.buttonStyle(.glassProminent)` | Filled tinted capsule | Call-to-action; auto-applied to `.confirmationAction` |

```swift
Button("Save") { }
    .buttonStyle(.glassProminent)
    .tint(.blue)
```

**Avoid double-glassing**: don't add `.buttonStyle(.glass)` to items already inside a system toolbar, and don't add `.glassEffect()` to a `.glassProminent` button.

---

## 3. ToolbarItemGroup, ToolbarSpacer, and grouping

### 3.1 `ToolbarItemGroup` (iOS 14+)

```swift
ToolbarItemGroup(placement: ToolbarItemPlacement = .automatic,
                 @ViewBuilder content: () -> Content)
```

Use when multiple actions in the same placement should visually read as one cluster. In iOS 26, all members of one group share **one glass capsule**; the system owns inter-item padding (you can't insert `Spacer()` to push items apart inside the glass surface, except on legacy `.bottomBar`).

```swift
.toolbar {
    ToolbarItem(placement: .cancellationAction) {
        Button("Cancel", systemImage: "xmark") { }
    }

    // Two related actions share ONE glass capsule
    ToolbarItemGroup(placement: .primaryAction) {
        Button("Draw",  systemImage: "pencil") { }
        Button("Erase", systemImage: "eraser") { }
    }

    ToolbarItem(placement: .confirmationAction) {
        Button("Save", systemImage: "checkmark") { }
    }
}
```

**Legacy bottom-bar trick still works** — `Spacer()` inside `ToolbarItemGroup(placement: .bottomBar)` is honored:

```swift
ToolbarItemGroup(placement: .bottomBar) {
    Button("First")  { }
    Spacer()
    Button("Second") { }
}
```

### 3.2 `ToolbarSpacer` (iOS 26+)

A `ToolbarContent`-level spacer that lives inside `.toolbar { }`. It splits the shared glass capsule into multiple capsules, or pushes items apart on the bar.

```swift
@available(iOS 26.0, macOS 26.0, *)
struct ToolbarSpacer: ToolbarContent {
    init()
    init(_ sizing: SpacerSizing)
    init(_ sizing: SpacerSizing, placement: ToolbarItemPlacement)
}

enum SpacerSizing {
    case fixed       // small system-determined gap; breaks one capsule into two
    case flexible    // expands like Spacer(); pushes items to opposite ends
}
```

| Sizing | Visual effect | Use for |
|---|---|---|
| `.fixed` | Small gap; breaks one capsule into two | Unrelated actions in the same placement (Delete + Add) that should stay close but not *attached* |
| `.flexible` | Expands to fill available width | Pushing groups to opposite ends (Mail-style filter + compose) |

```swift
// Splitting unrelated items so they render as separate capsules
.toolbar {
    ToolbarItem {
        Button("Delete", systemImage: "trash", role: .destructive) { }
    }
    ToolbarSpacer(.fixed)
    ToolbarItem {
        Button("Add", systemImage: "plus") { }
    }
}

// Mail-style flexible split
.toolbar {
    ToolbarItem(placement: .bottomBar) { FilterMenu() }
    ToolbarSpacer(.flexible, placement: .bottomBar)
    DefaultToolbarItem(kind: .search, placement: .bottomBar)
    ToolbarItem(placement: .bottomBar) { ComposeButton() }
}
```

UIKit equivalents: `UIBarButtonItem.fixedSpace(_:)`, `UIBarButtonItem.flexibleSpace()`. In iOS 26 UIKit, `UIBarButtonItemGroup` drives the auto-grouping behavior.

### 3.3 `DefaultToolbarItem` (iOS 26+)

Inserts a system-provided toolbar item (currently `.search`) at a specific placement.

```swift
@available(iOS 26.0, macOS 26.0, *)
struct DefaultToolbarItem: ToolbarContent {
    init(kind: Kind, placement: ToolbarItemPlacement)
    enum Kind { case search }
}
```

```swift
.toolbar {
    if #available(iOS 26.0, *) {
        DefaultToolbarItem(kind: .search, placement: .bottomBar)
        ToolbarSpacer(.flexible, placement: .bottomBar)
    }
    ToolbarItem(placement: .bottomBar) { NewNoteButton() }
}
.searchable(text: $searchText)
```

### 3.4 Grouping semantics summary

| Goal | API |
|---|---|
| Visually one cluster, shared capsule | `ToolbarItemGroup` |
| Two capsules, close together | `ToolbarSpacer(.fixed)` between `ToolbarItem`s |
| Two capsules, pushed to opposite ends | `ToolbarSpacer(.flexible)` |
| Remove shared capsule from one item | `.sharedBackgroundVisibility(.hidden)` on `ToolbarItem` |
| Include system search between items | `DefaultToolbarItem(kind: .search, placement:)` |

---

## 4. Navigation bar specifics — titles, subtitles, back buttons, search

### 4.1 `navigationTitle(_:)` — all variants

| Variant | Signature | Availability |
|---|---|---|
| LocalizedStringKey | `func navigationTitle(_ titleKey: LocalizedStringKey) -> some View` | iOS 14+ |
| String | `func navigationTitle<S: StringProtocol>(_ title: S) -> some View` | iOS 14+ |
| `Text` | `func navigationTitle(_ title: Text) -> some View` | iOS 14+ |
| `Binding<String>` (editable) | `func navigationTitle(_ title: Binding<String>) -> some View` | **iOS 16+**, macOS 13+ |

The binding variant adds a chevron disclosure next to the title, opening a system-provided **Rename** menu. Works only with `.inline` display mode.

```swift
struct DocView: View {
    @State private var title = "Untitled"
    var body: some View {
        NavigationStack {
            TextEditor(text: .constant(""))
                .navigationTitle($title)
                .navigationBarTitleDisplayMode(.inline)
                .toolbarRole(.editor)   // iPad: leading-aligned title
        }
    }
}
```

> **Note:** Font customization on `navigationTitle` is *not* supported in pure SwiftUI — the `Text`-accepting variant ignores font/weight modifiers. Workarounds: `UINavigationBar.appearance()` proxy, or `ToolbarItem(placement: .principal) { … }` for a fully custom title view.

### 4.2 Title display modes

```swift
// iOS 14+
.navigationBarTitleDisplayMode(.automatic)    // inherits from previous
.navigationBarTitleDisplayMode(.inline)       // small centered
.navigationBarTitleDisplayMode(.large)        // large, collapses on scroll

// iOS 17+
.toolbarTitleDisplayMode(.inlineLarge)        // large-looking but inline
```

**HIG guidance:** use `.large` at the root of a hierarchy to introduce content (Settings root, Mail inbox, Music library). Switch to `.inline` after drilling in, on modals, and on forms. Leave title empty if redundant with prominent content.

**iOS 26 constraint:** a large title can no longer be placed inline with toolbar actions simultaneously — when large is used, it is always displayed below the toolbar row (per Apple Forums 798497, confirmed by Apple engineer).

### 4.3 `navigationSubtitle(_:)` — iOS 26+ / macOS 11+

```swift
func navigationSubtitle<S: StringProtocol>(_ subtitle: S) -> some View
func navigationSubtitle(_ subtitleKey: LocalizedStringKey) -> some View
func navigationSubtitle(_ subtitle: Text) -> some View
```

Renders a smaller line directly below the navigation title, same horizontal alignment as the title. Must be used alongside `.navigationTitle` — not instead of it. macOS SwiftUI has had this since macOS 11 (maps to `NSWindow.subtitle`); iOS/iPadOS 26 adds cross-platform parity. UIKit 26 exposes an equivalent `UINavigationItem.subtitle`.

```swift
NavigationStack {
    NoteBody(note: note)
        .navigationTitle(note.title)
        .navigationSubtitle("Edited 2 min ago")    // iOS 26+
}
```

For backwards compatibility:

```swift
private extension View {
    @ViewBuilder
    func compatSubtitle(_ s: String) -> some View {
        if #available(iOS 26.0, macOS 11.0, *) {
            self.navigationSubtitle(s)
        } else {
            self
        }
    }
}
```

### 4.4 Back button customization

**Hide the default back button:**

```swift
.navigationBarBackButtonHidden(true)
```

**Custom back button via toolbar** (disables the interactive swipe-back gesture):

```swift
struct DetailView: View {
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        Content()
            .navigationBarBackButtonHidden(true)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button {
                        dismiss()
                    } label: {
                        Label("Back", systemImage: "chevron.backward")
                    }
                }
            }
    }
}
```

**`.toolbarRole(.editor)` — minimal back button on iPad / Mac** (iOS 16+):

```swift
DetailView().toolbarRole(.editor)
```

`ToolbarRole` cases: `.automatic`, `.browser`, `.editor`, `.navigationStack`. On iPad/Mac, `.editor` hides the previous view's title next to the back chevron — the SwiftUI analog of `UINavigationItem.backButtonDisplayMode = .minimal`. Does **not** change iPhone back buttons.

**UIKit back-button equivalents:**

| Goal | UIKit |
|---|---|
| Hide back button | `navigationItem.hidesBackButton = true` |
| Custom leading item | `navigationItem.leftBarButtonItem = …` |
| Change pushed-screen back label | `previousVC.navigationItem.backButtonTitle = "Prev"` |
| Full back replacement | `previousVC.navigationItem.backBarButtonItem = …` |
| Chevron-only | `navigationItem.backButtonDisplayMode = .minimal` (iOS 14+) |

### 4.5 `toolbarTitleMenu { … }` — tap the title for a menu (iOS 16+)

```swift
.toolbarTitleMenu {
    RenameButton()                                         // works with $title binding
    Button("Duplicate", systemImage: "plus.square.on.square") { }
    Button("Move…", systemImage: "folder") { }
    Divider()
    Button("Delete", systemImage: "trash", role: .destructive) { }
}
```

Only appears when title display mode is `.inline`. `RenameButton()` is provided so your custom menu can retain the system rename action.

### 4.6 Search integration — `searchable`

```swift
.searchable(
    text: $query,
    placement: .navigationBarDrawer(displayMode: .always),
    prompt: "Search countries"
)
```

`SearchFieldPlacement` cases (iOS 15+): `.automatic`, `.navigationBarDrawer(displayMode:)`, `.toolbar`, `.sidebar` (iOS 16+).

Environment support:

```swift
@Environment(\.isSearching)   private var isSearching
@Environment(\.dismissSearch) private var dismissSearch
```

Scopes and suggestions:

```swift
.searchable(text: $q)
.searchScopes($scope) {
    Text("All").tag(Scope.all)
    Text("Albums").tag(Scope.albums)
}
.searchSuggestions {
    Text("Apple").searchCompletion("apple")
    Text("Orange").searchCompletion("orange")
}
```

### 4.7 iOS 26 search changes

On iPhone, `.searchable()` attached to a `NavigationStack` / `NavigationSplitView` now defaults to a **floating Liquid Glass capsule at the bottom** for one-handed reach. On iPad, it floats at the top trailing. Force legacy iPad sidebar placement with `.searchable(text:, placement: .sidebar)`.

**Dedicated search tab** (iOS 26+):

```swift
TabView {
    Tab("Library", systemImage: "books.vertical") { LibraryView() }
    Tab("Store",   systemImage: "bag")             { StoreView() }
    Tab(role: .search) {
        NavigationStack { SearchView() }
            .searchable(text: $query)
    }
}
```

**Minimize search when not primary** (iOS 26+):

```swift
.searchable(text: $query)
.searchToolbarBehavior(.minimize)
```

### 4.8 Navigation bar SwiftUI → UIKit cross-reference

| Concern | SwiftUI | UIKit equivalent |
|---|---|---|
| Title | `.navigationTitle("X")` | `navigationItem.title = "X"` |
| Editable title | `.navigationTitle($title)` | No direct equivalent |
| Custom title view | `ToolbarItem(.principal) { … }` | `navigationItem.titleView = …` |
| Subtitle | `.navigationSubtitle("Y")` (iOS 26) | `UINavigationItem.subtitle` (iOS 26) / `NSWindow.subtitle` |
| Large titles | `.navigationBarTitleDisplayMode(.large)` | `navigationBar.prefersLargeTitles = true` + `navigationItem.largeTitleDisplayMode` |
| Inline large (iOS 17+) | `.toolbarTitleDisplayMode(.inlineLarge)` | No exact UIKit equivalent |
| Background color | `.toolbarBackground(c, for: .navigationBar)` | `UINavigationBarAppearance.backgroundColor` |
| Color scheme | `.toolbarColorScheme(.dark, for: .navigationBar)` | `UINavigationBarAppearance.titleTextAttributes` + status bar |
| Hide back | `.navigationBarBackButtonHidden(true)` | `navigationItem.hidesBackButton = true` |
| Minimal back | `.toolbarRole(.editor)` | `navigationItem.backButtonDisplayMode = .minimal` |
| Title menu | `.toolbarTitleMenu { … }` | `navigationItem.titleMenuProvider = …` |
| Search | `.searchable(text:)` | `navigationItem.searchController = UISearchController(...)` |
| Search always visible | `.searchable(..., placement: .navigationBarDrawer(displayMode: .always))` | `navigationItem.hidesSearchBarWhenScrolling = false` |

---

## 5. Tab bar customization (iOS 18 Tab API, iOS 26 minimize)

### 5.1 The new `Tab` type — iOS 18+

iOS 18 replaced implicit `.tabItem`-modified views with a type-safe, first-class `Tab` value.

```swift
TabView {
    Tab("Home",     systemImage: "house")          { HomeView() }
    Tab("Library",  systemImage: "books.vertical") { LibraryView() }
    Tab("Settings", systemImage: "gear")           { SettingsView() }
}
```

Initializer overloads include `Tab(_:systemImage:content:)`, `Tab(_:image:content:)`, `Tab(content:label:)`, `Tab(_:systemImage:value:content:)`, and `Tab(role:content:)`.

**Selection-based tabs:**

```swift
enum AppTab: Hashable { case home, library, search, settings }

struct Root: View {
    @State private var selection: AppTab = .home

    var body: some View {
        TabView(selection: $selection) {
            Tab("Home",    systemImage: "house",          value: AppTab.home)    { HomeView() }
            Tab("Library", systemImage: "books.vertical", value: AppTab.library) { LibraryView() }
            Tab("Settings", systemImage: "gear",          value: AppTab.settings) { SettingsView() }
            Tab(value: AppTab.search, role: .search) {
                NavigationStack { SearchView() }
            }
        }
    }
}
```

### 5.2 Legacy `.tabItem` — still works

```swift
TabView(selection: $selection) {
    HomeView()
        .tabItem { Label("Home", systemImage: "house") }
        .tag(AppTab.home)
}
```

| Feature | Legacy `.tabItem` | New `Tab` |
|---|---|---|
| Identity | `.tag(…)` | `value:` parameter |
| Type safety | Runtime | Compile-time |
| Sidebar grouping | No | `TabSection` |
| Roles (`.search`) | No | Yes |
| iOS 26 minimize | **No** | **Yes** |
| iOS 26 bottom accessory | **No** | **Yes** |

**Migrate to `Tab` if you support iOS 18+** — mixing legacy `.tabItem` with new `Tab` disables iOS 26 features.

### 5.3 `TabSection` and the search role

```swift
TabView {
    Tab("Watch Now", systemImage: "play")           { WatchNowView() }
    Tab("Library",   systemImage: "books.vertical") { LibraryView() }

    TabSection("Collections") {
        Tab("Cinematic", systemImage: "film") { CinematicView() }
        Tab("Forest",    systemImage: "leaf") { ForestView() }
    }
    .sectionActions {
        Button("New Collection", systemImage: "plus") { }
    }

    Tab(role: .search) { SearchView() }
}
.tabViewStyle(.sidebarAdaptable)
```

Sections render inline in the floating tab bar and as labeled sections in the sidebar. `Tab(role: .search)` gets a default magnifying-glass icon, localized title, trailing-edge placement, and on iOS 26 transforms into a search field when selected.

### 5.4 TabViewStyle options

| Style | Platforms | Behavior |
|---|---|---|
| `.automatic` | all | Default; floating glass on iOS 26 |
| `.sidebarAdaptable` (iOS 18+) | iPad/Mac/tvOS | Sidebar ↔ tab bar morph on iPad; always sidebar on Mac |
| `.tabBarOnly` (iOS 18+) | iPad | Force tab bar |
| `.sidebar` | iPad/macOS | Sidebar |
| `.page` / `PageTabViewStyle` | iOS/tvOS/watchOS | Swipeable pages |
| `.verticalPage` | watchOS | Vertical pages |
| `.grouped` | macOS | Segmented-control in toolbar |

### 5.5 Badges

```swift
Tab("Inbox",  systemImage: "tray") { InboxView() }
    .badge(42)

Tab("Alerts", systemImage: "bell") { AlertsView() }
    .badge("!")
```

### 5.6 Customization — `tabViewCustomization`

Users can tap Edit in the sidebar to reorder, hide, and drag tabs. Required: `@AppStorage` for a `TabViewCustomization`, `.tabViewCustomization($customization)` on `TabView`, `.customizationID("…")` on every customizable tab and section, and `.tabViewStyle(.sidebarAdaptable)`.

```swift
struct KaraokeApp: View {
    @AppStorage("tabViewCustomization") private var customization: TabViewCustomization

    var body: some View {
        TabView {
            Tab("Watch Now", systemImage: "play") { WatchNowView() }
                .customizationID("tab.watchNow")

            Tab("Library", systemImage: "books.vertical") { LibraryView() }
                .customizationID("tab.library")

            // Hidden by default; user can drag onto tab bar
            Tab("New Releases", systemImage: "sparkles") { NewReleasesView() }
                .customizationID("tab.newReleases")
                .defaultVisibility(.hidden, for: .tabBar)

            // Pinned — disable reordering
            Tab("Home", systemImage: "house") { HomeView() }
                .customizationID("tab.home")
                .customizationBehavior(.disabled, for: .sidebar, .tabBar)

            TabSection("Collections") {
                ForEach(Collection.all) { c in
                    Tab(c.name, systemImage: c.icon) { CollectionView(c) }
                        .customizationID("tab.collection.\(c.id)")
                }
            }
            .customizationID("tab.collections")
        }
        .tabViewStyle(.sidebarAdaptable)
        .tabViewCustomization($customization)
    }
}
```

`TabViewCustomization` conforms to `Codable` — `@AppStorage` serializes to JSON automatically.

### 5.7 iOS 26 Liquid Glass tab bar

**Auto-adoption:** recompile against iOS 26 SDK with the new `Tab` API and the tab bar becomes floating Liquid Glass automatically.

**`tabBarMinimizeBehavior(_:)`** — iOS 26+:

```swift
func tabBarMinimizeBehavior(_ behavior: TabBarMinimizeBehavior) -> some View
```

| Case | Behavior |
|---|---|
| `.automatic` | Platform default (stays visible on iOS/iPadOS) |
| `.never` | Never collapses |
| `.onScrollDown` | iPhone only; collapses on downward scroll |
| `.onScrollUp` | iPhone only; collapses on upward scroll |

```swift
TabView {
    Tab("Feed", systemImage: "list.bullet") {
        List(0..<100, id: \.self) { Text("Row \($0)") }
    }
    Tab(role: .search) { SearchView() }
}
.tabBarMinimizeBehavior(.onScrollDown)
```

**Known caveats** (Apple Forums, Xcode 26 betas):
- `.onScrollDown` may not trigger inside `NavigationStack(path:)` with a bound `NavigationPath`.
- Minimization requires the scroll container to be overlaid by the tab bar — a `VStack` that pushes content *above* the bar disables minimize.
- Legacy `.tabItem` syntax disables the minimize behavior entirely.

**`tabViewBottomAccessory { … }`** — iOS 26+. A custom view pinned above the tab bar, styled with a Liquid Glass capsule (Apple Music's "Now Playing" strip):

```swift
TabView {
    Tab("Library", systemImage: "books.vertical") { LibraryView() }
    Tab("Radio",   systemImage: "dot.radiowaves.left.and.right") { RadioView() }
    Tab(role: .search) { SearchView() }
}
.tabBarMinimizeBehavior(.onScrollDown)
.tabViewBottomAccessory {
    NowPlayingBar()
}

struct NowPlayingBar: View {
    @Environment(\.tabViewBottomAccessoryPlacement) var placement

    var body: some View {
        HStack {
            Image(systemName: "music.note")
            if placement == .expanded {
                Text("Song Title").lineLimit(1)
                Spacer()
                Button("", systemImage: "play.fill") { }
            }
        }
        .padding(.horizontal)
    }
}
```

Read `@Environment(\.tabViewBottomAccessoryPlacement)` inside the accessory to adapt layout for expanded vs. minimized states.

### 5.8 UIKit tab bar equivalents

**Legacy** (pre-iOS 18):

```swift
let home = HomeVC()
home.tabBarItem = UITabBarItem(title: "Home", image: UIImage(systemName: "house"), tag: 0)
home.tabBarItem.badgeValue = "3"

let search = SearchVC()
search.tabBarItem = UITabBarItem(tabBarSystemItem: .search, tag: 1)

tabBarController.viewControllers = [home, search]
```

**iOS 18 `UITab` / `UITabGroup` / `UISearchTab`:**

```swift
class RootTabController: UITabBarController {
    override func viewDidLoad() {
        super.viewDidLoad()
        tabs = [
            UITab(title: "Home", image: UIImage(systemName: "house"),
                  identifier: "tab.home") { _ in UIHostingController(rootView: HomeView()) },
            UITab(title: "Library", image: UIImage(systemName: "books.vertical"),
                  identifier: "tab.library") { _ in LibraryVC() },
            UITabGroup(title: "Collections", image: UIImage(systemName: "folder"),
                       identifier: "tab.collections",
                       children: [
                           UITab(title: "Cinematic", image: UIImage(systemName: "film"),
                                 identifier: "tab.cinematic") { _ in CinematicVC() }
                       ]) { _ in CollectionsHubVC() },
            UISearchTab { _ in SearchVC() }
        ]
        mode = .tabSidebar                           // iPad sidebar adaptive
        if #available(iOS 26, *) {
            tabBarMinimizeBehavior = .onScrollDown
        }
    }
}
```

### 5.9 SwiftUI → UIKit tab comparison

| SwiftUI | UIKit | Since |
|---|---|---|
| `TabView { … }` | `UITabBarController` | iOS 13 / 2 |
| `Tab("…", systemImage:) { … }` | `UITab(title:image:identifier:viewControllerProvider:)` | iOS 18 |
| `TabView(selection:)` | `UITabBarController.selectedViewController` | iOS 18 / always |
| `TabSection("…") { }` | `UITabGroup(...)` | iOS 18 |
| `Tab(role: .search)` | `UISearchTab` | iOS 18 |
| `.badge(_:)` | `UITabBarItem.badgeValue` / `.badgeColor` | iOS 15 / 2 |
| `.tabViewStyle(.sidebarAdaptable)` | `UITabBarController.mode = .tabSidebar` | iOS 18 |
| `.tabViewCustomization($c)` | `UITabBarController.customizableViewControllers` | iOS 18 / 3 |
| `.tabBarMinimizeBehavior(.onScrollDown)` | `UITabBarController.tabBarMinimizeBehavior` | iOS 26 |
| `.tabViewBottomAccessory { }` | `UITabBarController.bottomAccessory` | iOS 26 |
| `.toolbar(.hidden, for: .tabBar)` | `hidesBottomBarWhenPushed = true` | iOS 16 / 2 |

---

## 6. Bottom bar vs tab bar — when each is correct

### 6.1 The HIG rule

Apple's Human Interface Guidelines, unchanged from iOS 7 through iOS 26:

> **Tab bar** = persistent **top-level navigation** between the major sections of an app. *Not for actions.*
> **Toolbar / Bottom bar** = buttons that **perform actions on the current screen**. Contextual to the view.
> **"Tab bars and toolbars don't appear together in the same view."**

- Tab bar items are **destinations** (nouns: Home, Library, Search).
- Bottom bar items are **actions** (verbs: Add, Delete, Share).
- Target 3–5 tabs on iPhone; a few more acceptable on iPad.
- `.badge(_:)` communicates unobtrusive state changes on tabs.

### 6.2 Platform conventions

| Platform | Primary navigation | Notes |
|---|---|---|
| **iPhone (iOS)** | Tab bar at bottom | iOS 26: floating Liquid Glass |
| **iPad (iPadOS 18+)** | Tab bar (top-floating) or sidebar via `.sidebarAdaptable` | User-toggleable |
| **Mac (macOS)** | Sidebar (`NavigationSplitView`) or toolbar segmented control | Traditionally no tab bar; `.sidebarAdaptable` maps to sidebar |
| **watchOS** | `TabView` with `.verticalPage` | Pages, not persistent tabs |
| **tvOS** | Tab bar at top | Focus-driven |
| **visionOS** | Ornament tab bar | Auto minimizes when user looks away |

### 6.3 iOS 26 visual similarity caveat

Both the Liquid Glass tab bar and the Liquid Glass bottom toolbar now look visually similar — floating translucent capsules near the bottom. Apple's HIG re-emphasizes the distinction: **don't fake tabs with a bottom toolbar of navigation-looking buttons, and don't put actions (`+`, Scan, Pay) as tab items.**

### 6.4 Bottom bar with `ToolbarItemGroup`

```swift
NavigationStack {
    List { /* … */ }
        .navigationTitle("Items")
        .toolbar {
            ToolbarItemGroup(placement: .bottomBar) {
                Button("Delete", systemImage: "trash", role: .destructive) { }
                Spacer()
                Button("New",    systemImage: "plus")  { }
                Spacer()
                Button("Share",  systemImage: "square.and.arrow.up") { }
            }
        }
}
```

### 6.5 Hiding the tab bar on deeper screens

**For a pushed destination:**

```swift
NavigationStack {
    RootListView()
        .navigationDestination(for: Item.self) { item in
            DetailView(item: item)
                .toolbar(.hidden, for: .tabBar)
        }
}
```

**Toggle between tab bar and contextual bottom bar (edit-mode pattern):**

```swift
struct Root: View {
    @State private var isEditing = false

    var body: some View {
        NavigationStack {
            TabView {
                Tab("Inbox", systemImage: "tray") {
                    Button("Toggle Edit") { isEditing.toggle() }
                        .toolbar(isEditing ? .hidden : .visible, for: .tabBar)
                }
                Tab("Sent", systemImage: "paperplane") { Color.blue }
            }
            .toolbar(isEditing ? .visible : .hidden, for: .bottomBar)
            .animation(.easeIn, value: isEditing)
            .toolbar {
                ToolbarItem(placement: .bottomBar) { Text("Edit actions here") }
            }
        }
    }
}
```

**UIKit equivalent** — `hidesBottomBarWhenPushed`:

```swift
let detail = DetailVC()
detail.hidesBottomBarWhenPushed = true
navigationController?.pushViewController(detail, animated: true)
```

On iOS 26, `hidesBottomBarWhenPushed` has reported behavior changes (Apple Forums 789660) — prefer SwiftUI's `.toolbar(.hidden, for: .tabBar)` for cross-version safety.

---

## 7. Keyboard toolbar and FocusState

### 7.1 Basics

`ToolbarItemGroup(placement: .keyboard)` renders above the software keyboard when any text field becomes first responder. Introduced in iOS 15 / macOS 12 (Touch Bar).

### 7.2 Dismiss patterns

**Preferred — `@FocusState`:**

```swift
@FocusState private var isFocused: Bool
// …
Button("Done") { isFocused = false }
```

**Legacy resignFirstResponder hack** (use only when you can't access a focus binding):

```swift
UIApplication.shared.sendAction(
    #selector(UIResponder.resignFirstResponder),
    to: nil, from: nil, for: nil
)
```

### 7.3 Full example — Form with Previous / Next / Done

```swift
struct SignUpForm: View {
    enum Field: Hashable { case firstName, lastName, email, password }

    @State private var firstName = ""
    @State private var lastName  = ""
    @State private var email     = ""
    @State private var password  = ""
    @FocusState private var focusedField: Field?

    private let order: [Field] = [.firstName, .lastName, .email, .password]

    var body: some View {
        NavigationStack {
            Form {
                TextField("First name", text: $firstName)
                    .focused($focusedField, equals: .firstName)
                    .textContentType(.givenName)
                    .submitLabel(.next)

                TextField("Last name", text: $lastName)
                    .focused($focusedField, equals: .lastName)
                    .textContentType(.familyName)
                    .submitLabel(.next)

                TextField("Email", text: $email)
                    .focused($focusedField, equals: .email)
                    .textContentType(.emailAddress)
                    .keyboardType(.emailAddress)
                    .textInputAutocapitalization(.never)
                    .submitLabel(.next)

                SecureField("Password", text: $password)
                    .focused($focusedField, equals: .password)
                    .textContentType(.newPassword)
                    .submitLabel(.done)
            }
            .onSubmit(advanceFocus)
            .toolbar {
                ToolbarItemGroup(placement: .keyboard) {
                    Button { focusPrevious() } label: {
                        Label("Previous", systemImage: "chevron.up")
                    }
                    .disabled(!canGoPrevious)

                    Button { advanceFocus() } label: {
                        Label("Next", systemImage: "chevron.down")
                    }
                    .disabled(!canGoNext)

                    Spacer()

                    Button("Done") { focusedField = nil }.bold()
                }
            }
            .navigationTitle("Sign up")
        }
    }

    private var canGoPrevious: Bool {
        guard let c = focusedField, let i = order.firstIndex(of: c) else { return false }
        return i > 0
    }
    private var canGoNext: Bool {
        guard let c = focusedField, let i = order.firstIndex(of: c) else { return false }
        return i < order.count - 1
    }
    private func focusPrevious() {
        guard let c = focusedField, let i = order.firstIndex(of: c), i > 0 else { return }
        focusedField = order[i - 1]
    }
    private func advanceFocus() {
        guard let c = focusedField, let i = order.firstIndex(of: c) else {
            focusedField = order.first; return
        }
        focusedField = (i < order.count - 1) ? order[i + 1] : nil
    }
}
```

### 7.4 `submitLabel(_:)` integration

Sets the return-key glyph. Values: `.continue`, `.done`, `.go`, `.join`, `.next`, `.return`, `.route`, `.search`, `.send`.

```swift
TextField("Email", text: $email)
    .submitLabel(.next)
    .onSubmit { focusedField = .password }
```

**Gotcha:** `onSubmit` does not fire for a multi-line `TextField(axis: .vertical)` — return inserts a newline. Watch `onChange(of: text)` for `"\n"` and dismiss manually.

### 7.5 UIKit equivalent

```swift
let toolbar = UIToolbar(frame: CGRect(x: 0, y: 0, width: view.bounds.width, height: 44))
toolbar.items = [
    UIBarButtonItem(title: "Previous", style: .plain, target: self, action: #selector(prev)),
    UIBarButtonItem(title: "Next",     style: .plain, target: self, action: #selector(next)),
    UIBarButtonItem.flexibleSpace(),
    UIBarButtonItem(barButtonSystemItem: .done, target: self, action: #selector(done))
]
textField.inputAccessoryView = toolbar
```

### 7.6 iOS 26 caveat

Apple Developer Forums thread 799692 reports an extra top-margin layout regression between the keyboard toolbar and the focused field on iOS 26. Don't hard-pixel-tune the spacing — SwiftUI manages it.

---

## 8. macOS differences — customization, roles, window style

### 8.1 User-customizable toolbars — `.toolbar(id:)` (iOS 16+ / macOS 13+)

Give the toolbar a stable `id`, give each item a stable `id`, use `.primaryAction` (pinned) or `.secondaryAction` (customizable), and optionally set `showsByDefault: false` for items hidden until the user adds them.

```swift
struct NotesWindow: View {
    var body: some View {
        NavigationStack {
            NoteList()
                .navigationTitle("Notes")
                .toolbar(id: "notes.main") {
                    ToolbarItem(id: "new", placement: .primaryAction) {
                        Button("New", systemImage: "square.and.pencil") { }
                            .help("New note")
                            .keyboardShortcut("n")
                    }
                    ToolbarItem(id: "share", placement: .secondaryAction) {
                        ShareLink(item: URL(string: "https://example.com")!)
                    }
                    ToolbarItem(id: "tag", placement: .secondaryAction) {
                        Button("Tag", systemImage: "tag") { }
                    }
                    ToolbarItem(id: "print",
                                placement: .secondaryAction,
                                showsByDefault: false) {
                        Button("Print", systemImage: "printer") { }
                    }
                }
                .toolbarRole(.editor)
        }
    }
}
```

On macOS this wires into the native "Customize Toolbar…" sheet (right-click the toolbar); the OS auto-persists user reordering.

**Known crash (macOS 15+):** wrapping `ToolbarItem(id:)` inside a conditional `if` can crash when opening a second window (Apple Forums 772096). Mitigation: always declare items unconditionally; toggle `.disabled(!condition)` instead.

**HIG note:** the customizable `.toolbar(id:)` surface is meaningfully user-facing only on iPadOS and macOS, even though the API compiles everywhere.

### 8.2 `toolbarRole(_:)` — semantic roles (iOS 16+)

| Role | Effect |
|---|---|
| `.automatic` | Default; `.navigationStack` on iOS, `.editor` on macOS |
| `.navigationStack` | Standard push-nav layout; title centered on iOS |
| `.editor` | Document editor; title moves to leading edge, frees center for secondary actions, minimal back button on iPad/Mac |
| `.browser` | Web/file-browser layout; title leading, actions trailing (Safari-style) |

### 8.3 Mac placement mapping

| Placement | Mac behavior |
|---|---|
| `.navigation` | Leading edge near traffic lights; non-customizable |
| `.principal` | Center of title bar |
| `.primaryAction` | Trailing edge, pinned |
| `.secondaryAction` | Center area (with `.editor`/`.browser`), customizable |
| `.confirmationAction` / `.cancellationAction` | Sheet trailing/leading (idiomatic Save/Cancel) |
| `.destructiveAction` | Red-tinted |
| `.automatic` | Typically trailing |
| `.status` | Center — "Saving…" text |

HIG: *"Only specify one primary action, and put it on the trailing side of the toolbar."*

### 8.4 `windowToolbarStyle(_:)` — macOS only (macOS 11+)

Attach to `WindowGroup` / `Window`.

| Style | Appearance |
|---|---|
| `.automatic` | Defaults to `.unified` |
| `.unified` | Title bar merges with toolbar (single row) |
| `.unifiedCompact` | Tighter — typical productivity apps |
| `.expanded` | Classic two-row: title on top, toolbar below |

```swift
@main
struct EditorApp: App {
    var body: some Scene {
        WindowGroup { ContentView() }
            .windowToolbarStyle(.unifiedCompact)
    }
}
```

**Related modifiers (macOS 14+/15+):**

```swift
.windowToolbarLabelStyle(fixed: .iconOnly)          // macOS 14+
.windowResizability(.contentSize)
.toolbar(removing: .sidebarToggle)                   // macOS 14+
.toolbar(.hidden, for: .windowToolbar)
```

### 8.5 macOS 26 Tahoe Liquid Glass

From WWDC25 session 323:

> "iOS 26 and macOS Tahoe introduce Liquid Glass, a new adaptive material for controls and navigational elements inspired by glass and liquid."

- Recompiling against the macOS 26 SDK causes `NavigationBar`, `TabBar`, `Toolbar`, sidebars, sheets, menus, and `NSPopover` to adopt Liquid Glass automatically — no code changes.
- Apple guidance: **Glass only on floating controls** — don't apply `.glassEffect()` to content.
- New APIs available on macOS 26: `ToolbarSpacer`, `DefaultToolbarItem`, `.searchToolbarBehavior(.minimize)`, `.largeTitle` placement.

### 8.6 AppKit equivalent

```swift
class WindowController: NSWindowController, NSToolbarDelegate {
    override func windowDidLoad() {
        super.windowDidLoad()
        let toolbar = NSToolbar(identifier: "main")
        toolbar.delegate = self
        toolbar.displayMode = .iconOnly
        toolbar.allowsUserCustomization = true
        toolbar.autosavesConfiguration = true
        window?.toolbar = toolbar
        window?.toolbarStyle = .unified                 // macOS 11+
    }

    func toolbarAllowedItemIdentifiers(_ t: NSToolbar) -> [NSToolbarItem.Identifier] {
        [.newItem, .share, .flexibleSpace, NSToolbarItem.Identifier("print")]
    }
    func toolbarDefaultItemIdentifiers(_ t: NSToolbar) -> [NSToolbarItem.Identifier] {
        [.newItem, .share, .flexibleSpace]
    }
    func toolbar(_ t: NSToolbar,
                 itemForItemIdentifier id: NSToolbarItem.Identifier,
                 willBeInsertedIntoToolbar flag: Bool) -> NSToolbarItem? {
        let item = NSToolbarItem(itemIdentifier: id)
        item.label = "New"
        item.image = NSImage(systemSymbolName: "square.and.pencil", accessibilityDescription: nil)
        item.target = self; item.action = #selector(newDoc(_:))
        return item
    }

    @objc func newDoc(_ sender: Any?) { }
}
```

### 8.7 SwiftUI → AppKit cross-reference

| SwiftUI | AppKit |
|---|---|
| `.toolbar(id:)` | `NSToolbar(identifier:)` + `autosavesConfiguration = true` |
| `ToolbarItem(id:)` | `NSToolbarItem(itemIdentifier:)` |
| `ToolbarItemGroup` | `NSToolbarItemGroup` |
| `showsByDefault: false` | In `toolbarAllowedItemIdentifiers` but not `toolbarDefaultItemIdentifiers` |
| `.toolbarRole(.editor)` | No direct equivalent; `centeredItemIdentifier` gets partway |
| `.windowToolbarStyle(.unifiedCompact)` | `window.toolbarStyle = .unifiedCompact` |

---

## 9. Anti-patterns and best practices

Apple HIG, *Toolbars* (updated June 9, 2025):

> *"Choose items deliberately to avoid overcrowding. Reduce the use of toolbar backgrounds and tinted controls. Prefer using standard components in a toolbar. Prefer system-provided symbols without borders. Only specify one primary action, and put it on the trailing side of the toolbar."*

### 9.1 Too many items

❌ **Bad** — overcrowded, overlaps title on small iPhones:

```swift
.toolbar {
    ToolbarItemGroup(placement: .topBarTrailing) {
        Button("Add")    { }
        Button("Edit")   { }
        Button("Sort")   { }
        Button("Filter") { }
        Button("Share")  { }
        Button("Info")   { }
    }
}
```

✅ **Good** — surface one primary action, move the rest into a `Menu`:

```swift
.toolbar {
    ToolbarItem(placement: .primaryAction) {
        Button("Add", systemImage: "plus") { addItem() }
    }
    ToolbarItem(placement: .topBarTrailing) {
        Menu {
            Button("Edit",   systemImage: "pencil") { }
            Button("Sort",   systemImage: "arrow.up.arrow.down") { }
            Button("Filter", systemImage: "line.3.horizontal.decrease.circle") { }
            ShareLink(item: url)
            Button("Info",   systemImage: "info.circle") { }
        } label: {
            Label("More", systemImage: "ellipsis.circle")
        }
    }
}
```

### 9.2 Unclear priority

❌ **Bad** — everything `.automatic`; Save doesn't read as primary:

```swift
.toolbar {
    ToolbarItem { Button("Settings") { } }
    ToolbarItem { Button("Help") { } }
    ToolbarItem { Button("Save") { } }
}
```

✅ **Good** — semantic placements communicate intent:

```swift
.toolbar(id: "docs") {
    ToolbarItem(id: "save", placement: .primaryAction) {
        Button("Save") { save() }.keyboardShortcut("s")
    }
    ToolbarItem(id: "settings", placement: .secondaryAction) { Button("Settings") { } }
    ToolbarItem(id: "help",     placement: .secondaryAction) { Button("Help") { } }
}
.toolbarRole(.editor)
```

### 9.3 Custom chrome replacing the system toolbar

❌ **Bad** — breaks Liquid Glass, Dynamic Type, VoiceOver order, safe areas:

```swift
VStack(spacing: 0) {
    HStack {
        Button("Back") { dismiss() }
        Spacer()
        Text("My Screen").font(.headline)
        Spacer()
        Button("Save") { }
    }
    .padding()
    .background(Color.blue)
    ContentBody()
}
```

✅ **Good**:

```swift
NavigationStack {
    ContentBody()
        .navigationTitle("My Screen")
        .toolbar {
            ToolbarItem(placement: .confirmationAction) { Button("Save") { save() } }
        }
}
```

### 9.4 Breaking platform conventions

❌ **Bad** — back button on the wrong side, wrong glyph:

```swift
.toolbar {
    ToolbarItem(placement: .navigationBarTrailing) {
        Button("< Back") { dismiss() }
    }
}
```

✅ **Good** — do nothing; `NavigationStack` provides the correct back button automatically. Customize only what you must:

```swift
.navigationTitle("Details")
```

### 9.5 Mixing `.bottomBar` with a `TabView`

HIG: *"Toolbars and tab bars don't appear together in the same view."*

❌ **Bad** — on iOS 26 the bottom bar is obscured by / layered with the tab bar:

```swift
TabView {
    Tab("Inbox", systemImage: "tray") {
        InboxView()
            .toolbar {
                ToolbarItemGroup(placement: .bottomBar) {
                    Button("Compose") { }
                    Spacer()
                    Button("Archive") { }
                }
            }
    }
}
```

✅ **Good** — use `.tabViewBottomAccessory` on iOS 26+, or move actions to the top-trailing toolbar:

```swift
TabView {
    Tab("Inbox", systemImage: "tray") {
        NavigationStack {
            InboxView()
                .toolbar {
                    ToolbarItem(placement: .primaryAction) {
                        Button("Compose", systemImage: "square.and.pencil") { }
                    }
                }
        }
    }
}
.tabViewBottomAccessory {
    QuickComposeBar()
}
```

### 9.6 Not adapting to Dynamic Type / size class

❌ **Bad** — hard-coded frame, fixed font size:

```swift
ToolbarItem {
    Text("Add to playlist")
        .frame(width: 120)
        .font(.system(size: 13))
}
```

✅ **Good**:

```swift
ToolbarItem {
    Button { add() } label: {
        Label("Add to playlist", systemImage: "plus.square.on.square")
    }
    .labelStyle(.iconOnly)
    .help("Add to playlist")
}
```

### 9.7 Hiding back without alternative

❌ **Bad** — user is trapped:

```swift
.navigationBarBackButtonHidden(true)
```

✅ **Good**:

```swift
.navigationBarBackButtonHidden(true)
.toolbar {
    ToolbarItem(placement: .cancellationAction) {
        Button("Cancel") { dismiss() }
    }
    ToolbarItem(placement: .confirmationAction) {
        Button("Done") { save(); dismiss() }
    }
}
.interactiveDismissDisabled(isDirty)
```

### 9.8 Text labels vs SF Symbols

HIG: *"In a toolbar that contains three or fewer buttons, consider using concise text labels instead of symbols to add clarity. In a toolbar that has more than three buttons, consider using symbols to conserve space. Keep actions with text labels separate. Placing an action with a text label next to an action with a symbol can create the illusion of a single action."*

❌ **Bad** — mixing labels and icons without separation:

```swift
ToolbarItemGroup {
    Button("Save") { }
    Button("", systemImage: "trash") { }  // reads as "Save 🗑"
}
```

✅ **Good** — separate with a spacer on iOS 26:

```swift
ToolbarItem { Button("Save") { } }
ToolbarSpacer(.fixed)
ToolbarItem {
    Button("Delete", systemImage: "trash", role: .destructive) { }
}
```

---

## 10. Appendix

### 10.1 Toolbar placement version cheat sheet

| Placement | iOS | macOS | iPadOS | Notes |
|---|---|---|---|---|
| `.automatic` | 14 | 11 | 14 | |
| `.principal` | 14 | 11 | 14 | |
| `.navigation` | 14 | 11 | 14 | |
| `.navigationBarLeading` / `.navigationBarTrailing` | 14 | 11 | 14 | Superseded by `.topBar*` (iOS 17+) |
| `.topBarLeading` / `.topBarTrailing` | 17 | 14 | 17 | |
| `.primaryAction` | 14 | 11 | 14 | Auto `.glassProminent` on iOS 26 |
| `.secondaryAction` | 16 | 13 | 16 | Customizable; collapses to overflow |
| `.confirmationAction` / `.cancellationAction` / `.destructiveAction` | 14 | 11 | 14 | Modal-idiomatic |
| `.bottomBar` | 14 | — | 14 | |
| `.keyboard` | 15 | 12 | 15 | Touch Bar on macOS |
| `.status` | 14 | 11 | 14 | |
| `.bottomOrnament` | — | — | — | visionOS 1+ |
| `.title` / `.subtitle` / `.largeTitle` / `.largeSubtitle` | 26 | 26 | 26 | |

### 10.2 iOS 26 new APIs cheat sheet

| API | Purpose |
|---|---|
| `ToolbarSpacer(.fixed | .flexible, placement:)` | Split shared glass capsules |
| `DefaultToolbarItem(kind: .search, placement:)` | Insert system search in a toolbar |
| `.searchToolbarBehavior(.minimize)` | Collapse search into an icon |
| `.sharedBackgroundVisibility(.hidden)` | Opt out of glass capsule |
| `.backgroundExtensionEffect()` | Mirror/blur content under floating bars |
| `.safeAreaBar(edge:alignment:spacing:content:)` | Custom bar with auto blur/fade |
| `.scrollEdgeEffectStyle(_:for:)` | Tune `.automatic` / `.hard` / `.soft` |
| `.toolbarBackgroundVisibility(_:for:)` | Fine-grained background visibility |
| `.buttonStyle(.glass)` / `.glassProminent` | Liquid Glass button styles |
| `.glassEffect(_:in:isEnabled:)` | Apply Liquid Glass to custom views |
| `.tabBarMinimizeBehavior(_:)` | Auto-minimize tab bar on scroll |
| `.tabViewBottomAccessory { }` | Persistent accessory above tab bar |
| `.navigationSubtitle(_:)` | Subtitle under nav title |

### 10.3 Migration checklist (iOS 18 → iOS 26)

1. **Remove custom toolbar backgrounds** — strip `.toolbarBackground(Color.x, for: .navigationBar)` unless truly required for branding.
2. **Replace `safeAreaInset` for floating bars** with `safeAreaBar(edge:…)` so you get the progressive blur.
3. **Insert `ToolbarSpacer(.fixed)`** between unrelated `ToolbarItem`s in the same placement — iOS 26 will otherwise merge them into one capsule.
4. **Use `ToolbarSpacer(.flexible)`** to push items to opposite ends rather than embedding `Spacer()` in a `ToolbarItemGroup`.
5. **Switch to symbol+text `Label`** in toolbar items so monochrome rendering looks right.
6. **Adopt semantic placements** — move from `.topBarTrailing` → `.confirmationAction` / `.primaryAction` so the system applies `.glassProminent` automatically.
7. **Add `.backgroundExtensionEffect()`** on sidebar hero images so they continue under the floating sidebar.
8. **Tune scroll edge effects** with `.scrollEdgeEffectStyle(.hard, for: .top)` only where the soft default competes visually.
9. **Avoid bottom toolbars inside TabView** — migrate to `.tabViewBottomAccessory`.
10. **Don't apply `.toolbarBackground` to TabView** — apply to per-tab content.
11. **Don't double-glass** — don't stack `.buttonStyle(.glass)` on toolbar items, don't add `.glassEffect()` to a `.glassProminent` button.
12. **Fully migrate from legacy `.tabItem`** to `Tab` — mixing disables iOS 26 features.
13. **Use `searchToolbarBehavior(.minimize)`** when search isn't the primary feature.

### 10.4 Known issues to be aware of

- **`.keyboard` iOS 26 top-margin gap** — Apple Forums 799692.
- **`.largeTitle` overlap during nav transitions** — Apple Forums 811877; currently requires non-empty `.navigationTitle()`.
- **`tabBarMinimizeBehavior(.onScrollDown)`** — may not trigger inside `NavigationStack(path:)` with a bound `NavigationPath`.
- **`.tabViewBottomAccessory` conditional content crash** — FB18479195; prefer unconditional builder with conditional inner views.
- **macOS 15+ `ToolbarItem(id:)` in conditional `if`** — Apple Forums 772096; always declare items, toggle `.disabled` instead.
- **`hidesBottomBarWhenPushed` on iOS 26** — reported behavioral changes (Apple Forums 789660); prefer `.toolbar(.hidden, for: .tabBar)`.

### 10.5 WWDC session references

| Session | Year | Topic |
|---|---|---|
| "The SwiftUI cookbook for navigation" | 2022 | Navigation fundamentals |
| "SwiftUI on iPad: Add toolbars, titles, and more" (110343) | 2022 | `toolbarRole`, `.secondaryAction`, customizable toolbars |
| "What's new in SwiftUI" | 2023/2024/2025 | Yearly updates |
| "Elevate your tab and sidebar experience in iPadOS" (10147) | 2024 | `Tab`, `TabSection`, `sidebarAdaptable`, customization |
| "What's new in UIKit" (10118) | 2024 | `UITab`, `UITabGroup`, `UISearchTab` |
| "Meet Liquid Glass" (219) | 2025 | Design material introduction |
| "Build a SwiftUI app with the new design" (323) | 2025 | Toolbar Liquid Glass, `ToolbarSpacer`, bottom accessory |
| "Get to know the new design system" (356) | 2025 | Design system overview |

### 10.6 Apple HIG references

- Navigation bars — `developer.apple.com/design/human-interface-guidelines/navigation-bars`
- Toolbars — `developer.apple.com/design/human-interface-guidelines/toolbars`
- Tab bars — `developer.apple.com/design/human-interface-guidelines/tab-bars`
- Search fields — `developer.apple.com/design/human-interface-guidelines/search-fields`
- Designing with Liquid Glass — `developer.apple.com/design/human-interface-guidelines/designing-with-liquid-glass`
- Designing for macOS — `developer.apple.com/design/human-interface-guidelines/designing-for-macos`