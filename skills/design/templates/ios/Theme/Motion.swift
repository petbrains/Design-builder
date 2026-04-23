import SwiftUI

// MARK: - Design System Motion
//
// Prefer springs over curves on iOS 18 and iOS 26. Always scope .animation()
// to a value — blanket .animation(_) re-animates every descendant change.
//
// Respect Reduce Motion: substitute (cross-fade) rather than remove. See:
// @Environment(\.accessibilityReduceMotion) var reduceMotion
// .animation(reduceMotion ? .easeInOut(duration: 0.18) : DS.Motion.springSnappy, value: state)

extension DS {

    enum Motion {

        // MARK: Spring presets — prefer these
        static let springSnappy = Animation.spring(response: 0.32, dampingFraction: 0.86)
        static let springBouncy = Animation.spring(response: 0.42, dampingFraction: 0.72)
        static let springCalm   = Animation.spring(response: 0.55, dampingFraction: 0.90)

        // MARK: Duration constants (only when a spring isn't appropriate)
        static let durInstant: TimeInterval = 0.10   // taps, presses
        static let durFast:    TimeInterval = 0.16   // button feedback
        static let durNormal:  TimeInterval = 0.22   // sheets, popovers
        static let durSlow:    TimeInterval = 0.32   // page transitions

        // MARK: Curve presets (fallbacks when you need exact timing)
        static let easeOutQuart = Animation.timingCurve(0.25, 1.0, 0.5, 1.0, duration: durNormal)
        static let easeOutQuint = Animation.timingCurve(0.22, 1.0, 0.36, 1.0, duration: durNormal)
    }
}
