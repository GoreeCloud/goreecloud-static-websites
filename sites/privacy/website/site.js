(() => {
  const root = document.documentElement;
  const key = 'goreecloud-privacy-site-appearance';
  const button = document.querySelector('[data-theme-toggle]');
  const brand = document.querySelector('.brand');
  const navLinks = [...document.querySelectorAll('.nav-wrap nav a[href^="#"]')];
  const sections = navLinks.map((link) => document.querySelector(link.getAttribute('href'))).filter(Boolean);
  const modes = ['system', 'light', 'dark'];
  let appearance = 'system';
  try {
    const stored = localStorage.getItem(key);
    if (modes.includes(stored)) appearance = stored;
  } catch (_) {}

  const label = () => appearance === 'system' ? 'System' : appearance[0].toUpperCase() + appearance.slice(1);
  const apply = () => {
    if (appearance === 'system') delete root.dataset.glzAppearance;
    else root.dataset.glzAppearance = appearance;
    if (button) {
      button.textContent = label();
      button.setAttribute('aria-label', `Appearance: ${label()}. Activate to change appearance.`);
    }
  };
  const setCurrent = (id) => {
    navLinks.forEach((link) => {
      if (link.getAttribute('href') === `#${id}`) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
  };

  apply();
  const initialSection = location.hash.slice(1);
  if (navLinks.some((link) => link.getAttribute('href') === `#${initialSection}`)) setCurrent(initialSection);
  else setCurrent('role');

  button?.addEventListener('click', () => {
    appearance = modes[(modes.indexOf(appearance) + 1) % modes.length];
    apply();
    try {
      if (appearance === 'system') localStorage.removeItem(key);
      else localStorage.setItem(key, appearance);
    } catch (_) {}
  });

  if (sections.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio);
      if (visible[0]) setCurrent(visible[0].target.id);
    }, { rootMargin: '-24% 0px -60% 0px', threshold: [0, .1, .25, .5] });
    sections.forEach((section) => observer.observe(section));
  }
  navLinks.forEach((link) => link.addEventListener('click', () => setCurrent(link.getAttribute('href').slice(1))));
  brand?.addEventListener('click', () => setCurrent('role'));
})();
