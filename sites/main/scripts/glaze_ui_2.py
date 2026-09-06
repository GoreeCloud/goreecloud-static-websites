"""Glaze UI 2.1 public-site normalization helpers.

The main GoreeCloud site has several deployable HTML templates. This helper keeps
all of them on the same Stable Glaze UI contract and preserves compatibility for
older source fragments while the canonical templates are made source-native.
Current public facts must remain authoritative in source and generated artifacts.
"""

from __future__ import annotations

GLAZE_VERSION = "2.1.0"
GLAZE_PROMOTION_REVISION = "c49113eb8b93c267613fdf1bbca1f814495acad7"
GLAZE_BUNDLE = "css/glaze-ui-2.1.0.css"

FILE_MANAGER_CARD = '''<article class="service-card suite-card" data-suite-app="file-manager">
  <div class="service-art suite-art" aria-hidden="true"><span class="repo-mark">FM</span></div>
  <h3>GoreeCloud File Manager</h3>
  <p class="suite-description"><strong>Description:</strong> First-party file-management experience for local and connected GoreeCloud storage surfaces.</p>
  <p class="suite-role"><strong>Role:</strong> File-management experience across local and connected GoreeCloud storage.</p>
  <span class="badge growing">Active Development</span>
</article>'''

MAPS_CARD = '''<article class="service-card suite-card" data-suite-app="maps">
  <div class="service-art suite-art" aria-hidden="true"><span class="repo-mark">MP</span></div>
  <h3>GoreeCloud Maps</h3>
  <p class="suite-description"><strong>Description:</strong> GoreeCloud mapping experience with privacy, location, navigation, and identity boundaries kept explicit.</p>
  <p class="suite-role"><strong>Role:</strong> First-party maps, navigation, and location presentation experience.</p>
  <span class="badge growing">Active Development</span>
</article>'''

APP_STORE_CARD = '''<article class="service-card suite-card" data-suite-app="app-store">
  <div class="service-art suite-art" aria-hidden="true"><span class="repo-mark">AS</span></div>
  <h3>GoreeCloud App Store</h3>
  <p class="suite-description"><strong>Description:</strong> Official multi-user catalog for discovering GoreeCloud applications and services according to account access and entitlement.</p>
  <p class="suite-role"><strong>Role:</strong> GoreeCloud application and service discovery catalog with account and entitlement boundaries.</p>
  <span class="badge growing">Active Development</span>
</article>'''


def _insert_suite_card_after(html: str, anchor_id: str, card: str) -> str:
    """Insert a current Suite card after a rendered manifest card, idempotently."""
    card_id = card.split('data-suite-app="', 1)[1].split('"', 1)[0]
    if f'data-suite-app="{card_id}"' in html:
        return html
    marker = f'data-suite-app="{anchor_id}"'
    start = html.find(marker)
    if start < 0:
        raise ValueError(f"Suite card anchor missing: {anchor_id}")
    end = html.find("</article>", start)
    if end < 0:
        raise ValueError(f"Suite card boundary missing: {anchor_id}")
    end += len("</article>")
    return html[:end] + "\n            " + card + html[end:]


