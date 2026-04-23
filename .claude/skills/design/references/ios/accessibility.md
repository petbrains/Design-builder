---
name: accessibility
description: Apple accessibility reference for iOS 26 (every assistive tech, SwiftUI + UIKit)
platform: ios
---

# Apple accessibility for iOS 26 — a developer's reference

**iOS 26 is the current SDK as of April 2026.** Apple unified platform versioning at WWDC25 (June 2025) — iOS, iPadOS, macOS Tahoe, watchOS, tvOS, and visionOS all jumped straight to version 26 to match the 2026 model year. iOS 26 shipped publicly on September 15, 2025. iOS 27 has not been released or seeded yet; WWDC26 is announced for **June 8–12, 2026**. All code and API references below apply to iOS 18, iOS 26, and the intervening SDKs. Where a symbol was introduced later than iOS 14, its availability is called out inline.

This document is organized by assistive technology and user preference, then by framework (SwiftUI + UIKit). Every section gives you the *why*, the *exact API surface*, good-vs-bad usage, and copy-pasteable code for both frameworks.

---

## 1. VoiceOver

VoiceOver is the screen reader. It announces elements in this fixed order: **Label → Value → Trait → Hint**. Everything you expose flows through that pipeline.

### 1.1 Label vs. hint vs. value — the three attributes that matter most

These three strings are the contract your app has with VoiceOver. They have precise, non-overlapping jobs, and conflating them is the single most common accessibility bug.

- **`accessibilityLabel`** — *what the element is.* A short noun phrase. Required on every interactive or informative element that lacks sufficient visible text (icon-only buttons, decorative-looking images with meaning, custom-drawn controls).
- **`accessibilityValue`** — *the current state or content* that changes over time. A slider's percentage, a text field's contents, a toggle's "on"/"off" beyond its default announcement, a progress bar's completion.
- **`accessibilityHint`** — *what happens when you activate.* Optional, verb-first, and **users can disable hints globally** (Settings → Accessibility → VoiceOver → Verbosity → Speak Hints). Never put critical information only in the hint.

**SwiftUI — all three together:**
```swift
Slider(value: $volume, in: 0...100)
    .accessibilityLabel("Volume")                        // what it is
    .accessibilityValue("\(Int(volume)) percent")        // current state
    .accessibilityHint("Adjusts playback volume")        // optional behavior
```

**UIKit — all three together:**
```swift
slider.isAccessibilityElement = true
slider.accessibilityLabel = "Volume"
slider.accessibilityValue = "\(Int(slider.value)) percent"
slider.accessibilityHint = "Adjusts playback volume"
slider.accessibilityTraits = .adjustable
```

**Good vs. bad, side by side:**

| Attribute | Bad | Good | Why |
|---|---|---|---|
| Label | `"btn_play_icon_24"` | `"Play"` | Don't leak asset names. |
| Label | `"Tap here to submit form, button"` | `"Submit"` | The trait adds "button" automatically. |
| Value | label `"Volume 42%"`, value unset | label `"Volume"`, value `"42 percent"` | Label = noun; value = state. |
| Hint | `"Button"` | `"Plays the current track"` | Hint is a verb phrase, not a role. |
| Hint | `"Double-tap to play"` | `"Plays the current track"` | VoiceOver adds the gesture itself. |

### 1.2 Writing great labels

From WWDC19 #254 *"Writing Great Accessibility Labels"* and the HIG:

1. **Be brief.** One word or short phrase.
2. **Don't include the control type.** VoiceOver would then read "Add button button."
3. **Put the most important word first** — Voice Control matches on the prefix.
4. **Sentence case, not ALL CAPS.** VoiceOver spells all-caps letter by letter.
5. **No trailing periods** except on acronyms ("U.S.A.") or questions.
6. **Localize** alongside the rest of the UI.
7. **Update dynamically** when state changes (a favorite toggle flips between "Favorite" and "Unfavorite").
8. **Describe function, not appearance.** "Submit order," not "Blue button."

| Bad | Good |
|---|---|
| `"IMG_3421.jpg"` | `"Sunset over the Golden Gate Bridge"` |
| `"Click here to learn more"` | `"Learn more about Dynamic Type"` |
| `"X"` | `"Close"` |
| `"Play."` (trailing period) | `"Play"` |
| `"TAP TO BUY"` | `"Buy"` |
| `"add_icon_32"` | `"Add contact"` |

### 1.3 Writing useful hints

Hints describe the *result* of the action and are the only place developers consistently get verbosity wrong. Rules:

1. Action-oriented, verb-first.
2. Present-tense third-person.
3. One short clause.
4. No gesture instructions ("Double-tap to…") — VoiceOver narrates the gesture itself.
5. Never essential-only — users can disable hints.

| Bad | Good |
|---|---|
| `"Double-tap to add to favorites"` | `"Adds the song to your favorites"` |
| `"A button that submits"` | `"Submits your answer"` |
| `"Tap here."` | `"Opens the article"` |
| `"Button for composing a new message that takes you to…"` | `"Composes a new message"` |

### 1.4 Traits — the complete set

Traits describe the role of an element. They're an option set, so combine freely (`[.isImage, .isButton]`). The UIKit names live on `UIAccessibilityTraits`; the SwiftUI names live on `AccessibilityTraits`.

| Role | UIKit | SwiftUI | Notes |
|---|---|---|---|
| Button | `.button` | `.isButton` | VoiceOver appends "button." |
| Link | `.link` | `.isLink` | Typically inline; says "link." |
| Header | `.header` | `.isHeader` | Surfaces in the Headings rotor. |
| Search field | `.searchField` | `.isSearchField` | Text entry used for search. |
| Image | `.image` | `.isImage` | Default on `UIImageView`/`Image`. |
| Selected | `.selected` | `.isSelected` | Rows, segmented controls. |
| Plays sound | `.playsSound` | `.playsSound` | VoiceOver quiets while sound plays. |
| Keyboard key | `.keyboardKey` | `.isKeyboardKey` | Suppresses "button" for custom keyboards. |
| Static text | `.staticText` | `.isStaticText` | Non-changing text. |
| Summary element | `.summaryElement` | `.isSummaryElement` | Announced at launch (Weather). Only one per screen. |
| Not enabled | `.notEnabled` | use `.disabled()` | VoiceOver says "dimmed." |
| Updates frequently | `.updatesFrequently` | `.updatesFrequently` | Stopwatch/counter; VoiceOver polls. |
| Starts media session | `.startsMediaSession` | `.startsMediaSession` | Silences VoiceOver while media plays. |
| Adjustable | `.adjustable` | use `.accessibilityAdjustableAction` | Swipe up/down to inc/dec. |
| Allows direct interaction | `.allowsDirectInteraction` | `.allowsDirectInteraction` | Piano, drawing canvas. |
| Causes page turn | `.causesPageTurn` | `.causesPageTurn` | Scrolls to next page at end of read. |
| Tab bar | `.tabBar` | `.isTabBar` | Tab bar container. |
| Toggle / switch | `.switchButton` (iOS 17+) | `.isToggle` | On/off switch. |
| Modal | `accessibilityViewIsModal` | `.isModal` | Ignores sibling views outside the modal. |

**SwiftUI example:**
```swift
Image("heart")
    .accessibilityRemoveTraits(.isImage)
    .accessibilityAddTraits([.isButton, .isSelected])
    .accessibilityLabel("Liked")
```

**UIKit example:**
```swift
view.isAccessibilityElement = true
view.accessibilityLabel = "Piano keyboard"
view.accessibilityTraits = [.allowsDirectInteraction]
```

### 1.5 Grouping with `.accessibilityElement(children:)`

SwiftUI grouping takes an `AccessibilityChildBehavior`. Pick deliberately:

- **`.ignore`** (default when you call `.accessibilityElement()`) — children disappear from the tree. You must provide a label yourself. Use when you want one fluid custom sentence.
- **`.combine`** — merges children's labels/traits into a single element with pauses. Child buttons become **custom actions** on the merged element. Great for card-like groupings (avatar + name + status).
- **`.contain`** — keeps children individually focusable but defines a container boundary. Enables the Container rotor and gives assistive tech a logical scope.

```swift
// .combine — merge labels into one announcement
HStack {
    Text("Time:");        Text("12:00 PM")
    Text("Temperature:"); Text("68°F")
}
.accessibilityElement(children: .combine)
// VoiceOver: "Time:, 12:00 PM, Temperature:, 68°F"

// .ignore + custom label — one curated sentence
VStack {
    Text("Your score is")
    Text("1000").font(.title)
}
.accessibilityElement(children: .ignore)
.accessibilityLabel("Your score is 1000")

// .contain — keep children navigable but scope them
List(alerts) { AlertRow(alert: $0) }
    .accessibilityElement(children: .contain)
    .accessibilityLabel("Budget alerts")
```

