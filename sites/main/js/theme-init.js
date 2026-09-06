/* GoreeCloud public website — early appearance and application identity initialization.
 *
 * This tiny self-hosted script runs before stylesheets so an explicit Light or Dark
 * preference can be applied before the first paint. System mode requires no stored value.
 * It also publishes the local web app manifest without introducing an inline-script CSP exception.
 */

(() => {
  const THEME_STORAGE_KEY = 'goreecloud-theme';
  const MANIFEST_HREF = '/site.webmanifest';
  const THEME_COLORS = {
    dark: '#07111f',
    light: '#f4f7fb',
  };
  const root = document.documentElement;

  function ensureManifestLink() {
    if (document.querySelector('link[rel~="manifest"]')) return;

    const manifest = document.createElement('link');
    manifest.rel = 'manifest';
    manifest.href = MANIFEST_HREF;
    document.head.append(manifest);
  }

  function updateThemeColors(mode) {
    document.querySelectorAll('meta[name="theme-color"][data-theme-color]').forEach((meta) => {
      const scheme = meta.dataset.themeColor;
      meta.content = mode === 'light' || mode === 'dark'
        ? THEME_COLORS[mode]
        : THEME_COLORS[scheme] ?? meta.content;
    });
  }

  ensureManifestLink();

  try {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    if (savedTheme === 'light' || savedTheme === 'dark') {
      root.dataset.theme = savedTheme;
      updateThemeColors(savedTheme);
    } else if (savedTheme) {
      localStorage.removeItem(THEME_STORAGE_KEY);
    }
  } catch {
    // Follow the operating-system appearance when browser storage is unavailable.
  }

  function refreshPublicProductCopy() {
    const heroLabels = document.querySelector('.hero-labels');
    if (heroLabels && !heroLabels.querySelector('[data-platform-foundation="everkeep"]')) {
      const everkeep = document.createElement('a');
      everkeep.className = 'glaze-chip';
      everkeep.href = 'https://projects.goreecloud.com/';
      everkeep.dataset.platformFoundation = 'everkeep';
      everkeep.textContent = 'Everkeep';
      const identity = document.createElement('span');
      identity.className = 'glaze-chip';
      identity.dataset.platformFoundation = 'identity';
      identity.textContent = 'GoreeCloud Identity';
      const summary = heroLabels.querySelector('.eyebrow');
      if (summary) {
        heroLabels.insertBefore(everkeep, summary);
        heroLabels.insertBefore(identity, summary);
        summary.textContent = 'Design • Privacy • Security • Resilience • Identity';
      }
    }

    const products = {
      immich: {
        kicker: 'Photos & Memories',
        name: 'GoreeCloud Photos',
        copy: 'A GoreeCloud-maintained Immich foundation evolving toward a more independent first-party photos platform for preservation, organization, search, sharing, and Keepsake capabilities.',
        badge: 'Active Development',
        badgeClass: 'growing',
      },
      navidrome: {
        kicker: 'Music',
        name: 'GoreeCloud Music',
        copy: 'A native multi-user music service for owned libraries, scanning, metadata, artwork, playback, and the GoreeCloud Resonance capability family.',
        badge: 'Native Development',
        badgeClass: 'growing',
      },
      vaultwarden: {
        kicker: 'Passwords & Secrets',
        name: 'GoreeCloud Vault Server',
        copy: 'A GoreeCloud-maintained Vaultwarden foundation for passwords, credentials, secure records, and sensitive information while the product continues its controlled fork-to-native evolution.',
        badge: 'Active Development',
        badgeClass: 'growing',
      },
    };

    for (const [service, product] of Object.entries(products)) {
      const card = document.querySelector(`[data-service="${service}"]`);
      if (!card) continue;
      const kicker = card.querySelector('.service-kicker');
      const title = card.querySelector('h3');
      const copy = card.querySelector('p:not(.service-kicker)');
      const badge = card.querySelector('.badge');
      if (kicker) kicker.textContent = product.kicker;
      if (title) title.textContent = product.name;
      if (copy) copy.textContent = product.copy;
      if (badge) {
        badge.textContent = product.badge;
        badge.className = `badge ${product.badgeClass}`;
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', refreshPublicProductCopy, { once: true });
  } else {
    refreshPublicProductCopy();
  }
})();
