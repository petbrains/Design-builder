---
name: figma-ios-swiftui
description: iOS/SwiftUI-specific routing when the Figma MCP is involved. Covers the "build new screen" and "adapt existing screen" flows, layout/typography/color/effect mapping tables, variant → native state translation, asset pipeline, and responsive multi-device handling.
---

# Figma → SwiftUI routing

Loaded by `/design craft`, `/design make`, and `/design refine` whenever `--platform ios` is active AND the agent has at least one `mcp__*figma*__*` tool available. For web, the generic `references/figma/implement-design/` is used instead.

## Entry modes

| User said | Mode | Skips |
|---|---|---|
| "build this screen" + Figma URL | Build-from-scratch (§2) | §3 |
| "match / adapt / align / update this screen to Figma" | Adapt-existing (§3) | §2 partial |
| "tweak node 42:15 — move, resize, re-bind variable" | Point-edit (§4) | §2, §3 |
| "extract the tokens" | Token sync only (§5) | §2, §3, §6 |

If the user gives a Figma URL without context, ask which mode before calling MCP — the first tool call budget matters for Starter/View seats (6 writes/month hard cap). Dev/Full seat: per-minute limit, no pre-call check needed.

---

## 1. URL parsing (shared prelude)

Accept `figma.com/design/:fileKey/:name?node-id=X-Y` and legacy `/file/`. Reject `/proto/` (prototype) and `/board/` (FigJam) — not implementable. Convert `node-id` `X-Y` → `X:Y` before passing to MCP (`get_design_context`, `get_variable_defs`, `get_screenshot`). Other query params (`m=dev`, `t=...`, `page-id=...`) are ignored.

Figma desktop MCP variant: selected node in the app is used automatically; only `nodeId` needed, `fileKey` inferred.

---

## 2. Build-from-scratch flow

**Order is non-negotiable:**

1. `get_design_context(fileKey, nodeId, prompt="generate for iOS using SwiftUI")` — steers default code output toward SwiftUI. Treat the returned code as a **spec, not source** — do not port its React/Tailwind into SwiftUI line-by-line.
2. `get_metadata(fileKey, nodeId)` — only if (1) was truncated or the frame has 50+ children. Identify sections → fetch each with (1).
3. `get_screenshot(fileKey, nodeId)` — visual source of truth for later validation. Always fetch once, reuse per section.
4. `get_variable_defs(fileKey, nodeId)` — tokens. Run the mapping in §5 *before* writing any view code.
5. Download assets inline during this MCP session (§7) — URLs are ephemeral localhost and expire when the session closes.
6. `get_code_connect_map(fileKey, nodeId)` — check if the components in the frame already have code mappings. If yes, use the mapped views; generate nothing from scratch for those components.
7. Write SwiftUI (§6).
8. `add_code_connect_map(...)` for any reusable custom component you created (§9).

**What NOT to implement** — these elements appear in Figma mockups but are rendered by iOS itself. Skip unless the frame explicitly uses a custom non-system version:

- System keyboard, emoji picker, formatting bar
- Status bar (time/battery/signal)
- Home indicator
- `NavigationStack` back chevron
- Native `TabView` tab bar (only implement a custom one)
- System alerts / action sheets → `.alert()` / `.confirmationDialog()`
- Share sheet → `ShareLink` or `UIActivityViewController`
- `.searchable()`, `.refreshable()`, native page dots
- System context menus → `.contextMenu {}`

If unsure whether something is system-provided, ask.

**Dependency respect** — before picking a SwiftUI primitive, read `Package.swift` / `Podfile` / `*.xcodeproj`. Use what the project already imports:

| Concern | Native default | Override if project has |
|---|---|---|
| Remote images | `AsyncImage` | Kingfisher, Nuke, SDWebImage |
| Animations | SwiftUI `.animation` | Lottie |
| Layout | SwiftUI stacks | SnapKit (rare in pure SwiftUI) |
| Charts | Swift Charts | Charts library, custom |
| Networking | URLSession | Alamofire, Moya |

Do not introduce a new image-loading or animation dependency. If the project has none and the design genuinely needs one, ask the user before adding.

---

## 3. Adapt-existing flow

