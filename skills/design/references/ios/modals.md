---
name: modals
description: SwiftUI modals, menus, alerts — when to pick which surface (iOS 18/26)
platform: ios
---

# Choosing modals, menus, and alerts in SwiftUI

**Pick the lightest surface that still forces the user to notice.** That single rule drives every decision below: alerts interrupt, confirmation dialogs confirm an action the user just took, menus offer a tidy list of related actions near their trigger, context menus accelerate power users, and sheets host sub-tasks. Getting the mapping wrong is the single biggest cause of modal fatigue in iOS apps — users tune out alerts that should have been inline errors, miss features hidden only in context menus, and reflexively dismiss "Are you sure?" dialogs. This reference targets **iOS 18 and iOS 26** (Liquid Glass). It gives you a decision tree, the canonical SwiftUI code for each surface, Apple's writing rules, and the anti-patterns Apple explicitly calls out in the Human Interface Guidelines.

Two things changed in iOS 26 that should shape every decision you make now: alerts, confirmation dialogs, menus, context menus, sheets, and popovers **morph out of the view the modifier is attached to**, so attachment point matters more than ever; and the new `Button` roles `.confirm` and `.close` give you the correct tinted/xmark appearance without custom styling. WWDC 2026 has not yet happened as of April 20, 2026 — it runs June 8–12, 2026 — so the current guidance continues to derive from WWDC 2020 (Session 10205), WWDC 2021 (Session 10018), WWDC 2023 (Session 10148), and WWDC 2025 sessions 219, 323, 356, and 208.

---

## The decision tree

```
                     ┌──────────────────────────────────────┐
                     │   Do I need the user's attention?    │
                     └──────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼──────────────────────────────┐
        │                             │                              │
     NO, just                    YES, but not                   YES, must
   status/feedback               right now                    decide NOW
        │                             │                              │
        ▼                             ▼                              ▼
┌───────────────┐        ┌─────────────────────────┐      ┌─────────────────────┐
│ Inline error  │        │ Badge / TipKit /        │      │ Is it in response   │
│ Status view   │        │ ContentUnavailableView  │      │ to a user action?   │
│ Toolbar count │        │ or a non-blocking       │      └─────────────────────┘
│ (NO alert)    │        │ ambient indicator       │                │
└───────────────┘        └─────────────────────────┘     ┌──────────┴──────────┐
                                                          │                     │
                                                         YES                   NO
                                                          │                     │
                                                          ▼                     ▼
                                       ┌────────────────────────────┐  ┌─────────────────┐
                                       │ Is the action destructive  │  │ System/app-driven│
                                       │ or irreversible?           │  │ problem?         │
                                       └────────────────────────────┘  └─────────────────┘
                                              │         │                     │
                                            YES         NO                    ▼
                                              │         │            ┌─────────────────┐
                                              ▼         ▼            │     ALERT       │
                       ┌──────────────────────────┐  ┌──────────┐    │ (blocking, must │
                       │ Is undo realistic?       │  │ Just do  │    │ be acknowledged)│
                       └──────────────────────────┘  │ it — use │    └─────────────────┘
                              │            │         │ undo or  │
                             YES           NO        │ toast    │
                              │            │         │ instead  │
                              ▼            ▼         └──────────┘
              ┌────────────────────┐ ┌────────────────────────────┐
              │ Do it + offer Undo │ │ CONFIRMATION DIALOG         │
              │ (swipe-back, undo  │ │ .confirmationDialog(...)    │
              │ banner, shake)     │ │ with role:.destructive      │
              └────────────────────┘ └────────────────────────────┘


    ════════════════ Presenting CHOICES (not warnings) ═════════════════

                     ┌──────────────────────────────────────┐
                     │ How many related actions on a button?│
                     └──────────────────────────────────────┘
                                       │
            ┌──────────────────────────┼─────────────────────────┐
            │                          │                         │
           1                         2–7                        many / complex
            │                          │                         │
            ▼                          ▼                         ▼
       ┌────────┐            ┌─────────────────────┐    ┌─────────────────┐
       │ BUTTON │            │ Mutually exclusive? │    │      SHEET      │
       │ (never │            └─────────────────────┘    │ (hosts a sub-   │
       │  wrap  │                  │       │            │ task or form)   │
       │  in a  │                 YES      NO           └─────────────────┘
       │  Menu) │                  │       │
       └────────┘                  ▼       ▼
                        ┌────────────┐  ┌────────────┐
                        │ Picker with│  │   MENU     │
                        │.pickerStyle│  │ (pull-down │
                        │   (.menu)  │  │  or split  │
                        │ = pop-up   │  │  button w/ │
                        │  button    │  │primaryAction)│
                        └────────────┘  └────────────┘


    ═══════════════ Per-ITEM actions on a row/cell/object ═══════════════

                     ┌──────────────────────────────────────┐
                     │ Is it the only way to do this thing? │
                     └──────────────────────────────────────┘
                                       │
                     ┌─────────────────┴─────────────────┐
                     │                                   │
                    YES                                  NO
                     │                                   │
                     ▼                                   ▼
            ┌────────────────┐                 ┌──────────────────┐
            │ Do NOT use a   │                 │ CONTEXT MENU     │
            │ context menu — │                 │ as an accelerator│
            │ add a visible  │                 │ (+ mirror key    │
            │ button first.  │                 │  actions in      │
            │ Then add a     │                 │  toolbar/swipe)  │
            │ context menu   │                 └──────────────────┘
            │ as a shortcut. │
            └────────────────┘
```