**UIKit equivalent:**
```swift
container.isAccessibilityElement = true
container.accessibilityLabel = "Your score is 1000"
// Or keep children and just group them as a container:
container.accessibilityElements = [titleLabel, scoreLabel]
container.shouldGroupAccessibilityChildren = true
```

**Pitfall:** when `.combine` is applied to a parent that contains `Button`s, those buttons become custom actions rather than part of the label. If you want them speakable, reconstruct the behavior with `.accessibilityAction(named:)`.

### 1.6 Custom actions

SwiftUI ships three standard action kinds and unlimited named ones:

- **`.default`** — the primary activation.
- **`.magicTap`** — two-finger double-tap anywhere. Convention: play/pause, answer/end call, start/stop primary action.
- **`.escape`** — two-finger Z scrub. Convention: dismiss the modal or go back.
- **`named: Text(...)`** — appears in VoiceOver's Actions rotor.

```swift
PlayerView()
    .accessibilityAction(.magicTap) { viewModel.togglePlay() }
    .accessibilityAction(.escape)   { dismiss() }
    .accessibilityAction(named: Text("Skip"))   { viewModel.skip() }
    .accessibilityAction(named: Text("Repeat")) { viewModel.repeatTrack() }
```

**Groups of actions (iOS 17+):**
```swift
MessageRow(message: m)
    .accessibilityActions {
        Button("Reply")       { reply(m) }
        Button("Mark Unread") { markUnread(m) }
        Button("Delete", role: .destructive) { delete(m) }
    }
```

