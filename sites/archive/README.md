# GoreeCloud Archive

Canonical static website source for `archive.goreecloud.com`.

The Archive is a curated public historical record of major GoreeCloud milestones, architectural eras, product transitions, superseded decisions, and platform evolution. It is not an automatic mirror of internal change logs or operational records.

## Current design target

- GLAZE UI: **V1.3 / 1.3.0 Stable**
- Exact Stable source revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Consumer state: `source-migrated-rendered-acceptance-pending`

Historical Glaze UI 1.x and 2.x milestones may remain in Archive content when clearly described as historical. They do not override the current V1.3 lifecycle authority and must never be activated as current stylesheet dependencies.

## Curation boundary

Public history may preserve approved context, including superseded technical or product direction. It must not publish credentials, private topology, administrative interfaces, sensitive operational details, personal information that was not deliberately approved for release, or internal records simply because they exist.

## Governed Cloudflare Pages cutover contract

The approved centralized publication contract is:

- Cloudflare Pages project: `goreecloud-archive`
- Pages namespace: `goreecloud-archive.pages.dev`
- Repository: `GoreeCloud/goreecloud-static-websites`
- Production branch: `main`
- Root directory: repository root (leave the Cloudflare Root directory setting blank)
- Build command: `python3 scripts/build_simple_static_site.py sites/archive`
- Build output directory: `sites/archive/dist`
- Canonical custom domain: `archive.goreecloud.com`
- Legacy deployment/source repository: `GoreeCloud/goreecloud-website`

The Pages project identity and namespace are verified from legacy-repository Cloudflare deployment evidence. The root/build/output settings above match the centralized exact-build workflow and are the governed target for source reconnection; documenting them does not establish that Cloudflare has already been re-pointed to the central repository.

After an independently authorized source cutover, run the Archive workflow manually so the allowlisted production verifier can compare the canonical domain against the reviewed `dist/` artifact, required security headers, canonical-host and 404 behavior, and the live Chrome rendering contract. Provider deployment success by itself is not production acceptance.

## Acceptance boundary

The exact-source V1.3 build and validation establish static source/build state only. Rendered/accessibility acceptance, Cloudflare source cutover, custom-domain verification, and exact production acceptance remain independent. Current project records govern current engineering state when they differ from historical Archive entries.
