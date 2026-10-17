/**
 * Signal Earth : Interactive 3D Planetary Country Globe (assets/globe-country.js)
 * Full-viewport WebGL 3D Earth visualization tracking sovereign environmental metrics.
 * Built with Three.js (0.160.0) and Globe.gl (2.32.2).
 * Strict typography: ZERO EM DASHES.
 */

(function () {
  'use strict';

  var globeContainer = document.getElementById('globe-container');
  var globeSkeleton = document.getElementById('globe-skeleton');
  var searchInput = document.getElementById('globe-country-search');
  var searchResults = document.getElementById('globe-search-results');
  var metricSelect = document.getElementById('globe-metric-select');
  var rotateToggleBtn = document.getElementById('globe-rotate-btn');
  var resetViewBtn = document.getElementById('globe-reset-btn');
  var pillsContainer = document.getElementById('globe-pills-bar');
  var legendContainer = document.getElementById('globe-legend');

  if (!globeContainer) return;

  var myGlobe = null;
  var countriesIndex = {};
  var allCountriesList = [];
  var isAutoRotating = true;
  var hoverD = null;
  var currentMetric = 'pm25';

  // Check prefers-reduced-motion
  var prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReducedMotion) {
    isAutoRotating = false;
  }

  // Metric color scale configurations (Colourblind-safe sequential & diverging)
  var METRIC_CONFIGS = {
    pm25: {
      name: 'Annual Mean PM2.5',
      unit: 'µg/m³',
      min: 5,
      max: 60,
      type: 'sequential_warm',
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        // 5 (clean emerald) -> 15 (yellow) -> 35 (orange) -> 60+ (crimson)
        if (v <= 5) return '#10B981';
        if (v <= 15) return interpolateHex('#10B981', '#FBBF24', (v - 5) / 10);
        if (v <= 35) return interpolateHex('#FBBF24', '#F97316', (v - 15) / 20);
        return interpolateHex('#F97316', '#EF4444', Math.min(1, (v - 35) / 25));
      }
    },
    temp_anomaly: {
      name: 'Temperature Anomaly',
      unit: '°C',
      min: -0.5,
      max: 2.5,
      type: 'diverging_cool_warm',
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        // -0.5 (blue) -> 0.5 (slate) -> 1.5 (amber) -> 2.5+ (crimson)
        if (v <= 0.5) return interpolateHex('#3B82F6', '#94A3B8', (v + 0.5) / 1.0);
        if (v <= 1.5) return interpolateHex('#94A3B8', '#F59E0B', (v - 0.5) / 1.0);
        return interpolateHex('#F59E0B', '#EF4444', Math.min(1, (v - 1.5) / 1.0));
      }
    },
    co2_per_capita: {
      name: 'CO2 per Capita',
      unit: 't/person',
      min: 0.5,
      max: 18,
      type: 'sequential',
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        if (v <= 3) return interpolateHex('#10B981', '#FBBF24', v / 3);
        if (v <= 10) return interpolateHex('#FBBF24', '#F97316', (v - 3) / 7);
        return interpolateHex('#F97316', '#9333EA', Math.min(1, (v - 10) / 8));
      }
    },
    total_co2: {
      name: 'Total Territorial CO2',
      unit: 'Mt/yr',
      min: 10,
      max: 5000,
      type: 'sequential',
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        var logV = Math.log10(Math.max(1, v));
        // log scale: 1 (10 Mt) to 4 (10,000 Mt)
        var t = Math.min(1, Math.max(0, (logV - 1) / 3));
        return interpolateHex('#34D399', '#EF4444', t);
      }
    },
    renewable_elec_share: {
      name: 'Renewable Electricity Share',
      unit: '%',
      min: 0,
      max: 100,
      type: 'sequential_green',
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        if (v <= 30) return interpolateHex('#475569', '#0D9488', v / 30);
        return interpolateHex('#0D9488', '#10B981', Math.min(1, (v - 30) / 70));
      }
    },
    forest_share: {
      name: 'Forest Area Share',
      unit: '%',
      min: 0,
      max: 75,
      type: 'sequential_forest',
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        if (v <= 25) return interpolateHex('#E2E8F0', '#4ADE80', v / 25);
        return interpolateHex('#4ADE80', '#15803D', Math.min(1, (v - 25) / 50));
      }
    },
    forest_change: {
      name: '10-Yr Forest Net Change',
      unit: '%',
      min: -15,
      max: 15,
      type: 'diverging_forest',
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        if (v < 0) return interpolateHex('#EF4444', '#94A3B8', Math.min(1, (v + 15) / 15));
        return interpolateHex('#94A3B8', '#10B981', Math.min(1, v / 15));
      }
    }
  };

  function interpolateHex(hex1, hex2, factor) {
    factor = Math.max(0, Math.min(1, factor));
    var c1 = parseInt(hex1.replace('#', ''), 16);
    var c2 = parseInt(hex2.replace('#', ''), 16);
    var r1 = (c1 >> 16) & 255, g1 = (c1 >> 8) & 255, b1 = c1 & 255;
    var r2 = (c2 >> 16) & 255, g2 = (c2 >> 8) & 255, b2 = c2 & 255;
    var r = Math.round(r1 + factor * (r2 - r1));
    var g = Math.round(g1 + factor * (g2 - g1));
    var b = Math.round(b1 + factor * (b2 - b1));
    return 'rgb(' + r + ',' + g + ',' + b + ')';
  }

  // Check WebGL availability
  function isWebGLAvailable() {
    try {
      var canvas = document.createElement('canvas');
      return !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
    } catch (e) {
      return false;
    }
  }

  if (!isWebGLAvailable()) {
    if (globeSkeleton) {
      globeSkeleton.innerHTML = '<div style="padding: 2rem; text-align: center; color: #94A3B8; font-family: var(--se-font-sans);">' +
        '<p style="font-size: 1.1rem; color: #F8FAFC; margin-bottom: 0.5rem;">WebGL acceleration is unavailable in your browser environment.</p>' +
        '<p style="font-size: 0.9rem; margin-bottom: 1.5rem;">You can explore all sovereign country profiles using the accessible directory table below.</p>' +
        '<a href="#accessible-country-index" class="se-stream-btn" style="display: inline-block; background: #1FB6A6; color: #0A1628; font-weight: 600;">Browse Country Directory &darr;</a>' +
        '</div>';
    }
    return;
  }

  // Load countries index and boundary GeoJSON concurrently
  Promise.all([
    fetch('data/countries.json').then(function (r) { return r.json(); }),
    fetch('data/world-110m.geojson').then(function (r) { return r.json(); })
  ])
  .then(function (results) {
    var indexData = results[0];
    var geoData = results[1];

    allCountriesList = indexData;
    indexData.forEach(function (c) {
      countriesIndex[c.iso3.toUpperCase()] = c;
    });

    initGlobe(geoData);
    initMetricSelector();
    initSearch();
    initPills();
    initControls();
    updateLegend();
    populateAccessibleIndex(indexData);

    if (globeSkeleton) {
      globeSkeleton.style.opacity = '0';
      setTimeout(function () {
        if (globeSkeleton.parentNode) globeSkeleton.parentNode.removeChild(globeSkeleton);
      }, 400);
    }
  })
  .catch(function (err) {
    console.error('Failed to load globe data:', err);
    if (globeSkeleton) {
      globeSkeleton.innerHTML = '<div style="color: #F87171; font-family: var(--se-font-mono); font-size: 0.85rem; padding: 2rem; text-align: center;">' +
        'Unable to load planetary boundary data. Please reload or browse the country directory below.' +
        '</div>';
    }
  });

  function getCountryMetric(iso3, metricKey) {
    var c = countriesIndex[iso3];
    if (!c || !c.indicators || !c.indicators[metricKey]) return null;
    return c.indicators[metricKey];
  }

  function getPolygonColor(feature) {
    var iso3 = getIso3(feature);
    var metricObj = getCountryMetric(iso3, currentMetric);
    var cfg = METRIC_CONFIGS[currentMetric] || METRIC_CONFIGS.pm25;

    if (!metricObj || metricObj.value === null || metricObj.value === undefined) {
      // Visibly distinct unranked / no-data color: dark muted slate with opacity
      return 'rgba(71, 85, 105, 0.45)';
    }

    var baseColor = cfg.interpolate(metricObj.value);
    if (!baseColor) return 'rgba(71, 85, 105, 0.45)';

    // Parse rgb or hex to rgba with subtle translucency over satellite marble
    if (baseColor.indexOf('rgb') === 0) {
      return baseColor.replace('rgb', 'rgba').replace(')', ', 0.78)');
    }
    return baseColor;
  }

  function initGlobe(geoData) {
    var width = globeContainer.clientWidth;
    var height = globeContainer.clientHeight;

    myGlobe = Globe()
      (globeContainer)
      .globeImageUrl('assets/earth-blue-marble.jpg')
      .backgroundColor('rgba(10, 22, 40, 0)')
      .showAtmosphere(true)
      .atmosphereColor('#1FB6A6')
      .atmosphereAltitude(0.18)
      .width(width)
      .height(height)
      .polygonsData(geoData.features)
      .polygonAltitude(function (d) {
        return d === hoverD ? 0.045 : 0.006;
      })
      .polygonCapColor(function (d) {
        if (d === hoverD) {
          return 'rgba(255, 255, 255, 0.9)';
        }
        return getPolygonColor(d);
      })
      .polygonSideColor(function () {
        return 'rgba(255, 255, 255, 0.12)';
      })
      .polygonStrokeColor(function (d) {
        if (d === hoverD) {
          return '#1FB6A6';
        }
        return 'rgba(255, 255, 255, 0.28)';
      })
      .polygonLabel(function (d) {
        var iso3 = getIso3(d);
        var countryMeta = countriesIndex[iso3];
        var name = (d.properties && d.properties.NAME) || iso3;
        var region = (countryMeta && countryMeta.region) || (d.properties && d.properties.REGION_UN) || 'Global';

        var metricObj = getCountryMetric(iso3, currentMetric);
        var cfg = METRIC_CONFIGS[currentMetric] || METRIC_CONFIGS.pm25;

        var metricLine = '';
        if (metricObj && metricObj.value !== null && metricObj.value !== undefined) {
          var valStr = metricObj.formatted || (metricObj.value + ' ' + (metricObj.unit || ''));
          var yrStr = metricObj.year ? ' (' + metricObj.year + ')' : '';
          var rkStr = metricObj.rank ? ' · Rank #' + metricObj.rank + (metricObj.total_ranked ? ' of ' + metricObj.total_ranked : '') : '';
          metricLine = '<div style="font-family: monospace; font-size: 0.85rem; font-weight: 700; color: #1FB6A6; margin-top: 0.35rem;">' +
            cfg.name + ': ' + valStr + yrStr +
            '</div>' +
            '<div style="font-size: 0.72rem; color: #94A3B8; margin-top: 2px;">' + rkStr + '</div>';
        } else {
          metricLine = '<div style="font-family: monospace; font-size: 0.8rem; color: #94A3B8; margin-top: 0.35rem; font-style: italic;">' +
            cfg.name + ': No data / Unranked' +
            '</div>';
        }

        return '<div style="background: rgba(10, 22, 40, 0.96); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.22); border-radius: 6px; padding: 0.75rem 1rem; color: #F8FAFC; max-width: 300px; box-shadow: 0 12px 28px rgba(0,0,0,0.6); pointer-events: none;">' +
          '<div style="font-family: Georgia, serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; line-height: 1.2;">' + name + ' <span style="font-family: monospace; font-size: 0.75rem; color: #94A3B8; font-weight: normal;">[' + iso3 + ']</span></div>' +
          '<div style="font-size: 0.75rem; color: #CBD5E1; margin-top: 2px;">' + region + '</div>' +
          metricLine +
          '<div style="font-size: 0.75rem; color: #5EEAD4; margin-top: 0.5rem; font-weight: 600;">Click to open sovereign dossier &rarr;</div>' +
          '</div>';
      })
      .onPolygonHover(function (d) {
        hoverD = d;
        globeContainer.style.cursor = d ? 'pointer' : 'grab';
        myGlobe
          .polygonAltitude(function (polygon) { return polygon === hoverD ? 0.045 : 0.006; })
          .polygonCapColor(function (polygon) {
            if (polygon === hoverD) return 'rgba(255, 255, 255, 0.9)';
            return getPolygonColor(polygon);
          })
          .polygonStrokeColor(function (polygon) {
            if (polygon === hoverD) return '#1FB6A6';
            return 'rgba(255, 255, 255, 0.28)';
          });
      })
      .onPolygonClick(function (d) {
        if (!d) return;
        var iso3 = getIso3(d);
        if (!iso3) return;
        navigateToCountry(iso3);
      });

    // Controls setup
    var controls = myGlobe.controls();
    controls.autoRotate = isAutoRotating;
    controls.autoRotateSpeed = 0.55;
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Interaction stops auto-rotation
    controls.addEventListener('start', function () {
      if (isAutoRotating) {
        isAutoRotating = false;
        controls.autoRotate = false;
        updateRotateButtonState();
      }
    });

    // Center camera with gentle framing of South Asia / Indian Ocean
    myGlobe.pointOfView({ lat: 20.0, lng: 77.0, altitude: 2.1 }, 1000);

    // Renderer optimization
    var renderer = myGlobe.renderer();
    if (renderer) {
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    }

    // Responsive resize listener
    window.addEventListener('resize', function () {
      if (!myGlobe || !globeContainer) return;
      myGlobe.width(globeContainer.clientWidth);
      myGlobe.height(globeContainer.clientHeight);
    });
  }

  function initMetricSelector() {
    if (!metricSelect) return;
    metricSelect.addEventListener('change', function () {
      currentMetric = metricSelect.value;
      if (myGlobe) {
        myGlobe.polygonCapColor(function (d) {
          if (d === hoverD) return 'rgba(255, 255, 255, 0.9)';
          return getPolygonColor(d);
        });
      }
      updateLegend();
    });
  }

  function updateLegend() {
    if (!legendContainer) return;
    var cfg = METRIC_CONFIGS[currentMetric] || METRIC_CONFIGS.pm25;

    var gradientCss = '';
    if (currentMetric === 'pm25') {
      gradientCss = 'linear-gradient(to right, #10B981, #FBBF24, #F97316, #EF4444)';
    } else if (currentMetric === 'temp_anomaly') {
      gradientCss = 'linear-gradient(to right, #3B82F6, #94A3B8, #F59E0B, #EF4444)';
    } else if (currentMetric === 'co2_per_capita') {
      gradientCss = 'linear-gradient(to right, #10B981, #FBBF24, #F97316, #9333EA)';
    } else if (currentMetric === 'total_co2') {
      gradientCss = 'linear-gradient(to right, #34D399, #F59E0B, #EF4444)';
    } else if (currentMetric === 'renewable_elec_share') {
      gradientCss = 'linear-gradient(to right, #475569, #0D9488, #10B981)';
    } else if (currentMetric === 'forest_share') {
      gradientCss = 'linear-gradient(to right, #E2E8F0, #4ADE80, #15803D)';
    } else if (currentMetric === 'forest_change') {
      gradientCss = 'linear-gradient(to right, #EF4444, #94A3B8, #10B981)';
    }

    legendContainer.innerHTML = '<div style="font-family: var(--se-font-sans); font-size: 0.75rem; color: #CBD5E1; margin-bottom: 4px; font-weight: 600;">' +
      cfg.name + ' (' + cfg.unit + ')' +
      '</div>' +
      '<div style="height: 10px; width: 100%; border-radius: 4px; background: ' + gradientCss + '; margin-bottom: 4px;"></div>' +
      '<div style="display: flex; justify-content: space-between; font-family: monospace; font-size: 0.7rem; color: #94A3B8;">' +
      '<span>' + cfg.min + ' ' + cfg.unit + '</span>' +
      '<span>' + cfg.max + '+ ' + cfg.unit + '</span>' +
      '</div>' +
      '<div style="display: flex; align-items: center; gap: 6px; margin-top: 6px; font-size: 0.7rem; color: #94A3B8;">' +
      '<span style="display: inline-block; width: 10px; height: 10px; border-radius: 2px; background: rgba(71, 85, 105, 0.75); border: 1px solid rgba(255,255,255,0.2);"></span>' +
      '<span>Unranked / No data</span>' +
      '</div>';
  }

  function getIso3(feature) {
    if (!feature || !feature.properties) return '';
    var p = feature.properties;
    var iso = p.ISO_A3;
    if (!iso || iso === '-99') {
      iso = p.ADM0_A3 || p.SOV_A3 || '';
    }
    return (iso || '').toUpperCase();
  }

  function navigateToCountry(iso3) {
    var isoClean = iso3.toLowerCase();
    window.location.href = 'country/' + isoClean + '/';
  }

  function focusCountry(iso3) {
    var iso = iso3.toUpperCase();
    var meta = countriesIndex[iso];
    if (meta && meta.coordinates && meta.coordinates.length === 2) {
      if (myGlobe) {
        var controls = myGlobe.controls();
        if (controls) controls.autoRotate = false;
        isAutoRotating = false;
        updateRotateButtonState();
        myGlobe.pointOfView({
          lat: meta.coordinates[0],
          lng: meta.coordinates[1],
          altitude: 1.65
        }, 1200);
      }
    }
  }

  // Quick Select Country Search Filter
  function initSearch() {
    if (!searchInput || !searchResults) return;

    searchInput.addEventListener('input', function () {
      var q = searchInput.value.trim().toLowerCase();
      if (!q) {
        searchResults.style.display = 'none';
        searchResults.innerHTML = '';
        return;
      }

      var matches = allCountriesList.filter(function (c) {
        return c.name.toLowerCase().indexOf(q) !== -1 || c.iso3.toLowerCase().indexOf(q) !== -1;
      }).slice(0, 7);

      if (!matches.length) {
        searchResults.innerHTML = '<div style="padding: 0.6rem 0.85rem; font-size: 0.8rem; color: #94A3B8;">No sovereign nation found</div>';
        searchResults.style.display = 'block';
        return;
      }

      var html = matches.map(function (c) {
        return '<div class="globe-search-item" data-iso="' + c.iso3 + '" style="padding: 0.55rem 0.85rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.06);">' +
          '<span style="font-weight: 600; color: #F8FAFC; font-size: 0.85rem;">' + c.name + '</span>' +
          '<span style="font-family: monospace; font-size: 0.72rem; color: #1FB6A6;">[' + c.iso3 + ']</span>' +
          '</div>';
      }).join('');

      searchResults.innerHTML = html;
      searchResults.style.display = 'block';

      var items = searchResults.querySelectorAll('.globe-search-item');
      items.forEach(function (el) {
        el.addEventListener('click', function () {
          var targetIso = el.getAttribute('data-iso');
          searchInput.value = '';
          searchResults.style.display = 'none';
          focusCountry(targetIso);
        });
      });
    });

    document.addEventListener('click', function (e) {
      if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.style.display = 'none';
      }
    });
  }

  // Quick Select Country Pills
  function initPills() {
    if (!pillsContainer) return;
    var pillBtns = pillsContainer.querySelectorAll('.globe-pill');
    pillBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var iso = btn.getAttribute('data-iso');
        pillBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        focusCountry(iso);
      });
    });
  }

  // Camera and Auto-Rotation controls
  function initControls() {
    if (rotateToggleBtn) {
      rotateToggleBtn.addEventListener('click', function () {
        if (!myGlobe) return;
        var controls = myGlobe.controls();
        if (!controls) return;
        isAutoRotating = !isAutoRotating;
        controls.autoRotate = isAutoRotating;
        updateRotateButtonState();
      });
    }

    if (resetViewBtn) {
      resetViewBtn.addEventListener('click', function () {
        if (!myGlobe) return;
        myGlobe.pointOfView({ lat: 20.0, lng: 77.0, altitude: 2.1 }, 1000);
      });
    }
  }

  function updateRotateButtonState() {
    if (!rotateToggleBtn) return;
    var icon = rotateToggleBtn.querySelector('.rotate-icon');
    var text = rotateToggleBtn.querySelector('.rotate-text');
    if (isAutoRotating) {
      if (icon) icon.textContent = '⏸';
      if (text) text.textContent = 'Pause Orbit';
    } else {
      if (icon) icon.textContent = '▶';
      if (text) text.textContent = 'Resume Orbit';
    }
  }

  // Accessible Keyboard Directory Populator
  function populateAccessibleIndex(countries) {
    var tbody = document.getElementById('accessible-countries-tbody');
    if (!tbody) return;

    var sorted = countries.slice().sort(function (a, b) {
      return a.name.localeCompare(b.name);
    });

    var rowsHtml = sorted.map(function (c) {
      var ind = c.indicators || {};
      var pmObj = ind.pm25 || {};
      var co2Obj = ind.co2_per_capita || ind.total_co2 || {};
      var pmRank = pmObj.rank ? '#' + pmObj.rank : 'Unranked';
      var co2Rank = co2Obj.rank ? '#' + co2Obj.rank : 'Unranked';

      return '<tr style="border-bottom: 1px solid var(--se-border);">' +
        '<td style="padding: 0.65rem 0.5rem; font-weight: 600;"><a href="country/' + c.iso3.toLowerCase() + '/" style="color: inherit; text-decoration: underline;">' + c.name + '</a></td>' +
        '<td style="padding: 0.65rem 0.5rem; font-family: monospace; font-size: 0.85rem;">' + c.iso3 + '</td>' +
        '<td style="padding: 0.65rem 0.5rem; color: var(--se-text-secondary);">' + c.region + '</td>' +
        '<td style="padding: 0.65rem 0.5rem; font-family: monospace; font-size: 0.85rem;">' + pmRank + '</td>' +
        '<td style="padding: 0.65rem 0.5rem; font-family: monospace; font-size: 0.85rem;">' + co2Rank + '</td>' +
        '<td style="padding: 0.65rem 0.5rem; text-align: right;"><a href="country/' + c.iso3.toLowerCase() + '/" class="se-link" style="font-weight: 600;">View dossier &rarr;</a></td>' +
        '</tr>';
    }).join('');

    tbody.innerHTML = rowsHtml;
  }

})();
