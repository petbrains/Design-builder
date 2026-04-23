---
name: haptics
description: iOS haptics reference (Taptic Engine, SwiftUI sensoryFeedback, UIFeedbackGenerator, Core Haptics)
platform: ios
---

# The complete iOS haptics reference for modern apps

Apple's haptic stack is a three-layer pyramid: **SwiftUI `sensoryFeedback`** (declarative, iOS 17+), **UIKit `UIFeedbackGenerator`** (imperative, iOS 10+), and **Core Haptics `CHHapticEngine`** (custom patterns, iOS 13+). Choosing correctly matters more than most developers realize — the Taptic Engine is a physical actuator the user *feels*, and misused haptics cause "haptic fatigue" so quickly that Apple's HIG explicitly warns against it. This reference consolidates every API, every semantic type, concrete examples from Apple's own apps, accessibility rules, and the anti-patterns you must avoid — targeted at iOS 17 through iOS 26 and cross-referenced across iPadOS, macOS, watchOS, and visionOS.

The single most useful insight before you write any haptic code: **the system already plays the right haptic for standard controls**. `UISwitch`, `UISlider`, `UIPickerView`, pull-to-refresh, the keyboard, scroll rubber-banding — all of these are handled. Your job is to extend that vocabulary *consistently* for the handful of moments that are genuinely yours to decorate.

---

## Decision tree: does this action deserve a haptic?

Use this to decide *whether* and *which*:

```
START — Did the USER explicitly initiate this action?
│
├─ NO  → ❌ DO NOT play a haptic (ambient/background events are not haptic events)
│
└─ YES → Is it a standard UIKit/SwiftUI control (UISwitch, UISlider, UIPickerView,
         UIDatePicker, scroll, keyboard, pull-to-refresh)?
         │
         ├─ YES → ❌ Let the system handle it. Do not add more.
         │
         └─ NO  → Is this a TRIVIAL interaction (ordinary button tap, tab switch,
                  list-row tap with no consequence)?
                  │
                  ├─ YES → ❌ Skip. Haptic fatigue kills signal value.
                  │
                  └─ NO  → What KIND of event is it?
                           │
                           ├─ Result of a task ─────────────┐
                           │   ├─ Succeeded         → .success
                           │   ├─ Warned            → .warning
                           │   └─ Failed / invalid  → .error
                           │
                           ├─ Physical/visual collision ────┐
                           │   ├─ Small element         → .impact(.light)
                           │   ├─ Standard snap         → .impact(.medium)
                           │   ├─ Heavy/big element     → .impact(.heavy)
                           │   ├─ Soft/cushioned feel   → .impact(.soft) or flexibility: .soft
                           │   └─ Hard/metallic feel    → .impact(.rigid) or flexibility: .rigid
                           │
                           ├─ Scrubbing/picking through discrete values → .selection
                           │
                           ├─ Crossing a significant value threshold ──┐
                           │   ├─ Upward  → .increase
                           │   └─ Downward → .decrease
                           │
                           ├─ Beginning/ending a continuous activity ──┐
                           │   ├─ Begin → .start
                           │   └─ End   → .stop
                           │
                           ├─ Drag snapped to an alignment guide → .alignment (macOS focus)
                           ├─ Moved between hierarchical/pressure levels → .levelChange
                           │
                           └─ Needs custom timing, texture, audio sync,
                              or real-time modulation  → Use Core Haptics (CHHapticEngine)
```

**Final gate before shipping**: Is there a matching **visual and/or audible** cue? If haptics are the *only* signal, rework the UI — many users disable haptics, rely on VoiceOver, or don't feel the device in-hand.

---

## Comparison table of all haptic types

| Type | SwiftUI API | UIKit API | Semantic meaning | Example use case | Physical feel |
|---|---|---|---|---|---|
| Success | `.success` | `UINotificationFeedbackGenerator` → `.success` | Task completed successfully | Apple Pay confirmed, file saved | Distinctive double-tap, high-low |
| Warning | `.warning` | `UINotificationFeedbackGenerator` → `.warning` | Caution; non-blocking issue | Approaching a limit, unusual input | Two taps with pause between |
| Error | `.error` | `UINotificationFeedbackGenerator` → `.error` | Failure / invalid action | Wrong password, rejected payment | Sharper triple-tap |
| Impact light | `.impact(weight: .light)` | `UIImpactFeedbackGenerator(style: .light)` | Small UI element touching | Chip snap, tooltip appearance | Small, quick tick |
| Impact medium | `.impact` (default) or `.impact(weight: .medium)` | `UIImpactFeedbackGenerator(style: .medium)` | Standard snap | Sheet hits detent, card locks | Solid click |
| Impact heavy | `.impact(weight: .heavy)` | `UIImpactFeedbackGenerator(style: .heavy)` | Substantial collision | Big modal landing, boundary hit | Firm thud |
| Impact soft | `.impact(flexibility: .soft)` | `UIImpactFeedbackGenerator(style: .soft)` (iOS 13+) | Cushioned / elastic collision | Soft dismissal bounce | Damped, muted |
| Impact rigid | `.impact(flexibility: .rigid)` | `UIImpactFeedbackGenerator(style: .rigid)` (iOS 13+) | Stiff / precise collision | Shutter click, hard latch | Crisp, snappy |
| Selection | `.selection` | `UISelectionFeedbackGenerator.selectionChanged()` | Value is changing through discrete values | Picker wheel, segmented control | Barely-perceptible tick per value |
| Increase | `.increase` | (bridges internally) | Value crossed upward past threshold | Volume step up, brightness past 50% | Rising-feel tick |
| Decrease | `.decrease` | (bridges internally) | Value crossed downward past threshold | Volume step down | Falling-feel tick |
| Start | `.start` | WatchKit `.start` / `CHHapticEngine` on iOS | Continuous activity began | Workout, recording, drag begin | Distinct onset pulse |
| Stop | `.stop` | WatchKit `.stop` / `CHHapticEngine` | Continuous activity ended | Workout ended, recording stopped | Distinct terminal pulse |
| Alignment | `.alignment` | `NSHapticFeedbackManager` `.alignment` / `UICanvasFeedbackGenerator.alignmentOccurred(at:)` | Dragged item snapped to a guide | Grid/guide snap on macOS, Pencil alignment on iPad | Subtle "lock" tick |
| Level change | `.levelChange` | `NSHapticFeedbackManager` `.levelChange` | Moved between hierarchical or pressure levels | Fast-forward speed step, Force Touch level | Two-stage click |
| Path complete | `.pathComplete` (iOS 17.5+) | `UICanvasFeedbackGenerator.pathCompleted(at:)` | Continuous gesture reached completion | Drawing stroke closes | Short confirming tap |