**Five questions that resolve 95% of cases.** Is dismissal blocking or non-blocking? Is the surface discoverable or hidden behind a gesture? Is the action reversible or destructive? Is the content informational or actionable? Is the task part of the current view or a scoped sub-task? An alert is blocking + discoverable + for critical info/actionable. A context menu is non-blocking + hidden + for accelerators. A menu is non-blocking + discoverable + for actions. A sheet is blocking + discoverable + for sub-tasks. Get those axes right and the component picks itself.

---

## Surface comparison at a glance

| Component | Presentation | Blocking? | Discoverability | iPad adaptation | Typical use | Dismissal |
|---|---|---|---|---|---|---|
| **`.alert`** | Centered card over dimmed backdrop | **Blocking** | Visible when triggered | Same centered card | Critical info, errors needing action, confirm destructive with explanation | Tap action button |
| **`.confirmationDialog`** | Bottom action sheet (iPhone) / popover (iPad) | **Blocking** | Visible when triggered | Popover anchored to source | Confirm user-initiated action, multi-choice branch | Any button, tap outside (iPad), Cancel (iPhone) |
| **`Menu`** (pull-down) | Inline pop-out near button | Non-blocking | **Visible** (button is an affordance) | Same inline pop-out | 2–7 related actions, selections attached to a button | Tap outside, pick item |
| **Picker `.menu` style** (pop-up) | Inline pop-out with checkmark | Non-blocking | **Visible** | Same | Mutually exclusive selection | Pick option |
| **`.contextMenu`** | Floating pop-out with optional preview | Non-blocking | **Hidden** (long-press/right-click) | Same, can show preview side-by-side | Per-item accelerators | Tap outside, pick item |
| **`.sheet`** | Bottom slide-up card (partial/full detents) | Typically blocking | Visible when triggered | Centered form sheet | Scoped sub-task, form, detail | Swipe down, Done/Cancel button |
| **Inline error** | In-layout text near input | Non-blocking | **Always visible** | Same | Field validation, recoverable problem | Fix the input |
| **TipKit / status view** | Ambient, contextual | Non-blocking | Visible | Same | Discoverability tips, empty states | Auto / user interaction |

iOS 26 applies Liquid Glass automatically to everything in the top half of this table when you recompile with Xcode 26; sheets adopt the new floating translucent appearance only when you declare a partial detent.

---

## Alerts — interruptive by design

**Use an alert only when the user must decide or acknowledge something critical right now.** Apple's Human Interface Guidelines are blunt: *"Avoid using an alert merely to provide information."* Alerts are centered, dim the rest of the app, and require a tap to dismiss — they are the most expensive surface in your UI. Reserve them for (1) problems the user must act on, (2) destructive confirmations that need explanatory text, and (3) purchase/authorization confirmations. For field validation or recoverable errors, use an **inline error**; for transient success, use a status indicator or haptic.

### Single-button informational alert

A one-button alert is almost always a smell. If you are tempted to write one, reconsider whether a non-modal indicator would do. When it is genuinely warranted (e.g., confirming an account was created), omit the `actions` closure to let SwiftUI add the default OK button:

```swift
struct SingleButtonAlert: View {
    @State private var showSaved = false

    var body: some View {
        Button("Save") { showSaved = true }
            .alert("Saved", isPresented: $showSaved) {
                // Empty actions → SwiftUI provides a default "OK"
            } message: {
                Text("Your changes have been saved to iCloud.")
            }
    }
}
```

