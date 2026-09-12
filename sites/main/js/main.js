/* GoreeCloud public website — appearance, navigation, and local-only repository discovery. */

const THEME_STORAGE_KEY = 'goreecloud-theme';
const THEME_MODES = ['system', 'light', 'dark'];
const THEME_COLORS = {
  dark: '#07111f',
  light: '#f4f7fb',
};
const root = document.documentElement;
const themeToggle = document.querySelector('.theme-toggle');
const themeIcon = document.querySelector('.theme-toggle-icon');
const themeLabel = document.querySelector('.theme-toggle-label');
const colorScheme = window.matchMedia('(prefers-color-scheme: light)');

root.dataset.js = 'true';
if (themeToggle) themeToggle.hidden = false;

function getThemeMode() {
  const explicitTheme = root.dataset.theme;
  return explicitTheme === 'light' || explicitTheme === 'dark' ? explicitTheme : 'system';
}

function updateThemeColors(mode) {
  document.querySelectorAll('meta[name="theme-color"][data-theme-color]').forEach((meta) => {
    const scheme = meta.dataset.themeColor;
    meta.content = mode === 'light' || mode === 'dark'
      ? THEME_COLORS[mode]
      : THEME_COLORS[scheme] ?? meta.content;
  });
}

function updateThemeControl() {
  if (!themeToggle || !themeIcon || !themeLabel) return;

  const currentMode = getThemeMode();
  const currentIndex = THEME_MODES.indexOf(currentMode);
  const nextMode = THEME_MODES[(currentIndex + 1) % THEME_MODES.length];
  const currentLabel = currentMode[0].toUpperCase() + currentMode.slice(1);
  const nextLabel = nextMode[0].toUpperCase() + nextMode.slice(1);
  const accessibleLabel = `Appearance: ${currentLabel}. Activate for ${nextLabel} mode.`;

  themeToggle.dataset.themeMode = currentMode;
  themeIcon.textContent = currentMode === 'system' ? '◐' : currentMode === 'light' ? '☀' : '☾';
  themeToggle.setAttribute('aria-label', accessibleLabel);
  themeToggle.setAttribute('title', accessibleLabel);
  themeLabel.textContent = accessibleLabel;
}

function setThemeMode(mode, { persist = true } = {}) {
  if (!THEME_MODES.includes(mode)) return;

  if (mode === 'system') {
    delete root.dataset.theme;
  } else {
    root.dataset.theme = mode;
  }

  updateThemeColors(mode);

  if (persist) {
    try {
      if (mode === 'system') {
        localStorage.removeItem(THEME_STORAGE_KEY);
      } else {
        localStorage.setItem(THEME_STORAGE_KEY, mode);
      }
    } catch {
      // The site remains fully usable when browser storage is unavailable.
    }
  }

  updateThemeControl();
}

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

updateThemeControl();

themeToggle?.addEventListener('click', () => {
  const currentIndex = THEME_MODES.indexOf(getThemeMode());
  const nextMode = THEME_MODES[(currentIndex + 1) % THEME_MODES.length];
  setThemeMode(nextMode);
});

colorScheme.addEventListener?.('change', () => {
  if (getThemeMode() === 'system') {
    updateThemeColors('system');
    updateThemeControl();
  }
});

const navToggle = document.querySelector('.nav-toggle');
const navToggleLabel = navToggle?.querySelector('.sr-only');
const nav = document.querySelector('.site-nav');
const desktopNavigation = window.matchMedia('(min-width: 721px)');

function updateNavigationControl(open) {
  if (!navToggle) return;
  navToggle.setAttribute('aria-expanded', String(open));
  if (navToggleLabel) navToggleLabel.textContent = open ? 'Close navigation' : 'Open navigation';
}

function closeNavigation({ restoreFocus = false } = {}) {
  if (!navToggle || !nav) return;
  nav.classList.remove('open');
  updateNavigationControl(false);
  if (restoreFocus) navToggle.focus();
}

if (navToggle && nav) {
  updateNavigationControl(nav.classList.contains('open'));

  navToggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    updateNavigationControl(open);
  });

  nav.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => closeNavigation());
  });

  document.addEventListener('click', (event) => {
    if (!nav.classList.contains('open')) return;
    if (nav.contains(event.target) || navToggle.contains(event.target)) return;
    closeNavigation();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && nav.classList.contains('open')) {
      closeNavigation({ restoreFocus: true });
    }
  });

  desktopNavigation.addEventListener?.('change', (event) => {
    if (event.matches) closeNavigation();
  });
}