**App Intent–driven actions (iOS 18+, WWDC24 #10073):**
```swift
.accessibilityAction(intent: FavoriteBeachIntent(beach: beach))
```

**UIKit equivalents:**
```swift
override func accessibilityPerformMagicTap() -> Bool { togglePlay(); return true }
override func accessibilityPerformEscape()   -> Bool { dismiss(animated: true); return true }

let skip = UIAccessibilityCustomAction(name: "Skip") { _ in self.skip(); return true }
view.accessibilityCustomActions = [skip]
```

### 1.7 Custom rotors

Rotors are user-discoverable navigation shortcuts (two-finger rotate). SwiftUI got custom rotors in iOS 15 via WWDC21 #10119. Use them for lists of warnings, chapters, bookmarks, mentions, emails, or any text range that deserves jump navigation.

```swift
struct AlertsView: View {
    let alerts: [Alert]
    @Namespace var ns
    var body: some View {
        ScrollViewReader { proxy in
            List(alerts) { alert in
                AlertRow(alert: alert)
                    .accessibilityRotorEntry(id: alert.id, in: ns)
                    .id(alert.id)
            }
            .accessibilityElement(children: .contain)
            .accessibilityRotor("Warnings") {
                ForEach(alerts.filter(\.isWarning)) { alert in
                    AccessibilityRotorEntry(alert.title, id: alert.id, in: ns) {
                        proxy.scrollTo(alert.id)
                    }
                }
            }
        }
    }
}
```

**Text-range rotors** work on `TextEditor` content — perfect for jumping through emails, URLs, mentions:
```swift
TextEditor(text: $content.text)
    .accessibilityRotor("Emails", textRanges: content.emailRanges)
    .accessibilityRotor("Links",  textRanges: content.linkRanges)
```

**Headings rotor** requires both the trait and a heading level:
```swift
Text("Section title")
    .font(.headline)
    .accessibilityAddTraits(.isHeader)
    .accessibilityHeading(.h2)
```

**UIKit custom rotor:**
```swift
override var accessibilityCustomRotors: [UIAccessibilityCustomRotor]? {
    get {
        [UIAccessibilityCustomRotor(name: "Warnings") { predicate in
            let current = predicate.currentItem.targetElement as? AlertCell
            let reverse = predicate.searchDirection == .previous
            guard let next = self.nextWarning(after: current, reverse: reverse) else { return nil }
            return UIAccessibilityCustomRotorItemResult(targetElement: next, targetRange: nil)
        }]
    }
    set { }
}
```

### 1.8 Direct Touch for custom drawing and music apps

`allowsDirectInteraction` **passes touches straight through VoiceOver** instead of requiring swipe-to-focus + double-tap. Mandatory for piano keyboards (GarageBand), drawing canvases, signature fields, and real-time gesture games.

```swift
// SwiftUI (iOS 17+ adds options for precise control)
PianoKeyboardView()
    .accessibilityLabel("Piano keyboard")
    .accessibilityDirectTouch(options: .silentOnTouch) // also .requiresActivation

// UIKit
pianoView.isAccessibilityElement = true
pianoView.accessibilityLabel = "Piano keyboard"
pianoView.accessibilityTraits = [.allowsDirectInteraction]
```

**Caveat:** direct-interaction regions break rotor and heading navigation inside their frame. Bound them tightly and put navigable controls around the edges.

### 1.9 VoiceOver announcements and focus

```swift
// Quick announcement (UIKit)
UIAccessibility.post(notification: .announcement,   argument: "Item added to cart")
UIAccessibility.post(notification: .layoutChanged,  argument: revealedView)   // small update
UIAccessibility.post(notification: .screenChanged,  argument: firstElement)   // major context change

// iOS 17+ priority announcement
var msg = AttributedString("Camera loading")
msg.accessibilitySpeechAnnouncementPriority = .high
AccessibilityNotification.Announcement(msg).post()
```

---

## 2. Dynamic Type

Dynamic Type is Apple's systemwide text-size preference. Users set it at **Settings → Display & Brightness → Text Size** for the standard range, or **Settings → Accessibility → Display & Text Size → Larger Text** to unlock the five **accessibility sizes (AX1–AX5)** that go up to roughly 310% of default.

### 2.1 All twelve sizes

| SwiftUI `DynamicTypeSize` | UIKit `UIContentSizeCategory` |
|---|---|
| `.xSmall` | `.extraSmall` |
| `.small` | `.small` |
| `.medium` | `.medium` |
| **`.large`** (default) | **`.large`** |
| `.xLarge` | `.extraLarge` |
| `.xxLarge` | `.extraExtraLarge` |
| `.xxxLarge` | `.extraExtraExtraLarge` |
| `.accessibility1` (AX1) | `.accessibilityMedium` |
| `.accessibility2` (AX2) | `.accessibilityLarge` |
| `.accessibility3` (AX3) | `.accessibilityExtraLarge` |
| `.accessibility4` (AX4) | `.accessibilityExtraExtraLarge` |
| `.accessibility5` (AX5) | `.accessibilityExtraExtraExtraLarge` |

`DynamicTypeSize.isAccessibilitySize` is true for AX1–AX5. The enum is `Comparable`, so `.large ... .accessibility3` is a valid range.

### 2.2 Why AX5 is the stress test

**AX5 is the largest size any user can request.** If AX5 survives, everything smaller survives. Bugs you'll only find at AX5:

- Text truncated mid-word in fixed-height cards
- HStacks overflowing the trailing edge
- Icons looking tiny next to enormous text (`@ScaledMetric` missing)
- Navigation-bar "Done"/"Cancel" pushed off-screen
- Tab-bar titles degrading to "…"
- Headers clipping descenders

### 2.3 Scaled system fonts — the baseline

**SwiftUI** scales automatically when you use a text style:
```swift
Text("Body copy").font(.body)           // scales
Text("Chapter").font(.title)
```

**UIKit** requires one extra line, because the default is *false*:
```swift
label.font = UIFont.preferredFont(forTextStyle: .body)
label.adjustsFontForContentSizeCategory = true   // REQUIRED
label.numberOfLines = 0                          // allow wrapping
```

`Font.TextStyle` ↔ `UIFont.TextStyle` pair up one-to-one: `.largeTitle` (34pt), `.title/.title1` (28), `.title2` (22), `.title3` (20), `.headline` (17 semibold), `.subheadline` (15), `.body` (17), `.callout` (16), `.footnote` (13), `.caption/.caption1` (12), `.caption2` (11). iOS 17 added `.extraLargeTitle` and `.extraLargeTitle2`.

### 2.4 Custom fonts that actually scale

The number-one custom-font accessibility bug is forgetting `relativeTo:`.

**SwiftUI:**
```swift
// GOOD: scales with Dynamic Type
Text("Welcome").font(.custom("Avenir-Heavy", size: 28, relativeTo: .title))
// BAD: locked at 17pt forever
Text("Body").font(.custom("Avenir-Book", size: 17))
```

**UIKit:**
```swift
let base    = UIFont(name: "Avenir-Book", size: 17)!
let metrics = UIFontMetrics(forTextStyle: .body)
label.font  = metrics.scaledFont(for: base)
label.adjustsFontForContentSizeCategory = true
// Optional cap:
label.font  = metrics.scaledFont(for: base, maximumPointSize: 60)
```

You can also clamp at the view level (iOS 15+):
```swift
view.minimumContentSizeCategory = .medium
view.maximumContentSizeCategory = .accessibilityExtraLarge
```

### 2.5 `@ScaledMetric` for non-text values

Without `@ScaledMetric`, a 24pt icon next to AX5 body text looks like a pinhead. The property wrapper scales any CGFloat along with Dynamic Type.

```swift
struct Row: View {
    @ScaledMetric private var iconSize = 24.0
    @ScaledMetric(relativeTo: .largeTitle) private var titleSpacing = 12.0
    @ScaledMetric private var rowPadding = 16.0

    var body: some View {
        HStack(spacing: titleSpacing) {
            Image(systemName: "star.fill")
                .resizable()
                .frame(width: iconSize, height: iconSize)
            Text("Favorite").font(.body)
        }
        .padding(rowPadding)
    }
}
```

**UIKit** equivalent:
```swift
let scaled = UIFontMetrics(forTextStyle: .body).scaledValue(for: 16) // pt
```

### 2.6 Layouts that survive AX5

The trick is to **swap** layout shapes rather than shrink text. The `Layout` protocol and `AnyLayout` (both iOS 16+) make this elegant.

```swift
struct FigureCell: View {
    @Environment(\.dynamicTypeSize) private var size
    let title: String, imageName: String

    var body: some View {
        let layout: AnyLayout = size.isAccessibilitySize
            ? AnyLayout(VStackLayout(alignment: .leading, spacing: 8))
            : AnyLayout(HStackLayout(spacing: 12))

        layout {
            Image(imageName).resizable().scaledToFit().frame(width: 60, height: 60)
            Text(title).font(.headline)
        }
    }
}
```

`ViewThatFits` (iOS 16+) degrades gracefully by trying progressively simpler variants:

```swift
ViewThatFits(in: .horizontal) {
    HStack { Image(systemName: "icloud.and.arrow.up"); Text("Upload to iCloud Drive") }
    HStack { Image(systemName: "icloud.and.arrow.up"); Text("Upload") }
    Image(systemName: "icloud.and.arrow.up").accessibilityLabel("Upload to iCloud Drive")
}
```

**Clamp subtrees only when absolutely necessary:**
```swift
DenseChart().dynamicTypeSize(.large ... .accessibility3)
```
Avoid capping below `.accessibility5` without strong justification.

### 2.7 Dos and don'ts

**Do:** let text wrap (`numberOfLines = 0`), use `@ScaledMetric` for everything numeric near text, switch H↔V stacks at AX sizes, prefer `minHeight` over `height`, cap custom fonts with `maximumPointSize:` where necessary.

**Don't:** hardcode a `height` on text containers (clipping), blanket-apply `.lineLimit(1)`, lean on `minimumScaleFactor` as a layout strategy (text below ~0.7 is unreadable at AX5 and defeats Dynamic Type), disable Dynamic Type across the app because layout is hard.

**Wrap vs. truncate vs. scale:** wrap by default; truncate only where space is genuinely fixed by design (tab bars, nav titles) and expose the full text via `accessibilityLabel`; scale down only for short numeric badges.

### 2.8 Dynamic Type testing checklist — run every screen at six sizes

1. **xSmall** — nothing collapses unexpectedly.
2. **Large** (default) — baseline.
3. **xxxLarge** — last non-accessibility size; adaptation should be kicking in.
4. **AX1** — HStack→VStack swaps should fire here.
5. **AX3** — `ViewThatFits` fallbacks kick in.
6. **AX5** — the stress test. Nothing clipped, no off-screen primary actions, every control reachable.

In Xcode Previews, use **Variants → Dynamic Type Variants** to render all six at once.

---

## 3. Switch Control

Switch Control is for users with significant motor impairments. Inputs include external Bluetooth/MFi switches, sip-and-puff devices, joysticks, the screen itself, head movements via the TrueDepth camera (Head Tracking), facial expressions, MIDI devices, and in iOS 26, **Brain-Computer Interface** switches.

### 3.1 Focus order follows accessibility order

There is **no separate API for Switch Control order**. It walks the same accessibility tree as VoiceOver in the same reading order. Fix it there and Switch Control follows.

### 3.2 Scanning modes

Apple documents three scanning styles under **Settings → Accessibility → Switch Control**:

1. **Auto Scanning** — default. The highlight moves automatically; one switch selects.
2. **Manual Scanning** — one switch advances, another selects. Requires two switches.
3. **Single Switch Step Scanning** — one switch advances; if the user pauses past a configurable duration, the current item auto-selects.

Separate from scanning style is the **cursor mode**: Item Mode (default), Point Mode / Gliding Cursor for pixel-level aim, and Head Tracking for TrueDepth-camera control.

### 3.3 When default focus breaks

- **Modal presentations** — sheets, alerts, and `fullScreenCover` should take focus automatically. Custom `ZStack` overlays posing as sheets trap focus behind them.
- **Dynamic content** — error banners, inline validation, newly loaded rows may never be discovered unless you push focus there.
- **Off-screen elements** — items in hidden horizontal scrollers are still focusable; the ring disappears "into the void."
- **Ancestors with `.accessibilityHidden(true)`** accidentally hide subtrees.
- **Incorrect grouping** — 20 cells each needing a switch hit where one combined cell would do.
- **Post-dismiss anchoring** — when a sheet closes, focus should return near the button that opened it. Manage this manually if SwiftUI doesn't.

### 3.4 Reducing switch hits with grouping

```swift
HStack {
    Image("avatar")
    VStack(alignment: .leading) {
        Text("Ada Lovelace").font(.headline)
        Text("Online now").font(.caption)
    }
}
.accessibilityElement(children: .combine)
.accessibilityLabel("Ada Lovelace, online now")
.accessibilityAddTraits(.isButton)
.onTapGesture { openProfile() }
```

### 3.5 Reordering focus with `.accessibilitySortPriority`

Higher priority → earlier in the swipe order within the *same* container. Default is 0.

```swift
VStack {
    Image("hero").accessibilitySortPriority(0)
    Text("Shuttle launch").font(.largeTitle).accessibilitySortPriority(2)
    Text("Live from Cape Canaveral").accessibilitySortPriority(1)
}
.accessibilityElement(children: .contain)
```

### 3.6 Programmatic focus

SwiftUI's `@AccessibilityFocusState` drives VoiceOver and Switch Control focus directly — essential for surfacing errors and restoring context after sheet dismissal.

```swift
struct SignInForm: View {
    enum Field: Hashable { case email, password, error }
    @AccessibilityFocusState private var focus: Field?
    @State private var email = "", password = ""
    @State private var errorMessage: String?

    var body: some View {
        VStack(spacing: 16) {
            TextField("Email", text: $email).accessibilityFocused($focus, equals: .email)
            SecureField("Password", text: $password).accessibilityFocused($focus, equals: .password)
            if let err = errorMessage {
                Text(err).foregroundStyle(.red).accessibilityFocused($focus, equals: .error)
            }
            Button("Sign in") {
                if password.isEmpty {
                    errorMessage = "Password is required."
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { focus = .error }
                }
            }
        }
    }
}
```

**UIKit** sets an explicit ordered array on a container:
```swift
override var accessibilityElements: [Any]? {
    get { [nameLabel, bioLabel, avatarView] }
    set { super.accessibilityElements = newValue }
}
// Move focus:
UIAccessibility.post(notification: .screenChanged, argument: errorLabel)  // major shift
UIAccessibility.post(notification: .layoutChanged, argument: errorLabel)  // minor update
```

### 3.7 Testing Switch Control without hardware

Enable it, then add it to the Accessibility Shortcut (triple-click side/home). Configure **Screen** as a switch assigned to "Select Item." Set Auto Scanning speed to about two seconds, then walk each screen and verify: every action reachable, order logical, sheets receive focus, focus returns sensibly on dismiss.

---

## 4. Voice Control

Voice Control lets users drive iOS entirely by voice — Siri's speech engine running locally (one-time model download). Settings → Accessibility → Voice Control. Common commands include **"Tap [name]"**, **"Show names"** (overlay each control's speakable label), **"Show numbers"** (tap numbered overlays), and **"Show grid"** for precise point-and-zoom targeting.

