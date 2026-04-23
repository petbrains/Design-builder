---
name: motion
description: iOS motion & animation reference (iOS 18 + 26 Liquid Glass, SwiftUI springs, reduce motion)
platform: ios
---

# Motion on iOS 18 and iOS 26 — the complete developer reference

This reference is a single, opinionated guide to animation on modern Apple platforms. It targets **iOS 18 and iOS 26** with **SwiftUI as the primary framework**, UIKit equivalents included, and covers the Liquid Glass motion system introduced in iOS 26. Code examples are Swift 5.10+ / Swift 6-compatible and assume Xcode 16 (iOS 18) or Xcode 26 (iOS 26) toolchains.

The short version: **prefer springs over curves**, **scope every `.animation()` modifier to a value**, **never delete motion for Reduce Motion users — substitute it**, and **let Liquid Glass morph itself**.

---

## 1. Animation primitives

### 1.1 `withAnimation` — the explicit animation

`withAnimation` wraps a state change in a `Transaction` carrying an `Animation`. Every view whose rendering depends on state changed inside the closure will animate.

```swift
public func withAnimation<Result>(
    _ animation: Animation? = .default,
    _ body: () throws -> Result
) rethrows -> Result
```

```swift
Button("Toggle") {
    withAnimation(.snappy) { isExpanded.toggle() }
}
```

