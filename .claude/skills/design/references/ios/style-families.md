---
name: style-families
description: iOS-native taxonomy of 10 shipping visual-style families (root reference for style recommender)
platform: ios
---

# An iOS-native taxonomy of 10 shipping visual-style families

## Intro

This document defines ten visual-style families observable in iOS app binaries on iOS 18 stable and iOS 26 (Liquid Glass era, shipped September 2025). It is the root reference for a style recommendation engine: given a brief, a user should land on one family with high confidence. Families are mutually distinguishable on at least three of {typography, density, chroma, motion, dark-mode posture, iconography system}, and collectively cover the top-100 App Store without a "miscellaneous" bucket.

The taxonomy is iOS-native, not web-design-borrowed. It reflects SF Pro defaults, HIG constraints (Materials, Sidebars, Tab bars, Sheets, Toolbars, Typography, Dynamic Type), App Review pressure against non-standard interactions, the WidgetKit/Live-Activity surface, and the Liquid Glass material introduced in WWDC25 session 219 ("Meet Liquid Glass"). Web-borrowed labels like glassmorphic, brutalist, and neumorphic do not appear as family names — Liquid Glass is treated as an orthogonal axis because every family must state its posture toward it.

How to use: (1) pick family from the decision tree at the end based on domain, density, chroma, motion; (2) read that family's visual signatures and anti-patterns; (3) check domain affinity to confirm fit; (4) consult the Liquid Glass section for iOS 26 rendering rules. Every claim in this document attaches to a named app, a concrete numeric value, a named Apple API, a HIG section, or a WWDC session. Sentences that would fail that test are absent by design.

## Summary table

| Family | Density | Chroma | Motion | Typography posture | Dark mode default | Liquid Glass fit | Primary domain |
|---|---|---|---|---|---|---|---|
| System Default Plus | Comfortable | Low (system tints) | Minimal spring | SF Pro Text/Display, Regular+Bold | Auto (elevated gray) | Native fit | Productivity, utilities |
| Editorial Canvas | Spacious | Monochrome + 1 accent | Curve, slow | Custom serif + sans pairing | True black or warm cream | Partial (content layer unaffected) | Editorial/news, media |
| Data-Dense Terminal | Compact | Monochrome + semantic hues | Minimal, snap | SF Pro + SF Mono (tabular) | True/near-black default | Resistant (high density) | Dev tools, fintech, productivity |
| Warm Handcrafted | Comfortable | Saturated pastels/primaries | Spring-heavy, bouncy | Custom rounded sans (Feather, Aperçu, Bear 2.0 custom) | Custom always-dark or muted | Partial (brand chrome preserved) | Wellness, education, casual games |
| Tactile Depth Playful | Spacious | High (scene-driven) | Physics, 3D, 500–900ms | Custom display, heavy weights | Always ambient/dark | Resistant (own material language) | Utilities, creative tools, casual |
| Minimalist Monochrome | Spacious | Near-zero (1 accent) | Near-zero | Custom monospaced or system Light | True black + warm cream | Partial (toolbars only) | Writing, notes, fintech |
| Editorial Photography | Spacious | Image-driven | Minimal, parallax | SF Pro Display Bold or custom serif | Always-dark | Strong fit (floating controls) | Media, streaming, social cataloging |
| Fitness Vitality | Medium | Saturated brand + data | Curve + ring-fill bursts | Custom display (Boathouse, Futura, SF Rounded) | Always-dark chrome | Partial | Fitness, health |
| Youth Social Widget | Sparse to medium | Album-art/photo-driven + 1 accent | Fast spring + haptic | SF Pro + Inter-like rounded | Always-dark | Strong fit on WidgetKit surfaces | Social, photo, music |
| Enterprise Muted | Compact | Brand blue/purple primary | Curve, conservative | Brand sans (Ember, Cereal, Lato, SLDS, Fluent, Graphik) | Elevated gray | Weak (auto chrome only) | Enterprise, ecommerce, travel |

## Liquid Glass as an orthogonal axis

Liquid Glass is a navigation-layer material, not a style. Per WWDC25 session 219 ("Meet Liquid Glass") and session 323 ("Build a SwiftUI app with the new design"), it applies to toolbars, tab bars, sidebars, sheets, menus, popovers, alerts, floating controls, and primary action buttons — never to the content layer (list rows, cards, backgrounds). Apps opt in automatically by linking against the iOS 26 SDK; there is no `disableLiquidGlass()` API. User-facing opt-outs are Accessibility → Reduce Transparency, Increase Contrast, and Reduce Motion, which the system honors automatically for any view using `.glassEffect()` (SwiftUI) or `UIGlassEffect` (UIKit).

Two variants exist and never mix: `.regular` (default, adaptive) and `.clear` (requires a dimming layer; reserved for media-rich backgrounds). `GlassEffectContainer` groups adjacent glass elements so they sample consistently; without it, two glass views next to each other render inconsistently because glass cannot sample other glass. `.glassEffectID(_:in:)` with a `@Namespace` enables morph transitions between grouped elements. New standard button styles are `.buttonStyle(.glass)` and `.buttonStyle(.glassProminent)`. Corner concentricity is enforced via `ConcentricRectangle(cornerRadii: .containerConcentric)` so button corners share centers with their enclosing sheet or window.

