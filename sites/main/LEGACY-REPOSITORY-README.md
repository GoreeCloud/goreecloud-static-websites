# GoreeCloud Website

> **Repository migration notice:** `GoreeCloud/goreecloud-website` is a transitional legacy source. The canonical repository for all GoreeCloud static websites is `GoreeCloud/goreecloud-static-websites`.

The main GoreeCloud public website and the Projects, Roadmap, Blog, and Archive destinations currently remain here only while their source, build/deployment configuration, documentation, automation, and references are migrated and validated in `goreecloud-static-websites`.

All GoreeCloud static websites — including the main website, Wardveil Security website, Identity website, Privacy website, Roadmap website, Archive website, and static websites embedded in other GoreeCloud applications or services — MUST ultimately be stored, maintained, and referenced from `GoreeCloud/goreecloud-static-websites`.

This repository MUST be deleted after every GoreeCloud static website has completed migration to the centralized repository, all required deployment and repository references have been cut over, production has been verified where applicable, legacy website copies have been retired, and no required dependency remains on `goreecloud-website`. It must not be deleted before those gates are complete, and it must not remain as a competing website authority afterward.

## Current baseline

- Current accepted website package: **v5.24.0**
- Current accepted Website design-system implementation: **Glaze UI 2.1.0**
- Current GoreeCloud platform design-system target: **Glaze UI 2.2.0 Stable**
- Glaze UI 2.1 Stable promotion reference for the accepted Website implementation: `c49113eb8b93c267613fdf1bbca1f814495acad7`
- Glaze UI authority: `GoreeCloud/goreecloud-glaze-ui`
- Branding and approved visual-asset authority: `GoreeCloud/goreecloud-branding-assets`
- Repository inventory reviewed on **2026-08-31**: **57 repositories — 40 public, 17 private**
- Production-accepted public website portfolio recorded by the GoreeCloud Public Websites project: **10 destinations on Glaze UI 2.1.0 Stable**
- Additional official first-party surface: **Identity Center**, with Glaze UI 2.1 source merged while public-domain publication and exact production acceptance remain separately gated

`VERSION` is the canonical machine-readable version source for the last accepted website package. Version metadata is repository-only release metadata and does not establish deployment or production acceptance by itself.

Glaze UI 2.1.0 remains the accepted design-system implementation for the current Website package. The current GoreeCloud platform baseline is Glaze UI 2.2.0 Stable, so Website migration and repository-specific acceptance against 2.2 remain required. New source revisions do not inherit production acceptance from an earlier accepted deployment. Exact repository validation, rendered branch-preview review, authorized merge, and exact production deployment verification remain required.

## Official GoreeCloud website ecosystem

During migration, this repository still contains five production website destinations:

| Destination | Domain | Current legacy source |
| --- | --- | --- |
| GoreeCloud | `www.goreecloud.com` | repository root |
| Projects | `projects.goreecloud.com` | `sites/projects/` |
| Roadmap | `roadmap.goreecloud.com` | `sites/roadmap/` |
| Blog | `blog.goreecloud.com` | `sites/blog/` |
| Archive | `archive.goreecloud.com` | `sites/archive/` |

Their canonical target paths are maintained by `GoreeCloud/goreecloud-static-websites`. These entries describe the current migration source only and do not establish this repository as the long-term authority.

The wider production ecosystem also includes GoreeCloud Suite, Design Center, Privacy Center, Security Center, and Continuity Center in their current legacy repositories. Identity Center is an official first-party website surface whose current source exists in `GoreeCloud/goreecloud-identity`; publication and production acceptance remain pending until their separate gates are satisfied. Every static website source package in those repositories is also in scope for consolidation into `goreecloud-static-websites`.

## Public-web principles

The browser surface is intentionally static, privacy-preserving, evidence-scoped, and visually consistent:

- static HTML with locally hosted CSS, JavaScript, and approved visual assets;
- no advertising, behavioral analytics, tracking, fingerprinting, or third-party browser-loaded fonts;
- no unsupported production, privacy, security, continuity, or identity claims;
- public/private GitHub repository boundaries are preserved;
- application and platform-system claims are tied to current source, project specifications, and accepted evidence;
- the accepted Website package currently implements Glaze UI 2.1.0; current platform conformance requires migration and acceptance against Glaze UI 2.2.0 Stable;
- durable content surfaces remain solid while interaction uses controlled Glaze material;
- phone, tablet, and desktop behavior are deliberate layouts rather than scaled copies of one another;
- keyboard, pointer, touch, reduced-motion, reduced-transparency, contrast, forced-colors, zoom, and large-text states are part of release validation.