Since iOS 17 the default animation used when you write `withAnimation { … }` without arguments is **`.smooth`** — a spring with `bounce = 0`. Before iOS 17 it was a timing-curve ease. If you need a completion callback, use `withAnimation(_:completionCriteria:_:completion:)`; it fires on **perceptual** duration (the spring's `duration` parameter), not physical settling time.

### 1.2 `.animation` — the implicit (declarative) modifier

There are three overloads; treat only the last two as alive.

```swift
// iOS 13+, deprecated on most views: animates EVERYTHING in the subtree
func animation(_ animation: Animation?) -> some View

// iOS 15+, preferred: scoped to a specific value
func animation<V: Equatable>(_ animation: Animation?, value: V) -> some View

// iOS 17+, cleanest scoping: animation applies only to modifiers inside the closure
func animation<V: View>(
    _ animation: Animation?,
    @ViewBuilder body: (PlaceholderContentView<Self>) -> V
) -> some View
```

```swift
// Value-scoped: only changes correlated with `isOn` animate
Circle()
    .offset(x: isOn ? 100 : 0)
    .animation(.smooth, value: isOn)

// ViewBuilder-scoped (iOS 17+): surgical
SomeView()
    .animation(.default) { content in
        content
            .opacity(firstStep ? 1 : 0)
            .blur(radius: secondStep ? 0 : 20)
    }
```

### 1.3 The built-in `Animation` presets

| Preset | Underlying model | Default duration | Default bounce | Feel |
|---|---|---|---|---|
| `.linear` | timing curve | 0.35 s | — | Mechanical, constant speed — spinners only |
| `.easeIn` | timing curve | 0.35 s | — | Slow start, abrupt end — outgoing elements |
| `.easeOut` | timing curve | 0.35 s | — | Quick start, soft settle — **incoming** elements |
| `.easeInOut` | timing curve | 0.35 s | — | Symmetric, balanced — general-purpose curve |
| `.default` (iOS 17+) | spring | 0.5 s | 0.0 | Equivalent to `.smooth` |
| `.smooth` | spring | 0.5 s | **≈ 0.0** | No bounce, gentle settle — general purpose |
| `.snappy` | spring | 0.5 s | **≈ 0.15** | Quick, decisive, brisk tail |
| `.bouncy` | spring | 0.5 s | **≈ 0.30** | Playful, visible overshoot |
| `.spring` (iOS 17+) | spring | 0.5 s | 0.0 | Same as `.smooth` |
| `.interactiveSpring()` | spring | response 0.15 s | dampingFraction 0.86 | Low-latency tracking of live gestures |
| `.interpolatingSpring(...)` | physics spring | — | — | True physics; retriggers accumulate velocity |

Preset **intrinsic bounce values** (`.smooth ≈ 0`, `.snappy ≈ 0.15`, `.bouncy ≈ 0.30`) are not published numerically by Apple — only the additive `extraBounce` parameter is public — but they match WWDC 2023 "Animate with springs" (session 10158) demo snippets and all community cheat sheets. `extraBounce` is added **on top of** the intrinsic value.

```swift
withAnimation(.smooth) { /* bounce 0 */ }
withAnimation(.snappy(duration: 0.4)) { /* shorter */ }
withAnimation(.bouncy(extraBounce: 0.1)) { /* ≈ 0.40 */ }
withAnimation(.spring(duration: 0.6, bounce: 0.2)) { /* custom */ }
```

### 1.4 Legacy spring APIs — use with care

```swift
.animation(.spring(response: 0.55, dampingFraction: 0.825, blendDuration: 0), value: x)
.animation(.interpolatingSpring(mass: 1, stiffness: 170, damping: 15, initialVelocity: 0), value: x)
.animation(.interactiveSpring(), value: x)
```

**Pitfall**: `.interpolatingSpring` composes on retrigger — hitting the same button mid-animation makes motion increasingly energetic as springs combine. The iOS 17 `.spring(duration:bounce:)` uses velocity hand-off instead and does not accumulate.

---

## 2. Spring animations (iOS 17+)

WWDC 2023 session 10158 ("Animate with springs") reframed springs as the primary animation type in SwiftUI. Three insights make springs indispensable:

- **Velocity hand-off**: a drag gesture's release velocity flows directly into the animation.
- **Retargeting mid-flight**: changing the target mid-animation absorbs current velocity as the new initial velocity — no jerk.
- **Graceful settling**: exponential decay, never an abrupt stop.

From Jacob in 10158: *"Springs are the only type of animation that maintains continuity both for static cases and cases with an initial velocity."* And: *"A spring animation doesn't only mean a bouncy animation. … Non-bouncy springs are used in animations all over iOS."*

### 2.1 The `Spring` type

```swift
// Primary iOS 17+ initializer — perceptual duration + intuitive bounce
Spring(duration: TimeInterval = 0.5, bounce: Double = 0.0)

// Response / damping (iOS 17+, more familiar to UIKit animators)
Spring(response: Double, dampingRatio: Double)

// Physics form — for interop with UIKit / Core Animation
Spring(mass: Double = 1.0, stiffness: Double, damping: Double, allowOverDamping: Bool = false)

// From a target settling time
Spring(settlingDuration: TimeInterval, dampingRatio: Double, epsilon: Double = 0.001)
```

**`bounce` range: –1.0 … 1.0.**

| bounce | physics term | visual |
|---|---|---|
| `> 0` (up to 1.0) | underdamped | overshoots, oscillates |
| `= 0` | critically damped | smooth approach, no overshoot |
| `< 0` (down to –1.0) | overdamped | flatter than smooth; two-exponential decay — good for scroll-style decay |
| `= 1.0` | undamped | pure cosine — oscillates forever |

**Duration is perceptual, not settling.** Apple chose a duration parameter that stays stable as you adjust bounce, so tweaking doesn't force you to re-tune timing.

### 2.2 Old vs. new parameter mapping

| Old param | New param | Relationship |
|---|---|---|
| `response` | `duration` | ≈ equal at bounce 0 (`response` is half-period) |
| `dampingFraction` | `bounce` | `bounce = 1 − dampingFraction` |
| `blendDuration` | `blendDuration` | unchanged |

`dampingFraction = 0.825` ≈ `bounce = 0.175` — close to `.snappy`.

### 2.3 The math is first-class

`Spring` conforms to a calculation API that lets you drive custom renderers or compute settle times.

```swift
let s = Spring(duration: 0.5, bounce: 0.2)
let pos      = s.value(target: 1.0, time: 0.2)        // where is the spring at t=0.2s?
let velocity = s.velocity(target: 1.0, time: 0.2)
let settle   = s.settlingDuration(target: 1.0, initialVelocity: 2.0, epsilon: 0.01)
let (m, k, c) = (s.mass, s.stiffness, s.damping)      // convert to physics form
```

This is what makes sophisticated gesture animations possible — see §10.

### 2.4 When springs feel right vs. curves

**Use springs** for any user-initiated interaction (drag, swipe, flick), any state transition that may be interrupted, and any animation you want to compose naturally. Apple's recommendation in 10158: *"When you're not sure, use a spring with bounce 0."*

**Use curves** (`.linear`, `.easeInOut`) for continuous loops (spinners, shimmer), precise timing requirements, and non-interactive decorative motion where physics feels out of place.

Cap `bounce` around 0.4 for productivity UI. Anything higher draws attention away from the task and can feel gimmicky.

### 2.5 What's new in iOS 26

Springs themselves are unchanged in iOS 26. New animation-adjacent APIs that ride on the same spring system:

- `@Animatable` macro for making custom structs animatable with one attribute.
- Toolbar morphing (`DefaultToolbarItem`, `ToolbarSpacer`) for Liquid Glass.
- `glassEffectTransition(_:)` that respects Reduce Motion automatically.
- UIKit `UIView.animate(options: [.flushUpdates])` to coordinate UIKit animations with SwiftUI's observation-driven invalidation.

No breaking changes between iOS 17, 18, and 26 for the primitives covered so far.

---

## 3. Transitions

A **transition** is the visual change SwiftUI animates when a view is inserted into or removed from the hierarchy — inside a conditional branch, a `ForEach`, or when an `id` changes. Transitions run only when the insertion/removal happens inside an animated state change (most reliably, inside `withAnimation`).

### 3.1 The modifier and the built-ins

```swift
func transition(_ t: AnyTransition) -> some View                 // classic
func transition<T: Transition>(_ transition: T) -> some View     // iOS 17+
```

`AnyTransition` built-ins: `.opacity`, `.slide`, `.scale`, `.scale(scale:anchor:)`, `.move(edge:)`, `.offset(x:y:)`, `.push(from:)` (iOS 16+), `.identity`.

```swift
if show {
    Banner().transition(.push(from: .top))
}
```

### 3.2 Asymmetric and combined

```swift
.transition(.asymmetric(
    insertion: .move(edge: .trailing).combined(with: .opacity),
    removal:   .move(edge: .leading ).combined(with: .opacity)
))
```

`combined(with:)` runs effects simultaneously; `asymmetric(insertion:removal:)` lets insertion and removal differ.

### 3.3 Custom transitions — the `Transition` protocol (iOS 17+)

This is the modern approach. Conform to `Transition` and read a `TransitionPhase` (`.willAppear`, `.identity`, `.didDisappear`). `phase.value` is `-1 / 0 / +1` for clean arithmetic.

```swift
struct Twirl: Transition {
    func body(content: Content, phase: TransitionPhase) -> some View {
        content
            .scaleEffect(phase.isIdentity ? 1 : 0.5)
            .opacity(phase.isIdentity ? 1 : 0)
            .rotationEffect(phase.isIdentity ? .zero : .degrees(360))
            .blur(radius: phase.isIdentity ? 0 : 10)
    }
}

if show { Icon().transition(Twirl()) }
```

### 3.4 `matchedGeometryEffect` — hero animations

```swift
func matchedGeometryEffect<ID: Hashable>(
    id: ID,
    in namespace: Namespace.ID,
    properties: MatchedGeometryProperties = .frame,
    anchor: UnitPoint = .center,
    isSource: Bool = true
) -> some View
```

Put the same `id` in a shared `@Namespace` on two views; SwiftUI interpolates geometry between them.

```swift
struct HeroDemo: View {
    @Namespace private var ns
    @State private var expanded = false
    var body: some View {
        VStack {
            if expanded {
                RoundedRectangle(cornerRadius: 30).fill(.blue)
                    .matchedGeometryEffect(id: "hero", in: ns)
                    .frame(width: 300, height: 300)
            } else {
                RoundedRectangle(cornerRadius: 8).fill(.blue)
                    .matchedGeometryEffect(id: "hero", in: ns)
                    .frame(width: 60, height: 60)
            }
        }
        .onTapGesture { withAnimation(.spring) { expanded.toggle() } }
    }
}
```

### 3.5 Zoom navigation (iOS 18+)

`matchedGeometryEffect` doesn't survive navigation pushes, sheets, or full-screen covers. iOS 18 fixed this with a first-class zoom transition.

```swift
@Namespace private var ns

NavigationStack {
    NavigationLink {
        DetailView()
            .navigationTransition(.zoom(sourceID: item.id, in: ns))
    } label: {
        Thumbnail(item: item)
            .matchedTransitionSource(id: item.id, in: ns)
    }
}
```

Works on `.sheet` and `.fullScreenCover` too. On iOS 26, developers have reported (Apple Developer Forums thread 807208) a regression where drag-dismiss briefly misaligns geometry — worth testing on the target OS.

### 3.6 UIKit equivalents

`UIView.transition(with:duration:options:animations:completion:)` for simple crossfades and flips; `UIViewControllerAnimatedTransitioning` + `UIPercentDrivenInteractiveTransition` for custom navigation/modal transitions; on iOS 18+, you also get the platform zoom transition via standard navigation APIs when you opt in.

---

## 4. Phase and keyframe animations (iOS 17+)

Both APIs were introduced in WWDC 2023 session **10157 "Wind your way through advanced animations in SwiftUI"**. They solve cases where a two-state interpolation isn't enough.

### 4.1 `phaseAnimator` — discrete phases

```swift
// Continuously loops through the phase sequence
func phaseAnimator<Phase: Equatable>(
    _ phases: some Sequence<Phase>,
    @ViewBuilder content: @escaping (PlaceholderContentView<Self>, Phase) -> some View,
    animation: @escaping (Phase) -> Animation? = { _ in .default }
) -> some View

// Plays the sequence once per trigger change
func phaseAnimator<Phase: Equatable>(
    _ phases: some Sequence<Phase>,
    trigger: some Equatable,
    @ViewBuilder content: @escaping (PlaceholderContentView<Self>, Phase) -> some View,
    animation: @escaping (Phase) -> Animation? = { _ in .default }
) -> some View
```

All animated properties move **together** between any two adjacent phases. When one phase transition completes, SwiftUI animates to the next.

```swift
// Attention-getter — continuously pulsing dot
Circle().fill(.red).frame(width: 40, height: 40)
    .phaseAnimator([false, true]) { view, on in
        view.scaleEffect(on ? 1.2 : 1.0).opacity(on ? 1.0 : 0.6)
    } animation: { _ in
        .easeInOut(duration: 0.6)
    }
```

```swift
// Triggered three-phase — "Tap Me!" reaction
enum Phase: CaseIterable { case start, middle, end }
@State private var step = 0

Button("Tap Me!") { step += 1 }
    .phaseAnimator(Phase.allCases, trigger: step) { content, phase in
        content
            .blur(radius: phase == .start ? 0 : 10)
            .scaleEffect(phase == .middle ? 3 : 1)
    } animation: { phase in
        switch phase {
        case .start, .end: .bouncy
        case .middle:      .easeInOut(duration: 2)
        }
    }
```

### 4.2 `keyframeAnimator` — multi-track, time-based

```swift
// Plays once per trigger change
func keyframeAnimator<Value>(
    initialValue: Value,
    trigger: some Equatable,
    @ViewBuilder content: @escaping (PlaceholderContentView<Self>, Value) -> some View,
    @KeyframesBuilder<Value> keyframes: @escaping (Value) -> some Keyframes<Value>
) -> some View

// Loops continuously
func keyframeAnimator<Value>(
    initialValue: Value,
    repeating: Bool = true,
    @ViewBuilder content: @escaping (PlaceholderContentView<Self>, Value) -> some View,
    @KeyframesBuilder<Value> keyframes: @escaping (Value) -> some Keyframes<Value>
) -> some View
```

You declare a `Value` struct of animatable properties; each property lives on its own `KeyframeTrack`, each with its own timeline.

Keyframe types:

- `LinearKeyframe(value, duration:, timingCurve:)` — constant-speed.
- `CubicKeyframe(value, duration:, startVelocity:, endVelocity:)` — smooth cubic Bézier.
- `SpringKeyframe(value, duration:, spring:, startVelocity:)` — physics spring.
- `MoveKeyframe(value)` — teleport; no interpolation.

The canonical WWDC 2023 example — a reaction that rotates, stretches, scales, and translates in parallel:

```swift
struct AnimationValues {
    var scale = 1.0
    var verticalStretch = 1.0
    var verticalTranslation = 0.0
    var angle = Angle.zero
}

ReactionView()
    .keyframeAnimator(initialValue: AnimationValues()) { content, v in
        content
            .rotationEffect(v.angle)
            .scaleEffect(v.scale)
            .scaleEffect(y: v.verticalStretch)
            .offset(y: v.verticalTranslation)
    } keyframes: { _ in
        KeyframeTrack(\.angle) {
            CubicKeyframe(.zero,          duration: 0.58)
            CubicKeyframe(.degrees( 16),  duration: 0.125)
            CubicKeyframe(.degrees(-16),  duration: 0.125)
            CubicKeyframe(.degrees( 16),  duration: 0.125)
            CubicKeyframe(.zero,          duration: 0.125)
        }
        KeyframeTrack(\.verticalStretch) {
            CubicKeyframe(1.0,  duration: 0.1)
            CubicKeyframe(0.6,  duration: 0.15)
            CubicKeyframe(1.5,  duration: 0.1)
            CubicKeyframe(1.05, duration: 0.15)
            CubicKeyframe(1.0,  duration: 0.88)
        }
        KeyframeTrack(\.scale) {
            LinearKeyframe(1.0, duration: 0.36)
            SpringKeyframe(1.5, duration: 0.8, spring: .bouncy)
            SpringKeyframe(1.0, spring: .bouncy)
        }
        KeyframeTrack(\.verticalTranslation) {
            LinearKeyframe(0,   duration: 0.1)
            SpringKeyframe(20,  duration: 0.15, spring: .bouncy)
            SpringKeyframe(-60, duration: 1.0,  spring: .bouncy)
            SpringKeyframe(0,   spring: .bouncy)
        }
    }
```

Tracks are **independent** — each property has its own timeline; SwiftUI advances them in parallel. `KeyframeTimeline` exposes `duration` and `value(time:)` so you can sample keyframes from a gesture offset or scroll position to build scrubbable effects.

### 4.3 Phase vs. keyframe — which to use

| Concern | `phaseAnimator` | `keyframeAnimator` |
|---|---|---|
| Mental model | Discrete **states** you cycle through | Continuous **tracks** of values over time |
| Timing | One animation per phase transition, chosen per phase | Fixed durations per segment, per track |
| Multiple properties | All animate together between adjacent phases | Each property is independent |
| Looping | Built-in (continuous variant) | `repeating: true` |
| Great for | Pulses, breathing indicators, attention-getters, simple reveal sequences | Choreographed multi-property animations, icon reactions, complex reveals |
| Scrubbable | No | Yes, via `KeyframeTimeline` |

---

## 5. Implicit vs. explicit — and where implicit animation bites

### 5.1 The mental model

Everything is a **transaction**. `withAnimation { ... }` is sugar for `withTransaction(Transaction(animation: …)) { ... }`, propagating the animation from the SwiftUI root through every affected view. `.animation(_:value:)` rewrites the transaction on its way down a specific subtree. **Precedence**: an implicit `.animation` on a child overrides an ancestor's, because it rewrites the inbound transaction.

### 5.2 The classic implicit bug

The original `.animation(_:)` (no value) animates *any* change in the subtree — including changes you didn't cause:

- Keyboard-avoidance safe-area insets pushing views up.
- Environment-value changes (color scheme, dynamic type, size class).
- Parent layout shifts.
- Orientation rotations.

Typical bug: attach `.animation(.default)` to a `VStack` containing a `TextField`. When the keyboard appears, iOS already animates safe-area changes; your modifier piles a second animation on top, producing a fight or a doubled spring. The fix is to scope with `value:`:

```swift
VStack {
    HugeView().opacity(isHidden ? 0 : 1)
    AnotherHugeView()
}
.animation(.default, value: isHidden)
```

The iOS 17+ `ViewBuilder`-scoped form is the cleanest — it applies only to modifiers inside the closure, nothing outside.

### 5.3 `.transaction` for fine control

```swift
// Speed up inherited animation
SomeView().transaction { t in t.animation = t.animation?.speed(2) }

// Kill inherited animation
ImportantView().transaction { t in t.animation = nil }

// Override inside a gesture
DragGesture()
    .updating($offset) { value, state, transaction in
        state = value.translation
        transaction.animation = .interactiveSpring()
    }
```

### 5.4 When to use which

| Situation | Prefer |
|---|---|
| Tap/button/gesture handler triggers state change | **Explicit** `withAnimation` — siblings without their own `.animation` also animate |
| Animation bound to a single piece of state | **Implicit** `.animation(_:value:)` on the leaf view |
| Multiple properties with different timings | Multiple `.animation(_:value:)` modifiers, one per value |
| Tight scoping to a few modifiers | **iOS 17+ `.animation(_:body:)`** form |
| Gesture `.updating` / binding updates | `transaction.animation` inside the update closure |
| Need to block an ancestor's animation | `.transaction { $0.animation = nil }` on the child |

---

## 6. Timing and duration

### 6.1 Apple's de-facto standard durations

| Duration | Use |
|---|---|
| **0.2 s** | Small, quick feedback: button press, icon scale, popover appear |
| **0.3 s** | Typical state transitions: toggle, list insert, minor layout |
| **0.5 s** | Larger spatial transitions: sheet, navigation push, view morph. Also the default duration for `.smooth/.snappy/.bouncy` |

Timing-curve presets (`.linear`, `.easeInOut`) default to **0.35 s**. Apple's HIG "Motion" page frames this as: *"Prefer quick, precise animations. Animations that combine brevity and precision tend to feel more lightweight and less intrusive."*

### 6.2 Perception thresholds

- **< 100 ms** reads as instantaneous; animation adds little value.
- **100–200 ms** is crisp tap feedback.
- **200–500 ms** is the responsive and intuitive band — most UI lives here.
- **> 500 ms** feels deliberately slow; only for large spatial transitions.
- **> 1 s** only for onboarding or narrative moments.

### 6.3 When to deviate

- **Distance traveled**: a 800 pt slide needs longer than a 40 pt one — scale duration roughly logarithmically, not linearly.
- **Frequency**: actions repeated many times per session deserve shorter durations (0.15 s is fine for a row check toggle).
- **Surface size**: inline chips stay ≤ 0.2 s; full-screen transitions can justify 0.4–0.6 s.
- **Emotional weight**: celebratory success moments can stretch to 0.6–0.7 s because they're *meant* to pull attention.
- **Continuous gestures**: use `.interactiveSpring()` during the drag for minimum latency; switch to `.smooth`/`.snappy` on release.

### 6.4 HIG caution

The HIG specifically warns about oscillating motions with large amplitudes at frequencies around 0.2 Hz (one oscillation per 5 s) — a known vestibular-disorder and migraine trigger. Keep repeating bounces above 0.5 Hz and amplitudes modest.

---

## 7. Reduce Motion — what to preserve, what to replace

Reduce Motion is a user accessibility setting (Settings → Accessibility → Motion → Reduce Motion) for vestibular disorders, motion sensitivity, and cognitive challenges. It is **not** "remove all animation" — per Apple's App Store Connect Reduced Motion evaluation criteria and HIG, you should **substitute** motion-heavy animations with lower-motion equivalents (typically opacity crossfades), not delete them.

A companion setting, **Prefer Cross-Fade Transitions** (iOS 14+), appears only when Reduce Motion is on and expresses an even stronger preference for pure crossfades.

### 7.1 APIs

SwiftUI:

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion   // Bool
```

UIKit:

```swift
UIAccessibility.isReduceMotionEnabled          // Bool, iOS 8+
UIAccessibility.prefersCrossFadeTransitions    // Bool, iOS 14+

// Observe
NotificationCenter.default.addObserver(
    self,
    selector: #selector(reduceMotionChanged),
    name: UIAccessibility.reduceMotionStatusDidChangeNotification,
    object: nil
)
```

**Known Apple bug**: `UIAccessibility.prefersCrossFadeTransitionsStatusDidChangeNotification` does not reliably fire when the setting toggles. Poll `prefersCrossFadeTransitions` in `viewWillAppear` or on app foregrounding as a fallback.

### 7.2 Degradation table

| Offending animation | Replacement under Reduce Motion |
|---|---|
| Slide / push / `.move(edge:)` | Opacity crossfade (`.opacity`) |
| Zoom navigation (iOS 18 `.zoom`) | System auto-degrades; audit custom zooms |
| Parallax backgrounds, tilt effects, `UIInterpolatingMotionEffect` | Remove offset entirely |
| Spring with `bounce > 0` | `.easeInOut` (short) or `nil` |
| `.scale` transition | `.opacity` |
| Offset transitions | `.opacity` |
| Repeating rotation / pulsing | Stop after first cycle or render static |
| Autoplay hero video / Lottie | Pause; show static poster |
| Confetti / particles | Static success icon + haptic |
| Screen shake / jiggle | Haptic + brief color flash |

### 7.3 Preserve these even with Reduce Motion on

- Short button-tap scale feedback (< 150 ms).
- State-change confirmations (checkmark draw-in, toggle thumb slide).
- Focus indicators — VoiceOver focus ring, keyboard focus ring.
- Loading / progress indicators.
- `.symbolEffect(.replace)` icon state changes.
- Number tickers and content transitions where the motion *is* the meaning.

Rule of thumb: if removing the animation would make the app *less* understandable, substitute a non-translational equivalent; never delete.

### 7.4 Code patterns

```swift
// Conditional animation
@Environment(\.accessibilityReduceMotion) private var reduceMotion

.animation(
    reduceMotion ? .easeInOut(duration: 0.12)
                 : .spring(response: 0.4, dampingFraction: 0.5),
    value: scale
)

// Transition degradation
var transition: AnyTransition {
    reduceMotion ? .opacity
                 : .move(edge: .trailing).combined(with: .opacity)
}

// Helper that bypasses animation
func withOptionalAnimation<R>(_ animation: Animation? = .default,
                              _ body: () throws -> R) rethrows -> R {
    if UIAccessibility.isReduceMotionEnabled { return try body() }
    return try withAnimation(animation, body)
}

Button("Tap") { withOptionalAnimation(.spring()) { scale *= 1.5 } }
```

### 7.5 Reduce Motion developer checklist

1. Read `@Environment(\.accessibilityReduceMotion)` in every view that drives a custom animation.
2. In UIKit, observe `reduceMotionStatusDidChangeNotification` and re-evaluate on foregrounding.
3. Replace slide/push/move transitions with opacity crossfades.
4. Replace spring bounces with short `.easeInOut` or `nil`.
5. Disable parallax — scroll-linked background offsets, tilt-reactive motion, `UIInterpolatingMotionEffect`.
6. Disable autoplay video, Lottie loops, confetti, particles, camera flybys; require explicit user action.
7. Stop `.repeatForever` loops; render the end state statically.
8. Preserve essential feedback — button press, toggle, focus ring, progress, symbol replace.
9. For meaning-carrying motion (add to cart, delete row), **substitute** a dissolve/highlight — never just delete.
10. Check `UIAccessibility.prefersCrossFadeTransitions` and prefer `crossDissolve` modal style when true.
11. Audit iOS 18 `.navigationTransition(.zoom(...))` and custom `matchedTransitionSource` usage with Reduce Motion on.
12. Don't add competing motion on top of Liquid Glass elements — they tone themselves down automatically.
13. Never gate critical info behind animation (don't make status changes visible only through motion).
14. Test with Reduce Motion ON, RM + Prefer Cross-Fade ON, and RM + Reduce Transparency ON — three separate passes.
15. Consider short haptics (`UIImpactFeedbackGenerator`) to substitute for removed motion.
16. Answer Apple's Accessibility Nutrition Label "Reduced Motion" criteria before App Store submission.
17. Never expose an in-app toggle that *overrides* the user's system setting without a strong reason.

---

## 8. Liquid Glass motion (iOS 26)

Liquid Glass, introduced at **WWDC 2025 session 219 "Meet Liquid Glass"**, is a new refractive meta-material for iOS 26, iPadOS 26, macOS Tahoe 26, watchOS 26, tvOS 26, and visionOS 26. It lives in the **navigation and control layer** — never in content — and its motion is almost entirely system-driven.

### 8.1 What Liquid Glass is doing, optically and kinetically

- **Lensing**: refracts and concentrates light along shape edges — the opposite of blur.
- **Specular highlights**: surface reflections that respond to device tilt and underlying scroll content.
- **Materialization**: elements appear by modulating light bending instead of fading.
- **Fluidity**: elastic, gel-like touch response.
- **Morphing**: shapes physically transform between control states — no fade, the material continuously reshapes.
- **Adaptivity**: tint, contrast, and shadow adjust based on the content behind and in front.
- **Depth shift**: as a button flexes into a menu, material characteristics deepen — thicker glass, softer light scatter.

Motion timing defaults to springy behavior that the system controls. You drive the *state* (what's visible, where); you wrap the state change in `withAnimation(.bouncy)` or `.spring`; Liquid Glass handles the morph.

### 8.2 Core SwiftUI APIs

```swift
// Apply Liquid Glass to a view
func glassEffect(
    _ glass: Glass = .regular,
    in shape: some Shape = Capsule(),
    isEnabled: Bool = true
) -> some View

// Glass variants
struct Glass {
    static var regular: Glass
    static var clear: Glass          // high transparency — needs media-rich bg + bold fg
    static var identity: Glass       // no-op, for conditional toggling
    func tint(_ color: Color) -> Glass
    func interactive(_ isInteractive: Bool = true) -> Glass
}

// Group glass elements so they share sampling and can morph
struct GlassEffectContainer<Content: View>: View {
    init(spacing: CGFloat? = nil, @ViewBuilder content: () -> Content)
}

// Stable identity for morph continuity across state changes
func glassEffectID<ID: Hashable>(_ id: ID, in namespace: Namespace.ID) -> some View

// Force distant glass elements to render as one shape
func glassEffectUnion<ID: Hashable>(id: ID, namespace: Namespace.ID) -> some View

// Customize the insertion/removal transition (exact cases: verify against Xcode 26 headers)
func glassEffectTransition(_ transition: GlassEffectTransition,
                           isEnabled: Bool = true) -> some View
```

Button styles and related modifiers: `.buttonStyle(.glass)`, `.buttonStyle(.glassProminent)` (automatic for `.confirmationAction`), `.controlSize(.extraLarge)`, `.buttonBorderShape(.circle)`.

Tab and toolbar extensions: `.tabBarMinimizeBehavior(.onScrollDown)`, `.tabViewBottomAccessory { … }`, `@Environment(\.tabViewBottomAccessoryPlacement)`, `ToolbarSpacer(.fixed, spacing:)`, `.sharedBackgroundVisibility(.hidden)`.

UIKit equivalents in iOS 26:

```swift
let glass = UIGlassEffect(glass: .regular, isInteractive: true)
let view  = UIVisualEffectView(effect: glass)

let container = UIGlassContainerEffect()
let containerView = UIVisualEffectView(effect: container)
```

### 8.3 The canonical morphing pattern

This is the Liquid Glass equivalent of `matchedGeometryEffect` — a cluster of action buttons that expand from a primary control, morphing as one gel-like shape.

```swift
struct ExpandingActions: View {
    @State private var expanded = false
    @Namespace private var ns

    var body: some View {
        GlassEffectContainer(spacing: 30) {
            HStack(spacing: 16) {
                if expanded {
                    Button { } label: { Image(systemName: "camera") }
                        .glassEffect(.regular.interactive())
                        .glassEffectID("camera", in: ns)

                    Button { } label: { Image(systemName: "photo") }
                        .glassEffect(.regular.interactive())
                        .glassEffectID("photo", in: ns)
                }

                Button {
                    withAnimation(.bouncy) { expanded.toggle() }
                } label: {
                    Image(systemName: expanded ? "xmark" : "plus")
                        .frame(width: 44, height: 44)
                }
                .buttonStyle(.glassProminent)
                .buttonBorderShape(.circle)
                .glassEffectID("toggle", in: ns)
            }
        }
    }
}
```

### 8.4 Rules for clean morphing

- All morphing participants must live in the **same `GlassEffectContainer`**.
- Each must carry a **`glassEffectID`** in a **shared `@Namespace`**.
- State changes must be wrapped in **`withAnimation`** (`.bouncy` or `.spring` recommended).
- All participants must use the **same glass variant** (all `.regular` or all `.clear`).
- Never stack glass on glass — it breaks sampling and morph.

### 8.5 Customize system motion — only what you control

You never write a timing curve for the material. You control:

- **When** state changes happen (`withAnimation(.bouncy)`).
- **Grouping** via `GlassEffectContainer(spacing:)` — larger spacing, more aggressive merging.
- **Identity continuity** via `glassEffectID`.
- **Interactive feel** via `.interactive()` — toggles scale / bounce / shimmer.
- **Tint, shape, variant**.

### 8.6 What you get for free by recompiling with Xcode 26

Liquid Glass and its morph animations are adopted automatically by `NavigationStack`/`NavigationSplitView` toolbars and sidebars, `TabView` (with `.onScrollDown` minimize animation), sheets, popovers, menus, alerts, search bars, Control Center-style toggles, sliders, and pickers.

### 8.7 Reduce Motion and Liquid Glass

Accessibility is automatic. Apple's guidance (sessions 219 and 323) is to **let the system handle it**. Elastic bounce is toned down; specular highlights damp; morph becomes a simpler cross-fade-like replacement under Reduce Motion. Under Reduce Transparency, the material becomes frostier and more opaque. Under Increase Contrast, stark colors and visible borders appear. iOS 26.1 adds a user-controlled "Tinted" Liquid Glass mode (Settings → Display & Brightness).

Only intervene if necessary:

```swift
@Environment(\.accessibilityReduceTransparency) var reduceTransparency

Text("Adaptive")
    .padding()
    .glassEffect(reduceTransparency ? .identity : .regular)
```

### 8.8 Known iOS 26 quirks (as of April 2026)

- `.glassEffect(.regular.interactive(), in: RoundedRectangle())` may snap to Capsule on early 26.0 builds — use `.buttonStyle(.glass)`.
- `.glassProminent` + `.buttonBorderShape(.circle)` shows rendering artifacts on some betas; `clipShape(Circle())` fixes it.
- On iOS 26.1, a `Menu` inside `GlassEffectContainer` can break morph — put `.glassEffect(.regular.interactive())` directly on the `Menu` instead.
- `GlassEffectTransition` case spellings vary across community docs — verify against live Xcode 26 headers.
- Battery and thermal impact is higher than iOS 18 on iPhone 11–13 class hardware; profile on oldest supported device.

Backporting pattern for mixed-OS codebases:

```swift
extension View {
    @ViewBuilder
    func backportGlass<S: Shape>(in shape: S = Capsule()) -> some View {
        if #available(iOS 26, *) {
            self.glassEffect(.regular, in: shape)
        } else {
            self.background(shape.fill(.ultraThinMaterial))
        }
    }
}
```

---

## 9. Scroll-driven animations (iOS 17+)

Two complementary APIs: `.scrollTransition` (declarative, three-phase) and `.visualEffect` (imperative, full geometry access).

### 9.1 `.scrollTransition`

```swift
func scrollTransition(
    _ configuration: ScrollTransitionConfiguration = .interactive,
    axis: Axis = .vertical,
    transition: @escaping (EmptyVisualEffect, ScrollTransitionPhase) -> some VisualEffect
) -> some View

