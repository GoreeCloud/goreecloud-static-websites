(() => {
  const root = document.documentElement;
  const key = 'goreecloud-appearance';
  const appearanceButton = document.querySelector('.appearance-toggle');
  const navButton = document.querySelector('.nav-toggle');
  const nav = document.querySelector('#primary-nav');
  const year = document.querySelector('#year');
  const modes = ['system', 'light', 'dark'];

  const currentMode = () => {
    const explicit = root.dataset.glzAppearance;
    return explicit === 'light' || explicit === 'dark' ? explicit : 'system';
  };

  const applyMode = (mode) => {
    if (mode === 'light' || mode === 'dark') {
      root.dataset.glzAppearance = mode;
    } else {
      delete root.dataset.glzAppearance;
    }
    try {
      if (mode === 'system') localStorage.removeItem(key);
      else localStorage.setItem(key, mode);
    } catch (_) {}
    if (appearanceButton) {
      const label = mode[0].toUpperCase() + mode.slice(1);
      appearanceButton.textContent = label;
      appearanceButton.setAttribute('aria-label', `Appearance: ${label}. Change appearance.`);
    }
  };

  if (appearanceButton) {
    applyMode(currentMode());
    appearanceButton.hidden = false;
    appearanceButton.addEventListener('click', () => {
      const mode = currentMode();
      const next = modes[(modes.indexOf(mode) + 1) % modes.length];
      applyMode(next);
    });
  }

  if (navButton && nav) {
    navButton.addEventListener('click', () => {
      const open = navButton.getAttribute('aria-expanded') === 'true';
      navButton.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('is-open', !open);
    });
    nav.addEventListener('click', (event) => {
      if (event.target.closest('a')) {
        navButton.setAttribute('aria-expanded', 'false');
        nav.classList.remove('is-open');
      }
    });
  }

  if (year) year.textContent = String(new Date().getFullYear());
})();
