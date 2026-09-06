#!/usr/bin/env python3
"""Protect Glaze UI theme-aware surfaces from dark fallback regressions."""

from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPOSITORIES_CSS = (ROOT / "css" / "repositories.css").read_text(encoding="utf-8")
PLATFORM_CSS = (ROOT / "css" / "platform.css").read_text(encoding="utf-8")
GLAZE_CSS = (ROOT / "css" / "glaze.css").read_text(encoding="utf-8")


class ThemeSurfaceContractTests(unittest.TestCase):
    def test_repository_surfaces_use_canonical_glaze_tokens(self) -> None:
        for marker in (
            "var(--glaze-surface)",
            "var(--glaze-surface-strong)",
            "var(--glaze-line)",
            "var(--glaze-muted)",
        ):
            self.assertIn(marker, REPOSITORIES_CSS)

        self.assertNotIn("--surface-glaze", REPOSITORIES_CSS)
        self.assertNotIn("--surface-raised", REPOSITORIES_CSS)

    def test_platform_surfaces_follow_theme_tokens(self) -> None:
        self.assertIn("var(--glaze-surface-strong)", PLATFORM_CSS)
        self.assertIn("var(--glaze-surface)", PLATFORM_CSS)
        self.assertIn("var(--muted-strong)", PLATFORM_CSS)
        self.assertNotIn("background: rgba(5,13,29,.58)", PLATFORM_CSS)

    def test_light_theme_defines_surface_and_text_roles(self) -> None:
        light_block = GLAZE_CSS.split(':root[data-theme="light"]', 1)[1].split("@media (prefers-color-scheme: light)", 1)[0]
        for marker in (
            "--glaze-surface:",
            "--glaze-surface-strong:",
            "--glaze-text:",
            "--glaze-muted:",
            "--glaze-line:",
        ):
            self.assertIn(marker, light_block)


if __name__ == "__main__":
    unittest.main()