func scrollTransition(
    topLeading: ScrollTransitionConfiguration,
    bottomTrailing: ScrollTransitionConfiguration,
    axis: Axis = .vertical,
    transition: @escaping (EmptyVisualEffect, ScrollTransitionPhase) -> some VisualEffect
) -> some View

enum ScrollTransitionPhase {
    case topLeading        // -1: about to enter
    case identity          //  0: fully visible
    case bottomTrailing    // +1: leaving
    var isIdentity: Bool
    var value: Double      // -1 / 0 / +1
}
```

Configurations: `.interactive`, `.animated`, chainable via `.threshold(...)` and `.animation(...)`.

```swift
// Fade and scale on appear
ScrollView {
    ForEach(0..<20) { _ in
        RoundedRectangle(cornerRadius: 25).fill(.blue).frame(height: 80)
            .scrollTransition(.animated.threshold(.visible(0.9))) { content, phase in
                content
                    .opacity(phase.isIdentity ? 1 : 0)
                    .scaleEffect(phase.isIdentity ? 1 : 0.75)
                    .blur(radius: phase.isIdentity ? 0 : 10)
            }
            .padding(.horizontal)
    }
}
```

```swift
// Hue shift driven by continuous phase.value
.scrollTransition { content, phase in
    content.hueRotation(.degrees(phase.value * 120))
}

