---
name: controls
description: iOS UI controls reference (every standard control family, SwiftUI + UIKit, iOS 18/26)
platform: ios
---

# iOS UI Controls Reference — iOS 18 Baseline with iOS 26 Liquid Glass

**A definitive SwiftUI + UIKit lookup for iOS developers.** This reference covers every standard control family, when to use each, code for both declarative (SwiftUI) and imperative (UIKit) paths, style variations, anti-patterns, accessibility expectations, and WWDC session pointers. The baseline is iOS 18; iOS 26 changes are called out inline under **"iOS 26 / Liquid Glass"** headings.

---

## Table of contents

1. [How to read this reference](#1-how-to-read-this-reference)
2. [Buttons](#2-buttons)
3. [Toggles & switches](#3-toggles--switches)
4. [Lists](#4-lists)
5. [Forms](#5-forms)
6. [Text input](#6-text-input)
7. [Pickers & the Picker Decision Guide](#7-pickers--the-picker-decision-guide)
8. [DatePicker & ColorPicker](#8-datepicker--colorpicker)
9. [Sliders](#9-sliders)
10. [Steppers](#10-steppers)
11. [Progress indicators](#11-progress-indicators)
12. [Search](#12-search)
13. [iOS 26 Liquid Glass quick-reference](#13-ios-26-liquid-glass-quick-reference)
14. [Backward compatibility patterns](#14-backward-compatibility-patterns)
15. [Consolidated anti-pattern checklist](#15-consolidated-anti-pattern-checklist)
16. [Consolidated WWDC session index](#16-consolidated-wwdc-session-index)

---

## 1. How to read this reference

Every control family section follows the same anatomy: **visual description → primary use cases → SwiftUI code → UIKit equivalent → style variations table → anti-patterns → accessibility → WWDC references**. **Bold** marks the 1–3 facts you most need to remember in each section. Version tags (iOS 15+, iOS 17+, iOS 26+) indicate the minimum OS for each API; anything unmarked is iOS 13+ (SwiftUI baseline). Treat the decision tables as primary — the prose expands them.

The single most important meta-rule: **on iOS 26, recompile with Xcode 26 and your standard controls adopt Liquid Glass automatically.** You only need new APIs (`.buttonStyle(.glass)`, `.glassEffect`, `GlassEffectContainer`, `.searchToolbarBehavior`, `ToolbarSpacer`, `DefaultToolbarItem`, `.tabBarMinimizeBehavior`) when you want custom glass chrome or new search/tab-bar behaviors.

---

## 2. Buttons

Buttons are the most configurable control in SwiftUI. The triad you combine is **style (`buttonStyle`) × size (`controlSize`) × shape (`buttonBorderShape`)**, with an optional **role** (`.destructive`, `.cancel`) carrying semantic meaning. Get these four axes right and you rarely need a custom `ButtonStyle`.

### 2.1 Built-in `ButtonStyle` values

| Style | iOS | Visual | When to use |
|---|---|---|---|
| `.automatic` | 13+ | Resolves to `.borderless` on iOS | Default; let SwiftUI decide |
| `.plain` | 13+ | No chrome; dimming on press | Custom label views, card-style buttons, buttons inside `List` rows |
| `.borderless` | 13+ | Tint-colored label, no background | Inline text actions, "See all" links, toolbar-like hit zones |
| `.bordered` | 15+ | Translucent tinted capsule | Secondary actions, grouped button rows |
| `.borderedProminent` | 15+ | Solid tint fill with contrasting label | **Primary CTA — one per visual group** |
| `.glass` (iOS 26) | 26+ | Translucent Liquid Glass pill | Secondary actions under the new design |
| `.glassProminent` (iOS 26) | 26+ | Opaque, tintable Liquid Glass | Primary CTA under the new design |

```swift
Button("Cancel")   { }.buttonStyle(.bordered)
Button("Save")     { }.buttonStyle(.borderedProminent).tint(.indigo)

// iOS 26
Button("Save")     { }.buttonStyle(.glassProminent).tint(.blue)
Button("Cancel")   { }.buttonStyle(.glass)
```

`.tint(_:)` is the idiomatic way to color bordered and glass buttons — **never use `.foregroundColor` on the button itself**; it breaks the system's contrast calculations in dark mode and Increase Contrast.

### 2.2 Roles, sizes, shapes

`ButtonRole` (iOS 15+) is **semantic**, not decorative. `.destructive` renders in red AND re-orders the button in alerts/confirmation dialogs/menus; `.cancel` pins to the conventional cancel slot. Setting a role purely to obtain red color is an anti-pattern — use `.tint(.red)` on a role-less button instead.

`controlSize` values are `.mini`, `.small`, `.regular` (default), `.large`, and `.extraLarge` (iOS 17+). On iOS, size meaningfully affects only `.bordered`/`.borderedProminent`/`.glass*` styles — `.plain`/`.borderless` ignore it. `buttonBorderShape` offers `.automatic`, `.capsule`, `.roundedRectangle(radius:)`, and `.circle` (iOS 17+); it is ignored by unbordered styles. The canonical App Store "Get" button is the combination of all three axes:

```swift
Button("Get") { purchase() }
    .buttonStyle(.borderedProminent)
    .buttonBorderShape(.capsule)
    .controlSize(.small)
    .tint(.blue)
```

### 2.3 Destructive confirmation pattern

```swift
@State private var showConfirm = false

Button("Delete Account", role: .destructive) { showConfirm = true }
    .buttonStyle(.bordered)
    .confirmationDialog("Delete your account permanently?",
                        isPresented: $showConfirm, titleVisibility: .visible) {
        Button("Delete", role: .destructive) { vm.deleteAccount() }
        Button("Cancel", role: .cancel) { }
    } message: {
        Text("This action cannot be undone.")
    }
```

The outer button's role drives color; the inner dialog buttons' roles drive placement and emphasis in the system sheet. **Destructive full-swipe actions should pair with either `allowsFullSwipe: false` or an undo path** (see Lists).

### 2.4 UIKit — `UIButton.Configuration`

UIKit's modern button story (iOS 15+, WWDC 2021 session 10064 "Meet the UIKit button system") mirrors SwiftUI closely. Factory methods on `UIButton.Configuration` map to SwiftUI styles:

| SwiftUI | UIKit |
|---|---|
| `.buttonStyle(.plain)` | `.plain()` |
| `.buttonStyle(.borderless)` | `.borderless()` |
| `.buttonStyle(.bordered)` | `.tinted()` / `.bordered()` / `.borderedTinted()` |
| `.buttonStyle(.borderedProminent)` | `.filled()` / `.borderedProminent()` |
| `.controlSize(.large)` | `config.buttonSize = .large` (`.mini/.small/.medium/.large`) |
| `.buttonBorderShape(.capsule)` | `config.cornerStyle = .capsule` |
| `Button(role: .destructive) {}` | `button.role = .destructive` (iOS 14+) |
| `.buttonStyle(.glass)` (iOS 26) | New UIKit glass bezel via `UIButton.Configuration` (WWDC25 #284) |

```swift
var config = UIButton.Configuration.filled()
config.title = "Get"
config.image = UIImage(systemName: "cart")
config.imagePlacement = .leading
config.imagePadding = 8
config.buttonSize = .large
config.cornerStyle = .capsule
let button = UIButton(configuration: config,
                      primaryAction: UIAction { _ in purchase() })
button.role = .primary
```

### 2.5 Anti-patterns

- **Multiple `.borderedProminent` (or `.glassProminent`) per screen.** Dilutes the primary-action signal; one per visual group.
- **`.destructive` for reversible actions** like Archive or Hide. Red implies data loss.
- **Using role purely for color.** That's `.tint(.red)`'s job; role additionally changes placement/emphasis in alerts and menus.
- **Tap targets under 44×44 pt.** HIG minimum; wrap small icons with `.frame(minWidth: 44, minHeight: 44).contentShape(Rectangle())`.
- **`Text("Tap").onTapGesture { }` in place of `Button`** — loses `.isButton` trait, disabled state, keyboard-shortcut, focus.
- **Nesting `Button` in `Button`** — gesture conflicts; only the outer fires.
- **`Button` in a List row without `.buttonStyle(.plain)`** — whole row becomes the target.
- **`.foregroundColor` on a bordered/glass button** — breaks contrast; use `.tint(_:)`.

### 2.6 Accessibility

SwiftUI Buttons expose the `.isButton` trait and the label text automatically. For icon-only buttons, **you must supply `.accessibilityLabel(_:)`**. Bordered/glass styles scale padding with Dynamic Type; plain/borderless scale only text. Respect `@Environment(\.accessibilityReduceTransparency)` — the system auto-solidifies translucent styles when it's on. Provide `.accessibilityHint(_:)` when the button's effect is non-obvious, and `.accessibilityIdentifier(_:)` for UI testing.

### 2.7 Key WWDC sessions

- **WWDC19 #216** — SwiftUI Essentials (introduces `Button`, `Toggle`).
- **WWDC21 #10018** — What's new in SwiftUI (`.bordered`, `.borderedProminent`, `ButtonRole`, `controlSize`, `buttonBorderShape`).
- **WWDC21 #10064** — Meet the UIKit button system.
- **WWDC23 #10148** — What's new in SwiftUI (`.controlSize(.extraLarge)`, `.circle` border shape).
- **WWDC25 #323** — Build a SwiftUI app with the new design (`.glass`, `.glassProminent`).
- **WWDC25 #284** — Build a UIKit app with the new design (UIKit glass bezels).

---

## 3. Toggles & switches

A `Toggle` represents **persistent binary state**. If the UI should remember the value, it is a Toggle; if it triggers an action and reverts, it is a Button; if it's a 2-state choice whose labels carry meaning ("Metric/Imperial"), it is a segmented Picker.

### 3.1 Initializers and styles

```swift
Toggle("Airplane Mode", isOn: $isOn)
Toggle(isOn: $isOn) { Label("Wi-Fi", systemImage: "wifi") }
Toggle("Wi-Fi", systemImage: "wifi", isOn: $isOn)                 // iOS 17+
Toggle(sources: items, isOn: \.isEnabled) { Text("Enable all") }  // iOS 16+ mixed-state
```

| Style | Platforms | Visual | Use |
|---|---|---|---|
| `.automatic` | All | `.switch` on iOS, `.checkbox` on macOS | Default |
| `.switch` | iOS/iPadOS/macOS 13+/visionOS | Green sliding switch | Settings, Form rows |
| `.button` | iOS 15+, macOS 12+ | Rendered as a tint-filled toggleable button | Filter chips, editor format toolbars (Bold/Italic) |
| `.checkbox` | **macOS only** — compile error on iOS | Native checkbox | macOS forms only; on iOS make a custom `ToggleStyle` |

Apply with `.toggleStyle(.switch)` plus `.tint(_:)` for color. Older `SwitchToggleStyle(tint:)` is deprecated.

### 3.2 UIKit — `UISwitch`

```swift
let toggle = UISwitch()
toggle.isOn = true
toggle.onTintColor = .systemGreen
toggle.addTarget(self, action: #selector(changed(_:)), for: .valueChanged)
// setOn(_:animated:) does NOT fire .valueChanged
```

`UISwitch`'s frame width/height is fixed — use `CGAffineTransform(scaleX:y:)` or build a custom control if you truly need resizing.

### 3.3 iOS 26 / Liquid Glass

The switch knob transforms into Liquid Glass during interaction (visible lift and bounce). There is no new `.glassToggle` style — recompile and it adopts automatically. Respect `@Environment(\.accessibilityReduceMotion)` for any custom toggle animations.

### 3.4 Anti-patterns and accessibility

Using `.toggleStyle(.checkbox)` on iOS is a compile error — macOS only. Custom `ToggleStyle` implementations must remember to call `configuration.isOn.toggle()` or the switch appears broken, and should add `.isSelected` trait when on so VoiceOver announces state. VoiceOver reads `Toggle("Wi-Fi", isOn: $on)` as **"Wi-Fi, switch button, on"** with no extra work. Use a Toggle when state persists; use a Button when state doesn't.

---

## 4. Lists

`List` is a lazy vertical container optimized for selection, swipe actions, edit mode, and platform-native row styling. On iOS it renders as `UITableView` under `.plain`/`.grouped`/`.insetGrouped`/`.inset` styles, and `UICollectionView` with list configuration under `.sidebar`.

### 4.1 List styles

| Style | iOS | Visual | Use |
|---|---|---|---|
| `.automatic` | 13+ | Platform default (insetGrouped on iOS in a NavigationStack) | Default |
| `.plain` | 13+ | Full-bleed rows, thin separators, sticky headers | Feeds, search results, mail |
| `.grouped` | 13+ | Full-width grouped with tinted section bg | Legacy Settings look |
| `.insetGrouped` | 14+ | Rounded-corner inset cards | **iOS default — Settings/data-entry** |
| `.inset` | 14+ | Plain, horizontally inset | Plain with lateral breathing room |
| `.sidebar` | 14+ | Collapsible disclosure sections | NavigationSplitView primary column |

### 4.2 Dynamic rows, selection, edit mode

Use `ForEach` for any mutation-supporting row set (`.onDelete`, `.onMove`, `.swipeActions` all attach to `ForEach`, not to `List`-initialized-from-data):

```swift
List {
    ForEach(items) { item in row(for: item) }
        .onDelete { offsets in items.remove(atOffsets: offsets) }
        .onMove   { from, to in items.move(fromOffsets: from, toOffset: to) }
}
```

Selection bindings drive single- vs multi-select:

```swift
@State private var selection = Set<Contact.ID>()
List(contacts, selection: $selection) { Text($0.name) }
    .toolbar { EditButton() }
```

`EditButton()` flips the `\.editMode` environment binding between `.active` and `.inactive` and localizes its label ("Edit" ↔ "Done") automatically. **Since iOS 16, multi-select works on iPhone without first entering edit mode** — Edit is now only required for `.onDelete`/`.onMove` reordering.

### 4.3 Swipe actions

```swift
row.swipeActions(edge: .leading) {
    Button { pin(item) } label: { Label("Pin", systemImage: "pin") }.tint(.orange)
}
.swipeActions(edge: .trailing, allowsFullSwipe: false) {
    Button(role: .destructive) { delete(item) } label: { Label("Delete", systemImage: "trash") }
    Button { archive(item) } label: { Label("Archive", systemImage: "archivebox") }.tint(.indigo)
}
```

Only the **first** action on an edge is the full-swipe action; tint via `.tint(_:)`; destructive role auto-animates row removal. Adding `.swipeActions` overrides the implicit delete that `.onDelete` would render — if you want both behaviors, supply your own destructive button.

### 4.4 Row & section modifiers

`.listRowSeparator(.hidden)`, `.listRowSeparatorTint(_:)`, `.listRowBackground(_:)`, `.listRowInsets(_:)`, `.listSectionSpacing(_:)` (iOS 17+), and `.alignmentGuide(.listRowSeparatorLeading)` (iOS 16+) shape row appearance without escaping to UIKit. For the empty state, use **`ContentUnavailableView`** (iOS 17+), including `ContentUnavailableView.search(text:)` for empty-search UX. `.refreshable { await reload() }` attaches pull-to-refresh.

### 4.5 UIKit equivalents

`List` ↔ `UITableView` or `UICollectionView` with `UICollectionLayoutListConfiguration`. Swipe actions ↔ `UISwipeActionsConfiguration` with `UIContextualAction` (`.normal`/`.destructive`). `EditButton()` ↔ `editButtonItem` + `setEditing(_:animated:)`. Selection ↔ `allowsMultipleSelection` + `indexPathsForSelectedRows`. Modern data flow uses `UITableViewDiffableDataSource<Section,Item>` with `NSDiffableDataSourceSnapshot`.

### 4.6 iOS 26 / Liquid Glass

**List content does not become glass.** Apple's explicit WWDC25 guidance is that Liquid Glass belongs to the navigation layer, never content. `List` and `Form` backgrounds remain opaque so they don't fight the glass toolbar/tab bar floating above them. When presenting a Form inside a partial-detent sheet (where the glass sheet background would otherwise be hidden by the Form's background), toggle `.scrollContentBackground(.hidden)` while at a small detent. macOS Tahoe's List loads large datasets ~6× faster and updates ~16× faster than before, per session 256.

### 4.7 Anti-patterns

- Using `List` for 3 static rows — prefer `VStack` inside `ScrollView`.
- Duplicate IDs in nested `ForEach` (breaks animations and identity).
- Destructive full-swipe with no undo path.
- Using `Form` for dashboards — its opinionated styles (menu pickers, switch toggles) look wrong for catalogs or read-only displays. Use `List` + `.listStyle(.insetGrouped)` if you want only the visual.
- Applying `.glassEffect` to list rows on iOS 26 — violates Apple's layering guidance.
- Calling `.onDelete`/`.onMove` on `List(items)` rather than on a nested `ForEach` — silently does nothing.

### 4.8 Accessibility

Wrap multi-view rows with `.accessibilityElement(children: .combine)` so VoiceOver reads them as one element. **Swipe actions are invisible to VoiceOver** — expose them with `.accessibilityActions { Button("Delete") {…}; Button("Archive") {…} }` (iOS 16+). Section headers gain the heading trait automatically. Dynamic Type auto-resizes row height; avoid fixed `.frame(height:)` on rows, and use `@ScaledMetric` for padding and icon sizes.

### 4.9 Key WWDC sessions

- **WWDC20 #10031** — Stacks, Grids, and Outlines in SwiftUI (sidebar, selection).
- **WWDC21 #10018** — `.swipeActions`, `.refreshable`, `.listRowSeparator`.
- **WWDC22 #10058** — SwiftUI on iPad: Organize your interface (selection, EditButton on iPad).
- **WWDC23 #10148** — What's new in SwiftUI (`ContentUnavailableView`).
- **WWDC24 #10073** — Catch up on accessibility in SwiftUI.

---

## 5. Forms

`Form` is a `List`-like container with opinionated data-entry styling. **Inside a `Form`, Pickers default to `.menu`, Toggles to `.switch`, labels align leading with values trailing.** `Form { ... }.formStyle(.grouped)` (iOS 16+) is the explicit iOS-default style; macOS gained a matching System-Settings-style form at WWDC22.

### 5.1 Mixed-control example

```swift
Form {
    Section("Profile") {
        TextField("Name", text: $name).textContentType(.name)
        SecureField("Password", text: $password).textContentType(.newPassword)
        LabeledContent("Member since", value: joinDate.formatted(date: .abbreviated, time: .omitted))
    }
    Section("Preferences") {
        Toggle("Notifications", isOn: $notify)
        Picker("Theme", selection: $theme) {
            ForEach(Theme.allCases) { Text($0.title).tag($0) }
        }                                                 // .menu style by default in Form
        Stepper("Guests: \(guests)", value: $guests, in: 1...20)
        ColorPicker("Accent", selection: $accent, supportsOpacity: false)
    }
    Section("Schedule") {
        DatePicker("When", selection: $date, displayedComponents: [.date, .hourAndMinute])
    }
}
.navigationTitle("Settings")
```

**`LabeledContent`** (iOS 16+) is the idiomatic read-only "row with value" primitive: `LabeledContent("Version") { Text("4.2.1").monospacedDigit() }`.

### 5.2 Form-specific picker behavior

Inside a Form, `Picker` defaults to `.menu`; you can override with `.segmented`, `.wheel`, `.inline`, or (iOS 16+, iOS only, requires a `NavigationStack` ancestor) `.navigationLink`. Use `.labelsHidden()` with `.inline` so the title doesn't look like a row itself. See Section 7 for the full decision guide.

### 5.3 UIKit equivalents

iOS UIKit has no first-class `Form` container — the standard approach is a `UITableView` with `.insetGrouped` style, specializing cells per row type (`UISwitch`, `UIDatePicker`, `UITextField`, `UIPickerView` or pull-down `UIButton` with `UIMenu`, `UIColorWell`/`UIColorPickerViewController`). iOS 15+ modern pull-down menus on `UIButton` largely replace `UIPickerView` for discrete-value rows.

### 5.4 Anti-patterns specific to Form

Forms in non-settings contexts impose styling that looks wrong in dashboards. Hiding the scroll background without supplying one (`.scrollContentBackground(.hidden)` then no `.background`) yields a transparent region that exposes window chrome. On iOS 26, a Form inside a partial-detent sheet covers the sheet's glass — hide the background when at a small detent.

---

## 6. Text input

Text entry in SwiftUI is layered: `TextField` / `SecureField` for single-line or multiline growing input, `TextEditor` for long-form, `@FocusState` for focus orchestration, and a rich set of keyboard/content/autofill modifiers. Getting `textContentType` + `keyboardType` + `textInputAutocapitalization` + `autocorrectionDisabled` right is the single largest UX win in most apps.

### 6.1 TextField fundamentals

```swift
TextField("Email", text: $email, prompt: Text("you@example.com"))  // iOS 15+
TextField("Notes", text: $notes, axis: .vertical)                  // iOS 16+
    .lineLimit(1...5)                                              // grow 1 → 5 lines
TextField("Amount", value: $amount,
          format: .currency(code: Locale.current.currency?.identifier ?? "USD"))
    .keyboardType(.decimalPad)                                     // iOS 15+ typed input
```

| Style | iOS | Visual |
|---|---|---|
| `.automatic` | 13+ | Platform default (iOS unbordered) |
| `.plain` | 13+ | No chrome at all |
| `.roundedBorder` | 13+ | System rounded-rect bezel |

### 6.2 Keyboard types (complete `UIKeyboardType` list)

`.default`, `.asciiCapable`, `.numbersAndPunctuation`, `.URL`, `.numberPad`, `.phonePad`, `.namePhonePad`, `.emailAddress`, `.decimalPad`, `.twitter`, `.webSearch`, `.asciiCapableNumberPad` — this last one is critical for OTP/PIN inputs as it guarantees ASCII digits only.

### 6.3 Content types (complete `UITextContentType` list)

**Names:** `.name`, `.namePrefix`, `.givenName`, `.middleName`, `.familyName`, `.nameSuffix`, `.nickname`, `.jobTitle`, `.organizationName`.
**Addresses:** `.location`, `.fullStreetAddress`, `.streetAddressLine1`, `.streetAddressLine2`, `.addressCity`, `.addressState`, `.addressCityAndState`, `.sublocality`, `.countryName`, `.postalCode`.
**Contact:** `.telephoneNumber`, `.emailAddress`, `.URL`, `.creditCardNumber`.
**Auth:** `.username` (iOS 11+), `.password` (iOS 11+), `.newPassword` (iOS 12+ — triggers strong-password suggestion), `.oneTimeCode` (iOS 12+ — enables SMS autofill).
**Shipment/Flight:** `.shipmentTrackingNumber`, `.flightNumber` (iOS 15+).
**iOS 17+ additions:** `.dateTime`, `.creditCardExpiration`, `.creditCardExpirationMonth`, `.creditCardExpirationYear`, `.creditCardSecurityCode`, `.creditCardType`, `.creditCardName`, `.creditCardGivenName`, `.creditCardMiddleName`, `.creditCardFamilyName`, `.birthdate`, `.birthdateDay`, `.birthdateMonth`, `.birthdateYear`.

### 6.4 Submit labels and focus orchestration

`SubmitLabel` values (iOS 15+): `.done`, `.go`, `.send`, `.search`, `.next`, `.continue`, `.return`, `.route`, `.join`. Pair with `.onSubmit { }` (scoped with `SubmitTriggers.text` vs `.search`).

```swift
enum Field: Hashable { case email, password }
@FocusState private var focus: Field?

Form {
    TextField("Email", text: $email)
        .textContentType(.username).keyboardType(.emailAddress)
        .submitLabel(.next).focused($focus, equals: .email)
    SecureField("Password", text: $password)
        .textContentType(.password)
        .submitLabel(.go).focused($focus, equals: .password)
}
.onSubmit {
    switch focus {
    case .email:    focus = .password
    case .password: submit()
    case .none:     break
    }
}
.onAppear { focus = .email }
```

**Setting `focus = nil` dismisses the keyboard.** Enum-based `@FocusState` beats multiple `Bool`s because only one case can be active at a time.

### 6.5 TextEditor and iOS 26 rich text

`TextEditor(text: $notes)` is your long-form input. `.textEditorStyle(.plain)` (iOS 17+) strips chrome. There is **no built-in placeholder** — overlay a `Text` with `.allowsHitTesting(false)` when `text.isEmpty`. On iOS 26, `TextEditor` accepts a `Binding<AttributedString>` directly plus an `AttributedTextSelection` binding:

```swift
@State private var text = AttributedString()
@State private var selection = AttributedTextSelection()

TextEditor(text: $text, selection: $selection)   // iOS 26: full rich text, ⌘B/⌘I/⌘U for free
```

Custom toolbars mutate attributes via `text.transformAttributes(in: &selection) { container in … }`. See WWDC25 #280 "Cook up a rich text experience in SwiftUI with AttributedString."

### 6.6 Validation UX

The accepted pattern is **inline error on blur**, not alert-on-submit:

```swift
TextField("Email", text: $email)
    .focused($focused)
    .onChange(of: focused) { _, isFocused in
        if !isFocused { emailError = validate(email) }
    }
    .overlay(RoundedRectangle(cornerRadius: 8)
        .stroke(emailError == nil ? Color.secondary : Color.red))
if let emailError {
    Text(emailError).font(.caption).foregroundStyle(.red)
}
```

Disable the submit button until the form is valid rather than showing a post-submit alert. Use `TextField(value:format:)` (typed input) when a field represents a non-`String` type so parsing/formatting and commit cycles are handled for you.

### 6.7 UIKit equivalents

`TextField` ↔ `UITextField` with `UITextFieldDelegate`, `textContentType`, `keyboardType`, `autocapitalizationType`, `autocorrectionType`, `returnKeyType`, `isSecureTextEntry`. `TextEditor` ↔ `UITextView` (TextKit 2 by default on iOS 16+) with `isEditable`, `isSelectable`, `attributedText`. `becomeFirstResponder()` / `resignFirstResponder()` are the UIKit analog of `@FocusState`.

### 6.8 Anti-patterns

- Omitting `textContentType` on login screens — breaks password autofill and strong-password suggestion.
- Splitting a 6-digit OTP into six single-char fields — defeats SMS autofill. Use a single field with `.textContentType(.oneTimeCode)` and `.keyboardType(.numberPad)` (or `.asciiCapableNumberPad`).
- Wrong keyboard type — email with `.default`, phone with `.default`.
- `TextField` for multi-paragraph content (use `TextEditor` or `TextField(axis: .vertical)`).
- Disabling autocorrect globally — do so only where it hurts (emails, usernames, codes).
- Validation surfaced only via alert on submit — inline on blur is the norm.
- Reading `\.isSearching` on the same view that applies `.searchable` — it only publishes to descendants. Extract a child view.

### 6.9 Accessibility

SecureField automatically suppresses character-by-character VoiceOver speaking; ensure `.textContentType(.password)`/`.newPassword` is set so QuickType cooperates. For error announcements, post `AccessibilityNotification.Announcement("Error: invalid format").post()` on commit failure. Programmatic `@FocusState` changes move VoiceOver focus too — use them to jump to the first error on submit.

### 6.10 Key WWDC sessions

- **WWDC21 #10023** — Direct and reflect focus in SwiftUI.
- **WWDC21 #10109** — What's new in Foundation (`ParseableFormatStyle`, typed `TextField`).
- **WWDC22 #10052** — Multiline `TextField(axis:)`, `scrollDismissesKeyboard`.
- **WWDC23 #10162** — The SwiftUI cookbook for focus.
- **WWDC25 #280** — Cook up a rich text experience in SwiftUI with AttributedString.

---

## 7. Pickers & the Picker Decision Guide

Choosing the right picker is the single most common SwiftUI controls question. **The axes are option count × context × content type.**

### 7.1 Picker style comparison

| Style | iOS | Visual | Ideal count | Gotchas |
|---|---|---|---|---|
| `.automatic` | 13+ | Context-dependent | — | In a Form resolves to `.menu` on iOS 16+ |
| `.menu` | 14+ | Pull-down with current value inline | 3–12 | — |
| `.segmented` | 13+ | Horizontal pill of equal-width buttons | 2–5 | Text clips with 5+ or long labels |
| `.wheel` | 13+ (iOS/watchOS) | Spinning barrel | 10+ ordered | Huge vertical space; poor Dynamic Type |
| `.inline` | 14+ | All options inline (rows inside List/Form) | 3–8 | Use `.labelsHidden()` |
| `.navigationLink` | 16+, **iOS only** | Row pushes to selection list | 12+ | **Requires `NavigationStack` ancestor** |
| `.palette` | 17+ | Row of icons/colors inside a `Menu` | 3–8 visual | Outside a Menu, silently falls back to `.segmented` |
| `.radioGroup` | macOS 13+ only | Vertical radios | 2–5 | Not on iOS/iPadOS |

### 7.2 The Decision Guide

| # | Scenario | Recommended | Alternative | Why |
|---|---|---|---|---|
| 1 | Birthdate (past) | `DatePicker(.wheel)` or `.compact` in Form | `.graphical` | One of the few wheels justified — fast year scrolling |
| 2 | Future appointment | `DatePicker(.compact)` in Form | `.graphical` in a sheet | Compact is efficient; graphical shows day-of-week |
| 3 | 3 filter options | `Picker(.segmented)` top-of-screen | `.menu` | 2–5 items; always-visible state |
| 4 | 2 themes | `Toggle` | `.segmented` if tri-state ("System") | Binary = Toggle, not a menu picker |
| 5 | 50-country list | `Picker(.navigationLink)` in Form | Searchable List + NavigationLink | Long lists need search + full height |
| 6 | Color | `ColorPicker` | `Picker(.palette)` for curated swatches | System color wheel + opacity |
| 7 | Priority 1–5 | `Picker(.segmented)` with symbols | `Stepper` | 5 equal-weight choices fit |
| 8 | Quantity 1–99 | `Stepper` + `TextField` | — | Both precision and nudging |
| 9 | Volume 0–100% | `Slider` | `Slider(step: 5)` | Analog continuous → slider |
| 10 | Emoji reaction | `Picker(.palette)` inside `Menu` | Custom HStack | Canonical WWDC23 pattern |
| 11 | 6–12 sort options | `Picker(.menu)` from toolbar | `.navigationLink` in Form | Menu keeps toolbar light |
| 12 | Font size adjust | `Stepper` + `Slider` | — | Fine ±1 + range scan |
| 13 | Alarm hour/minute | `DatePicker(.wheel, components: .hourAndMinute)` | `.compact` | Canonical wheel use |
| 14 | Multi-day booking | `MultiDatePicker` (iOS 16+) | Two graphical DatePickers | Native multi-select |
| 15 | iPad Form filter | `Picker(.menu)` | `.segmented` if ≤5 | iPad has room but menu scales |

**`Menu` vs `Picker(.menu)`**: a `Menu` is a container for heterogeneous actions (buttons, toggles, sub-menus); `Picker(.menu)` is a single-selection binding. Nest `Picker(.palette)` inside a `Menu` for the "row of swatches in a pull-down" pattern.

### 7.3 UIKit equivalents

`Picker(.wheel)` ↔ `UIPickerView`. `Picker(.menu)` ↔ `UIButton` with `UIMenu` and `showsMenuAsPrimaryAction = true` (iOS 14+). `Picker(.segmented)` ↔ `UISegmentedControl`. There is no direct UIKit analog of `.navigationLink` or `.palette` — build them with `UITableViewController` pushes or `UIMenu` with custom `UIAction` icons.

### 7.4 iOS 26 notes

Menu-backed pickers render on a Liquid Glass surface with lensing (not blur); segmented pickers get a glass "lens" selection thumb that lifts and refracts content beneath when the user taps. **No new picker style was added in iOS 26**, but HIG guidance further de-emphasizes `.wheel` in favor of `.menu` because the glass motion suits pop-up presentations better.

### 7.5 Picker anti-patterns

- Wheel for a short list — especially on iPad.
- Segmented with 5+ items or long labels.
- Menu with only 2 options — use Toggle (or segmented if tri-state).
- `.navigationLink` outside a `NavigationStack` — silently does nothing.
- `.palette` outside a `Menu` — silently falls back to `.segmented`.
- Forgetting `.labelsHidden()` on `.inline` in Form — the title looks like another row.

### 7.6 Key WWDC sessions

- **WWDC20 #10205** — Design with iOS pickers, menus, and actions.
- **WWDC21 #10018** — `.menu` picker style improvements.
- **WWDC22 #10052** — `MultiDatePicker`, `Gauge`.
- **WWDC23 #10148** — `.palette` picker style, `paletteSelectionEffect`.
- **WWDC25 #256 / #323** — Liquid Glass picker treatments.

---

## 8. DatePicker & ColorPicker

### 8.1 DatePicker

| Style | iOS | Visual | Best use |
|---|---|---|---|
| `.automatic` | 14+ | Platform default | General |
| `.compact` | 14+ | Tappable chip → popover calendar | **Default in Form/List on iOS** |
| `.graphical` | 14+ | Full-size calendar + time | Booking flows; screen-dominant |
| `.wheel` | 13+ iOS/watchOS | Spinning wheels | Birthdate, alarm, timer |
| `.field` | macOS 13+ only | Text field + stepper arrows | macOS forms |

```swift
DatePicker("Appt", selection: $date,
           in: Date()...Date().addingTimeInterval(30*24*3600),
           displayedComponents: [.date, .hourAndMinute])
    .datePickerStyle(.graphical)

DatePicker("DOB", selection: $date, in: ...Date())   // PartialRangeThrough — no future
```

`displayedComponents` is an `OptionSet`: `.date`, `.hourAndMinute`, or both. `MultiDatePicker` (iOS 16+, no macOS/watchOS) binds to `Set<DateComponents>` and looks like a `.graphical` DatePicker with multi-selection. **There is no native range (start/end) DatePicker** — use two `DatePicker`s or community wrappers around `MultiDatePicker`.

UIKit equivalent: `UIDatePicker` with `preferredDatePickerStyle`: `.automatic`, `.wheels`, `.compact`, `.inline` (iOS 14+). `MultiDatePicker` ↔ `UICalendarView` + `UICalendarSelectionMultiDate` (iOS 16+).

### 8.2 ColorPicker

```swift
ColorPicker("Tint", selection: $color, supportsOpacity: true)
```

Binds to `Color` or `CGColor`. Renders a swatch well; tapping presents the system sheet (`UIColorPickerViewController`). SwiftUI exposes only label + `supportsOpacity`; drop to a `UIViewControllerRepresentable` wrapping `UIColorPickerViewController` for programmatic presentation, preset eyedropper, or custom initial tab.

### 8.3 Accessibility

`.wheel` DatePicker has known Dynamic Type clipping at AX5 — prefer `.compact`/`.graphical` when supporting large text. All DatePicker styles announce their current value without extra work; `.graphical` exposes calendar navigation via VoiceOver rotor.

---

## 9. Sliders

A `Slider` is for **continuous analog values**: volume, brightness, opacity, scrub position, filter intensity. If the value is a small integer count, use a Stepper or Picker. If it's a typed number the user will read back precisely, use `TextField(value:format:)`.

### 9.1 iOS 18 API

```swift
Slider(value: $v, in: 0...1)                                // continuous
Slider(value: $v, in: 0...100, step: 5)                     // discrete
Slider(value: $v, in: 0...1) {
    Text("Volume")                                          // VoiceOver label
} minimumValueLabel: {
    Image(systemName: "speaker.fill")
} maximumValueLabel: {
    Image(systemName: "speaker.wave.3.fill")
} onEditingChanged: { editing in
    if !editing { commit(v) }                               // drag ended
}
.tint(.pink)                                                // track color
.sensoryFeedback(.selection, trigger: Int(v))               // iOS 17+ haptics
```

**There is still no native two-thumb range slider in SwiftUI.** Roll your own with two `Circle`s and `DragGesture`, or use community packages (`spacenation/swiftui-sliders`, `brendanperry/RangeSlider`). iOS 26 adds tick marks but does not add a range slider.

### 9.2 iOS 26 / Liquid Glass (most notable control change)

Tick marks render automatically when `step:` is supplied, and a new `ticks:` closure accepts `SliderTick` and `SliderTickContentForEach` for custom positions and labels:

```swift
Slider(value: $pct) {
    Text("Percentage")
} currentValueLabel: {
    Text(pct, format: .percent)
} ticks: {
    SliderTickContentForEach(stride(from: 0.0, through: 1.0, by: 0.25).map { $0 }, id: \.self) { v in
        SliderTick(v) { Text(v, format: .percent) }
    }
}

// neutralValue: fills from a non-leading anchor (e.g., playback speed centered at 1.0×)
Slider(value: $speed, in: 0.5...2.0, neutralValue: 1.0)
```

Snapping-to-ticks behavior is built in. UIKit's `UISlider` also gains momentum, stretch-past-bounds, ticks, neutral value, and a thumbless "progress-bar" style (WWDC25 #284). **Pitfall:** on iOS the legacy `init(value:in:step:onEditingChanged:)` does not auto-show ticks — use an initializer that accepts a `label:` closure.

### 9.3 UIKit, anti-patterns, accessibility

UIKit: `UISlider` with `minimumValue`, `maximumValue`, `value`, `isContinuous`, `setThumbImage(_:for:)`. No native step — round in the `.valueChanged` handler.

Anti-patterns: Slider for 1–5 stars (use Stepper/Picker); Slider in a ScrollView without gesture priorities (scroll hijacks drag).

Accessibility: VoiceOver announces value and allows flick-up/down adjustment automatically. Provide a descriptive label via the `label:` closure. Override format with `.accessibilityValue("\(Int(v)) percent")`. Add `.sensoryFeedback(.selection, trigger: value)` (iOS 17+) for tactile steps.

---

## 10. Steppers

A `Stepper` is for **small integer adjustments**: quantity, guests, font size ±1. Over ~20 steps its UX collapses — switch to a Slider or TextField.

```swift
Stepper("Qty: \(qty)", value: $qty, in: 1...99, step: 1)
Stepper(value: $qty, in: 1...99) { Text("Qty"); Text("Under 99") }   // 2-line label
Stepper("Qty", onIncrement: { qty += 1 }, onDecrement: { qty = max(0, qty-1) })
```

### 10.1 Stepper + TextField (canonical pattern)

```swift
HStack {
    Text("Quantity")
    Spacer()
    TextField("Qty", value: $qty, format: .number)
        .keyboardType(.numberPad)
        .multilineTextAlignment(.trailing)
        .frame(width: 60)
        .onChange(of: qty) { _, new in
            qty = min(max(new, 0), 999)                              // clamp
        }
    Stepper("", value: $qty, in: 0...999).labelsHidden()
        .sensoryFeedback(.increase, trigger: qty)
}
.accessibilityElement(children: .combine)
.accessibilityLabel("Quantity")
.accessibilityValue("\(qty)")
```

### 10.2 UIKit, anti-patterns

UIKit: `UIStepper` with `minimumValue`, `maximumValue`, `stepValue` (default 1), `value`, `wraps` (default false), `autorepeat` (default true — press-hold accelerates), `isContinuous` (fires on every increment).

Anti-patterns: Stepper for >20 steps; stepper that doesn't clamp TextField edits to range.

On iOS 26, the ± control cluster gains a Liquid Glass pill backing; press-in state lights up.

---

## 11. Progress indicators

`ProgressView` unifies UIKit's split between `UIActivityIndicatorView` (spinner) and `UIProgressView` (linear bar). Which one you render is determined by whether you pass a value binding and by `.progressViewStyle`.

### 11.1 API

```swift
ProgressView()                               // indeterminate spinner
ProgressView("Loading…")                     // spinner with label
ProgressView(value: 0.4)                     // determinate (0...1)
ProgressView(value: bytes, total: totalBytes)
ProgressView(timerInterval: start...end)     // iOS 16+
```

| Style | iOS behavior |
|---|---|
| `.automatic` | Linear if determinate, circular spinner if not |
| `.linear` | Bar with optional label/current-value |
| `.circular` | **On iOS: always spinner — never a percentage ring**, even with a value. Use `Gauge` for a ring. |

### 11.2 For a percentage ring, use `Gauge` (iOS 16+)

```swift
Gauge(value: progress) { Text("Download") } currentValueLabel: {
    Text(progress, format: .percent)
}
.gaugeStyle(.accessoryCircularCapacity)
.tint(.blue)
```

`GaugeStyle` offers `.linearCapacity`, `.accessoryLinear`, `.accessoryLinearCapacity`, `.accessoryCircular`, `.accessoryCircularCapacity` (watchOS adds `.circular`, `.linear` for complications).

### 11.3 Loading-state best practices

- **Show spinner only after >500 ms** to avoid flicker (`try? await Task.sleep(for: .milliseconds(500))`).
- **Prefer skeletons** (content placeholders with `.redacted(reason: .placeholder)`) when the layout is knowable.
- **Prefer determinate progress** for any operation whose progress is knowable — downloads, uploads, exports.
- **Always supply an accessibility label.** A naked spinner reads only "In progress."
- `.controlSize(.large)` grows both spinner and linear bar.

### 11.4 UIKit, anti-patterns

UIKit: `UIProgressView` (linear determinate only — `progress: Float`, `progressTintColor`, `trackTintColor`) and `UIActivityIndicatorView` (spinner — `style: .medium/.large`, `startAnimating()` / `stopAnimating()`). No UIKit circular-percentage equivalent — bridge SwiftUI `Gauge` or draw with `CAShapeLayer`.

Anti-patterns: indeterminate spinner for long knowable operations; `.circular` expecting a ring on iOS; flicker from immediate spinner presentation; missing accessibility label.

---

## 12. Search

Search in SwiftUI is a single modifier — `.searchable` — that adapts placement and presentation to the platform and context. iOS 18 adds `Tab(role: .search)` for a dedicated search tab; iOS 26 overhauls presentation with Liquid Glass and bottom-anchored pills.

### 12.1 Base modifier (iOS 15+)

```swift
.searchable(text: $query, placement: .automatic, prompt: "Search")
```

`SearchFieldPlacement`: `.automatic`, `.navigationBarDrawer(displayMode: .automatic|.always)`, `.toolbar`, `.sidebar`. Read state with `@Environment(\.isSearching)` (from a **child view** — a common gotcha) and dismiss with `@Environment(\.dismissSearch)` invoking `dismissSearch()`.

### 12.2 Suggestions, scopes, tokens (iOS 16+)

```swift
.searchable(text: $query, placement: .toolbar, prompt: "Search notes")
.searchSuggestions {
    ForEach(topSuggestions, id: \.self) { s in Text(s).searchCompletion(s) }
}
.searchScopes($scope, activation: .onSearchPresentation) {
    Text("All").tag(Scope.all)
    Text("Inbox").tag(Scope.inbox)
    Text("Archive").tag(Scope.archive)
}
.onSubmit(of: .search) { runSearch() }
```

`SearchScopeActivation` (iOS 16.4+): `.automatic`, `.onSearchPresentation`, `.onTextEntry`. `.searchable(text:tokens:suggestedTokens:)` provides token-based search with `Identifiable` tokens.

### 12.3 iOS 18 — `Tab(role: .search)`

```swift
TabView {
    Tab("Home",    systemImage: "house")           { HomeView() }
    Tab("Library", systemImage: "books.vertical")  { LibraryView() }
    Tab(role: .search) {
        NavigationStack { SearchView() }.searchable(text: $query)
    }
}
```

A tab with `role: .search` gets a magnifying-glass glyph and pins to the trailing edge of the tab bar. UIKit equivalent: `UISearchTab` (subclass of `UITab`); set `automaticallyActivateSearch = true` to auto-focus the embedded `UISearchController` on tap.

### 12.4 iOS 26 — Liquid Glass search

On iPhone, `.searchable` on a `NavigationStack` places the field in a **bottom-anchored Liquid Glass pill above the keyboard** (within thumb reach). On iPad/Mac it sits top-trailing in the toolbar. New APIs:

- **`.searchToolbarBehavior(.minimize)`** — collapses the search field into a magnifying-glass toolbar button until tapped.
- **`.searchPresentationToolbarBehavior(_:)`** — configures toolbar items while search is presented.
- **`DefaultToolbarItem(kind: .search, placement: .bottomBar)`** + **`ToolbarSpacer(.flexible, placement: .bottomBar)`** — explicit bottom-bar placement.
- With `Tab(role: .search)`, the trailing search tab visually expands into the search field on tap.

```swift
NavigationStack {
    List(items) { … }
        .toolbar {
            ToolbarSpacer(.flexible, placement: .bottomBar)
            DefaultToolbarItem(kind: .search, placement: .bottomBar)
        }
        .searchable(text: $query, placement: .toolbar, prompt: "Search")
        .searchToolbarBehavior(.minimize)
}
```

### 12.5 UIKit equivalents

`UISearchController(searchResultsUpdater:)` installed via `navigationItem.searchController`. Toggle `navigationItem.hidesSearchBarWhenScrolling` for drawer-like behavior. `UISearchBar.scopeButtonTitles` + `showsScopeBar` for scopes. `UISearchTextField` supports `tokens: [UISearchToken]`. iOS 18+ tab-with-search uses `UISearchTab` added to `UITabBarController.tabs`.

### 12.6 Anti-patterns and accessibility

Attaching `.searchable` to a leaf detail view when you want global search — put it on the stack root. Forcing `.navigationBarDrawer(displayMode: .always)` overrides iOS 26 Liquid Glass placement; only use for the classic "always-visible under title" look. The searchable field auto-exposes search semantics to VoiceOver; provide a descriptive `prompt:` rather than relying on the generic "Search" string when context matters.

### 12.7 Key WWDC sessions

- **WWDC21 #10176** — Craft search experiences in SwiftUI.
- **WWDC22 #10052** — What's new in SwiftUI (scopes, tokens).
- **WWDC24 #10144 / #10147** — Tab API, search tab, iPadOS sidebar.
- **WWDC25 #323** — Build a SwiftUI app with the new design (Liquid Glass search).
- **WWDC25 #284** — Build a UIKit app with the new design (`UISearchTab`).

---

## 13. iOS 26 Liquid Glass quick-reference

**Liquid Glass is Apple's translucent, dynamic "digital meta-material" introduced at WWDC25 and shipped with iOS 26, iPadOS 26, macOS Tahoe 26, watchOS 26, tvOS 26, and visionOS 26.** Its design thesis: glass belongs to the **navigation layer** — bars, tabs, sheets, popovers, menus, alerts, and floating controls — never content. Recompiling with Xcode 26 grants automatic adoption for standard SwiftUI/UIKit chrome.

### 13.1 API cheat sheet

```swift
// Button styles
.buttonStyle(.glass)
.buttonStyle(.glassProminent)

// Generic glass material
.glassEffect(.regular, in: .capsule, isEnabled: true)
.glassEffect(.clear.tint(.blue).interactive())
.glassEffectID("id", in: namespace)
.glassEffectUnion(id: "group", namespace: ns)
.glassEffectTransition(.materialize)   // .identity, .matchedGeometry, .materialize

GlassEffectContainer(spacing: 20) { … }

// Toolbars
ToolbarSpacer(.flexible, placement: .bottomBar)
DefaultToolbarItem(kind: .search, placement: .bottomBar)
.sharedBackgroundVisibility(.hidden)

// Search
.searchToolbarBehavior(.minimize)
.searchPresentationToolbarBehavior(_:)

// Tab bar
Tab("Search", systemImage: "magnifyingglass", role: .search) { … }
.tabBarMinimizeBehavior(.onScrollDown)         // .automatic / .never / .onScrollDown
.tabViewBottomAccessory { NowPlayingView() }
@Environment(\.tabViewBottomAccessoryPlacement)

// Concentric corners (match device/container radius)
RoundedRectangle(cornerRadius: .containerConcentric, style: .continuous)

// Scroll edge + safe-area
.scrollEdgeEffectStyle(_:for:)
.backgroundExtensionEffect()
.containerBackground(.clear, for: .navigation)

// Morphing sheets
.matchedTransitionSource(id: in:)
.navigationTransition(.zoom(sourceID:in:))
```

### 13.2 `Glass` type

```swift
struct Glass {
    static var regular: Glass      // default, legible on any content
    static var clear: Glass        // high translucency; for bold/media-rich content
    static var identity: Glass     // no effect (for conditional disable)
    func tint(_ color: Color) -> Glass
    func interactive(_ enabled: Bool = true) -> Glass
}
```

**Glass cannot sample other glass.** Put adjacent or overlapping glass views inside a `GlassEffectContainer` so they share a sampling region and blend/morph together. Use `.glassEffectID(_:in:)` with a shared `Namespace` to make them morph as they appear/disappear across states.

### 13.3 Accessibility

Liquid Glass adapts to system settings automatically — **let the system handle it**:

| Setting | Effect |
|---|---|
| Reduce Transparency | Glass becomes frostier, obscures more background |
| Increase Contrast | Elements go predominantly black or white with high-contrast borders |
| Reduce Motion | Disables elastic bouncing and shimmer/morph |
| iOS 26.1 Tinted Mode | User slider to increase opacity system-wide |

Read environment values if you need to adapt custom glass surfaces: `\.accessibilityReduceTransparency`, `\.accessibilityReduceMotion`, `\.accessibilityShowButtonShapes`.

### 13.4 UIKit / AppKit analogs

- UIKit: `UIGlassEffect` (use via `UIVisualEffectView`). No `GlassEffectContainer` equivalent — bridge via `UIHostingController`.
- AppKit: `NSGlassEffectView` with a `contentView`, plus `NSGlassEffectContainerView` for grouping. Glass bezel style replaces the standard AppKit button backing (WWDC25 #310).

---

## 14. Backward compatibility patterns

### 14.1 Temporary opt-out

Add to **Info.plist** to keep the pre–Liquid Glass appearance while migrating:

```xml
<key>UIDesignRequiresCompatibility</key>
<true/>
```

Per Apple DTS (forum thread 802419), "We intend this option to be removed in the next major release" — treat it as expiring with iOS 27 / Xcode 27. Not available on watchOS.

### 14.2 Conditional API gating

```swift
extension View {
    @ViewBuilder
    func primaryCTAStyle() -> some View {
        if #available(iOS 26.0, *) {
            self.buttonStyle(.glassProminent)
        } else {
            self.buttonStyle(.borderedProminent)
        }
    }
}
```

```swift
extension View {
    @ViewBuilder
    func glassedBackground<S: Shape>(in shape: S = Capsule(),
                                     interactive: Bool = false) -> some View {
        if #available(iOS 26.0, *) {
            let glass: Glass = interactive ? .regular.interactive() : .regular
            self.glassEffect(glass, in: shape)
        } else {
            self.background(
                shape.fill(.ultraThinMaterial)
                    .overlay(LinearGradient(colors: [.white.opacity(0.3), .clear],
                                            startPoint: .topLeading, endPoint: .bottomTrailing))
                    .overlay(shape.stroke(.white.opacity(0.2), lineWidth: 1))
            )
        }
    }
}
```

For toolbar-spacer, default-toolbar-item, search-toolbar-behavior, tab-bar-minimize, and rich text `TextEditor`, wrap the entire toolbar/TabView/TextEditor block in `if #available(iOS 26.0, *)` branches.

### 14.3 Performance caution

Apple's docs flag Liquid Glass as **GPU-intensive**. Do not apply `.glassEffect` inside nested scrolling lists or per-cell; reserve it for top-level chrome. Test thermal behavior on iPhone 11–13. Avoid `.glassEffect` on iOS 26 betas where community-reported crashes exist — target iOS 26.1+ and a final-release SDK.

---

## 15. Consolidated anti-pattern checklist

The single checklist to audit a screen against. If any line applies, revisit the design.

- Multiple `.borderedProminent` / `.glassProminent` buttons in one visual group.
- `ButtonRole.destructive` on a reversible action (Archive, Hide, Mute).
- Role used purely for red color — use `.tint(.red)` instead.
- Tap target smaller than 44×44 pt.
- `Text(…).onTapGesture {}` where a `Button` belongs.
- `Button` inside `List` row without `.buttonStyle(.plain)`.
- `.foregroundColor` to color a bordered or glass button — use `.tint(_:)`.
- `.toggleStyle(.checkbox)` on iOS (compile error).
- `List` for 3 static rows — use `VStack` in `ScrollView`.
- Duplicate IDs across nested `ForEach`.
- Destructive full-swipe without undo.
- `Form` outside settings/data-entry (dashboards, catalogs).
- `.scrollContentBackground(.hidden)` without providing a replacement background.
- `TextField` for multi-paragraph content — use `TextEditor` or `axis: .vertical`.
- Missing `textContentType` on login/credit-card/address fields.
- OTP split into per-digit fields — defeats SMS autofill.
- Wrong `keyboardType` (email with `.default`).
- Globally disabling autocorrect.
- Validation as alert-on-submit rather than inline-on-blur.
- `.searchable` on a leaf view when you want global search.
- Reading `\.isSearching` on the same view that applies `.searchable`.
- Wheel picker on iPad, or for short option lists.
- Segmented picker with 5+ items or long labels.
- Menu picker for 2 options — use a Toggle.
- `.navigationLink` picker outside a `NavigationStack`.
- `.palette` picker outside a `Menu` (silently falls back to `.segmented`).
- `.inline` picker in Form without `.labelsHidden()`.
- DatePicker `.wheel` as default for general date input.
- Slider for discrete small counts — use Stepper/Picker.
- Stepper for >20 steps — use Slider/TextField.
- Stepper not clamping TextField edits to range.
- ProgressView `.circular` expecting a ring on iOS — use `Gauge`.
- Indeterminate spinner for knowable long operations.
- Spinner shown synchronously (no >500 ms debounce — causes flicker).
- `.glassEffect` on List rows (violates Liquid Glass layering).
- Re-adding custom toolbar/sheet backgrounds on iOS 26 (fights the glass).

---

## 16. Consolidated WWDC session index

| Year | # | Title | Relevance |
|---|---|---|---|
| 2019 | 216 | SwiftUI Essentials | Introduced `Button`, `Toggle`, `Picker` |
| 2019 | 238 | Accessibility in SwiftUI | Labels, hints, traits |
| 2020 | 10031 | Stacks, Grids, and Outlines in SwiftUI | Sidebar lists, selection |
| 2020 | 10205 | Design with iOS pickers, menus and actions | Picker HIG baseline |
| 2021 | 10018 | What's new in SwiftUI | `.bordered`/`.borderedProminent`, `ButtonRole`, `controlSize`, `buttonBorderShape`, `swipeActions`, `refreshable`, `submitLabel`, `.toggleStyle(.button)`, `.menu` picker refinements |
| 2021 | 10023 | Direct and reflect focus in SwiftUI | `@FocusState` |
| 2021 | 10064 | Meet the UIKit button system | `UIButton.Configuration` |
| 2021 | 10109 | What's new in Foundation | `ParseableFormatStyle`, typed `TextField` |
| 2021 | 10119 | SwiftUI Accessibility: Beyond the basics | Custom rotors, deep a11y |
| 2021 | 10176 | Craft search experiences in SwiftUI | `.searchable`, suggestions |
| 2022 | 10052 | What's new in SwiftUI | `LabeledContent`, multiline `TextField(axis:)`, search scopes/tokens, `MultiDatePicker`, `Gauge`, `formStyle(.grouped)` |
| 2022 | 10058 | SwiftUI on iPad: Organize your interface | Selection, EditButton patterns |
| 2022 | 10072 | The SwiftUI cookbook for navigation | `NavigationStack`, roles in nav |
| 2022 | 110343 | SwiftUI on iPad: Add toolbars, titles, and more | Toolbar placements |
| 2023 | 10148 | What's new in SwiftUI | `.controlSize(.extraLarge)`, `.circle` border shape, `.palette` picker, `ContentUnavailableView`, `Toggle(_:systemImage:)`, `.sensoryFeedback` |
| 2023 | 10160 | Demystify SwiftUI performance | List/ForEach identity |
| 2023 | 10162 | The SwiftUI cookbook for focus | Enum `@FocusState` patterns |
| 2023 | 10163 | Build accessible apps with SwiftUI and UIKit | A11y for custom controls |
| 2024 | 10073 | Catch up on accessibility in SwiftUI | `.accessibilityActions`, rotors |
| 2024 | 10144 | What's new in SwiftUI | `Tab`, `Tab(role: .search)`, `@Entry` |
| 2024 | 10147 | Elevate your tab and sidebar experience in iPadOS | `UITab`, `UISearchTab`, sidebar toggle |
| 2025 | 101 | Keynote | Liquid Glass public reveal |
| 2025 | 102 | Platforms State of the Union | `UIDesignRequiresCompatibility` opt-out |
| 2025 | 208 | Elevate the design of your iPad app | Pointer + Liquid Glass hover |
| 2025 | 219 | Meet Liquid Glass | Principles: lensing, materialization, fluidity, adaptivity, accessibility |
| 2025 | 243 | What's new in UIKit | UIKit highlights for new design |
| 2025 | 256 | What's new in SwiftUI | Liquid Glass adoption, rich text, WebView, 3D Charts, performance |
| 2025 | 280 | Cook up a rich text experience in SwiftUI with AttributedString | `TextEditor` + `AttributedString` |
| 2025 | 284 | Build a UIKit app with the new design | `UIGlassEffect`, glass button appearances, slider momentum/ticks, `UISearchTab` |
| 2025 | 310 | Build an AppKit app with the new design | `NSGlassEffectView`, control prominence |
| 2025 | 323 | Build a SwiftUI app with the new design | `.glass`/`.glassProminent`, `glassEffect`, `GlassEffectContainer`, search + toolbar APIs, slider ticks |
| 2025 | 356 | Get to know the new design system | Visual design, info architecture, concentricity |

---

## Closing notes

Three principles shape every decision above. **First, prefer semantics over decoration** — `.borderedProminent` means "primary"; `.destructive` means "data loss"; `.oneTimeCode` means "autofill from SMS." Treat these tokens as contracts with the system, not styling hints. **Second, choose controls by user intent, not by visual preference** — a 2-state choice is a Toggle, not a menu; a continuous analog value is a Slider, not a Stepper; a 50-item list is a NavigationLink picker, not a wheel. **Third, on iOS 26, do less.** Recompile with Xcode 26 and your standard controls adopt Liquid Glass automatically — reach for `.glassEffect`, `GlassEffectContainer`, and the new toolbar/search/tab APIs only when you need custom chrome. Everything else should keep its shape and let the system do the work.

When in doubt, the primary authorities in priority order are the **Apple Human Interface Guidelines** (`developer.apple.com/design/human-interface-guidelines`), the **SwiftUI and UIKit developer documentation** (`developer.apple.com/documentation`), and the WWDC sessions indexed above. Third-party sources (Hacking with Swift, Swift by Sundell, Sarunw, Swift with Majid, Use Your Loaf, Point-Free) are excellent for idiomatic patterns but defer to Apple's docs for API signatures and availability.