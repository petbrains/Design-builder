---
name: ambient-surfaces
description: Widgets, Live Activities, Dynamic Island, StandBy, Control Center, Lock Screen (iOS 17 → 26)
platform: ios
---

# Apple's ambient and glanceable surfaces: a Swift/SwiftUI reference (iOS 17 → iOS 26)

> A single-source developer reference for widgets, Live Activities, Dynamic Island, StandBy, Control Center, and Lock Screen on Apple platforms. Covers iOS 17 baseline with iOS 18 and iOS 26 features clearly marked. All code is Swift 5.9+/Swift 6 and SwiftUI only.

---

## How to read this document

Each section covers one **surface** (widget, Live Activity, Dynamic Island region, control, etc.) with four parts: **the API**, **SwiftUI code examples**, **sizing/constraint tables**, and **design callouts + anti-patterns**. WWDC citations are inline. Items introduced after iOS 17 are tagged **[iOS 18]** or **[iOS 26]**.

> **Design callouts** appear in blockquotes like this, typically sourced from Apple's Human Interface Guidelines or a specific WWDC session.

🚫 **Anti-patterns** are called out explicitly. Treat them as do-not-ship patterns.

---

# 1. WidgetKit fundamentals

## 1.1 Widget families

`WidgetFamily` enumerates the possible sizes and placements. A widget opts in via `.supportedFamilies(_:)` on its `WidgetConfiguration`.

| Case | Platform | Typical use |
|---|---|---|
| `.systemSmall` | iOS, iPadOS, macOS, visionOS | One data point, single tap target. Also the **only family used in StandBy**. |
| `.systemMedium` | iOS, iPadOS, macOS, visionOS | Two or three data points; multiple tap targets via `Link`. |
| `.systemLarge` | iOS, iPadOS, macOS, visionOS | List-style content with richer hierarchy. |
| `.systemExtraLarge` | iPadOS 15+, macOS | iPad/Mac only; dense dashboards. |
| `.systemExtraLargePortrait` **[iOS 26]** | visionOS 26 | Tall poster-style spatial widget. |
| `.accessoryCircular` | iOS 16+ Lock Screen, watchOS 9+ | Gauge, single glyph, percentage. |
| `.accessoryRectangular` | iOS 16+ Lock Screen, watchOS 9+ | Two–three lines of text, mini-chart. |
| `.accessoryInline` | iOS 16+ Lock Screen (above clock), watchOS 9+ | Single line of system-font text. |

> Apple **does not publish an authoritative pixel/point table** for widget sizes. The guidance from WWDC 2020 *"Design great widgets"* is to lay out in SwiftUI using points and stacks, not pixels. At runtime, read `context.displaySize: CGSize` inside your `TimelineProvider` or use `GeometryReader`.

**Approximate widget container points (iPhone, community-measured):**

| Device class (pt) | Small | Medium | Large |
|---|---|---|---|
| 430×932 (iPhone 15/16/17 Pro Max) | ~170×170 | ~364×170 | ~364×382 |
| 393×852 (iPhone 15/16 Pro, 15/16) | ~158×158 | ~338×158 | ~338×354 |
| 390×844 (iPhone 12–14) | 158×158 | 338×158 | 338×354 |
| 375×667 (iPhone SE 2nd/3rd gen) | 148×148 | 321×148 | 321×324 |

**iPad (points):**

| Device | Small | Medium | Large | Extra Large |
|---|---|---|---|---|
| 12.9" iPad Pro | 170×170 | 379×170 | 379×379 | 795×379 |
| 11" iPad Pro / Air | 155×155 | 342×155 | 342×342 | 716×342 |
| iPad mini | 141×141 | 306×141 | 306×306 | 635×306 |

**Lock Screen / watchOS accessory (points, approx):** `.accessoryCircular` ~76×76; `.accessoryRectangular` ~160×72 iPhone / ~170×76 Series 7+; `.accessoryInline` single line, status-area width.

## 1.2 The TimelineProvider protocol

Widgets are **timelines of static snapshots**. The provider supplies (a) a *placeholder*, (b) a *snapshot* (for gallery/preview), and (c) a *timeline* of entries with a reload policy.

```swift
import WidgetKit
import SwiftUI

struct SimpleEntry: TimelineEntry {
    let date: Date
    let value: Int
    var relevance: TimelineEntryRelevance?
}

struct Provider: TimelineProvider {
    typealias Entry = SimpleEntry

    // 1) Synchronous placeholder — must be instant.
    func placeholder(in context: Context) -> SimpleEntry {
        SimpleEntry(date: .now, value: 0)
    }

    // 2) Snapshot for the widget gallery / transient state.
    //    `context.isPreview == true` means gallery — return mock data.
    func getSnapshot(in context: Context,
                     completion: @escaping (SimpleEntry) -> Void) {
        completion(SimpleEntry(date: .now, value: 42))
    }

    // 3) Real timeline + reload policy.
    func getTimeline(in context: Context,
                     completion: @escaping (Timeline<SimpleEntry>) -> Void) {
        let now = Date()
        let entries = (0..<5).map { i in
            SimpleEntry(date: now.addingTimeInterval(TimeInterval(i) * 900),
                        value: i)
        }
        completion(Timeline(entries: entries, policy: .atEnd))
    }
}
```

**Async variant (iOS 17+).** `AppIntentTimelineProvider` accepts a configuration intent and uses `async`/`await` instead of completion handlers.

```swift
struct AsyncProvider: AppIntentTimelineProvider {
    typealias Entry = SimpleEntry
    typealias Intent = ConfigIntent

    func placeholder(in context: Context) -> SimpleEntry { … }

    func snapshot(for configuration: ConfigIntent,
                  in context: Context) async -> SimpleEntry { … }

    func timeline(for configuration: ConfigIntent,
                  in context: Context) async -> Timeline<SimpleEntry> { … }
}
```

`TimelineProviderContext` exposes `family: WidgetFamily`, `displaySize: CGSize`, `isPreview: Bool`, and `environmentVariants`.

> **Don't do network I/O in `placeholder(in:)`.** It runs synchronously and must be instant. Use `getSnapshot` with `context.isPreview == true` for fast mock data. — WWDC 2020, *Meet WidgetKit* (10028).

## 1.3 Configuration types

| Type | Introduced | When to use |
|---|---|---|
| `StaticConfiguration` | iOS 14 | No user configuration. |
| `IntentConfiguration` | iOS 14 | **Legacy.** SiriKit `.intentdefinition` file. |
| `AppIntentConfiguration` | iOS 17 | **Recommended.** User-configurable using the App Intents framework (Swift-only). |
| `ActivityConfiguration` | iOS 16.1 | Live Activities. |
| `StaticControlConfiguration` / `AppIntentControlConfiguration` | iOS 18 | Control widgets (Control Center, Lock Screen, Action Button). |
| `RelevanceConfiguration` | iOS 26 / watchOS 26 | Widgets that appear only when contextually relevant. |

### `AppIntentConfiguration` end-to-end example