The seven substantive GoreeCloud Integral Platform Systems are GoreeCloud Manager, Privacy Shield, Wardveil Security, Everkeep, Glaze UI, GoreeCloud Mesh, and GoreeCloud Identity. Their names represent actual management, privacy, security, continuity, interface, coordination, identity, authentication, and authorization responsibilities rather than decorative branding. Each system must be evaluated according to the current GoreeCloud platform contract; repository-local behavior must not be promoted into producer-system acceptance without supporting evidence.

## Design and accessibility

Glaze UI is treated as a design contract, not merely a stylesheet or theme. The accepted Website Glaze UI 2.1 web layer currently governs typography, spacing, materials, navigation, cards, buttons, forms, focus treatment, responsive behavior, density, minimum interaction targets, mobile safe areas, reduced motion, reduced transparency, increased contrast, forced colors, large text, deterministic reduced-material/performance fallbacks, and print resilience. Current interaction sizing preserves the **48px general interaction floor** and the **56px Touch Assistance floor** when Touch Assistance is active or required. Migration to the current Glaze UI 2.2.0 Stable platform baseline remains a separate required acceptance track.

The governing material rule is **Content is solid. Interaction is glazed.** Durable reading surfaces use Canvas or Surface material; navigation, transient controls, selected interactive emphasis, and deliberately live interaction surfaces may use the appropriate Glaze material level. Site-specific CSS may extend that layer while preserving Glaze UI hierarchy and accessibility contracts. Importing tokens alone is not considered conformance.

Automated checks are regression controls, not a claim of complete WCAG conformance. Release acceptance still requires appropriate human interaction review, representative viewport review, keyboard testing, and screen-reader testing where applicable.

## Content and repository authority

`docs/repository-portfolio.json` is the machine-readable authority for the reviewed GoreeCloud GitHub portfolio shown on the public site. The current authenticated inventory includes `goreecloud-index`, a private Development repository whose presence does not imply Stable or production acceptance.

`docs/public-runtime-status.json` records reviewed public maturity and migration claims. Repository visibility must never be treated as evidence of production acceptance.

Approved GoreeCloud logos, product icons, system marks, artwork, and derivatives come from `GoreeCloud/goreecloud-branding-assets`. New products without an approved canonical asset use a neutral presentation until an asset is approved; the website must not invent an “official” mark.

`docs/public-asset-inventory.md` records reviewed publication and provenance facts for deployable creative assets. The inventory is not a license grant. Official artwork is required when it exists, and publication eligibility remains separate from mere repository presence.

## Source license and creative-rights boundary

The website source code, repository automation, validation scripts, and technical repository documentation are licensed under the **Apache License 2.0**. The authoritative source-license identifier is **Apache-2.0**, and the top-level `LICENSE` contains the reviewed license text.

`NOTICE` records the separate creative-rights boundary. The source license does not grant unrestricted reuse of GoreeCloud trade names, logos, branding, editorial identity, or third-party marks. `docs/public-asset-inventory.md` is not a license grant.

Issue #5 remains open as the separate human-controlled reachable-history, contextual-disclosure, creative-rights, and repository-publication decision. The final human reachable-history/contextual-disclosure review is required where that gate applies. Passing CI does not itself authorize a repository visibility change, publication decision, trademark use, or release.

## Build and publication allowlist

The current legacy main public site is built as an explicit allowlisted artifact:

```bash
python scripts/build_public_site.py
```

Build output directory: `dist`.

The publication boundary is exact, per-file allowlisted. Adding a file to `assets/`, `css/`, `js/`, the repository root, or another source directory does not automatically add it to the deployable artifact. The build renders repository facts, normalizes the homepage, applies the accepted Glaze UI 2.1 implementation, and writes only approved paths to `dist/`.

Issue #6 is closed: the isolated `dist/` Cloudflare Pages cutover is complete. This records the deployment architecture only; it does not eliminate exact candidate and post-merge deployment verification.

