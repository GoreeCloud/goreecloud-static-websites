# GoreeCloud Suite Production Verification — 2026-09-10

## Current production-verification decision

**Production verification is accepted for the corrected public GoreeCloud Suite website at exact central repository revision `807adc08c955e37711ec6ba2c64a656d3bff0bfb`.**

This acceptance covers the reconciled **45-product / 9-group** Suite publication at `https://suite.goreecloud.com/`. It supersedes the temporary `deployment-cutover-pending` disposition that followed discovery of the incomplete 27-product directory.

The Cloudflare GitHub App recorded a successful `Cloudflare Pages: goreecloud-suite` deployment for exact revision `807adc08c955e37711ec6ba2c64a656d3bff0bfb`, reporting `Deployed successfully` for commit prefix `807adc0`.

The repository's read-only production verification workflow then independently waited for the canonical domain to converge to the exact reviewed build. The first six attempts correctly failed closed because the live `glaze-v1.3-consumer.css` still contained the older 1839-byte publication while the merged revision expected 1928 bytes. The seventh attempt observed exact byte convergence and passed the full HTTP publication contract. This establishes that the production result was not inferred merely from provider-side deployment success.

## Corrected live-production evidence

The exact merged Suite build produced 94 files and 423847 bytes before publication verification.

The production HTTP verifier passed against `https://suite.goreecloud.com/` and established:

- canonical HTTPS delivery through Cloudflare;
- HTTP 200 for the root publication;
- exact byte equality between the live root and the reviewed built `index.html`;
- exact byte equality for the reviewed `404.html`, `sitemap.xml`, `robots.txt`, `styles.css`, `glaze-v1.3-consumer.css`, and canonical Glaze V1.3 entrypoint;
- a true HTTP 404 with `Cache-Control: no-store` for the deliberately missing deployment-smoke path;
- committed Content-Security-Policy, Referrer-Policy, X-Content-Type-Options, X-Frame-Options, Permissions-Policy, Cross-Origin-Opener-Policy, and Cross-Origin-Resource-Policy behavior;
- root cache behavior requiring revalidation;
- the canonical `https://suite.goreecloud.com/` sitemap and robots publication;
- exactly **45 product cards** and **9 functional product groups**;
- representative reconciled products including GoreeCloud Documents, Drive, File Manager, Mail, Messenger, Maps, Terminal, App Store, Gateway, AI, Index, Code, Health, Reader, Router OS, Social, Home, and Home Security;
- GLAZE UI `1.3.0` with exact source revision `8354308445da9ac35ced2b37a7f503a08a0aaf72`;
- exact canonical Glaze V1.3 Git blob SHA `4c3ad293ba9196e2e5a32700b530ec67fd01cef6`.

The production Chrome smoke then passed at **1180×900, 768×900, 390×844, and 320×844**. The live canonical page rendered all 45 products in 9 groups, retained the approved Glaze V1.3 identity, loaded all document images successfully, preserved the canonical URL, maintained the expected responsive grid behavior and navigation target floors, and no longer exhibited the 320-pixel horizontal overflow previously discovered during live-browser validation.

The successful production workflow run was `34559034711`, job `103137750792`, using `contents: read` permissions only. It did not mutate Cloudflare, DNS, deployment state, or product lifecycle state.

## 320-pixel overflow correction

The live browser verifier initially exposed a real production defect at a 320-pixel viewport: the document width was 330 pixels, producing 10 pixels of horizontal overflow.

The defect was traced to intrinsic CSS grid sizing caused by the long exact Glaze revision token in the hero truth note. PR #42 corrected the consumer layout by allowing hero-grid children to shrink with `min-width: 0` and allowing the revision token to wrap safely at narrow widths. The exact PR candidate passed local Chrome validation at 1180, 768, 390, and 320 pixels before merge.

After PR #42 merged as exact central revision `807adc08c955e37711ec6ba2c64a656d3bff0bfb`, the production workflow waited until the merged consumer CSS was actually present on the canonical domain and then passed the same live Chrome checks. The production acceptance therefore includes evidence that the previously observed 320-pixel overflow is corrected in the live publication.

## Central repository and Cloudflare deployment contract

The verified public Suite website uses:

- Git repository: `GoreeCloud/goreecloud-static-websites`
- Production branch: `main`
- Root directory: `sites/suite`
- Build command: `python3 scripts/build_public_site.py`
- Build output directory: `dist`
- Pages project: `goreecloud-suite`
- Canonical custom domain: `suite.goreecloud.com`

The successful Cloudflare deployment is tied to exact central revision `807adc08c955e37711ec6ba2c64a656d3bff0bfb`.

## GLAZE UI V1.3 evidence

The accepted production HTML reports `data-glaze-version="1.3.0"`, `<meta name="goreecloud-glaze-ui" content="1.3.0">`, and `<meta name="goreecloud-glaze-source-revision" content="8354308445da9ac35ced2b37a7f503a08a0aaf72">`.

The deployed canonical Glaze entrypoint `https://suite.goreecloud.com/assets/glaze-v1.3.0.css` matches reviewed Git blob SHA `4c3ad293ba9196e2e5a32700b530ec67fd01cef6`.

## Authority boundary

This record verifies the **public GoreeCloud Suite website deployment** only for the exact accepted revision stated above. It does not by itself prove or authorize production readiness of any listed Suite product; correctness of a product runtime, backend, security, privacy, continuity, identity, networking, or recovery behavior; lifecycle or release promotion; global GLAZE UI acceptance outside this reviewed website deployment; or retirement/deletion of `GoreeCloud/goreecloud-suite`.

Application and service implementation/runtime authority remains with the applicable producer repository, specification, release process, and independently verified evidence.

## Historical 27-product verification

The earlier production verification for exact central revision `f03b0c5d62f870a52fda286636771db2a34d3aaf` remains valid historical evidence for the publication that existed at that revision.

That older deployment used the same central repository, Suite package root, build command, output directory, Cloudflare Pages project, and canonical domain. It passed HTTP 200, explicit HTTP 404 with `no-store`, committed response headers, GLAZE UI V1.3 metadata, canonical sitemap, exact Glaze CSS integrity, and rendered review.

However, the older page contained only 27 products because a stale initial inventory had incorrectly been treated as complete during migration. That historical result must never be represented as acceptance of the corrected 45-product directory. The current accepted revision is `807adc08c955e37711ec6ba2c64a656d3bff0bfb`.

## Legacy-source retirement

`GoreeCloud/goreecloud-suite` remains a GoreeCloud project source and is not retired or deleted by this website production verification.

Before any former website source, deployment reference, automation, rollback material, or preserved publication artifact in that repository is removed, verify that no Cloudflare Pages configuration still depends on it, no rollback or automation path requires it, documentation and deployment references have been reconciled to the centralized package, and preservation requirements have been satisfied.

## Result

The corrected 45-product GoreeCloud Suite publication is **`production-verified`** at exact central revision `807adc08c955e37711ec6ba2c64a656d3bff0bfb`.

The previous `f03b0c5d62f870a52fda286636771db2a34d3aaf` verification remains historical exact-revision evidence only.

`legacy-source-retired` remains a later, separately verified state.
