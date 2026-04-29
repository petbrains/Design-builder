# skills/design/scripts/compute_contrast.py
"""WCAG 2.1 sRGB contrast calculator.

Used by /setup Phase 5b to fill the contrast table in design/style-guide.md
for the chosen palette × ink combinations.

CLI: read JSON {"pairs": [{name, fg, bg, threshold}, ...]} from stdin.
     write JSON {"results": [{name, ratio, pass}, ...]} to stdout.

Stdlib only.
"""

import json
import sys
from typing import Tuple


def _channel_luminance(c: int) -> float:
    """Convert one sRGB channel byte (0-255) to its linear-light value."""
    s = c / 255.0
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """Relative luminance per WCAG 2.1.

    Accepts '#RRGGBB' or 'RRGGBB', case-insensitive.
    Returns float in [0, 1]; 0 = black, 1 = white.
    """
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"expected 6 hex digits, got {hex_color!r}")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (
        0.2126 * _channel_luminance(r)
        + 0.7152 * _channel_luminance(g)
        + 0.0722 * _channel_luminance(b)
    )


def contrast_ratio(fg: str, bg: str) -> float:
    """Contrast ratio between two colors per WCAG 2.1, in [1, 21]."""
    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    lighter, darker = (l1, l2) if l1 >= l2 else (l2, l1)
    return (lighter + 0.05) / (darker + 0.05)


def check(fg: str, bg: str, threshold: float) -> Tuple[float, bool]:
    """Return (ratio, passes_threshold)."""
    r = contrast_ratio(fg, bg)
    return r, r >= threshold


def main():
    payload = json.load(sys.stdin)
    pairs = payload.get("pairs", [])
    results = []
    for p in pairs:
        ratio, ok = check(p["fg"], p["bg"], float(p["threshold"]))
        results.append({
            "name": p["name"],
            "fg": p["fg"],
            "bg": p["bg"],
            "threshold": p["threshold"],
            "ratio": round(ratio, 2),
            "pass": ok,
        })
    json.dump({"results": results}, sys.stdout)


if __name__ == "__main__":
    main()