This is the highest-value iOS flow because it's the most common request in real projects ("our profile screen drifted from Figma — resync it").

### 3.1 Read current state

Before any MCP write or SwiftUI edit, load:

- The target view file
- Every referenced subcomponent (custom views, shared styles)
- Relevant model types (you need to know what data is already available)

Record the *current* values verbatim: paddings, stack spacings, corner radii, opacities, colors, font sizes, frame widths.

### 3.2 Build the diff checklist

Compare line-by-line against `get_design_context` + `get_screenshot`. Bucket every difference into one of three categories. **One bucket per row** — no "refactor + restyle" combos.

- **ADD** — in Figma, not in code. New element, new variant, new icon.
- **UPDATE** — in both, different. **Always** show `old → new`.
- **REMOVE** — in code, not in Figma. Always ask the user before deleting; designers sometimes just hide a frame.

### 3.3 Spacing pass (mandatory separate pass)

Spacing is where 80% of adaptation misses happen. Run a dedicated pass over the frame — every padding, every stack `spacing:`, every `frame()`, every `safeAreaInset`. If Figma says 20 and code says 16, that is a change, not "close enough." Read exact values from the MCP `properties` — do not eyeball the screenshot.

Common blind spots:
- Vertical gap between two `VStack`s that have their own internal spacing
- Trailing padding on a row that uses `.frame(maxWidth: .infinity, alignment: .leading)`
- Safe-area inset on bottom sheet content
- `EdgeInsets` vs per-edge `.padding()` mismatch

### 3.4 Checklist format

Present grouped, with old→new explicit. Example skeleton:

```
Structural
- ADD: countdown card (lime bg, timer, progress)
- REMOVE: "Winner" section — confirm?

Spacing
- UPDATE: avatar size 56 → 64
- UPDATE: VStack inter-row spacing 12 → 8
- UPDATE: card bottom padding 16 → 24

Typography
- UPDATE: title 17pt medium → 20pt semibold
- UPDATE: points 28pt semibold → 22pt semibold expanded

Color / style
- UPDATE: place badge gradient (gold/silver/bronze) → purple for all
- UPDATE: background — hardcoded RGB → Color("surface.primary")

New data required
- Timer: hardcode or needs API field?
- Stats tags: source?
```

### 3.5 Clarify, then apply

Before editing code, confirm: new data sources, REMOVEs, ambiguous system-vs-custom elements. Then apply **every** item — do not skip 4pt or 0.02-opacity changes. Those are exactly what erodes visual fidelity over months.

### 3.6 Common font trap

Figma "Expanded Semibold" is two things: weight `.semibold` AND width `.expanded`. `Font.system(size:, weight: .semibold)` alone is wrong — need `.width(.expanded)`. Same for Condensed, Compressed. Check both axes before writing the `.font()` modifier.

---

## 4. Point-edit flow

User says: "in node 42:15, shift the button 16pt down" / "change the card radius to 12" / "re-bind the fill to `color/accent`".

One MCP write-call per edit, via `figma-use`:

```js
const node = await figma.getNodeByIdAsync("42:15")
node.y += 16
// or: node.resize(w, h) / node.paddingLeft = 24 / node.cornerRadius = 12
// or: re-bind variable via node.setBoundVariable("fills", 0, variableId)
```

No read-back-and-diff is needed — this mode trusts the user's intent. The only pre-check: if the target is an **instance of a published component**, warn that changes create an override rather than propagating to the main component. For edits to the main component, confirm the user wants library-wide impact.

---

## 5. Token sync (from `get_variable_defs`)

### 5.1 Resolution order (same as Layer 1 of the plugin)

1. **Project already has a token system** (`Color+Extensions.swift`, `Theme.swift`, Asset Catalog named colors, `Spacing` enum, `CornerRadius` enum, `Font` extension) — map Figma names to existing ones **by value first, then by semantic name**. Never create a parallel system.
2. **Project has no tokens** → materialize from Figma vars. Group by concern:
   - Colors → Asset Catalog with Any/Dark Appearance (preferred), fallback to `Color` extension
   - Spacing → `enum Spacing { static let xs: CGFloat = 4 ... }`
   - Typography → `extension Font { static let bodyRegular = Font.system(size: 16, weight: .regular) }`
   - Radius → `enum CornerRadius` with a `.full = 9999` sentinel that callers treat as `Capsule()`
   - Elevation → `extension View { func shadowSm(); func shadowMd(); func shadowLg() }`