const sectionLinks = nav
  ? Array.from(nav.querySelectorAll('a[href^="#"]')).filter((link) => link.hash.length > 1)
  : [];
const sectionEntries = sectionLinks
  .map((link) => ({ link, section: document.getElementById(link.hash.slice(1)) }))
  .filter(({ section }) => section);
let navigationFrame = null;

function updateActiveNavigation() {
  navigationFrame = null;
  if (!sectionEntries.length) return;

  const headerHeight = document.querySelector('.site-header')?.offsetHeight ?? 0;
  const marker = window.scrollY + headerHeight + Math.min(window.innerHeight * 0.18, 140);
  let activeId = '';

  for (const { section } of sectionEntries) {
    if (section.offsetTop <= marker) activeId = section.id;
  }

  if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) {
    activeId = sectionEntries.at(-1)?.section.id ?? activeId;
  }

  for (const { link, section } of sectionEntries) {
    if (section.id === activeId) {
      link.setAttribute('aria-current', 'location');
    } else {
      link.removeAttribute('aria-current');
    }
  }
}

function scheduleActiveNavigationUpdate() {
  if (navigationFrame !== null) return;
  navigationFrame = window.requestAnimationFrame(updateActiveNavigation);
}

if (sectionEntries.length) {
  updateActiveNavigation();
  window.addEventListener('scroll', scheduleActiveNavigationUpdate, { passive: true });
  window.addEventListener('resize', scheduleActiveNavigationUpdate);
}

const year = document.getElementById('year');
if (year) year.textContent = new Date().getFullYear();

