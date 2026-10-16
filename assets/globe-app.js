/**
 * Signal Earth - Centerpiece Interactive Environmental Globe (assets/globe-app.js)
 * Built on Three.js (0.160.0) and Globe.gl (2.32.2) pinned distributions.
 * Features 14 color-coded planetary regions, NASA Worldview Snapshot API,
 * filterable legend, accessible keyboard table, and WebGL disabled fallback.
 */

(function () {
  'use strict';

  var globeInstance = null;
  var allRegions = [];
  var activeFilters = {
    'heat': true,
    'air quality': true,
    'ice': true,
    'forest': true,
    'sea level': true,
    'coral': true,
    'drought': true
  };
  var activeRegion = null;
  var isAutoRotating = true;
  var isGlobeInitialized = false;

  // NASA Worldview default date: 3 days prior to current system date (processing latency)
  function getDefaultWorldviewDate() {
    var d = new Date();
    d.setDate(d.getDate() - 3);
    return d.toISOString().split('T')[0];
  }

  function getTenYearAgoDate(isoDate) {
    var parts = isoDate.split('-');
    var yr = parseInt(parts[0], 10) - 10;
    return yr + '-' + parts[1] + '-' + parts[2];
  }

  // WebGL support detector
  function isWebGLAvailable() {
    try {
      var canvas = document.createElement('canvas');
      return !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
    } catch (e) {
      return false;
    }
  }

  // Fetch regions dataset
  function loadRegionsData(callback) {
    var path = 'data/regions.json';
    fetch(path)
      .then(function (res) {
        if (!res.ok) throw new Error('Network error loading regions');
        return res.json();
      })
      .then(function (data) {
        allRegions = data.regions || [];
        callback(null, allRegions);
      })
      .catch(function (err) {
        console.warn('Failed to fetch data/regions.json directly, using fallback.', err);
        // Fallback default regions
        allRegions = [
          {
            id: 'kanpur',
            name: 'Kanpur Observatory',
            region: 'Indo-Gangetic Basin, India',
            lat: 26.4499,
            lon: 80.3319,
            issue_type: 'air quality',
            issue_badge: 'Particulate Stagnation',
            color: '#F2A33A',
            bbox: [26.0, 79.8, 27.0, 80.8],
            summary: 'Central Ganga valley subject to acute winter boundary layer aerosol entrapment.',
            why_it_matters: 'Multiplies PM2.5 concentrations 4.2x above baseline with severe public health impact.',
            signal_shows: 'Documents a 4.2x winter surge ratio and an 855-day unmonitored regulatory hiatus.',
            metrics: [
              { name: 'Winter Multiplier', value: '4.2×', source: 'CPCB CAAQMS', url: 'investigations/kanpur.html', year: 2026 },
              { name: 'Documented Hiatus', value: '855 Days', source: 'Signal Earth Audit', url: 'known-problems.html', year: 2026 },
              { name: 'Urban Delta', value: '+3.60K', source: 'Landsat 8/9 TIRS-2', url: 'investigations/kanpur-uhi.html', year: 2026 }
            ],
            investigation_url: 'investigations/kanpur.html'
          }
        ];
        callback(null, allRegions);
      });
  }

  // Filter regions based on activeFilters state
  function getFilteredRegions() {
    return allRegions.filter(function (r) {
      return activeFilters[r.issue_type] !== false;
    });
  }

  // Initialize Globe
  function initGlobe(containerEl) {
    if (isGlobeInitialized) return;
    isGlobeInitialized = true;

    if (!isWebGLAvailable()) {
      showWebGLFallback(containerEl);
      return;
    }

    var skeletonEl = document.getElementById('globe-skeleton');
    if (skeletonEl) skeletonEl.style.display = 'flex';

    loadRegionsData(function (err, regions) {
      if (skeletonEl) skeletonEl.style.display = 'none';

      // Check prefers-reduced-motion
      var prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (prefersReducedMotion) isAutoRotating = false;

      var width = containerEl.clientWidth || window.innerWidth;
      var height = containerEl.clientHeight || (window.innerHeight * 0.85);

      if (typeof Globe === 'undefined') {
        console.error('Globe.gl library not loaded');
        showWebGLFallback(containerEl);
        return;
      }

      globeInstance = Globe()(containerEl)
        .width(width)
        .height(height)
        .backgroundColor('#0A1628')
        .globeImageUrl('https://unpkg.com/three-globe@2.31.0/example/img/earth-blue-marble.jpg')
        .bumpImageUrl('https://unpkg.com/three-globe@2.31.0/example/img/earth-topology.png')
        .showAtmosphere(true)
        .atmosphereColor('#2E6FD8')
        .atmosphereAltitude(0.22)
        // Rings layer for active pulsing markers
        .ringsData(getFilteredRegions())
        .ringLat(function (d) { return d.lat; })
        .ringLng(function (d) { return d.lon; })
        .ringColor(function (d) { return function (t) { return d.color || '#1FB6A6'; }; })
        .ringMaxRadius(3.5)
        .ringPropagationSpeed(2)
        .ringRepeatPeriod(1800)
        // Points layer for markers
        .pointsData(getFilteredRegions())
        .pointLat(function (d) { return d.lat; })
        .pointLng(function (d) { return d.lon; })
        .pointColor(function (d) { return d.color || '#1FB6A6'; })
        .pointAltitude(0.04)
        .pointRadius(0.85)
        .pointLabel(function (d) {
          return '<div style="background: rgba(10, 22, 40, 0.92); border: 1px solid ' + (d.color || '#1FB6A6') + '; padding: 6px 10px; border-radius: 4px; font-family: IBM Plex Mono, monospace; font-size: 11px; color: #F8FAFC;">' +
                 '<strong>' + d.name + '</strong><br>' +
                 '<span style="color: ' + (d.color || '#1FB6A6') + ';">● ' + d.issue_badge + '</span>' +
                 '</div>';
        })
        .onPointClick(function (d) {
          selectRegion(d);
        });

      // Controls configuration
      var controls = globeInstance.controls();
      controls.autoRotate = isAutoRotating;
      controls.autoRotateSpeed = 0.45;
      controls.enableDamping = true;
      controls.dampingFactor = 0.08;

      // Stop auto-rotation immediately when user starts dragging or interacting
      controls.addEventListener('start', function () {
        isAutoRotating = false;
        controls.autoRotate = false;
      });

      // Focus on India / Central Asia initially
      globeInstance.pointOfView({ lat: 24, lng: 75, altitude: 2.2 }, 1500);

      // Handle window resize
      window.addEventListener('resize', function () {
        if (!globeInstance) return;
        var w = containerEl.clientWidth || window.innerWidth;
        var h = containerEl.clientHeight || (window.innerHeight * 0.85);
        globeInstance.width(w).height(h);
      });

      // Check URL hash for initial deep-link (#region=kanpur)
      handleUrlHash();
      window.addEventListener('hashchange', handleUrlHash);

      // Populate accessibility list table
      populateKeyboardList(regions);
    });
  }

  // WebGL Fallback Map Renderer
  function showWebGLFallback(containerEl) {
    var skeletonEl = document.getElementById('globe-skeleton');
    if (skeletonEl) skeletonEl.style.display = 'none';

    containerEl.innerHTML =
      '<div style="width: 100%; height: 100%; min-height: 480px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #0A1628; color: #F8FAFC; padding: 2rem; text-align: center;">' +
        '<div style="font-family: var(--se-font-mono); font-size: 0.85rem; color: #F2A33A; margin-bottom: 0.75rem;">● 2D Planar Observation Fallback Active</div>' +
        '<h3 style="font-family: var(--se-font-serif); font-size: 1.8rem; margin: 0 0 1rem;">Planetary Telemetry Observation Stations</h3>' +
        '<p style="max-width: 600px; font-family: var(--se-font-sans); font-size: 0.95rem; line-height: 1.6; color: #94A3B8; margin-bottom: 1.5rem;">' +
          'WebGL hardware acceleration is unavailable in your browser. You can inspect all 14 active planetary observation stations below.' +
        '</p>' +
        '<img src="assets/river_basin_network.jpg" alt="Planetary observation map" style="max-width: 90%; max-height: 280px; border-radius: 8px; border: 1px solid #1E3456; margin-bottom: 1.5rem;">' +
        '<a href="#globe-regions-list" class="se-editorial-btn-primary">Browse All Regional Stations &darr;</a>' +
      '</div>';
  }

  // Update Points & Rings when filters change
  function updateGlobeLayers() {
    if (!globeInstance) return;
    var filtered = getFilteredRegions();
    globeInstance.pointsData(filtered);
    globeInstance.ringsData(filtered);
  }

  // Select Region and Open Side Drawer Panel
  function selectRegion(region) {
    if (!region) return;
    activeRegion = region;

    // Halt auto-rotation when focusing region
    if (globeInstance) {
      var controls = globeInstance.controls();
      controls.autoRotate = false;
      globeInstance.pointOfView({ lat: region.lat, lng: region.lon, altitude: 1.6 }, 1200);
    }

    var drawer = document.getElementById('globe-drawer');
    if (!drawer) return;

    // Set textual details
    document.getElementById('drawer-region-name').textContent = region.name;
    document.getElementById('drawer-coords').textContent = region.lat.toFixed(4) + '°N, ' + region.lon.toFixed(4) + '°E · ' + region.region;
    
    var badgeEl = document.getElementById('drawer-issue-badge');
    badgeEl.textContent = region.issue_badge;
    badgeEl.style.borderColor = region.color || '#1FB6A6';
    badgeEl.style.color = region.color || '#1FB6A6';

    document.getElementById('drawer-why-matters').textContent = region.why_it_matters || region.summary;
    document.getElementById('drawer-signal-shows').textContent = region.signal_shows || region.summary;

    // Metrics
    var metricsWrap = document.getElementById('drawer-metrics-list');
    metricsWrap.innerHTML = '';
    if (region.metrics && region.metrics.length) {
      region.metrics.forEach(function (m) {
        var row = document.createElement('div');
        row.className = 'se-drawer-metric-card';
        row.innerHTML =
          '<span class="se-drawer-metric-name">' + m.name + '</span>' +
          '<span class="se-drawer-metric-val">' + m.value + '</span>' +
          '<a href="' + m.url + '" target="_blank" rel="noopener noreferrer" class="se-drawer-metric-src">' + m.source + ' (' + (m.year || 2026) + ') &rarr;</a>';
        metricsWrap.appendChild(row);
      });
    }

    // Investigation link
    var investLink = document.getElementById('drawer-investigation-link');
    if (investLink) {
      investLink.href = region.investigation_url || 'research.html';
    }

    // Share link
    var shareInput = document.getElementById('drawer-share-input');
    if (shareInput) {
      var shareUrl = window.location.origin + window.location.pathname + '#region=' + region.id;
      shareInput.value = shareUrl;
    }

    // NASA Worldview Snapshot Integration
    var defaultDate = getDefaultWorldviewDate();
    var datePicker = document.getElementById('drawer-date-picker');
    if (datePicker) {
      datePicker.value = defaultDate;
      datePicker.max = defaultDate;
    }
    loadWorldviewSnapshot(region, defaultDate, false);

    // Open Drawer
    drawer.classList.add('is-open');
    drawer.setAttribute('aria-hidden', 'false');

    // Update URL hash smoothly without jump
    if (history.replaceState) {
      history.replaceState(null, null, '#region=' + region.id);
    }
  }

  // Load NASA Worldview Snapshot API image
  function loadWorldviewSnapshot(region, dateStr, isCompare) {
    var imgEl = document.getElementById('drawer-snapshot-img');
    var compImgEl = document.getElementById('drawer-compare-img');
    var worldviewLink = document.getElementById('drawer-worldview-link');
    var statusEl = document.getElementById('drawer-snapshot-status');

    if (!imgEl) return;

    var bbox = region.bbox || [region.lat - 1, region.lon - 1, region.lat + 1, region.lon + 1];
    var minLat = bbox[0], minLon = bbox[1], maxLat = bbox[2], maxLon = bbox[3];

    // NASA GIBS WMS / Snapshot query
    var targetDate = isCompare ? getTenYearAgoDate(dateStr) : dateStr;
    var snapshotUrl = 'https://wxs.earthdata.nasa.gov/api/v1/snapshot?REQUEST=GetSnapshot&TIME=' + targetDate + '&BBOX=' + minLat + ',' + minLon + ',' + maxLat + ',' + maxLon + '&CRS=EPSG:4326&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor&FORMAT=image/jpeg&WIDTH=640&HEIGHT=400';
    var wvPermalink = 'https://worldview.earthdata.nasa.gov/?v=' + minLon + ',' + minLat + ',' + maxLon + ',' + maxLat + '&l=Reference_Labels_15m,Reference_Features_15m,Coastlines_15m,MODIS_Terra_CorrectedReflectance_TrueColor&t=' + targetDate;

    if (worldviewLink) worldviewLink.href = wvPermalink;
    if (statusEl) statusEl.textContent = 'Loading satellite observation for ' + targetDate + '...';

    var targetImg = isCompare ? compImgEl : imgEl;
    targetImg.style.opacity = '0.3';

    var testImg = new Image();
    testImg.onload = function () {
      targetImg.src = snapshotUrl;
      targetImg.style.opacity = '1';
      if (statusEl) statusEl.textContent = 'NASA Worldview · Terra MODIS 250m (' + targetDate + ')';
    };
    testImg.onerror = function () {
      // Fallback local satellite asset if NASA Worldview network is unreachable or cloud obscured
      var fallbackSrc = region.id === 'kanpur' ? 'assets/satellite_view_kanpur_haze_20211111.jpg' :
                        region.id === 'delhi' ? 'assets/delhi_iss_night.jpg' :
                        region.id === 'arctic' ? 'assets/nasa_arctic_sea_ice.jpg' :
                        region.id === 'himalayas' ? 'assets/himalaya_haze_panorama.jpg' :
                        'assets/river_basin_network.jpg';
      targetImg.src = fallbackSrc;
      targetImg.style.opacity = '1';
      if (statusEl) statusEl.textContent = 'Cached satellite radiometry (' + targetDate + ')';
    };
    testImg.src = snapshotUrl;
  }

  // Handle URL Hash deep linking
  function handleUrlHash() {
    var hash = window.location.hash;
    if (hash && hash.indexOf('#region=') === 0) {
      var id = hash.replace('#region=', '');
      var found = allRegions.find(function (r) { return r.id === id; });
      if (found) {
        selectRegion(found);
      }
    }
  }

  // Accessible Keyboard Region Table
  function populateKeyboardList(regions) {
    var tableBody = document.getElementById('globe-keyboard-tbody');
    if (!tableBody) return;
    tableBody.innerHTML = '';

    regions.forEach(function (r, index) {
      var tr = document.createElement('tr');
      tr.innerHTML =
        '<td><strong>' + r.name + '</strong><br><span style="font-size: 11px; color: var(--se-text-muted);">' + r.region + '</span></td>' +
        '<td><span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: ' + (r.color || '#1FB6A6') + '; margin-right: 6px;"></span>' + r.issue_badge + '</td>' +
        '<td style="font-family: var(--se-font-mono); font-size: 12px;">' + r.lat.toFixed(2) + '°N, ' + r.lon.toFixed(2) + '°E</td>' +
        '<td><button type="button" class="se-stream-btn" data-region-id="' + r.id + '" style="font-size: 11px; padding: 3px 8px;">Focus on Globe</button></td>';

      tr.querySelector('button').addEventListener('click', function () {
        selectRegion(r);
        window.scrollTo({ top: document.getElementById('globe-section').offsetTop - 40, behavior: 'smooth' });
      });
      tableBody.appendChild(tr);
    });
  }

  // Wire UI Controls: Filters, Drawer Close, Date Picker, Share Copy
  function initGlobeControls() {
    // Filter tags
    var filterBtns = document.querySelectorAll('.se-globe-filter-btn');
    filterBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var issueType = btn.getAttribute('data-filter');
        activeFilters[issueType] = !activeFilters[issueType];

        if (activeFilters[issueType]) {
          btn.classList.add('active');
          btn.setAttribute('aria-pressed', 'true');
        } else {
          btn.classList.remove('active');
          btn.setAttribute('aria-pressed', 'false');
        }
        updateGlobeLayers();
      });
    });

    // Drawer close button
    var closeBtn = document.getElementById('globe-drawer-close');
    var drawer = document.getElementById('globe-drawer');
    if (closeBtn && drawer) {
      closeBtn.addEventListener('click', function () {
        drawer.classList.remove('is-open');
        drawer.setAttribute('aria-hidden', 'true');
      });
    }

    // Date picker
    var datePicker = document.getElementById('drawer-date-picker');
    if (datePicker) {
      datePicker.addEventListener('change', function () {
        if (activeRegion) {
          loadWorldviewSnapshot(activeRegion, datePicker.value, false);
        }
      });
    }

    // 10-year compare toggle
    var compareToggle = document.getElementById('drawer-compare-toggle');
    var compareWrap = document.getElementById('drawer-compare-wrap');
    if (compareToggle && compareWrap) {
      compareToggle.addEventListener('change', function () {
        if (compareToggle.checked) {
          compareWrap.style.display = 'block';
          if (activeRegion && datePicker) {
            loadWorldviewSnapshot(activeRegion, datePicker.value, true);
          }
        } else {
          compareWrap.style.display = 'none';
        }
      });
    }

    // Copy share link button
    var copyBtn = document.getElementById('drawer-copy-share-btn');
    var shareInput = document.getElementById('drawer-share-input');
    if (copyBtn && shareInput) {
      copyBtn.addEventListener('click', function () {
        shareInput.select();
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(shareInput.value).then(function () {
            copyBtn.textContent = 'Copied ✓';
            setTimeout(function () { copyBtn.textContent = 'Copy'; }, 2000);
          });
        }
      });
    }
  }

  // Lazy initialization with IntersectionObserver
  function setupLazyGlobe() {
    var container = document.getElementById('globe-container');
    if (!container) return;

    initGlobeControls();

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            initGlobe(container);
            observer.unobserve(entry.target);
          }
        });
      }, { rootMargin: '200px 0px' });
      observer.observe(container);
    } else {
      initGlobe(container);
    }
  }

  // Expose globally for manual standalone or embedded initialization
  window.SignalEarthGlobe = {
    init: setupLazyGlobe,
    selectRegion: selectRegion
  };

  document.addEventListener('DOMContentLoaded', setupLazyGlobe);

})();
