# GoreeCloud Public Websites — Feature Roadmap

**Status:** Active roadmap control  
**As of:** 2026-09-15  
**Authoritative project record:** Project Record — Public Websites  
**Canonical repository:** GoreeCloud/goreecloud-static-websites  
**Drive control:** `GoreeCloud/Feature Roadmap/GoreeCloud Public Websites/FEATURE-ROADMAP.docx`

## Purpose

This file is the repository-side feature roadmap control for GoreeCloud Public Websites. It records current planned and recommended feature work without replacing the authoritative project record, implementation evidence, release gates, or GoreeCloud Tasks Management.

## Roadmap

| ID | Feature / obligation | Priority | Current state |
| --- | --- | --- | --- |
| PW-001 | Reconcile all fourteen static website packages on authoritative `main` to the current GLAZE UI 1.4.1 Stable contract, with per-site evidence and acceptance. | High | In progress / evidence-gated |
| PW-002 | Complete the provider-side Labs deployment cutover from the accepted central source and exact production acceptance. | High | Unified `/labs/` path live; per-site exact production acceptance and legacy retirement pending |
| PW-003 | Complete the Manager public informational website deployment cutover while preserving the separate `manager.goreecloud.com` authenticated application boundary. | High | Unified `/manager/` path live; `manage.goreecloud.com` redirect verified and `manager.goreecloud.com` application boundary preserved; per-site exact production acceptance and legacy retirement pending |
| PW-004 | Require reviewed source/build, rendered-accessibility, deployment, and exact deployed-revision evidence before recording new production acceptance. | High | Ongoing release gate |
| PW-005 | Migrate public informational/static websites to `https://www.goreecloud.com/<website-slug>`, including `/glaze-ui`, `/wardveil`, `/suite`, `/labs`, and `/identity`; reserve `https://<application>.goreecloud.com/` for the actual web application. Preserve required compatibility and require per-site production verification before acceptance. | High | In progress / unified www production cutover and 13 legacy informational-host redirects verified; per-site metadata, GLAZE UI 1.4.1, rendered/accessibility, exact-revision acceptance, and legacy retirement pending |

## Current evidence baseline

Authoritative `main` registers fourteen centralized static website packages, and the Glaze UI lifecycle registry identifies 1.4.1 as current Official Stable. Source-side URL namespace preparation was implemented through PR #96 at merge revision `6a5c70292857ea3ccbc922585f7a905195cd92bb`. The existing `goreecloud-website` Cloudflare Pages project now builds the unified repository-root www namespace with `python3 scripts/build_www_namespace.py` and output directory `dist`, and public readback confirms all fourteen governed `www.goreecloud.com` path destinations are reachable.

The account-level Bulk Redirect Rule `goreecloud-website-url-migration` is enabled against `goreecloud_website_url_migration` with 13 permanent legacy informational-host redirects. The original 12 legacy hosts are verified, and `manage.goreecloud.com` now redirects to `https://www.goreecloud.com/manager/` with query strings preserved. PR #98 merged as main revision `6029da3313b570cc730ebf24c475eda905f5064e` to distinguish the legacy Manager informational hostname from `manager.goreecloud.com`, which remains reserved for the actual Manager application, and Cloudflare Pages successfully deployed that exact revision to `goreecloud-website`.

Final migration acceptance remains open because some mounted sites still expose stale canonical/design-system metadata, current GLAZE UI 1.4.1 per-site conformance is not yet established, and per-site rendered/accessibility/indexing/exact deployed-revision acceptance, old Pages-project/reference cleanup, nested legacy-path compatibility where applicable, and legacy-source retirement remain pending.

## Maintenance and synchronization

This roadmap and the corresponding Drive `FEATURE-ROADMAP.docx` must remain materially synchronized with one another and with the authoritative project or service record. Update both copies whenever feature scope, priority, dependency, implementation status, cancellation, supersession, recommendation, or verification state materially changes.

No feature may be represented as complete or Stable solely because it appears in this roadmap. Completion and lifecycle claims require the applicable authoritative implementation, validation, review, release, and production evidence.

## Reconciliation rule

At each material feature change, reconcile this roadmap against the current authoritative project record, repository implementation state, applicable platform-system requirements, and GoreeCloud Tasks Management. Missing obligations, stale status, duplicated work, roadmap drift, or undocumented disposition changes are defects to correct.