### 5.2 Figma name → SwiftUI name conventions

| Figma variable path | SwiftUI binding |
|---|---|
| `primary/500` | `Color.primary500` or `Color("primary500")` |
| `text/primary` | `Color.textPrimary` |
| `surface/default` | `Color.surfaceDefault` |
| `border/subtle` | `Color.borderSubtle` |
| `spacing/md` (value 12) | `Spacing.md` |

Convention: slash → camelCase collapse (`text/primary` → `textPrimary`). Numeric suffixes stay (`primary500`, not `primaryFiveHundred`).

### 5.3 Dark mode

Prefer Asset Catalog sets with Any Appearance + Dark Appearance entries — `Color("textPrimary")` then adapts automatically, no conditional code. Only use `@Environment(\.colorScheme)` when Asset Catalog is unavailable (Swift Package without resources, for example).

### 5.4 Dynamic Type

If the Figma size maps to an iOS text style (≈17pt body, ≈28pt title), use the semantic style: `.font(.body)`, `.font(.title)`. They scale with user's Dynamic Type setting for free. For custom sizes you want scaling on, use `@ScaledMetric(relativeTo: .body) private var fontSize: CGFloat = 16`.

---

## 6. Mapping tables (SwiftUI)

### 6.1 Layout

| Figma | SwiftUI |
|---|---|
| Auto-layout vertical | `VStack(alignment:, spacing:) { }` |
| Auto-layout horizontal | `HStack(alignment:, spacing:) { }` |
| Auto-layout wrap | `LazyVGrid(columns: [GridItem(.adaptive(minimum:))])` or custom `FlowLayout` |
| Absolute positioning | `ZStack { }` + `.offset(x:, y:)` (avoid when possible) |
| Pin to edges | Parent alignment + `.frame(maxWidth/Height: .infinity, alignment:)` |
| Hug contents | Default — no frame modifier |
| Fill container | `.frame(maxWidth: .infinity)` or `.frame(maxHeight: .infinity)` |
| Fixed size | `.frame(width:, height:)` — only for genuinely fixed elements (icon, avatar, badge) |
| Aspect ratio | `.aspectRatio(w/h, contentMode: .fit / .fill)` |
| Uniform padding 16 | `.padding(16)` |
| H16 V12 | `.padding(.horizontal, 16).padding(.vertical, 12)` |
| Per-edge | `.padding(EdgeInsets(top:, leading:, bottom:, trailing:))` |
| Gap = 12 | `spacing: 12` argument in stack initializer |
| Scroll (vertical) | `ScrollView(.vertical) { VStack { } }` |
| Paging | `ScrollView { LazyHStack { } }.scrollTargetBehavior(.paging)` |

**Primary-axis alignment** (Figma "justify"):
- Packed start → default
- Packed center → `Spacer()` on both sides, or `frame(maxWidth: .infinity)` with `.center` alignment
- Packed end → `Spacer()` before content
- Space between → `Spacer()` between each child
- Space around / evenly → no native — compute via GeometryReader or custom insets

**L/R vs leading/trailing**: Figma is absolute (left/right), SwiftUI uses leading/trailing for RTL support. Convert.

### 6.2 Typography

| Figma | SwiftUI |
|---|---|
| Font family (system) | `.font(.system(size:, weight:, design:))` |
| Font family (custom) | `.font(.custom("Inter-Regular", size:))` — verify font is in `Info.plist UIAppFonts` first |
| Weight | `.semibold`, `.bold`, `.medium`, `.regular` — on `Font.Weight` |
| Width (Expanded/Condensed) | `.width(.expanded)` / `.width(.condensed)` — separate axis from weight |
| Line height | `.lineSpacing(lineHeight - fontSize)` — SwiftUI measures *extra* spacing between lines |
| Letter spacing (tracking) | `.tracking(value)` — Figma px equals SwiftUI points 1:1 on iOS |
| Semantic style match | Prefer `.font(.headline)`, `.font(.body)`, `.font(.caption)` when sizes align — free Dynamic Type |

