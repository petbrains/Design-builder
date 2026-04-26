#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a temporary, single-file HTML preview of three design-system
candidates so the user can pick A / B / C *visually* before any tokens
are written to the project.

The preview is platform-aware:
 - web → hero + button row + card + type specimen + palette swatches
 - ios → status-bar mock + nav title + list cell + button + tab bar
        + type specimen + palette swatches (faux iOS frame)
 - cross → both, stacked

Apply ≠ Approve. This script only RENDERS the preview. Writing
`tokens.css`, `.impeccable.md`, xcassets, etc. happens *after* the user
picks, in the inline `/design system` flow in SKILL.md.

Usage (called by the skill / agent):
    python generate_system_preview.py \
        --candidates path/to/candidates.json \
        --project "Kora" \
        --platform web

Where candidates.json is a list of exactly 3 objects with this shape:
    {
      "id": "A",                               # required: "A" | "B" | "C"
      "name": "Botanical Editorial",           # short label, shown on the tab
      "differentiation_hook":                  # one concrete sentence,
        "220px Playfair Bold display with a   #  required, must not be a
         terracotta dot baseline-anchored",   #  generic adjective stack
      "tone_one_liner":
        "Premium literary, paper-grain, arched shapes",
      "platform_focus": "web",                 # web | ios | cross
      "fonts": {
        "display": {"family": "Playfair Display", "google": "Playfair+Display:wght@400;700"},
        "body":    {"family": "Inter", "google": "Inter:wght@400;500;600"},
        "mono":    {"family": "JetBrains Mono", "google": "JetBrains+Mono:wght@400;500"}
      },
      "palette": {
        "bg":     "#E6E2DA",
        "fg":     "#1F1B16",
        "muted":  "#6B6258",
        "accent": "#C27B66",                   # primary CTA / hook
        "accent_fg": "#FFFFFF",
        "support":"#2D3A31",                   # secondary accent
        "border": "#D6CFC2"
      },
      "type": {
        "display_size_px": 72,
        "body_size_px":    16,
        "scale": [12, 14, 16, 18, 24, 36, 56, 72]
      },
      "radius_px": 8,
      "spacing_unit_px": 4,
      "motion": "restrained"                   # restrained | confident | maximal
    }

The script prints the absolute path of the generated HTML to stdout, on
its own line, so the calling agent can hand the path to the user. Any
diagnostic chatter goes to stderr.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import html
import json
import os
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# constants

REPO_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "system-preview.html"
VALID_IDS = ("A", "B", "C")
VALID_PLATFORMS = ("web", "ios", "cross")


# ---------------------------------------------------------------------------
# validation


def _die(msg: str, code: int = 2) -> None:
    print(f"[generate_system_preview] {msg}", file=sys.stderr)
    sys.exit(code)


def _validate_candidate(c: dict, idx: int) -> None:
    expected_id = VALID_IDS[idx]
    if c.get("id") != expected_id:
        _die(f"candidate #{idx} must have id={expected_id!r}, got {c.get('id')!r}")
    for key in ("name", "differentiation_hook", "tone_one_liner",
                "fonts", "palette", "type"):
        if not c.get(key):
            _die(f"candidate {expected_id}: missing required field {key!r}")
    hook = (c.get("differentiation_hook") or "").strip()
    # Generic-ness guard: hook must reference SOMETHING concrete (px,
    # specific font name, weight, named shape, named ratio, or a numeric
    # value). If it's only adjectives, reject — that's the bug we're
    # solving here.
    if len(hook.split()) < 5:
        _die(f"candidate {expected_id}: differentiation_hook is too short "
             f"({len(hook.split())} words). Need a concrete sentence.")
    concrete_signals = ("px", "%", "deg", "Display", "Italic", "Bold",
                        "Regular", "Medium", "Sans", "Serif", "Mono",
                        "1.", "2.", "3.", "0.", "rem", "ch", "/")
    if not any(sig in hook for sig in concrete_signals):
        _die(f"candidate {expected_id}: differentiation_hook reads as "
             f"adjectives only — needs at least one concrete reference "
             f"(font name, size, weight, ratio, %, deg). Got: {hook!r}")
    fonts = c["fonts"]
    for slot in ("display", "body"):
        if slot not in fonts or not fonts[slot].get("family"):
            _die(f"candidate {expected_id}: fonts.{slot}.family required")
    palette = c["palette"]
    for slot in ("bg", "fg", "accent"):
        if slot not in palette:
            _die(f"candidate {expected_id}: palette.{slot} required")