```swift
import WidgetKit
import AppIntents
import SwiftUI

// 1. Configuration intent.
struct WeatherConfigIntent: WidgetConfigurationIntent {
    static var title: LocalizedStringResource = "Weather"
    static var description = IntentDescription("Pick a city")
    @Parameter(title: "City", default: "San Francisco") var city: String
}

// 2. Timeline entry.
struct WeatherEntry: TimelineEntry {
    let date: Date
    let city: String
    let temperature: Int
    let condition: String
    let configuration: WeatherConfigIntent
}

// 3. Provider.
struct WeatherProvider: AppIntentTimelineProvider {
    func placeholder(in context: Context) -> WeatherEntry {
        WeatherEntry(date: .now, city: "—", temperature: 0,
                     condition: "—", configuration: WeatherConfigIntent())
    }
    func snapshot(for configuration: WeatherConfigIntent,
                  in context: Context) async -> WeatherEntry {
        WeatherEntry(date: .now, city: configuration.city,
                     temperature: 72, condition: "Sunny",
                     configuration: configuration)
    }
    func timeline(for configuration: WeatherConfigIntent,
                  in context: Context) async -> Timeline<WeatherEntry> {
        let now = Date()
        let entries = (0..<4).map { i in
            WeatherEntry(date: now.addingTimeInterval(TimeInterval(i) * 3600),
                         city: configuration.city,
                         temperature: 70 + i, condition: "Sunny",
                         configuration: configuration)
        }
        return Timeline(entries: entries,
                        policy: .after(now.addingTimeInterval(3600)))
    }
}

// 4. View.
struct WeatherWidgetView: View {
    let entry: WeatherEntry
    var body: some View {
        VStack(alignment: .leading) {
            Text(entry.city).font(.headline)
            Text("\(entry.temperature)°").font(.system(size: 44, weight: .bold))
            Text(entry.condition).font(.caption)
        }
        .containerBackground(.fill.tertiary, for: .widget)
    }
}

// 5. Widget.
struct WeatherWidget: Widget {
    let kind = "WeatherWidget"
    var body: some WidgetConfiguration {
        AppIntentConfiguration(kind: kind,
                               intent: WeatherConfigIntent.self,
                               provider: WeatherProvider()) { entry in
            WeatherWidgetView(entry: entry)
        }
        .configurationDisplayName("Weather")
        .description("Current conditions for your chosen city.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}
```

## 1.4 Deep linking

Two orthogonal mechanisms:

- **`.widgetURL(_:)`** — one tap target for the whole widget. Required for `systemSmall`, `accessoryCircular`, `accessoryInline`. A widget supports exactly **one** `widgetURL`; multiple are undefined.
- **`Link(destination:)`** — multiple tap targets inside `systemMedium`, `systemLarge`, `systemExtraLarge`, and `accessoryRectangular`.

```swift
// Small — one tap target.
SmallEntryView(entry: entry)
    .widgetURL(URL(string: "myapp://weather/\(entry.city)"))

// Medium/Large — multiple Link views.
HStack {
    Link(destination: URL(string: "myapp://weather")!)  { … }
    Link(destination: URL(string: "myapp://calendar")!) { … }
    Link(destination: URL(string: "myapp://tasks")!)    { … }
}
```

Handle in the app with `.onOpenURL { … }` on the root scene.

---

# 2. Widget design principles

## 2.1 The three pillars

> From WWDC 2020 *Design great widgets* (10103) and the HIG *Widgets* chapter:
>
> 1. **Glanceable.** The user should extract value without scrolling, zooming, or tapping.
> 2. **Relevant.** Show what matters now — time, location, upcoming event, recent activity.
> 3. **Personalized.** Support configuration via App Intents so users tailor the view.

## 2.2 Relevance and the Smart Stack

Set `TimelineEntry.relevance: TimelineEntryRelevance?` with a `score: Float` (higher = more important) and optional `duration: TimeInterval`. The system uses this to pick which widget to surface in the iOS Smart Stack, in StandBy Smart Rotate, and in the watchOS 10+ Smart Stack (WWDC 2023, *Build widgets for the Smart Stack on Apple Watch*, 10029).

```swift
struct CalendarEntry: TimelineEntry {
    let date: Date
    let event: Event?
    var relevance: TimelineEntryRelevance? {
        guard let e = event else { return TimelineEntryRelevance(score: 0) }
        return TimelineEntryRelevance(
            score: 90,
            duration: e.endDate.timeIntervalSince(date))
    }
}
```

## 2.3 Interactivity (iOS 17+)

iOS 17 added two new initializers to SwiftUI: `Button(intent:)` and `Toggle(isOn:intent:)`, backed by `AppIntent`. Nothing else is interactive. See section 10 for detail.

## 2.4 Anti-patterns

| 🚫 Anti-pattern | ✅ Do instead |
|---|---|
| Treating a widget as a mini-app | It's a projection of your app's content onto the Home Screen |
| Scroll views, tabs, page controls | A single snapshot — use multiple sizes if more data is needed |
| Cramming 10+ fields in `systemSmall` | One headline + 2–3 supporting values |
| Fonts < 11pt | Use Dynamic Type: `.headline`, `.body`, `.caption` |
| Requiring tap to be useful | Widget is valuable at a glance; interaction is accelerator |
| Replacing primary navigation | Deep links drill into the app; nav lives in the app |
| Showing sensitive data unconditionally | `.privacySensitive()` so the Lock Screen redacts it |
| Using a logo to fill `systemSmall` | Show content; the App Icon label below handles identity |

---

# 3. Widget backgrounds and tinting

## 3.1 `.containerBackground(for:)` — mandatory for iOS 17+

Introduced in WWDC 2023 *Bring widgets to new places* (10027). If a widget built with the iOS 17 SDK omits this modifier, it shows the *"Please adopt containerBackground API"* placeholder and layout breaks.

```swift
WeatherView(entry: entry)
    .containerBackground(for: .widget) {
        LinearGradient(colors: [.blue, .cyan],
                       startPoint: .top, endPoint: .bottom)
    }
```

The system **removes this background automatically** in StandBy widgets, iPad Lock Screen, watchOS Smart Stack, macOS desktop, and the iOS 18+/iOS 26 tinted Home Screen. Widgets whose entire visual is the background (full-bleed photo, map) opt out:

```swift
.containerBackgroundRemovable(false)
```

Detect the background-removed state:

```swift
@Environment(\.showsWidgetContainerBackground) var hasBackground
```

## 3.2 Rendering modes

`@Environment(\.widgetRenderingMode)` exposes the current mode:

| Mode | Context | Behavior |
|---|---|---|
| `.fullColor` | Default Home Screen, macOS desktop, visionOS, CarPlay | No system recoloring |
| `.accented` **[iOS 18+]** | Tinted/dark Home Screen, watchOS complications | Content split into *accent group* and *default group*, each flattened to a system tint; opacity preserved |
| `.vibrant` | iOS Lock Screen, iPad Lock Screen, **StandBy Night Mode** | Desaturated to monochrome, recolored against wallpaper; only luminance/alpha survive |

Tag views that should be in the **accent group** with `.widgetAccentable()`:

```swift
Text(entry.title)
    .font(.headline)
    .widgetAccentable()          // accent group
```

## 3.3 `.widgetAccentedRenderingMode` on Image — iOS 18+

Controls how bitmap images behave under accented rendering.

| Value | Effect | Use for |
|---|---|---|
| `.accented` | Flat tint with accent color | SF Symbols, simple glyphs |
| `.accentedDesaturated` | Luminance-preserving tint | **Default for photos** |
| `.desaturated` | Black-and-white | Stylized photography |
| `.fullColor` | Keeps original colors | Album art, book covers (media) |

```swift
Image("albumArt")
    .resizable()
    .widgetAccentedRenderingMode(.fullColor)   // keep brand colors
```

