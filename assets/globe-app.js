/**
 * Signal Earth - Centerpiece Interactive Environmental Globe (assets/globe-app.js)
 * High-performance 3D Earth observation controller with Three.js (0.160.0) & Globe.gl (2.32.2).
 * Features 14 color-coded planetary regions, genuine NASA GIBS satellite radiometry,
 * quick-select region pills, filterable legend, accessible keyboard table, and WebGL disabled fallback.
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
        allRegions = [
          {
            id: 'kanpur',
            name: 'Kanpur Observatory',
            region: 'Central Indo-Gangetic Basin, India',
            lat: 26.4499,
            lon: 80.3319,
            issue_type: 'air quality',
            issue_badge: 'Particulate Stagnation & Hiatus',
            color: '#F2A33A',
            bbox: [26.0, 79.8, 27.0, 80.8],
            gibs_layer: 'MODIS_Terra_CorrectedReflectance_TrueColor',
            summary: 'Central Ganga valley subject to acute winter boundary layer aerosol entrapment.',
            why_it_matters: 'Meteorological inversions multiply particulate concentrations 4.2x above baseline with severe public health impact.',
            signal_shows: 'Documents a 4.2x winter surge ratio and an 855-day unmonitored regulatory hiatus.',
            metrics: [
              { name: 'Winter Multiplier', value: '4.2×', source: 'CPCB CAAQMS / Signal Earth Audit', url: 'investigations/kanpur.html', year: 2026 },
              { name: 'Documented Hiatus', value: '855 Days', source: 'Statutory Telemetry Audit', url: 'known-problems.html', year: 2026 },
              { name: 'Urban Heat Delta', value: '+3.60K', source: 'Landsat 8/9 TIRS-2 Band 10', url: 'investigations/kanpur-uhi.html', year: 2026 }
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

  // Render or populate Quick-Select Region Pills
  function renderRegionPills(regions) {
    var pillsContainer = document.getElementById('globe-regions-pills');
    if (!pillsContainer) return;

    pillsContainer.innerHTML = '';
    regions.forEach(function (r) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'se-globe-pill';
      btn.setAttribute('data-region-id', r.id);
      btn.innerHTML =
        '<span class="se-globe-pill-dot" style="background-color: ' + (r.color || '#1FB6A6') + ';"></span>' +
        r.name;

      btn.addEventListener('click', function () {
        selectRegion(r);
      });
      pillsContainer.appendChild(btn);
    });
  }

  // Highlight active pill
  function updateActivePill(regionId) {
    var pills = document.querySelectorAll('.se-globe-pill');
    pills.forEach(function (p) {
      if (p.getAttribute('data-region-id') === regionId) {
        p.classList.add('active');
        p.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      } else {
        p.classList.remove('active');
      }
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

      // Render Region Pills
      renderRegionPills(regions);

      // Build High-Performance Globe Instance (omitting heavy bump map & rings GC loops)
      globeInstance = Globe()(containerEl)
        .width(width)
        .height(height)
        .backgroundColor('#0A1628')
        .globeImageUrl('https://unpkg.com/three-globe@2.31.0/example/img/earth-night.jpg')
        .showAtmosphere(true)
        .atmosphereColor('#2E6FD8')
        .atmosphereAltitude(0.20)
        // High-contrast points
        .pointsData(getFilteredRegions())
        .pointLat(function (d) { return d.lat; })
        .pointLng(function (d) { return d.lon; })
        .pointColor(function (d) { return d.color || '#1FB6A6'; })
        .pointAltitude(0.035)
        .pointRadius(1.6)
        .pointLabel(function (d) {
          return '<div style="background: rgba(10, 22, 40, 0.94); border: 1px solid ' + (d.color || '#1FB6A6') + '; padding: 6px 10px; border-radius: 4px; font-family: IBM Plex Mono, monospace; font-size: 11px; color: #F8FAFC; pointer-events: none;">' +
                 '<strong>' + d.name + '</strong><br>' +
                 '<span style="color: ' + (d.color || '#1FB6A6') + ';">● ' + d.issue_badge + '</span>' +
                 '</div>';
        })
        .onPointClick(function (d) {
          selectRegion(d);
        })
        // Crisp labels orbiting with globe
        .labelsData(getFilteredRegions())
        .labelLat(function (d) { return d.lat; })
        .labelLng(function (d) { return d.lon; })
        .labelText(function (d) { return d.name; })
        .labelSize(1.1)
        .labelDotRadius(0.4)
        .labelColor(function (d) { return '#F8FAFC'; })
        .labelAltitude(0.04)
        .onLabelClick(function (d) {
          selectRegion(d);
        });

      // Broad click tolerance on globe surface: find closest region within 14 degrees
      globeInstance.onGlobeClick(function (coords) {
        if (!coords) return;
        var filtered = getFilteredRegions();
        var closest = null;
        var minDist = Infinity;
        filtered.forEach(function (r) {
          var dLat = r.lat - coords.lat;
          var dLon = r.lon - coords.lng;
          var dist = Math.sqrt(dLat * dLat + dLon * dLon);
          if (dist < minDist) {
            minDist = dist;
            closest = r;
          }
        });
        if (closest && minDist < 14) {
          selectRegion(closest);
        }
      });

      // Controls configuration
      var controls = globeInstance.controls();
      controls.autoRotate = isAutoRotating;
      controls.autoRotateSpeed = 0.5;
      controls.enableDamping = true;
      controls.dampingFactor = 0.1;

      // Stop auto-rotation immediately when user starts dragging or interacting
      controls.addEventListener('start', function () {
        isAutoRotating = false;
        controls.autoRotate = false;
      });

      // Handle window resize
      window.addEventListener('resize', function () {
        if (!globeInstance) return;
        var w = containerEl.clientWidth || window.innerWidth;
        var h = containerEl.clientHeight || (window.innerHeight * 0.85);
        globeInstance.width(w).height(h);
      });

      // Populate accessibility list table
      populateKeyboardList(regions);

      // Check URL hash for initial deep-link (#region=kanpur) or auto-select first region
      var initialHashMatch = handleUrlHash();
      if (!initialHashMatch && regions.length > 0) {
        // Select first region so information is immediately present
        selectRegion(regions[0]);
      }
      window.addEventListener('hashchange', handleUrlHash);
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

  // Update Points & Labels when filters change
  function updateGlobeLayers() {
    if (!globeInstance) return;
    var filtered = getFilteredRegions();
    globeInstance.pointsData(filtered);
    globeInstance.labelsData(filtered);
    renderRegionPills(filtered);
    if (activeRegion && activeFilters[activeRegion.issue_type] === false) {
      if (filtered.length > 0) selectRegion(filtered[0]);
    }
  }

  // Select Region and Open Side Drawer Panel
  function selectRegion(region) {
    if (!region) return;
    activeRegion = region;

    // Highlight pill
    updateActivePill(region.id);

    // Halt auto-rotation and smoothly focus region
    if (globeInstance) {
      var controls = globeInstance.controls();
      controls.autoRotate = false;
      globeInstance.pointOfView({ lat: region.lat, lng: region.lon, altitude: 1.55 }, 800);
    }

    var drawer = document.getElementById('globe-drawer');
    if (!drawer) return;

    // Set textual details
    var nameEl = document.getElementById('drawer-region-name');
    if (nameEl) nameEl.textContent = region.name;

    var coordsEl = document.getElementById('drawer-coords');
    if (coordsEl) coordsEl.textContent = region.lat.toFixed(4) + '°N, ' + region.lon.toFixed(4) + '°E · ' + region.region;
    
    var badgeEl = document.getElementById('drawer-issue-badge');
    if (badgeEl) {
      badgeEl.textContent = region.issue_badge;
      badgeEl.style.borderColor = region.color || '#1FB6A6';
      badgeEl.style.color = region.color || '#1FB6A6';
    }

    var whyEl = document.getElementById('drawer-why-matters');
    if (whyEl) whyEl.textContent = region.why_it_matters || region.summary;

    var signalEl = document.getElementById('drawer-signal-shows');
    if (signalEl) signalEl.textContent = region.signal_shows || region.summary;

    // Metrics
    var metricsWrap = document.getElementById('drawer-metrics-list');
    if (metricsWrap) {
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

    // If compare mode is active, load comparison image too
    var compareToggle = document.getElementById('drawer-compare-toggle');
    if (compareToggle && compareToggle.checked) {
      loadWorldviewSnapshot(region, defaultDate, true);
    }

    // Open Drawer
    drawer.classList.add('is-open');
    drawer.setAttribute('aria-hidden', 'false');

    // Update URL hash smoothly without scroll jump
    if (history.replaceState) {
      history.replaceState(null, null, '#region=' + region.id);
    }
  }

  // Load NASA Worldview Snapshot / Genuine Region Satellite Asset
  function loadWorldviewSnapshot(region, dateStr, isCompare) {
    var imgEl = document.getElementById('drawer-snapshot-img');
    var compImgEl = document.getElementById('drawer-compare-img');
    var worldviewLink = document.getElementById('drawer-worldview-link');
    var statusEl = document.getElementById('drawer-snapshot-status');

    if (!imgEl) return;

    var bbox = region.bbox || [region.lat - 1, region.lon - 1, region.lat + 1, region.lon + 1];
    var minLat = bbox[0], minLon = bbox[1], maxLat = bbox[2], maxLon = bbox[3];
    var targetDate = isCompare ? getTenYearAgoDate(dateStr) : dateStr;
    var layer = region.gibs_layer || 'MODIS_Terra_CorrectedReflectance_TrueColor';

    var targetImg = isCompare ? compImgEl : imgEl;
    if (!targetImg) return;

    // Accurate local high-resolution NASA GIBS asset
    var localAsset = isCompare
      ? 'assets/regions/' + region.id + '_10yr.jpg'
      : 'assets/regions/' + region.id + '.jpg';

    // Direct NASA Worldview web application permalink
    var wvPermalink = 'https://worldview.earthdata.nasa.gov/?v=' + minLon + ',' + minLat + ',' + maxLon + ',' + maxLat + '&l=Reference_Labels_15m,Reference_Features_15m,Coastlines_15m,' + layer + '&t=' + targetDate;
    if (worldviewLink) worldviewLink.href = wvPermalink;

    // Immediately show accurate local satellite radiometry (0ms delay)
    targetImg.src = localAsset;
    targetImg.style.opacity = '1';
    if (statusEl && !isCompare) {
      statusEl.textContent = 'NASA GIBS Observation · ' + region.name + ' (' + (region.gibs_layer ? 'MODIS 250m' : 'TrueColor') + ')';
    }

    // If user changed date from default, query live NASA GIBS WMS endpoint
    if (dateStr !== getDefaultWorldviewDate() && !isCompare) {
      if (statusEl) statusEl.textContent = 'Querying NASA GIBS WMS for ' + targetDate + '...';
      var liveWmsUrl = 'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?' +
        'SERVICE=WMS&REQUEST=GetMap&LAYERS=' + layer + '&VERSION=1.3.0&' +
        'FORMAT=image/jpeg&TRANSPARENT=true&WIDTH=640&HEIGHT=400&' +
        'CRS=EPSG:4326&BBOX=' + minLat + ',' + minLon + ',' + maxLat + ',' + maxLon + '&TIME=' + targetDate;

      var liveTest = new Image();
      liveTest.onload = function () {
        targetImg.src = liveWmsUrl;
        if (statusEl) statusEl.textContent = 'NASA GIBS Live WMS · ' + layer + ' (' + targetDate + ')';
      };
      liveTest.onerror = function () {
        if (statusEl) statusEl.textContent = 'Curated NASA GIBS radiometry archive displayed.';
      };
      liveTest.src = liveWmsUrl;
    }
  }

  // Handle URL Hash deep linking
  function handleUrlHash() {
    var hash = window.location.hash;
    if (hash && hash.indexOf('#region=') === 0) {
      var id = hash.replace('#region=', '');
      var found = allRegions.find(function (r) { return r.id === id; });
      if (found) {
        selectRegion(found);
        return true;
      }
    }
    return false;
  }

  // Accessible Keyboard Region Table
  function populateKeyboardList(regions) {
    var tableBody = document.getElementById('globe-keyboard-tbody');
    if (!tableBody) return;
    tableBody.innerHTML = '';

    regions.forEach(function (r) {
      var tr = document.createElement('tr');
      tr.innerHTML =
        '<td><strong>' + r.name + '</strong><br><span style="font-size: 11px; color: var(--se-text-muted);">' + r.region + '</span></td>' +
        '<td><span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: ' + (r.color || '#1FB6A6') + '; margin-right: 6px;"></span>' + r.issue_badge + '</td>' +
        '<td style="font-family: var(--se-font-mono); font-size: 12px;">' + r.lat.toFixed(2) + '°N, ' + r.lon.toFixed(2) + '°E</td>' +
        '<td><button type="button" class="se-stream-btn" data-region-id="' + r.id + '" style="font-size: 11px; padding: 3px 8px;">Focus on Globe</button></td>';

      tr.querySelector('button').addEventListener('click', function () {
        selectRegion(r);
        var sec = document.getElementById('globe-section');
        if (sec) window.scrollTo({ top: sec.offsetTop - 40, behavior: 'smooth' });
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

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupLazyGlobe);
  } else {
    setupLazyGlobe();
  }

})();