# ---------------------------------------------------------------------------
# CSS generation


def _google_fonts_link(candidates: list[dict]) -> str:
    families = []
    for c in candidates:
        for slot in ("display", "body", "mono"):
            f = c.get("fonts", {}).get(slot)
            if not f:
                continue
            spec = f.get("google")
            if spec:
                families.append(spec)
    if not families:
        return ""
    seen = []
    for fam in families:
        if fam not in seen:
            seen.append(fam)
    href = "https://fonts.googleapis.com/css2?" + "&".join(
        f"family={fam}" for fam in seen
    ) + "&display=swap"
    return (
        f'<link rel="preconnect" href="https://fonts.googleapis.com">'
        f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        f'<link rel="stylesheet" href="{href}">'
    )


def _variant_css(c: dict) -> str:
    vid = c["id"]
    p = c["palette"]
    f = c["fonts"]
    t = c["type"]
    radius = int(c.get("radius_px", 8))
    unit = int(c.get("spacing_unit_px", 4))
    display_family = f["display"]["family"]
    body_family = f["body"]["family"]
    mono_family = (f.get("mono") or {}).get("family") or "ui-monospace, monospace"
    display_size = int(t.get("display_size_px", 56))
    body_size = int(t.get("body_size_px", 16))

    # quoted family helpers
    def q(name: str) -> str:
        if "," in name:
            return name
        return f'"{name}"'

    return f"""
  [data-variant="{vid}"] {{
    --bg: {p['bg']};
    --fg: {p['fg']};
    --muted: {p.get('muted', p['fg'])};
    --accent: {p['accent']};
    --accent-fg: {p.get('accent_fg', '#ffffff')};
    --support: {p.get('support', p['accent'])};
    --border: {p.get('border', 'rgba(0,0,0,.1)')};
    --radius: {radius}px;
    --unit: {unit}px;
    --display: {q(display_family)}, "Times New Roman", serif;
    --body: {q(body_family)}, ui-sans-serif, system-ui, sans-serif;
    --mono: {q(mono_family)}, ui-monospace, monospace;
    --display-size: {display_size}px;
    --body-size: {body_size}px;
    background: var(--bg);
    color: var(--fg);
    font-family: var(--body);
    font-size: var(--body-size);
  }}
  [data-variant="{vid}"] .v-display {{ font-family: var(--display); }}
  [data-variant="{vid}"] .v-mono    {{ font-family: var(--mono); }}
  [data-variant="{vid}"] .v-accent  {{ color: var(--accent); }}
  [data-variant="{vid}"] .v-support {{ color: var(--support); }}
  [data-variant="{vid}"] .v-muted   {{ color: var(--muted); }}
"""


# ---------------------------------------------------------------------------
# variant body — web


def _swatch_grid(palette: dict) -> str:
    swatches = [
        ("bg", "background"),
        ("fg", "foreground"),
        ("muted", "muted"),
        ("accent", "accent"),
        ("support", "support"),
        ("border", "border"),
    ]
    cells = []
    for key, label in swatches:
        if key not in palette:
            continue
        hexv = palette[key]
        cells.append(
            f'<div class="sw"><div class="sw-chip" style="background:{html.escape(hexv)};'
            f'border:1px solid rgba(0,0,0,.06)"></div>'
            f'<div class="sw-meta"><strong>{html.escape(label)}</strong>'
            f'<code>{html.escape(hexv)}</code></div></div>'
        )
    return f'<div class="sw-grid">{"".join(cells)}</div>'


def _type_specimen(candidate: dict) -> str:
    scale = candidate.get("type", {}).get("scale") or [12, 14, 16, 18, 24, 36, 56, 72]
    rows = []
    for px in scale:
        sample = "Aa typography" if px < 20 else "Editorial typography"
        rows.append(
            f'<div class="ts-row" style="font-size:{int(px)}px">'
            f'<span class="ts-label v-mono v-muted">{int(px)}px</span>'
            f'<span class="v-display">{html.escape(sample)}</span></div>'
        )
    return f'<div class="ts">{"".join(rows)}</div>'


