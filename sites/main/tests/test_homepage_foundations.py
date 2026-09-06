from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from glaze_ui_2 import apply_glaze_ui_2  # noqa: E402
from normalize_homepage import normalize_homepage  # noqa: E402
from render_repository_portfolio import load_manifest, render_public_file  # noqa: E402

INDEX = ROOT / "index.html"
CONTRACT = ROOT / "docs" / "homepage-foundations-integration.md"


class HomepageFoundationsContractTests(unittest.TestCase):
    def setUp(self) -> None:
        source = INDEX.read_text(encoding="utf-8")
        rendered = render_public_file("index.html", source, load_manifest(ROOT))
        rendered = normalize_homepage(rendered)
        self.index = apply_glaze_ui_2(rendered)
        self.contract = CONTRACT.read_text(encoding="utf-8")

    def test_homepage_exposes_all_three_foundations(self) -> None:
        expected = {
            "Glaze UI": "https://design.goreecloud.com/",
            "Privacy Shield": "https://privacy.goreecloud.com/",
            "Wardveil Security": "https://security.goreecloud.com/",
        }
        for label, url in expected.items():
            with self.subTest(label=label):
                self.assertIn(f'href="{url}"', self.index)
                self.assertIn(f"<h3>{label}</h3>", self.index)

    def test_homepage_keeps_scopes_separate(self) -> None:
        # The current homepage keeps the hero focused and places platform-system
        # authority on the rendered ecosystem cards rather than duplicating it in
        # the hero. The footer still states the three original role boundaries.
        self.assertIn('aria-label="GoreeCloud platform focus"', self.index)
        self.assertIn("Private • Self-hosted • Recoverable", self.index)
        self.assertIn('<strong>Glaze UI</strong> design', self.index)
        self.assertIn('<strong>Privacy Shield</strong> privacy', self.index)
        self.assertIn('<strong>Wardveil Security</strong> security', self.index)
        for system in (
            "Glaze UI",
            "Privacy Shield",
            "Wardveil Security",
            "Everkeep",
            "GoreeCloud Mesh",
            "GoreeCloud Identity",
        ):
            self.assertIn(system, self.index)
        self.assertIn("six substantive platform systems", self.index)

    def test_contract_preserves_authority_boundaries(self) -> None:
        self.assertIn("design and interaction authority", self.contract)
        self.assertIn("privacy and privacy-control identity", self.contract)
        self.assertIn("security and protection identity", self.contract)
        self.assertIn("must not imply that Privacy Shield and Wardveil are the same authority", self.contract)
        self.assertIn("must not imply", self.contract)
        self.assertIn("blanket Wardveil protection assurance", self.contract)
        self.assertIn("unverified Privacy Shield enforcement runtime", self.contract)


if __name__ == "__main__":
    unittest.main()
