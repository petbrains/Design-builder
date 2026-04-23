import SwiftUI

// MARK: - Design System Typography
//
// Replace HEADING_FAMILY / BODY_FAMILY with names from designlib font_pair.
// If font_pair says "system" — call .system(size:weight:design:) instead and skip .custom.
//
// Dynamic Type: every size is wired with `relativeTo:` so AX5 users get scaled type.
// Custom fonts must be registered in Info.plist → UIAppFonts.

extension DS {
    enum Font {

        static func display(_ size: Size, weight: Weight = .bold) -> SwiftUI.Font {
            .custom("HEADING_FAMILY", size: size.rawValue, relativeTo: size.textStyle)
                .weight(weight)
        }

        static func body(_ size: Size, weight: Weight = .regular) -> SwiftUI.Font {
            .custom("BODY_FAMILY", size: size.rawValue, relativeTo: size.textStyle)
                .weight(weight)
        }

        static func mono(_ size: Size) -> SwiftUI.Font {
            .system(size: size.rawValue, design: .monospaced)
        }

        enum Size: CGFloat {
            case caption2    = 11
            case caption     = 12
            case footnote    = 13
            case subheadline = 15
            case callout     = 16
            case body        = 17
            case headline    = 17
            case title3      = 20
            case title2      = 22
            case title1      = 28
            case largeTitle  = 34
            case display     = 48

            var textStyle: SwiftUI.Font.TextStyle {
                switch self {
                case .caption2:               return .caption2
                case .caption:                return .caption
                case .footnote:               return .footnote
                case .subheadline:            return .subheadline
                case .callout:                return .callout
                case .body, .headline:        return .body
                case .title3:                 return .title3
                case .title2:                 return .title2
                case .title1:                 return .title
                case .largeTitle, .display:   return .largeTitle
                }
            }
        }
    }
}

enum DS {} // namespace; Spacing.swift, Motion.swift extend it