## 3.4 A fully adaptive widget view

```swift
struct AdaptiveWidgetView: View {
    let entry: MyEntry
    @Environment(\.widgetRenderingMode) private var renderingMode
    @Environment(\.showsWidgetContainerBackground) private var hasBackground

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Image("cover")
                    .resizable().scaledToFit()
                    .frame(width: 44, height: 44)
                    .widgetAccentedRenderingMode(.accentedDesaturated)
                VStack(alignment: .leading) {
                    Text(entry.title).font(.headline).widgetAccentable()
                    Text(entry.subtitle).font(.caption).foregroundStyle(.secondary)
                }
            }
            Spacer()
            Text(entry.date, style: .time)
                .font(.caption2)
                .opacity(renderingMode == .vibrant ? 0.9 : 0.6)
        }
        .padding()
        .containerBackground(for: .widget) {
            switch renderingMode {
            case .fullColor:
                LinearGradient(colors: [.blue, .purple],
                               startPoint: .top, endPoint: .bottom)
            case .accented, .vibrant: Color.clear
            @unknown default: Color.clear
            }
        }
    }
}
```

> **Tips for great tinting.** Prefer **SF Symbols** and **vector assets** (PDF with "Preserve Vector Data"). Mark your headline `.widgetAccentable()`. In `.vibrant` never rely on hue to convey meaning — use shape and weight.

---

# 4. Live Activities (ActivityKit)

## 4.1 Framework and configuration

**ActivityKit** ships in iOS 16.1 (October 2022). A Live Activity surfaces ongoing state in up to four places: **Lock Screen banner**, **Dynamic Island** (iPhone 14 Pro and later), **StandBy**, and, as of iOS 18/26, **watchOS Smart Stack**, **CarPlay Dashboard**, and the **macOS menu bar** via iPhone Mirroring.

**Info.plist keys:**
- `NSSupportsLiveActivities = YES` in the main app.
- `NSSupportsLiveActivitiesFrequentUpdates = YES` (optional) to request a larger update budget.
- Push Notifications capability, only for remote push/push-to-start/channel pushes.

## 4.2 Core types

`ActivityAttributes` holds static data set at start; its nested `ContentState` holds dynamic values updated over the activity's lifetime. Both must be `Codable & Hashable`.

```swift
import ActivityKit

struct DeliveryAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var status: DeliveryStatus
        var estimatedDeliveryTime: Date
        var driverName: String
        var progress: Double           // 0.0 … 1.0
    }
    let orderNumber: String
    let restaurantName: String
    let deliveryAddress: String
}

enum DeliveryStatus: String, Codable, Hashable {
    case confirmed, preparing, outForDelivery, delivered
}
```

`ActivityContent<State>` wraps the state with a `staleDate` and `relevanceScore`:

```swift
ActivityContent(state: state,
                staleDate: .now.addingTimeInterval(15 * 60),
                relevanceScore: 80)
```

- **`staleDate`** — when reached, the system visually redacts the activity as stale. It does **not** auto-end.
- **`relevanceScore`** — when this app has multiple Live Activities active, the highest score wins the compact/expanded slot; others fall to `.minimal` in the Dynamic Island.

## 4.3 Lifecycle

### Start

```swift
guard ActivityAuthorizationInfo().areActivitiesEnabled else { return }

let content = ActivityContent(state: initialState, staleDate: nil, relevanceScore: 50)
let activity = try Activity<DeliveryAttributes>.request(
    attributes: attrs,
    content: content,
    pushType: .token                 // .token, .channel(id), or nil
)
```

iOS 16.x requires foreground. iOS 17.2+ supports **push-to-start** (activity begins without the app running — section 4.5).

**[iOS 26]** A new overload `request(attributes:content:pushType:style:alertConfiguration:start:)` allows **scheduling a Live Activity for a future date** (e.g. a flight's boarding time, a game's start). Previously limited to Apple Sports; iOS 26 opens it to third parties.

### Update

```swift
let alert = AlertConfiguration(title: "Driver arrived",
                               body: "Come to the door",
                               sound: .default)
await activity.update(
    ActivityContent(state: newState, staleDate: nil),
    alertConfiguration: alert
)
```

Alerts produce a banner + haptic on iPhone without Dynamic Island, a brief Dynamic Island expansion on iPhone Pro, and a banner on Apple Watch.

### End

```swift
await activity.end(
    ActivityContent(state: finalState, staleDate: nil),
    dismissalPolicy: .default        // .default, .immediate, .after(Date)
)
```

| Dismissal policy | Lock Screen behavior | Dynamic Island |
|---|---|---|
| `.default` | Persists up to **4 hours** after end | Removed immediately |
| `.immediate` | Removed instantly | Removed instantly |
| `.after(Date)` | Removed at that date (≤ 4h out) | Removed immediately |

### The 8-hour / 12-hour rule

Apple's DTS (Dev Forums thread 797676) confirms:

- A Live Activity can run up to **8 hours from its last update** before the system auto-ends it.
- After ending (by you or the system), the Lock Screen keeps showing it up to **4 additional hours** under `.default` dismissal.
- Net: **~8 hours on Dynamic Island, ~12 hours on Lock Screen.**

> Always set a `staleDate` so the user gets a visual cue before your 8-hour window elapses. — WWDC 2023 *Update Live Activities with push notifications* (10185).

## 4.4 Observing state

```swift
Task {
    for await state in activity.activityStateUpdates {
        // .active, .ended, .dismissed, .stale
    }
}
Task {
    for await content in activity.contentUpdates {
        // ActivityContent<DeliveryAttributes.ContentState>
    }
}
```

## 4.5 Push notifications

### Per-activity update token

```swift
let activity = try Activity.request(attributes: attrs,
                                    content: content,
                                    pushType: .token)
Task {
    for await data in activity.pushTokenUpdates {
        let hex = data.map { String(format: "%02x", $0) }.joined()
        await API.uploadUpdateToken(hex, activityID: activity.id)
    }
}
```

### APNs payload

```json
{
  "aps": {
    "timestamp": 1735689600,
    "event": "update",
    "content-state": { "status": "outForDelivery", "progress": 0.8 },
    "stale-date": 1735693200,
    "relevance-score": 75,
    "alert": { "title": "Driver nearby", "body": "Please head outside", "sound": "default" }
  }
}
```

Headers: `apns-push-type: liveactivity`, `apns-topic: <bundleID>.push-type.liveactivity`. Priority **5** (background) or **10** (alerting). Payload ≤ **4 KB**.

### Push-to-start (iOS 17.2+)

```swift
if #available(iOS 17.2, *) {
    Task {
        for await data in Activity<DeliveryAttributes>.pushToStartTokenUpdates {
            await API.register(pushToStartToken: data)
        }
    }
}
```

The server sends an APNs payload with `"event": "start"` and embedded attributes + content-state.

### Broadcast channel (iOS 18+)

WWDC 2024 *Broadcast updates to your Live Activities*. One channel serves thousands of devices; great for live sports, elections, concerts.

```swift
let activity = try Activity.request(attributes: gameAttrs,
                                    content: .init(state: initial, staleDate: nil),
                                    pushType: .channel(channelId))
```

## 4.6 Update-frequency limits