### Multi-button alert with a destructive role

SwiftUI auto-arranges buttons based on their `role`. `.destructive` renders red; `.cancel` is bolded as the safe default and pinned to the correct locale-appropriate position. **Never assign `.destructive` to a primary button** — HIG explicitly warns that visual prominence on a destructive action causes accidental loss.

```swift
struct DeleteAccountAlert: View {
    @State private var confirming = false

    var body: some View {
        Button("Delete Account", role: .destructive) { confirming = true }
            .alert("Delete account?", isPresented: $confirming) {
                Button("Delete", role: .destructive) { deleteAccount() }
                Button("Cancel",  role: .cancel) { }
            } message: {
                Text("Your photos, documents, and subscriptions will be removed. This can't be undone.")
            }
    }

    func deleteAccount() { /* … */ }
}
```

### Text fields inside an alert (iOS 16+)

Since iOS 16, `TextField` and `SecureField` can appear inside the `actions` closure. No other controls render — `Toggle`, `Menu`, etc. are stripped. Use this for simple credential or rename prompts; anything richer belongs in a sheet.

```swift
struct RenameAlert: View {
    @State private var isPresented = false
    @State private var newName = ""

    var body: some View {
        Button("Rename…") { isPresented = true }
            .alert("Rename playlist", isPresented: $isPresented) {
                TextField("Playlist name", text: $newName)
                Button("Rename") { commit(newName) }
                Button("Cancel", role: .cancel) { }
            } message: {
                Text("Enter a new name for this playlist.")
            }
    }

    func commit(_ name: String) { /* … */ }
}
```

### The `presenting:` overload for item-based alerts

When the alert needs data from a specific model, the `presenting:` variant passes the item into both the `actions` and `message` builders — cleaner than capturing optionals in closures.

```swift
.alert("Delete document",
       isPresented: $isPresenting,
       presenting: selectedDocument) { doc in
    Button("Delete \(doc.name)", role: .destructive) { delete(doc) }
    Button("Cancel", role: .cancel) { }
} message: { doc in
    Text("\"\(doc.name)\" (\(doc.size)) will be deleted permanently.")
}
```

### iOS 26 specifics

Alerts pick up Liquid Glass automatically on recompile and **animate outward from the button you attached the modifier to** — attach `.alert` to the triggering view, not to a distant parent, or the morph looks broken. iOS 26 added two `ButtonRole` cases relevant here: **`.confirm`** renders a filled primary button (the new affirmative style) and **`.close`** renders the xmark dismiss glyph (reserve for informational sheets, not for "Cancel" in a destructive flow). There is no `.alertStyle(.glass)` modifier in Apple's public API — a few third-party articles claim one exists, but I could not verify it in Xcode 26 SDK headers. Styling is automatic.

---

## Confirmation dialogs — the right home for "are you sure?"

A confirmation dialog is the correct surface when the user just initiated an action and you need to confirm it (especially if destructive) or offer 2–5 follow-up choices. On iPhone it slides up as an action sheet; on iPad it appears as a popover anchored to the triggering control with no automatic Cancel. **Prefer confirmation dialogs over alerts when you have more than one reasonable action and don't need a long explanatory message.**

### Destructive confirmation with a visible title

`titleVisibility` has three values — `.automatic`, `.visible`, `.hidden`. The default `.automatic` hides the title on iPhone when no message is provided. Use `.visible` whenever the title carries meaning (which it almost always does).

```swift
struct EmptyTrashButton: View {
    @State private var confirming = false
    let itemCount: Int

    var body: some View {
        Button("Empty Trash") { confirming = true }
            .confirmationDialog(
                "Empty the Trash?",
                isPresented: $confirming,
                titleVisibility: .visible
            ) {
                Button("Empty Trash", role: .destructive) { emptyTrash() }
                Button("Cancel",       role: .cancel) { }
            } message: {
                Text("\(itemCount) items will be permanently deleted.")
            }
    }

    func emptyTrash() { /* … */ }
}
```

### Multi-choice dialog (the Mail "Cancel draft" pattern)

Apple's canonical example: when the user cancels a draft, give them three paths.

```swift
.confirmationDialog("Discard this draft?",
                    isPresented: $isCancelingDraft,
                    titleVisibility: .visible) {
    Button("Delete Draft", role: .destructive) { discardDraft() }
    Button("Save Draft") { saveDraft() }
    Button("Keep Editing", role: .cancel) { }
}
```

### iPhone vs iPad behavior