def _web_body(c: dict, project: str) -> str:
    hook = html.escape(c.get("differentiation_hook", ""))
    tone = html.escape(c.get("tone_one_liner", ""))
    name = html.escape(c.get("name", ""))
    headline = html.escape(f"{project} — a hero that earns its scroll.")
    sub = html.escape(
        "This is a sample on the proposed system. Real copy comes after you pick. "
        "What you should be reading right now: the typography, the rhythm, the colour story."
    )
    return f"""
<section class="web-hero">
  <header class="web-eyebrow">
    <span class="v-mono v-muted">VARIANT {c['id']} · {name}</span>
    <span class="v-mono v-muted">— {tone}</span>
  </header>
  <h1 class="web-h1 v-display">{headline}</h1>
  <p class="web-sub v-muted">{sub}</p>
  <div class="web-cta-row">
    <button class="web-cta web-cta-primary">Try it free</button>
    <button class="web-cta web-cta-ghost">See how it works <span class="v-accent">→</span></button>
  </div>
  <p class="web-hook v-mono v-support">hook · {hook}</p>
</section>

<section class="web-grid">
  <article class="web-card">
    <h3 class="v-display">Card surface</h3>
    <p class="v-muted">Rendered on a real surface token, not a screenshot. Hover to see the border response.</p>
    <div class="web-card-meta v-mono">
      <span>radius {int(c.get('radius_px', 8))}px</span>
      <span>unit {int(c.get('spacing_unit_px', 4))}px</span>
    </div>
  </article>
  <article class="web-card web-card-accent">
    <h3>On accent</h3>
    <p>The accent treatment is where the brand gets remembered. Reads as primary CTA, never decoration.</p>
  </article>
</section>

<section class="web-block">
  <h2 class="web-h2 v-display">Type</h2>
  {_type_specimen(c)}
</section>

<section class="web-block">
  <h2 class="web-h2 v-display">Palette</h2>
  {_swatch_grid(c['palette'])}
</section>
"""


# ---------------------------------------------------------------------------
# variant body — iOS (faux iPhone frame)


def _ios_body(c: dict, project: str) -> str:
    name = html.escape(c.get("name", ""))
    hook = html.escape(c.get("differentiation_hook", ""))
    tone = html.escape(c.get("tone_one_liner", ""))
    project_e = html.escape(project)
    return f"""
<div class="ios-stage">
  <div class="ios-phone">
    <div class="ios-status-bar">
      <span class="v-mono">9:41</span>
      <span class="v-mono">●●●●  ⌃  100%</span>
    </div>
    <div class="ios-nav">
      <span class="v-mono v-muted">Back</span>
      <span class="ios-nav-title v-display">{project_e}</span>
      <span class="v-mono v-accent">Edit</span>
    </div>
    <div class="ios-list">
      <div class="ios-row">
        <div class="ios-row-icon" aria-hidden="true">▣</div>
        <div class="ios-row-body">
          <div class="ios-row-title v-display">Today</div>
          <div class="ios-row-sub v-muted">3 lessons · 12 min</div>
        </div>
        <div class="ios-row-cta v-accent">→</div>
      </div>
      <div class="ios-row">
        <div class="ios-row-icon" aria-hidden="true">◧</div>
        <div class="ios-row-body">
          <div class="ios-row-title v-display">Library</div>
          <div class="ios-row-sub v-muted">Saved · 24 items</div>
        </div>
        <div class="ios-row-cta v-accent">→</div>
      </div>
      <div class="ios-row">
        <div class="ios-row-icon" aria-hidden="true">◑</div>
        <div class="ios-row-body">
          <div class="ios-row-title v-display">Streak</div>
          <div class="ios-row-sub v-muted">14 days · keep going</div>
        </div>
        <div class="ios-row-cta v-accent">→</div>
      </div>
    </div>
    <div class="ios-cta-wrap">
      <button class="ios-cta">Start a lesson</button>
    </div>
    <div class="ios-tab-bar">
      <span class="ios-tab v-accent">● Home</span>
      <span class="ios-tab v-muted">Library</span>
      <span class="ios-tab v-muted">Profile</span>
    </div>
  </div>

  <aside class="ios-meta">
    <header>
      <span class="v-mono v-muted">VARIANT {c['id']} · {name}</span>
      <p class="v-muted">{tone}</p>
    </header>
    <div class="ios-block">
      <h2 class="v-display">Type</h2>
      {_type_specimen(c)}
    </div>
    <div class="ios-block">
      <h2 class="v-display">Palette</h2>
      {_swatch_grid(c['palette'])}
    </div>
    <p class="ios-hook v-mono v-support">hook · {hook}</p>
  </aside>
</div>
"""


