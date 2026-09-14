/* GoreeCloud public website — optional, consent-first telemetry.
 *
 * PostHog is never contacted until the visitor explicitly grants analytics consent.
 * The integration is intentionally limited to one minimized `website opened` event.
 */

(() => {
  'use strict';

  const POSTHOG_ACTIVATION = true;
  const CONSENT_STORAGE_KEY = 'goreecloud-analytics-consent';
  const WEBSITE_EVENT = 'website opened';
  const POSTHOG_TOKEN = 'phc_q6ASRxAkQW9mXnjJfNHeZAM6LzyYeiYQbtVuj4seiyEb';
  const POSTHOG_API_HOST = 'https://us.i.posthog.com';
  const POSTHOG_DEFAULTS = '2026-05-30';
  const TELEMETRY_ENVIRONMENT = window.location.hostname === 'www.goreecloud.com' ? 'production' : 'preview';

  const TELEMETRY_STATUS = Object.freeze({
    staged: !POSTHOG_ACTIVATION,
    provider: 'PostHog US Cloud',
    schema: '0.1',
    consentRequired: true,
  });

  window.GoreeCloudTelemetry = Object.freeze({
    status: TELEMETRY_STATUS,
    capture() {
      return false;
    },
  });

  if (!POSTHOG_ACTIVATION) return;

  function readConsent() {
    try {
      const value = localStorage.getItem(CONSENT_STORAGE_KEY);
      return value === 'granted' || value === 'denied' ? value : null;
    } catch {
      return null;
    }
  }

  function writeConsent(value) {
    try {
      localStorage.setItem(CONSENT_STORAGE_KEY, value);
      return true;
    } catch {
      return false;
    }
  }

  function scrubEvent(event) {
    if (!event || event.event !== WEBSITE_EVENT) return null;

    const source = event.properties || {};
    const properties = {
      token: source.token,
      distinct_id: source.distinct_id,
      $lib: source.$lib,
      $lib_version: source.$lib_version,
      $process_person_profile: false,
      $geoip_disable: true,
      application: source.application,
      environment: source.environment,
      telemetry_schema: source.telemetry_schema,
    };

    for (const key of Object.keys(properties)) {
      if (properties[key] === undefined) delete properties[key];
    }

    return { ...event, properties };
  }

  function installPostHogStub() {
    const t = document;
    const e = window.posthog || [];
    let o;
    let n;
    let p;
    let r;

    if (e.__SV || (window.posthog && window.posthog.__loaded)) return;

    window.posthog = e;
    e._i = [];
    e.init = function init(i, s, a) {
      function g(target, method) {
        const parts = method.split('.');
        if (parts.length === 2) {
          target = target[parts[0]];
          method = parts[1];
        }
        target[method] = function queuedMethod() {
          target.push([method].concat(Array.prototype.slice.call(arguments, 0)));
        };
      }

      if (!p) {
        p = t.createElement('script');
        p.type = 'text/javascript';
        p.crossOrigin = 'anonymous';
        p.async = true;
        p.src = s.api_host.replace('.i.posthog.com', '-assets.i.posthog.com') + '/static/array.js';
        p.onerror = function onPostHogLoadError() {
          p = null;
        };
        r = t.getElementsByTagName('script')[0];
        r.parentNode.insertBefore(p, r);
      }

      let u = e;
      if (a !== undefined) {
        u = e[a] = [];
      } else {
        a = 'posthog';
      }
      u.people = u.people || [];
      Object.defineProperty(u, 'toString', {
        configurable: true,
        enumerable: false,
        writable: true,
        value: function toString(detail) {
          let name = 'posthog';
          if (a !== 'posthog') name += `.${a}`;
          if (!detail) name += ' (stub)';
          return name;
        },
      });
      Object.defineProperty(u.people, 'toString', {
        configurable: true,
        enumerable: false,
        writable: true,
        value: function peopleToString() {
          return `${u.toString(1)}.people (stub)`;
        },
      });

      o = 'capture identify alias people.set people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing clear_opt_in_out_capturing reset isFeatureEnabled onFeatureFlags getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group shutdown'.split(' ');
      for (n = 0; n < o.length; n += 1) g(u, o[n]);
      e._i.push([i, s, a]);
    };
    e.__SV = 1;
  }

  function enableTelemetry() {
    if (readConsent() !== 'granted') return;

    installPostHogStub();
    window.posthog.init(POSTHOG_TOKEN, {
      api_host: POSTHOG_API_HOST,
      defaults: POSTHOG_DEFAULTS,
      person_profiles: 'identified_only',
      persistence: 'memory',
      cross_subdomain_cookie: false,
      autocapture: false,
      capture_pageview: false,
      capture_pageleave: false,
      capture_dead_clicks: false,
      capture_exceptions: false,
      capture_heatmaps: false,
      capture_performance: false,
      disable_session_recording: true,
      disable_external_dependency_loading: true,
      advanced_disable_flags: true,
      before_send: scrubEvent,
    });

    window.posthog.clear_opt_in_out_capturing();
    window.posthog.capture(WEBSITE_EVENT, {
      application: 'GoreeCloud Website',
      environment: TELEMETRY_ENVIRONMENT,
      telemetry_schema: '0.1',
      $process_person_profile: false,
      $geoip_disable: true,
    });
  }

  function revokeTelemetry() {
    if (!writeConsent('denied')) return;
    if (window.posthog && typeof window.posthog.opt_out_capturing === 'function') {
      window.posthog.opt_out_capturing();
    }
  }

  function makeButton(label, className, action) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = className;
    button.textContent = label;
    button.addEventListener('click', action);
    return button;
  }

  function showConsentPrompt() {
    if (document.getElementById('goreecloud-analytics-consent')) return;

    const notice = document.createElement('section');
    notice.id = 'goreecloud-analytics-consent';
    notice.className = 'glaze-callout';
    notice.setAttribute('role', 'region');
    notice.setAttribute('aria-labelledby', 'goreecloud-analytics-consent-title');

    const copy = document.createElement('div');
    const title = document.createElement('h2');
    title.id = 'goreecloud-analytics-consent-title';
    title.textContent = 'Optional anonymous analytics';
    const description = document.createElement('p');
    description.textContent = 'GoreeCloud can send one minimized website-open event to PostHog to understand whether the public site is being used. No analytics is sent unless you allow it.';
    const privacy = document.createElement('a');
    privacy.href = '/privacy.html';
    privacy.textContent = 'Read the website privacy details';
    copy.append(title, description, privacy);

    const actions = document.createElement('div');
    actions.className = 'hero-actions';
    actions.append(
      makeButton('Allow anonymous analytics', 'button primary glaze-button', () => {
        if (!writeConsent('granted')) return;
        notice.remove();
        enableTelemetry();
      }),
      makeButton('No thanks', 'button secondary glaze-button', () => {
        revokeTelemetry();
        notice.remove();
      }),
    );

    notice.append(copy, actions);
    const main = document.querySelector('main');
    if (main && main.parentNode) main.parentNode.insertBefore(notice, main);
  }

  function installPreferencesControl() {
    if (document.getElementById('goreecloud-analytics-preferences')) return;
    const footerLinks = document.querySelector('.footer-links');
    if (!footerLinks) return;

    const button = makeButton('Analytics preferences', 'button secondary glaze-button', () => {
      revokeTelemetry();
      showConsentPrompt();
    });
    button.id = 'goreecloud-analytics-preferences';
    footerLinks.append(button);
  }

  function start() {
    const consent = readConsent();
    installPreferencesControl();
    if (consent === 'granted') {
      enableTelemetry();
    } else if (consent !== 'denied') {
      showConsentPrompt();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }
})();
