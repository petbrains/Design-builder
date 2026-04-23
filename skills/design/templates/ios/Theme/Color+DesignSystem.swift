import SwiftUI

// MARK: - Design System Colors
//
// Consume these in views. Do NOT use raw hex or Color.white/Color.black for chrome.
// Palette values live in Assets.xcassets/DesignSystem/*.colorset — edit there, not here.
//
// Semantic precedence:
//   1. Apple system semantics (Color(.label), Color(.systemBackground)) for chrome
//   2. Design system semantics (Color.dsBackground, Color.dsAccent) for brand surfaces
//   3. Raw hex — NEVER

extension Color {

    // MARK: Brand surfaces (from designlib palette)
    static let dsBackground    = Color("Background",    bundle: .main)
    static let dsSurface       = Color("Surface",       bundle: .main)
    static let dsSurfaceRaised = Color("SurfaceRaised", bundle: .main)
    static let dsBorder        = Color("Border",        bundle: .main)
    static let dsTextPrimary   = Color("TextPrimary",   bundle: .main)
    static let dsTextSecondary = Color("TextSecondary", bundle: .main)
    static let dsTextMuted     = Color("TextMuted",     bundle: .main)

    // MARK: Accent — do NOT alias AccentColor here.
    // Apply brand tint via `.tint(.accentColor)` at app root; iOS picks up AccentColor.colorset automatically.

    // MARK: Apple system semantics — prefer these for chrome
    static let dsChromeFill       = Color(.systemBackground)
    static let dsChromeSecondary  = Color(.secondarySystemBackground)
    static let dsGroupedBg        = Color(.systemGroupedBackground)
    static let dsGroupedSecondary = Color(.secondarySystemGroupedBackground)
    static let dsSeparator        = Color(.separator)
    static let dsLabel            = Color(.label)
    static let dsSecondaryLabel   = Color(.secondaryLabel)
    static let dsTertiaryLabel    = Color(.tertiaryLabel)
    static let dsQuaternaryLabel  = Color(.quaternaryLabel)
}
