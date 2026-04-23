import SwiftUI

// MARK: - Design System Spacing & Radius
//
// Prefer these over magic numbers. For Apple-native layout rhythm, also lean on
// .contentMargins (SwiftUI) and readableContentGuide / layoutMargins (UIKit).

extension DS {

    enum Space {
        static let xs:   CGFloat = 4
        static let sm:   CGFloat = 8
        static let md:   CGFloat = 12
        static let lg:   CGFloat = 16   // iOS system default
        static let xl:   CGFloat = 20
        static let xxl:  CGFloat = 24
        static let xxxl: CGFloat = 32
        static let huge: CGFloat = 48
    }

    enum Radius {
        static let sm:      CGFloat = 6
        static let md:      CGFloat = 10   // iOS card standard
        static let lg:      CGFloat = 16   // iOS 26 Liquid Glass card default
        static let xl:      CGFloat = 22
        static let capsule: CGFloat = .infinity
    }
}