// Asymmetric entry vs. exit
.scrollTransition(topLeading: .interactive,
                  bottomTrailing: .animated) { content, phase in
    content.opacity(phase.isIdentity ? 1 : 0.3)
           .scaleEffect(phase.isIdentity ? 1 : 0.85)
}
```

### 9.2 `.visualEffect`

```swift
func visualEffect(
    _ effect: @escaping (EmptyVisualEffect, GeometryProxy) -> some VisualEffect
) -> some View
```

Critical property: `.visualEffect` **cannot affect layout** — no `.frame`, no position writes that feed back into layout. It can change `.offset`, `.scale`, `.rotation`, `.blur`, color effects. This makes it strictly faster than `GeometryReader`, because no layout feedback loop occurs.

```swift
// Blur by distance from scroll-view center
ScrollView {
    ForEach(0..<100) { i in
        Text("Row \(i)")
            .font(.largeTitle)
            .frame(maxWidth: .infinity)
            .visualEffect { content, proxy in
                let h = proxy.bounds(of: .scrollView)?.height ?? 100
                let y = proxy.frame(in: .scrollView).midY
                return content.blur(radius: abs(h/2 - y) / 100)
            }
    }
}
```

`proxy.bounds(of: .scrollView)` and `proxy.frame(in: .scrollView)` (both iOS 17+) are the key primitives.

### 9.3 Parallax header, built from `.visualEffect`

```swift
ScrollView {
    Image("hero")
        .resizable().scaledToFill()
        .frame(height: 300).clipped()
        .visualEffect { content, proxy in
            let y = proxy.frame(in: .scrollView).minY
            return content
                .offset(y: y > 0 ? -y / 2 : 0)               // drift at half-speed
                .scaleEffect(y > 0 ? 1 + y / 500 : 1,        // stretchy hero
                             anchor: .top)
        }
    ArticleBody()
}
```

### 9.4 Paging, target behavior, and container-relative frames

```swift
func containerRelativeFrame(_ axes: Axis.Set, alignment: Alignment = .center) -> some View
func scrollTargetLayout(isEnabled: Bool = true) -> some View
func scrollTargetBehavior(_ behavior: some ScrollTargetBehavior) -> some View
// built-ins: .viewAligned, .paging
```

TikTok-style full-screen paging in 20 lines:

```swift
ScrollView(.vertical) {
    LazyVStack(spacing: 0) {
        ForEach(videos) { video in
            VideoTile(video: video)
                .containerRelativeFrame([.horizontal, .vertical])
        }
    }
    .scrollTargetLayout()
}
.scrollTargetBehavior(.paging)
.ignoresSafeArea()
```

### 9.5 When to pick which

Use `.scrollTransition` when the stock three-phase `-1 / 0 / +1` model suffices. Drop to `.visualEffect` for custom math — distance-from-center, non-linear ratios, geometry pulled from the enclosing scroll view — or when you need both scroll and non-scroll geometry in the same formula.

---

## 10. Gesture-driven animations

### 10.1 `DragGesture.Value` — everything you need for momentum

- `translation: CGSize` — offset from start.
- `velocity: CGSize` — instantaneous velocity (iOS 17+).
- `predictedEndLocation: CGPoint` and `predictedEndTranslation: CGSize` — where the finger would end up if released now, extrapolated from velocity. Apple uses the same math as `UIScrollView` internally.

### 10.2 `@GestureState` vs. `@State`

- `@GestureState` resets to its initial value the instant the gesture ends. Use it for the live "offset while finger is down" value; a `.animation(_:value:)` modifier then springs cleanly back to rest.
- `@State` persists after the gesture ends. Use it for committed positions that the user's release confirmed.

### 10.3 `.interactiveSpring()` during a gesture; a heavier spring on release

`.interactiveSpring()` (response 0.15 s, dampingFraction 0.86) is tuned to track a finger with minimal lag. Use it inside `.updating`/`.onChanged`. On `.onEnded`, switch to `.spring`, `.bouncy`, or `.snappy` — the target is now a committed value and the spring's velocity continuity picks up right where the finger left off.

### 10.4 Draggable card with snap-back

```swift
struct DraggableCard: View {
    @GestureState private var dragOffset: CGSize = .zero
    @State private var committedOffset: CGSize = .zero