const repositoryDirectory = document.querySelector('.repo-directory-section');
if (repositoryDirectory) {
  const directoryContainer = repositoryDirectory.querySelector('.container');
  const directoryHeading = directoryContainer?.querySelector('.compact-heading');
  const repositoryGroups = Array.from(repositoryDirectory.querySelectorAll('.repo-group'));
  const repositoryCards = repositoryGroups.flatMap((group) => Array.from(group.querySelectorAll('.repo-card')));

  if (directoryContainer && directoryHeading && repositoryGroups.length && repositoryCards.length) {
    const tools = document.createElement('section');
    tools.className = 'repo-tools';
    tools.setAttribute('aria-labelledby', 'repository-tools-title');

    const toolsHeader = document.createElement('div');
    toolsHeader.className = 'repo-tools-header';
    const toolsCopy = document.createElement('div');
    toolsCopy.className = 'repo-tools-copy';
    const toolsEyebrow = document.createElement('p');
    toolsEyebrow.className = 'eyebrow';
    toolsEyebrow.textContent = 'Local directory tools';
    const toolsTitle = document.createElement('h3');
    toolsTitle.id = 'repository-tools-title';
    toolsTitle.textContent = 'Find a repository';
    const toolsDescription = document.createElement('p');
    toolsDescription.textContent = 'Search by repository name, purpose, role, or functional group. Filters run only in this page and are not stored, added to the URL, or sent anywhere.';
    toolsCopy.append(toolsEyebrow, toolsTitle, toolsDescription);

    const resetButton = document.createElement('button');
    resetButton.type = 'button';
    resetButton.className = 'repo-reset-button';
    resetButton.textContent = 'Reset filters';
    resetButton.disabled = true;
    toolsHeader.append(toolsCopy, resetButton);

    const filterGrid = document.createElement('div');
    filterGrid.className = 'repo-filter-grid';

    const searchLabel = document.createElement('label');
    searchLabel.className = 'repo-filter-field repo-search-field';
    const searchLabelText = document.createElement('span');
    searchLabelText.textContent = 'Search repositories';
    const searchInput = document.createElement('input');
    searchInput.type = 'search';
    searchInput.autocomplete = 'off';
    searchInput.spellcheck = false;
    searchInput.placeholder = 'Search name, purpose, or role';
    searchInput.setAttribute('aria-describedby', 'repo-filter-status');
    searchLabel.append(searchLabelText, searchInput);

    const groupLabel = document.createElement('label');
    groupLabel.className = 'repo-filter-field';
    const groupLabelText = document.createElement('span');
    groupLabelText.textContent = 'Functional group';
    const groupSelect = document.createElement('select');
    const allGroupsOption = document.createElement('option');
    allGroupsOption.value = 'all';
    allGroupsOption.textContent = 'All functional groups';
    groupSelect.append(allGroupsOption);
    repositoryGroups.forEach((group, index) => {
      const option = document.createElement('option');
      option.value = String(index);
      option.textContent = group.querySelector('.repo-group-heading .eyebrow')?.textContent?.trim() || `Group ${index + 1}`;
      groupSelect.append(option);
    });
    groupLabel.append(groupLabelText, groupSelect);

    const visibilityField = document.createElement('div');
    visibilityField.className = 'repo-filter-field repo-visibility-field';
    const visibilityLabel = document.createElement('span');
    visibilityLabel.textContent = 'Visibility';
    const visibilityButtons = document.createElement('div');
    visibilityButtons.className = 'repo-visibility-buttons';
    visibilityButtons.setAttribute('role', 'group');
    visibilityButtons.setAttribute('aria-label', 'Repository visibility');

    let visibilityFilter = 'all';
    const visibilityOptions = [
      ['all', 'All'],
      ['public', 'Public'],
      ['private', 'Private'],
    ];
    const filterButtons = visibilityOptions.map(([value, label]) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'repo-filter-button';
      button.dataset.visibility = value;
      button.setAttribute('aria-pressed', String(value === 'all'));
      button.textContent = label;
      visibilityButtons.append(button);
      return button;
    });
    visibilityField.append(visibilityLabel, visibilityButtons);

    filterGrid.append(searchLabel, groupLabel, visibilityField);

    const feedback = document.createElement('div');
    feedback.className = 'repo-filter-feedback';
    const status = document.createElement('p');
    status.id = 'repo-filter-status';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    const emptyState = document.createElement('p');
    emptyState.className = 'repo-empty-state';
    emptyState.hidden = true;
    emptyState.textContent = 'No repositories match these filters. Try another search term or reset the filters.';
    feedback.append(status, emptyState);

    tools.append(toolsHeader, filterGrid, feedback);
    directoryHeading.insertAdjacentElement('afterend', tools);

    function repositoryVisibility(card) {
      return card.querySelector('.repo-visibility.public') ? 'public' : 'private';
    }

    function updateRepositoryFilters() {
      const query = searchInput.value.trim().toLowerCase();
      const selectedGroup = groupSelect.value;
      let visibleCount = 0;

      repositoryGroups.forEach((group, groupIndex) => {
        const groupSelected = selectedGroup === 'all' || selectedGroup === String(groupIndex);
        const groupContext = group.querySelector('.repo-group-heading')?.textContent?.trim().toLowerCase() || '';
        let visibleInGroup = 0;

        group.querySelectorAll('.repo-card').forEach((card) => {
          const haystack = `${groupContext} ${card.textContent || ''}`.toLowerCase();
          const matchesQuery = !query || haystack.includes(query);
          const matchesVisibility = visibilityFilter === 'all' || repositoryVisibility(card) === visibilityFilter;
          const matches = groupSelected && matchesQuery && matchesVisibility;
          card.hidden = !matches;
          if (matches) {
            visibleCount += 1;
            visibleInGroup += 1;
          }
        });

        group.hidden = visibleInGroup === 0;
      });

      filterButtons.forEach((button) => {
        button.setAttribute('aria-pressed', String(button.dataset.visibility === visibilityFilter));
      });

      const filtersActive = Boolean(query) || selectedGroup !== 'all' || visibilityFilter !== 'all';
      resetButton.disabled = !filtersActive;
      emptyState.hidden = visibleCount !== 0;
      status.textContent = visibleCount === repositoryCards.length
        ? `Showing all ${repositoryCards.length} repositories.`
        : `Showing ${visibleCount} of ${repositoryCards.length} repositories.`;
    }

    searchInput.addEventListener('input', updateRepositoryFilters);
    searchInput.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && searchInput.value) {
        searchInput.value = '';
        updateRepositoryFilters();
      }
    });
    groupSelect.addEventListener('change', updateRepositoryFilters);
    filterButtons.forEach((button) => {
      button.addEventListener('click', () => {
        visibilityFilter = button.dataset.visibility || 'all';
        updateRepositoryFilters();
      });
    });
    resetButton.addEventListener('click', () => {
      searchInput.value = '';
      groupSelect.value = 'all';
      visibilityFilter = 'all';
      updateRepositoryFilters();
      searchInput.focus();
    });

    updateRepositoryFilters();
  }
}