| Mechanism | Practical limit |
|---|---|
| Local updates | No hard cap; background runtime budget applies. Exceeding delays future updates until the budget replenishes. |
| Push updates | ~1/second sustained with burst allowance. Priority 5 has higher ceiling than priority 10. APNs throttles abusive clients. |
| With `NSSupportsLiveActivitiesFrequentUpdates` | Larger budget; only request if you genuinely have a high-cadence use case. |
| Total activity lifetime | 8 hours from last update before auto-end. |
| Concurrent Live Activities per app | ~5. |

> During testing, enable **Settings → Developer → WidgetKit Developer Mode** to bypass budgets.

---

# 5. Dynamic Island

Available on **iPhone 14 Pro and later Pro models** (extended to all iPhone 15+ Pro models; the cutout hardware is Pro-only through iPhone 17 Pro as of this writing).

## 5.1 Regions and states

| State | When shown | Approx. footprint |
|---|---|---|
| `compactLeading` | One active Live Activity | ~44×36 pt, left of cutout |
| `compactTrailing` | Same | ~44×36 pt, right of cutout |
| `minimal` | ≥ 2 activities competing | 24–36 pt circle |
| `expanded` (leading / trailing / center / bottom) | Long-press or alerting update | ~full width, max ~160 pt tall |

> Apple has not published exact pixel sizes for the Dynamic Island. Design to **content**, not to fixed frames. Use `.dynamicIsland(verticalPlacement: .belowIfTooWide)` to let a wide region wrap beneath the TrueDepth cutout.

## 5.2 Full example — all regions

```swift
struct DeliveryLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: DeliveryAttributes.self) { context in
            // ===== LOCK SCREEN =====
            LockScreenDeliveryView(context: context)
                .activityBackgroundTint(Color.black.opacity(0.85))
                .activitySystemActionForegroundColor(.white)
        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    Label(context.attributes.restaurantName,
                          systemImage: "bag.fill")
                        .font(.caption2)
                }
                DynamicIslandExpandedRegion(.trailing) {
                    Label {
                        Text(timerInterval: .now ... context.state.estimatedDeliveryTime,
                             countsDown: true)
                    } icon: { Image(systemName: "clock") }
                    .monospacedDigit()
                }
                DynamicIslandExpandedRegion(.center) {
                    Text(context.state.status.rawValue.capitalized)
                        .font(.headline)
                }
                DynamicIslandExpandedRegion(.bottom) {
                    ProgressView(value: context.state.progress).tint(.orange)
                    HStack {
                        Button(intent: PauseOrderIntent(
                            orderID: context.attributes.orderNumber)) {
                            Label("Pause", systemImage: "pause.fill")
                        }
                        .buttonStyle(.bordered).tint(.orange)
                    }
                }
            } compactLeading: {
                Image(systemName: "bag.fill").foregroundStyle(.orange)
            } compactTrailing: {
                Text(timerInterval: .now ... context.state.estimatedDeliveryTime,
                     countsDown: true)
                    .monospacedDigit().frame(maxWidth: 50)
            } minimal: {
                Image(systemName: "bag.fill").foregroundStyle(.orange)
            }
            .widgetURL(URL(string: "myapp://order/\(context.attributes.orderNumber)"))
            .keylineTint(.orange)
        }
        .supplementalActivityFamilies([.small])   // [iOS 18+] Watch / CarPlay
    }
}
```

## 5.3 Useful modifiers

| Modifier | Purpose |
|---|---|
| `.keylineTint(_:)` | Accent the Dynamic Island border |
| `.activityBackgroundTint(_:)` | Tint the Lock Screen background |
| `.activitySystemActionForegroundColor(_:)` | Color of system-supplied "Open" text |
| `.contentMargins(_:for:)` | Per-state padding (`.minimal`, `.compactLeading`, `.compactTrailing`, `.expanded`) |
| `.dynamicIsland(verticalPlacement:)` | `.belowIfTooWide` wraps below the cutout |
| `.widgetURL(_:)` | Deep link for taps on Lock Screen, compact, minimal |
| `.supplementalActivityFamilies([.small])` | Opt into Watch Smart Stack / CarPlay small layout |

> **Animations.** `withAnimation { }` is ignored by ActivityKit. Use `.contentTransition(.numericText())`, `.transition(.opacity)`, and `.monospacedDigit()` for clean counter changes. Transitions between states (compact ↔ expanded ↔ minimal) are system-provided cross-fades.

## 5.4 Dynamic Island anti-patterns

| 🚫 | Do instead |
|---|---|
| Primary navigation via Dynamic Island | Use it for glanceable status; deep link to the app for interaction |
| Interactive controls in `minimal` or `compact` | Interactive buttons belong in **expanded** region only |
| Relying on color hue alone | Use shape + symbol; don't assume color fidelity |
| Unbounded activity without `staleDate` | Content looks fresh until it abruptly vanishes at 8h |

---

# 6. StandBy mode (iOS 17+)

## 6.1 What StandBy is

StandBy activates when the iPhone is **charging + landscape + stationary**. It shows three full-screen pages: widgets, photos, clock. iPhone 14 Pro and later keep StandBy visible continuously via Always-On display.

- The **widgets page** shows **two independent widget stacks side-by-side**.
- Only `.systemSmall` is used in StandBy. If your widget supports `systemSmall`, it is automatically available in the StandBy gallery.
- Stacks participate in **Smart Rotate** driven by `TimelineEntry.relevance`.

## 6.2 The container background contract

`.containerBackground(for: .widget)` is mandatory (iOS 17+). In StandBy the system strips the background and scales your content larger. If your widget *is* the whole image (photo/map), set `.containerBackgroundRemovable(false)`.

## 6.3 Night Mode

Below a certain ambient-light threshold StandBy enters Night Mode: red-tinted, monochrome, **vibrant rendering**. Detect with:

```swift
@Environment(\.widgetRenderingMode) var renderingMode   // == .vibrant
@Environment(\.isLuminanceReduced) var dim               // true at night / AOD
@Environment(\.showsWidgetContainerBackground) var showsBackground
```

> There is **no `isStandBy` environment value.** Infer StandBy by combining `showsWidgetContainerBackground == false` with `widgetFamily == .systemSmall` on iOS 17+.

## 6.4 Adaptive StandBy widget

```swift
struct CaffeineStandByView: View {
    @Environment(\.widgetRenderingMode) private var renderingMode
    @Environment(\.showsWidgetContainerBackground) private var hasBackground
    @Environment(\.isLuminanceReduced) private var dim
    let entry: CaffeineEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("Caffeine").font(.caption).widgetAccentable()
            Text(entry.total.formatted())
                .font(hasBackground ? .title : .largeTitle)
                .bold()
                .contentTransition(.numericText(value: entry.total.value))
            if hasBackground {
                Text("Last: \(entry.lastDrink.name)")
                    .font(.caption2).foregroundStyle(.secondary)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        .padding(hasBackground ? 0 : 4)
        .containerBackground(for: .widget) {
            LinearGradient(colors: [.brown, .black],
                           startPoint: .top, endPoint: .bottom)
        }
    }
}
```

## 6.5 Smart Rotate via relevance

```swift
struct CaffeineEntry: TimelineEntry {
    let date: Date
    let total: Measurement<UnitMass>
    let lastDrink: Drink
    var relevance: TimelineEntryRelevance? {
        TimelineEntryRelevance(score: lastDrink.isRecent ? 90 : 20)
    }
}
```

## 6.6 Migration checklist

