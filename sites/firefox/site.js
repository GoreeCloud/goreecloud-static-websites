(() => {
  const root = document.documentElement;
  const button = document.getElementById('theme-toggle');
  const saved = localStorage.getItem('goreecloud-theme');
  if (saved === 'light' || saved === 'dark') root.dataset.theme = saved;
  const current = () => root.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  const updateLabel = () => button?.setAttribute('aria-label', `Switch to ${current() === 'dark' ? 'light' : 'dark'} appearance`);
  updateLabel();
  button?.addEventListener('click', () => {
    const next = current() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    localStorage.setItem('goreecloud-theme', next);
    updateLabel();
  });
})();
