import SwiftUI
import UIKit

// MARK: - Design System Haptics
//
// Prefer SwiftUI .sensoryFeedback (iOS 17+) — declarative, system-throttled, free.
// Usage:
//   .sensoryFeedback(.success, trigger: submittedCount)
//   .sensoryFeedback(.selection, trigger: selectedIndex)
//   .sensoryFeedback(.impact(weight: .light), trigger: toggledValue)
//
// Haptic budget levels (set at interview):
//   off              — this file is unused; delete
//   system-only      — rely on system controls (UISwitch, pull-to-refresh) only
//   curated-moments  — hook .success / .warning / .error / .selection at meaningful moments
//   expressive       — add Core Haptics patterns for signature moments (see references/ios/haptics.md)
//
// Anti-pattern: haptic fatigue. If your feedback fires more than ~5×/minute in normal use,
// you are in fatigue territory — remove some or throttle.

extension DS {
    enum Haptic {

        @available(iOS, deprecated: 17.0, message: "Use .sensoryFeedback() on iOS 17+")
        static func impact(_ style: UIImpactFeedbackGenerator.FeedbackStyle = .medium) {
            let g = UIImpactFeedbackGenerator(style: style)
            g.prepare()
            g.impactOccurred()
        }

        @available(iOS, deprecated: 17.0, message: "Use .sensoryFeedback() on iOS 17+")
        static func selection() {
            let g = UISelectionFeedbackGenerator()
            g.prepare()
            g.selectionChanged()
        }

        @available(iOS, deprecated: 17.0, message: "Use .sensoryFeedback() on iOS 17+")
        static func notification(_ type: UINotificationFeedbackGenerator.FeedbackType) {
            let g = UINotificationFeedbackGenerator()
            g.prepare()
            g.notificationOccurred(type)
        }
    }
}