def _cross_body(c: dict, project: str) -> str:
    return _web_body(c, project) + _ios_body(c, project)


# ---------------------------------------------------------------------------
# layout CSS shared across variants (web + iOS frames)

_LAYOUT_CSS = """
  /* web layout */
  .web-hero {
    padding: clamp(48px, 8vw, 96px) clamp(24px, 5vw, 80px) 24px;
  }
  .web-eyebrow { display: flex; gap: 16px; flex-wrap: wrap; font-size: 12px; letter-spacing: .04em; text-transform: uppercase; margin-bottom: 28px; }
  .web-h1 { font-size: clamp(40px, 6vw, var(--display-size, 72px)); line-height: 1.05; letter-spacing: -0.02em; max-width: 18ch; font-weight: 600; }
  .web-sub { margin-top: 22px; font-size: clamp(16px, 1.4vw, 20px); line-height: 1.55; max-width: 56ch; }
  .web-cta-row { display: flex; gap: 14px; margin-top: 36px; flex-wrap: wrap; }
  .web-cta { appearance: none; border: 1px solid var(--border); padding: 14px 22px; border-radius: var(--radius); font: inherit; font-weight: 500; cursor: pointer; background: transparent; color: var(--fg); transition: transform .15s ease, background .15s ease; }
  .web-cta:hover { transform: translateY(-1px); }
  .web-cta-primary { background: var(--accent); color: var(--accent-fg); border-color: var(--accent); }
  .web-cta-ghost { background: transparent; }
  .web-hook { margin-top: 36px; font-size: 12px; letter-spacing: .02em; }

  .web-grid {
    display: grid; gap: 20px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    padding: 12px clamp(24px, 5vw, 80px) 32px;
  }
  .web-card {
    border: 1px solid var(--border); border-radius: var(--radius); padding: 24px;
    background: color-mix(in srgb, var(--bg) 92%, white);
    transition: border-color .2s ease;
  }
  .web-card:hover { border-color: color-mix(in srgb, var(--accent) 60%, var(--border)); }
  .web-card h3 { font-size: 22px; margin-bottom: 8px; line-height: 1.2; }
  .web-card p { font-size: 14px; line-height: 1.55; }
  .web-card-meta { display: flex; gap: 14px; margin-top: 14px; font-size: 11px; letter-spacing: .04em; opacity: .7; }
  .web-card-accent { background: var(--accent); color: var(--accent-fg); border-color: var(--accent); }
  .web-card-accent h3, .web-card-accent p { color: var(--accent-fg); }
  .web-block { padding: 32px clamp(24px, 5vw, 80px); border-top: 1px solid var(--border); }
  .web-h2 { font-size: 28px; margin-bottom: 18px; letter-spacing: -0.01em; }

  .ts { display: grid; gap: 8px; }
  .ts-row { display: grid; grid-template-columns: 60px 1fr; align-items: baseline; gap: 16px; line-height: 1.05; }
  .ts-label { font-size: 11px; letter-spacing: .04em; }

  .sw-grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
  .sw { display: flex; gap: 12px; align-items: center; }
  .sw-chip { width: 44px; height: 44px; border-radius: 8px; flex: none; }
  .sw-meta { display: flex; flex-direction: column; gap: 2px; }
  .sw-meta strong { font-size: 13px; font-weight: 500; }
  .sw-meta code { font-family: var(--mono); font-size: 11px; opacity: .7; }

  /* iOS layout */
  .ios-stage {
    display: grid; gap: 28px; padding: clamp(28px, 5vw, 56px) clamp(20px, 5vw, 56px);
    grid-template-columns: minmax(0, 380px) 1fr; align-items: start;
  }
  @media (max-width: 880px) {
    .ios-stage { grid-template-columns: 1fr; }
  }
  .ios-phone {
    border: 1px solid var(--border); border-radius: 36px;
    background: color-mix(in srgb, var(--bg) 96%, white);
    padding: 14px 12px 18px; box-shadow: 0 30px 60px -30px rgba(0,0,0,.18);
    overflow: hidden; position: relative;
  }
  .ios-status-bar { display: flex; justify-content: space-between; padding: 4px 12px 14px; font-size: 11px; }
  .ios-nav { display: flex; justify-content: space-between; align-items: baseline; padding: 4px 16px 14px; font-size: 13px; }
  .ios-nav-title { font-size: 26px; line-height: 1; letter-spacing: -0.01em; }
  .ios-list { display: flex; flex-direction: column; }
  .ios-row { display: grid; grid-template-columns: 36px 1fr 24px; gap: 12px; align-items: center; padding: 14px 16px; border-top: 1px solid var(--border); }
  .ios-row:first-child { border-top: 0; }
  .ios-row-icon { width: 32px; height: 32px; border-radius: 8px; background: color-mix(in srgb, var(--accent) 14%, transparent); color: var(--accent); display: grid; place-items: center; font-size: 16px; }
  .ios-row-title { font-size: 16px; line-height: 1.2; }
  .ios-row-sub { font-size: 12px; margin-top: 2px; }
  .ios-row-cta { font-size: 18px; text-align: right; }
  .ios-cta-wrap { padding: 18px 16px 8px; }
  .ios-cta { width: 100%; appearance: none; border: 0; padding: 14px 18px; border-radius: calc(var(--radius) + 4px); background: var(--accent); color: var(--accent-fg); font: inherit; font-weight: 600; cursor: pointer; }
  .ios-tab-bar { display: flex; justify-content: space-around; padding: 14px 12px 6px; font-size: 11px; border-top: 1px solid var(--border); margin-top: 8px; }
  .ios-meta { display: grid; gap: 22px; }
  .ios-meta header p { font-size: 14px; margin-top: 6px; }
  .ios-block h2 { font-size: 22px; margin-bottom: 12px; }
  .ios-hook { font-size: 12px; letter-spacing: .02em; }
"""