### 4.1 The critical rule

**Visible text must match `accessibilityLabel`, or provide `accessibilityInputLabels`.** If the button shows "Send" but the label reads "Compose message," the user who says "Tap Send" gets nothing. The first string in `accessibilityInputLabels` is what appears under "Show names" — make it short and natural.

### 4.2 Good vs. bad patterns

**Icon-only button with engineer-speak label (BAD):**
```swift
Button { delete() } label: { Image(systemName: "trash") }
    .accessibilityLabel("Purge Item From Persistence Store")
```

**Natural name first, alternates provided (GOOD):**
```swift
Button { delete() } label: { Image(systemName: "trash") }
    .accessibilityLabel("Delete")
    .accessibilityInputLabels(["Delete", "Remove", "Trash"])
```

**Visible/label mismatch (BAD):**
```swift
Button("Buy") { purchase() }
    .accessibilityLabel("Purchase premium subscription for $4.99 per month")
```

**Label contains the visible word (GOOD):**
```swift
Button("Buy") { purchase() }
    .accessibilityLabel("Buy, premium subscription, $4.99 per month")
    .accessibilityInputLabels(["Buy", "Purchase", "Subscribe"])
```

**Duplicate labels across a list (BAD):** three "Edit" buttons trigger a disambiguation dialog on every "Tap Edit."

**Unique speakable names (GOOD):**
```swift
ForEach(items) { item in
    Button("Edit") { edit(item) }
        .accessibilityLabel("Edit \(item.name)")
        .accessibilityInputLabels(["Edit \(item.name)", "Edit"])
}
```

**UIKit:**
```swift
send.accessibilityLabel = "Send message"
send.accessibilityUserInputLabels = ["Send", "Send message", "Reply"]
```

### 4.3 Pitfalls checklist

- Every tappable has visible text or a speakable input label matching what a user would naturally say.
- The first input-label string is short (1–3 words).
- No two visible controls on the same screen share an identical speakable name unless they genuinely do the same thing.
- Toolbars and icon-only rows explicitly provide input labels — never rely on engineer-facing accessibility labels.
- Custom-drawn views (Canvas/Metal/shapes) are exposed as accessibility elements with labels.
- Audit with **Settings → Accessibility → Voice Control → Overlay → Item Names** visible — fastest way to see what the user sees.

---

## 5. Reduce Motion

**User intent:** suppress motion that can trigger vestibular disorders, migraines, or motion sickness.

### 5.1 APIs

| Surface | API |
|---|---|
| UIKit | `UIAccessibility.isReduceMotionEnabled` |
| Notification | `UIAccessibility.reduceMotionStatusDidChangeNotification` |
| UIKit (iOS 14+) | `UIAccessibility.prefersCrossFadeTransitions` (true only when both Reduce Motion and "Prefer Cross-Fade Transitions" sub-setting are on) |
| Notification | `UIAccessibility.prefersCrossFadeTransitionsStatusDidChange` |
| SwiftUI | `@Environment(\.accessibilityReduceMotion)` |

### 5.2 What to preserve vs. replace

**Preserve** essential motion: loading spinners, determinate progress, pull-to-refresh, VoiceOver focus rings, keyboard animations, direct-manipulation gesture follow, subtle "new message" fades.

**Replace or disable** decorative motion: parallax backgrounds, spring bounces, elaborate hero transitions, scale/zoom transitions, Ken Burns, shimmer, particles, auto-advancing carousels.

**Cross-fade pattern:** replace `.slide` / `.scale` with `.opacity`. In UIKit, replace `CATransition(type: .push)` with `.fade` or just set the final state with no animation.

### 5.3 SwiftUI patterns

```swift
struct AnimatedCard: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var expanded = false
    var body: some View {
        Rectangle().fill(.blue)
            .scaleEffect(expanded ? 1.3 : 1)
            .animation(reduceMotion ? nil : .spring(response: 0.5, dampingFraction: 0.6), value: expanded)
            .onTapGesture { expanded.toggle() }
    }
}

// Conditional withAnimation helper (Paul Hudson pattern)
func withOptionalAnimation<Result>(_ animation: Animation? = .default,
                                   _ body: () throws -> Result) rethrows -> Result {
    UIAccessibility.isReduceMotionEnabled
        ? try body()
        : try withAnimation(animation, body)
}

// Transition swap: slide → cross-fade
DetailView().transition(reduceMotion ? .opacity : .slide)

// Suppress implicit animation on a specific change
content.transaction { tx in
    if UIAccessibility.isReduceMotionEnabled { tx.animation = nil }
}
```

### 5.4 UIKit patterns

```swift
NotificationCenter.default.addObserver(self,
    selector: #selector(reduceMotionDidChange),
    name: UIAccessibility.reduceMotionStatusDidChangeNotification, object: nil)

func animateBounce() {
    if UIAccessibility.isReduceMotionEnabled {
        bounceView.transform = .identity
    } else {
        UIView.animate(withDuration: 0.3, delay: 0,
                       usingSpringWithDamping: 0.5, initialSpringVelocity: 0.8,
                       options: [],
                       animations: { self.bounceView.transform = .init(scaleX: 1.1, y: 1.1) })
    }
}

func pushDetail(_ vc: UIViewController) {
    if UIAccessibility.prefersCrossFadeTransitions {
        let t = CATransition(); t.type = .fade; t.duration = 0.2
        navigationController?.view.layer.add(t, forKey: kCATransition)
        navigationController?.pushViewController(vc, animated: false)
    } else {
        navigationController?.pushViewController(vc, animated: true)
    }
}

// Parallax off when reduced
if UIAccessibility.isReduceMotionEnabled {
    heroImageView.motionEffects.forEach { heroImageView.removeMotionEffect($0) }
}
```

**Known quirk:** `prefersCrossFadeTransitionsStatusDidChange` may not fire until `UIAccessibility.prefersCrossFadeTransitions` is read at least once per process. "Prime" it at launch with a throwaway read.

---

## 6. Reduce Transparency

**User intent:** convert blurs and translucency to solid backgrounds for legibility.

| Surface | API |
|---|---|
| UIKit | `UIAccessibility.isReduceTransparencyEnabled` |
| Notification | `UIAccessibility.reduceTransparencyStatusDidChangeNotification` |
| SwiftUI | `@Environment(\.accessibilityReduceTransparency)` |

**Important gotcha:** SwiftUI's `.background(.ultraThinMaterial)` does **not** automatically fall back to an opaque fill when Reduce Transparency is on. Branch manually.

```swift
struct OverlayCard: View {
    @Environment(\.accessibilityReduceTransparency) private var reduce
    var body: some View {
        VStack { Text("Hello").font(.title) }
            .padding()
            .background {
                if reduce { Color(.systemBackground) }
                else      { Rectangle().fill(.ultraThinMaterial) }
            }
    }
}
```

**UIKit** swaps a `UIVisualEffectView` for a solid fill:
```swift
@objc func update() {
    let reduced = UIAccessibility.isReduceTransparencyEnabled
    blurView.isHidden = reduced
    fallbackView.isHidden = !reduced
}
NotificationCenter.default.addObserver(self, selector: #selector(update),
    name: UIAccessibility.reduceTransparencyStatusDidChangeNotification, object: nil)
```

With iOS 26's Liquid Glass design system, this matters more than ever — the new material defaults are more translucent than before, and they remain translucent under Reduce Transparency only for backgrounds of chrome that don't obscure legibility-critical text. Custom materials must branch.

---

## 7. Increase Contrast / Darker System Colors

**User intent:** more separation between foreground and background; richer, darker system colors.

| Surface | API |
|---|---|
| UIKit | `UIAccessibility.isDarkerSystemColorsEnabled` |
| Notification | `UIAccessibility.darkerSystemColorsStatusDidChangeNotification` |
| UIKit trait | `UITraitCollection.accessibilityContrast` (`.unspecified`, `.normal`, `.high`) |
| SwiftUI (iOS 15+) | `@Environment(\.colorSchemeContrast)` (`.standard`, `.increased`) |

### 7.1 Semantic colors adapt automatically

Never hardcode hex for legibility-critical UI. Use:
- `UIColor.label`, `.secondaryLabel`, `.tertiaryLabel`, `.quaternaryLabel`
- `.systemBackground`, `.secondarySystemBackground`, `.tertiarySystemBackground`, `.systemGroupedBackground`
- `.separator`, `.opaqueSeparator`, `.link`, `.placeholderText`
- `.systemRed`/`.systemBlue`/etc. — all have high-contrast variants built in.