1. Add `.containerBackground(for: .widget) { … }` to every widget view.
2. Remove any outer `ZStack { Color … }` backgrounds.
3. Respect `\.widgetContentMargins` — don't cancel with negative padding.
4. Test `.vibrant` rendering (iPad Lock Screen is a proxy for StandBy Night).
5. Provide `relevance` on timeline entries.
6. Only set `.containerBackgroundRemovable(false)` if the widget has no distinct foreground.

---

# 7. Control Center widgets (iOS 18+)

## 7.1 The framework

Types ship inside WidgetKit (the `ControlWidget` protocol is declared in SwiftUI). Minimum OS: **iOS 18 / iPadOS 18**. Extended to **macOS 26** (Control Center + menu bar) and **watchOS 26** (Control Center, Smart Stack, Action button on Ultra) — WWDC 2025, *What's new in widgets* (278).

## 7.2 Placements and sizes

| Placement | Sizes | Introduced |
|---|---|---|
| Control Center | Small (1×1), Medium (2×1), Large (2×2) | iOS 18 |
| Lock Screen (bottom slots) | Small (symbol only) | iOS 18 |
| Action Button (iPhone 15 Pro+, iPhone 16 line) | Symbol + action hint | iOS 18 |
| macOS Tahoe Control Center / menu bar | Small/Medium/Large | **iOS 26 / macOS 26** |
| watchOS Control Center / Smart Stack / Action button | Compact / Smart Stack row | **watchOS 26** |

You provide **symbol**, **title**, **tint**, **value/state**. The system renders the shell.

## 7.3 The two control templates

### `ControlWidgetButton` — stateless

```swift
struct OpenComposeIntent: AppIntent {
    static let title: LocalizedStringResource = "Compose"
    static var openAppWhenRun: Bool = true
    func perform() async throws -> some IntentResult & OpensIntent {
        .result(opensIntent: OpenURLIntent(URL(string: "myapp://compose")!))
    }
}

@available(iOSApplicationExtension 18.0, *)
struct ComposeControl: ControlWidget {
    var body: some ControlWidgetConfiguration {
        StaticControlConfiguration(kind: "com.myapp.control.compose") {
            ControlWidgetButton(action: OpenComposeIntent()) {
                Label("Compose", systemImage: "square.and.pencil")
            }
        }
        .displayName("Compose")
        .description("Start a new note.")
    }
}
```

### `ControlWidgetToggle` — stateful

Toggles bind to a `SetValueIntent` (system passes a `Bool` to `value`):

```swift
struct ToggleTimerIntent: SetValueIntent {
    static let title: LocalizedStringResource = "Productivity Timer"
    @Parameter(title: "Running") var value: Bool
    func perform() async throws -> some IntentResult {
        TimerManager.shared.setRunning(value)
        return .result()
    }
}

@available(iOSApplicationExtension 18.0, *)
struct TimerToggle: ControlWidget {
    var body: some ControlWidgetConfiguration {
        StaticControlConfiguration(kind: "com.myapp.control.timer") {
            ControlWidgetToggle("Work Timer",
                                isOn: TimerManager.shared.isRunning,
                                action: ToggleTimerIntent()) { isOn in
                Label(isOn ? "Running" : "Stopped",
                      systemImage: isOn ? "hourglass" : "hourglass.bottomhalf.filled")
            }
            .tint(.purple)
        }
    }
}
```

## 7.4 Dynamic values

Use a `ControlValueProvider` (or `AppIntentControlValueProvider` for configurable controls) to fetch the current state asynchronously:

```swift
struct TimerValueProvider: ControlValueProvider {
    let previewValue: Bool = false
    func currentValue() async throws -> Bool {
        try await TimerManager.shared.fetchRunningState()
    }
}

@available(iOSApplicationExtension 18.0, *)
struct TimerToggleAsync: ControlWidget {
    var body: some ControlWidgetConfiguration {
        StaticControlConfiguration(kind: "com.myapp.control.timer.async",
                                   provider: TimerValueProvider()) { isRunning in
            ControlWidgetToggle("Work Timer",
                                isOn: isRunning,
                                action: ToggleTimerIntent()) { isOn in
                Label(isOn ? "Running" : "Stopped", systemImage: "hourglass")
            }
        }
    }
}
```

## 7.5 Configurable controls

Use `AppIntentControlConfiguration` with a `ControlConfigurationIntent`:

```swift
struct SelectTimerIntent: ControlConfigurationIntent {
    static let title: LocalizedStringResource = "Select Timer"
    @Parameter(title: "Timer") var timer: ProductivityTimer
}

struct TimerState { let timer: ProductivityTimer; let isRunning: Bool }

struct ConfigurableTimerValueProvider: AppIntentControlValueProvider {
    func currentValue(configuration: SelectTimerIntent) async throws -> TimerState {
        let running = try await TimerManager.shared.running(for: configuration.timer)
        return TimerState(timer: configuration.timer, isRunning: running)
    }
    func previewValue(configuration: SelectTimerIntent) -> TimerState {
        TimerState(timer: configuration.timer, isRunning: false)
    }
}
```

## 7.6 Reloading controls

Three triggers: (1) the control's intent returns, (2) the app calls `ControlCenter.shared.reloadControls(ofKind:)` / `reloadAllControls()`, (3) a **push** via a `ControlPushHandler`.

## 7.7 Refinement modifiers

| Modifier | Effect |
|---|---|
| `.displayName("…")` | Gallery name |
| `.description("…")` | Configuration-time description |
| `.tint(.purple)` | Active color |
| `.controlWidgetActionHint("Start")` | Action Button verb ("Hold to Start") |
| `.controlWidgetStatus("Updated")` | Momentary status after action |
| `.promptsForUserConfiguration()` | Auto-prompt on add |

## 7.8 Control anti-patterns

> **Controls are single-purpose.** From the iOS 18 HIG *Controls* chapter:

| 🚫 | Why |
|---|---|
| Destructive actions (delete, reset, purchase) | No confirmation dialog on Lock Screen / Action Button |
| Sensitive operations | Triggerable without unlocking |
| Actions that need multi-step input | Controls are one-tap |
| Overloaded title (using your app name) | Title should describe the action |

**Gotchas:**
- Intent types must be in **both** app target and widget extension target.
- `openAppWhenRun = true` on `ControlConfigurationIntent` was unreliable until iOS 18.1 (DevForums 759794). Prefer returning `OpenURLIntent` from an `AppIntent` that conforms to `OpensIntent`.

---

# 8. Lock Screen widgets

## 8.1 Constraints

Introduced in WWDC 2022 *Complications and widgets: Reloaded* (10050). Same WidgetKit API; you add the accessory families to `.supportedFamilies`.

- Rendered in **`.vibrant`** mode on iOS Lock Screen and **`.accented`** on watchOS complications.
- Colors are flattened; only luminance and opacity survive.
- No custom backgrounds — use `AccessoryWidgetBackground()` for the standard pill/circle backdrop.
- `accessoryInline` is **text-only**: system font, one line, no color, no images.
- `accessoryCircular` is typically < 76 pt diameter — ideal for `Gauge`.
- `accessoryRectangular` fits 2–3 lines or a tiny chart.

## 8.2 Lock Screen example across all three accessory families

