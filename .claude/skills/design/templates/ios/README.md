# iOS Theme Starter

Drop these files into `<App>/Theme/` after running `/design system ios`. Replace placeholders:

- `HEADING_FAMILY` / `BODY_FAMILY` in `Typography.swift` → designlib `font_pair.heading.family` / `font_pair.body.family`
- Color asset catalog entries referenced by `Color+DesignSystem.swift` must exist in `Assets.xcassets/DesignSystem/`
- Register custom fonts in `Info.plist` under `UIAppFonts`
- Apply tint at app root: `.tint(.accentColor)` — AccentColor.colorset drives it

## Files

| File | Purpose |
|---|---|
| `Color+DesignSystem.swift` | Semantic `Color` accessors (`Color.dsBackground`, `Color.dsLabel`) |
| `Typography.swift` | `DS.Font.display/body/mono(_:weight:)` with Dynamic Type scaling |
| `Spacing.swift` | `DS.Space.{xs,sm,md,lg,xl,xxl,xxxl,huge}` + `DS.Radius.*` |
| `Motion.swift` | `DS.Motion.springSnappy/Bouncy/Calm` + duration constants |
| `Haptics.swift` | `DS.Haptic.*` legacy wrappers; prefer `.sensoryFeedback(...)` on iOS 17+ |

## Deletion rules

- `Haptics.swift` — delete if haptic budget = `off`
- `Motion.swift` duration constants — delete if you only use springs

## Do not

- Add computed color blends here — add them as new `.colorset` assets instead (so they resolve dark/HC variants)
- Expand `DS.Space` beyond the 8 tokens — if you need in-between values, question whether you're breaking rhythm
