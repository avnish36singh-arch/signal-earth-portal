/**
 * Signal Earth : Interactive 3D Planetary Country Globe (assets/globe-country.js)
 * Full-viewport WebGL 3D Earth visualization tracking sovereign environmental metrics.
 * Built with Three.js (0.160.0) and Globe.gl (2.32.2).
 * Minimalist Monochrome (Black & White) Aesthetic.
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

  // Base path resolver for dual deployment (GitHub Pages subpath vs Netlify root vs localhost)
  function getRelPath(relPath) {
    var p = relPath.replace(/^\/+/, '');
    var isGhPages = window.location.pathname.indexOf('/signal-earth-portal') === 0;
    return (isGhPages ? '/signal-earth-portal/' : '/') + p;
  }

  // Check prefers-reduced-motion
  var prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReducedMotion) {
    isAutoRotating = false;
  }

  // Minimalist Monochrome Color Scale Configurations (Charcoal to Stark White)
  var METRIC_CONFIGS = {
    pm25: {
      name: 'Annual Mean PM2.5',
      unit: 'µg/m³',
      min: 5,
      max: 60,
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        if (v <= 5) return '#27272A';
        if (v <= 15) return interpolateHex('#27272A', '#71717A', (v - 5) / 10);
        if (v <= 35) return interpolateHex('#71717A', '#D4D4D8', (v - 15) / 20);
        return interpolateHex('#D4D4D8', '#FFFFFF', Math.min(1, (v - 35) / 25));
      }
    },
    temp_anomaly: {
      name: 'Temperature Anomaly',
      unit: '°C',
      min: -0.5,
      max: 2.5,
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        if (v <= 0.5) return interpolateHex('#3F3F46', '#71717A', (v + 0.5) / 1.0);
        if (v <= 1.5) return interpolateHex('#71717A', '#D4D4D8', (v - 0.5) / 1.0);
        return interpolateHex('#D4D4D8', '#FFFFFF', Math.min(1, (v - 1.5) / 1.0));
      }
    },
    co2_per_capita: {
      name: 'CO2 per Capita',
      unit: 't/person',
      min: 0.5,
      max: 18,
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        if (v <= 3) return interpolateHex('#27272A', '#71717A', v / 3);
        if (v <= 10) return interpolateHex('#71717A', '#D4D4D8', (v - 3) / 7);
        return interpolateHex('#D4D4D8', '#FFFFFF', Math.min(1, (v - 10) / 8));
      }
    },
    total_co2: {
      name: 'Total Territorial CO2',
      unit: 'Mt/yr',
      min: 10,
      max: 5000,
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        var logV = Math.log10(Math.max(1, v));
        var t = Math.min(1, Math.max(0, (logV - 1) / 3));
        return interpolateHex('#27272A', '#FFFFFF', t);
      }
    },
    renewable_elec_share: {
      name: 'Renewable Electricity Share',
      unit: '%',
      min: 0,
      max: 100,
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        return interpolateHex('#27272A', '#FFFFFF', v / 100);
      }
    },
    forest_share: {
      name: 'Forest Area Share',
      unit: '%',
      min: 0,
      max: 75,
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        return interpolateHex('#27272A', '#FFFFFF', v / 75);
      }
    },
    forest_change: {
      name: '10-Yr Forest Net Change',
      unit: '%',
      min: -15,
      max: 15,
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        if (v < 0) return interpolateHex('#3F3F46', '#71717A', Math.min(1, (v + 15) / 15));
        return interpolateHex('#71717A', '#FFFFFF', Math.min(1, v / 15));
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

  // Protocol check: file:// protocol restriction warning
  if (window.location.protocol === 'file:') {
    if (globeSkeleton) {
      globeSkeleton.innerHTML = '<div style="padding: 2.5rem; text-align: center; color: #CBD5E1; font-family: sans-serif; max-width: 580px; margin: 0 auto; background: #0A0A0A; border: 1px solid #222222; border-radius: 4px;">' +
        '<h2 style="color: #FFFFFF; font-size: 1.25rem; margin-top: 0; margin-bottom: 0.5rem; font-family: Georgia, serif;">Local Web Server Required for 3D Globe</h2>' +
        '<p style="font-size: 0.88rem; line-height: 1.6; color: #A1A1AA; margin-bottom: 1.25rem;">' +
        'You opened this page directly as a <code>file://</code> URL. Web browsers strictly restrict WebGL and GeoJSON data fetching when opened directly from the filesystem.' +
        '</p>' +
        '<div style="background: #000000; padding: 0.75rem 1rem; border-radius: 3px; font-family: monospace; font-size: 0.85rem; color: #FFFFFF; margin-bottom: 1.25rem; border: 1px solid #333333;">' +
        'python -m http.server 8000' +
        '</div>' +
        '<p style="font-size: 0.88rem; color: #CBD5E1; margin-bottom: 1.5rem;">' +
        'Then open <a href="http://localhost:8000/" style="color: #FFFFFF; font-weight: 700; text-decoration: underline;">http://localhost:8000/</a> in your browser, or visit <a href="https://signalearth.netlify.app/" style="color: #FFFFFF; font-weight: 700; text-decoration: underline;">https://signalearth.netlify.app/</a>.' +
        '</p>' +
        '<a href="#accessible-country-index" style="display: inline-block; background: #FFFFFF; color: #000000; padding: 0.5rem 1rem; border-radius: 2px; font-weight: 700; text-decoration: none; font-size: 0.82rem;">Browse Country Directory Below &darr;</a>' +
        '</div>';
    }
    return;
  }

  if (!isWebGLAvailable()) {
    if (globeSkeleton) {
      globeSkeleton.innerHTML = '<div style="padding: 2rem; text-align: center; color: #A1A1AA; font-family: var(--se-font-sans);">' +
        '<p style="font-size: 1.1rem; color: #FFFFFF; margin-bottom: 0.5rem;">WebGL acceleration is unavailable in your browser environment.</p>' +
        '<p style="font-size: 0.9rem; margin-bottom: 1.5rem;">You can explore all sovereign country profiles using the accessible directory table below.</p>' +
        '<a href="#accessible-country-index" style="display: inline-block; background: #FFFFFF; color: #000000; padding: 0.5rem 1rem; border-radius: 2px; font-weight: 600; text-decoration: none;">Browse Country Directory &darr;</a>' +
        '</div>';
    }
    return;
  }

  // Load countries index and boundary GeoJSON concurrently
  Promise.all([
    fetch(getRelPath('data/countries.json')).then(function (r) { return r.json(); }),
    fetch(getRelPath('data/world-110m.geojson')).then(function (r) { return r.json(); })
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
        if (globeSkeleton && globeSkeleton.parentNode) {
          globeSkeleton.parentNode.removeChild(globeSkeleton);
        }
      }, 300);
    }
  })
  .catch(function (err) {
    console.error('Failed to load globe data:', err);
    if (globeSkeleton) {
      globeSkeleton.innerHTML = '<div style="color: #A1A1AA; font-family: var(--se-font-mono); font-size: 0.85rem; padding: 2rem; text-align: center;">' +
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
      return 'rgba(24, 24, 27, 0.72)';
    }

    var baseColor = cfg.interpolate(metricObj.value);
    if (!baseColor) return 'rgba(24, 24, 27, 0.72)';

    if (baseColor.indexOf('rgb') === 0) {
      return baseColor.replace('rgb', 'rgba').replace(')', ', 0.82)');
    }
    return baseColor;
  }

  function initGlobe(geoData) {
    if (typeof Globe === 'undefined') {
      console.warn('Globe.gl not loaded yet, retrying in 150ms...');
      setTimeout(function () { initGlobe(geoData); }, 150);
      return;
    }

    var width = globeContainer.clientWidth || window.innerWidth || 800;
    var height = globeContainer.clientHeight || (window.innerHeight - 58) || 600;

    myGlobe = Globe()
      (globeContainer)
      .globeImageUrl(getRelPath('assets/earth-blue-marble.jpg'))
      .backgroundColor('#000000')
      .showAtmosphere(true)
      .atmosphereColor('#FFFFFF')
      .atmosphereAltitude(0.10)
      .width(width)
      .height(height)
      .polygonsData(geoData.features)
      .polygonAltitude(function (d) {
        return d === hoverD ? 0.045 : 0.006;
      })
      .polygonCapColor(function (d) {
        if (d === hoverD) {
          return 'rgba(255, 255, 255, 0.98)';
        }
        return getPolygonColor(d);
      })
      .polygonSideColor(function () {
        return 'rgba(255, 255, 255, 0.10)';
      })
      .polygonStrokeColor(function (d) {
        if (d === hoverD) {
          return '#FFFFFF';
        }
        return 'rgba(255, 255, 255, 0.22)';
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
          metricLine = '<div style="font-family: monospace; font-size: 0.85rem; font-weight: 700; color: #FFFFFF; margin-top: 0.35rem;">' +
            cfg.name + ': ' + valStr + yrStr +
            '</div>' +
            '<div style="font-size: 0.72rem; color: #A1A1AA; margin-top: 2px;">' + rkStr + '</div>';
        } else {
          metricLine = '<div style="font-family: monospace; font-size: 0.8rem; color: #71717A; margin-top: 0.35rem; font-style: italic;">' +
            cfg.name + ': No data / Unranked' +
            '</div>';
        }

        return '<div style="background: #0A0A0A; border: 1px solid #333333; border-radius: 3px; padding: 0.75rem 1rem; color: #FFFFFF; max-width: 290px; box-shadow: 0 10px 25px rgba(0,0,0,0.8); pointer-events: none;">' +
          '<div style="font-family: Georgia, serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; line-height: 1.2;">' + name + ' <span style="font-family: monospace; font-size: 0.75rem; color: #A1A1AA; font-weight: normal;">[' + iso3 + ']</span></div>' +
          '<div style="font-size: 0.75rem; color: #A1A1AA; margin-top: 2px;">' + region + '</div>' +
          metricLine +
          '<div style="font-size: 0.72rem; color: #D4D4D8; margin-top: 0.5rem; font-weight: 600;">Click to open sovereign dossier &rarr;</div>' +
          '</div>';
      })
      .onPolygonHover(function (d) {
        hoverD = d;
        globeContainer.style.cursor = d ? 'pointer' : 'grab';
        myGlobe
          .polygonAltitude(function (polygon) { return polygon === hoverD ? 0.045 : 0.006; })
          .polygonCapColor(function (polygon) {
            if (polygon === hoverD) return 'rgba(255, 255, 255, 0.98)';
            return getPolygonColor(polygon);
          })
          .polygonStrokeColor(function (polygon) {
            if (polygon === hoverD) return '#FFFFFF';
            return 'rgba(255, 255, 255, 0.22)';
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

    // Force dimension check shortly after mounting
    setTimeout(function () {
      if (myGlobe && globeContainer) {
        var w = globeContainer.clientWidth || window.innerWidth;
        var h = globeContainer.clientHeight || (window.innerHeight - 58);
        myGlobe.width(w).height(h);
      }
    }, 250);

    // Responsive resize listener
    window.addEventListener('resize', function () {
      if (!myGlobe || !globeContainer) return;
      myGlobe.width(globeContainer.clientWidth || window.innerWidth);
      myGlobe.height(globeContainer.clientHeight || (window.innerHeight - 58));
    });
  }

  function initMetricSelector() {
    if (!metricSelect) return;
    metricSelect.addEventListener('change', function () {
      currentMetric = metricSelect.value;
      if (myGlobe) {
        myGlobe.polygonCapColor(function (d) {
          if (d === hoverD) return 'rgba(255, 255, 255, 0.98)';
          return getPolygonColor(d);
        });
      }
      updateLegend();
    });
  }

  function updateLegend() {
    if (!legendContainer) return;
    var cfg = METRIC_CONFIGS[currentMetric] || METRIC_CONFIGS.pm25;

    var gradientCss = 'linear-gradient(to right, #27272A, #71717A, #D4D4D8, #FFFFFF)';

    legendContainer.innerHTML = '<div style="font-family: var(--se-font-sans); font-size: 0.75rem; color: #FFFFFF; margin-bottom: 5px; font-weight: 600;">' +
      cfg.name + ' (' + cfg.unit + ')' +
      '</div>' +
      '<div style="height: 6px; width: 100%; border-radius: 2px; background: ' + gradientCss + '; margin-bottom: 5px; border: 1px solid rgba(255,255,255,0.15);"></div>' +
      '<div style="display: flex; justify-content: space-between; font-family: monospace; font-size: 0.7rem; color: #A1A1AA;">' +
      '<span>' + cfg.min + ' ' + cfg.unit + '</span>' +
      '<span>' + cfg.max + '+ ' + cfg.unit + '</span>' +
      '</div>' +
      '<div style="display: flex; align-items: center; gap: 6px; margin-top: 8px; font-size: 0.7rem; color: #71717A;">' +
      '<span style="display: inline-block; width: 8px; height: 8px; border-radius: 1px; background: #18181B; border: 1px solid rgba(255,255,255,0.25);"></span>' +
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
    window.location.href = getRelPath('country/' + isoClean + '/');
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
        searchResults.innerHTML = '<div style="padding: 0.6rem 0.85rem; font-size: 0.8rem; color: #71717A;">No sovereign nation found</div>';
        searchResults.style.display = 'block';
        return;
      }

      var html = matches.map(function (c) {
        return '<div class="globe-search-item" data-iso="' + c.iso3 + '" style="padding: 0.55rem 0.85rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1F1F23;">' +
          '<span style="font-weight: 600; color: #FFFFFF; font-size: 0.85rem;">' + c.name + '</span>' +
          '<span style="font-family: monospace; font-size: 0.72rem; color: #A1A1AA;">[' + c.iso3 + ']</span>' +
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

      return '<tr>' +
        '<td style="padding: 0.75rem 0.5rem; font-weight: 600;"><a href="' + getRelPath('country/' + c.iso3.toLowerCase() + '/') + '" style="color: inherit; text-decoration: underline;">' + c.name + '</a></td>' +
        '<td style="padding: 0.75rem 0.5rem; font-family: monospace; font-size: 0.85rem;">' + c.iso3 + '</td>' +
        '<td style="padding: 0.75rem 0.5rem; color: var(--se-text-secondary);">' + c.region + '</td>' +
        '<td style="padding: 0.75rem 0.5rem; font-family: monospace; font-size: 0.85rem;">' + pmRank + '</td>' +
        '<td style="padding: 0.75rem 0.5rem; font-family: monospace; font-size: 0.85rem;">' + co2Rank + '</td>' +
        '<td style="padding: 0.75rem 0.5rem; text-align: right;"><a href="' + getRelPath('country/' + c.iso3.toLowerCase() + '/') + '" class="se-link" style="font-weight: 600;">View dossier &rarr;</a></td>' +
        '</tr>';
    }).join('');

    tbody.innerHTML = rowsHtml;
  }

})();