### 6.3 Color

| Figma | SwiftUI |
|---|---|
| Hex fill | `Color("name")` from Asset Catalog (preferred) or `Color(hex: "#...")` extension |
| Fill + opacity | `.opacity()` modifier (view) or `.color.opacity()` (on Color) |
| Linear gradient | `LinearGradient(colors:, startPoint:, endPoint:)` |
| Radial gradient | `RadialGradient(colors:, center:, startRadius:, endRadius:)` |
| Angular / conic | `AngularGradient(colors:, center:)` |
| Variable reference | Project token (see §5), never inline hex |

### 6.4 Effects

| Figma | SwiftUI |
|---|---|
| Drop shadow | `.shadow(color:, radius:, x:, y:)` |
| Inner shadow | `.overlay` with masked stroke, or custom shape stroke (no native) |
| Layer blur | `.blur(radius:)` |
| Background blur | `.background(.ultraThinMaterial)` / `.thinMaterial` / `.regularMaterial` / `.thickMaterial` |
| Corner radius (uniform) | `.clipShape(.rect(cornerRadius:))` or `RoundedRectangle(cornerRadius:)` |
| Per-corner radius | `UnevenRoundedRectangle(topLeadingRadius:, topTrailingRadius:, bottomLeadingRadius:, bottomTrailingRadius:)` |
| Stroke / border | `.overlay(RoundedRectangle(cornerRadius:).stroke(color, lineWidth:))` |
| Clip content | `.clipped()` or `.clipShape()` |
| Mask | `.mask { }` |
| Blend mode | `.blendMode(.multiply / .overlay / ...)` |
| **Liquid Glass (iOS 26+)** | `.glassEffect(...)` with an appropriate shape — see `references/ios/liquid-glass.md` |

### 6.5 Motion

Figma prototype arrows encode *intent*, not exact timings. Translate to state-driven SwiftUI, then pick standard iOS timing unless the user overrides.

| Figma | SwiftUI |
|---|---|
| Dissolve | `.opacity()` + `withAnimation(.easeInOut) { }` |
| Move in / slide in | `.transition(.move(edge:))` + `withAnimation` |
| Push (screen) | `NavigationStack` push — system provides the transition, don't custom-implement |
| Smart animate | `withAnimation { state = new }` on diffed properties (position, size, opacity) |
| Shared element | `matchedGeometryEffect(id:in:)` |
| Scroll animate | `.scrollTransition { content, phase in ... }` |

Rules:
- If a prototype arrow only changes screens, it's navigation — not a custom animation.
- Standard timings (`.default`, `.spring`, `.easeInOut`) unless user specifies exact curves.
- Check for Lottie in deps before writing SwiftUI animations for anything choreographed.
- Do not over-animate. If unsure whether something is a transition or a scene change, ask.

---

## 7. Asset pipeline

### 7.1 SF Symbols first

Check SF Symbols before downloading any icon. Matches cover most UI iconography:

| Figma label | SF Symbol |
|---|---|
| arrow right / back | `arrow.right` / `arrow.left` |
| close / x | `xmark` |
| settings / gear | `gearshape` |
| search | `magnifyingglass` |
| user / profile | `person` |
| home | `house` |
| notification / bell | `bell` |
| menu / hamburger | `line.3.horizontal` |
| plus / minus / check | `plus` / `minus` / `checkmark` |
| share | `square.and.arrow.up` |

**Cross-platform caveat** — if the project targets iOS **and** Android (Skip, KMP, Flutter), do NOT auto-default to SF Symbols. List every icon + proposed match, ask per-icon. Some need platform-neutral SVGs (Material Symbols for Android).

### 7.2 When to download from Figma instead

- Brand/logo marks (app logo, company logos, social logos)
- Illustrated or multi-color icons not in SF Symbols
- Custom color treatments SF Symbols can't replicate
- Complex illustrations / photos

### 7.3 Downloading

`get_design_context` returns localhost URLs in its response. **Download immediately in-session** — URLs die when the MCP session ends.

```bash
curl -o onboarding-hero.png "http://localhost:PORT/path"
```

If a node has no download URL (sometimes happens for custom icons), fall back to `get_screenshot(fileKey, nodeId)` with that node ID alone.