// Public-profile inventory follows the authoritative GoreeCloud social-media record.
const PUBLIC_PROFILES = [
  { name: 'Instagram', handle: '@goreecloud', role: 'Visual progress and demonstrations', href: 'https://instagram.com/goreecloud', icon: 'assets/social/instagram.ico', monogram: 'IG' },
  { name: 'Threads', handle: '@goreecloud', role: 'Conversations and community updates', href: 'https://www.threads.com/@goreecloud', monogram: 'TH' },
  { name: 'TikTok', handle: '@goreecloud', role: 'Short-form video and demonstrations', href: 'https://www.tiktok.com/@goreecloud', monogram: 'TT' },
  { name: 'X', handle: '@GoreeCloud', role: 'Concise technical updates and announcements', href: 'https://x.com/GoreeCloud', icon: 'assets/social/x.ico', monogram: 'X' },
  { name: 'Reddit', handle: 'u/goreecloud', role: 'Detailed technical discussions', href: 'https://www.reddit.com/user/goreecloud/', monogram: 'RD' },
  { name: 'Pinterest', handle: '@goreecloud', role: 'Evergreen visual discovery and references', href: 'https://www.pinterest.com/goreecloud/', monogram: 'PI' },
  { name: 'YouTube', handle: '@GoreeCloud', role: 'Long-form video and demonstrations', href: 'https://www.youtube.com/@GoreeCloud', icon: 'assets/social/youtube.ico', monogram: 'YT' },
  { name: 'GitHub', handle: 'GoreeCloud', role: 'Public source and development history', href: 'https://github.com/GoreeCloud', icon: 'assets/social/github.ico', monogram: 'GH' },
];

function createPublicProfileLink(profile, { compact = false } = {}) {
  const link = document.createElement('a');
  link.href = profile.href;
  link.target = '_blank';
  link.rel = 'me noopener noreferrer';
  link.setAttribute('aria-label', `${profile.name}: ${profile.handle}`);

  if (compact) {
    link.className = 'footer-social-link';
    link.textContent = profile.name;
    return link;
  }

  link.className = `social-card${profile.name === 'GitHub' ? ' github-card' : ''}`;
  const icon = document.createElement('span');
  icon.className = 'social-icon';
  icon.setAttribute('aria-hidden', 'true');
  if (profile.icon) {
    const image = document.createElement('img');
    image.src = profile.icon;
    image.alt = '';
    image.width = 52;
    image.height = 52;
    icon.append(image);
  } else {
    const monogram = document.createElement('span');
    monogram.className = 'social-monogram';
    monogram.textContent = profile.monogram;
    icon.append(monogram);
  }

  const name = document.createElement('strong');
  name.textContent = profile.name;
  const handle = document.createElement('span');
  handle.textContent = profile.handle;
  const role = document.createElement('small');
  role.textContent = profile.role;
  link.append(icon, name, handle, role);
  return link;
}

const followSection = document.getElementById('follow');
const socialGrid = followSection?.querySelector('.social-grid');
if (followSection && socialGrid) {
  socialGrid.replaceChildren(...PUBLIC_PROFILES.map((profile) => createPublicProfileLink(profile)));
  const heading = followSection.querySelector('.section-heading');
  if (heading && !followSection.querySelector('.social-scope-note')) {
    const note = document.createElement('p');
    note.className = 'social-scope-note';
    note.textContent = 'Six active GoreeCloud social-media accounts are listed here, with YouTube and GitHub included as additional public destinations.';
    heading.insertAdjacentElement('afterend', note);
  }
}

const footerGrid = document.querySelector('.site-footer .footer-grid');
const copyright = footerGrid?.querySelector('.copyright');
if (footerGrid && copyright && !footerGrid.querySelector('.footer-social')) {
  const social = document.createElement('nav');
  social.className = 'footer-social';
  social.setAttribute('aria-label', 'GoreeCloud public profiles');

  const label = document.createElement('strong');
  label.className = 'footer-social-label';
  label.textContent = 'Follow GoreeCloud';
  const links = document.createElement('div');
  links.className = 'footer-social-links';
  links.append(...PUBLIC_PROFILES.map((profile) => createPublicProfileLink(profile, { compact: true })));
  social.append(label, links);
  copyright.insertAdjacentElement('beforebegin', social);
}
