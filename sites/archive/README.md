# GoreeCloud Archive

Canonical static website source for `archive.goreecloud.com`.

The Archive is a curated public historical record of major GoreeCloud milestones, architectural eras, product transitions, superseded decisions, and platform evolution. It is not an automatic mirror of internal change logs or operational records.

## Current design target

- GLAZE UI: **V1.3 / 1.3.0 Stable**
- Exact Stable source revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Consumer state: `source-migrated-rendered-acceptance-pending`

Historical Glaze UI 1.x and 2.x milestones may remain in Archive content when clearly described as historical. They do not override the current V1.3 lifecycle authority and must never be activated as current stylesheet dependencies.

## Current website-authority boundary

The canonical static-site repository currently contains **14 authoritative website packages**. Historical Archive entries may preserve earlier package counts when they are clearly tied to their original period. The current-boundary section must use the present 14-package authority: Labs is integrated as the fourteenth authoritative-main package, while its Cloudflare source cutover, exact deployed-revision verification, canonical-domain browser acceptance, production acceptance, and indexing release remain separate gates.

## Curation boundary

Public history may preserve approved context, including superseded technical or product direction. It must not publish credentials, private topology, administrative interfaces, sensitive operational details, personal information that was not deliberately approved for release, or internal records simply because they exist.

## Acceptance boundary

The exact-source V1.3 build and validation establish static source/build state only. Rendered/accessibility acceptance, Cloudflare source cutover, custom-domain verification, and exact production acceptance remain independent. Current project records govern current engineering state when they differ from historical Archive entries.
