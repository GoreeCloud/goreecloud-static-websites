# GoreeCloud Website Wardveil Security and Observability Contract

## Purpose

This record defines how the GoreeCloud public website applies **Wardveil Security by GoreeCloud** and production observability without weakening the website's privacy-first, static architecture.

Wardveil Security is the platform security and protection identity. It does not replace the technical authorities that establish the website's actual security state, including source review, GitHub Actions validation, Cloudflare Pages publication, browser security headers, the public security-reporting policy, or GoreeCloud governance records.

Glaze UI remains the website's design and interaction language. Wardveil-facing website surfaces must use the existing Glaze UI semantic system rather than introducing a separate visual system.

## Current Runtime Classification

The current public website is an anonymous static site. It has no application backend, user accounts, authentication, authorization, private workspace, application database, form-processing service, server-side session store, service worker, browser analytics, advertising technology, behavioral tracking, or browser telemetry exporter.

Because those capabilities do not exist in the current runtime, application authentication events, authorization decisions, database mutations, administrator actions, and server-side request-correlation events are **not applicable to the current website runtime**. This is a scoped architectural determination, not a permanent exemption.

If a future website revision adds authentication, authorization, forms, APIs, dynamic server execution, private user data, administrative actions, or another state-changing backend, that revision must add privacy-conscious structured logging and audit coverage for the new capability before it can be classified Stable.

## Current Production Evidence

The website uses source- and deployment-bound evidence instead of client telemetry:

- GitHub Actions validates the exact pull-request or push revision with read-only permissions and immutable action references.
- Repository hygiene and reachable-history checks detect unsafe source and publication material before release.
- The isolated `dist/` build proves which files are eligible for public publication.
- Branch-preview verification compares the reviewed candidate with the deployed Cloudflare Pages preview before merge.
- Production verification compares the resulting `main` revision with the live production deployment after merge.
- Scheduled and manually dispatchable remote deployment verification provides continuing availability and deployment-integrity evidence.
- The public security policy and `.well-known/security.txt` provide a dedicated vulnerability-reporting path through `security@goreecloud.com`.

A failed validation or remote verification is a release or operational failure. Unknown, skipped, unavailable, stale, or unverified required evidence does not count as passing.

## Privacy Boundary

The website must not add client-side logging, analytics, session replay, fingerprinting, advertising measurement, behavioral tracking, or a remote telemetry exporter merely to create observability data.

Browser-side GoreeCloud code must not intentionally transmit or persist operational records containing:

- page URLs or query strings;
- page content, DOM content, form values, or future user-provided content;
- cookies, authorization material, credentials, tokens, private keys, or recovery data;
- referrers, browser history, IP addresses, or user-agent strings;
- private infrastructure addresses, private service names, internal topology, or administrative endpoints.

The existing local appearance preference is not an observability channel and must remain browser-local.

## Hosting and Provider Logs

Cloudflare Pages and other infrastructure providers may generate platform-level logs or operational records outside this repository. This source tree does not assume that a provider logging product is enabled, retained, exported, or sufficient for GoreeCloud audit requirements unless that state is separately verified and documented.

Provider logs must not be represented in Wardveil status or release evidence as available merely because the hosting provider is capable of producing them.

## Error Handling and Resilience

The public site follows progressive enhancement. Core navigation, content, privacy guidance, security guidance, and policy pages must remain usable when optional JavaScript fails or browser storage is unavailable.

Client-side failures must fail safely and locally. A failure in appearance persistence, navigation enhancement, section highlighting, repository teaser enhancement, or footer-year enhancement must not disable security controls, expose private information, create a remote error-reporting channel, or make core public content unavailable.

Deployment verification and automated resilience checks remain the authoritative machine-readable evidence for release-blocking failures in the current static architecture.

## Wardveil Presentation Boundary

Public Wardveil presentation must remain evidence-scoped. The website may identify **Wardveil Security by GoreeCloud** as the platform security identity and explain its relationship to the underlying controls.

The website must not use **Protected by Wardveil** as a blanket decorative assurance for the entire public site unless a future, separately reviewed change defines the exact evidenced protection scope and the governing Wardveil standard supports that presentation.

Wardveil presentation must not imply trademark clearance, legal clearance, or a completed external name-conflict review. Those remain separate governance matters.

## Stable-Release Gate

A website revision that changes Wardveil presentation, observability, security reporting, runtime execution, browser data collection, authentication, authorization, or state-changing behavior is Stable only when:

1. the exact candidate passes the complete repository validation workflow;
2. the Wardveil and observability validator passes;
3. public security-reporting guidance and `security.txt` remain synchronized;
4. privacy and browser-origin validators confirm that no prohibited telemetry or remote runtime was introduced;
5. the isolated public artifact validates;
6. exact branch-preview verification passes before merge;
7. exact production verification passes after merge; and
8. any newly introduced dynamic capability has its required structured operational and security event coverage, sensitive-data exclusions, access controls, retention rules, failure behavior, and audit validation documented and tested.

Automated source validation does not by itself authorize repository publication, DNS changes, Cloudflare project-setting changes, or unrelated GoreeCloud production cutovers.
