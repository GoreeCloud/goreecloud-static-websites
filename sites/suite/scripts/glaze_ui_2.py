"""Normalize the GoreeCloud Suite public HTML onto Glaze UI 2.1.0 Stable.

The build boundary upgrades superseded Glaze UI markers and reconciles historical
Suite source text without manufacturing product inventory. Approved application
artwork belongs in the canonical source template; the normalizer must never add a
placeholder or duplicate an already governed product card.
"""

from __future__ import annotations

GLAZE_VERSION = "2.1.0"
GLAZE_PROMOTION_REVISION = "c49113eb8b93c267613fdf1bbca1f814495acad7"

IDENTITY_SYSTEM = '''<div><strong>GoreeCloud Identity · Identity Center</strong><span>identity, authentication, authorization, accounts, devices, credentials, sessions, and delegated authority</span></div>'''

OLD_FILE_MANAGER_CARD = '''<article class="app-card"><span class="app-mark app-mark-pending" aria-hidden="true">FM</span><h4>GoreeCloud File Manager</h4><p>First-party file-management experience for local and connected GoreeCloud storage surfaces.</p><span class="badge growing">Active Development</span></article>'''
FILE_MANAGER_CARD = '''<article class="app-card"><img src="assets/suite/file-manager.svg" alt="" width="56" height="56"><h4>GoreeCloud File Manager</h4><p>First-party provider-spanning file-management experience for local, cloud, synchronized, removable, network, backup, and continuity storage contexts.</p><span class="badge growing">Active Development</span></article>'''

OLD_MAPS_CARD = '''<article class="app-card"><span class="app-mark app-mark-pending" aria-hidden="true">MP</span><h4>GoreeCloud Maps</h4><p>GoreeCloud mapping experience with privacy, location, navigation, and identity boundaries kept explicit.</p><span class="badge growing">Active Development</span></article>'''
MAPS_CARD = '''<article class="app-card"><img src="assets/suite/maps.svg" alt="" width="56" height="56"><h4>GoreeCloud Maps</h4><p>Mapping, spatial exploration, route understanding, and navigation experience kept distinct from GoreeCloud Location's positioning authority.</p><span class="badge growing">Active Development</span></article>'''

OLD_APP_STORE_CARD = '''<article class="app-card"><span class="app-mark app-mark-pending" aria-hidden="true">AS</span><h4>GoreeCloud App Store</h4><p>Official multi-user catalog for discovering GoreeCloud applications and services according to account access and entitlement.</p><span class="badge growing">Active Development</span></article>'''
APP_STORE_CARD = '''<article class="app-card"><img src="assets/suite/app-store.svg" alt="" width="56" height="56"><h4>GoreeCloud App Store</h4><p>Official first-party software catalog for discovering, obtaining, updating, and opening GoreeCloud applications and services according to account access and entitlement.</p><span class="badge growing">Active Development</span></article>'''


def _insert_after(html: str, anchor: str, addition: str) -> str:
    if addition in html:
        return html
    if anchor not in html:
        raise ValueError(f"Suite content anchor missing: {anchor[:72]}")
    return html.replace(anchor, anchor + "\n            " + addition, 1)


def apply_glaze_ui_2(html: str) -> str:
    replacements = (
        ('name="goreecloud-glaze-ui" content="1.5.0"', 'name="goreecloud-glaze-ui" content="2.1.0"'),
        ('name="goreecloud-glaze-ui" content="2.0.0"', 'name="goreecloud-glaze-ui" content="2.1.0"'),
        ('href="glaze-ui-1.5.0.css" data-glaze-ui="1.5.0"', 'href="glaze-ui-2.1.0.css" data-glaze-ui="2.1.0"'),
        ('href="glaze-ui-2.0.0.css" data-glaze-ui="2.0.0"', 'href="glaze-ui-2.1.0.css" data-glaze-ui="2.1.0"'),
        ('class="site-header"', 'class="site-header glaze-material-soft"'),
        ('<nav aria-label="Primary navigation">', '<nav class="glaze-navigation-capsule" aria-label="Primary navigation">'),
        ('class="button primary"', 'class="button primary glaze-button"'),
        ('class="button" href="#capabilities"', 'class="button glaze-button" href="#capabilities"'),
        ('class="hero-panel"', 'class="hero-panel glaze-material"'),
        ('Stable 1.5.0 design, interaction, accessibility, motion, material, and form-factor contract', 'Stable 2.1.0 design, interaction, accessibility, motion, material, density, and form-factor contract'),
        ('Stable 2.0.0 design, interaction, accessibility, motion, material, and form-factor contract', 'Stable 2.1.0 design, interaction, accessibility, motion, material, density, and form-factor contract'),
        ('Glaze UI 1.5.0', 'Glaze UI 2.1.0'),
        ('Glaze UI 2.0.0', 'Glaze UI 2.1.0'),
        ('Glaze UI 1.5', 'Glaze UI 2.1'),
        ('Glaze UI 2.0', 'Glaze UI 2.1'),
        ('the five substantive platform systems', 'the six substantive platform systems'),
        ('<div><strong>34</strong><span>current applications & services</span></div>', '<div><strong>38</strong><span>current applications & services</span></div>'),
        ('<div><strong>37</strong><span>current applications & services</span></div>', '<div><strong>38</strong><span>current applications & services</span></div>'),
        (
            'The Suite website uses the reviewed canonical application identity for each product.',
            'The Suite website uses the reviewed canonical application identity when one is approved.',
        ),
        (OLD_FILE_MANAGER_CARD, FILE_MANAGER_CARD),
        (OLD_MAPS_CARD, MAPS_CARD),
        (OLD_APP_STORE_CARD, APP_STORE_CARD),
        (
            'Newer products without approved artwork use neutral text marks until the branding authority publishes a canonical asset.',
            'If a future product has no approved artwork, it must use a neutral treatment until the branding authority publishes a canonical asset.',
        ),
    )
    for old, new in replacements:
        html = html.replace(old, new)

    html = _insert_after(
        html,
        '<div><strong>GoreeCloud Mesh · Mesh Center</strong><span>coordination and governance plane for explicit service relationships, dependencies, and evidence exchange</span></div>',
        IDENTITY_SYSTEM,
    )
    return html