    var body: some View {
        RoundedRectangle(cornerRadius: 20).fill(.tint)
            .frame(width: 240, height: 320).shadow(radius: 10)
            .offset(x: committedOffset.width + dragOffset.width,
                    y: committedOffset.height + dragOffset.height)
            .gesture(
                DragGesture()
                    .updating($dragOffset) { value, state, _ in
                        state = value.translation
                    }
                    .onEnded { _ in
                        withAnimation(.spring(response: 0.45, dampingFraction: 0.7)) {
                            committedOffset = .zero
                        }
                    }
            )
            .animation(.interactiveSpring(response: 0.15,
                                          dampingFraction: 0.86,
                                          blendDuration: 0.25),
                       value: dragOffset)
    }
}
```

### 10.5 Velocity-driven commit using `Spring` math

```swift
struct SwipeToDismissCard: View {
    @GestureState private var drag: CGSize = .zero
    @State private var committed: CGSize = .zero
    @State private var dismissed = false

    var body: some View {
        let spring = Spring(duration: 0.45, bounce: 0.15)

        RoundedRectangle(cornerRadius: 24).fill(.blue)
            .frame(width: 280, height: 380)
            .offset(x: committed.width + drag.width,
                    y: committed.height + drag.height)
            .opacity(dismissed ? 0 : 1)
            .gesture(
                DragGesture()
                    .updating($drag) { value, state, _ in state = value.translation }
                    .onEnded { value in
                        let vx = value.velocity.width
                        let predicted = value.predictedEndTranslation.width
                        let threshold: CGFloat = 150

                        if abs(predicted) > threshold {
                            withAnimation(.spring(response: 0.35, dampingFraction: 0.9)) {
                                committed.width = predicted > 0 ? 800 : -800
                                dismissed = true
                            }
                        } else {
                            withAnimation(.interpolatingSpring(
                                mass: 1, stiffness: 170, damping: 18,
                                initialVelocity: Double(vx / 100))) {
                                committed = .zero
                            }
                        }
                        let settle = spring.settlingDuration(target: CGFloat(0),
                                                             initialVelocity: vx,
                                                             epsilon: 0.5)
                        print("settles in ~\(settle)s")
                    }
            )
    }
}
```

### 10.6 Rubber-banding — the UIScrollView formula

The canonical resistance function (constant `c = 0.55` matches `UIScrollView`):

```
f(x, d, c) = (x · d · c) / (d + c · x)
```

- `x` — raw overshoot distance.
- `d` — container dimension.
- `c` — stiffness (0.55 for Apple's feel).

```swift
func rubberBand(offset x: CGFloat, dimension d: CGFloat, coefficient c: CGFloat = 0.55) -> CGFloat {
    guard d > 0 else { return 0 }
    let sign: CGFloat = x < 0 ? -1 : 1
    let absX = abs(x)
    return sign * (absX * d * c) / (d + c * absX)
}
```

Apply the function to the gesture's raw translation before driving the offset; feed the result into an `.interactiveSpring()` during drag, and either commit or snap back on release.

### 10.7 UIKit — `UIPanGestureRecognizer` + `UIViewPropertyAnimator`

The canonical interruptible-drawer pattern from WWDC 2017 session 230:

```swift
class InstantPanGestureRecognizer: UIPanGestureRecognizer {
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent) {
        super.touchesBegan(touches, with: event)
        self.state = .began          // report .began immediately so in-flight animations can pause
    }
}