Tab bars in iOS 26 float above content by default rather than pinning to the edge. The new modifier `.tabBarMinimizeBehavior(.onScrollDown | .onScrollUp | .automatic | .never)` controls collapse behavior — Apple TV uses `.onScrollDown`. `.tabViewBottomAccessory { }` adds an inline accessory (Music's playback bar is the canonical example). A tab with `role: .search` becomes a dedicated search tab. Toolbars use `ToolbarSpacer(placement:)` with `.fixed` or `.flexible` to group items; `.sharedBackgroundVisibility(.hidden)` removes a single item's shared glass pill (used for avatar buttons). Toolbar icons default to monochrome; tint only for semantic emphasis. Sheets gain Liquid Glass backgrounds that become opaque as the sheet pulls to full height, and can morph out of the button that presented them via the zoom-transition APIs introduced alongside `matchedTransitionSource`.

Family-level adoption patterns observed as of April 2026:

**Native fit** — System Default Plus, Editorial Photography, Youth Social Widget, and (partly) Tactile Depth Playful families absorb Liquid Glass without resistance. Apple TV (iOS 26 redesign, June 2025), Apple Fitness, Apple Weather, Lumy (featured in developer.apple.com/design/new-design-gallery), Fantastical 4.1 (moved controls to a Liquid Glass bottom toolbar), Matter (full rebuild on native components), and CARROT Weather ("Glassy Redesign") are concrete exemplars.

**Partial** — Editorial Canvas and Minimalist Monochrome absorb Liquid Glass on toolbars and sheets but leave their content layer unchanged (Cheltenham serif over white in NYT Cooking, monospaced canvas in iA Writer). Warm Handcrafted families retain custom brand chrome (Duolingo, Headspace, Strava) and only consume glass in system sheets.

**Resistant** — Data-Dense Terminal (GitHub, Linear, Ivory, Robinhood) resists glass on content because row density and semantic color coding cannot tolerate translucency behind every separator. Tactile Depth Playful apps (Not Boring Weather, Not Boring Habits) use their own 3D / sound / haptic language that competes with glass rather than layering it. Enterprise Muted (Outlook, Slack, Salesforce) adopts glass only via Xcode-26 recompile — the custom chrome (Microsoft blue header, Slack aubergine sidebar) is preserved.

For any family, the rule is: translucency belongs to navigation, not to information. When in doubt, use the `GlassEffectContainer` around a tab-bar/toolbar cluster and leave the list alone.

---

## System Default Plus

**Identity.** Apps that lean hard on UIKit / SwiftUI defaults with one or two opinionated departures — the posture Apple's own apps take.

**Reference apps.**
- Things 3 — Cultured Code — `id904237743`
- Fantastical — Flexibits — `id718043190` (Apple Design Awards 2015, Liquid Glass gallery feature 2026)
- Apple Notes / Apple Reminders — `com.apple.mobilenotes`
- Reeder (2024) — Silvio Rizzi — `id6475002485`
- Mela (Recipe Manager) — Silvio Rizzi — ADA 2025 Interaction finalist

**Visual signatures.**
- List style: `.insetGrouped` or `.sidebar` on iPad, 16pt leading inset, 10pt corner radius on inset cards (Apple Notes iOS 26 default).
- Row heights: 60–72pt for two-line cells (Apple Notes note list), 44pt for single-line settings rows.
- Separators: 0.5pt hairline at `systemGray5` inside inset groups.
- Typography: SF Pro Text 17pt Regular body, SF Pro Display Bold 28–34pt `largeTitle`, no Medium in-between — Regular vs. Bold contrast is the rule.
- Accent: single system accent color (Things yellow star, Reeder `#E8743B` orange, Fantastical deep red).
- Iconography: SF Symbols only for UI chrome; Fantastical and Things allow themselves one or two custom vector glyphs (Things' checkbox, Fantastical's DayTicker dots).
- Dark mode: elevated gray (`systemBackground`), not true black.
- Sheets: default `.presentationDetents([.medium, .large])` with system-default corner radius.
- Toolbars: iOS 26 adopts `glassEffect(.regular, in: Capsule())` automatically under `.toolbar` placement.
- Motion: spring damping 0.8, duration 250–350ms on inset transitions; no custom curves.

**Emotional keywords.** Standardized, predictable, low-friction, recognizable, discoverable, HIG-faithful, conservative, restrained.

**Typography character.** SF Pro Text body at 17pt Regular + SF Pro Display Bold largeTitle at 34pt. Dynamic Type: full support via `.dynamicTypeSize(.xSmall ... .accessibility5)`, nothing capped. No SF Rounded (breaks the serious posture).

**Color character.** System neutrals with one accent. Chroma: low. Accent frequency: only on primary action and unread indicators. Dark mode posture: auto, elevated gray.

**Motion character.** Spring-damping 0.8, 250–350ms, curve-based for push transitions (`UIViewController`'s default coordinator curve). Minimal decorative animation — Things' Magic Plus drag and Reeder's swipe-to-mark-read are the whole inventory.

**Density.** Comfortable. 44pt min-touch rows for settings, 60–72pt for list content.

**Domain affinity.**
- Perfect: productivity, utilities, healthcare/wellness (info-presenting tier).
- Good: fintech (for Copilot-style restraint), editorial/news (as wrapper), dev tools.
- Avoid: gaming, fitness (too calm), social (too institutional), creative tools (too restrained), ecommerce (too restrained).

**Anti-patterns.**
- Don't introduce a custom typeface — breaks the "native" signal immediately.
- Don't use `.presentationBackground(.regularMaterial)` on iOS 26 — override defeats the Liquid Glass sheet behavior per WWDC25 session 323.
- Don't colorize SF Symbols beyond semantic tint — HIG "Toolbars" June 2025 revision explicitly states monochrome default.
- Don't exceed 2 levels of nested navigation on iPhone; `NavigationStack` depth > 3 degrades hit testing.
- Don't replace the system share sheet with a custom one.

**HIG compliance.** Follows Sidebars, Tab bars, Toolbars, Sheets, Typography, Materials sections verbatim.

**Liquid Glass integration.** Native fit. Tab bar gets `.tabBarMinimizeBehavior(.automatic)` default. Toolbars auto-group with `ToolbarSpacer(.flexible)`. Sheets use system Liquid Glass background; custom `presentationBackground` should be removed. Fantastical 4.1 is the canonical migration example.

---

## Editorial Canvas

**Identity.** Reader-first surfaces with serif typography, generous margins, and full-bleed hero imagery.

**Reference apps.**
- NYT Cooking — `id911422904`
- Matter — `id1501592184`
- Readwise Reader — `id1567599761`
- Arc Search — The Browser Company — `id6472513080` (ADA 2024 Interaction finalist)
- The Criterion Channel — `id1454275199`

**Visual signatures.**
- Hero imagery full-bleed at device width × 220–280pt tall; body column padded at 20–24pt horizontal.
- Typography pairing: custom serif for titles (NYT Cheltenham at 28–36pt Bold; Criterion's bespoke Caslon-like serif), custom or system sans for UI (NYT Franklin, SF Pro in Matter).
- Body text: 16–17pt Regular with 1.4–1.5 line-height; reader view offers size and line-height sliders (Readwise, Matter).
- List style: custom card or `.plain` continuous feed — never `.insetGrouped`.
- Accent color: single brand hue — NYT saffron `#F5B335`, Matter coral `#FF6B4A` (ESTIMATE), Arc's pink/orange gradient on load states.
- Iconography: SF Symbols for chrome; custom bookmark/highlight/three-dot-save glyphs.
- Dark mode: true near-black for reader immersion; light mode uses warm off-white `#F9F7F3`–`#FAF6F3` (Arc, Matter) rather than pure white.
- Motion: curve-based, 300–500ms crossfades on article entry; minimal spring. Arc Search is the motion outlier — 1.2s particle-gather on "Browse for Me."
- Quiet chrome: tab bar with 3–4 items max, often hidden on scroll.

**Emotional keywords.** Considered, magazine-paced, serif-weighted, long-form, paginated, archival, library-like, unhurried.

**Typography character.** Custom serif + sans pairing is the signal. Weight contrast: Serif Bold 28–36pt titles vs. Sans Regular 16pt body. Dynamic Type: supported but capped at `.accessibility2` in reader views to preserve line-length (Matter, Readwise).

**Color character.** Monochrome + one warm accent. Chroma: low-to-zero in chrome, content provides color. Dark mode posture: true near-black option (for reader) plus warm-cream light.

**Motion character.** Curve-based, `easeInOut`, 300–500ms. No springs on text transitions. Parallax on hero images only.

**Density.** Spacious. 20–24pt horizontal margins; 96–120pt tall feed rows with large thumbnail.

**Domain affinity.**
- Perfect: editorial/news, media consumption (read/watch), productivity (reader tier).
- Good: travel (guide-style), creative tools (documentation).
- Avoid: fintech, social, fitness, dev tools, gaming, enterprise ecommerce.

**Anti-patterns.**
- Don't use `.insetGrouped` — collapses the magazine posture.
- Don't use SF Rounded — clashes with serif titles.
- Don't saturate the palette — editorial posture depends on content carrying color.
- Don't add spring-heavy motion — collides with the paced reading rhythm.
- Don't hide typography controls behind settings — Readwise-style in-reader sliders are the family convention.

**HIG compliance.** Follows Typography and Color sections; departs from Materials/Sheets by using custom reader backgrounds (a sanctioned departure per HIG "Materials" which explicitly permits custom reading surfaces).

**Liquid Glass integration.** Partial. Toolbar and tab bar absorb glass automatically; content column remains solid opaque paper. Matter's 2025 rebuild demonstrates the intended pattern: native Liquid Glass nav + solid reader canvas. Arc Search absorbed glass on its bottom pill and sheets in its iOS 26 update.

---

## Data-Dense Terminal

**Identity.** Numbers-first surfaces with monospaced data columns, semantic color coding, and information density that tolerates no translucency.

**Reference apps.**
- Ivory for Mastodon — Tapbots — `id6444602274`
- Robinhood — `com.robinhood.release.Robinhood`
- GitHub Mobile — `id1477376905`
- Linear Mobile — `id1645587184`
- Fastmail — `id931370077`

**Visual signatures.**
- SF Mono or bundled mono (Berkeley Mono in Linear per community reports) for IDs, tickers, commit SHAs, prices; tabular numerics everywhere (`.monospacedDigit()`).
- Row heights: 44–56pt in Linear (issue rows), 56pt in Robinhood (position rows), 72pt in GitHub (issue cards) — compact.
- Semantic color: GitHub's `#2DA44E` open / `#CF222E` closed / `#8250DF` merged; Robinhood's electric `#00C805` up / tinted red down; Linear's priority bars (red urgent, orange high, yellow medium, blue low).
- Dark mode: default or near-default — Linear `#08090A`, GitHub `#0D1117` primary + `#161B22` elevated, Robinhood true `#000000` bound to market hours.
- List style: `.plain` with full-width separators at 0.5pt; never `.insetGrouped` except in Settings.
- Iconography: custom glyph set over SF Symbols — GitHub Octicons, Tapbots hand-drawn circular action icons, Linear's status-circle arc-fill. This is a defining signal.
- Typography: SF Pro Text 15pt Semibold for display names, 13pt Regular secondary gray for handles/timestamps.
- Motion: minimal — curve transitions at 150–200ms, no decorative springs (exception: Tapbots' elastic pull-to-refresh + bot animation, inherited from Tweetbot).
- Chrome: persistent bottom tab bar, 5 items, user-customizable order in Ivory.
- Accent tint: single brand hue that survives dark mode (Linear `#5E6AD2` purple, GitHub's merge-green only on primary CTA).

**Emotional keywords.** Workmanlike, keyboard-first, dense, semantic, indexed, monospaced, opinionated, power-user.

**Typography character.** SF Pro Text + SF Mono mixed on the same row. Weight strategy: 15pt Semibold labels vs 13pt Regular secondary. Dynamic Type: supported but capped at `.xLarge` because density breaks at accessibility sizes — documented trade-off in Ivory release notes.

**Color character.** Monochrome base + semantic hue vocabulary (3–5 encoded colors). Chroma: low in chrome, high in data cells. Dark mode posture: true-or-near-black as default, often preferred by users.

**Motion character.** 150–200ms curves, no springs on rows. Pull-to-refresh is the one permitted spring — community convention traced to Tapbots 2008.

**Density.** Compact. 44–56pt rows, 8–12pt vertical gutters.

**Domain affinity.**
- Perfect: dev tools, fintech (trading/data), productivity (email/issues).
- Good: social (power-user clients like Ivory), enterprise, utilities (1Password-adjacent).
- Avoid: healthcare/wellness, fitness (too clinical for motivation), casual gaming, creative tools, travel, ecommerce, editorial/news.

**Anti-patterns.**
- Don't use SF Rounded — destroys the terminal posture.
- Don't apply `.glassEffect()` to rows — breaks density legibility per HIG "Materials" ("avoid glass in content layer").
- Don't use illustrative empty states — workmanlike identity dies; prefer monochrome SF Symbol + one-line copy.
- Don't introduce more than 5 semantic colors; too many and they stop reading as codes.
- Don't replace custom glyph sets with SF Symbols mid-redesign (GitHub Octicons, Ivory Tapbots icons are brand-load-bearing).

**HIG compliance.** Follows Typography (SF Mono usage), Color (semantic tint), Dark Mode; departs consciously from Tab Bars and Sidebars when custom chrome is the brand.

**Liquid Glass integration.** Resistant. Toolbars auto-adopt on recompile but stay visually terse; row backgrounds stay opaque. Ivory, GitHub, Linear leave content layer alone. Robinhood's market-hours black-white inversion is incompatible with Liquid Glass tinting; likely remains pre-glass content chrome in iOS 26.

---

## Warm Handcrafted

**Identity.** Illustration-forward, rounded-corner, mascot-bearing surfaces with saturated primary palettes and spring-heavy micro-interactions.

**Reference apps.**
- Duolingo — `id570060128` (ADA 2023 Delight and Fun winner)
- Headspace — `id493145008` (ADA 2023 Social Impact winner)
- Finch — `id1528595748`
- Bears Gratitude — Isuru Wanasinghe (ADA 2024 Delight and Fun winner)
- Rooms — Things, Inc. (ADA 2024 Visuals and Graphics winner)

**Visual signatures.**
- Custom rounded sans: Feather Bold (Duolingo, Johnson Banks + Fontsmith); Aperçu cut (Headspace via Italic Studio 2024); Quicksand-family (Finch, COMMUNITY FINDING).
- Saturated primary palette: Duolingo `#58CC02` Feather Green + `#FF4B4B` Cardinal Red + `#FFC800` Bee Yellow + `#1CB0F6` Macaw Blue; Headspace hero orange `#F47D31`; Finch pastels `#C4B5E8` lavender, `#FFD4B8` peach.
- Mascot present: Duo the owl, Finch bird, Headspace hero-smile, Bears' bear, Oak's oak tree — a defining requirement.
- Button shape: "chunky raised" — 4pt hard bottom shadow, 16pt corner radius, 64–72pt tap target height (Duolingo's lesson nodes 80pt circular).
- Iconography: custom 2D flat illustrations, 100–200 asset set per app, zero SF Symbols on hero surfaces.
- Dark mode: often supported but not brand-primary — Duolingo dark `#131F24` retains full chromatic accents; Headspace Sleep section always-dark deep-purple.
- Motion: spring damping 0.55–0.65, duration 300–450ms, bounce-physics on checkmarks and completion; confetti bursts on task/lesson complete via Lottie or SwiftUI `.phaseAnimator`.
- Streak / fire / heart / gem currency UI — Duolingo codifies, others copy.
- Illustrated empty states, never monochrome SF Symbol fallbacks.
- Full-bleed chromatic backgrounds per screen section.

**Emotional keywords.** Encouraging, gamified, pastel-or-primary, mascot-led, forgiving, habit-building, cartoon, cheerful-clinical.

**Typography character.** Custom rounded sans Bold/Heavy. Weight contrast: Heavy display (~48–80pt for numerals) vs. Medium body. Dynamic Type: capped — custom fonts rarely scale past `.xLarge` without layout breakage.

**Color character.** High-saturation triadic or complementary palette. Chroma: high. Accent frequency: everywhere — color is the brand. Dark mode posture: supported, not default.

**Motion character.** Spring damping 0.55–0.65, 300–450ms; Lottie loops 1–3s for mascot idles; confetti at completion moments. One of the two motion-heaviest families.

**Density.** Comfortable. 64–80pt button heights; 16–24pt gutters.

**Domain affinity.**
- Perfect: healthcare/wellness, fitness (motivational tier), casual gaming (Wordle-adjacent), social (teen-coded).
- Good: productivity (habit/task), education.
- Avoid: fintech (gamification is a regulatory risk — see Robinhood confetti backlash), editorial/news, dev tools, enterprise, data-heavy utilities.

**Anti-patterns.**
- Don't use SF Pro — the custom rounded sans IS the brand.
- Don't use `.insetGrouped` — the chunky card is the unit.
- Don't use curve-based 200ms transitions — the spring IS the feel.
- Don't drop the mascot from core flows — family identity collapses.
- Don't borrow Liquid Glass on buttons — the raised-shadow chunky button is inconsistent with glass lensing per HIG "Buttons" (no stacking custom shadows on glass).

**HIG compliance.** Departs from Typography default but within sanctioned custom-font territory. Follows Dynamic Type with caps.

**Liquid Glass integration.** Partial. System sheets and share UI absorb glass; custom chrome (chunky buttons, mascot scenes, streak UI) stays. Duolingo, Headspace, Finch have not rebuilt hero surfaces on Liquid Glass as of April 2026.

---

## Tactile Depth Playful

**Identity.** Physics-driven 3D scenes, haptic-synced sound, skin/theme systems, unlabeled maximalist interactions — the "Not Boring" lineage.

**Reference apps.**
- (Not Boring) Habits — Andy Works — ADA 2022 Delight and Fun winner
- (Not Boring) Weather — Andy Works — ADA 2021 finalist
- Lumy — Raja V — `id908905093` (ADA 2025 Delight and Fun finalist; Apple Liquid Glass gallery feature)
- CARROT Weather — Grailr — `id961390574` (ADA 2021 Interaction winner)
- Widgetsmith — `id1523682319`

**Visual signatures.**
- Custom bold display sans (Andy Works' wide blocky rounded), heavy weights, huge numerals (140–180pt for temperature in Not Boring Weather, 44–56pt in Lumy).
- Full-bleed 3D scene rendered in Metal/SceneKit (Not Boring Weather's sky, Not Boring Habits' low-poly landscape, Lumy's solar scene).
- Skin / theme system — purchasable packs change whole palette + sound + icons (Not Boring Super!Boring tier, CARROT's Odin/Chronos/Fenrir/Bahamut presets).
- Motion: physics-heavy, 500–900ms per interaction; Not Boring Habits' "mighty checkbox" explodes ~600–900ms; CARROT's AR garden has continuous particle motion.
- Sound: every major interaction has an audio cue — this is a defining family signal.
- Haptics: `UIImpactFeedbackGenerator` at every milestone.
- Iconography: custom 3D low-poly objects or hand-rendered scenes, near-zero SF Symbols on hero views.
- Dark mode: always-ambient — color follows time-of-day or weather, not system setting.
- Personality chrome: CARROT's AI persona 5 levels; Not Boring's unlabeled controls (user-reported friction, brand-defining).
- Widgets: first-class surface — Lumy on Apple Watch Live Activities, CARROT on Control Center, Widgetsmith's actions for iOS 18+ Control Center.

**Emotional keywords.** Toy-like, synthwave, game-UI, opinionated-maximalist, sound-rich, skinnable, physical.

**Typography character.** Custom display sans Heavy. Weight contrast: 140–180pt Heavy hero numeral vs. 15pt SF Pro metadata. Dynamic Type: rarely fully supported — hero numerals often fixed-size.

**Color character.** Scene-driven gradients — synthwave magenta→orange, cyan→indigo. Chroma: extreme on hero, restrained on metadata. Dark mode posture: always-ambient.

**Motion character.** Spring damping 0.4–0.55, 500–900ms; 3D scene interpolation is continuous; haptic-synced. The highest-motion family.

**Density.** Spacious. One focal object per screen. Not Boring Habits' checkbox occupies ~200pt square.

**Domain affinity.**
- Perfect: utilities (weather, sun/moon), casual gaming (Wordle/utility-adjacent), creative tools (toy-like).
- Good: productivity (habit, only if user wants delight), healthcare/wellness (ambient breath apps).
- Avoid: fintech, enterprise, dev tools, editorial/news, ecommerce, fitness (serious tracking), social.

**Anti-patterns.**
- Don't ship without sound — the audio cue IS part of the family signature.
- Don't label every control — Not Boring aesthetic depends on discovery.
- Don't target compact row heights — the scene is the content.
- Don't use `.plain` list style — the scene displaces lists entirely.
- Don't use Liquid Glass over the 3D scene — glass sampling a Metal layer is unsupported per WWDC25 session 219 (glass cannot sample other glass or high-motion 3D consistently).

**HIG compliance.** Departs from Tab Bars and Typography; stays within Motion accessibility (respects Reduce Motion by disabling physics scenes).

**Liquid Glass integration.** Resistant on the hero scene; strong fit on Lumy's smaller card modules and Apple Watch complications (Lumy is Apple's featured Liquid Glass gallery example for watchOS 26). Not Boring apps keep their own material language.

---

## Minimalist Monochrome

**Identity.** Near-zero chroma, single signature accent, custom or monospaced typography, Swiss/Rams-descended restraint.

**Reference apps.**
- iA Writer — `id775737172` (ADA 2025 Interaction finalist)
- Bear — `id1016366447` (Apple Design Awards 2017 winner)
- Copilot Money — `id1447330651` (ADA 2024 Innovation finalist)
- Oak — Meditation & Breathing — `id1210209691`
- Letterboxd — `id1054271011` (arguable placement — see note in Editorial Photography; Letterboxd reads here when judged on density and monochrome posture)

**Visual signatures.**
- Custom typeface: iA Writer Mono/Duo/Quattro (IBM Plex modifications, SIL OFL), Bear 2.0 bespoke typeface, Oak hand-painted icons (Sarah Kilcoyne). Letterboxd uses Graphik licensed from Commercial Type.
- Single accent: iA Writer's blue caret `#2E7CD6` (ESTIMATE), Bear red-paw `#E8392A`, Oak forest green — ONE color doing identity work.
- Background: warm off-white `#F9F8F4` (iA Writer), cream `#F4EEE3` (Oak) — never pure `#FFFFFF`.
- Dark mode: true off-black + dark gray syntax; explicit always-dark themes (Bear's "Dieci" OLED theme).
- Typography: monospaced body (iA Writer Duo at 16–18pt + 3pt line padding); SF Pro Display Ultralight/Thin for Oak's 96pt timer; Graphik Regular/Medium for Letterboxd.
- Iconography: near-absent; one or two custom glyphs, no SF Symbols on hero.
- Motion: near-zero — iA Writer is the lowest-motion app in the 48-app sample; Focus Mode crossfade is the entire animation budget.
- Density: spacious. iA Writer's 72-character max column; Oak's full-viewport timer.
- Sheet: minimal, system-default.

**Emotional keywords.** Still, Swiss, distraction-free, typographic, paper-like, restrained, Rams-descended, quiet.

**Typography character.** Custom mono or Light weight. Weight strategy: Regular body vs. no contrast — the type does the work alone. Dynamic Type: custom fonts with explicit line-height/line-width sliders (Bear exposes both).

**Color character.** Monochrome + one accent. Chroma: near-zero. Dark mode posture: true black-adjacent + warm cream light.

**Motion character.** 0–200ms crossfades. No springs. Intentional stillness.

**Density.** Spacious. iA Writer 72-character line cap; Oak single focal CTA per screen.

**Domain affinity.**
- Perfect: productivity (writing, notes), fintech (Copilot's emoji-on-circle badges), healthcare/wellness (Oak).
- Good: editorial/news (overlaps with Editorial Canvas), creative tools.
- Avoid: fitness, gaming, social, dev tools (too restrained for density), travel, ecommerce, enterprise.

**Anti-patterns.**
- Don't add a mascot — identity collapses.
- Don't add a second accent color — the single-accent rule is load-bearing.
- Don't use spring motion — Swiss posture dies.
- Don't use SF Pro default — the custom mono or Light weight IS the signal.
- Don't use `.insetGrouped` with cards — flat list or full canvas only.

**HIG compliance.** Follows Typography (sanctioned custom fonts), Accessibility (high contrast in monochrome). Departs from Tab Bars by preferring minimal chrome.

**Liquid Glass integration.** Partial. Toolbars adopt glass automatically; content canvas stays solid. iA Writer's iOS 26 update left the writing canvas unchanged and only glassed the toolbar. Copilot Money embraced the refresh across light + dark per release notes.

---

## Editorial Photography

**Identity.** Image-dominant surfaces, full-bleed hero media, minimal chrome that Liquid Glass floats above.

**Reference apps.**
- Apple TV app — `com.apple.tv` (iOS 26 redesign June 2025)
- Letterboxd — `id1054271011`
- The Criterion Channel — `id1454275199`
- NYT Cooking — `id911422904` (dual-categorization with Editorial Canvas)
- Halide Mark II — Lux — ADA 2022 Visuals winner (photography-creation sibling)

**Visual signatures.**
- Poster/photo fills 55–65% of viewport above fold (Apple TV tvOS 26 / iOS 26 vertical poster art).
- Chrome: black `#000000` (Apple TV default) or pure white `#FFFFFF` (Criterion — rare among streaming).
- Typography: SF Pro Display Bold 28–36pt for show/film titles; Criterion's bespoke serif for film titles; NYT Cheltenham Bold.
- List style: horizontal-scrolling shelves + vertical poster grids; Letterboxd's 3-wide poster grid at ~110pt thumbnail.
- Dark mode: always-dark chrome regardless of system setting (streaming convention).
- Accent: one signature — Letterboxd's green/orange/blue triad used as category dots; Criterion's muted red for CTAs.
- Iconography: SF Symbols for chrome (play, +, info); channel/brand logos within content tiles.
- Motion: parallax on hero 200–400ms, spring poster-zoom 350ms on tap; no decorative motion on text.
- Liquid Glass-native controls: Apple TV iOS 26 player controls float above video via `.glassEffect(.clear)` with dimming layer — the canonical `.clear` variant use case.
- Tab bar: 3–5 items, often minimized on scroll via `.tabBarMinimizeBehavior(.onScrollDown)` (Apple TV is the documented example).

**Emotional keywords.** Cinematic, poster-first, gallery-wall, curated-browse, cinephile, theatrical.

**Typography character.** SF Pro Display Bold or custom serif Bold 28–36pt hero. Weight strategy: hero Bold vs. 13pt Regular metadata gray. Dynamic Type: capped at `.large` to preserve poster ratios.

**Color character.** Content supplies color; chrome is neutral-black-or-white. Chroma: image-driven; chrome low. Dark mode posture: always-dark (except Criterion's signature white).

**Motion character.** 200–400ms parallax + 350ms spring on cards. No bounce.

**Density.** Spacious above fold; medium in grids.

**Domain affinity.**
- Perfect: media consumption (streaming), editorial/news (magazine browsing), social (cataloging — Letterboxd).
- Good: ecommerce (photo-heavy — Airbnb-adjacent), travel (destination imagery), creative tools (portfolio).
- Avoid: fintech, dev tools, productivity (task), utilities, fitness tracking, gaming.

**Anti-patterns.**
- Don't crop poster art — preserving original aspect is family convention (Criterion explicit).
- Don't use `.insetGrouped` — breaks the gallery posture.
- Don't add more than 1 accent color — content is the color.
- Don't use `.regular` glass on text-over-video — use `.clear` with dimming layer per WWDC25 session 219 rules for `.clear` variant.
- Don't put serif body under sans title — Criterion's serif-title / sans-metadata pairing is the convention.

**HIG compliance.** Follows Materials (`.clear` variant justified), Tab Bars (minimize behavior), Typography (custom fonts for editorial identity sanctioned).

**Liquid Glass integration.** Strong fit. Apple TV is the first-party exemplar — Liquid Glass player controls over full-bleed video is the textbook `.clear` application. Letterboxd has partially adopted on toolbars; grid content unchanged.

---

## Fitness Vitality

**Identity.** Data-rich dashboards with big metric numerals, saturated brand accent, dark-chrome, and instructor/coach photography.

**Reference apps.**
- Strava — `id426826309`
- Nike Run Club — `id387771637`
- Peloton — `id792750948`
- Apple Fitness / Fitness+ — `com.apple.Fitness`
- Gentler Streak — Gentler Stories (ADA 2024 Social Impact winner)
- Any Distance — ADA 2023 Visuals winner

**Visual signatures.**
- Custom or brand-heavy sans: Boathouse (Strava, Grilli Type custom) + Inter; Nike Futura / Trade Gothic derivatives; SF Pro Rounded (Apple Fitness rings); Inter on Peloton Android + SF Pro on iOS.
- Dark chrome: `#111111`–`#181818` primary; brand accent pops on dark — Strava orange `#FC5200`, Peloton red `#DF1D2C`, Nike Volt `#DCFF00`, Apple Fitness ring trio `#FA114F` / `#92E82A` / `#1EEAEF`.
- Metric typography: 96–160pt Bold during active session (Nike's distance/pace during runs); tabular numerics always on (`.monospacedDigit()`).
- Route-map or hero-video fill: map thumbnail on activity card, instructor video 16:9 during class.
- Ring/bar/streak graphics: Apple's Activity Rings (HIG "Activity rings" component), Strava crown icons, Peloton leaderboard bars.
- Dark mode: always-dark chrome (brand convention). Apple Fitness Summary follows system.
- Motion: ring-fill burst 800ms + confetti (Apple Fitness triple-close), number-tick on metric change, minimal spring elsewhere.
- Card grid 2-col with overlay metadata (Peloton class library).
- Kudos/reaction row at bottom of activity cards (Strava thumb, Gentler's supportive copy).

**Emotional keywords.** Kinetic, athletic-brand, neon-on-dark, leaderboard-driven, coach-led, ring-centric, chart-heavy.

**Typography character.** Custom brand display at 96–160pt during sessions; Inter / SF Pro at 13–15pt for metadata. Weight strategy: Heavy/Black hero vs. Regular body, no midweight. Dynamic Type: capped — custom display fonts fixed-size on metric screens.

**Color character.** One saturated brand hue on near-black. Chroma: high on accent, near-zero on chrome. Dark mode posture: always-dark.

**Motion character.** Curve 200–300ms + 800ms celebration bursts (ring-close, achievement unlock). Tabular number ticks on live metrics.

**Density.** Medium — hero sparse, library grids dense.

**Domain affinity.**
- Perfect: fitness, healthcare/wellness.
- Good: social (Strava's kudos feed).
- Avoid: editorial/news, gaming (except workout-gamified), dev tools, fintech, enterprise, travel, ecommerce.

**Anti-patterns.**
- Don't use light-mode-first chrome — dark-chrome is brand convention across Strava/Nike/Peloton.
- Don't use SF Pro Rounded outside of the Apple Fitness / ring context — rounded conflicts with athletic brand sans.
- Don't hide metrics behind taps — at-a-glance is the whole job.
- Don't apply `.glassEffect()` to metric numerals — translucency damages legibility on route maps.
- Don't use pastel palettes — saturation IS the vitality signal.

**HIG compliance.** Follows Typography (tabular numerics), Dark Mode (always-dark sanctioned for content apps), Materials (glass on minimized nav during active sessions).

**Liquid Glass integration.** Partial. Active-session UI stays opaque for legibility; browse/library and tab bars absorb glass. Apple Fitness iOS 26 adopts Liquid Glass on tab bar and nav controls; Strava/Nike/Peloton glass only system sheets.

---

## Youth Social Widget

**Identity.** Widget-first social surfaces with photo/album-art dominance, monochrome-or-dark chrome, and sticker/emoji reaction grammar.

**Reference apps.**
- BeReal — `id1459645446`
- Locket Widget — `id1600525061`
- Retro — `id6443709020`
- Airbuds Widget — `id1638906106`
- Finity. — Seabaa (ADA 2024 Interaction finalist)

**Visual signatures.**
- Widget as primary surface: Locket's heart-locket home-screen tile, Airbuds' now-playing widget, Retro's weekly grid.
- Photo or album art fills card: BeReal's dual-camera PiP (front ~100pt inset on ~375pt rear square); Airbuds' ~300pt album-cover tiles.
- Chrome: black `#000000` or warm cream `#F5F0E6` (Retro's signature anti-Instagram cream) — binary brand choice.
- Accent: single saturated — BeReal hazard yellow `#F5E63E` only on "Time to BeReal" notification; Locket gold `#F5C518`; Airbuds album-art-derived.
- Typography: Inter-family or SF Pro; bold display for timer/prompts.
- Small-circle social: friend caps or emphasis on private circles — BeReal capped circles, Locket 20-friend cap, Retro close-friends-only.
- Capture / quick-send flow is ≤2 taps from launch.
- Motion: haptic-synced shutter, 2-minute countdown overlay (BeReal), iPod-click haptic dial (Retro's Rewind Dec 2025), album-art scale-bounce on song change.
- Sticker reactions / background-removed selfies (RealMoji, Airbuds stickers) — custom emoji grammar.
- Weekly-recap shareable cards (Airbuds' Sunday recap, Retro's "this week in [year]").

**Emotional keywords.** Intimate, small-circle, anti-follower-count, widget-native, authenticity-coded, Gen-Z, home-screen-forward.

**Typography character.** SF Pro Display Bold + Inter-like rounded; hazard-yellow display type for alerts. Weight strategy: Bold / Heavy on prompts vs. Regular on metadata. Dynamic Type: limited support — widget surfaces constrain sizing.

**Color character.** Monochrome or dark + 1 accent + photo color. Chroma: chrome near-zero, content high. Dark mode posture: always-dark (BeReal, Locket, Airbuds) or always-cream (Retro).

**Motion character.** Fast spring damping 0.7, 200–300ms, haptic-synced. WidgetKit timeline animations update without app open.

**Density.** Sparse. One card per viewport typically.

**Domain affinity.**
- Perfect: social, media consumption (music social).
- Good: healthcare/wellness (journaling), casual gaming (prompts).
- Avoid: fintech, enterprise, dev tools, editorial/news, fitness (unless Gentler-style), travel, ecommerce, utilities, creative tools.

**Anti-patterns.**
- Don't show follower/like counts — family rejects them by convention.
- Don't require >2 taps from launch to core action — thumb-reach one-handed is the constraint.
- Don't omit WidgetKit integration — the widget is load-bearing.
- Don't over-design chrome — black/white/cream is the constraint.
- Don't use gamified streak-punishment — tone is permissive (Retro explicit "no streaks").

**HIG compliance.** Follows Widgets, Materials (glass on widget backgrounds), Dark Mode.

**Liquid Glass integration.** Strong fit on widget surfaces (iOS 26 widgets consume Liquid Glass automatically). In-app tab bars absorb glass; capture flows stay opaque for photo fidelity.

---

## Enterprise Muted

**Identity.** Brand-heavy cross-platform chrome with conservative motion, corporate-sans custom typography, and high information density on hybrid native-web foundations.

**Reference apps.**
- Microsoft Outlook — `id951937596`
- Slack — `id618783545`
- Salesforce — `id404249815`
- Notion — `id1232780281`
- Airbnb — `id401626263` (travel/ecommerce sub-cluster)
- Amazon Shopping — `id297606951`
- Etsy — `id477128284`
- Hopper — `id904052407`

**Visual signatures.**
- Custom brand sans: Microsoft Fluent type, Slack's Lato (bundled), Salesforce Sans (SLDS), Inter (Notion, Linear), Airbnb Cereal (Dalton Maag 2018), Amazon Ember (Dalton Maag 2014), Graphik (Etsy). The custom typeface survives even where SF Pro would be native.
- Brand primary on chrome bar: Outlook `#0078D4` Microsoft blue, Slack aubergine `#4A154B`, Salesforce `#0176D3`, Airbnb Rausch `#FF385C`, Amazon squid-ink `#131A22` + orange `#FF9900`, Etsy `#F1641E`.
- Custom icon set (not SF Symbols): Microsoft Fluent icons 24pt line, Slack in-house rounded line, SLDS colorful per-object icons, Airbnb DLS line icons, Amazon's photo-first + smile-arrow mark.
- Density: high — Outlook 72–80pt message rows, Amazon 180–280pt product cards stacked in carousels, Etsy 2-col photo grid at 8pt gutter.
- Dark mode: elevated gray never true black — brand hue survives in dark.
- Motion: curve-based, 150–250ms, conservative. No decorative springs in core flows (exception: Airbnb heart-save spring, Hopper bunny mascot animations — brand-carved allowances).
- Bottom tab bar 4–5 items, often platform-parity with Android (Figma variable-driven in Peloton's case — same pattern Enterprise Muted brands use).
- Hybrid native-web shells common: Fastmail (explicit), Notion (historically), Salesforce (Lightning components).
- Corporate sparkle affordance for AI: Microsoft Copilot, Salesforce Agentforce, Amazon Rufus — all share a 4-point-star iconography.

**Emotional keywords.** Corporate-consistent, cross-platform, brand-forward, dense, hybrid-shelled, enterprise-trusted, commercial.

**Typography character.** Brand sans Regular body + Semibold/Bold headers. Weight strategy: Regular/Medium/Semibold triad. Dynamic Type: partial — custom fonts rarely scale past `.large` in dense tables.

**Color character.** One saturated brand primary + neutral grays + semantic red/green/yellow. Chroma: medium. Dark mode posture: elevated gray (brand hue preserved).

**Motion character.** Curve 150–250ms. No bounce outside branded mascot moments.

**Density.** Compact to medium. 56–80pt rows; high data per viewport.

**Domain affinity.**
- Perfect: ecommerce, enterprise, productivity (email/chat/CRM), travel.
- Good: fintech (institutional tier), utilities.
- Avoid: gaming, editorial/news (too commercial), healthcare/wellness (too corporate), fitness.

**Anti-patterns.**
- Don't drop the custom typeface for SF Pro — cross-platform brand parity is the job.
- Don't use `.glassEffect(.regular)` on the branded header bar — breaks brand color consistency with Android / web.
- Don't replace brand icon set with SF Symbols — Fluent/Octicons/SLDS carry brand-recognition weight.
- Don't introduce mascot-driven motion outside sanctioned moments (Hopper bunny is the exception, not the rule).
- Don't use true-black dark mode — elevated gray preserves brand hue.

**HIG compliance.** Departs consciously from Typography (custom fonts), Tab Bars (custom chrome), Color (brand primary on header). Stays within Accessibility and Dynamic Type where data permits.

**Liquid Glass integration.** Weak. Most Enterprise Muted apps absorb glass only via Xcode 26 recompile on system sheets and share UI. Brand header stays opaque. Apple's Liquid Glass gallery (launched Nov 2025) highlighted Crumbl, American Airlines, Lowe's, CNN, and OmniFocus 4 as exemplars of the family — suggesting enterprise brands can partially adopt on tab bars while keeping brand chrome.

---

## Decision tree

Use this tree to classify a brief. Traverse in order: domain → density → chroma → motion → dark-mode posture. Resolve ties by the tiebreaker column. Eight named outcomes; four additional branches cover the remaining families.

**Step 1 — domain.**
- Fintech / dev tools / power-email / issue-tracking / Mastodon-class social → go to Step 2A.
- Editorial / news / long-form reading / recipe / film-catalog / film-streaming → go to Step 2B.
- Wellness / language / habit / casual gaming / education → go to Step 2C.
- Fitness / running / cycling / gym streaming → **Fitness Vitality**.
- Photo-social / music-social / widget-social → **Youth Social Widget**.
- Enterprise / ecommerce / travel / CRM / corporate productivity → **Enterprise Muted**.
- Utility (weather, sun, passwords, podcast) → go to Step 2D.

**Step 2A — terminal / editorial vs system-default.**
- Monospaced data, semantic colors, compact ≤56pt rows, keyboard-first → **Data-Dense Terminal**.
- Conservative SF Pro, 60–72pt rows, single accent, minimal motion → **System Default Plus**.

**Step 2B — image vs text as hero.**
- Full-bleed poster/photo dominant ≥55% of viewport, video-layer present → **Editorial Photography**.
- Serif title + sans body, text column with hero imagery subordinate → **Editorial Canvas**.

**Step 2C — mascot vs restraint.**
- Mascot present, chunky 64pt+ buttons, saturated triadic palette, spring 300–450ms → **Warm Handcrafted**.
- No mascot, 3D scene or skin system, sound + physics-heavy motion 500–900ms → **Tactile Depth Playful**.
- No mascot, single accent, monospaced type or Light weights, near-zero motion → **Minimalist Monochrome**.

**Step 2D — tactile vs default utility.**
- 3D scene + skin system + sound (weather with personality, sun tracker with scenes) → **Tactile Depth Playful**.
- Marco-Arment-style SF Rounded + orange accent, list-first, indie-quality → **System Default Plus**.

**Worked branch outcomes (eight named):**

1. *Brief: A bank challenger app for budgeting with category tags.* Domain = fintech. Density preference = comfortable, not compact. Chroma = low + single accent + emoji-on-circle badges. Motion = curve + chart-tween. → **Minimalist Monochrome** (Copilot Money lineage), with System Default Plus as fallback if the brief demands full Apple-first-party posture.

2. *Brief: A news reader that mimics a print newspaper.* Domain = editorial. Image dominance = medium (hero only). Typography = serif + sans pair. Motion = near-zero. → **Editorial Canvas** (NYT Cooking lineage).

3. *Brief: A GitHub-like issue tracker.* Domain = dev tools. Density = compact. Chroma = semantic 4–5 colors. Motion = minimal. Dark mode default true. → **Data-Dense Terminal** (Linear lineage).

4. *Brief: A habit tracker targeting teens who find Duolingo too loud.* Domain = wellness. Mascot = yes (soft, not demanding). Chroma = pastel. Motion = spring + confetti capped. Streak = optional. → **Warm Handcrafted** (Finch lineage).

5. *Brief: A weather app that teaches physics.* Domain = utility. 3D scene = required. Sound = required. Skin system = required. → **Tactile Depth Playful** (Not Boring Weather / CARROT lineage).

6. *Brief: A Letterboxd for restaurants.* Domain = social cataloging. Photo dominance = high. Dark chrome. Three-dot accent system. → **Editorial Photography** (Letterboxd lineage).

7. *Brief: A running app for a non-serious runner.* Domain = fitness. Metric hero = yes. Dark chrome. Single brand hue. → **Fitness Vitality** (Gentler Streak lineage if permissive, Strava if competitive).

8. *Brief: A photo-sharing widget for close friends only.* Domain = social. Widget = primary surface. ≤20 friend cap. Anti-follower-count. → **Youth Social Widget** (Retro / Locket lineage).

**Additional branches for completeness:**

9. *Brief: A task manager that should feel like an Apple app.* → **System Default Plus** (Things / Reeder lineage). The tiebreaker over Minimalist Monochrome: SF Pro is mandatory, not a custom typeface.

10. *Brief: A writing app for novelists.* → **Minimalist Monochrome** (iA Writer lineage). Tiebreaker over System Default Plus: custom typography is required, and motion must drop to near-zero.

11. *Brief: A CRM or team-chat product.* → **Enterprise Muted** (Slack / Salesforce lineage). Tiebreaker over System Default Plus: cross-platform parity with Android/web forces custom brand typography and brand-color header chrome that Liquid Glass cannot absorb cleanly.

12. *Brief: A puzzle game with newsprint feel.* → **Editorial Canvas** at the chrome layer (NYT Karnak/Franklin/Cheltenham trio) combined with game-board custom rendering. Wordle / NYT Crossword live at this intersection.

**Liquid Glass as final filter (iOS 26 brief).** After family selection, apply the Liquid Glass axis: if the brief says "must feel like a 2026 iOS app," require native-fit (System Default Plus, Editorial Photography, Youth Social Widget, Fitness Vitality, Tactile Depth Playful on small modules). If the brief prioritizes brand parity across platforms (Enterprise Muted, Warm Handcrafted), accept partial glass only on system sheets. If the brief demands content density (Data-Dense Terminal, parts of Minimalist Monochrome), keep content opaque and use glass exclusively on toolbars.

## Conclusion

Three structural findings change how this taxonomy gets used. First, iconography is a stronger family signal than typography alone — apps that ship custom glyph sets (Octicons, Tapbots circular action icons, Duolingo's Cool Kids, Airbnb DLS, SLDS) cluster tightly even when they span domains, and an app's choice to use or abandon SF Symbols is the single best early classifier. Second, Liquid Glass does not collapse family distinctions; it amplifies them, because each family's posture toward the material (native / partial / resistant) is now a load-bearing axis rather than a detail. Third, dark-mode default — always-dark, auto/elevated, true-black-bound-to-state — splits the taxonomy into three cohorts that domain alone does not predict, and it is the tiebreaker when density and chroma inconclusively point to two families.

The taxonomy deliberately places Letterboxd and NYT Cooking in boundary positions. Letterboxd sits between Editorial Photography (poster grid) and Minimalist Monochrome (Graphik-on-dark restraint); community writers disagree (Viticci leans cinephile-editorial, Venkatesan leans minimal — COMMUNITY FINDING), and the engine should surface both families when an app matches Letterboxd's brief. NYT Cooking sits between Editorial Canvas and Editorial Photography. The resolution is density: text-column-plus-hero goes Canvas; poster-grid-dominant goes Photography.

Two families expand under iOS 26 and two contract. Editorial Photography expands because Liquid Glass's `.clear` variant was engineered for video-dominant chrome. Youth Social Widget expands because iOS 26 widgets natively render in glass. Tactile Depth Playful contracts because glass cannot sample 3D Metal scenes consistently, forcing these apps to keep their own material language. Data-Dense Terminal contracts because glass-on-rows destroys the density that defines the family — the Linear / GitHub / Ivory posture becomes more distinct, not less, after iOS 26.

What this taxonomy will not do is classify deeply custom games, spatial-computing-first apps, or first-party Apple apps that exist outside category conventions (Shortcuts, Wallet). Anything that lives primarily on Vision Pro or that depends on Metal-rendered content as its primary surface sits outside the ten families and should route to a separate spatial / metal-native taxonomy not attempted here.