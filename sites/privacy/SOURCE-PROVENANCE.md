# Privacy Shield Static-Site Source Provenance

## Legacy transfer baseline

- Legacy repository: `GoreeCloud/goreecloud-privacy-shield`
- Legacy source commit: `345b4bd42aaed09afb0e2384c421aab8661f1d5c`
- Exact legacy `website/` tree: `467d95f979a18e13b83ffa7dde6a68165720ebad`
- Transferred authority: active public document source, security headers, product CSS, responsive polish, JavaScript, the then-active Glaze UI 2.1.0 web subset, deterministic build script, and approved Privacy Shield public icon.
- Explicitly excluded: generated `website/dist`, application/runtime code, adapters, private configuration, service contracts, internal tests, and unrelated repository governance.

## Canonical central migration

The centralized Privacy Center source no longer uses the transferred Glaze UI 2.1.0 runtime subset as its active design-system target.

On September 10, 2026:

- commit `df503451fcb508a84c35c0d7e95dc726372af749` introduced the fail-closed Glaze consumer lock targeting Stable Glaze UI `1.3.0` at revision `8354308445da9ac35ced2b37a7f503a08a0aaf72`;
- commit `5f63af9fe0438858cb6e3f8f5f9debd53282e403` refreshed the canonical Privacy Center source for the V1.3 target and current Privacy Shield authorization model.

The active consumer lock binds the V1.3 entrypoint `glaze-v1.3.0.css` to Git blob `4c3ad293ba9196e2e5a32700b530ec67fd01cef6` and deliberately records `source-migrated-rendered-acceptance-pending`.

The former 2.1.0 package remains historical provenance only. Reintroducing its runtime asset into the active canonical package is a regression and must fail repository validation.

## Acceptance boundary

Source migration does not establish rendered, accessibility, performance, rollback, deployment, Privacy Shield runtime, or production acceptance. Production source cutover, Cloudflare Pages configuration, deployed-byte verification, DNS/HTTPS verification, and legacy-source retirement remain separate gates.

Historical Glaze adoption records and the original transfer baseline remain preserved in Git history.