@objc func popupViewPanned(_ recognizer: UIPanGestureRecognizer) {
    switch recognizer.state {
    case .began:
        animateOrReverse(to: currentState == .closed ? .open : .closed, duration: 1)
        runningAnimators.forEach { $0.pauseAnimation() }
        progressWhenInterrupted = runningAnimators.first?.fractionComplete ?? 0

    case .changed:
        let translation = recognizer.translation(in: drawer)
        var fraction = -translation.y / popupOffset
        if currentState == .open { fraction *= -1 }
        if runningAnimators.first?.isReversed == true { fraction *= -1 }
        runningAnimators.forEach { $0.fractionComplete = fraction + progressWhenInterrupted }

    case .ended:
        let yVel = recognizer.velocity(in: drawer).y
        // decide reverse vs. continue based on velocity direction, then:
        let relVel = abs(yVel) / popupOffset
        let timing = UISpringTimingParameters(
            dampingRatio: 0.8,
            initialVelocity: CGVector(dx: relVel, dy: relVel)
        )
        runningAnimators.forEach {
            $0.continueAnimation(withTimingParameters: timing, durationFactor: 0)
        }

    default: break
    }
}
```

Three rules from session 230: `pauseAnimation()` on `.began` to capture `fractionComplete`; scrub by writing `fractionComplete` on `.changed`; on `.ended`, call `continueAnimation(withTimingParameters:durationFactor:)` with a new `UISpringTimingParameters` whose `initialVelocity` is **normalized** (gesture velocity ÷ remaining distance).

### 10.8 SwiftUI sheet interactive dismiss

`.sheet` (iOS 15+) gives you swipe-to-dismiss for free. Control it with `.interactiveDismissDisabled(true)`, `.presentationDragIndicator(.visible)`, `.presentationDetents([.medium, .large])` (iOS 16+), and `.presentationBackgroundInteraction(.enabled(upThrough: .medium))` (iOS 16.4+).

---

## 11. UIKit and Core Animation equivalents

### 11.1 `UIView.animate` family

```swift
// Basic
class func animate(withDuration: TimeInterval,
                   animations: @escaping () -> Void)