On iPhone, SwiftUI adds a Cancel button automatically if you don't supply one and slides the sheet up from the bottom. On iPad, the dialog is a popover anchored to the button — there is no auto-Cancel because tapping outside dismisses. As of iOS 26, UIKit action sheets on iPhone are also source-anchored (like iPad), and the inline variant loses its Cancel button; SwiftUI's `.confirmationDialog` abstracts that away, but be aware if you are mixing SwiftUI and UIKit.

### iOS 23 severity and suppression (still relevant)

WWDC 2023's Session 10148 added `.dialogSeverity(.critical)` and `.dialogSuppressionToggle(isSuppressed:)`. Use `.critical` sparingly to elevate attention; the suppression toggle (macOS-focused) adds a "Do not show this again" checkbox. `HelpLink { }` adds a help link to a dialog. In iOS 26, attach `.confirmationDialog` directly to the trigger view — Hacking with Swift's updated guidance is explicit: *"it is critical to attach it to whatever view is triggering the dialog – the liquid glass effect will animate out from that view."*

---

## Context menus — accelerators, never sole paths

**Context menus are hidden by default, so they can never be the only way to reach a command.** The HIG is unambiguous on this: *"Although a context menu provides convenient access to frequently used items, it's hidden by default, so people might not know it's there."* Every action in a context menu must also exist somewhere visible — a toolbar, a button, a swipe action, or a menu. Use context menus to speed up power users on items they can already act on elsewhere.

### Basic context menu

```swift
struct NoteRow: View {
    let note: Note

    var body: some View {
        Text(note.title)
            .contextMenu {
                Button { share(note) } label: {
                    Label("Share", systemImage: "square.and.arrow.up")
                }
                Button { pin(note) } label: {
                    Label("Pin to Top", systemImage: "pin")
                }
                Divider()
                Button(role: .destructive) { delete(note) } label: {
                    Label("Delete", systemImage: "trash")
                }
            }
    }
}
```

Destructive items go **at the bottom** of a context menu per HIG, with a divider separating them from non-destructive items.

### Context menu with a custom preview (iOS 16+)

The `preview:` builder lets you render a rich preview above the menu. Apple's Photos app is the archetype. Keep previews fast to render — they appear during a live long-press.

```swift
.contextMenu {
    Button("Open") { open(photo) }
    Button("Duplicate") { duplicate(photo) }
    Divider()
    Button(role: .destructive) { delete(photo) } label: {
        Label("Delete", systemImage: "trash")
    }
} preview: {
    AsyncImage(url: photo.url) { image in
        image.resizable().scaledToFit()
    } placeholder: {
        ProgressView()
    }
    .frame(width: 300, height: 300)
}
```

### Nested submenus

Keep nesting to one level. Apple offers two mechanisms: a nested `Menu` (acts as a submenu) and, since iOS 17, `ControlGroup` (renders as a compact icon row on iOS, as a submenu on macOS).

```swift
.contextMenu {
    Button("Open") { }
    Menu {
        Button("Copy")  { }
        Button("Cut")   { }
        Button("Paste") { }
    } label: {
        Label("Edit", systemImage: "pencil")
    }
    Divider()
    Button(role: .destructive) { } label: {
        Label("Delete", systemImage: "trash")
    }
}
```

### Discoverability and iPad pointer behavior

On iPad with a trackpad or mouse, context menus are invoked by secondary-click (two-finger tap on the trackpad, right-click on a mouse) — matching macOS. With Apple Pencil or touch, long-press or Haptic Touch reveals them. Because discoverability differs by input device, **never put unique commands only in a context menu**. HIG also warns against showing keyboard shortcuts inside a context menu — they belong in the iPad/Mac menu bar. In iOS 26 context menus adopt Liquid Glass, and menu-item labels reorder so **the icon is leading** regardless of how you wrote the `HStack` — use `Label(_:systemImage:)` to get the intended order automatically.

---

## Menus — the pull-down and pop-up workhorses

A `Menu` attaches 2–7 related actions or a mutually-exclusive selection to a button, opening inline near the trigger. Apple adds two rules to the HIG: list at least three items (two barely justifies a menu), and **never hide a view's primary actions in a menu** — those need to be immediately tappable.

### Basic pull-down menu

```swift
Menu {
    Button { addFile() }        label: { Label("New File", systemImage: "doc.badge.plus") }
    Button { addFolder() }      label: { Label("New Folder", systemImage: "folder.badge.plus") }
    Button { addSharedAlbum() } label: { Label("New Shared Album", systemImage: "person.2") }
} label: {
    Label("Add", systemImage: "plus")
}
```