### 7.4 Asset Catalog

Raster:

```
Assets.xcassets/
  Images/
    onboarding-hero.imageset/
      onboarding-hero@1x.png
      onboarding-hero@2x.png
      onboarding-hero@3x.png
      Contents.json
```

Generate @1x/@2x from the highest-res source with `sips -Z`. MCP usually returns one resolution — treat it as @3x and downscale.

`Contents.json` for raster:

```json
{
  "images": [
    { "filename": "name@1x.png", "idiom": "universal", "scale": "1x" },
    { "filename": "name@2x.png", "idiom": "universal", "scale": "2x" },
    { "filename": "name@3x.png", "idiom": "universal", "scale": "3x" }
  ],
  "info": { "author": "xcode", "version": 1 }
}
```

SVG: single file in the imageset, `"properties": { "preserves-vector-representation": true }`. Use `Image("name").renderingMode(.template)` if the icon needs to tint with `.foregroundStyle()`.

**Convert SVG to `Shape`** only if: fewer than ~5 control points, needs runtime stroke/fill animation, or you genuinely need to animate its path. Otherwise keep it as an asset.

### 7.5 Remote images

Never download remote user content (avatars, feed photos) into the Asset Catalog. Use the project's image-loading library. If none is present, ask — do not silently default to `AsyncImage`.

### 7.6 Hard rules

1. Never create placeholder images. Always download actual assets in-session.
2. Never add a new icon dependency (no new SPM package for icons).
3. Match project's existing asset-naming convention (kebab-case vs camelCase — read before adding).

---

## 8. Responsive / multi-device

### 8.1 When to even ask

- Figma frame width 375–430pt (iPhone) + project targets iPad → ask about iPad before implementing.
- Figma file has separate iPhone **and** iPad frames → fetch both, then ask how to combine.
- iPad-only (744–1024pt) → ask about iPhone support.
- Don't assume.

### 8.2 Fixed values vs adaptive

| Figma value | iOS treatment |
|---|---|
| Full-screen width (375, 390, 393, 430) | `.frame(maxWidth: .infinity)` — **never** `.frame(width: 375)` |
| Icon / avatar / badge (fixed-size by design) | Keep `.frame(width:, height:)` |
| Content container (e.g., 343 in 375) | `.containerRelativeFrame(.horizontal) { w, _ in w * 0.915 }` (iOS 17+) |
| Anything relying on screen width | `containerRelativeFrame` or `GeometryReader`. **Banned: `UIScreen.main.bounds`** — breaks under Split View, Slide Over, Stage Manager |

### 8.3 Size classes

Switch layouts (not just widths) on `@Environment(\.horizontalSizeClass)`:

- compact = iPhone portrait, iPad split/slide-over
- regular = iPad full-screen, some iPhone landscape

Use only when Figma shows **fundamentally different layouts** per device:

- List (iPhone) vs grid (iPad) → switch via size class
- Single column vs sidebar + detail → `NavigationSplitView` regular / `NavigationStack` compact
- Stacked sections vs side-by-side → VStack compact / HStack regular

Do NOT use size classes when it's the same layout with different paddings — flexible frames solve that without branching.

### 8.4 `ViewThatFits` (iOS 16+)

For content that may or may not fit in one row without any notion of device — action bars, label+value rows, tag lines. SwiftUI picks the first variant that fits:

```swift
ViewThatFits(in: .horizontal) {
    HStack(spacing: 12) { icon; label; Spacer(); value }
    VStack(alignment: .leading, spacing: 8) {
        HStack(spacing: 12) { icon; label }
        value
    }
}
```

---

## 9. Variants → state

### 9.1 Mapping principle

Use the nearest native mechanism. **Custom enum is a last resort** — only for states iOS doesn't model.

| Figma variant | Native mechanism |
|---|---|
| Pressed | `configuration.isPressed` inside `ButtonStyle.makeBody` |
| Disabled | `@Environment(\.isEnabled)` in the style (or `.disabled(true)` on caller) |
| On/Off | `configuration.isOn` inside `ToggleStyle` |
| Focused | `@FocusState` + `.focused($state, equals: ...)` |
| Selected (list/picker) | Selection binding on the container |
| Loading / Error / Empty / Skeleton | Custom enum in view model (no system equivalent) |

