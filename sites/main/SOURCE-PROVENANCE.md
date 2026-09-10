# Source Provenance

## Centralization lineage

- Legacy repository: `GoreeCloud/goreecloud-website`
- Immutable imported source revision: `18f5276d21b8eb3b55adc18e00e88aa11b6edfd8`
- Legacy root tree: `49e1723e4d28310f3e680c8c80249cb0f1a0d76f`
- Initial migration method: exact Git checkout followed by bounded transfer into `sites/main`.
- Excluded from central Main authority: legacy `.github/`, legacy satellite `sites/` copies, generated `dist/`, and the legacy repository Platform Contract.
- Projects, Roadmap, Blog, and Archive remain independent canonical packages under the central repository's `sites/` hierarchy rather than duplicated beneath Main.
- `LEGACY-REPOSITORY-README.md` preserves historical source-repository context; `README.md` identifies the active canonical source boundary.

## September 10, 2026 — GLAZE UI V1.3 migration lineage

The Main package was reconciled from the imported Glaze UI 2.1 transformation model to source-native **GLAZE UI V1.3 / 1.3.0 Stable**.

Canonical Glaze source:

- Repository: `GoreeCloud/goreecloud-glaze-ui`
- Revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Entrypoint: `css/glaze-v1.3.0.css`
- Entrypoint Git blob: `4c3ad293ba9196e2e5a32700b530ec67fd01cef6`

The migration intentionally removes the old committed `css/glaze-ui-2.1.0.css`, the `scripts/glaze_ui_2.py` post-render transformation helper, and its render monkey patch. Public HTML now carries the V1.3 source contract directly. The isolated build resolves and vendors the exact same-origin recursive CSS dependency closure from the pinned canonical revision.

The public roadmap also stops publishing Home Assistant and Frigate as GoreeCloud product identities. Their old roadmap artwork is removed from the public source package; current product-level direction uses GoreeCloud Home and GoreeCloud Home Security. No replacement official artwork is invented where canonical product artwork is unavailable.

The old `docs/repository-portfolio.json` remains a dated review snapshot from its recorded `as_of` date. It is retained only for provenance/audit context and is not live inventory authority. Current repository inventory and counts come from the connected GoreeCloud GitHub organization; the public `repositories.html` is a reviewed source-role guide and intentionally omits a numeric live-total claim.

## Acceptance boundary

This provenance record documents source lineage and the V1.3 candidate transformation. It does not establish Cloudflare source cutover, rendered visual acceptance, accessibility acceptance, exact deployed-revision equivalence, or a new production acceptance record.
