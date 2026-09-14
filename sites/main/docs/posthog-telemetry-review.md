# GoreeCloud Public Website — PostHog Telemetry Review

**Status:** Activation candidate / production verification pending
**Canonical source:** `GoreeCloud/goreecloud-static-websites/sites/main`
**Provider:** PostHog US Cloud
**PostHog project:** Project 606430
**Telemetry schema:** 0.1

## Purpose

PostHog is approved for narrowly scoped public-website product telemetry so GoreeCloud can confirm whether the public website is being used without introducing broad behavioral tracking.

The initial approved use case is limited to one event: `website opened`.

## Authoritative PostHog privacy state

On September 14, 2026, the connected PostHog project was re-read after the project privacy control was changed. Project 606430 reported client IP discard/anonymization enabled (`anonymize_ips: true`) and session recording disabled. No GoreeCloud website event had yet been ingested at that verification point.

The website event additionally sets `$geoip_disable: true`, so PostHog GeoIP enrichment is disabled for this event rather than using the connection IP before discard.

## Consent model

The browser integration is designed to:

- load no PostHog network resource before an explicit visitor choice;
- store only the first-party preference `goreecloud-analytics-consent` with values `granted` or `denied`;
- send telemetry only after the visitor grants analytics permission;
- provide an Analytics preferences control so the visitor can revoke the choice;
- remain disabled when browser storage is unavailable rather than weakening the consent boundary.

`POSTHOG_ACTIVATION = true` means the consent experience is available. It does **not** mean PostHog is contacted before consent.

## Event contract

The only initial event permitted by the client-side `before_send` gate is:

### `website opened`

Explicit GoreeCloud properties:

- `application`: `GoreeCloud Website`
- `environment`: `production` on `www.goreecloud.com`, otherwise `preview`
- `telemetry_schema`: `0.1`
- `$process_person_profile`: `false`
- `$geoip_disable`: `true`

PostHog technical routing fields required for event delivery may remain, including the public project token, an in-memory non-persistent distinct identifier, and SDK library/version fields. The `before_send` hook removes unrelated automatically attached browser, navigation, referral, and interaction properties from the event.

## Explicitly disabled collection

The client configuration disables:

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
- cross-subdomain cookies;
- person-profile processing for the website event;
- GeoIP enrichment for the website event.

The integration does not call `identify`.

## Data excluded by design

The event contract does not include page contents, form contents, search text, contact details, message text, filenames, document names, clipboard content, exact location, URL query parameters, referrers, user-agent details, or other user-generated content.

## Retention

The authoritative PostHog project currently reports a 12-month event-retention setting. That is the current provider-side retention associated with this integration and must be reviewed when the project retention setting or telemetry scope changes.

## Network boundary

The website Content Security Policy permits only the minimum PostHog origins needed by this integration:

- `script-src`: `https://us-assets.i.posthog.com`
- `connect-src`: `https://us.i.posthog.com`

No wildcard PostHog origin is approved by this telemetry contract.

## Production acceptance boundary

Source activation is not production acceptance. Main is still recorded in `sites/manifest.json` as a validated central source whose production deployment remains `legacy-source` until the separately governed Cloudflare source cutover and exact production verification are complete.

Production telemetry may be described as active only after all of the following are verified:

1. The exact activated source passes repository and Main-site validation.
2. The activated source is merged through the governed GitHub path.
3. The exact deployed `www.goreecloud.com` artifact is verified to contain the approved telemetry, privacy disclosure, and CSP contract.
4. A visitor explicitly grants analytics consent on the verified deployment.
5. PostHog independently shows the approved `website opened` event and the received event properties remain inside the approved contract.
6. PostHog still reports client IP discard enabled and session recording disabled.
7. Canonical GoreeCloud documentation is synchronized to the verified final state.

Until those production checks pass, GoreeCloud must describe this work as an activation candidate rather than active production analytics.
