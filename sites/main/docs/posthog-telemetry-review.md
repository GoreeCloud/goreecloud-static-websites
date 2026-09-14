# GoreeCloud Public Website — PostHog Telemetry Review

**Status:** Staged / inactive
**Canonical source:** `GoreeCloud/goreecloud-static-websites/sites/main`
**Provider:** PostHog US Cloud
**PostHog project:** Project 606430
**Telemetry schema:** 0.1

## Purpose

PostHog is being evaluated for narrowly scoped public-website product telemetry so GoreeCloud can confirm whether the public website is being used without introducing broad behavioral tracking.

The initial approved use case is limited to one event: `website opened`.

## Activation boundary

The integration is deliberately fail-closed in source. `js/telemetry.js` contains `POSTHOG_ACTIVATION = false` and performs no PostHog network request while that gate remains false.

Activation is blocked until the authoritative PostHog project is independently verified to discard client IP data. At the time this review was written, PostHog project 606430 reported IP anonymization/discard disabled. The connected PostHog API does not currently expose a project-settings write action for that control, and an authorized TinyFish browser attempt could not pass the PostHog login boundary. No project privacy setting was changed by that attempt.

The existing website Content Security Policy remains intentionally unchanged while telemetry is staged. It continues to allow only self-hosted scripts and no browser connections, providing an independent fail-closed control even if the source activation constant were changed accidentally.

## Consent model

When activation is eventually approved, the browser integration is designed to:

- load no PostHog network resource before an explicit visitor choice;
- store only the first-party preference `goreecloud-analytics-consent` with values `granted` or `denied`;
- send telemetry only after the visitor grants analytics permission;
- provide an Analytics preferences control so the visitor can revoke the choice;
- remain disabled when browser storage is unavailable rather than weakening the consent boundary.

## Event contract

The only initial event permitted by the client-side `before_send` gate is:

### `website opened`

Explicit GoreeCloud properties:

- `application`: `GoreeCloud Website`
- `environment`: `production`
- `telemetry_schema`: `0.1`
- `$process_person_profile`: `false`

PostHog technical routing fields required for event delivery may remain. The `before_send` hook removes unrelated automatically attached browser, navigation, referral, and interaction properties from the event.

## Explicitly disabled collection

The staged client configuration disables:

- interaction autocapture;
- automatic page views;
- automatic page leaves;
- session replay;
- dead-click capture;
- exception autocapture;
- heatmaps;
- performance/Web Vitals capture;
- feature-flag requests;
- externally loaded PostHog feature dependencies;
- persistent PostHog identity storage;
- cross-subdomain cookies.

The integration does not call `identify`, so `person_profiles: 'identified_only'` does not create person profiles for this anonymous website event.

## Data excluded by design

The event contract must not include page contents, form contents, search text, contact details, message text, filenames, document names, clipboard content, exact location, URL query parameters, referrers, user-agent details, or other user-generated content.

## Retention

The authoritative PostHog project currently reports a 12-month event-retention setting. That is the maximum provider-side retention presently associated with this staged integration and must be reviewed again before activation.

## Required activation verification

Activation requires all of the following to be verified against authoritative systems:

1. PostHog project 606430 reports client IP discard/anonymization enabled.
2. Session replay remains disabled.
3. Broad automatic collection remains disabled or is independently blocked by the client contract.
4. The website privacy statement is updated to accurately disclose optional PostHog analytics, purpose, recipient, consent, retention, local preference storage, and revocation.
5. The website CSP is changed only as narrowly as necessary for the approved PostHog US Cloud script and ingestion endpoints.
6. `scripts/validate_privacy_policy.py` is updated to validate the activated consent-first telemetry contract.
7. Source validation and deployment checks pass.
8. Production behavior is independently verified after deployment before documentation claims telemetry is active.

Until those conditions are satisfied, GoreeCloud must describe this integration as staged/inactive, not implemented in production.