### Split button with `primaryAction:` (iOS 15+)

Adding a `primaryAction:` closure turns the control into a **split button** — tap fires the primary action, long-press opens the menu. This is exactly how Safari's back button works.

```swift
Menu {
    Button("Add reference") { addReference() }
    Button("Add folder")    { addFolder() }
    Divider()
    Button(role: .destructive) { removeLast() } label: {
        Label("Remove Last", systemImage: "trash")
    }
} label: {
    Label("Add File", systemImage: "plus")
} primaryAction: {
    addFile()                       // fires on tap
}
```

### Picker as a pop-up menu

For a **mutually exclusive selection**, use `Picker` with `.pickerStyle(.menu)`. The current selection shows next to the label; opening the menu reveals options with a checkmark on the active one.

```swift
enum SortOrder: String, CaseIterable, Identifiable {
    case name, date, size
    var id: Self { self }
}

struct SortMenu: View {
    @State private var order: SortOrder = .name

    var body: some View {
        Picker("Sort by", selection: $order) {
            ForEach(SortOrder.allCases) { o in
                Text(o.rawValue.capitalized).tag(o)
            }
        }
        .pickerStyle(.menu)
    }
}
```

### Dividers, sections, and icons

Use `Divider()` for rules, `Section("Header") { … }` for titled groups, and always label items with `Label(_:systemImage:)` so SF Symbols render correctly. In iOS 26 the system forces **icon-leading** order in menu items; building your own `HStack { Image; Text }` will be overridden.

```swift
Menu {
    Section("Quick") {
        Button { } label: { Label("Today",   systemImage: "sun.max") }
        Button { } label: { Label("Tomorrow",systemImage: "sun.haze") }
    }
    Divider()
    Menu("Later") {
        Button("This Weekend") { }
        Button("Next Week")    { }
    }
    Divider()
    Button(role: .destructive) { } label: {
        Label("Remove Reminder", systemImage: "trash")
    }
} label: {
    Label("Remind Me", systemImage: "bell")
}
```

### iOS 17+ selection features — palette style

Since iOS 17, a `Picker` inside a `Menu` can use `.pickerStyle(.palette)` for a horizontal row of SF Symbols — great for tags, colors, or reactions. Pair with `.paletteSelectionEffect(.symbolVariant(.slash))` for richer state feedback.

```swift
Menu("Tag") {
    Picker("Tag", selection: $tag) {
        Label("Red",    systemImage: "circle.fill").tint(.red).tag(Tag.red)
        Label("Yellow", systemImage: "circle.fill").tint(.yellow).tag(Tag.yellow)
        Label("Green",  systemImage: "circle.fill").tint(.green).tag(Tag.green)
    }
    .pickerStyle(.palette)
}
```

### iOS 26 behavior you need to know

Menus automatically morph out of their trigger button on Liquid Glass. Two changes affect existing code: **the menu label hides while the menu is open** (plan for this if the label conveyed state — some teams have adopted the third-party `FixedMenu` package as a workaround), and **icons always appear leading**, even if your code ordered them differently. A known iOS 26.1 regression breaks the morphing animation when a `Menu` lives inside a `GlassEffectContainer` — apply `.glassEffect(.regular.interactive())` directly on the Menu as a workaround.

### `MenuStyle` reference

```swift
Menu("Options") { Button("One") { }; Button("Two") { } }
    .menuStyle(.borderlessButton)    // macOS: no border/chevron
    .buttonStyle(.bordered)          // iOS: capsule background
    .menuIndicator(.hidden)          // hides the chevron (iOS 15+)
```

---

## Destructive confirmations done right

**Ask for confirmation only when data loss is unexpected and irreversible.** The HIG draws a crisp line: *"Warn people when they initiate a task that can cause data loss that's unexpected and irreversible. In contrast, don't warn people when data loss is the expected result of their action."* If the user just tapped a "Discard Draft" button, an extra "Are you sure?" is over-confirming — they told you twice already. If the user tapped a small trash icon on a row, a confirmation is appropriate because single-touch destruction of content is accidental-prone.

The canonical delete flow has three rules. First, make the destructive button red via `role: .destructive` — the system styles it, positions it correctly (trailing in alerts, top in action sheets, bottom in context menus), and never makes it the default Return-key target. Second, use a **specific verb** in the button label: "Delete," "Erase," "Discard Changes," "Remove Photo" — never "OK," "Yes," "No." Third, pair it with a Cancel button using `role: .cancel` so SwiftUI bolds it as the safe default.

