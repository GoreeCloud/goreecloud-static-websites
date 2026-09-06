(() => {
  const root = document.documentElement;
  root.dataset.js = 'true';
  const key = 'goreecloud-appearance';
  try {
    const value = localStorage.getItem(key);
    if (value === 'light' || value === 'dark') {
      root.dataset.glzAppearance = value;
    } else {
      delete root.dataset.glzAppearance;
    }
  } catch (_) {
    delete root.dataset.glzAppearance;
  }
})();
