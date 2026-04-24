---
name: figma-integration-hub
description: Routing index for Figma integration references. Determines which sub-reference to load based on the user's intent (build, adapt, implement, map) and platform (web, iOS).
---

# Figma integration — routing hub

This folder is loaded by `/design` pipelines whenever the Figma MCP (`mcp__*figma*__*` tools) is available and the task touches Figma. The hub decides **what to load next** — do not treat any file here as default reading.

## Prerequisite

For every write operation (`use_figma`), the top-level skill [`skills/figma-use/`](../../../figma-use/SKILL.md) must be loaded. It carries the Plugin API contract (return pattern, font loading, color ranges, node-id format). Skipping it is the #1 cause of silent failures.

## Routing table

| User intent + context | Load |
|---|---|
| "Build a new screen in Figma from our design system" | [`generate-design/SKILL.md`](generate-design/SKILL.md) + `figma-use` |
| "Create / rebuild / extend the design system **in Figma**" (from code or from scratch) | [`generate-library/SKILL.md`](generate-library/SKILL.md) + `figma-use` |
| "Implement this Figma frame as **iOS / SwiftUI** code" | [`ios-swiftui.md`](ios-swiftui.md) |
| "Implement this Figma frame as **web / React / Vue / Svelte** code" | [`implement-design/SKILL.md`](implement-design/SKILL.md) |
| "I need a fresh blank Figma file before we start" | [`create-new-file/SKILL.md`](create-new-file/SKILL.md) |
| "Set up Figma-to-code rules for this project" | [`design-system-rules/SKILL.md`](design-system-rules/SKILL.md) |
| "Connect these Figma components to the code ones" (batch, no `.figma.ts`) | [`code-connect-batch.md`](code-connect-batch.md) |
| "Tweak node 42:15 — move / resize / re-bind variable" | [`figma-use`](../../../figma-use/SKILL.md) alone — point-edit flow |

## Platform router for `/design craft` and `/design make`

When a Figma URL is given:

```
if --platform ios           →  ios-swiftui.md
elif --platform web         →  implement-design/
elif --platform cross       →  detect project (Package.swift/xcodeproj → ios, package.json → web), ask if ambiguous
```

When building **in Figma** (not from Figma):

```
if "design system" / "tokens" / "library"  →  generate-library/
if "screen" / "page" / "view"              →  generate-design/
```

## What this folder does NOT contain

- **`figma-use`** — lives at `skills/figma-use/` as a top-level skill. It's required before every Plugin-API write, so the model-invocation layer needs it discoverable independently.
- **`figma-code-connect` (template `.figma.ts` version)** — deliberately excluded from this release. Requires Org/Enterprise plan + `tsconfig.json` changes. Batch version (`code-connect-batch.md`) covers the 90% case without those prerequisites.

## Extension points

- New platform variant (e.g., Android Jetpack Compose from Figma) → add a sibling file `android-compose.md` + row in the platform router table.
- New MCP tool surfaces → add a row to the routing table above pointing to the appropriate sub-reference.
