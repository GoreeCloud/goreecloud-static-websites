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
| PW-002 | Complete the provider-side Labs deployment cutover from the accepted central source and exact production acceptance. | High | Source accepted / deployment cutover pending |
| PW-003 | Complete the Manager public informational website deployment cutover while preserving the separate `manager.goreecloud.com` authenticated application boundary. | High | Source accepted / deployment cutover pending |
| PW-004 | Require reviewed source/build, rendered-accessibility, deployment, and exact deployed-revision evidence before recording new production acceptance. | High | Ongoing release gate |
| PW-005 | Migrate public informational/static websites to `https://www.goreecloud.com/<website-slug>`, including `/glaze-ui`, `/wardveil`, `/suite`, `/labs`, and `/identity`; reserve `https://<application>.goreecloud.com/` for the actual web application. Preserve required compatibility and require per-site production verification before acceptance. | High | Planned / migration required |

## Current evidence baseline

Authoritative `main` currently registers fourteen centralized static website packages. The live Glaze UI lifecycle registry identifies 1.4.1 as the current Official Stable and consumer-eligible release. Existing website hostnames remain the current deployment locations until each URL migration is separately implemented and verified; this roadmap does not represent the future `www.goreecloud.com/<website-slug>` paths as already live.

## Maintenance and synchronization

This roadmap and the corresponding Drive `FEATURE-ROADMAP.docx` must remain materially synchronized with one another and with the authoritative project or service record. Update both copies whenever feature scope, priority, dependency, implementation status, cancellation, supersession, recommendation, or verification state materially changes.

No feature may be represented as complete or Stable solely because it appears in this roadmap. Completion and lifecycle claims require the applicable authoritative implementation, validation, review, release, and production evidence.

## Reconciliation rule

At each material feature change, reconcile this roadmap against the current authoritative project record, repository implementation state, applicable platform-system requirements, and GoreeCloud Tasks Management. Missing obligations, stale status, duplicated work, roadmap drift, or undocumented disposition changes are defects to correct.
