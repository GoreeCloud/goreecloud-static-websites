# GoreeCloud Website Icon Identity Audit

Date: 2026-09-01

The GoreeCloud Suite homepage must display the reviewed canonical application artwork recorded in `docs/suite-portfolio.json`.

Each Suite entry records its authoritative GoreeCloud repository, source artwork path, reviewed source ref, website icon path, and expected Git blob identity. `scripts/validate_suite_portfolio.py` verifies that the website copy matches the reviewed canonical artwork before publication.

## September 1, 2026 synchronization checkpoint

The Suite publication set has been synchronized with the four product identities newly approved in `GoreeCloud/goreecloud-branding-assets`:

- GoreeCloud App Store — `products/app-store/app-icon.svg`, Git blob `05c66a2a4c8edcc194183bb8ffb10ca90d8eaeef`;
- GoreeCloud File Manager — `products/file-manager/app-icon.svg`, Git blob `c723a84eb2ecb29ef8a0cef845eb1d2cff714cd0`;
- GoreeCloud Maps — `products/maps/app-icon.svg`, Git blob `07b6e52e04c95e1ec9f703a9d323cf799481351c`;
- GoreeCloud Index — `products/index/app-icon.svg`, Git blob `797cfbd9ae490e37b5a90efe02905159158a8e88`.

Their website derivatives are byte-identical synchronized SVG copies under `assets/suite/` and are bound to immutable canonical branding revision `715a2d13e92474a96b107cc66b5f0c026d5911f4`. The Suite validator requires all four IDs explicitly in addition to the expected 38-entry portfolio count, so this accepted identity set cannot silently regress to the earlier 34-entry registry.

The canonical product identity is intended to remain the same across supported web/PWA, desktop/Linux, Android, future iOS, GoreeCloud Manager, repository, release, documentation, notification, installer, update, and recovery surfaces. Platform-specific masking, padding, raster sizes, formats, adaptive layers, monochrome variants, or other required derivatives may differ while preserving the same underlying product identity.

Third-party infrastructure and roadmap technologies are different: their cards use the official or otherwise authorized identity of the external product when that third party is being represented. Those assets are referential and are not GoreeCloud application identities.

A product may still be in development before every client package consumes every required derivative. Full visual production acceptance requires supported release targets to reference or reproducibly derive the approved canonical identity. This website synchronization establishes publication-source conformance only; it does not establish application runtime, deployment, release, production, or Stable acceptance.