**Prefer undo over confirmation when possible.** Many destructive actions are better served by doing the thing immediately and offering an undo: a swipe-to-delete with undo banner, shake-to-undo, or a Mail-style "1 message archived — Undo." This is less friction and more respectful of the user's attention. Reserve up-front confirmation for actions that cannot be undone (empty trash, delete account, erase device, sign out of iCloud account on this device, unrecoverable network operations).

A good confirmation dialog template:

```swift
.confirmationDialog(
    "Delete \(note.title)?",
    isPresented: $confirming,
    titleVisibility: .visible
) {
    Button("Delete", role: .destructive) { delete(note) }
    Button("Cancel", role: .cancel) { }
} message: {
    Text("This note will be deleted from all your devices.")
}
```

Apple's SwiftUI sample code famously shows `confirmationDialog("Are you sure?", …)`, but the HIG writing guidance prefers descriptive titles. **"Delete this draft?" beats "Are you sure?"** every time — it tells the user what they are confirming.

---

## Error presentation: inline, alert, or ambient

The right error surface depends on severity and recoverability. Apple frames this in HIG → Feedback: *"The most effective feedback tends to match the significance of the information to the way it's delivered."*

**Inline errors are the default for recoverable input problems.** An email field that lost focus with an invalid value gets a red helper text beneath it, not an alert. The user stays in the flow, sees exactly what to fix, and corrects it without a modal interruption. Inline errors are always visible, always contextual, and never block scrolling.

```swift
TextField("Email", text: $email)
    .textContentType(.emailAddress)
    .textInputAutocapitalization(.never)

if let error = emailError {
    Text(error)
        .font(.footnote)
        .foregroundStyle(.red)
}
```

**Alerts are for non-recoverable or blocking problems.** Network failed while saving and the user cannot proceed without knowing? Alert. Subscription required before continuing? Alert. Attempting to leave a screen with unsaved work? Alert. The common thread: the user must decide or acknowledge before they can continue.

**Ambient/toast-style feedback has no first-party SwiftUI API.** Apple does not provide a native toast. For transient confirmations ("Copied to clipboard," "Saved"), the platform conventions are: haptic feedback, status text in an existing toolbar/nav bar, **TipKit** (iOS 17+) for actionable discoverability tips, and **`ContentUnavailableView`** (iOS 17+) for empty states. Third-party toast packages exist (AlertToast, SimpleToast, swiftui-toasts) if you need classic toast semantics.

```swift
// iOS 17+ empty state
ContentUnavailableView {
    Label("No snippets", systemImage: "swift")
} description: {
    Text("You don't have any saved snippets yet.")
} actions: {
    Button("Create Snippet") { createNew() }
        .buttonStyle(.borderedProminent)
}

// iOS 17+ search empty state (localized, matches Apple apps)
ContentUnavailableView.search(text: query)
```

**When each fits.** Use inline errors for field validation, soft warnings beside a control, and any recoverable problem where context matters. Use alerts for critical failures that block progress, destructive confirmations needing explanation, and security prompts. Use ambient feedback (integrated status, TipKit, haptics) for success confirmations, discoverability hints, and anything that does not require user action. The anti-pattern in both directions is common: developers turn validation errors into alerts (user fatigue) or try to deliver genuinely critical failures as toasts (users miss them).

---

## Writing alert and dialog copy

Apple's HIG writing guidance for alerts is specific and worth internalizing. **Titles should be short, descriptive, multiword, and avoid ending punctuation for fragments.** A good alert title reads like a headline or a question: *"Delete this draft?"* — not *"Warning"* and not *"Are you sure?"*. Single-word titles rarely convey anything useful.

**Messages add context only when context is needed.** If the title and buttons are clear, skip the message. When you write one, use complete sentences, sentence-style capitalization, and two lines or fewer. Avoid sounding accusatory or insulting. HIG: *"It's better to be negative and direct than positive and oblique."* A user who couldn't sync doesn't need a cheerful "Oops, something went wrong!" — they need to know what happened and what to do.

**Button labels are verbs, one or two words, title-case, no ending punctuation.** The single most-cited Apple rule: *"Avoid using OK as the default button title unless the alert is purely informational."* A button labeled "Delete" tells the user precisely what will happen. "OK" leaves them asking whether they are agreeing to proceed or acknowledging a warning. Replace "Yes"/"No" with specific verbs — "Delete"/"Cancel," "Discard Changes"/"Keep Editing," "Sign Out"/"Stay Signed In."

