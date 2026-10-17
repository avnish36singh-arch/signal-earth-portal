/**
 * Signal Earth : Interactive 3D Planetary Country Globe (assets/globe-country.js)
 * Centerpiece 3D Earth visualization tracking global environmental metrics.
 * Built with Three.js (0.160.0) and Globe.gl (2.32.2).
 * Strictly zero em dashes throughout.
 */

(function () {
  'use strict';

  var globeContainer = document.getElementById('globe-container');
  var globeSkeleton = document.getElementById('globe-skeleton');
  var searchInput = document.getElementById('globe-country-search');
  var searchResults = document.getElementById('globe-search-results');
  var rotateToggleBtn = document.getElementById('globe-rotate-btn');
  var resetViewBtn = document.getElementById('globe-reset-btn');
  var pillsContainer = document.getElementById('globe-pills-bar');

  if (!globeContainer) return;

  var myGlobe = null;
  var countriesIndex = {};
  var allCountriesList = [];
  var isAutoRotating = true;
  var hoverD = null;

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
    initSearch();
    initPills();
    initControls();
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
        return d === hoverD ? 0.04 : 0.005;
      })
      .polygonCapColor(function (d) {
        var iso3 = getIso3(d);
        if (d === hoverD) {
          return 'rgba(31, 182, 166, 0.72)';
        }
        if (countriesIndex[iso3]) {
          return 'rgba(15, 23, 42, 0.42)';
        }
        return 'rgba(15, 23, 42, 0.3)';
      })
      .polygonSideColor(function () {
        return 'rgba(255, 255, 255, 0.08)';
      })
      .polygonStrokeColor(function (d) {
        if (d === hoverD) {
          return '#1FB6A6';
        }
        return 'rgba(255, 255, 255, 0.22)';
      })
      .polygonLabel(function (d) {
        var iso3 = getIso3(d);
        var countryMeta = countriesIndex[iso3];
        var name = (d.properties && d.properties.NAME) || iso3;
        var region = (countryMeta && countryMeta.region) || (d.properties && d.properties.REGION_UN) || 'Global';

        var ranksHtml = '';
        var actionText = 'Click to open country dossier &rarr;';

        if (countryMeta && countryMeta.ranks) {
          var r = countryMeta.ranks;
          var badges = [];
          if (r.pm25) badges.push('PM2.5 Rank #' + r.pm25);
          if (r.co2_total) badges.push('CO2 Rank #' + r.co2_total);
          if (r.temp_anomaly) badges.push('Temp Rank #' + r.temp_anomaly);
          if (badges.length > 0) {
            ranksHtml = '<div style="font-family: monospace; font-size: 0.75rem; color: #1FB6A6; margin-top: 0.25rem;">' + badges.join(' &middot; ') + '</div>';
          }
        }

        if (!countryMeta) {
          actionText = 'Click to view sovereign territory overview &rarr;';
        }

        return '<div style="background: rgba(10, 22, 40, 0.95); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.18); border-radius: 6px; padding: 0.65rem 0.9rem; color: #F8FAFC; max-width: 280px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); pointer-events: none;">' +
          '<div style="font-family: Georgia, serif; font-size: 1rem; font-weight: 700; color: #FFFFFF; line-height: 1.2;">' + name + ' <span style="font-family: monospace; font-size: 0.78rem; color: #94A3B8; font-weight: normal;">[' + iso3 + ']</span></div>' +
          '<div style="font-size: 0.78rem; color: #CBD5E1; margin-top: 2px;">' + region + '</div>' +
          ranksHtml +
          '<div style="font-size: 0.75rem; color: #5EEAD4; margin-top: 0.45rem; font-weight: 600;">' + actionText + '</div>' +
          '</div>';
      })
      .onPolygonHover(function (d) {
        hoverD = d;
        globeContainer.style.cursor = d ? 'pointer' : 'grab';
        myGlobe
          .polygonAltitude(function (polygon) { return polygon === hoverD ? 0.04 : 0.005; })
          .polygonCapColor(function (polygon) {
            var iso3 = getIso3(polygon);
            if (polygon === hoverD) return 'rgba(31, 182, 166, 0.72)';
            if (countriesIndex[iso3]) return 'rgba(15, 23, 42, 0.42)';
            return 'rgba(15, 23, 42, 0.3)';
          })
          .polygonStrokeColor(function (polygon) {
            if (polygon === hoverD) return '#1FB6A6';
            return 'rgba(255, 255, 255, 0.22)';
          });
      })
      .onPolygonClick(function (d) {
        if (!d) return;
        var iso3 = getIso3(d);
        if (!iso3) return;
        navigateToCountry(iso3);
      });

    // Beacon rings for primary stations (e.g. India)
    var ringsData = [
      { lat: 20.5937, lng: 78.9629, maxR: 4, propagationSpeed: 1.5, repeatPeriod: 1200, color: function () { return 'rgba(31, 182, 166, 0.8)'; } }
    ];
    myGlobe
      .ringsData(ringsData)
      .ringColor(function (d) { return d.color(); })
      .ringMaxRadius('maxR')
      .ringPropagationSpeed('propagationSpeed')
      .ringRepeatPeriod('repeatPeriod');

    // Controls setup
    var controls = myGlobe.controls();
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.55;
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Center camera with gentle framing of South Asia / Indian Ocean
    myGlobe.pointOfView({ lat: 22.0, lng: 78.0, altitude: 2.1 }, 1000);

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
    // Direct navigation to pre-built static country page
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
        myGlobe.pointOfView({ lat: 22.0, lng: 78.0, altitude: 2.1 }, 1000);
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
      var r = c.ranks || {};
      var pmRank = r.pm25 ? '#' + r.pm25 : 'Unranked';
      var co2Rank = r.co2_total ? '#' + r.co2_total : 'Unranked';
      var tempRank = r.temp_anomaly ? '#' + r.temp_anomaly : 'Unranked';

      return '<tr style="border-bottom: 1px solid var(--home-border);">' +
        '<td style="padding: 0.65rem 0.5rem; font-weight: 600;"><a href="country/' + c.iso3.toLowerCase() + '/" style="color: inherit; text-decoration: underline;">' + c.name + '</a></td>' +
        '<td style="padding: 0.65rem 0.5rem; font-family: monospace; font-size: 0.85rem;">' + c.iso3 + '</td>' +
        '<td style="padding: 0.65rem 0.5rem; color: var(--home-secondary);">' + c.region + '</td>' +
        '<td style="padding: 0.65rem 0.5rem; font-family: monospace; font-size: 0.85rem;">' + pmRank + '</td>' +
        '<td style="padding: 0.65rem 0.5rem; font-family: monospace; font-size: 0.85rem;">' + co2Rank + '</td>' +
        '<td style="padding: 0.65rem 0.5rem; text-align: right;"><a href="country/' + c.iso3.toLowerCase() + '/" class="se-link" style="font-weight: 600;">View dossier &rarr;</a></td>' +
        '</tr>';
    }).join('');

    tbody.innerHTML = rowsHtml;
  }

})();
