# GoreeCloud Privacy Shield Static Website

Canonical source repository: `GoreeCloud/goreecloud-static-websites`

- Site root: `sites/privacy`
- Canonical domain: `privacy.goreecloud.com`
- Legacy source repository: `GoreeCloud/goreecloud-privacy-shield`
- Reviewed legacy source commit: `345b4bd42aaed09afb0e2384c421aab8661f1d5c`
- Exact legacy website tree: `467d95f979a18e13b83ffa7dde6a68165720ebad`
- Current Glaze UI source target: `1.3.0` Stable
- Pinned Glaze UI revision: `8354308445da9ac35ced2b37a7f503a08a0aaf72`
- Pinned Glaze UI entrypoint: `css/glaze-v1.3.0.css`
- Consumer state: `source-migrated-rendered-acceptance-pending`

This package contains only the Privacy Center public static source, deterministic build contract, approved public Privacy Shield icon, and the fail-closed Glaze UI consumer lock used to reproduce the current source artifact. Generated `website/dist`, Privacy Shield runtime code, adapters, internal contracts, private configuration, and service implementation remain outside static-site authority.

The original centralized source transfer preserved the then-active Glaze UI 2.1.0 website baseline. The canonical central source was subsequently migrated to Glaze UI V1.3 / `1.3.0` on September 10, 2026. The source lock was introduced by commit `df503451fcb508a84c35c0d7e95dc726372af749`, and the Privacy Center source was refreshed for the V1.3/current authorization model by commit `5f63af9fe0438858cb6e3f8f5f9debd53282e403`.

The V1.3 source migration is not rendered acceptance. The upstream Glaze lifecycle state does not automatically confer Privacy Center consumer conformance, production eligibility, Privacy Shield runtime acceptance, or deployment approval. Rendered visual review, accessibility and browser/device verification, performance qualification, rollback verification, Cloudflare Pages source cutover, deployed-byte verification, DNS/HTTPS verification, and production approval remain independent gates.

Historical Glaze adoption records and the superseded 2.1.0 source baseline remain available through Git history; superseded runtime assets must not be reintroduced into the active Privacy Center package.
