from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class MobileNavigationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.styles = (ROOT / "css" / "style.css").read_text(encoding="utf-8")
        cls.script = (ROOT / "js" / "main.js").read_text(encoding="utf-8")

    def test_mobile_navigation_is_hidden_until_opened(self) -> None:
        self.assertIn(".site-nav:not(.open) { display: none; }", self.styles)
        self.assertIn(".site-nav.open {", self.styles)
        self.assertIn("display: grid;", self.styles)

    def test_mobile_navigation_uses_compact_bounded_popover(self) -> None:
        self.assertIn("width: min(20rem, calc(100vw - 1.4rem));", self.styles)
        self.assertIn(
            "max-height: calc(100dvh - 96px - env(safe-area-inset-bottom));",
            self.styles,
        )
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr));", self.styles)
        self.assertIn("overscroll-behavior: contain;", self.styles)
        self.assertIn(".site-nav.open .nav-cta { grid-column: 1 / -1; }", self.styles)

    def test_navigation_keeps_accessible_close_paths(self) -> None:
        self.assertIn("nav.classList.toggle('open')", self.script)
        self.assertIn("if (nav.contains(event.target) || navToggle.contains(event.target)) return;", self.script)
        self.assertIn("if (event.key === 'Escape' && nav.classList.contains('open'))", self.script)
        self.assertIn("closeNavigation({ restoreFocus: true })", self.script)


if __name__ == "__main__":
    unittest.main()
