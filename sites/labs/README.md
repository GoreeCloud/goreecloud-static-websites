# GoreeCloud Labs six-product public center

Canonical static-site source for the combined public website covering **GoreeCloud Home Security**, **GoreeCloud Home**, **GoreeCloud AI**, **GoreeCloud Containers**, **GoreeCloud Code**, and **GoreeCloud Boot**.

`labs.goreecloud.com` is a technical website namespace, not a new GoreeCloud product or umbrella brand. The public page uses the GoreeCloud master brand and preserves the six canonical product names.

## Source authority

- Canonical static-site repository: `GoreeCloud/goreecloud-static-websites`
- Canonical package: `sites/labs`
- Transitional source: `GoreeCloud/goreecloud-website`, branch `agent/rebuild-public-site-v1-1`
- Migrated legacy Labs tree: `60cf6dbefa274a19bbb7bf3ae75638ac6d20e1c7`
- Source candidate carrying GoreeCloud Boot: `7d9b03c90d3ea2c74dacd2f03430a86dd93a3ba6`
- Deployment state: legacy source until the Labs Cloudflare Pages project is cut over and exact production verification succeeds

## Cloudflare Pages contract

- Repository: `GoreeCloud/goreecloud-static-websites`
- Root directory: `/`
- Build command: `python sites/labs/build.py`
- Build output directory: `sites/labs/dist`
- Intended production branch: `main` after review, merge, and controlled cutover
- Custom domain: `labs.goreecloud.com`
- Current central migration state: **source copied; central validation and deployment cutover pending**

The site is static at browser runtime. It does not host GoreeCloud Home device control, Home Security camera processing, AI inference/runtime APIs, Containers workload execution, Code forge/provider operations, GoreeCloud Boot provisioning/boot runtime, or private GoreeCloud application services.

## Publication gates

Before the central package is treated as production authority:

1. Pass the central Labs source/build validation on the exact candidate revision.
2. Preserve the existing `noindex,nofollow` / `Disallow: /` boundary until the governed publication gate allows indexing.
3. Cut the Labs Cloudflare Pages source reference from the transitional repository to this canonical package.
4. Verify custom-domain DNS, HTTPS/TLS, headers, 404 behavior, responsive behavior, appearance controls, and representative-mobile interaction on the deployed central revision.
5. Verify the exact deployed artifact matches the accepted central revision.
6. Retire the legacy Labs source only after the cutover, rollback/dependency, and preservation gates pass.

## GLAZE UI

The Pages build fetches the exact GLAZE UI V1.1 / 1.1.0 web CSS from canonical commit `15cc76d2bcd4065552dc31c77145b63f34d9e7b2`, validates the expected import closure and Stable markers, and republishes the CSS same-origin inside the isolated artifact. Browsers do not fetch GLAZE UI from GitHub at runtime.