Impact **intensity** is a `Double` in `0.0…1.0` (default `1.0`). SwiftUI's `.impact(weight:)` maps to UIKit's `.light/.medium/.heavy`; `.impact(flexibility:)` maps to `.soft/.solid/.rigid` (`.solid` approximates default style).

---

## 1. SwiftUI sensoryFeedback (iOS 17+)

`sensoryFeedback` was introduced at **WWDC 2023 inside session 10148 "What's new in SwiftUI"**. It is a **declarative, trigger-driven** replacement for manually driving `UIFeedbackGenerator` from your SwiftUI views. SwiftUI handles generator lifecycle, `prepare()`, main-thread dispatch, and platform bridging (UIKit on iOS, WatchKit on watchOS, AppKit on macOS) for you. The broader *"sensory"* name reflects that audio can accompany haptics on certain platforms.

### The three overloads

All overloads require `T: Equatable` and are available iOS 17.0+, iPadOS 17.0+, macOS 14.0+, watchOS 10.0+, tvOS 17.0+, visionOS 1.0+.

```swift
// 1. Basic: fire this feedback whenever `trigger` changes
func sensoryFeedback<T: Equatable>(
    _ feedback: SensoryFeedback,
    trigger: T
) -> some View

// 2. Conditional: fire only when your closure returns true
func sensoryFeedback<T: Equatable>(
    _ feedback: SensoryFeedback,
    trigger: T,
    condition: @escaping (_ oldValue: T, _ newValue: T) -> Bool
) -> some View

// 3. Dynamic: choose which feedback to fire (return nil to skip)
func sensoryFeedback<T: Equatable>(
    trigger: T,
    _ feedback: @escaping (_ oldValue: T, _ newValue: T) -> SensoryFeedback?
) -> some View
```

### Every SensoryFeedback case, with examples

```swift
// .success — task completion
struct SaveView: View {
    @State private var didSave = false
    var body: some View {
        Button("Save") { didSave = true }
            .sensoryFeedback(.success, trigger: didSave)
    }
}

// .warning and .error — chosen dynamically via the closure overload
struct SubmitView: View {
    @State private var status = 0   // 0 idle, 1 warn, 2 error
    var body: some View {
        Button("Submit") { status = Int.random(in: 0...2) }
            .sensoryFeedback(trigger: status) { _, new in
                switch new {
                case 1: return .warning
                case 2: return .error
                default: return nil
                }
            }
    }
}

// .selection — scrubbing through discrete values
struct ThemePicker: View {
    @State private var scheme: ColorScheme = .light
    var body: some View {
        Picker("Theme", selection: $scheme) {
            Text("Light").tag(ColorScheme.light)
            Text("Dark").tag(ColorScheme.dark)
        }
        .pickerStyle(.segmented)
        .sensoryFeedback(.selection, trigger: scheme)
    }
}

// .impact with weight + intensity
struct HeavyButton: View {
    @State private var tapped = false
    var body: some View {
        Button("Slam") { tapped.toggle() }
            .sensoryFeedback(.impact(weight: .heavy, intensity: 0.9),
                             trigger: tapped)
    }
}

// .impact with flexibility
struct SoftTap: View {
    @State private var n = 0
    var body: some View {
        Button("Squish \(n)") { n += 1 }
            .sensoryFeedback(.impact(flexibility: .soft, intensity: 0.5),
                             trigger: n)
    }
}

// .increase and .decrease — chosen by comparing old and new
struct ValueStepper: View {
    @State private var value = 50
    var body: some View {
        Stepper("Value: \(value)", value: $value, in: 0...100)
            .sensoryFeedback(trigger: value) { old, new in
                new > old ? .increase : .decrease
            }
    }
}

// .start and .stop — for continuous activities
struct WorkoutControls: View {
    @State private var running = false
    var body: some View {
        Button(running ? "Stop" : "Start") { running.toggle() }
            .sensoryFeedback(running ? .start : .stop, trigger: running)
    }
}

// .alignment and .levelChange — macOS-centric
#if os(macOS)
struct MacDrag: View {
    @State private var snapped = false
    @State private var level = 0
    var body: some View {
        VStack {
            Rectangle().frame(width: 100, height: 100)
                .sensoryFeedback(.alignment, trigger: snapped)
            Slider(value: .init(
                get: { Double(level) },
                set: { level = Int($0) }
            ), in: 0...10, step: 1)
                .sensoryFeedback(.levelChange, trigger: level)
        }
    }
}
#endif

// Condition-based: only fire when selection becomes non-nil
struct SelectionList<Item: Hashable>: View {
    let items: [Item]
    @State var selection: Item?
    var body: some View {
        List(items, id: \.self, selection: $selection) { Text("\($0)") }
            .sensoryFeedback(.selection, trigger: selection) { old, new in
                new != nil && new != old
            }
    }
}

// Multiple modifiers can stack for disjoint signals
struct FormView: View {
    @State private var submitted = false
    @State private var hasErrors = false
    var body: some View {
        Button("Submit") { submitted.toggle() }
            .sensoryFeedback(.success, trigger: submitted) { _, new in new && !hasErrors }
            .sensoryFeedback(.error,   trigger: submitted) { _, new in new &&  hasErrors }
    }
}
```

### Version additions