```swift
struct StepsLockScreenWidget: Widget {
    let kind = "StepsLockScreen"
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: StepsProvider()) { entry in
            StepsLockView(entry: entry)
                .containerBackground(for: .widget) { AccessoryWidgetBackground() }
        }
        .configurationDisplayName("Steps")
        .description("Your step progress.")
        .supportedFamilies([.accessoryCircular, .accessoryRectangular, .accessoryInline])
    }
}

struct StepsLockView: View {
    let entry: StepsEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        switch family {
        case .accessoryCircular:
            Gauge(value: Double(entry.steps), in: 0...Double(entry.goal)) {
                Image(systemName: "figure.walk")
            } currentValueLabel: {
                Text("\(entry.steps * 100 / entry.goal)%")
            }
            .gaugeStyle(.accessoryCircular)

        case .accessoryRectangular:
            VStack(alignment: .leading) {
                Label("Steps", systemImage: "figure.walk").widgetAccentable()
                Text("\(entry.steps) / \(entry.goal)")
                ProgressView(value: Double(entry.steps), total: Double(entry.goal))
            }

        case .accessoryInline:
            Text("\(entry.steps) steps today")

        default: EmptyView()
        }
    }
}
```

## 8.3 Design guidelines

> **Convey meaning through shape, layout, and iconography — not color.** Strokes and masks survive flattening; hue does not. — HIG *Complications*.

- Use **SF Symbols** and **system fonts** wherever possible.
- Mark primary elements `.widgetAccentable()`.
- Prefer `Gauge` with `.gaugeStyle(.accessoryCircular)` for progress.
- Don't repeat what the Lock Screen already shows (clock, date, weather).
- Mark private fields `.privacySensitive()`.

**[iOS 26]** Lock Screen adds a resizable adaptive clock, spatial-scene wallpapers, Glass-styled clock colors, and widgets can now be placed at the **bottom** of the Lock Screen in addition to the top complication row. No API changes required — verify legibility against the new variety of tints and the larger auto-adapting clock.

---

# 9. Data and updates

## 9.1 `TimelineEntry`

```swift
public protocol TimelineEntry {
    var date: Date { get }
    var relevance: TimelineEntryRelevance? { get }   // default nil
}
```

## 9.2 `TimelineEntryRelevance`

```swift
public struct TimelineEntryRelevance: Hashable {
    public var score: Float
    public var duration: TimeInterval
    public init(score: Float, duration: TimeInterval = 0)
}
```

Higher `score` → higher Smart Stack / StandBy Smart Rotate priority. `duration == 0` means the score is valid until the next entry with relevance. Apps can also donate `INRelevantShortcut` to proactively promote widgets (WWDC 2021 *Add intelligence to your widgets*, 10049).

## 9.3 Reload policies

```swift
Timeline(entries: entries, policy: .atEnd)
Timeline(entries: entries, policy: .after(date))
Timeline(entries: entries, policy: .never)
```

- `.atEnd` — request a new timeline after the last entry.
- `.after(date:)` — request on or after that date.
- `.never` — only reload via `WidgetCenter.shared.reloadTimelines(ofKind:)`.

> All reload timing is **best-effort**. Budgets and activity-level heuristics may delay reloads by 5+ minutes from the requested time. Don't design UI assuming exact refresh.

## 9.4 Refresh budgets

Apple does not publish exact numbers. Practical community and Apple-documentation guidance:

- **~40–70 reloads per widget per day** (some sources cite ≈72 as an upper bound).
- Budget is **dynamically allocated** — visible, engaged widgets get more.
- A free reload typically occurs at midnight.
- **Xcode debug builds bypass the budget** — production behavior will be stricter.
- Plan timelines for ~24 hours at a time; don't exceed ~10 MB per timeline.

## 9.5 Forcing a reload

```swift
import WidgetKit

WidgetCenter.shared.reloadTimelines(ofKind: "WeatherWidget")
WidgetCenter.shared.reloadAllTimelines()

WidgetCenter.shared.getCurrentConfigurations { result in
    if case .success(let widgets) = result {
        for info in widgets { print(info.kind, info.family) }
    }
}
```

## 9.6 Push updates **[iOS 26]**

New `WidgetPushHandler` + `.pushHandler(_:)` modifier:

```swift
struct CaffeineTrackerPushHandler: WidgetPushHandler {
    func pushTokenDidChange(_ pushInfo: WidgetPushInfo,
                            widgets: [WidgetInfo]) {
        Task { await API.register(token: pushInfo.token) }
    }
}

StaticConfiguration(kind: "Caffeine", provider: Provider()) { entry in
    WidgetView(entry: entry)
}
.pushHandler(CaffeineTrackerPushHandler.self)
```

APNs request headers `apns-push-type: widgets`, `apns-topic: <bundleID>.push-type.widgets`. Payload `{ "aps": { "content-changed": true } }`. Requires Push Notifications entitlement on the widget extension.

## 9.7 Best practices

- **Batch entries.** Pre-compute hours or a day of entries in one timeline.
- Use `Text(date, style: .timer)` / `.relative` / `.date` to avoid entries that only update a clock.
- Apply `.privacySensitive()` to private data.
- Share data via App Group `UserDefaults(suiteName:)` or an App Group container.
- Use APNs + `.never` for real-time content.
- Call `WidgetCenter.shared.reloadTimelines(ofKind:)` from `perform()` after user-driven state changes.

---

# 10. Interactive widgets (iOS 17+)

## 10.1 The primitives

When both `SwiftUI` and `AppIntents` are imported:

```swift
Button(intent: AppIntent)                 { label }
Toggle(_ title: "…", isOn: Bool, intent: AppIntent)
Toggle(isOn: Bool, intent: AppIntent)     { label }
```

**Only these two controls are interactive in widgets.** No `TextField`, `Slider`, `Stepper`, `onTapGesture`, `NavigationLink`, or `ScrollView` scrolling.

## 10.2 Execution model (WWDC 2023 *Bring widgets to life*, 10028)

1. User taps → system launches the widget extension process.
2. `intent.perform()` is invoked with archived `@Parameter` values.
3. When `perform()` returns, the system **automatically reloads the widget's timeline**.
4. Toggles render both states at archive time, enabling **optimistic UI updates**.
5. Interactive reloads are **guaranteed** — they are not gated by the normal budget.

> **The 5-second budget.** `perform()` must complete quickly — the practical empirical cap is ~5 seconds. Apple does not publish an exact number, but exceeding it causes the process to be killed before your UI updates. Persist data, return, and let a background task handle anything longer.

## 10.3 Button example — mark complete

```swift
struct CompleteTaskIntent: AppIntent {
    static let title: LocalizedStringResource = "Complete Task"
    @Parameter(title: "Task ID") var taskID: String
    init() {}
    init(taskID: String) { self.taskID = taskID }
    func perform() async throws -> some IntentResult {
        await TaskStore.shared.complete(id: taskID)
        return .result()
    }
}

struct TaskRowView: View {
    let task: TaskItem
    var body: some View {
        HStack {
            Button(intent: CompleteTaskIntent(taskID: task.id)) {
                Image(systemName: task.isDone ? "checkmark.circle.fill" : "circle")
            }
            .buttonStyle(.plain)
            Text(task.title)
                .strikethrough(task.isDone)
                .invalidatableContent()           // iOS 17+
        }
    }
}
```

## 10.4 Toggle example — favorite