```swift
// BAD: hardcoded — never adapts
label.textColor = UIColor(red: 0.5, green: 0.5, blue: 0.5, alpha: 1)
// GOOD: adapts to light/dark/high-contrast
label.textColor = .label
label.backgroundColor = .systemBackground
```

### 7.2 Custom colors need four variants

In the asset catalog, enable "High Contrast" under Appearances to reveal four slots per color: **Any Appearance**, **Dark Appearance**, **Any Appearance + High Contrast**, **Dark Appearance + High Contrast**. High-contrast variants are typically darker in light mode and lighter in dark mode.

```swift
struct WarningBanner: View {
    @Environment(\.colorSchemeContrast) private var contrast
    var body: some View {
        Text("Low battery")
            .foregroundStyle(Color("WarningText"))
            .padding()
            .background(contrast == .increased ? Color("WarningBG-HC") : Color("WarningBG"))
            .overlay(RoundedRectangle(cornerRadius: 8)
                .stroke(.primary, lineWidth: contrast == .increased ? 2 : 0))
    }
}
```

**UIKit** reacts via `traitCollectionDidChange`:
```swift
override func traitCollectionDidChange(_ previous: UITraitCollection?) {
    super.traitCollectionDidChange(previous)
    if previous?.accessibilityContrast != traitCollection.accessibilityContrast { apply() }
}
func apply() {
    let hc = traitCollection.accessibilityContrast == .high
    borderView.layer.borderWidth  = hc ? 2 : 0.5
    borderView.layer.borderColor  = UIColor.separator.cgColor
    borderView.backgroundColor    = UIColor(named: "CardBG")  // resolves to HC variant
}
```

---

## 8. Color blindness and Differentiate Without Color

Roughly 1 in 12 men and 1 in 200 women are colorblind. The firm rule — **independent of the system setting** — is: **never use color alone to convey information**. The setting lets users request *additional* cues.

| Surface | API |
|---|---|
| UIKit | `UIAccessibility.shouldDifferentiateWithoutColor` |
| Notification | `UIAccessibility.differentiateWithoutColorDidChangeNotification` |
| SwiftUI | `@Environment(\.accessibilityDifferentiateWithoutColor)` |

Pair color with SF Symbols (`checkmark.circle.fill`, `xmark.circle.fill`, `exclamationmark.triangle.fill`, `info.circle.fill`, `arrow.up`, `arrow.down`), shapes, textures, or text prefixes (`+3.2%`, `-1.4%`).

**Status badge done right:**
```swift
struct StatusBadge: View {
    enum Status { case ok, warn, error }
    let status: Status
    var body: some View {
        HStack(spacing: 6) {
            Image(systemName: symbol).foregroundStyle(color)
            Text(label).font(.caption)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(label)
    }
    var symbol: String {
        switch status {
        case .ok:    "checkmark.circle.fill"
        case .warn:  "exclamationmark.triangle.fill"
        case .error: "xmark.octagon.fill"
        }
    }
    var color: Color { switch status { case .ok: .green; case .warn: .yellow; case .error: .red } }
    var label: String { switch status { case .ok: "OK"; case .warn: "Warning"; case .error: "Error" } }
}
```

**Chart enhancement when the flag is on:**
```swift
@Environment(\.accessibilityDifferentiateWithoutColor) private var differentiate
BarView(color: .green)
    .overlay(alignment: .top) { if differentiate { Image(systemName: "arrow.up") } }
```

**UIKit:**
```swift
func refreshStatus() {
    let useSymbol = UIAccessibility.shouldDifferentiateWithoutColor
    statusIcon.image = useSymbol
        ? UIImage(systemName: status == .ok ? "checkmark.circle.fill" : "xmark.circle.fill")
        : nil
    statusLabel.text = status == .ok ? "Connected" : "Offline"   // always show text
}
```

---

## 9. Haptic and audio as accessibility cues

Haptics are confirmation for users who can't see animations. Pair them with VoiceOver announcements to reach parity with sighted users.

### 9.1 UIKit feedback generators

```swift
// Impact — physical collision, button press
let impact = UIImpactFeedbackGenerator(style: .medium)  // .light .medium .heavy .soft .rigid
impact.prepare(); impact.impactOccurred(intensity: 0.8)

// Notification — task outcome
UINotificationFeedbackGenerator().notificationOccurred(.success)  // .success .warning .error

// Selection — discrete value change (picker tick)
UISelectionFeedbackGenerator().selectionChanged()
```

Call `.prepare()` shortly before firing to prime the Taptic Engine and minimize latency.

### 9.2 SwiftUI `.sensoryFeedback` (iOS 17+)

Built-in types: `.success`, `.warning`, `.error`, `.selection`, `.impact` (with optional `weight:`/`intensity:`), `.increase`, `.decrease`, `.start`, `.stop`, `.alignment`, `.levelChange`, `.pathComplete`.

```swift
Button("Save") { saved.toggle() }.sensoryFeedback(.success, trigger: saved)

// Closure to choose conditionally
.sensoryFeedback(trigger: errorCode) { _, new in
    switch new { case 1: .warning; case 2: .error; default: nil }
}

// Impact with weight/intensity
.sensoryFeedback(.impact(weight: .heavy, intensity: 0.6), trigger: tapCount)
```

Note: iPad doesn't play haptics, only audio. `.start`/`.stop` are primarily watchOS.

### 9.3 Core Haptics for custom patterns

For bespoke vibration curves or audio-haptic synchrony (game explosion, custom confirmation pattern):

```swift
import CoreHaptics
let engine = try CHHapticEngine(); try engine.start()
let sharp = CHHapticEvent(eventType: .hapticTransient,
    parameters: [
        .init(parameterID: .hapticIntensity, value: 1.0),
        .init(parameterID: .hapticSharpness, value: 0.9)
    ], relativeTime: 0)
let pattern = try CHHapticPattern(events: [sharp], parameters: [])
try engine.makePlayer(with: pattern).start(atTime: CHHapticTimeImmediate)
```

Check `CHHapticEngine.capabilitiesForHardware().supportsHaptics` first.

### 9.4 Audio cues respecting system context

Use `AudioServicesPlaySystemSound(_:)` or `AVAudioPlayer`. Configure the session carefully:

- Ambient/decorative feedback → `AVAudioSession.Category.ambient` (mixes with other audio, respects the silent switch).
- Essential feedback (alarm, timer) → `.playback` (overrides silent), only if the user opted in.
- Never bypass the silent switch for decorative cues.

### 9.5 Haptic + VoiceOver parity pattern

```swift
func deleteItem() {
    store.delete()
    UINotificationFeedbackGenerator().notificationOccurred(.success)
    UIAccessibility.post(notification: .announcement, argument: "Item deleted")
}
```

The confetti is invisible to a VoiceOver user; the haptic plus spoken announcement closes the gap.

---

## 10. Button Shapes, On/Off Labels, and other system preferences

A compact reference to the remaining preference flags — each with its UIKit property, change notification, and SwiftUI environment value (where Apple exposes one).

### 10.1 Button Shapes
- **UIKit:** `UIAccessibility.buttonShapesEnabled`
- **Notification:** `UIAccessibility.buttonShapesEnabledStatusDidChangeNotification`
- **SwiftUI:** `@Environment(\.accessibilityShowButtonShapes)`

Underlines/shapes appear on system buttons automatically. Custom `ButtonStyle`s must opt in:
```swift
struct MyButtonStyle: ButtonStyle {
    @Environment(\.accessibilityShowButtonShapes) var show
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding(.horizontal, 12).padding(.vertical, 8)
            .overlay(RoundedRectangle(cornerRadius: 6)
                .stroke(.tint, lineWidth: show ? 1 : 0))
    }
}
```

### 10.2 On/Off Switch Labels
- **UIKit:** `UIAccessibility.isOnOffSwitchLabelsEnabled` (`UISwitch` adapts automatically)
- **Notification:** `UIAccessibility.onOffSwitchLabelsDidChangeNotification`
- **SwiftUI:** no dedicated env value — read the UIKit property; system `Toggle` adapts.

### 10.3 Prefer Cross-Fade Transitions (iOS 14+)
- **UIKit:** `UIAccessibility.prefersCrossFadeTransitions` — see §5.
- **Notification:** `UIAccessibility.prefersCrossFadeTransitionsStatusDidChange` (priming quirk documented above).

### 10.4 Prefer Non-Blinking Text Insertion Indicator (iOS 17+)
- Lives on the `Accessibility` framework: `AccessibilitySettings.prefersNonBlinkingTextInsertionIndicator`. System text views honor it automatically; custom editors must suppress their blink.