- **iOS 17**: Full `SensoryFeedback` vocabulary shipped.
- **iOS 17.5**: Added `.pathComplete` alongside `UICanvasFeedbackGenerator` for drawing/canvas use cases on iPad.
- **iOS 18**: Added `SensoryFeedback.ReleaseFeedback` — a nested type for press-down/release-up pairs used by interactive controls and the Liquid Glass button treatments that iOS 26 leans on.
- **iOS 26**: No broad new public `SensoryFeedback` cases documented; refinement centers on paired press/release feedback on system controls and expanded user-facing Music Haptics options. Under the hood, SwiftUI still bridges to the same UIKit/WatchKit/AppKit primitives.

### How SwiftUI bridges to lower layers

On iOS, `.success/.warning/.error` → `UINotificationFeedbackGenerator`; `.selection` → `UISelectionFeedbackGenerator`; `.impact(*)` → `UIImpactFeedbackGenerator(style:).impactOccurred(intensity:)`; `.start/.stop` → WatchKit on watchOS; `.alignment/.levelChange` → `NSHapticFeedbackManager` on macOS.

---

## 2. UIKit feedback generators

The UIKit family dates from iOS 10 (WWDC 2016) and remains the workhorse for imperative code, UIKit apps, and anywhere you need explicit `prepare()` control.

### Class hierarchy

- `UIFeedbackGenerator` (abstract superclass — never subclass it yourself)
  - `UIImpactFeedbackGenerator`
  - `UINotificationFeedbackGenerator`
  - `UISelectionFeedbackGenerator`
  - `UICanvasFeedbackGenerator` (iPadOS 17.5+, Apple Pencil Pro / M4 Magic Keyboard only)

### Signatures you actually use

```swift
// Impact — iOS 10; .soft/.rigid + intensity added iOS 13; location APIs iOS 17.5
class UIImpactFeedbackGenerator: UIFeedbackGenerator {
    enum FeedbackStyle { case light, medium, heavy, soft, rigid }

    init()                                                 // medium
    init(style: FeedbackStyle)
    init(style: FeedbackStyle, view: UIView)               // iOS 17.5+

    func impactOccurred()
    func impactOccurred(intensity: CGFloat)                // iOS 13+
    func impactOccurred(at location: CGPoint)              // iOS 17.5+
    func impactOccurred(intensity: CGFloat, at location: CGPoint) // iOS 17.5+
}

// Notification
class UINotificationFeedbackGenerator: UIFeedbackGenerator {
    enum FeedbackType { case success, warning, error }
    init()
    init(view: UIView)                                     // iOS 17.5+
    func notificationOccurred(_ type: FeedbackType)
    func notificationOccurred(_ type: FeedbackType, at location: CGPoint)
}

// Selection
class UISelectionFeedbackGenerator: UIFeedbackGenerator {
    init()
    init(view: UIView)                                     // iOS 17.5+
    func selectionChanged()
    func selectionChanged(at location: CGPoint)
}
```

### The prepare() pattern — why it exists and how to use it

The Taptic Engine is kept idle to save power. Cold-starting it before a haptic incurs a wake-up cost commonly measured at **~100–200 ms** by third-party developers (Apple has not published an exact figure). `prepare()` primes the engine so the next trigger fires with near-zero latency. Apple engineers have confirmed on Developer Forums that the engine is held warm "for a short time" — community testing converges on **~2 seconds**.

**The rule**: call `prepare()` at a plausible leading edge (e.g., `touchDown`, `UIGestureRecognizer.State.began`), then fire the actual feedback on the trailing action (`touchUpInside`, `.changed/.ended`). Calling `prepare()` and `impactOccurred()` back-to-back is pointless — there's no time to amortize.

### UIKit examples

```swift
import UIKit

final class ButtonViewController: UIViewController {
    private let impact = UIImpactFeedbackGenerator(style: .medium)
    @IBOutlet weak var button: UIButton!

    override func viewDidLoad() {
        super.viewDidLoad()
        button.addTarget(self, action: #selector(touchDown), for: .touchDown)
        button.addTarget(self, action: #selector(touchUp),   for: .touchUpInside)
    }
    @objc private func touchDown() { impact.prepare() }
    @objc private func touchUp()   { impact.impactOccurred(intensity: 0.8) }
}

final class ResultVC: UIViewController {
    private let notif = UINotificationFeedbackGenerator()

    func onNetworkFinish(success: Bool) {
        notif.prepare()
        notif.notificationOccurred(success ? .success : .error)
    }
}

final class SliderVC: UIViewController {
    private var selection: UISelectionFeedbackGenerator?
    private var lastSegment = 0

    @IBAction func panned(_ sender: UIPanGestureRecognizer) {
        switch sender.state {
        case .began:
            selection = UISelectionFeedbackGenerator()
            selection?.prepare()
        case .changed:
            let segment = Int(sender.translation(in: view).x / 20)
            if segment != lastSegment {
                selection?.selectionChanged()
                selection?.prepare()
                lastSegment = segment
            }
        case .ended, .cancelled, .failed:
            selection = nil   // release to power down the Taptic Engine
        default: break
        }
    }
}
```

### A reusable UIKit haptic manager

```swift
import UIKit

@MainActor
final class HapticManager {
    static let shared = HapticManager()

    private let lightImpact  = UIImpactFeedbackGenerator(style: .light)
    private let mediumImpact = UIImpactFeedbackGenerator(style: .medium)
    private let heavyImpact  = UIImpactFeedbackGenerator(style: .heavy)
    private let softImpact   = UIImpactFeedbackGenerator(style: .soft)
    private let rigidImpact  = UIImpactFeedbackGenerator(style: .rigid)
    private let notification = UINotificationFeedbackGenerator()
    private let selection    = UISelectionFeedbackGenerator()

    private init() {}

    enum Impact { case light, medium, heavy, soft, rigid }

    func impact(_ style: Impact, intensity: CGFloat = 1.0) {
        let gen: UIImpactFeedbackGenerator = {
            switch style {
            case .light:  return lightImpact
            case .medium: return mediumImpact
            case .heavy:  return heavyImpact
            case .soft:   return softImpact
            case .rigid:  return rigidImpact
            }
        }()
        gen.impactOccurred(intensity: intensity)
    }

    func notify(_ type: UINotificationFeedbackGenerator.FeedbackType) {
        notification.notificationOccurred(type)
    }

    func selectionChanged() { selection.selectionChanged() }

    func prepareImpact(_ style: Impact) {
        switch style {
        case .light:  lightImpact.prepare()
        case .medium: mediumImpact.prepare()
        case .heavy:  heavyImpact.prepare()
        case .soft:   softImpact.prepare()
        case .rigid:  rigidImpact.prepare()
        }
    }
    func prepareNotification() { notification.prepare() }
    func prepareSelection()    { selection.prepare() }
}
```