Apple's concrete rules in one list:

- **Verb-first, result-describing button labels.** "View All," "Reply," "Ignore," "Delete," "Erase." Never "OK" in a decision alert.
- **Always label a cancellation button "Cancel."** Don't get creative with "Nevermind" or "Go Back."
- **Destructive buttons get `role: .destructive`** — the system colors them red and positions them correctly.
- **Never assign the primary role to a destructive button.** HIG: *"Because of its visual prominence, people sometimes choose a primary button without reading it first."*
- **Alert titles use sentence-style capitalization** in Apple's current iOS examples. (HIG has legacy guidance allowing title-style for fragments; match current Apple apps.)
- **Button labels use title-style capitalization.** "Delete Photo," not "Delete photo."
- **No ending punctuation on titles that are fragments** or on button labels.
- **Avoid explaining the buttons in the message.** If "Delete" and "Cancel" need a paragraph of explanation, rewrite the buttons.

"Are you sure?" deserves its own call-out. It is technically valid and Apple's own sample code uses it, but it fails the HIG's own guidance by being unspecific — it forces the user to re-read the button labels to remember what they are confirming. **Prefer a title that names the action**: "Delete this message?", "Log out of all devices?", "Empty the Trash?". Reserve "Are you sure?" for cases where the action is genuinely ambiguous and only asked once per session.

---

## Anti-patterns

These are the explicit don'ts from Apple's HIG and the most common abuses I see in code review. Each line maps to a specific HIG rule.

**Modality mistakes**

- ❌ **Alert for non-blocking info.** HIG: *"Avoid using an alert merely to provide information."* Use inline status, a toast-like status view, or TipKit.
- ❌ **Single-button "OK" alerts** to announce successes. Replace with a checkmark, haptic, or status update.
- ❌ **Over-confirming reversible actions.** If the action can be undone with a swipe or a tap, skip the confirmation and offer undo instead.
- ❌ **Under-confirming irreversible actions.** A one-tap "Delete Account" with no confirmation is hostile.
- ❌ **Modal view stacked above a popover** (HIG explicitly forbids — only alerts may appear over popovers).
- ❌ **Cascading popovers.** Never show one popover emerging from another.
- ❌ **Popovers on iPhone / compact width.** HIG: *"Avoid displaying popovers in compact views."* Use a sheet instead.
- ❌ **Popover used as a warning.** HIG: *"People can miss a popover or accidentally close it. If you need to warn people, use an alert instead."*

**Menu and action-sheet mistakes**

- ❌ **Menu for a single action.** If there's only one item, use a plain `Button`. HIG wants at least three items to justify a menu.
- ❌ **Menu hiding a view's primary actions.** Primary actions must be immediately discoverable on the surface.
- ❌ **Action sheet when a pull-down menu would do.** Since iOS 14, menus replace most action-sheet use cases — reserve action sheets for confirmations and multi-choice branches.
- ❌ **Scrolling action sheets.** If it doesn't fit, use a different surface.
- ❌ **Listing keyboard shortcuts inside a context menu.** They belong in the Mac/iPad menu bar.

**Context menu mistakes**

- ❌ **Context menu as the only way to access a feature.** Gestures are hidden; always expose commands in a visible control too.
- ❌ **Both context menu and edit menu on the same item.** The system can't infer intent and users get confused.
- ❌ **Advanced/rarely-used commands only in a context menu.** Context menus are for frequent per-item actions, not settings dumps.

**Writing and label mistakes**

- ❌ **"OK" / "Yes" / "No" as destructive button labels.** Use the specific verb ("Delete," "Discard," "Remove").
- ❌ **"Are you sure?"** as the alert title when a descriptive title ("Delete this draft?") would work.
- ❌ **Primary role on destructive buttons.** The safe button should be the default Return-key target.
- ❌ **"Click here" / "Tap here" links.** Accessibility-hostile; use descriptive phrases.
- ❌ **Cute or oblique copy** ("Oopsie!", "Let's do this!"). Be direct.

**iOS 26-specific mistakes**

- ❌ **Custom `.presentationBackground(.ultraThinMaterial)`** on sheets/dialogs — overrides Liquid Glass. Remove these.
- ❌ **Attaching `.alert` or `.confirmationDialog` to a distant parent view** — the Liquid Glass morph animates from the attachment point. Attach to the trigger.
- ❌ **Manual `HStack { Image; Text }` in Menu items** — iOS 26 forces icon-leading order. Use `Label(_:systemImage:)`.
- ❌ **Relying on the Menu label for state** — the label hides while the menu is open on iOS 26.

