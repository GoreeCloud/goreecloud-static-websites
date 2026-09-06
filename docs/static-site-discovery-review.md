# Static Site Discovery Review

**Reviewed:** 2026-09-06  
**Canonical static-site authority:** `GoreeCloud/goreecloud-static-websites`  
**Accepted central revision before this review:** `4bfee305550e2e43991188816f4fc80c16ccfad5`

## Conclusion

The current thirteen-site manifest is complete for GoreeCloud-controlled standalone public static website authority at the time of this review.

Evidence consists of:

- an automated recursive-tree scan of **66 public, non-archived GoreeCloud repositories**, recorded in `docs/public-static-discovery.json` on the discovery evidence branch;
- manual review of every repository returned by that scan with static-site-like signatures;
- an authenticated inventory of repositories available to the GoreeCloud GitHub connection, including the private repositories; and
- direct inspection of ambiguous candidates whose file layout alone could be mistaken for a standalone public site.

The authenticated inventory showed three private GoreeCloud repositories relevant to this migration boundary: `goreecloud-privacy-shield`, `goreecloud-wardveil-security`, and `goreecloud-everkeep`. Their bounded public website packages are already represented by `sites/privacy`, `sites/security`, and `sites/everkeep` and are `validated-in-central-repo`.

No additional standalone GoreeCloud public static website package was identified beyond the thirteen entries in `sites/manifest.json`.

This conclusion is a point-in-time inventory result. A future repository or a future standalone public website package is automatically subject to the centralization rule and must be added to this repository unless an explicit governed architectural exception is approved.

## Classification rule

A matching `index.html`, `404.html`, `_headers`, `CNAME`, `site.webmanifest`, or directory named `site`/`website` is not by itself evidence of a separate GoreeCloud static website.

Centralization scope includes a GoreeCloud-controlled public/static website package that is a distinct publication surface. It does not move application frontends, authenticated application UIs, browser-extension pages, internal service/debug pages, generated build output, validation fixtures, design/reference demos, portability templates, OpenAPI pages, or inherited upstream documentation merely because those files can render in a browser.

## Reviewed public-repository candidates

| Repository | Discovery signal | Classification | Result |
| --- | --- | --- | --- |
| `goreecloud-backup` | `app/public`, `internal/server`, Hugo-like `site/`, `CNAME` | Upstream Kopia application/internal UI and upstream documentation. `site/content/CNAME` is `kopia.io`. | Excluded from GoreeCloud standalone-site authority. |
| `goreecloud-bookmark-browser-extension` | root `index.html` | Browser-extension UI. | Excluded. |
| `goreecloud-bookmarks` | web `site.webmanifest` | Application web frontend. | Excluded. |
| `goreecloud-calendar` | `static/index.html` | Application static frontend. | Excluded. |
| `goreecloud-code` | `apps/web/index.html` | Application UI. | Excluded. |
| `goreecloud-contacts` | `frontend/index.html` | Application UI. | Excluded. |
| `goreecloud-dns` | two client trees and `openapi/index.html` | Product/service client UI plus API documentation. | Excluded. |
| `goreecloud-drive` | `web/index.html` | Application UI. | Excluded. |
| `goreecloud-glaze-ui` | `reference/index.html`, `website/` | `website/` is Design Center and is already centralized as `sites/design`; `reference/` is design-system reference material. | Covered / reference excluded. |
| `goreecloud-identity` | `identity-center-site`, theme demo, Docusaurus `website/` | Identity Center is already `sites/identity`; theme demo is a demo; `website/` is inherited authentik documentation rather than the GoreeCloud public Identity Center. | Covered / upstream and demo excluded. |
| `goreecloud-location` | `apps/web/index.html` | Application UI. | Excluded. |
| `goreecloud-mail` | `web/index.html` | Application UI shared with product clients. | Excluded. |
| `goreecloud-manager` | `website/` | Public Manager informational site. | Already centralized as `sites/manager`. |
| `goreecloud-memos` | multiple frontend `index.html` files and generated `dist` | Application frontend plus generated artifact. | Excluded. |
| `goreecloud-mesh` | `website/` | Public Mesh Center. | Already centralized as `sites/mesh`. |
| `goreecloud-monitor` | monitoring `site.webmanifest` | Application monitoring UI asset. | Excluded. |
| `goreecloud-music` | `web/index.html` | Application UI. | Excluded. |
| `goreecloud-network` | client UI, debug template, proxy web source and `dist` | Application/service UI, internal debug page, and generated artifact. | Excluded. |
| `goreecloud-notify` | `frontend/index.html` | Application UI. | Excluded. |
| `goreecloud-photos` | docs `CNAME` | Inherited Immich documentation tree; repository README and documentation links identify the upstream Immich documentation/product boundary. The discovered CNAME file is empty. | Excluded. |
| `goreecloud-rss` | root `index.html` | GoreeCloud Feed application web client shared with Linux/Android targets; not a separate static informational website. | Excluded. |
| `goreecloud-search` | native web UI and upstream template pages | Application/internal web UI and inherited search templates. | Excluded. |
| `goreecloud-static-websites` | `sites/` | Canonical repository itself. | In scope by definition; manifest governs sites. |
| `goreecloud-suite` | root static publication package | Public Suite website. | Already centralized as `sites/suite`. |
| `goreecloud-tasks` | `templates/portability/index.html` | Portability/export template, not a public website. | Excluded. |
| `goreecloud-vault-server` | web client and browser validation fixture | Application UI plus test/validation surface. | Excluded. |
| `goreecloud-website` | root and `sites/*` | Transitional source for Main, Projects, Roadmap, Blog, and Archive. | All five are already centralized and validated. |

## Private repository review

The authenticated GitHub installation inventory identified the private repositories `goreecloud-privacy-shield`, `goreecloud-wardveil-security`, and `goreecloud-everkeep`. Their public website packages have been migrated without moving private runtime or service authority:

- Privacy Shield → `sites/privacy`
- Wardveil Security → `sites/security`
- Everkeep → `sites/everkeep`

All three passed exact-candidate validation and post-merge validation on the accepted central repository revision.

## Inventory gate status

**Repository discovery gate: satisfied for the current repository inventory.**

The thirteen current standalone static website packages are all represented in `sites/manifest.json` and all are `validated-in-central-repo`.

This does **not** satisfy the deployment or retirement gates. Every current manifest entry still has `deployment_state: legacy-source` until its Cloudflare Pages source/root and related deployment references are cut over to the central repository and the exact resulting production revision is verified. Legacy source must remain available until those checks pass.

`GoreeCloud/goreecloud-website` therefore remains protected from deletion. It may be deleted only after every required Cloudflare cutover, exact production verification, downstream-reference cleanup, legacy-source retirement, dependency check, and applicable preservation gate has passed.
