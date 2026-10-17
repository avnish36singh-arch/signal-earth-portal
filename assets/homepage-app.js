/**
 * Signal Earth - Homepage Application Controller (assets/homepage-app.js)
 * Manages live key-numbers fetching (/api/key-numbers with data/key-numbers.json fallback),
 * papers feed category filtering, and observation archive stream controls.
 */

(function () {
  'use strict';

  // 1. Fetch Key Numbers (API with fallback to static JSON)
  function initKeyNumbers() {
    var stripEl = document.getElementById('key-numbers-strip');
    if (!stripEl) return;

    var tempVal = document.getElementById('kn-temp-val');
    var tempSrc = document.getElementById('kn-temp-src');
    var co2Val = document.getElementById('kn-co2-val');
    var co2Src = document.getElementById('kn-co2-src');
    var iceVal = document.getElementById('kn-ice-val');
    var iceSrc = document.getElementById('kn-ice-src');
    var seaVal = document.getElementById('kn-sea-val');
    var seaSrc = document.getElementById('kn-sea-src');

    function applyData(data) {
      if (!data || !data.metrics) return;
      data.metrics.forEach(function (m) {
        if (m.id === 'global_temp_anomaly' && tempVal) {
          tempVal.textContent = m.value;
          if (tempSrc) { tempSrc.textContent = m.source; tempSrc.href = m.url; }
        } else if (m.id === 'atmospheric_co2' && co2Val) {
          co2Val.textContent = m.value;
          if (co2Src) { co2Src.textContent = m.source; co2Src.href = m.url; }
        } else if (m.id === 'arctic_sea_ice' && iceVal) {
          iceVal.textContent = m.value;
          if (iceSrc) { iceSrc.textContent = m.source; iceSrc.href = m.url; }
        } else if (m.id === 'sea_level_rise_rate' && seaVal) {
          seaVal.textContent = m.value;
          if (seaSrc) { seaSrc.textContent = m.source; seaSrc.href = m.url; }
        }
      });
    }

    // Fetch static JSON directly without serverless backend
    fetch('data/key-numbers.json')
      .then(function (res) {
        if (!res.ok) throw new Error('Static data unavailable');
        return res.json();
      })
      .then(function (json) {
        applyData(json);
      })
      .catch(function (err) {
        console.warn('Key numbers static load warning:', err);
      });
  }

  // 2. Papers Feed Category Filtering
  function initPapersFilter() {
    var chips = document.querySelectorAll('.se-paper-chip');
    var cards = document.querySelectorAll('.se-paper-card');

    if (!chips.length || !cards.length) return;

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        chips.forEach(function (c) { c.classList.remove('active'); c.setAttribute('aria-pressed', 'false'); });
        chip.classList.add('active');
        chip.setAttribute('aria-pressed', 'true');

        var filter = chip.getAttribute('data-filter').toLowerCase();

        cards.forEach(function (card) {
          var cardCat = (card.getAttribute('data-category') || '').toLowerCase();
          if (filter === 'all' || cardCat === filter) {
            card.style.display = 'flex';
          } else {
            card.style.display = 'none';
          }
        });
      });
    });
  }

  // 3. Observation Archive Stream Controls
  function initStreamControls() {
    var streamTrack = document.getElementById('se-stream-track');
    var streamBtn = document.getElementById('stream-toggle-btn');
    var streamIcon = document.getElementById('stream-toggle-icon');
    var streamText = document.getElementById('stream-toggle-text');
    var isStreamPaused = false;

    if (streamBtn && streamTrack) {
      streamBtn.addEventListener('click', function () {
        isStreamPaused = !isStreamPaused;
        if (isStreamPaused) {
          streamTrack.classList.add('is-paused');
          if (streamIcon) streamIcon.textContent = '▶';
          if (streamText) streamText.textContent = 'Resume Stream';
        } else {
          streamTrack.classList.remove('is-paused');
          if (streamIcon) streamIcon.textContent = '⏸';
          if (streamText) streamText.textContent = 'Pause Stream';
        }
      });
    }
  }

  // DOM Ready
  document.addEventListener('DOMContentLoaded', function () {
    initKeyNumbers();
    initPapersFilter();
    initStreamControls();
  });

})();