### Lifecycle rules

**Retain generators as properties** for frequently used feedback (pickers, reorderable lists). **Create on demand** for one-offs. **Release when the gesture ends** — setting the generator to `nil` is a hint to the system to power down the Taptic Engine sooner, saving battery. All `UIFeedbackGenerator` calls must happen on the **main thread**; in Swift, the subclasses are effectively `@MainActor`.

---

## 3. Core Haptics (CHHapticEngine)

When system patterns aren't enough — when you need precise timing, arbitrary sequences, audio-synchronized taps, textures, or real-time modulation — you drop into Core Haptics. It was introduced at **WWDC 2019 session 520 "Introducing Core Haptics"** and requires **iPhone 8 or later**. iPads, Vision Pro, and the Apple TV do not support internal Core Haptics; Macs only support it via MFi game controllers.

### When to choose Core Haptics

Games, custom product interactions (dial detents, elastic pull-to-refresh variants, physics), ambient feedback (breathing exercises, heartbeats), textures (rolling-ball surfaces, footsteps), rhythmic patterns (Morse, drums), and any case where **haptic and audio must share one timeline**. Trade-offs: more code, real battery cost for long patterns, hardware gating, and `start()` latency if you don't pre-warm.

### Engine anatomy

```swift
// Capability check (authoritative)
let caps = CHHapticEngine.capabilitiesForHardware()
guard caps.supportsHaptics else { return }   // iPhone 8+ only

// Initialize (can throw)
let engine = try CHHapticEngine()
// or: try CHHapticEngine(audioSession: mySession)

engine.isAutoShutdownEnabled = true     // power-saves between plays
engine.playsHapticsOnly = false         // include audio events too
engine.isMutedForHaptics = false
engine.isMutedForAudio   = false
```

### Handlers you must wire up

```swift
engine.stoppedHandler = { reason in
    // .audioSessionInterrupt, .applicationSuspended, .idleTimeout,
    // .notifyWhenFinished, .engineDestroyed, .gameControllerDisconnect, .systemError
    print("Engine stopped:", reason)
}
engine.resetHandler = { [weak self] in
    // Server reset — rebuild players, re-register audio resources, restart.
    guard let self, let e = self.engine else { return }
    try? e.start()
}
```

**Critical detail about resets**: on `resetHandler`, `CHHapticPattern` and engine properties are preserved but **you must re-register any audio resources** and **recreate players**.

### Events, parameters, and patterns

Event types:
- `.hapticTransient` — a brief, percussive tap (no duration).
- `.hapticContinuous` — a sustained vibration up to ~30 s; supports attack/decay/release envelope.
- `.audioContinuous` — synthesized tone, parameterized (`audioPitch`, `audioVolume`, `audioPan`, `audioBrightness`).
- `.audioCustom` — your own WAV/CAF waveform, registered via `registerAudioResource` or referenced by `EventWaveformPath` in AHAP.

Static event parameters include `.hapticIntensity` (0.0–1.0), `.hapticSharpness` (0.0–1.0 — a perceptual "roundness→crispness" axis unique to Core Haptics), `.attackTime`, `.decayTime`, `.releaseTime`, `.sustained`, and audio equivalents.

Dynamic parameters (modify during playback) include `.hapticIntensityControl` (multiplicative, 0.0–1.0) and `.hapticSharpnessControl` (additive, −1.0…+1.0). `CHHapticParameterCurve` interpolates smoothly between control points — keep to ~16 points or fewer per curve (additional points are silently truncated in practice).

### Complete working example

```swift
import UIKit
import CoreHaptics

final class HapticsController {
    private var engine: CHHapticEngine?
    private var supportsHaptics: Bool {
        CHHapticEngine.capabilitiesForHardware().supportsHaptics
    }

    func prepare() {
        guard supportsHaptics else { return }
        do {
            let engine = try CHHapticEngine()
            self.engine = engine
            engine.isAutoShutdownEnabled = true
            engine.stoppedHandler = { reason in
                print("CHHapticEngine stopped:", reason.rawValue)
            }
            engine.resetHandler = { [weak self] in
                guard let self, let e = self.engine else { return }
                do { try e.start() }
                catch { print("Restart failed:", error) }
            }
            try engine.start()
        } catch {
            print("Engine init failed:", error)
        }
    }

    func playImpactPattern(intensity: Float = 1.0, sharpness: Float = 0.7) {
        guard supportsHaptics, let engine = engine else { return }
        do {
            try engine.start() // no-op if already running

            let transient = CHHapticEvent(
                eventType: .hapticTransient,
                parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: intensity),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: sharpness)
                ],
                relativeTime: 0
            )
            let continuous = CHHapticEvent(
                eventType: .hapticContinuous,
                parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: intensity * 0.8),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.2),
                    CHHapticEventParameter(parameterID: .attackTime,      value: 0.0),
                    CHHapticEventParameter(parameterID: .decayTime,       value: 0.5),
                    CHHapticEventParameter(parameterID: .sustained,       value: 0.0),
                    CHHapticEventParameter(parameterID: .releaseTime,     value: 0.2)
                ],
                relativeTime: 0.02,
                duration: 0.8
            )
            let curve = CHHapticParameterCurve(
                parameterID: .hapticIntensityControl,
                controlPoints: [
                    .init(relativeTime: 0.0,  value: 1.0),
                    .init(relativeTime: 0.4,  value: 0.6),
                    .init(relativeTime: 0.82, value: 0.0)
                ],
                relativeTime: 0.02
            )
            let pattern = try CHHapticPattern(events: [transient, continuous],
                                              parameterCurves: [curve])
            let player  = try engine.makePlayer(with: pattern)
            try player.start(atTime: CHHapticTimeImmediate)
        } catch {
            print("Failed to play:", error)
        }
    }

    func playAHAP(named name: String) {
        guard supportsHaptics, let engine = engine,
              let url = Bundle.main.url(forResource: name, withExtension: "ahap") else { return }
        do {
            try engine.start()
            try engine.playPattern(from: url)
        } catch {
            print("AHAP failed:", error)
        }
    }

    func sceneWillEnterForeground() { try? engine?.start() }
    func sceneDidEnterBackground()  { engine?.stop(completionHandler: nil) }
}
```

