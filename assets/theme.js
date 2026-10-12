/**
 * Signal Earth - Global Theme Management System
 * Persists theme in localStorage and respects prefers-color-scheme.
 * Automatically injects theme toggle button into header navigation if absent.
 */
(function () {
  function getPreferredTheme() {
    try {
      var stored = localStorage.getItem('signal-earth-theme');
      if (stored === 'dark' || stored === 'light') return stored;
    } catch (e) {}
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  // 1. Immediate attribute set to avoid FOUT (Flash of Unstyled Theme)
  var currentTheme = getPreferredTheme();
  document.documentElement.setAttribute('data-theme', currentTheme);

  // 2. Setup Toggle Button
  function setupThemeToggle() {
    var toggleBtn = document.getElementById('se-theme-toggle');

    // If no toggle button exists on the page, dynamically create and insert into nav
    if (!toggleBtn) {
      toggleBtn = document.createElement('button');
      toggleBtn.type = 'button';
      toggleBtn.id = 'se-theme-toggle';
      toggleBtn.className = 'se-theme-toggle-btn';
      toggleBtn.setAttribute('aria-label', 'Toggle theme mode');
      toggleBtn.setAttribute('title', 'Switch light / dark mode');
      toggleBtn.innerHTML =
        '<svg class="se-theme-icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
          '<circle cx="12" cy="12" r="5"></circle>' +
          '<line x1="12" y1="1" x2="12" y2="3"></line>' +
          '<line x1="12" y1="21" x2="12" y2="23"></line>' +
          '<line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>' +
          '<line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>' +
          '<line x1="1" y1="12" x2="3" y2="12"></line>' +
          '<line x1="21" y1="12" x2="23" y2="12"></line>' +
          '<line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>' +
          '<line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>' +
        '</svg>' +
        '<svg class="se-theme-icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
          '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>' +
        '</svg>' +
        '<span class="se-theme-label">Theme</span>';

      var navLinks = document.querySelector('.se-nav-links') || document.querySelector('.se-editorial-nav-list');
      var navRight = document.querySelector('.se-editorial-header-right');
      var navInner = document.querySelector('.se-nav-inner') || document.querySelector('.se-editorial-header-inner');

      if (navLinks) {
        var li = document.createElement('li');
        li.className = 'se-nav-theme-item';
        li.appendChild(toggleBtn);
        navLinks.appendChild(li);
      } else if (navRight) {
        navRight.appendChild(toggleBtn);
      } else if (navInner) {
        navInner.appendChild(toggleBtn);
      } else {
        var header = document.querySelector('header');
        if (header) header.appendChild(toggleBtn);
      }
    }

    if (toggleBtn) {
      toggleBtn.addEventListener('click', function () {
        var active = document.documentElement.getAttribute('data-theme') || 'light';
        var next = active === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        try {
          localStorage.setItem('signal-earth-theme', next);
        } catch (e) {}
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupThemeToggle);
  } else {
    setupThemeToggle();
  }
})();
