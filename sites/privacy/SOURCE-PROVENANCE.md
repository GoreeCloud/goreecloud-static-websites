# Privacy Shield Static-Site Source Provenance

## Historical transfer provenance

- Legacy repository: `GoreeCloud/goreecloud-privacy-shield`
- Legacy source commit: `345b4bd42aaed09afb0e2384c421aab8661f1d5c`
- Exact legacy `website/` tree: `467d95f979a18e13b83ffa7dde6a68165720ebad`
- Originally transferred authority: public Privacy Center document source, security headers, product CSS, responsive polish, JavaScript, deterministic build script, and approved Privacy Shield public icon.
- Explicitly excluded from static-site authority: generated `website/dist`, Privacy Shield application/runtime code, adapters, private configuration, service contracts, internal runtime tests, and unrelated repository governance.

The initial central copy preserved the then-active legacy website material, including its historical Glaze UI 2.1.0 subset. That transfer record is historical provenance only; it is not the current runtime target.

## Current canonical source/build authority

The active public Privacy Center source is maintained in `GoreeCloud/goreecloud-static-websites` under `sites/privacy`.

The current website source targets **GLAZE UI V1.3 / 1.3.0 Stable** through `website/glaze.lock.json`:

- GLAZE UI repository: `GoreeCloud/goreecloud-glaze-ui`
- exact Stable source revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- entrypoint: `glaze-v1.3.0.css`
- exact entrypoint Git blob: `4c3ad293ba9196e2e5a32700b530ec67fd01cef6`
- accepted Privacy Center website tree: `fa0543fcd940b8ecfdac1782364d15ea6fa344d3`
- accepted complete `sites/privacy` tree before this governance-only documentation reconciliation: `50d11f2ba52f7009ee8d1b08973ad1f4d75eff2c`

`website/build.py` is the canonical deterministic build path. It verifies the lock, exact Stable GLAZE UI source revision, exact entrypoint blob, safe local CSS dependency traversal, and the expected static publication inputs before producing `website/dist`.

Historical Glaze 2.1.0 material remains valid as repository history/provenance but is not an active Privacy Center runtime dependency and must not be restored as one.

## Production verification

Cloudflare Pages source cutover and public production verification are complete for the accepted publication represented by website tree `fa0543fcd940b8ecfdac1782364d15ea6fa344d3`.

Production verification was accepted on September 10, 2026 at exact central repository revision:

`80379f6962a5ded6c01317542941a2c55aedd922`

The accepted record verifies the central repository/root/build/output contract, canonical HTTPS behavior, explicit 404 behavior, committed response headers, GLAZE UI V1.3 identity, exact Stable Glaze source revision, exact production entrypoint blob, and rendered review. See `docs/production-verification-privacy-2026-09-10.md`.

The same website tree remains present on current canonical `main`, so later repository-wide changes outside `sites/privacy/website` do not invalidate that accepted publication evidence. Any future material change to the website tree requires independent build and production re-verification before the changed publication can inherit `production-verified` status.

## Remaining boundaries

Production verification covers the public static website only. It does not transfer or prove Privacy Shield runtime authorization, application/adapter acceptance, consent or purpose authority, Wardveil protection, Identity authority, Mesh authority, or any other platform execution state.

Legacy website-source retirement also remains separate. The former website subtree or related references in the Privacy Shield repository may be retired only after rollback dependencies, automation/deployment references, documentation references, and preservation requirements are independently cleared and the resulting state is revalidated.