### AHAP (Apple Haptic and Audio Pattern) — a full example

AHAP is a JSON document with top-level `Version`, optional `Metadata`, and `Pattern` (an array of `Event`, `Parameter`, and `ParameterCurve` objects). Here's a working heartbeat pattern — drop in the bundle as `Heartbeat.ahap`:

```json
{
  "Version": 1,
  "Metadata": { "Project": "Reference", "Description": "Two-beat heartbeat" },
  "Pattern": [
    { "Event": { "Time": 0.0, "EventType": "HapticTransient",
        "EventParameters": [
          { "ParameterID": "HapticIntensity", "ParameterValue": 1.0 },
          { "ParameterID": "HapticSharpness", "ParameterValue": 0.3 }]}},
    { "Event": { "Time": 0.18, "EventType": "HapticTransient",
        "EventParameters": [
          { "ParameterID": "HapticIntensity", "ParameterValue": 0.7 },
          { "ParameterID": "HapticSharpness", "ParameterValue": 0.2 }]}},
    { "Event": { "Time": 0.0, "EventType": "HapticContinuous", "EventDuration": 0.35,
        "EventParameters": [
          { "ParameterID": "HapticIntensity", "ParameterValue": 0.25 },
          { "ParameterID": "HapticSharpness", "ParameterValue": 0.1 },
          { "ParameterID": "Sustained",       "ParameterValue": 0.0 },
          { "ParameterID": "DecayTime",       "ParameterValue": 0.3 }]}},
    { "Event": { "Time": 1.0, "EventType": "HapticTransient",
        "EventParameters": [
          { "ParameterID": "HapticIntensity", "ParameterValue": 1.0 },
          { "ParameterID": "HapticSharpness", "ParameterValue": 0.3 }]}},
    { "Event": { "Time": 1.18, "EventType": "HapticTransient",
        "EventParameters": [
          { "ParameterID": "HapticIntensity", "ParameterValue": 0.7 },
          { "ParameterID": "HapticSharpness", "ParameterValue": 0.2 }]}},
    { "ParameterCurve": {
        "ParameterID": "HapticIntensityControl",
        "Time": 0.0,
        "ParameterCurveControlPoints": [
          { "Time": 0.0, "ParameterValue": 1.0 },
          { "Time": 1.0, "ParameterValue": 1.0 },
          { "Time": 1.4, "ParameterValue": 0.6 }]}}
  ]
}
```

### Audio synchronization

The tightest coupling is inside the AHAP: an `AudioCustom` event with `EventWaveformPath` plays on the same timeline as your haptic events, yielding sample-accurate sync. For programmatic sync with `AVAudioPlayer` or `AVAudioEngine`, use `engine.currentTime` as a shared clock:

```swift
let startTime = engine.currentTime + 0.1
try player.start(atTime: startTime)
let delay = startTime - engine.currentTime
audioPlayer.play(atTime: audioPlayer.deviceCurrentTime + delay)
```

**Caveat**: AHAP-referenced audio is treated as notification-style audio and honors the silent switch; haptics are also suppressed during active `AVCaptureSession` audio recording, which is why Apple's own Camera app uses `AudioServicesPlaySystemSound` for shutter haptics.

### Engine lifecycle best practices

Create one engine per surface and keep a strong reference. Start lazily on first need — or pre-warm on `onAppear` if latency matters. Stop when you know you won't need it for a while (view disappears, level ends). Always restart on `resetHandler` and re-register audio resources. Backgrounding stops the engine with reason `.applicationSuspended`; restart on `sceneWillEnterForeground`.

---

## 4. Semantic meaning: what each haptic actually says

The whole system depends on *consistent meaning*. Apple's HIG warns explicitly: *"If your app plays a specific haptic pattern when a game character fails to finish a mission, people associate that pattern with a negative outcome. If you use the same haptic pattern for a positive outcome… people will be confused."*

**Notification feedback is result-oriented**. `.success` is a double-tap (high-low) reserved for consequential positive outcomes — Apple Pay transactions, file saves, authentication. `.warning` is a paced double tap for non-blocking caution. `.error` is a sharper triple-tap for blocking failures — wrong password, rejected payment, failed validation.

**Impact feedback is physical-metaphor oriented**. Match intensity to visual weight. Light for a small chip clicking into place; medium for a standard sheet hitting its detent; heavy for a big modal landing. The iOS 13 additions widen the vocabulary: `.soft` feels damped and cushioned (good for squishy, cartoon-like dismissals); `.rigid` feels stiff and metallic (perfect for shutter clicks and hard latches).

**Selection feedback is a series, not a singleton**. `.selection` means *"a value crossed a discrete boundary"* — one tick per value crossed. Never use it for a single toggle (that's impact) and never for a final result (that's notification). The canonical example is scrubbing a UIPickerView.

**SwiftUI's semantic additions** refine further: `.increase`/`.decrease` mark a threshold crossing, not every tiny step; `.start`/`.stop` bracket a continuous activity; `.alignment` fires when a drag locks onto a guide; `.levelChange` marks transitions between discrete levels (fast-forward speeds, Force Touch pressure levels); `.pathComplete` (iOS 17.5+) marks a continuous gesture closing.