```swift
struct ToggleFavoriteIntent: AppIntent, SetValueIntent {
    static let title: LocalizedStringResource = "Toggle Favorite"
    @Parameter(title: "Item ID") var itemID: String
    @Parameter(title: "Favorite") var value: Bool
    init() {}
    init(itemID: String, value: Bool) { self.itemID = itemID; self.value = value }
    func perform() async throws -> some IntentResult {
        await LibraryStore.shared.setFavorite(value, id: itemID)
        return .result()
    }
}

struct FavoriteRow: View {
    let item: Item
    var body: some View {
        Toggle(isOn: item.isFavorite,
               intent: ToggleFavoriteIntent(itemID: item.id, value: !item.isFavorite)) {
            Label("Favorite", systemImage: item.isFavorite ? "heart.fill" : "heart")
        }
        .toggleStyle(.button)
    }
}
```

## 10.5 `.invalidatableContent()`

Dims the view with a system shimmer while an intent is in flight. Especially useful for iPhone widgets running on Mac where latency is visible.

```swift
Text(totalCaffeine.formatted())
    .contentTransition(.numericText(value: totalCaffeine.value))
    .invalidatableContent()
```

## 10.6 Interactive Live Activities

The same `Button(intent:)` / `Toggle(isOn:intent:)` work in Live Activity Lock Screen views and the Dynamic Island **expanded** region (not compact/minimal). Use `LiveActivityIntent` instead of a plain `AppIntent` when the intent will update activity state:

```swift
struct PauseOrderIntent: LiveActivityIntent {
    static let title: LocalizedStringResource = "Pause Order"
    @Parameter(title: "Order ID") var orderID: String
    init() {}
    init(orderID: String) { self.orderID = orderID }
    func perform() async throws -> some IntentResult {
        await OrderStore.shared.pause(orderID)
        return .result()
    }
}
```

> **Critical gotcha.** `LiveActivityIntent.perform()` runs in the **main app's process** — essential because `Activity.update(...)` can only be called there. A regular `AppIntent` runs in the widget extension. Declare intent types in **both** targets by putting them in a shared Swift file compiled into both.

## 10.7 What works vs what doesn't

| ✅ Works | 🚫 Doesn't work |
|---|---|
| `Button(intent:)` | Any `Gesture` or `onTapGesture` |
| `Toggle(isOn:intent:)` | `TextField`, keyboard |
| `Link(destination:)` (navigation via URL) | `NavigationLink` / pushing views |
| `widgetURL(_:)` on root | Scrolling or `List` selection |
| Atomic state changes (≤ ~5 s) | Long-running async work |
| Animations between timeline entries | `@State` mutations in the widget view |
| `.invalidatableContent()` | Drag, swipe, or complex gestures |

## 10.8 Interactive anti-patterns

```swift
// 🚫 Navigation from a widget — use Link or widgetURL instead.
Button(intent: OpenTaskIntent(id: task.id)) { Text(task.title) }

// 🚫 Long-running work in perform() — will exceed budget.
func perform() async throws -> some IntentResult {
    try await uploadHugeFile()
    try await heavyImageProcessing()
    return .result()
}
```

Also: **rapid repeated taps** can fall through and launch the app instead of running the intent (DevForums 731373). Debounce visually with `.invalidatableContent()` and test under finger-mashing conditions.

---

# 11. iOS 26 new features and surfaces

## 11.1 Liquid Glass rendering

The iOS 26 Home Screen gains a **"clear glass" presentation** and **tint-color presentation** for widgets, implemented by rendering in `.accented` mode with the background removed and replaced by a system-generated glass material. Adopt via:

1. Audit every `Image` — most need `.widgetAccentedRenderingMode(.accentedDesaturated)`. Reserve `.fullColor` for media (album art, book covers).
2. Provide meaningful content in `.accented` — test with `@Environment(\.widgetRenderingMode)` branches.
3. Re-verify `containerBackground` produces legible output when stripped.

Recompile with Xcode 26 SDK to inherit Liquid Glass chrome automatically on toolbars, tab bars, and controls.

## 11.2 Live Activities reach Mac, CarPlay, and iPad

| Destination | What to do |
|---|---|
| **macOS Tahoe menu bar** | Zero code. Appears automatically via iPhone Mirroring for paired iPhones on iOS 18+. |
| **CarPlay Dashboard** | Add `.supplementalActivityFamilies([.small])`; branch on `@Environment(\.activityFamily)` for layout |
| **iPadOS 26** | Live Activities power the new Background Tasks / Continued Processing feature (exports, renders). |
| **Scheduled start** | New `request(...start: Date)` overload — schedule activities for future events. |

## 11.3 visionOS 26 widgets

- iPhone/iPad widget binaries auto-port to visionOS 26 as **spatial objects** pinned to surfaces.
- New `WidgetFamily.systemExtraLargePortrait`.
- New config modifiers `supportedMountingStyles([.elevated, .recessed])` and `widgetTexture(.glass)` / `.paper`.
- New `@Environment(\.levelOfDetail)` — `.default` vs `.simplified` based on the user's distance from the widget. Hide interactive controls at distance.

## 11.4 CarPlay widgets

- Widgets appear on the CarPlay dashboard (all CarPlay cars, not just CarPlay Ultra).
- Rendered in **StandBy style**: `systemSmall`, `.fullColor`, background removed.
- Touch where the hardware supports it; otherwise read-only.

## 11.5 Relevance widgets (watchOS 26)

A new configuration type for widgets that surface in the Smart Stack only when contextually relevant (routines, location, time windows). Multiple instances can surface simultaneously.

```swift
struct HappyHourRelevanceWidget: Widget {
    var body: some WidgetConfiguration {
        RelevanceConfiguration(kind: "HappyHour", provider: Provider()) { entry in
            WidgetView(entry: entry)
        }
    }
}

struct Provider: RelevanceEntriesProvider {
    func placeholder(context: Context) -> Entry { Entry() }
    func relevance() async -> WidgetRelevance<Configuration> {
        let configs = await fetchConfigs()
        let attrs = configs.map {
            WidgetRelevanceAttribute(
                configuration: $0,
                context: .date(interval: $0.interval, kind: .default))
        }
        return WidgetRelevance(attrs)
    }
    func entry(configuration: Configuration,
               context: RelevanceEntriesProviderContext) async throws -> Entry {
        Entry(shop: configuration.shop, timeRange: configuration.timeRange)
    }
}
```

## 11.6 Widget push updates

See §9.6 — `WidgetPushHandler` + APNs `widgets` push type. Works across all WidgetKit platforms.

## 11.7 Controls reach macOS and watchOS

`ControlWidget` types built for iOS 18 automatically appear on macOS Tahoe (Control Center + menu bar) and watchOS 26 (Control Center, Smart Stack, Apple Watch Ultra Action button). Verify the backing `AppIntent` runs correctly on those platforms.

## 11.8 What did not change in iOS 26

- **Dynamic Island API surface** is unchanged — only the visual material (Liquid Glass) was updated.
- **StandBy** received no new public APIs beyond the system-wide redesign. Existing iOS 17 patterns (`.containerBackground`, `.vibrant` + `isLuminanceReduced` for Night Mode) still apply.
- No third-party Control placements in Camera or Focus modes — Camera capture continues to use the separate **LockedCameraCapture** mechanism (WWDC 2024, session 10204).
- No documented Apple Intelligence integration in ActivityKit as of iOS 26.0.

---

# 12. WWDC session reference