def apply_glaze_ui_2(html: str) -> str:
    replacements = (
        ('name="goreecloud-glaze-ui" content="1.5.0"', 'name="goreecloud-glaze-ui" content="2.1.0"'),
        ('name="goreecloud-glaze-ui" content="2.0.0"', 'name="goreecloud-glaze-ui" content="2.1.0"'),
        ('href="/css/glaze-ui-1.5.0.css" data-glaze-ui="1.5.0"', 'href="/css/glaze-ui-2.1.0.css" data-glaze-ui="2.1.0"'),
        ('href="/css/glaze-ui-2.0.0.css" data-glaze-ui="2.0.0"', 'href="/css/glaze-ui-2.1.0.css" data-glaze-ui="2.1.0"'),
        ('href="css/glaze-ui-1.5.0.css" data-glaze-ui="1.5.0"', 'href="css/glaze-ui-2.1.0.css" data-glaze-ui="2.1.0"'),
        ('href="css/glaze-ui-2.0.0.css" data-glaze-ui="2.0.0"', 'href="css/glaze-ui-2.1.0.css" data-glaze-ui="2.1.0"'),
        ('class="site-header"', 'class="site-header glaze-material-soft"'),
        ('class="site-nav"', 'class="site-nav glaze-navigation-capsule"'),
        ('class="button primary"', 'class="button primary glaze-button"'),
        ('class="button secondary"', 'class="button secondary glaze-button"'),
        ('class="hero-card"', 'class="hero-card glaze-material"'),
        ('class="repo-summary"', 'class="repo-summary"'),
        ('Glaze UI 1.5.0 is the current Stable', 'Glaze UI 2.1.0 is the current Stable'),
        ('Glaze UI 2.0.0 is the current Stable', 'Glaze UI 2.1.0 is the current Stable'),
        ('Glaze UI 1.5 is the current Stable', 'Glaze UI 2.1 is the current Stable'),
        ('Glaze UI 2.0 is the current Stable', 'Glaze UI 2.1 is the current Stable'),
        ('Glaze UI 1.5 Stable', 'Glaze UI 2.1 Stable'),
        ('Glaze UI 2.0 Stable', 'Glaze UI 2.1 Stable'),
        ('Stable 1.5', 'Stable 2.1'),
        ('Stable 2.0', 'Stable 2.1'),
        (
            'The public portfolio uses Glaze UI 2.0.0 Stable as its production design target.',
            'The public portfolio uses Glaze UI 2.1.0 Stable as its current design target; each independently deployed site must still earn exact-revision deployment acceptance.',
        ),
        (
            'The public portfolio is migrating to Glaze UI 2.1.0 Stable as its current design target; each independently deployed site must still earn exact 2.1 deployment acceptance.',
            'The public portfolio uses Glaze UI 2.1.0 Stable as its current design target; each independently deployed site must still earn exact-revision deployment acceptance.',
        ),
        (
            'The GoreeCloud Design Center for Glaze UI 2.0.0 Stable: interaction, material, adaptive form factors, accessibility, motion, visual language, and design-system governance. Glaze UI 2.1 remains Candidate.',
            'The GoreeCloud Design Center for Glaze UI 2.1.0 Stable: interaction, material, adaptive form factors, accessibility, motion, visual language, and design-system governance.',
        ),
        (
            'Glaze UI 2.1 remains Candidate and is not a Stable consumer-conformance target.',
            'Glaze UI 2.1.0 is Stable; each downstream consumer must still earn repository-local acceptance for its supported scope.',
        ),
        ('current 53-repository portfolio', 'current 57-repository portfolio'),
        ('current 56-repository portfolio', 'current 57-repository portfolio'),
        ('the five substantive platform systems', 'the six substantive platform systems'),
        (
            'Glaze UI, Privacy Shield, Wardveil Security, Everkeep, and GoreeCloud Mesh remain substantive platform systems',
            'Glaze UI, Privacy Shield, Wardveil Security, Everkeep, GoreeCloud Mesh, and GoreeCloud Identity remain substantive platform systems',
        ),
    )
    for old, new in replacements:
        html = html.replace(old, new)

    # Keep Main's public Suite directory synchronized with the dedicated Suite
    # website for newly current products whose canonical artwork is still
    # pending. Neutral text marks are presentation placeholders, not logos.
    if 'data-suite-app="drive"' in html:
        html = _insert_suite_card_after(html, "drive", FILE_MANAGER_CARD)
        html = _insert_suite_card_after(html, "location", MAPS_CARD)
        html = _insert_suite_card_after(html, "launcher", APP_STORE_CARD)
        html = html.replace(
            'Status labels describe GoreeCloud lifecycle and acceptance state, not upstream project maturity. A source repository, milestone, beta, or release-candidate label does not imply production approval unless the card explicitly states a Stable or current-service status.',
            'Status labels describe GoreeCloud lifecycle and acceptance state, not upstream project maturity. A source repository, milestone, beta, or release-candidate label does not imply production approval unless the card explicitly states a Stable or current-service status. Products without approved canonical artwork use a neutral text mark until the branding authority publishes an approved asset.',
        )
    return html