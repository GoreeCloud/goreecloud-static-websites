# Public system-site migration provenance

This record defines the bounded source packages imported into `GoreeCloud/goreecloud-static-websites` for the public system-site migration tranche. Generated deployment artifacts and product/runtime code are excluded from canonical static-site authority.

## Design Center

- Legacy repository: `GoreeCloud/goreecloud-glaze-ui`
- Reviewed source commit: `6b17bec103e8a0dbdf0f16c625fbc2f1ad359e80`
- Website tree: `f8ef25c1e0e9f5566e18d0bfdc67080844e8a319`
- Central package: `sites/design`
- Included: `website/` source excluding generated `website/dist`, the exact CSS inputs consumed by `website/build.py`, canonical Facet mark, and `reference/v1-system-shell.html`.
- Excluded: unrelated Glaze UI repository source, historical candidates, tests, release/governance material not required to reproduce the public site.

## Identity Center

- Legacy repository: `GoreeCloud/goreecloud-identity`
- Reviewed source commit: `7b0b8f2a391b795f6ddfbfcce006a7e83a414d72`
- Exact Identity Center tree: `3dd3ca4b4641561c7e94c49336dcae316e8c6f7f`
- Central package: `sites/identity`
- Included: only `identity-center-site`.
- Explicitly excluded: `website/`, which is upstream authentik technical/integration/API documentation source rather than the GoreeCloud Identity Center; Identity backend/authenticated runtime source is also excluded.

## Mesh Center

- Legacy repository: `GoreeCloud/goreecloud-mesh`
- Reviewed source commit: `1002c74a2f014b04719b6809da22b0026546f8f0`
- Exact website tree: `8969145d7e8ea96eaf2900b4558e8532df19ea32`
- Central package: `sites/mesh`
- Included: `website/` plus only `scripts/build_public_site.py`, `scripts/validate_public_site.py`, and `scripts/verify_public_deployment.py`.
- Excluded: Go runtime, APIs, contracts, internal coordination code, and all other non-site source.

## GoreeCloud Suite

- Legacy repository: `GoreeCloud/goreecloud-suite`
- Reviewed source tree: `2cced628d07d2ec48bd838e665e29b9ecb0024a8`
- Central package: `sites/suite`
- Included: the explicit public allowlist consumed by `scripts/build_public_site.py`, approved local Suite identity assets, and website-specific build/validation/responsive tools.
- Excluded: unrelated repository governance, project-management, and non-public source.

This source migration does not itself establish Cloudflare Pages cutover, DNS/HTTPS acceptance, production verification, or legacy-source retirement. Those remain separate evidence gates.