class func animate(withDuration: TimeInterval,
                   delay: TimeInterval,
                   options: UIView.AnimationOptions = [],
                   animations: @escaping () -> Void,
                   completion: ((Bool) -> Void)? = nil)

// iOS 7+ spring (damping ratio)
class func animate(withDuration: TimeInterval,
                   delay: TimeInterval,
                   usingSpringWithDamping dampingRatio: CGFloat,
                   initialSpringVelocity velocity: CGFloat,
                   options: UIView.AnimationOptions = [],
                   animations: @escaping () -> Void,
                   completion: ((Bool) -> Void)? = nil)

// iOS 17+ — same duration/bounce model as SwiftUI's Spring
@available(iOS 17.0, *)
@MainActor class func animate(springDuration: TimeInterval = 0.5,
                              bounce: CGFloat = 0.0,
                              initialSpringVelocity: CGFloat = 0.0,
                              delay: TimeInterval = 0.0,
                              options: UIView.AnimationOptions = [],
                              animations: () -> Void,
                              completion: ((Bool) -> Void)? = nil)

// Keyframes
class func animateKeyframes(withDuration: TimeInterval, delay: TimeInterval,
                            options: UIView.KeyframeAnimationOptions = [],
                            animations: @escaping () -> Void,
                            completion: ((Bool) -> Void)? = nil)

class func addKeyframe(withRelativeStartTime: Double,
                       relativeDuration: Double,
                       animations: @escaping () -> Void)

// Transitions (flip, crossfade, etc.)
class func transition(with view: UIView,
                      duration: TimeInterval,
                      options: UIView.AnimationOptions = [],
                      animations: (() -> Void)?,
                      completion: ((Bool) -> Void)? = nil)
```

### 11.2 `UIViewPropertyAnimator` (iOS 10+)

Interruptible, reversible, scrubbable animations — always prefer this for anything gesture-driven.

```swift
let animator = UIViewPropertyAnimator(duration: 0.4, dampingRatio: 0.85) {
    view.center.y -= 200
}
animator.startAnimation()

// Scrub
animator.pauseAnimation()
animator.fractionComplete = 0.5

// Reverse
animator.isReversed.toggle()

// Continue with velocity
let timing = UISpringTimingParameters(
    dampingRatio: 0.8,
    initialVelocity: CGVector(dx: relVelocity, dy: relVelocity)
)
animator.continueAnimation(withTimingParameters: timing, durationFactor: 0)
```

Key knobs: `state` (`.inactive` / `.active` / `.stopped`), `isRunning`, `isReversed`, `fractionComplete`, `pausesOnCompletion` (iOS 11+), `scrubsLinearly` (iOS 11+), `isInterruptible`.

Timing providers:

```swift
UICubicTimingParameters(animationCurve: .easeInOut)
UICubicTimingParameters(controlPoint1: .init(x: 0.2, y: 0), controlPoint2: .init(x: 0.0, y: 1))
UISpringTimingParameters(dampingRatio: 0.8, initialVelocity: CGVector(dx: 2, dy: 0))
UISpringTimingParameters(mass: 1, stiffness: 220, damping: 12, initialVelocity: .zero)
```

**Important**: `initialVelocity` for `UISpringTimingParameters` (and the old `initialSpringVelocity:` parameter) is **normalized**: units are `1 / (remaining_distance_in_seconds)`. If the finger moves 800 pt/s and the spring will travel 400 pt, magnitude is `800 / 400 = 2.0`.

### 11.3 Core Animation — `CABasicAnimation`, `CAKeyframeAnimation`, `CASpringAnimation`

```swift
let slide = CABasicAnimation(keyPath: "position.x")
slide.fromValue = view.layer.position.x
slide.toValue   = view.layer.position.x + 200
slide.duration  = 0.4
slide.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
slide.fillMode = .forwards
slide.isRemovedOnCompletion = false
view.layer.add(slide, forKey: "slide")
view.layer.position.x += 200                  // always update the model value too

// Path-based keyframe
let anim = CAKeyframeAnimation(keyPath: "position")
anim.path = path.cgPath
anim.duration = 1.2
anim.calculationMode = .paced                  // constant velocity
anim.rotationMode = .rotateAuto                // orient to tangent
icon.layer.add(anim, forKey: "arc")

// CASpringAnimation — make sure duration = settlingDuration, or the bounce clips
let spring = CASpringAnimation(keyPath: "transform.scale")
spring.fromValue = 1.0
spring.toValue   = 1.2
spring.damping   = 12
spring.stiffness = 220
spring.mass      = 1
spring.duration  = spring.settlingDuration
button.layer.add(spring, forKey: "tapBounce")
```

Group with `CAAnimationGroup`; swap layer contents with `CATransition`.

### 11.4 When to drop down to Core Animation

Drop down when you need to animate properties UIKit's animation blocks don't cover, or when you need behavior only CA provides.

| Situation | Why CA |
|---|---|
| `shadowPath`, `cornerRadius` on sublayers, `mask`, `strokeEnd`, gradient `locations`, `filter`, `contentsRect` | `UIView.animate` only animates a curated subset; everything on `CALayer` is fair game |
| Path-following motion | Only `CAKeyframeAnimation.path` does this |
| Shape / checkmark / progress ring drawing | `CAShapeLayer.strokeStart`, `strokeEnd`, `path` |
| Per-segment timing functions | `CAKeyframeAnimation.timingFunctions` |
| Particle / decorative systems | `CAEmitterLayer`, `CAEmitterCell` |
| Main-thread–independent rendering | CA runs on the render server |
| Animations that must continue while the main thread is busy | Same reason |

### 11.5 Why not always use CA?

CA detaches the model value from the presentation layer — you must always update the model alongside the animation (or use `fillMode = .forwards` + `isRemovedOnCompletion = false`, with its own caveats). You lose automatic layout integration. The SwiftUI → UIKit → CA ladder is a sequence of escape hatches, not defaults: go down a rung only when the rung above can't do what you need.

---

## 12. Anti-patterns — things that make animations bad

### 12.1 Gratuitous animation

Apple HIG: *"Don't add motion for the sake of adding motion."* Every animation in a productivity surface should communicate something — state change, hierarchy, causation — not decorate.

```swift
// Bad: every row constantly pulses AND spins
ForEach(items) { item in
    ItemRow(item: item)
        .phaseAnimator([1.0, 1.15, 1.0]) { v, s in v.scaleEffect(s) }
        .rotationEffect(.degrees(spinAngle))
        .animation(.linear(duration: 1).repeatForever(), value: spinAngle)
}

