# GoreeCloud Website Governance Readiness

## Purpose

This document maps the GoreeCloud public website to the mandatory GoreeCloud software and service production-readiness baseline. It records which platform-wide gates apply to the website's current architecture and prevents a scope exception from being mistaken for a permanent waiver.

The governing baseline requires multi-user readiness where non-administrative user accounts are part of a product, security and safe operation for every software/service surface, and Glaze UI for every GoreeCloud-controlled user-facing interface.

## Current application role

The GoreeCloud website is a public, anonymous, static informational website. Its current production contract contains no authentication system, account registration, user profiles, private workspace, application database, form-processing backend, Cloudflare Pages Function, Worker runtime, service worker, or user-owned application data store.

The website publishes public information about GoreeCloud. It is not the access-control layer for private GoreeCloud services and must not become a shortcut around application authentication, NetBird access policy, or private-service publication controls.

## Mandatory baseline mapping

### Multi-user readiness: Not applicable to the current static public website

The multi-user gate is not applicable to the current website because visitors do not receive application identities, accounts, private records, or per-user workspaces. Anonymous public readership is not a single-user application design and does not create a shared-user identity.

This status is scope-specific, not a waiver. If the website adds authentication, account registration, profiles, saved private state, form-submitted private data, personalized workspaces, administrative access, or any other user identity/data boundary, this Not Applicable determination expires. Individual identities, authorization, private-data boundaries, account lifecycle controls, and the applicable GoreeCloud multi-user requirements must then be implemented and validated before that feature reaches production.

### Security readiness: Applicable

Security and safe operation apply fully to the public website. The current repository enforces a deliberately small static architecture with:

- an exact per-file public deployment allowlist and isolated `dist/` artifact;
- origin-local browser render resources;
- no analytics, advertising, behavioral tracking, third-party browser runtime, or networked public JavaScript;
- restrictive browser security and privacy headers;
- responsible security-reporting surfaces and `security.txt` freshness checks;
- repository current-tree hygiene and reachable-history publication preflight;
- immutable GitHub Actions dependencies, read-only workflow permissions, exact-revision checkout, and no CI secret consumption;
- privacy, public-surface, resilience, performance, and deployment-contract validation;
- candidate-bound remote deployment verification so the reviewed source can be compared with the deployed HTTP surface.

The source license and branding/mark boundary are separately validated. Repository publication and production deployment remain explicit actions rather than consequences of a green CI run.

### Glaze UI compliance: Applicable

Glaze UI applies fully to every human-facing website page. The shared contract includes System, Light, and Dark appearance modes; layered and selectively translucent surfaces; rounded geometry; restrained depth; purposeful gradients; responsive behavior; keyboard focus; no-JavaScript navigation fallback; reduced-motion and reduced-transparency handling; increased-contrast and forced-colors support; print readability; and shared GoreeCloud product identity.

Automated Glaze UI and structural-accessibility validators are regression gates. They do not replace manual browser, keyboard, zoom/reflow, touch, contrast, and assistive-technology acceptance for an exact release candidate.

## Architecture-change triggers

The governance classification must be reviewed before production whenever a change introduces any of the following:

- authentication, accounts, profiles, or user-owned/private data;
- form submission or a server-side request handler;
- a database, session store, API, Pages Function, Worker, or other dynamic runtime;
- browser network clients, third-party telemetry, analytics, advertising, or externally loaded render dependencies;
- a service worker, background synchronization, notifications, or offline application state;
- a new public hostname, routing model, or deployment provider;
- a new user-facing page or interaction pattern that is not covered by the shared Glaze UI contract;
- a material change to the repository publication, licensing, privacy, security, or creative-rights boundary.

A new capability is not production-ready merely because it works. Its new identity, privacy, security, Glaze UI, deployment, backup/recovery, and documentation requirements must be evaluated before release.

## Release evidence

Repository-level production evidence requires, at minimum:

1. exact-head GitHub Actions success;
2. `python scripts/validate_governance_readiness.py` success;
3. source-license, security, privacy, accessibility, Glaze UI, public-surface, performance, repository-hygiene/history, artifact, and resilience gates remaining green;
4. manual Glaze UI/accessibility acceptance on the exact candidate;
5. issue #6 completion before claiming Cloudflare is enforcing the isolated `dist/` deployment boundary;
6. issue #5 completion before any repository-publication or visibility action that depends on the final human history/contextual disclosure review and publication decision;
7. explicit merge and production authorization.

## Final boundary

The current public website satisfies the GoreeCloud multi-user baseline through a documented Not Applicable determination for its anonymous static architecture, not through an exception to user isolation. Security readiness and Glaze UI compliance remain mandatory and fully applicable.

If the website's role changes, this document and its validator must change with it. Production readiness is evaluated against the architecture that actually exists, not the architecture the website used to have.