### 9.2 Style/Type variants

For Primary/Secondary/Destructive/Ghost:

- Minimal differences (colors, border) → single `ButtonStyle` with `enum ButtonVariant` parameter.
- Substantial differences (different structure, different shapes) → separate `ButtonStyle` types (`PrimaryButtonStyle`, `GhostButtonStyle`) + `.buttonStyle(.primary)` / `.buttonStyle(.ghost)` call sites.

### 9.3 Size variants

- Wrapping a system control (Button, Toggle, Picker, DatePicker) → `.controlSize(.mini / .small / .regular / .large / .extraLarge)`. No custom enum.
- Fully custom component → custom `enum ComponentSize { case sm, md, lg }` with a switch for font and paddings inside `makeBody`.

### 9.4 Fetching all variants from MCP

A single `get_design_context` on an instance returns its current variant. To understand the full state space, `get_metadata` on the parent component set → sibling nodes → `get_design_context` on each. Always do this for Button, Input, and anything with 4+ visible states — implementing only the default variant is the #2 source of adaptation drift after spacing.

---

## 10. Validation (opt-in only)

Do not auto-validate. Before step 6, ask the user how they want to check parity:

- Side-by-side preview in Xcode (`#Preview`)
- Simulator run + manual check
- Snapshot test (if project has iOSSnapshotTestCase or similar)
- None / trust the output

If the user doesn't specify, skip validation and move on. If they say "check everything":

- Layout (spacing, alignment, sizing)
- Typography (family, size, weight, width, line height, tracking)
- Colors (fills, strokes, backgrounds, text)
- Assets (no placeholders, @1x/2x/3x present for rasters)
- Interactive states (pressed, focused, disabled)
- Dark mode parity (if Figma has dark variants)
- Dynamic Type (scales cleanly)
- Safe areas (nothing behind notch or home indicator)
- Scroll behavior

Deviations from Figma due to accessibility, platform conventions, or technical constraints should have a one-line comment at the deviation site explaining why.

---

## 11. Code Connect registration (post-build)

After creating any reusable SwiftUI component that corresponds to a Figma component, register it via `add_code_connect_map(fileKey, nodeId, componentPath, componentName)`. Only register components that are:

- **Reusable** — used in ≥2 places or clearly a primitive (Button, TextField, Card, Avatar)
- **Stable** — not a one-off screen-specific composition

One-off screens do not get Code Connect — they pollute the map and create friction when the screen is refactored. Rule of thumb: if you'd put it in a design-system folder, register it.

---

## 12. Failure modes to watch

| Symptom | Cause | Fix |
|---|---|---|
| Spacing looks "close but off" across the screen | Eyeball audit instead of reading `properties` from MCP | Re-run §3.3 spacing pass with exact values |
| Custom state enum grows to 6+ cases | Native equivalent exists (pressed, disabled, focused) | Map to `configuration.isPressed`, `@Environment(\.isEnabled)`, `@FocusState` |
| Layout breaks under Split View on iPad | `UIScreen.main.bounds` used for widths | Replace with `containerRelativeFrame` |
| Font weight right, width wrong | Figma "Expanded Semibold" has two axes | Add `.width(.expanded)` |
| Dark mode looks wrong | `Color(hex:)` everywhere, no Asset Catalog entries | Move colors to Asset Catalog with Any/Dark Appearance |
| AsyncImage introduced into a Kingfisher project | Dependency check skipped | Read `Package.swift` before picking an image loader |
| React/Tailwind from MCP pasted into SwiftUI | Treated MCP output as source | Re-read §2: MCP code is a spec |
| Back chevron implemented manually | Didn't recognize system-provided element | Remove; use `NavigationStack` |
| Component only has default variant implemented | Skipped `get_metadata` sibling fetch | Fetch all variants, map with §9 table |

---

## Extension points

- **New effect** (e.g., iOS 27 feature) → add row to §6.4 with its `View` modifier and a link to `references/ios/` if the effect is HIG-sensitive.
- **New responsive pattern** → add to §8.4 as a `ViewThatFits` or size-class case.
- **New variant taxonomy** → extend §9.1 table, keep the "native before custom enum" rule.