### 10.5 Video Autoplay
- **UIKit:** `UIAccessibility.isVideoAutoplayEnabled` (`true` = autoplay OK). Gate autoplay on this.
- **Notification:** `UIAccessibility.videoAutoplayStatusDidChangeNotification`

### 10.6 Closed Captioning
- **UIKit:** `UIAccessibility.isClosedCaptioningEnabled`; `AVPlayerViewController` honors automatically.
- **Notification:** `UIAccessibility.closedCaptioningStatusDidChangeNotification`

### 10.7 Bold Text
- **UIKit:** `UIAccessibility.isBoldTextEnabled`
- **Notification:** `UIAccessibility.boldTextStatusDidChangeNotification`
- **SwiftUI:** `@Environment(\.legibilityWeight)` (`.regular` / `.bold`)
```swift
@Environment(\.legibilityWeight) var weight
Text("Hi").fontWeight(weight == .bold ? .bold : .regular)
```

### 10.8 Invert Colors
- **UIKit:** `UIAccessibility.isInvertColorsEnabled`; per view `view.accessibilityIgnoresInvertColors = true`.
- **SwiftUI:** `.accessibilityIgnoresInvertColors()` on images, video, previews.
```swift
Image("HeroPhoto").accessibilityIgnoresInvertColors()
```

### 10.9 Other preference flags (quick table)

| Setting | UIKit | Notification | SwiftUI env |
|---|---|---|---|
| VoiceOver running | `isVoiceOverRunning` | `voiceOverStatusDidChangeNotification` | — |
| Switch Control running | `isSwitchControlRunning` | `switchControlStatusDidChangeNotification` | — |
| AssistiveTouch | `isAssistiveTouchRunning` | `assistiveTouchStatusDidChangeNotification` | — |
| Speak Selection | `isSpeakSelectionEnabled` | `speakSelectionStatusDidChangeNotification` | — |
| Speak Screen | `isSpeakScreenEnabled` | `speakScreenStatusDidChangeNotification` | — |
| Mono Audio | `isMonoAudioEnabled` | `monoAudioStatusDidChangeNotification` | — |
| Grayscale | `isGrayscaleEnabled` | `grayscaleStatusDidChangeNotification` | — |
| Guided Access | `isGuidedAccessEnabled` | `guidedAccessStatusDidChangeNotification` | — |
| Shake to Undo | `isShakeToUndoEnabled` | `shakeToUndoDidChangeNotification` | — |
| Any AT active | — | — | `@Environment(\.accessibilityEnabled)` |

**Pattern summary.** SwiftUI: read the env value; views re-render automatically. UIKit: read the property at layout time *and* register an observer so the UI refreshes when the user toggles the setting while your app is visible.

---

## 11. Testing tools and workflow

### 11.1 Accessibility Inspector

Launch from **Xcode → Open Developer Tool → Accessibility Inspector**. The target picker (top-left) selects Mac, a running simulator, or a USB-connected device (trust + developer mode required).

- **Inspection pointer** reveals Label, Value, Traits, Identifier, Hint, Custom Actions, Frame, and the element hierarchy for any UI element.
- **Audit tab** runs an automated audit. Click **Run Audit**; each issue is clickable and jumps focus in the running app.
- **Settings tab** gives live toggles: Invert Colors, Increase Contrast, Reduce Motion, Reduce Transparency, Button Shapes, On/Off Labels, Bold Text, Differentiate Without Color, Smart Invert, and a Dynamic Type slider from xSmall to AX5.
- **Speech pane** simulates VoiceOver utterances without enabling VoiceOver on-device.

Audit categories: Contrast, Dynamic Type, Hit Region (≥44×44pt), Clipped Text, Sufficient Element Description, Element Detection, Parent/Child/Traits.

### 11.2 `performAccessibilityAudit()` in UI tests (WWDC23 #10035)

Introduced in Xcode 15 / iOS 17 SDK and enhanced every year since. The API:

```swift
try app.performAccessibilityAudit()                              // full
try app.performAccessibilityAudit(for: [.contrast, .dynamicType])
try app.performAccessibilityAudit(for: .all.subtracting(.sufficientElementDescription))
try app.performAccessibilityAudit(for: .all) { issue in
    // Return true to IGNORE this issue
    issue.auditType == .contrast && issue.element?.label == "LegalButton"
}
```

`XCUIAccessibilityAuditType` is an OptionSet: `.all`, `.contrast`, `.dynamicType`, `.elementDetection`, `.hitRegion`, `.sufficientElementDescription`, `.parentChildOrderRelationship`, `.textClipped`, `.trait`, `.action`. Failed checks report inline in the Report navigator — no explicit assertions needed.

### 11.3 VoiceOver on device

Enable at **Settings → Accessibility → VoiceOver**. Add to **Accessibility Shortcut** and trigger with **triple-click side button** (Face ID) or **triple-click Home button** (Touch ID). Also addable to Control Center.

Core gestures:
- Single-finger swipe L/R: next/previous element
- Double-tap: activate
- Two-finger double-tap: Magic Tap (play/pause, primary action)
- Two-finger Z-scrub: escape/dismiss
- Two-finger swipe down: continuous read
- Three-finger swipe: scroll page / swipe page
- Three-finger triple-tap: toggle screen curtain
- Four-finger tap top/bottom: first/last element
- Rotor: rotate two fingers; then single-finger swipe up/down within category

### 11.4 Environment Overrides in Xcode

With the app running, click the **sliders icon** in the debug bar (between Debug Memory Graph and Simulate Location), or **Debug → View Debugging → Configure Environment Overrides** on older Xcode. Toggles include Interface Style, Dynamic Type (slider to AX5), Increase Contrast, Reduce Transparency, Reduce Motion, Bold Text, Button Shapes, On/Off Labels, Grayscale, Smart Invert, Differentiate Without Color, Prefer Cross-Fade Transitions. Changes apply live.

### 11.5 A concrete per-screen testing workflow

1. **Dynamic Type sweep** at xSmall, Large, xxxLarge, AX1, AX3, AX5. Nothing clipped; layout reflows vertically where needed.
2. **VoiceOver navigation** — swipe right through the entire screen; verify order, labels, hints, traits, magic tap, and escape gesture. Check the Headings rotor contains what it should.
3. **Switch Control** — Auto Scanning reaches every actionable element; no focus traps or voids.
4. **Voice Control** — `"Show names"` overlay reveals a speakable label on every control; `"Tap [name]"` works for each; `"Show numbers"` and `"Show grid"` respond.
5. **Reduce Motion on** — slide/scale animations became cross-fades or disappeared.
6. **Reduce Transparency on** — materials became solids, especially behind text.
7. **Increase Contrast on** — contrast meets WCAG; semantic colors picked HC variants; borders thickened where planned.
8. **Differentiate Without Color on** — every state that was color-encoded now also has a symbol/shape/text cue.
9. **Bold Text on** — fonts switch to bold; no layout breakage.
10. **Dark Mode + High Contrast** combo — still legible.
11. **Large Content Viewer** — long-press small tab-bar/toolbar items reveals large content at AX sizes.
12. **Form focus** — each field announces its label and state when focused.
13. **`performAccessibilityAudit()`** runs green in CI as a regression net.

---

## 12. AccessibilityRepresentation

`.accessibilityRepresentation { ... }` lets a custom-drawn view borrow the accessibility tree of a standard SwiftUI control. The representation view is **never rendered** — it's consulted only to build the accessibility tree. This is far less error-prone than hand-plastering labels, values, traits, adjustable actions, and increment/decrement handlers onto a bespoke view.

- **Availability:** iOS 14+ in principle, but the idiomatic usage and supporting infrastructure landed in **WWDC 2021 session 10119 "SwiftUI Accessibility: Beyond the Basics"**.
- **Canonical current reference:** **WWDC 2024 session 10073 "Catch up on accessibility in SwiftUI"**, which refines it and connects it to App Intent–driven actions.

**Custom slider that exposes a standard Slider:**
```swift
struct CustomSlider: View {
    @Binding var value: Double
    let range: ClosedRange<Double> = 0...100
    var body: some View {
        GeometryReader { geo in
            ZStack(alignment: .leading) {
                Capsule().fill(.secondary.opacity(0.3)).frame(height: 4)
                Capsule().fill(.tint)
                    .frame(width: CGFloat(value / range.upperBound) * geo.size.width, height: 4)
                Circle().fill(.tint).frame(width: 24, height: 24)
                    .offset(x: CGFloat(value / range.upperBound) * geo.size.width - 12)
                    .gesture(DragGesture(minimumDistance: 0).onChanged { g in
                        let pct = min(max(0, g.location.x / geo.size.width), 1)
                        value = Double(pct) * range.upperBound
                    })
            }
        }
        .frame(height: 24)
        .accessibilityRepresentation {
            Slider(value: $value, in: range) { Text("Volume") }
        }
    }
}
```