**watchOS has its own vocabulary** (`WKHapticType`) that includes directional taps used by Apple Maps: `.navigationLeftTurn` plays three pairs of two taps; `.navigationRightTurn` plays twelve steady taps — a genuinely eyes-free signaling scheme.

---

## 5. Anti-patterns: when NOT to use haptics

These eleven rules are the distillation of Apple's HIG plus community experience. Each one reflects a real mistake that appears in poorly reviewed apps.

**❌ Haptic on every button tap.** Apple's HIG: *"Prefer adding haptics to a small number of significant, consequential interactions."* Ordinary taps don't need decoration. Haptic fatigue kills signal.

**❌ Haptic during scrolling.** The scroll system already provides rubber-band and end-of-content haptics. Adding more creates conflict and breaks the native feel.

**❌ Haptic during typing.** Users who want keyboard haptics have opted in system-wide (Settings → Sounds & Haptics → Keyboard Feedback). Overriding is rude — and Apple itself flags keyboard haptics as a battery consideration because it fires per keystroke.

**❌ Haptic on ambient/background state changes the user didn't trigger.** The causal link is the whole point. If the user didn't do something, they shouldn't feel something.

**❌ Haptics as the primary signal for critical information.** Many users disable System Haptics; others can't perceive subtle patterns (gloves, phone on a soft surface, sensory differences). Haptics always augment; they never substitute. HIG: *"Make haptics optional."*

**❌ Too many haptics in quick sequence.** Rapid repeated haptics blur into indistinct buzz, drawing more power without communicating anything.

**❌ Gratuitous haptics to "spice up" an animation.** HIG: *"Using them to add novelty can make your app feel gimmicky."* If there's no semantic meaning, don't add the tap.

**❌ Overriding standard control haptics.** `UISwitch`, `UISlider`, `UIPickerView`, `UIDatePicker`, pull-to-refresh — all handled. Stacking your own on top creates double-feedback.

**❌ Haptics without correspondence to a visual or auditory cue.** HIG: *"When visual, auditory, and tactile feedback are in harmony… the user experience is more coherent."* Unanchored haptics feel untethered.

**❌ Inconsistent haptic vocabulary across your app.** Same action → same haptic. Different outcome → different haptic. Anything else trains users into confusion.

**❌ Haptics during camera capture, microphone recording, or gyroscope-sensitive tasks.** iOS automatically suppresses haptics while an `AVCaptureSession` is actively recording audio. Design around it; don't fight it.

---

## 6. Battery and performance

The Taptic Engine is a **linear resonant actuator** (LRA) — much more efficient than older eccentric-rotating-mass vibrators. Individual transient pulses are brief (typically <50 ms) and cost essentially nothing at normal app-use rates. A handful of haptics per session is not measurable battery impact.

Apple has only published a battery caveat for **one feature**: keyboard haptics. The Apple support note states *"Turning on keyboard haptics might affect the battery life of your iPhone"* — precisely because they fire thousands of times per day. That's the useful calibration point: haptics become a battery concern at keyboard-use frequencies, not at normal app-feedback frequencies.

**Core Haptics is different**. `CHHapticEngine` is a server connection that costs real power when running. Keep an engine idle with `isAutoShutdownEnabled = true`, or explicitly `stop()` it when you know it won't be needed soon. Long continuous patterns with audio draw the most.

**`prepare()` cost model**: Apple engineer commentary on Developer Forums says *"we keep the engine warm for a short time, under the expectation that a request will come in 'soon'."* Community testing puts cold-start latency at **~100–200 ms** and the warm window at **~2 seconds**. If no haptic fires, the engine returns to idle — no harm done. The biggest performance mistake is **creating a new generator instance per event** instead of reusing one; each new instance loses its warm state and incurs fresh initialization.

**In-flight suppression**: while `AVCaptureSession` is actively recording audio, iOS suppresses haptics automatically. That's why Apple's own Camera app uses `AudioServicesPlaySystemSound` rather than `UIFeedbackGenerator` for shutter feedback.

---

## 7. Accessibility

### The system toggles that change your app's behavior

