# skills/design/scripts/test_compute_contrast.py
"""Tests for compute_contrast.py — WCAG 2.1 sRGB contrast calculator."""

import io
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent / "compute_contrast.py"


class TestRelativeLuminance(unittest.TestCase):
    """relative_luminance() returns the WCAG-defined L value for sRGB."""

    def setUp(self):
        # Import lazily so the test file remains runnable before the module exists
        # (run will fail at import — that's the expected RED).
        sys.path.insert(0, str(SCRIPT.parent))
        from compute_contrast import relative_luminance
        self.fn = relative_luminance

    def test_white_is_one(self):
        self.assertAlmostEqual(self.fn("#FFFFFF"), 1.0, places=4)

    def test_black_is_zero(self):
        self.assertAlmostEqual(self.fn("#000000"), 0.0, places=4)

    def test_mid_grey_known(self):
        # #777777 → ~0.1845
        self.assertAlmostEqual(self.fn("#777777"), 0.1845, places=3)

    def test_accepts_lowercase_hex(self):
        self.assertAlmostEqual(self.fn("#ffffff"), 1.0, places=4)

    def test_accepts_no_hash(self):
        self.assertAlmostEqual(self.fn("000000"), 0.0, places=4)


class TestContrastRatio(unittest.TestCase):
    """contrast_ratio(fg, bg) returns the WCAG ratio in [1, 21]."""

    def setUp(self):
        sys.path.insert(0, str(SCRIPT.parent))
        from compute_contrast import contrast_ratio
        self.fn = contrast_ratio

    def test_white_on_black_is_21(self):
        self.assertAlmostEqual(self.fn("#FFFFFF", "#000000"), 21.0, places=2)

    def test_black_on_white_is_21(self):
        # Symmetric: returns same ratio regardless of which is fg/bg
        self.assertAlmostEqual(self.fn("#000000", "#FFFFFF"), 21.0, places=2)

    def test_same_color_is_1(self):
        self.assertAlmostEqual(self.fn("#7A7E8C", "#7A7E8C"), 1.0, places=2)

    def test_known_pair(self):
        # #767676 on #FFFFFF → ~4.54 (WCAG AA pass for body)
        self.assertAlmostEqual(self.fn("#767676", "#FFFFFF"), 4.54, places=1)


class TestCheckPair(unittest.TestCase):
    """check(fg, bg, threshold) returns (ratio, pass_bool)."""

    def setUp(self):
        sys.path.insert(0, str(SCRIPT.parent))
        from compute_contrast import check
        self.fn = check

    def test_white_on_black_passes_aaa(self):
        ratio, ok = self.fn("#FFFFFF", "#000000", 7.0)
        self.assertTrue(ok)
        self.assertGreater(ratio, 7.0)

    def test_low_contrast_fails(self):
        ratio, ok = self.fn("#CCCCCC", "#FFFFFF", 4.5)
        self.assertFalse(ok)
        self.assertLess(ratio, 4.5)


class TestCLI(unittest.TestCase):
    """CLI: read JSON pairs from stdin, write JSON report to stdout."""

    def run_cli(self, payload):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)

    def test_single_pair_aa_body(self):
        out = self.run_cli({
            "pairs": [
                {"name": "primary-on-surface", "fg": "#000000", "bg": "#FFFFFF", "threshold": 4.5}
            ]
        })
        self.assertEqual(len(out["results"]), 1)
        r = out["results"][0]
        self.assertEqual(r["name"], "primary-on-surface")
        self.assertAlmostEqual(r["ratio"], 21.0, places=2)
        self.assertTrue(r["pass"])

    def test_multiple_pairs(self):
        out = self.run_cli({
            "pairs": [
                {"name": "a", "fg": "#FFFFFF", "bg": "#000000", "threshold": 4.5},
                {"name": "b", "fg": "#CCCCCC", "bg": "#FFFFFF", "threshold": 4.5},
            ]
        })
        self.assertEqual(len(out["results"]), 2)
        self.assertTrue(out["results"][0]["pass"])
        self.assertFalse(out["results"][1]["pass"])

    def test_empty_pairs(self):
        out = self.run_cli({"pairs": []})
        self.assertEqual(out["results"], [])


if __name__ == "__main__":
    unittest.main()