**Custom ring gauge that exposes a ProgressView:**
```swift
struct CustomRingGauge: View {
    let progress: Double   // 0...1
    var body: some View {
        ZStack {
            Circle().stroke(.secondary.opacity(0.25), lineWidth: 10)
            Circle().trim(from: 0, to: progress)
                .stroke(.tint, style: .init(lineWidth: 10, lineCap: .round))
                .rotationEffect(.degrees(-90))
            Text("\(Int(progress * 100))%").font(.headline)
        }
        .frame(width: 120, height: 120)
        .accessibilityRepresentation {
            ProgressView(value: progress) { Text("Download progress") }
        }
    }
}
```

**Contrast with `.accessibilityChildren { ... }`:** that modifier *adds* accessibility children to the current element (useful for charts with many logical parts), instead of *replacing* the element's accessibility with a different standard control.

---

## 13. SwiftUI accessibility modifiers — full reference

Every modifier below lives on `View` in SwiftUI. Default availability iOS 14.0+/iPadOS 14.0+/macOS 11.0+/tvOS 14.0+/watchOS 7.0+ unless noted.

| Modifier | Purpose | Example |
|---|---|---|
| `.accessibilityLabel(_:)` | The element's name (first thing VoiceOver speaks). iOS 18+: accepts a `@ViewBuilder` for rich labels and an `isEnabled:` parameter. | `Image("fav").accessibilityLabel("Favorite")` |
| `.accessibilityHint(_:)` | Short description of *what happens* when activated. | `Button("Send"){}.accessibilityHint("Sends your message")` |
| `.accessibilityValue(_:)` | Current state of a stateful element. | `ring.accessibilityValue("\(percent)%")` |
| `.accessibilityIdentifier(_:)` | Non-user-facing ID for UI tests and some Voice Control matching. | `.accessibilityIdentifier("buyButton")` |
| `.accessibilityHidden(_:)` | Hide from accessibility, keep visible. | `decorative.accessibilityHidden(true)` |
| `.accessibilityElement(children:)` | Make this view an accessibility element: `.ignore`, `.combine`, `.contain`. | `HStack{...}.accessibilityElement(children: .combine)` |
| `.accessibilityAddTraits(_:)` / `.accessibilityRemoveTraits(_:)` | Manage traits (see §1.4). | `row.accessibilityAddTraits(.isButton)` |
| `.accessibilityAction(_:_:)` | Standard actions: `.default`, `.escape`, `.magicTap`. | `.accessibilityAction(.escape){ dismiss() }` |
| `.accessibilityAction(named:_:)` | Named action in the Actions rotor. | `.accessibilityAction(named: "Delete"){ delete() }` |
| `.accessibilityActions { }` (iOS 17+) | Group multiple actions declaratively. | `.accessibilityActions { Button("Reply"){}; Button("Delete"){} }` |
| `.accessibilityRotor(_:entries:)` (iOS 15+) | Custom VoiceOver rotor category. Also supports text ranges. | see §1.7 |
| `.accessibilitySortPriority(_:)` | Higher priority → earlier in swipe order within the container. | `title.accessibilitySortPriority(2)` |
| `.accessibilityHeading(_:)` (iOS 15+) | Mark as heading with level `.h1`–`.h6` or `.unspecified`. | `Text("Chapter").accessibilityHeading(.h1)` |
| `.accessibilityInputLabels(_:)` | Alternate spoken names for Voice Control. | `.accessibilityInputLabels(["Submit","Send","Post"])` |
| `.accessibilityRepresentation { }` | Substitute accessibility tree with a standard control's tree. | see §12 |
| `.accessibilityFocused(_:_:)` (iOS 15+) with `@AccessibilityFocusState` | Programmatic VoiceOver / Switch Control focus. iOS 17+: focus-technology scopes. | see §3.6 |
| `.accessibilityShowsLargeContentViewer()` (iOS 15+) | Opt into Large Content Viewer long-press preview. | `.accessibilityShowsLargeContentViewer { Label("Home", systemImage:"house") }` |
| `.accessibilityIgnoresInvertColors(_:)` | Exclude from Smart Invert (photographs). | `photo.accessibilityIgnoresInvertColors()` |
| `.accessibilitySpeechPhoneticRepresentation(_:)` (iOS 15+) | IPA pronunciation hint. | `Text("Siobhán").accessibilitySpeechPhoneticRepresentation("ʃɪˈvɔːn")` |
| `.accessibilitySpeechPunctuation(_:)` (iOS 15+) | Force VoiceOver to speak all punctuation. | `code.accessibilitySpeechPunctuation(true)` |
| `.accessibilitySpeechSpellsOutCharacters(_:)` (iOS 15+) | Spell characters one by one (codes, OTPs). | `otp.accessibilitySpeechSpellsOutCharacters()` |
| `.accessibilitySpeechAnnouncesEmphasis(_:)` (iOS 15+) | Announce bold/italic. | `quote.accessibilitySpeechAnnouncesEmphasis()` |
| `.accessibilityTextContentType(_:)` (iOS 15+) | Content-kind hint: `.plain`, `.console`, `.fileSystem`, `.messaging`, `.narrative`, `.sourceCode`, `.spreadsheet`, `.wordProcessing`. | `logView.accessibilityTextContentType(.console)` |
| `.accessibilityZoomAction { }` (iOS 15+) | Handle VoiceOver zoom gesture on a map/chart. | `map.accessibilityZoomAction { a in a.direction == .zoomIn ? zoomIn() : zoomOut() }` |
| `.accessibilityChildren { }` (iOS 15+) | Populate a container's accessibility children with non-rendered views. | see §12 |
| `.accessibilityDirectTouch(_:options:)` (iOS 17+) | Direct-touch region. Options: `.silentOnTouch`, `.requiresActivation`. | `keyboard.accessibilityDirectTouch(options: .silentOnTouch)` |
| `.accessibilityCustomContent(_:_:importance:)` (iOS 15+, broadly iOS 17+) | Supplementary content in VoiceOver's More Content rotor. | `.accessibilityCustomContent(.age, "\(user.age)", importance: .high)` |
| `.accessibilityActivationPoint(_:)` | Set the point VoiceOver taps. | `.accessibilityActivationPoint(UnitPoint(x: 0.9, y: 0.5))` |
| `.accessibilityRespondsToUserInteraction(_:)` (iOS 16+) | Declare whether element is interactive. | `card.accessibilityRespondsToUserInteraction(false)` |
| `.accessibilityLinkedGroup(id:in:)` (iOS 15+) | Link scattered elements so VO treats them as adjacent. | see docs |
| `.accessibilityLabeledPair(role:id:in:)` (iOS 15+) | Associate a separate `Text` label with its content control. | `Text("Wi-Fi").accessibilityLabeledPair(role: .label, id: "wifi", in: ns)` |
| `.sensoryFeedback(_:trigger:)` (iOS 17+) | Play haptic/audio feedback on value change. | `.sensoryFeedback(.success, trigger: saved)` |
| `.speechAdjustedPitch(_:)` (iOS 16+) | Raise/lower VoiceOver pitch (−1...1). | `.speechAdjustedPitch(0.5)` |
| `.accessibilityDefaultFocus` (iOS 26+, WWDC25 #229) | Suggest initial accessibility focus when the scene appears. | see below |

### 13.1 New in iOS 18 (WWDC24 #10073)

- `isEnabled:` parameter on most accessibility modifiers for conditional application without fallback plumbing.
- `.accessibilityLabel { ... }` — `@ViewBuilder` form for rich label composition.
- First-class VoiceOver drag-and-drop support, surfaced automatically to SwiftUI drag/drop views.
- `.accessibilityAction(intent: MyAppIntent())` — actions driven by App Intents so Siri, Shortcuts, and VoiceOver actions share implementation.
- Drop-point annotation for VoiceOver drag-and-drop targets.

### 13.2 New in iOS 26 (WWDC25)

- **`.accessibilityDefaultFocus`** — suggest the initial element for assistive-technology focus when a scene appears. The system may still override based on user preference. From WWDC25 #229 "Make your Mac app more accessible to everyone" (applies across platforms).
- **`AssistiveAccess` Scene** — declare a simplified UI specifically for systemwide Assistive Access (original iOS 17 feature now extended). Previewable via `#Preview(traits: .assistiveAccess)`. Covered in WWDC25 #238 "Customize your app for Assistive Access".
- **Scene bridging** — UIKit scene delegates can declare a SwiftUI `AssistiveAccess` scene via `static rootScene`.
- **Accessibility Nutrition Labels** — App Store Connect metadata declaring which accessibility features your app supports (VoiceOver, Voice Control, Larger Text, Captions, Sufficient Contrast, Differentiate Without Color, Reduced Motion, Dark Interface). Voluntary now; Apple has indicated it will be required.
- **Voice Control in Xcode 26** — dictate Swift code with a programming-aware vocabulary that syncs across devices.
- **BCI Switch Control** — iOS 26 supports brain-computer-interface switches alongside existing switch types; your app needs no code changes as long as accessibility order is correct.
- **Liquid Glass + VoiceOver** — VoiceOver descriptions now convey the new material's depth and translucency for redesigned system controls.
- **Accessibility Reader**, **Braille Access**, and **Magnifier for Mac** ship systemwide.

Example (current WWDC25 wording; confirm exact symbol in the iOS 26 SDK):
```swift
struct CheckoutView: View {
    @AccessibilityFocusState private var focus: Field?
    var body: some View {
        Form { ... }
            .accessibilityDefaultFocus($focus, equals: .name)
    }
}
```

---

## 14. Anti-patterns — the mistakes that ship

These are the recurring failures surfaced by Xcode Accessibility Audits, App Store reviewers, and production bug reports. Treat them as a pre-PR checklist.

**Generic "Image" labels.** An `Image` with no meaningful label reads as "Image" in VoiceOver. Either give it a real label describing its content, or mark it `accessibilityHidden(true)` if it's decorative and the surrounding text already conveys the meaning.

**Icon-only buttons without labels.** A paper-airplane button that VoiceOver reads as just "Button" is unusable. Always set `accessibilityLabel`, and think about what a Voice Control user would say: "Tap Send" should work, so the label must contain "Send" or `accessibilityInputLabels` must include it.

**Color-only status.** A red dot next to "3 items" tells a colorblind user nothing. Pair color with a symbol (`exclamationmark.triangle.fill`) and a text label ("Error, 3 items"), and combine them with `.accessibilityElement(children: .combine)`.

**Hardcoded text sizes.** `Text("Hello").font(.system(size: 14))` will never scale. Use `.font(.body)` or `.custom(_:size:relativeTo:)`. In UIKit, use `UIFont.preferredFont(forTextStyle:)` with `adjustsFontForContentSizeCategory = true`.

**Fixed heights on text containers.** `Text("…").frame(height: 44)` guarantees clipping at AX5. Use `minHeight:` or let the container grow.

**Missing hints on non-obvious buttons.** A "▶︎" button that resumes playback from a specific track location should hint the consequence ("Resumes from the saved position"), not leave the user to guess.

**Accessibility modifiers on a container while children aren't combined.** Slapping `.accessibilityLabel("Profile card")` on a `VStack` without `.accessibilityElement(children:)` means VoiceOver still visits each child independently *and* the label is ignored. Always pair label overrides with an element-making modifier.

**Parallax that ignores Reduce Motion.** Any `UIMotionEffect` or SwiftUI `offset` tied to device tilt must branch on `accessibilityReduceMotion` and render a static alternative.

**Custom materials that ignore Reduce Transparency.** Remember that `.ultraThinMaterial` does not auto-swap to opaque. Branch on `accessibilityReduceTransparency` or layered visuals will stay unreadable.

**VoiceOver announcements used as primary UX.** Posting `.announcement` is fine for confirmations; it's a bug when it's the *only* way a state change is communicated (e.g., error shown only via announcement with no visible text).

**Inconsistent labels after state changes.** A heart button whose label stays "Favorite" after the user favorites it is a liar. Update the label to "Unfavorite" (or toggle `.isSelected`) whenever state changes.

**Duplicate speakable labels.** Three "Edit" buttons in a list force a Voice Control disambiguation dialog on every utterance. Disambiguate with item-specific labels (`"Edit birthday plans"`).

**Skipping the `adjustsFontForContentSizeCategory` flag in UIKit.** It's `false` by default. Easy to miss; means no Dynamic Type at all.

**Custom font without `relativeTo:`.** `.custom("Avenir", size: 17)` never scales — the top Dynamic Type bug in bespoke design systems.

**Relying on `minimumScaleFactor`.** It's a compromise for single-line badges, not a Dynamic Type strategy. Below ~0.7 the text is unreadable at AX5 anyway.

**`.accessibilityHidden(true)` on ancestors.** Silences entire subtrees. Audit regularly.

**Direct-touch regions without escape routes.** A full-screen `.allowsDirectInteraction` view traps VoiceOver users with no way to leave. Leave navigable controls around the edge.

**Haptic without announcement.** Firing `.success` haptic after a destructive action is fine, but VoiceOver users also need the spoken confirmation — post an `.announcement` or `layoutChanged` notification.

---

## 15. WWDC session references

The definitive Apple videos on each topic. These are the source-of-truth citations you want in code review comments.

- **WWDC 2019 session 238 — "Accessibility in SwiftUI"** — foundational SwiftUI accessibility session (the request references a "WWDC20 SwiftUI Accessibility" session; Apple's canonical SwiftUI accessibility session from the SwiftUI launch era is this WWDC19 talk).
- **WWDC 2019 session 254 — "Writing Great Accessibility Labels"** — where the "don't include button" and related writing rules are codified.
- **WWDC 2020 session 10020 — "Make your app visually accessible"** — Reduce Motion, Reduce Transparency, Increase Contrast, Differentiate Without Color.
- **WWDC 2020 session 10019 — "App Accessibility for Switch Control"**.
- **WWDC 2020 session 10116 — "VoiceOver efficiency with custom rotors"**.
- **WWDC 2021 session 10119 — "SwiftUI Accessibility: Beyond the Basics"** — introduces `accessibilityRepresentation`, custom rotors, focus management, and text-range rotors.
- **WWDC 2023 session 10035 — "Perform accessibility audits for your app"** — the canonical reference for `XCUIApplication.performAccessibilityAudit()`.
- **WWDC 2023 session 10036 — "Build accessible apps with SwiftUI and UIKit"** — new traits, Swift-native `AccessibilityNotification`, priority announcements.
- **WWDC 2024 session 10073 — "Catch up on accessibility in SwiftUI"** — App Intent actions, iOS 18 `isEnabled:` parameter, `@ViewBuilder` labels, VoiceOver drag-and-drop.
- **WWDC 2024 session 10074 — "Get started with Dynamic Type"** — the `AnyLayout` H↔V swap pattern and the canonical testing-at-AX5 workflow.
- **WWDC 2025 session 229 — "Make your Mac app more accessible to everyone"** — introduces `.accessibilityDefaultFocus`.
- **WWDC 2025 session 238 — "Customize your app for Assistive Access"** — the `AssistiveAccess` scene.

---

## 16. Conclusion — what this all adds up to

Accessibility on Apple platforms is not a checklist; it's a **parallel UI contract** — every visible affordance has a non-visual, non-motor, non-color-dependent equivalent, wired through a small set of well-defined APIs. In iOS 26 that contract is tighter than ever: App Store Connect now ships **Accessibility Nutrition Labels**, Xcode's `performAccessibilityAudit()` catches regressions in CI, Liquid Glass raises the stakes for Reduce Transparency, and BCI Switch Control adds an input method that rewards the exact same good hygiene — correct accessibility order, combined groupings, focused sort priority — that VoiceOver users have always needed.

The shortest useful summary of the whole document is this: **label every element like a human named it**; **scale every number next to text with `@ScaledMetric`**; **swap layout at `isAccessibilitySize`**; **never encode state in color alone**; **branch on the six preference flags** (Reduce Motion, Reduce Transparency, Increase Contrast, Differentiate Without Color, Bold Text, Button Shapes); **pair visual feedback with haptic and announcement** so VoiceOver users get parity; and **wire `performAccessibilityAudit()` into CI** so the discipline doesn't regress. Everything else in this document is a refinement of those seven rules.

Two forward-looking notes worth internalizing. First, the 2024 `.accessibilityRepresentation` and 2025 `.accessibilityDefaultFocus` modifiers are subtle but transformative: together they mean *custom visuals no longer cost accessibility* — a custom ring gauge can expose as a `ProgressView` and suggest itself for initial focus with two modifiers, no boilerplate. Second, Accessibility Nutrition Labels turn accessibility from a silent quality bar into a **visible product attribute** on the App Store. Apps that invest now will lead their categories when labels become mandatory; apps that don't will explain themselves to users who check the label first.