**Settings → Sounds & Haptics → System Haptics** is the master toggle for system-driven AND app-driven `UIFeedbackGenerator` haptics. When off, your `UIImpactFeedbackGenerator.impactOccurred()` call produces no vibration. Core Haptics is also effectively silenced when the user disables System Haptics (behavior has been inconsistent across iOS versions; the safe assumption is it's respected).

**Settings → Accessibility → Touch → Vibration** is a more aggressive master switch that disables ALL vibrations — including emergency alerts. Apple warns users explicitly when toggling it off.

**`UIAccessibility.isReduceMotionEnabled`** does NOT directly affect haptics. It suppresses certain *combined* experiences (iMessage screen effects and bubble effects include haptics that get disabled when Reduce Motion is on), but basic `UIFeedbackGenerator` haptics continue to fire. There is no public "isReduceHapticsEnabled" flag.

### Can you detect whether haptics are enabled?

**No, there is no public API for the user preference.** `CHHapticEngine.capabilitiesForHardware().supportsHaptics` tells you whether the **hardware** supports haptics, not whether the user has enabled them. Apple's explicit guidance on Developer Forums: trust the system to silently suppress, and follow the HIG's dictum to *"make haptics optional"* in your own settings for finer control.

### VoiceOver and haptic-dependent users

VoiceOver has its own independent haptic layer (Settings → Accessibility → VoiceOver → Audio → Sounds & Haptics on iPhone 8+), separately configurable per event (focus, scroll boundary, flick, etc.) with user-adjustable intensity. Blind and low-vision users **rely** on these cues to navigate. Your app should use standard controls so VoiceOver's built-in haptics fire correctly, and avoid piling custom haptics on top that could drown meaningful feedback.

For deaf and hard-of-hearing users, iOS 18's **Music Haptics** (Settings → Accessibility → Music Haptics) plays synchronized haptic textures along with songs in Apple Music, Music Classical, and Shazam — one of Apple's strongest examples of haptics as a primary accessibility channel rather than decoration.

### Practical rules for inclusive haptic design

Test your app with System Haptics **off** — the experience must still be complete. Test with VoiceOver **on** — your haptics must not interfere with VoiceOver's cues. Offer an in-app toggle for users who want *some* apps loud and others silent. Stay semantically strict: `.success` means success, `.error` means error. Users who rely on haptics *depend* on that consistency.

---

## 8. How Apple's own apps use haptics

The most useful study material is Apple's first-party apps. Here's what to observe on an iPhone with System Haptics enabled:

**Photos** gives a subtle impact tap when pinch-zoom hits its limit (the rubber-band wall), a light selection tick as each photo enters or leaves Select mode, a medium impact when a swipe-to-delete or favorite commits, and selection ticks as the library timeline scrubs across years/months/days.

**Music** emits selection ticks scrubbing the Now Playing progress bar, small taps as the volume slider crosses quanta, a gentle impact when a song ends and transitions, and a light impact on track selection. iOS 18's Music Haptics layers full-song textured feedback for accessibility.

**Mail** uses a distinct impact at the pull-to-refresh trigger point (one of iOS's signature haptics), medium impact when swipe-to-delete/archive crosses the commit threshold, and light ticks for mark-as-read/flag.

**Messages** pairs a subtle impact with the iMessage send animation; tapback selection plays a light tick with a stronger confirmation on apply; bubble effects (Slam, Loud, Gentle, Invisible Ink) each ship with custom Core Haptics patterns choreographed to their animations, and full-screen effects (Balloons, Confetti, Fireworks, etc.) use audio+haptic choreography that Apple demoed in the WWDC 2019 Core Haptics sessions.

**Camera** uses `AudioServicesPlaySystemSound` for shutter feedback (it fires during an active capture session where UIFeedbackGenerator would be suppressed). Mode changes scrub with selection ticks. The iPhone 16/17 **Camera Control button** is an especially rich surface: a force-sensor light-press gives a haptic half-click for focus/controls, a full press a stronger shutter click, and swipes for zoom produce selection ticks at each optical detent.

**Clock** uses classic picker-wheel ticks for time selection, medium impact on timer start/stop, light impact on each stopwatch lap, and a success notification when dismissing an alarm.

**Maps** is the best haptic design in Apple's lineup. On Apple Watch, turn-by-turn taps use distinct directional patterns — three pairs of two taps for a left turn, twelve steady taps for a right turn — so the user can navigate without glancing at the screen. On iPhone, impacts pair with spoken instructions at key maneuvers.

**Settings, Control Center, Weather, Stocks, Home Screen** all lean on a shared vocabulary: light impact on toggle switches (the most common haptic on iOS), selection ticks on sliders and scrubbers crossing detents, impact when Home Screen enters jiggle mode, alignment-like impacts as widgets snap to grid, and impact at each Control Center toggle or expanded-module transition.

The **Apple Pay success haptic** is the canonical reference Apple cites in its own HIG — it's the one haptic that defined the template for `.success` across the entire platform.

---

## 9. Cross-platform compatibility

| Platform | Built-in haptic hardware | Primary API | SwiftUI `sensoryFeedback` | Core Haptics | Fallback |
|---|---|---|---|---|---|
| iPhone (7+; 8+ for Core Haptics) | Taptic Engine | `UIFeedbackGenerator` (iOS 10+); `CHHapticEngine` (iOS 13+) | ✅ iOS 17+ | ✅ iPhone 8+ | — |
| iPad (all, incl. iPad mini A17 Pro, iPad Pro M4) | ❌ None internally | `UICanvasFeedbackGenerator` (Pencil Pro / M4 Magic Keyboard trackpad only) | Compiles; effectively no-op except Canvas contexts | Compiles; `supportsHaptics` = false | Silent no-op |
| Mac (Force Touch trackpad) | Force Touch actuator | `NSHapticFeedbackManager` | ✅ macOS 14+ (only `.alignment`/`.levelChange` meaningful) | MFi controllers only | Silent no-op |
| Mac (no Force Touch) | ❌ | — | No-op | No | Silent no-op |
| Apple Watch (all models) | Taptic Engine | `WKInterfaceDevice.play(WKHapticType)` | ✅ watchOS 10+ | ❌ not available | — |
| Vision Pro | ❌ | UIFeedbackGenerator unavailable | Compiles, silent no-op | No-op | Audio + visual only |
| Apple TV | ❌ (Siri Remote has no haptics) | UIFeedbackGenerator unavailable | Not meaningful | MFi controllers only | Silent no-op |

**Key facts to internalize**: No iPad ships with a Taptic Engine — **this remains true through iPad mini (A17 Pro, 2024) and iPad Pro M4** (Apple Pencil Pro contains its own haptic actuator that plays into the hand, which is separate hardware). `CHHapticEngine.capabilitiesForHardware().supportsHaptics` returns true only on iPhones with Core Haptics support; Apple DTS has confirmed this means "iPhones only, effectively." On macOS, Core Haptics is only useful for paired MFi game controllers; the Mac's internal Force Touch trackpad is driven by `NSHapticFeedbackManager`, which exposes only three patterns: `.generic`, `.alignment`, `.levelChange`.

**watchOS's full `WKHapticType` vocabulary**: `.notification`, `.directionUp`, `.directionDown`, `.success`, `.failure`, `.retry`, `.start`, `.stop`, `.click`, plus navigation-specific `.navigationLeftTurn`, `.navigationRightTurn`, `.navigationGenericManeuver` (watchOS 6+), and `.underwaterDepthPrompt`/`.underwaterDepthCriticalPrompt` (watchOS 9+ on Ultra). Core Haptics is *not* available on watchOS.

---

## 10. References — WWDC sessions and Apple documentation

### WWDC sessions

| Year | Session | Title | URL |
|---|---|---|---|
| 2016 | 205 | What's New in Cocoa Touch (introduced UIFeedbackGenerator) | https://developer.apple.com/videos/play/wwdc2016/205/ |
| 2019 | **520** | Introducing Core Haptics | https://developer.apple.com/videos/play/wwdc2019/520/ |
| 2019 | **223** | Expanding the Sensory Experience with Core Haptics | https://developer.apple.com/videos/play/wwdc2019/223/ |
| 2019 | 810 | Designing Audio-Haptic Experiences | https://developer.apple.com/videos/play/wwdc2019/810/ |
| 2021 | 10278 | Practice audio haptic design | https://developer.apple.com/videos/play/wwdc2021/10278/ |
| 2023 | **10148** | What's new in SwiftUI (introduces `.sensoryFeedback`) | https://developer.apple.com/videos/play/wwdc2023/10148/ |
| 2024 | 10214 | Squeeze the most out of Apple Pencil | https://developer.apple.com/videos/play/wwdc2024/10214/ |
| 2024 | 10118 | What's new in UIKit (covers `UICanvasFeedbackGenerator`) | https://developer.apple.com/videos/play/wwdc2024/10118/ |

There is no standalone "Introducing sensoryFeedback" session; the API was covered inside WWDC 2023's "What's new in SwiftUI." Core Haptics itself has seen no new dedicated sessions since 2021 — the framework is stable and unchanged through iOS 26.

### Apple Human Interface Guidelines
- Playing haptics — https://developer.apple.com/design/human-interface-guidelines/playing-haptics
- Playing haptic feedback in your app (Apple Pencil) — https://developer.apple.com/documentation/applepencil/playing-haptic-feedback-in-your-app

### SwiftUI
- `SensoryFeedback` — https://developer.apple.com/documentation/swiftui/sensoryfeedback
- `.sensoryFeedback(_:trigger:)` — https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(_:trigger:)
- `.sensoryFeedback(_:trigger:condition:)` — https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(_:trigger:condition:)
- `.sensoryFeedback(trigger:_:)` (feedback closure) — https://developer.apple.com/documentation/swiftui/view/sensoryfeedback(trigger:_:)
- `SensoryFeedback.impact(weight:intensity:)` — https://developer.apple.com/documentation/swiftui/sensoryfeedback/impact(weight:intensity:)
- `SensoryFeedback.impact(flexibility:intensity:)` — https://developer.apple.com/documentation/swiftui/sensoryfeedback/impact(flexibility:intensity:)
- `SensoryFeedback.ReleaseFeedback` — https://developer.apple.com/documentation/swiftui/sensoryfeedback/releasefeedback

### UIKit
- `UIFeedbackGenerator` — https://developer.apple.com/documentation/uikit/uifeedbackgenerator
- `UIImpactFeedbackGenerator` — https://developer.apple.com/documentation/uikit/uiimpactfeedbackgenerator
- `UINotificationFeedbackGenerator` — https://developer.apple.com/documentation/uikit/uinotificationfeedbackgenerator
- `UISelectionFeedbackGenerator` — https://developer.apple.com/documentation/uikit/uiselectionfeedbackgenerator
- `UICanvasFeedbackGenerator` — https://developer.apple.com/documentation/uikit/uicanvasfeedbackgenerator

### Core Haptics
- Framework — https://developer.apple.com/documentation/corehaptics
- `CHHapticEngine` — https://developer.apple.com/documentation/corehaptics/chhapticengine
- `CHHapticPattern` — https://developer.apple.com/documentation/corehaptics/chhapticpattern
- `CHHapticEvent` — https://developer.apple.com/documentation/corehaptics/chhapticevent
- AHAP file format — https://developer.apple.com/documentation/corehaptics/representing-haptic-patterns-in-ahap-files
- Sample: Playing a Custom Haptic Pattern from a File — https://developer.apple.com/documentation/corehaptics/playing-a-custom-haptic-pattern-from-a-file
- Sample: Delivering Rich App Experiences with Haptics — https://developer.apple.com/documentation/corehaptics/delivering-rich-app-experiences-with-haptics
- Updating Continuous and Transient Haptic Parameters in Real Time — https://developer.apple.com/documentation/corehaptics/updating-continuous-and-transient-haptic-parameters-in-real-time
- Playing Haptics on Game Controllers (macOS/tvOS path) — https://developer.apple.com/documentation/corehaptics/playing-haptics-on-game-controllers

### AppKit
- `NSHapticFeedbackManager` — https://developer.apple.com/documentation/appkit/nshapticfeedbackmanager

### WatchKit
- `WKInterfaceDevice` — https://developer.apple.com/documentation/watchkit/wkinterfacedevice
- `WKHapticType` — https://developer.apple.com/documentation/watchkit/wkhaptictype

---

## Conclusion: the one-page operating philosophy

The haptic system is best understood as a **shared vocabulary between Apple and the user**. Apple's HIG writes the dictionary; your app agrees to speak it. `.success` means success everywhere on iOS, so your app's `.success` had better not mean "I just tapped a button." The cost of inconsistency isn't abstract — it actively erodes the haptic channel for every other app.

The technical hierarchy mirrors the design hierarchy. Reach for **SwiftUI `sensoryFeedback`** first: it handles lifecycle, threading, and platform bridging, and it expresses intent declaratively (`trigger:` is a value, not a call site). Drop to **UIKit generators** when you need explicit `prepare()` timing or you're working in non-SwiftUI code — and always retain generators as properties to preserve their warmed state. Reach for **Core Haptics** only when you need custom patterns, textures, or audio synchronization; the complexity and battery cost are real.

The highest-leverage thing you can do for haptic quality in your app isn't writing more haptic code — it's **writing less**. Trust the system for standard controls. Haptic only the handful of moments that genuinely matter. Pair every haptic with a visual or auditory cue. Keep the vocabulary consistent. Offer a toggle. Test with System Haptics off, with VoiceOver on, and with the phone resting on a table where you can't feel the Taptic Engine through your hand. A haptic that the user *notices when it's missing* — Apple's own benchmark from the HIG — is the one worth shipping.