| Year | # | Title | Key topics |
|---|---|---|---|
| 2020 | 10028 | Meet WidgetKit | Providers, timelines, families |
| 2020 | 10033 | Build SwiftUI views for widgets | Widget-specific SwiftUI APIs |
| 2020 | 10034/35/36 | Widgets Code-along (3 parts) | End-to-end widget build |
| 2020 | 10194 | Add configuration and intelligence to your widgets | Intents, Smart Stack scoring |
| 2020 | 10103 | Design great widgets | HIG pillars |
| 2021 | 10048 | Principles of great widgets | Timeliness, customization |
| 2021 | 10049 | Add intelligence to your widgets | Relevance, Smart Rotate, `INRelevantShortcut` |
| 2022 | 10050 | Complications and widgets: Reloaded | Accessory families, Lock Screen, vibrant |
| 2022 | 10051 | Go further with Complications in WidgetKit | ClockKit→WidgetKit migration |
| 2023 | 10184 | Meet ActivityKit | Live Activities fundamentals |
| 2023 | 10185 | Update Live Activities with push notifications | APNs, relevance, staleDate |
| 2023 | 10194 | Design dynamic Live Activities | HIG for Dynamic Island/Lock Screen |
| 2023 | 10027 | Bring widgets to new places | StandBy, iPad Lock, Mac, `containerBackground` |
| 2023 | 10028 | Bring widgets to life | Interactive widgets, transitions |
| 2023 | 10029 | Build widgets for the Smart Stack on Apple Watch | watchOS 10 Smart Stack |
| 2023 | 10103 | Explore enhancements to App Intents | `AppIntentConfiguration`, `AppIntentTimelineProvider` |
| 2023 | 10309 | Design widgets for the Smart Stack on Apple Watch | Relevance signals for watch |
| 2024 | 10068 | Bring your Live Activity to Apple Watch | `supplementalActivityFamilies`, `activityFamily` |
| 2024 | 10098 | Design Live Activities for Apple Watch | Smart Stack UX |
| 2024 | 10069 | Broadcast updates to your Live Activities | Channel push |
| 2024 | 10157 | Extend your app's controls across the system | `ControlWidget`, placements |
| 2024 | 10205 | What's new in watchOS 11 | Smart Stack, interactive widgets, Live Activities |
| 2024 | 10210 | Bring your app's core features to users with App Intents | `ControlConfigurationIntent` |
| 2024 | 10204 | Build a great Lock Screen camera capture experience | `LockedCameraCapture` (separate from Controls) |
| 2025 | 278 | What's new in widgets | Liquid Glass, visionOS, CarPlay, push, Relevance |
| 2025 | 255 | Design widgets for visionOS | Mounting style, texture, level of detail |
| 2025 | 216 | Turbocharge your app for CarPlay | CarPlay widgets & Live Activities |
| 2025 | 334 | What's new in watchOS 26 | Relevance widgets, Smart Stack |
| 2025 | 219 | Meet Liquid Glass | Design language foundation |
| 2025 | 323 | Build a SwiftUI app with the new design | `glassEffect`, `GlassEffectContainer` |
| 2025 | 256 | What's new in SwiftUI | Widget/Live Activity SwiftUI deltas |
| 2025 | 202 | What's new in Wallet | Flight boarding pass Live Activities |

Apple doc companion: *Optimizing your widget for accented rendering mode and Liquid Glass* — `developer.apple.com/documentation/WidgetKit/optimizing-your-widget-for-accented-rendering-mode-and-liquid-glass`.

---

# 13. Cross-surface quick reference

## 13.1 Environment values cheat sheet

| Key | Type | Useful in |
|---|---|---|
| `\.widgetFamily` | `WidgetFamily` | All widgets |
| `\.widgetRenderingMode` | `.fullColor` / `.accented` / `.vibrant` | Branching layouts |
| `\.showsWidgetContainerBackground` | `Bool` | Detect StandBy / iPad Lock |
| `\.isLuminanceReduced` | `Bool` | StandBy Night Mode / AOD |
| `\.colorScheme` | `ColorScheme` | Light/dark |
| `\.widgetContentMargins` | `EdgeInsets` | Respect system padding |
| `\.levelOfDetail` **[iOS 26]** | `.default` / `.simplified` | visionOS spatial widgets |
| `\.activityFamily` **[iOS 18+]** | `.small` / `.medium` | Live Activity on Watch/CarPlay |

## 13.2 Minimum-adoption checklist per surface

| Surface | Minimum OS | Required adoption steps |
|---|---|---|
| Home Screen widget | iOS 14 | `AppIntentConfiguration` (iOS 17+), `.containerBackground`, `supportedFamilies` |
| Lock Screen widget | iOS 16 | Add accessory families, use SF Symbols, `.widgetAccentable()` on accents |
| StandBy | iOS 17 | `.containerBackground`, `relevance` on entries, test `.vibrant` |
| Tinted Home Screen | iOS 18 | Test `.accented`, add `.widgetAccentedRenderingMode(.accentedDesaturated)` on Image |
| Live Activity | iOS 16.1 | `ActivityAttributes`, `ActivityConfiguration`, `NSSupportsLiveActivities` Info.plist key |
| Dynamic Island | iOS 16.1 (iPhone Pro) | Provide compactLeading/Trailing, minimal, expanded regions |
| Interactive widget | iOS 17 | `Button(intent:)` / `Toggle(isOn:intent:)` + `AppIntent` in both targets |
| Control widget | iOS 18 | `ControlWidget`, `SetValueIntent` for toggles, `AppIntent` in both targets |
| CarPlay Live Activity | iOS 26 | `.supplementalActivityFamilies([.small])` |
| visionOS widget | iOS 26 / visionOS 26 | `supportedMountingStyles`, `widgetTexture`, `levelOfDetail` |
| Widget push | iOS 26 | `WidgetPushHandler`, `.pushHandler`, Push entitlement on extension |

---

# Conclusion

Apple's ambient and glanceable surfaces have converged on a single mental model: **WidgetKit is the content layer, App Intents is the action layer, and ActivityKit is the persistence layer.** Everything else — StandBy, Dynamic Island, Control Center, Lock Screen, CarPlay, the Mac menu bar, visionOS, watchOS Smart Stack — is a rendering destination that the system picks based on your declared families and the user's context. The single most important iOS 17 lesson remains `.containerBackground(for: .widget)`; the single most important iOS 26 lesson is that accented rendering is no longer optional — every image, every hue choice, and every background decision must be re-evaluated under `.accented` and `.vibrant` to survive Liquid Glass.

The anti-pattern that unifies every surface is the same: **these are not small apps.** They are projections of your app's most valuable moment, sized to fit where the user is already looking. A delivery countdown, a step total, a play/pause toggle, a one-tap control — each is a sentence, not a paragraph. When a surface feels cramped, the answer is almost never "show more"; it is "show less, but show it now."

Key shifts worth internalizing:

- **Interactivity is a feature, not the feature.** `Button(intent:)` and `Toggle(isOn:intent:)` are accelerators on top of a widget that must already be useful at a glance. The 5-second execution budget is a hard design constraint, not a polish item.
- **Live Activity time limits are architectural.** The 8-hour update window and 12-hour total Lock Screen visibility should shape what tasks you model — not be worked around.
- **Controls are the most dangerous surface** because they are triggerable without unlocking. Confirmation-requiring and destructive actions simply don't belong there.
- **Rendering modes are not a cosmetic concern.** `.accented` and `.vibrant` flatten hue. If your widget conveys state through color alone, it will fail on the Lock Screen and in iOS 18+ tinted Home Screens.

Build for the smallest surface first — `systemSmall` in `.vibrant` at low luminance in Night Mode — and everything larger and brighter will follow.