## Validation

Before a revision is accepted, run the repository validators and tests used by CI. Canonical local commands include:

```bash
python scripts/validate_repository_hygiene.py
python scripts/validate_repository_history.py
python scripts/validate_license.py
python scripts/validate_public_assets.py
python scripts/validate_accessibility.py
python scripts/validate_glaze_ui.py
python scripts/validate_repository_portfolio.py
python -m unittest discover -s tests -p "test_*.py"
```

Repository-history preflight must use a non-shallow checkout so reachable history is actually examined. The history validator reports whether a sensitive pattern was found without exposing the matched value. A green repository-history preflight does not replace the final human reachable-history/contextual-disclosure review or the explicit publication decision.

The broader CI contract also validates Suite/capability manifests, governance readiness, public runtime status, security reporting, Wardveil/observability boundaries, privacy statements, browser-origin integrity, application identity, public semantics, the full public surface, Cloudflare deployment contracts, performance budgets, isolated artifacts, remote-verifier configuration, repository guidance, release-evidence records, JavaScript syntax, branch preview, and post-merge production deployment.

Key validators and sources include:

- `scripts/validate_repository_portfolio.py`
- `scripts/validate_public_assets.py`
- `scripts/validate_public_runtime_status.py`
- `scripts/validate_public_semantics.py`
- `scripts/validate_public_surface.py`
- `scripts/validate_accessibility.py`
- `scripts/validate_glaze_ui.py`
- `scripts/validate_browser_origin_integrity.py`
- `scripts/validate_deployment_contract.py`
- `scripts/validate_performance_budget.py`
- `scripts/validate_build_artifact.py`
- `docs/glaze-ui-conformance.md`
- `docs/glaze-ui-2.1-public-sites.md`
- `docs/glaze-ui-2.0-public-sites.md` (historical adoption record)
- `docs/stability-baseline.md`
- `docs/release-readiness-checklist.md`
- `docs/release-evidence-template.md`

## Runtime-status boundary

The website must not turn development intent into a production claim. GoreeCloud Monitor remains a separately accepted replacement path: Uptime Kuma remains the current production availability monitor until a controlled GoreeCloud Monitor cutover is accepted and documented by its authoritative project evidence.

The same principle applies to every application and platform system. Source availability, a successful build, green CI, a release-candidate label, branding, or a public website card cannot manufacture production, privacy, security, continuity, identity, or conformance state.

## Deployment and release acceptance

Cloudflare Pages currently deploys reviewed static artifacts from this legacy repository until each site is cut over to `GoreeCloud/goreecloud-static-websites`. Exact accepted production revisions are recorded in the GoreeCloud Public Websites and Cloudflare Pages project specification in Google Drive.

A branch preview is evidence, not a release. Passing CI does not itself authorize merge, production deployment, a public claim upgrade, or broader product acceptance. The exact pull-request candidate must pass branch-preview verification; after merge, the exact resulting `main` revision must pass production verification. Source, isolated artifact, and deployed bytes must agree.

An earlier Glaze UI 2.1 production acceptance does not automatically transfer to a newer source revision. Each website revision must earn repository-local acceptance for the exact deployed commit. Platform Contract adoption also does not convert that prior 2.1 acceptance into current Glaze UI 2.2 conformance.

Deployment success does not by itself authorize broader product, privacy, security, continuity, identity, or production-readiness claims.

## Maintenance rules

When public behavior, architecture, project state, design-system conformance, branding authority, repository inventory, deployment scope, or static-site migration state changes:

1. update the canonical static website source and migration records in `GoreeCloud/goreecloud-static-websites` rather than adding a competing source of truth;
2. keep public claims evidence-scoped;
3. update the GoreeCloud project specification in `GoreeCloud/Projects` after the applicable source/release/deployment state changes;
4. append the canonical website changelog in `GoreeCloud/Changelogs` for substantive completed changes;
5. verify Cloudflare Pages and GitHub status before treating the revision as accepted;
6. remove obsolete static source and references from this repository only after the corresponding centralized site has passed its required cutover and verification gates.

Do not restore references to the retired `goreecloud-logo` repository. The unified authority is `GoreeCloud/goreecloud-branding-assets`.