// Good: animate only the row that just received a tap
ForEach(items) { item in
    ItemRow(item: item)
        .scaleEffect(item.id == justTappedID ? 1.05 : 1)
        .animation(.snappy(duration: 0.2), value: justTappedID)
}
```

### 12.2 Animations that block interaction

```swift
// Bad: 0.8 s of swallowed taps
UIView.animate(withDuration: 0.8, delay: 0, options: [],
               animations: { self.sheet.center.y -= 300 })

// Good: UIViewPropertyAnimator is interruptible by default
let animator = UIViewPropertyAnimator(duration: 0.4, dampingRatio: 0.85) {
    self.sheet.center.y -= 300
}
animator.isUserInteractionEnabled = true
animator.startAnimation()
```

### 12.3 Ignoring Reduce Motion

A high-bounce spring is exactly the kind of motion that makes sensitive users queasy. Always gate through Reduce Motion (§7).

### 12.4 Over-long durations

Over 0.5 s for routine transitions feels sluggish. `UIView.animate` defaults to 0.25 s; `.spring` defaults to 0.5 s with no bounce. Reserve ≥ 0.6 s for one-time celebratory or onboarding moments.

### 12.5 Animating too many things at once

Cognitive overload *and* performance cost — every animating layer contends for render-server time. Stagger instead:

```swift
// Bad
withAnimation(.bouncy) {
    for i in items.indices { items[i].offset = randomOffset() }   // 300 in parallel
}

// Good
for (i, _) in items.enumerated() {
    withAnimation(.smooth.delay(Double(i) * 0.015)) { items[i].offset = .zero }
}
```

### 12.6 Linear easing for UI

Nothing in the physical world starts and stops instantly. `.linear` is for spinners and shimmer only.

### 12.7 Ease-in for incoming elements

`.easeIn` starts slowly and ends fast — the opposite of what a user wants from *incoming* UI. Incoming → `.easeOut`. Outgoing → `.easeIn`. Both directions → `.easeInOut`.

### 12.8 Overshooting springs in productivity contexts

A `bounce: 0.7` spring on a settings toggle is a distraction. Cap `bounce` at 0.25 for utility UI; keep high-bounce presets for genuinely playful moments.

### 12.9 Implicit animation leaking

The deprecated `.animation(_:)` (no value) applies to every change in the subtree — including data-driven and environment changes you didn't intend to animate. Always use `.animation(_:value:)` or the iOS 17+ ViewBuilder form.

### 12.10 Infinite loops that drain battery

A `.repeatForever()` animation keeps the render server awake even offscreen. Stop it in `onDisappear` and on background:

```swift
Circle()
    .scaleEffect(pulse ? 1.2 : 1)
    .animation(.easeInOut(duration: 1).repeatForever(autoreverses: true), value: pulse)
    .onAppear    { pulse = true }
    .onDisappear { pulse = false }
    .onReceive(NotificationCenter.default.publisher(
                for: UIApplication.didEnterBackgroundNotification)) { _ in pulse = false }
```

For CALayer loops, call `layer.removeAllAnimations()` on background.

### 12.11 Animating large layer trees without optimization

```swift
// Bad — shadow recomputed from alpha every frame; offscreen rendering
UIView.animate(withDuration: 0.3) {
    self.card.layer.shadowOpacity = 0.3
    self.card.layer.cornerRadius  = 16
}

// Good — precompute shadowPath; optionally rasterize
card.layer.shadowPath = UIBezierPath(roundedRect: card.bounds, cornerRadius: 16).cgPath
card.layer.shouldRasterize = true
card.layer.rasterizationScale = UIScreen.main.scale
UIView.animate(withDuration: 0.3) { self.card.layer.shadowOpacity = 0.3 }
```

Instruments → Core Animation template → "Color Offscreen-Rendered Yellow" + "Color Blended Layers" to audit (WWDC 2014 "Advanced Graphics and Animations for iOS Apps").

---

## Which animation type should I use? — decision flow

```
Is the animation triggered by a user gesture (drag, swipe, flick)?
├── YES → Spring.
│   ├── Still tracking the finger?          → .interactiveSpring()
│   ├── Released with velocity to preserve? → .spring / .snappy / .bouncy
│   └── Needs to decide commit vs. snap back? → Use velocity + predictedEndTranslation
│
└── NO → Is it a one-shot state change (tap, toggle, navigation)?
    ├── YES → Spring by default.
    │   ├── Utility / productivity surface   → .smooth   (bounce 0)
    │   ├── Wants a "decisive" feel          → .snappy   (bounce ≈ 0.15)
    │   ├── Playful / celebratory            → .bouncy   (bounce ≈ 0.30, extraBounce up to ≈ 0.4)
    │   └── Precise timing required          → .easeInOut(duration:)
    │
    └── NO → Is it a continuous loop or non-interactive decoration?
        ├── Spinner / shimmer                → .linear + .repeatForever
        ├── Breathing / pulsing indicator    → phaseAnimator
        ├── Multi-property choreography      → keyframeAnimator
        └── Reduce Motion is ON?             → Replace with .opacity or nil
```

Secondary questions, in order:

1. **Is Reduce Motion on?** Substitute, don't delete (§7).
2. **Will a Liquid Glass container handle the motion?** Just drive state with `withAnimation(.bouncy)` and let the system morph (§8).
3. **Is the property on a raw layer (shadowPath, strokeEnd)?** Drop to Core Animation (§11.4).
4. **Will the animation need to be interrupted or reversed?** Use `UIViewPropertyAnimator` in UIKit; springs in SwiftUI handle this naturally.

---

## Conclusion

The short mental model for iOS 18 and iOS 26 is this: **springs are the default, scope every implicit animation to a value, and let the platform handle motion accessibility and Liquid Glass morphing for you.** The `duration + bounce` spring API is the most important single idea — it unifies gesture hand-off, retargeting, and natural settling in one predictable parameter space, and its `.smooth / .snappy / .bouncy` presets map cleanly onto the three feels most UIs actually need.

The biggest upgrades you should adopt first, if you haven't: replace any surviving `.animation(_:)` (no value) with `.animation(_:value:)` or the iOS 17+ ViewBuilder form; replace legacy `.spring(response:dampingFraction:)` with `.spring(duration:bounce:)` at the edges of your codebase; adopt `.scrollTransition` and `.visualEffect` for scroll effects (and retire most `GeometryReader` scroll hacks); and, for iOS 26, group morphable controls in `GlassEffectContainer` with shared `glassEffectID` rather than reinventing morphs with `matchedGeometryEffect`.

Two less obvious takeaways. First, **motion is an accessibility feature** — the Reduce Motion path is not a second-class checkbox, it's where real users live, and the substitution discipline (crossfade for slide, opacity for scale, static poster for autoplay) is the difference between a polished app and a rejected one. Second, **you don't fight the system** on iOS 26 — Liquid Glass's motion is deliberately not developer-tunable at the material level, and that's a feature, not a limitation. Drive the state, trust the morph.

Reach for Core Animation only when SwiftUI and UIKit genuinely can't animate the property (path animation, strokeEnd, particles, off-main-thread guarantees). Reach for timing curves only for loops or precise timing. For everything else — the 90% case — a spring with `bounce: 0` and a duration somewhere between 0.25 s and 0.5 s will do the right thing, and will keep doing the right thing as gestures, interruptions, and retargets are layered on top.