---

## WWDC session index

Use these sessions as primary sources when the HIG needs context. Priority order for current work is WWDC 2025 sessions 323 and 356 (iOS 26 design system) plus WWDC 2020 session 10205 (foundational menus-vs-action-sheets decision).

**Foundational**
- **WWDC 2020 Session 10205 — "Design with iOS pickers, menus and actions."** The origin of the iOS 14 menu era and still the clearest explanation of when a menu replaces an action sheet.
- **WWDC 2020 Session 10052 — "Build with iOS pickers, menus and actions."** API companion.
- **WWDC 2021 Session 10018 — "What's new in SwiftUI."** Introduced `.alert(_:isPresented:actions:message:)` and `confirmationDialog`, deprecating the old `Alert` struct and `ActionSheet`.

**iPad and menu-bar alignment**
- **WWDC 2022 Session 10058 — "SwiftUI on iPad: Organize your interface."** Multi-select context menus.
- **WWDC 2022 Session 110343 — "SwiftUI on iPad: Add toolbars, titles, and more."** Title menus via `toolbarTitleMenu(content:)`.
- **WWDC 2022 Session 10009 — "What's new in iPad app design."**

**Dialog customization**
- **WWDC 2023 Session 10148 — "What's new in SwiftUI."** `.dialogSeverity(.critical)`, `.dialogSuppressionToggle`, `HelpLink`, `.presentationCompactAdaptation(.popover)`, spring-loaded buttons.

**iOS 18 presentation work**
- **WWDC 2024 "What's new in SwiftUI."** `presentationSizing` modifier, zoom navigation transitions, `TabSection`.

**iOS 26 / Liquid Glass (most relevant now)**
- **WWDC 2025 Session 219 — "Meet Liquid Glass."** Design principles and the navigation-layer framing.
- **WWDC 2025 Session 356 — "Get to know the new design system."** Menus' left-column icons, shared anatomy of menu/context-menu/pop-up, symbols-over-text guidance.
- **WWDC 2025 Session 323 — "Build a SwiftUI app with the new design."** Alerts, menus, popovers, sheets, and dialogs morphing from their trigger; partial-detent floating sheets; `glassEffect` APIs; `ToolbarSpacer`; automatic toolbar grouping.
- **WWDC 2025 Session 284 — "Build a UIKit app with the new design."** iPhone action sheets now source-anchored like iPad; inline action sheets lose Cancel.
- **WWDC 2025 Session 208 — "Elevate the design of your iPad app."** iPad menu-bar design: order by frequency, symbols on every item, dim (don't hide) unavailable items.
- **WWDC 2025 Session 256 — "What's new in SwiftUI."** iOS 26 SwiftUI diff.
- **WWDC 2025 Session 359 — "Design foundations from idea to interface."** Warning not to lead UX with a menu.

**WWDC 2026** runs June 8–12, 2026 — it has not happened yet as of April 20, 2026, so no session content exists. iOS 27 and any further evolution of these APIs will be announced then.

---

## Conclusion

The surfaces Apple gives you are not interchangeable and they are not decorative. **Alerts interrupt; confirmation dialogs confirm user-initiated actions; menus list related options near their trigger; context menus accelerate power-users; sheets host sub-tasks; inline errors fix inputs in place.** The most common mistake in production SwiftUI code is reaching for the heaviest surface — usually an alert — when a lighter one would respect the user's attention better. The second most common is putting unique functionality only in a context menu, where most users will never find it.

iOS 26 raises the stakes on one specific mechanic: **modifier attachment point now drives animation quality**, because alerts, dialogs, menus, popovers, and sheets all morph out of the view you attached the modifier to. The fix is trivial — attach to the trigger — but the payoff is large: Liquid Glass makes correctly-placed modifiers feel physical and incorrectly-placed ones feel broken. Combined with the new `.confirm` and `.close` button roles, the iOS 26 platform pushes you toward cleaner, more semantic code by default.

The writing rules are the last 20% that separates acceptable from good. **Verb-first button labels, descriptive titles, and no "OK" in decision alerts** cost nothing and dramatically increase comprehension. "Delete Draft" and "Keep Editing" let a user act without reading the title. "OK" and "Cancel" force them to re-read everything. Treat every modal as interrupting attention you have borrowed — and design it to return that attention as quickly and clearly as possible.