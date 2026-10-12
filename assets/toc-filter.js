/**
 * Signal Earth - Table of Contents Category Filtering & Navigation
 */
(function () {
  'use strict';

  function initTocFilters() {
    var tabs = document.querySelectorAll('.se-toc-tab');
    var rows = document.querySelectorAll('.se-toc-row');

    if (!tabs.length || !rows.length) return;

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        var category = tab.getAttribute('data-filter');

        // Update active tab state
        tabs.forEach(function (t) {
          t.classList.remove('active');
          t.setAttribute('aria-selected', 'false');
        });
        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');

        // Filter rows
        rows.forEach(function (row) {
          var rowCategory = row.getAttribute('data-category');
          if (category === 'all' || rowCategory === category) {
            row.style.display = 'grid';
          } else {
            row.style.display = 'none';
          }
        });
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTocFilters);
  } else {
    initTocFilters();
  }
})();
