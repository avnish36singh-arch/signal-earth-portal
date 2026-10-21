/**
 * Signal Earth : Interactive 3D Planetary Country Globe (assets/globe-country.js)
 * Full-viewport WebGL 3D Earth visualization tracking 48 canonical countries.
 * Colourblind-safe sequential scale (Cividis), Top 10 panel with Highest/Lowest toggle,
 * type-ahead search with aliases and diacritic support, and flat 2D fallback map.
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
  var legendContainer = document.getElementById('globe-legend');
  var top10Tbody = document.getElementById('top10-tbody');
  var top10HighestBtn = document.getElementById('top10-highest-btn');
  var top10LowestBtn = document.getElementById('top10-lowest-btn');
  var top10MultiyearFlag = document.getElementById('top10-multiyear-flag');

  if (!globeContainer) return;

  var myGlobe = null;
  var countriesIndex = {};
  var allCountriesList = [];
  var isAutoRotating = true;
  var hoverD = null;
  var currentMetric = 'epi_score';
  var top10Order = 'highest'; // 'highest' or 'lowest'

  // Country aliases for instant search
  var COUNTRY_ALIASES = {
    'USA': ['united states', 'united states of america', 'us', 'america'],
    'GBR': ['united kingdom', 'uk', 'britain', 'great britain', 'england'],
    'ARE': ['united arab emirates', 'uae', 'dubai', 'abu dhabi'],
    'KOR': ['south korea', 'korea', 'republic of korea'],
    'RUS': ['russia', 'russian federation'],
    'COD': ['dr congo', 'democratic republic of the congo', 'drc', 'congo kinshasa'],
    'COG': ['congo', 'republic of the congo', 'congo brazzaville'],
    'CIV': ['cote divoire', 'ivory coast', 'cote d\'ivoire'],
    'AND': ['andorra'],
    'IND': ['india', 'bharat', 'hindustan']
  };

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

  // Colourblind-safe Cividis gradient: #00204d -> #414d6b -> #7c7b78 -> #c3ac50 -> #ffea46
  // Neutral fill for missing data: #2A2F3D
  var NEUTRAL_FILL = '#2A2F3D';

  var CIVIDIS_STOPS = [
    { pos: 0.00, r: 0,   g: 32,  b: 77 },   // #00204d
    { pos: 0.25, r: 65,  g: 77,  b: 107 },  // #414d6b
    { pos: 0.50, r: 124, g: 123, b: 120 },  // #7c7b78
    { pos: 0.75, r: 195, g: 172, b: 80 },   // #c3ac50
    { pos: 1.00, r: 255, g: 234, b: 70 }    // #ffea46
  ];

  function getCividisColor(t) {
    t = Math.max(0, Math.min(1, t));
    for (var i = 0; i < CIVIDIS_STOPS.length - 1; i++) {
      var s1 = CIVIDIS_STOPS[i];
      var s2 = CIVIDIS_STOPS[i + 1];
      if (t >= s1.pos && t <= s2.pos) {
        var localT = (t - s1.pos) / (s2.pos - s1.pos);
        var r = Math.round(s1.r + localT * (s2.r - s1.r));
        var g = Math.round(s1.g + localT * (s2.g - s1.g));
        var b = Math.round(s1.b + localT * (s2.b - s1.b));
        return 'rgb(' + r + ',' + g + ',' + b + ')';
      }
    }
    return 'rgb(255,234,70)';
  }

  var METRIC_CONFIGS = {
    epi_score: {
      name: 'Yale EPI 2026 Score',
      unit: 'Score (0-100)',
      min: 20,
      max: 75,
      source: 'Yale CIESIN (2026)',
      license: 'CC BY-NC-SA 4.0',
      direction: 'highest_best',
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        var t = (v - 20) / (75 - 20);
        return getCividisColor(t);
      }
    },
    pm25: {
      name: 'Annual Mean PM2.5',
      unit: 'µg/m³',
      min: 5,
      max: 60,
      source: 'World Bank / State of Global Air (2023)',
      license: 'CC BY 4.0',
      direction: 'highest_worst',
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        var t = (v - 5) / (60 - 5);
        return getCividisColor(t);
      }
    },
    co2_total: {
      name: 'Total Territorial Fossil CO2',
      unit: 'Mt CO2/yr',
      min: 1,
      max: 5000,
      source: 'Global Carbon Project (2024)',
      license: 'CC BY 4.0',
      direction: 'highest_worst',
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        var logV = Math.log10(Math.max(1, v));
        var t = logV / 3.7; // log10(5000) ~ 3.7
        return getCividisColor(t);
      }
    },
    co2_per_capita: {
      name: 'Per Capita Fossil CO2',
      unit: 't CO2/person/yr',
      min: 0.2,
      max: 16,
      source: 'Global Carbon Project & UN Population (2024)',
      license: 'CC BY 4.0',
      direction: 'highest_worst',
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        var t = (v - 0.2) / (16 - 0.2);
        return getCividisColor(t);
      }
    },
    renewables_share: {
      name: 'Renewable Electricity Share',
      unit: '% of generation',
      min: 0,
      max: 100,
      source: 'Ember Climate (2024-2025)',
      license: 'CC BY 4.0',
      direction: 'highest_best',
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        var t = v / 100;
        return getCividisColor(t);
      }
    },
    forest_share: {
      name: 'Forest Cover Fraction',
      unit: '% of land area',
      min: 0,
      max: 75,
      source: 'Food and Agriculture Organization (FAO / World Bank 2024)',
      license: 'CC BY 4.0',
      direction: 'highest_best',
      interpolate: function (v) {
        if (v === null || v === undefined) return null;
        var t = v / 75;
        return getCividisColor(t);
      }
    }
  };

  function isWebGLAvailable() {
    try {
      var canvas = document.createElement('canvas');
      return !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
    } catch (e) {
      return false;
    }
  }

  // Load countries index and boundaries
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

    if (isWebGLAvailable()) {
      initGlobe(geoData);
    } else {
      initFlatFallback(geoData);
    }

    initMetricSelector();
    initSearch();
    initTop10Panel();
    initControls();
    updateLegend();
    renderTop10Panel();

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
    console.error('Failed to load planetary data:', err);
    if (globeSkeleton) {
      globeSkeleton.innerHTML = '<div style="color: #A1A1AA; font-family: var(--se-font-mono); font-size: 0.85rem; padding: 2rem; text-align: center;">' +
        'Unable to load planetary data. You can browse all country records on the <a href="countries/index.html" style="color: #FFFFFF; text-decoration: underline;">All Countries Directory</a>.' +
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
    var cfg = METRIC_CONFIGS[currentMetric] || METRIC_CONFIGS.epi_score;

    if (!metricObj || metricObj.value === null || metricObj.value === undefined) {
      return NEUTRAL_FILL;
    }

    var baseColor = cfg.interpolate(metricObj.value);
    if (!baseColor) return NEUTRAL_FILL;

    if (baseColor.indexOf('rgb') === 0) {
      return baseColor.replace('rgb', 'rgba').replace(')', ', 0.88)');
    }
    return baseColor;
  }

  function initGlobe(geoData) {
    if (typeof Globe === 'undefined') {
      setTimeout(function () { initGlobe(geoData); }, 150);
      return;
    }

    var width = globeContainer.clientWidth || window.innerWidth || 800;
    var height = globeContainer.clientHeight || (window.innerHeight - 54) || 600;

    myGlobe = Globe()
      (globeContainer)
      .globeImageUrl(getRelPath('assets/earth-blue-marble.jpg'))
      .backgroundColor('#000000')
      .showAtmosphere(true)
      .atmosphereColor('#88B0D3')
      .atmosphereAltitude(0.12)
      .width(width)
      .height(height)
      .polygonsData(geoData.features)
      .polygonAltitude(function (d) {
        return d === hoverD ? 0.045 : 0.007;
      })
      .polygonCapColor(function (d) {
        if (d === hoverD) {
          return 'rgba(255, 255, 255, 0.98)';
        }
        return getPolygonColor(d);
      })
      .polygonSideColor(function () {
        return 'rgba(255, 255, 255, 0.12)';
      })
      .polygonStrokeColor(function (d) {
        if (d === hoverD) {
          return '#FFFFFF';
        }
        return 'rgba(255, 255, 255, 0.28)';
      })
      .polygonLabel(function (d) {
        var iso3 = getIso3(d);
        var countryMeta = countriesIndex[iso3];
        var name = (countryMeta && countryMeta.name) || (d.properties && d.properties.NAME) || iso3;
        var region = (countryMeta && countryMeta.region) || (d.properties && d.properties.REGION_UN) || 'Global';

        var metricObj = getCountryMetric(iso3, currentMetric);
        var cfg = METRIC_CONFIGS[currentMetric] || METRIC_CONFIGS.epi_score;

        var metricLine = '';
        if (metricObj && metricObj.value !== null && metricObj.value !== undefined) {
          var valStr = metricObj.formatted || (metricObj.value + ' ' + (metricObj.unit || ''));
          var yrStr = metricObj.year ? ' (' + metricObj.year + ')' : '';
          var rkStr = metricObj.rank ? ' · Rank #' + metricObj.rank + (metricObj.total_ranked ? ' of ' + metricObj.total_ranked : '') : '';
          metricLine = '<div style="font-family: monospace; font-size: 0.88rem; font-weight: 700; color: #FFFFFF; margin-top: 0.35rem;">' +
            cfg.name + ': ' + valStr + yrStr +
            '</div>' +
            '<div style="font-size: 0.72rem; color: #A1A1AA; margin-top: 2px;">' + rkStr + '</div>';
        } else {
          metricLine = '<div style="font-family: monospace; font-size: 0.8rem; color: #71717A; margin-top: 0.35rem; font-style: italic;">' +
            cfg.name + ': No data / Unranked' +
            '</div>';
        }

        return '<div style="background: rgba(10, 10, 10, 0.95); border: 1px solid #333333; border-radius: 3px; padding: 0.75rem 1rem; color: #FFFFFF; max-width: 290px; box-shadow: 0 10px 25px rgba(0,0,0,0.85); pointer-events: none;">' +
          '<div style="font-family: Georgia, serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; line-height: 1.2;">' + name + ' <span style="font-family: monospace; font-size: 0.75rem; color: #A1A1AA; font-weight: normal;">[' + iso3 + ']</span></div>' +
          '<div style="font-size: 0.75rem; color: #A1A1AA; margin-top: 2px;">' + region + '</div>' +
          metricLine +
          '<div style="font-size: 0.72rem; color: #5EC962; margin-top: 0.5rem; font-weight: 600;">Click to view country profile &rarr;</div>' +
          '</div>';
      })
      .onPolygonHover(function (d) {
        hoverD = d;
        globeContainer.style.cursor = d ? 'pointer' : 'grab';
        myGlobe
          .polygonAltitude(function (p) { return p === hoverD ? 0.045 : 0.007; })
          .polygonCapColor(function (p) {
            if (p === hoverD) return 'rgba(255, 255, 255, 0.98)';
            return getPolygonColor(p);
          })
          .polygonStrokeColor(function (p) {
            if (p === hoverD) return '#FFFFFF';
            return 'rgba(255, 255, 255, 0.28)';
          });
      })
      .onPolygonClick(function (d) {
        if (!d) return;
        var iso3 = getIso3(d);
        if (!iso3) return;
        navigateToCountry(iso3);
      });

    var controls = myGlobe.controls();
    controls.autoRotate = isAutoRotating;
    controls.autoRotateSpeed = 0.55;
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    controls.addEventListener('start', function () {
      if (isAutoRotating) {
        isAutoRotating = false;
        controls.autoRotate = false;
        updateRotateButtonState();
      }
    });

    // Center camera on Indian Ocean / South Asia
    myGlobe.pointOfView({ lat: 20.0, lng: 77.0, altitude: 2.1 }, 1000);

    var renderer = myGlobe.renderer();
    if (renderer) {
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    }

    setTimeout(function () {
      if (myGlobe && globeContainer) {
        var w = globeContainer.clientWidth || window.innerWidth;
        var h = globeContainer.clientHeight || (window.innerHeight - 54);
        myGlobe.width(w).height(h);
      }
    }, 250);

    window.addEventListener('resize', function () {
      if (!myGlobe || !globeContainer) return;
      myGlobe.width(globeContainer.clientWidth || window.innerWidth);
      myGlobe.height(globeContainer.clientHeight || (window.innerHeight - 54));
    });
  }

  // 2D Flat Fallback Map for low-power or non-WebGL devices
  function initFlatFallback(geoData) {
    var w = globeContainer.clientWidth || window.innerWidth || 900;
    var h = globeContainer.clientHeight || (window.innerHeight - 54) || 600;

    var svgHtml = '<svg viewBox="0 0 960 500" style="width: 100%; height: 100%; background: #07090E; display: block;" xmlns="http://www.w3.org/2000/svg">';
    
    geoData.features.forEach(function (f) {
      var iso3 = getIso3(f);
      var col = getPolygonColor(f);
      var pathD = featureToSvgPath(f);
      if (pathD) {
        svgHtml += '<path d="' + pathD + '" fill="' + col + '" stroke="#333842" stroke-width="0.5" class="flat-country" data-iso="' + iso3 + '" style="cursor: pointer; transition: opacity 0.15s ease;">' +
          '<title>' + ((f.properties && f.properties.NAME) || iso3) + '</title>' +
          '</path>';
      }
    });

    svgHtml += '</svg>';
    globeContainer.innerHTML = svgHtml;

    var paths = globeContainer.querySelectorAll('.flat-country');
    paths.forEach(function (p) {
      p.addEventListener('click', function () {
        var iso = p.getAttribute('data-iso');
        if (iso) navigateToCountry(iso);
      });
      p.addEventListener('mouseenter', function () {
        p.setAttribute('stroke', '#FFFFFF');
        p.setAttribute('stroke-width', '1.2');
      });
      p.addEventListener('mouseleave', function () {
        p.setAttribute('stroke', '#333842');
        p.setAttribute('stroke-width', '0.5');
      });
    });
  }

  function featureToSvgPath(f) {
    if (!f.geometry || !f.geometry.coordinates) return '';
    var type = f.geometry.type;
    var coords = f.geometry.coordinates;

    function project(pt) {
      var lon = pt[0], lat = pt[1];
      var x = ((lon + 180) / 360) * 960;
      var y = ((90 - lat) / 180) * 500;
      return x.toFixed(1) + ',' + y.toFixed(1);
    }

    function ringToPath(ring) {
      if (!ring || ring.length < 3) return '';
      var d = 'M' + project(ring[0]);
      for (var i = 1; i < ring.length; i++) {
        d += 'L' + project(ring[i]);
      }
      return d + 'Z';
    }

    if (type === 'Polygon') {
      return coords.map(ringToPath).join(' ');
    } else if (type === 'MultiPolygon') {
      return coords.map(function (poly) {
        return poly.map(ringToPath).join(' ');
      }).join(' ');
    }
    return '';
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
      renderTop10Panel();
    });
  }

  function initTop10Panel() {
    if (top10HighestBtn) {
      top10HighestBtn.addEventListener('click', function () {
        top10Order = 'highest';
        top10HighestBtn.classList.add('active');
        if (top10LowestBtn) top10LowestBtn.classList.remove('active');
        renderTop10Panel();
      });
    }
    if (top10LowestBtn) {
      top10LowestBtn.addEventListener('click', function () {
        top10Order = 'lowest';
        top10LowestBtn.classList.add('active');
        if (top10HighestBtn) top10HighestBtn.classList.remove('active');
        renderTop10Panel();
      });
    }
  }

  function renderTop10Panel() {
    if (!top10Tbody) return;

    var validCountries = allCountriesList.filter(function (c) {
      var ind = c.indicators && c.indicators[currentMetric];
      return ind && ind.value !== null && ind.value !== undefined;
    });

    validCountries.sort(function (a, b) {
      var va = a.indicators[currentMetric].value;
      var vb = b.indicators[currentMetric].value;
      return top10Order === 'highest' ? (vb - va) : (va - vb);
    });

    var top10 = validCountries.slice(0, 10);
    var years = [];

    var rowsHtml = top10.map(function (c, idx) {
      var ind = c.indicators[currentMetric];
      var yr = ind.year || '2024';
      years.push(yr);
      var displayRank = ind.rank ? ('#' + ind.rank) : ('#' + (idx + 1));
      var formattedVal = ind.formatted || (ind.value + ' ' + (ind.unit || ''));

      return '<tr>' +
        '<td style="font-family: monospace; font-size: 0.72rem; color: #A1A1AA;">' + displayRank + '</td>' +
        '<td><a href="' + getRelPath('country/' + c.iso3.toLowerCase() + '/') + '">' + c.name + '</a></td>' +
        '<td style="font-family: monospace; font-size: 0.75rem; text-align: right; color: #FFFFFF;">' + formattedVal + '</td>' +
        '<td style="font-family: monospace; font-size: 0.72rem; text-align: right; color: #71717A;">' + yr + '</td>' +
        '</tr>';
    }).join('');

    top10Tbody.innerHTML = rowsHtml;

    // Multi-year anchor flag: check if observation years differ
    var uniqueYears = Array.from(new Set(years));
    if (top10MultiyearFlag) {
      if (uniqueYears.length > 1) {
        var sortedYrs = uniqueYears.slice().sort();
        top10MultiyearFlag.textContent = '* Multi-year anchor: observation years span ' + sortedYrs[0] + ' to ' + sortedYrs[sortedYrs.length - 1] + '.';
        top10MultiyearFlag.style.display = 'block';
      } else {
        top10MultiyearFlag.style.display = 'none';
      }
    }
  }

  function updateLegend() {
    if (!legendContainer) return;
    var cfg = METRIC_CONFIGS[currentMetric] || METRIC_CONFIGS.epi_score;

    var gradientCss = 'linear-gradient(to right, #00204d, #414d6b, #7c7b78, #c3ac50, #ffea46)';

    legendContainer.innerHTML = '<div style="font-family: var(--se-font-sans); font-size: 0.78rem; color: #FFFFFF; margin-bottom: 4px; font-weight: 600;">' +
      cfg.name + ' (' + cfg.unit + ')' +
      '</div>' +
      '<div style="height: 6px; width: 100%; border-radius: 2px; background: ' + gradientCss + '; margin-bottom: 5px; border: 1px solid rgba(255,255,255,0.15);"></div>' +
      '<div style="display: flex; justify-content: space-between; font-family: monospace; font-size: 0.7rem; color: #A1A1AA;">' +
      '<span>' + cfg.min + '</span>' +
      '<span>' + cfg.max + '+</span>' +
      '</div>' +
      '<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; font-size: 0.7rem; color: #71717A;">' +
      '<div style="display: flex; align-items: center; gap: 5px;">' +
      '<span style="display: inline-block; width: 8px; height: 8px; border-radius: 1px; background: ' + NEUTRAL_FILL + '; border: 1px solid rgba(255,255,255,0.25);"></span>' +
      '<span>No data / Neutral</span>' +
      '</div>' +
      '<div style="font-size: 0.68rem; color: #A1A1AA;">' + cfg.license + '</div>' +
      '</div>' +
      '<div style="font-size: 0.68rem; color: #71717A; margin-top: 4px; line-height: 1.3;">' +
      cfg.source +
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

  function normalizeText(s) {
    return (s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
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
          altitude: 1.55
        }, 1200);
      }
    }
  }

  function initSearch() {
    if (!searchInput || !searchResults) return;

    searchInput.addEventListener('input', function () {
      var q = normalizeText(searchInput.value);
      if (!q) {
        searchResults.style.display = 'none';
        searchResults.innerHTML = '';
        return;
      }

      var matches = allCountriesList.filter(function (c) {
        var nameNorm = normalizeText(c.name);
        var isoNorm = normalizeText(c.iso3);
        if (nameNorm.indexOf(q) !== -1 || isoNorm.indexOf(q) !== -1) return true;

        var aliases = COUNTRY_ALIASES[c.iso3.toUpperCase()] || [];
        for (var i = 0; i < aliases.length; i++) {
          if (normalizeText(aliases[i]).indexOf(q) !== -1) return true;
        }
        return false;
      }).slice(0, 7);

      if (!matches.length) {
        searchResults.innerHTML = '<div style="padding: 0.6rem 0.85rem; font-size: 0.8rem; color: #71717A;">No country found</div>';
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

})();
