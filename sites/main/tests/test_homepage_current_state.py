from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from normalize_homepage import normalize_homepage  # noqa: E402
from render_repository_portfolio import load_manifest, render_public_file  # noqa: E402


class HomepageCurrentStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        rendered = render_public_file("index.html", source, load_manifest(ROOT))
        cls.homepage = normalize_homepage(rendered)
        cls.homepage_css = (ROOT / "css" / "homepage-v6.css").read_text(encoding="utf-8")
        cls.websites_css = (ROOT / "css" / "websites.css").read_text(encoding="utf-8")

    def test_hero_is_focused_without_platform_system_duplication(self) -> None:
        hero = self.homepage.split("<h1>", 1)[0]
        self.assertIn("Private • Self-hosted • Recoverable", hero)
        for label in (
            "Glaze UI",
            "Privacy Shield",
            "Wardveil Security",
            "Everkeep",
            "GoreeCloud Mesh",
            "GoreeCloud Identity",
        ):
            with self.subTest(label=label):
                self.assertNotIn(label, hero)
        self.assertNotIn('<section class="band" aria-label="Core principles">', self.homepage)

    def test_hero_visual_contract_rejects_chip_stack_and_narrow_title(self) -> None:
        hero = self.homepage.split("<h1>", 1)[0]
        self.assertNotIn('class="glaze-chip"', hero)
        self.assertIn('.hero .hero-labels .glaze-chip', self.homepage_css)
        self.assertIn('display: none !important;', self.homepage_css)
        self.assertIn('max-width: 13.7ch;', self.homepage_css)
        self.assertIn('grid-template-columns: minmax(0, 1.16fr) minmax(360px, .84fr);', self.homepage_css)
        self.assertIn('background: transparent;', self.homepage_css)

    def test_main_homepage_is_a_website_hub(self) -> None:
        self.assertEqual(self.homepage.count('id="websites"'), 1)
        domains = (
            "goreecloud.com",
            "suite.goreecloud.com",
            "projects.goreecloud.com",
            "design.goreecloud.com",
            "privacy.goreecloud.com",
            "security.goreecloud.com",
            "everkeep.goreecloud.com",
            "roadmap.goreecloud.com",
            "blog.goreecloud.com",
            "archive.goreecloud.com",
            "identity.goreecloud.com",
        )
        for domain in domains:
            with self.subTest(domain=domain):
                self.assertEqual(self.homepage.count(f'<p class="service-kicker">{domain}</p>'), 1)
        self.assertEqual(self.homepage.count('class="service-card website-card '), 11)
        self.assertIn('<a href="#websites">Websites</a>', self.homepage)
        self.assertIn('<a href="https://suite.goreecloud.com/">Suite</a>', self.homepage)
        self.assertIn('css/websites.css', self.homepage)
        self.assertIn('css/homepage-v6.css', self.homepage)

    def test_website_cards_are_concise_without_browser_mockups(self) -> None:
        self.assertNotIn('website-preview', self.homepage)
        self.assertNotIn('website-preview-browser', self.homepage)
        self.assertNotIn('.website-preview', self.websites_css)
        self.assertNotIn('website-preview', self.homepage_css)
        self.assertEqual(self.homepage.count('class="website-card-body"'), 11)
        self.assertEqual(self.homepage.count('class="website-card-head"'), 11)
        self.assertEqual(self.homepage.count('class="website-mark"'), 11)
        self.assertEqual(self.homepage.count('class="website-link"'), 11)

    def test_website_grid_balances_all_eleven_destinations(self) -> None:
        self.assertIn('.website-card:nth-child(n+8) { grid-column: span 3; }', self.homepage_css)
        self.assertIn('.website-card:last-child {', self.homepage_css)
        self.assertIn('grid-column: 1 / -1;', self.homepage_css)

    def test_mobile_reading_rhythm_keeps_interaction_and_content_distinct(self) -> None:
        self.assertIn('.site-nav.open {', self.homepage_css)
        self.assertIn(
            'background: color-mix(in srgb, var(--glaze-surface-elevated) 94%, transparent);',
            self.homepage_css,
        )
        self.assertIn('row-gap: 1.35rem;', self.homepage_css)
        self.assertIn('font-size: .96rem;', self.homepage_css)

    def test_website_names_are_visible_once_as_card_titles(self) -> None:
        names = (
            "GoreeCloud",
            "GoreeCloud Suite",
            "GoreeCloud Projects",
            "Glaze UI",
            "Privacy Shield",
            "Wardveil Security",
            "Everkeep",
            "GoreeCloud Roadmap",
            "GoreeCloud Blog",
            "GoreeCloud Archive",
            "GoreeCloud Identity",
        )
        for name in names:
            with self.subTest(name=name):
                self.assertEqual(self.homepage.count(f'<h3>{name}</h3>'), 1)

    def test_everkeep_has_a_dedicated_public_destination(self) -> None:
        self.assertIn('https://everkeep.goreecloud.com/', self.homepage)
        self.assertIn('<h3>Everkeep</h3>', self.homepage)
        self.assertIn('resilience, backup, recovery, preservation, portability, succession, legacy, and evidence-backed continuity', self.homepage)

    def test_suite_and_capability_cards_moved_off_main_homepage(self) -> None:
        self.assertNotIn('data-suite-app=', self.homepage)
        self.assertNotIn('data-capability=', self.homepage)
        self.assertNotIn('<p class="eyebrow">GoreeCloud Suite</p>', self.homepage)
        self.assertNotIn('<p class="eyebrow">Umbrella Capabilities</p>', self.homepage)

    def test_goreecloud_ai_replaces_retired_front_ends_in_roadmap(self) -> None:
        self.assertIn('data-roadmap="goreecloud-ai"', self.homepage)
        self.assertIn('<h3>GoreeCloud AI</h3>', self.homepage)
        self.assertIn('src="assets/suite/ai.svg"', self.homepage)
        self.assertNotIn("Open WebUI", self.homepage)
        self.assertNotIn("AnythingLLM", self.homepage)
        self.assertIn("Local model runtime support", self.homepage)
        self.assertIn("Keep model runtimes replaceable", self.homepage)
        self.assertIn("Controlled web research through GoreeCloud Search", self.homepage)


if __name__ == "__main__":
    unittest.main()