# ---------------------------------------------------------------------------
# render


def _render(template: str, candidates: list[dict], project: str, platform: str) -> str:
    body_renderer = {"web": _web_body, "ios": _ios_body, "cross": _cross_body}[platform]
    variant_html = {c["id"]: body_renderer(c, project) for c in candidates}
    variant_css = "".join(_variant_css(c) for c in candidates) + _LAYOUT_CSS
    google_fonts = _google_fonts_link(candidates)
    out = template
    out = out.replace("{{PROJECT_NAME}}", html.escape(project))
    out = out.replace("{{PLATFORM}}", html.escape(platform))
    out = out.replace("{{VARIANT_CSS}}", variant_css)
    for c in candidates:
        out = out.replace(f"{{{{VARIANT_{c['id']}_NAME}}}}", html.escape(c["name"]))
        out = out.replace(f"{{{{VARIANT_{c['id']}_HTML}}}}", variant_html[c["id"]])
    out = out.replace(
        "{{GENERATED_AT}}",
        _dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    if google_fonts:
        out = out.replace("</head>", google_fonts + "</head>", 1)
    return out


# ---------------------------------------------------------------------------
# CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidates", required=True,
                        help="Path to JSON array of exactly 3 candidate objects.")
    parser.add_argument("--project", default="Untitled",
                        help="Project name shown in the top bar.")
    parser.add_argument("--platform", choices=VALID_PLATFORMS, default="web",
                        help="Render target. cross renders both web and ios mocks.")
    parser.add_argument("--out", default=None,
                        help="Optional output path. Default: a fresh tempfile.")
    parser.add_argument("--template", default=str(REPO_TEMPLATE),
                        help="Template path. Defaults to the repo template.")
    args = parser.parse_args(argv)

    candidates_path = Path(args.candidates)
    if not candidates_path.exists():
        _die(f"candidates file not found: {candidates_path}")
    try:
        candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        _die(f"candidates file is not valid JSON: {e}")
    if not isinstance(candidates, list) or len(candidates) != 3:
        _die("candidates must be a JSON list of exactly 3 objects.")
    for idx, c in enumerate(candidates):
        _validate_candidate(c, idx)

    template_path = Path(args.template)
    if not template_path.exists():
        _die(f"template not found: {template_path}")
    template = template_path.read_text(encoding="utf-8")

    rendered = _render(template, candidates, args.project, args.platform)

    if args.out:
        out_path = Path(args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
    else:
        fd, tmp = tempfile.mkstemp(prefix="design-system-preview-", suffix=".html")
        os.close(fd)
        out_path = Path(tmp)
        out_path.write_text(rendered, encoding="utf-8")

    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
