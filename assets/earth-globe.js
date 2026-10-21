/**
 * Signal Earth - Planetary 3D Rotating Globe Widget
 * Pure Canvas orthographic projection with real land boundaries,
 * atmospheric corona, graticule rings, pulsing telemetry beacons,
 * interactive pointer drag, inertia, and location focus.
 */

(function () {
  'use strict';

  var canvas, ctx;
  var container;
  var hudLatLon, hudTarget, hudSensor, hudAction;
  var width = 420;
  var height = 420;
  var radius = 170;
  var cx = 210;
  var cy = 210;

  // Rotation parameters
  var lonRot = -75 * (Math.PI / 180); // Center near India initially
  var latTilt = 18 * (Math.PI / 180); // Modest northward axial tilt
  var rotSpeed = 0.0032;
  var isAutoRotating = true;
  var isDragging = false;
  var lastPointerX = 0;
  var lastPointerY = 0;
  var velX = 0;
  var velY = 0;
  var targetLon = null;
  var targetTilt = null;

  // Pulse animation phase
  var pulsePhase = 0;

  // Telemetry locations
  var LOCATIONS = [
    {
      id: 'kanpur',
      name: 'Kanpur, India',
      sub: 'Central Ganga Basin · Inversion Trap',
      lat: 26.4499,
      lon: 80.3319,
      elev: '126m AMSL',
      platform: 'Landsat 8/9 TIRS-2 · CPCB CAAQMS',
      status: '855-Day Hiatus Documented · +3.60K UHI',
      url: 'investigations/kanpur.html',
      briefUrl: 'briefs/kanpur-winter-ratio.html'
    },
    {
      id: 'delhi',
      name: 'Delhi NCR, India',
      sub: 'Indo-Gangetic Airshed · Regional Basin',
      lat: 28.6139,
      lon: 77.2090,
      elev: '216m AMSL',
      platform: 'DPCC CAAQMS · Terra MODIS Plumes',
      status: '95.3% PM Governing · 731-Day Hiatus',
      url: 'investigations/delhi.html',
      briefUrl: 'briefs/delhi-criteria-dominance.html'
    },
    {
      id: 'arctic',
      name: 'High Arctic Cryosphere',
      sub: 'Svalbard & Barents Sea · Polar Margins',
      lat: 78.2232,
      lon: 15.6469,
      elev: '0-450m AMSL',
      platform: 'Polar Orbit Earth Observation',
      status: 'Seasonal Pack Fracturing & Melt',
      url: 'research.html',
      briefUrl: 'research.html'
    },
    {
      id: 'himalayas',
      name: 'Himalayan Ridge',
      sub: 'Orographic Atmospheric Barrier',
      lat: 30.1500,
      lon: 78.4000,
      elev: '3,800m AMSL',
      platform: 'MODIS & Sentinel-5P TROPOMI',
      status: 'Aerosol Plume Entrapment Boundary',
      url: 'investigations/kanpur-lst.html',
      briefUrl: 'briefs/kanpur-landsat-thermal-snapshot.html'
    }
  ];

  var activeLocationIndex = 0;

  // Stars background
  var stars = [];
  function initStars() {
    stars = [];
    for (var i = 0; i < 48; i++) {
      stars.push({
        x: Math.random() * width,
        y: Math.random() * height,
        r: Math.random() * 1.2 + 0.4,
        alpha: Math.random() * 0.6 + 0.2,
        twinkle: Math.random() * 0.02 + 0.005
      });
    }
  }

  // Orthographic 3D projection
  // Returns [x, y, z] where z > 0 is facing viewer
  function project(lonDeg, latDeg) {
    var lon = lonDeg * (Math.PI / 180);
    var lat = latDeg * (Math.PI / 180);

    var theta = lon - lonRot;
    var phi = lat;

    // 3D coordinates on unit sphere
    var X = Math.cos(phi) * Math.sin(theta);
    var Y = Math.sin(phi);
    var Z = Math.cos(phi) * Math.cos(theta);

    // Apply latitude tilt (rotation around X axis)
    var cosT = Math.cos(latTilt);
    var sinT = Math.sin(latTilt);

    var yPrime = Y * cosT - Z * sinT;
    var zPrime = Y * sinT + Z * cosT;
    var xPrime = X;

    return {
      x: cx + xPrime * radius,
      y: cy - yPrime * radius,
      z: zPrime,
      xNorm: xPrime,
      yNorm: yPrime
    };
  }

  function resizeCanvas() {
    if (!canvas || !container) return;
    var rect = container.getBoundingClientRect();
    var containerWidth = rect.width;
    if (!containerWidth || containerWidth < 260) {
      containerWidth = container.offsetWidth || 380;
    }
    var size = Math.min(containerWidth, 440);
    if (size < 260) size = 320;

    var dpr = window.devicePixelRatio || 1;
    width = size;
    height = size;
    canvas.width = Math.round(size * dpr);
    canvas.height = Math.round(size * dpr);
    canvas.style.width = size + 'px';
    canvas.style.height = size + 'px';

    ctx = canvas.getContext('2d');
    if (ctx.setTransform) {
      ctx.setTransform(1, 0, 0, 1, 0, 0);
    }
    ctx.scale(dpr, dpr);

    cx = width / 2;
    cy = height / 2;
    radius = (size / 2) * 0.82;

    initStars();
  }

  // Draw atmosphere glow
  function drawAtmosphere() {
    // Outer corona glow
    var outerGlow = ctx.createRadialGradient(cx, cy, radius * 0.95, cx, cy, radius * 1.28);
    outerGlow.addColorStop(0, 'rgba(6, 182, 212, 0.22)');
    outerGlow.addColorStop(0.35, 'rgba(16, 185, 129, 0.12)');
    outerGlow.addColorStop(0.7, 'rgba(14, 165, 233, 0.04)');
    outerGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');

    ctx.fillStyle = outerGlow;
    ctx.beginPath();
    ctx.arc(cx, cy, radius * 1.28, 0, Math.PI * 2);
    ctx.fill();

    // Ocean base
    var oceanGrad = ctx.createRadialGradient(
      cx - radius * 0.32,
      cy - radius * 0.32,
      radius * 0.1,
      cx,
      cy,
      radius
    );
    oceanGrad.addColorStop(0, '#0f202e');
    oceanGrad.addColorStop(0.55, '#09131c');
    oceanGrad.addColorStop(0.9, '#04090e');
    oceanGrad.addColorStop(1, '#020508');

    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.clip();

    ctx.fillStyle = oceanGrad;
    ctx.fillRect(cx - radius, cy - radius, radius * 2, radius * 2);

    // Deep space stars within sphere reflection / subtle backdrop
    drawGrid();
    drawContinents();
    drawInnerRimGlow();

    ctx.restore();

    // Sharp outer rim stroke
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.25)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.stroke();
  }

  // Draw lat-long graticule grid
  function drawGrid() {
    ctx.save();
    ctx.lineWidth = 0.75;

    // Parallels
    var parallels = [-60, -30, 0, 30, 60];
    for (var p = 0; p < parallels.length; p++) {
      var lat = parallels[p];
      var isEquator = lat === 0;
      ctx.strokeStyle = isEquator ? 'rgba(56, 189, 248, 0.28)' : 'rgba(148, 163, 184, 0.1)';

      ctx.beginPath();
      var first = true;
      for (var lon = -180; lon <= 180; lon += 5) {
        var pt = project(lon, lat);
        if (pt.z > 0) {
          if (first) {
            ctx.moveTo(pt.x, pt.y);
            first = false;
          } else {
            ctx.lineTo(pt.x, pt.y);
          }
        } else {
          first = true;
        }
      }
      ctx.stroke();
    }

    // Meridians
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.09)';
    for (var m = -180; m < 180; m += 30) {
      ctx.beginPath();
      var firstM = true;
      for (var latM = -90; latM <= 90; latM += 4) {
        var ptM = project(m, latM);
        if (ptM.z > 0) {
          if (firstM) {
            ctx.moveTo(ptM.x, ptM.y);
            firstM = false;
          } else {
            ctx.lineTo(ptM.x, ptM.y);
          }
        } else {
          firstM = true;
        }
      }
      ctx.stroke();
    }
    ctx.restore();
  }

  // Draw world continent boundaries
  function drawContinents() {
    if (!window.WORLD_LAND || !window.WORLD_LAND.length) return;

    ctx.save();
    ctx.fillStyle = 'rgba(24, 46, 56, 0.85)';
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.55)';
    ctx.lineWidth = 0.85;

    var polys = window.WORLD_LAND;
    for (var i = 0; i < polys.length; i++) {
      var ring = polys[i];
      if (ring.length < 3) continue;

      ctx.beginPath();
      var drawing = false;

      for (var j = 0; j < ring.length; j++) {
        var p = ring[j];
        var pt = project(p[0], p[1]);

        if (pt.z > -0.1) {
          if (!drawing) {
            ctx.moveTo(pt.x, pt.y);
            drawing = true;
          } else {
            ctx.lineTo(pt.x, pt.y);
          }
        } else {
          drawing = false;
        }
      }

      ctx.fill();
      ctx.stroke();
    }

    ctx.restore();
  }

  // Inner rim glow (Fresnel effect)
  function drawInnerRimGlow() {
    var innerGlow = ctx.createRadialGradient(
      cx,
      cy,
      radius * 0.72,
      cx,
      cy,
      radius
    );
    innerGlow.addColorStop(0, 'rgba(6, 182, 212, 0)');
    innerGlow.addColorStop(0.7, 'rgba(6, 182, 212, 0.08)');
    innerGlow.addColorStop(0.95, 'rgba(56, 189, 248, 0.28)');
    innerGlow.addColorStop(1, 'rgba(16, 185, 129, 0.45)');

    ctx.fillStyle = innerGlow;
    ctx.fillRect(cx - radius, cy - radius, radius * 2, radius * 2);
  }

  // Draw stars background outside the globe
  function drawStars() {
    ctx.save();
    for (var i = 0; i < stars.length; i++) {
      var s = stars[i];
      s.alpha += Math.sin(pulsePhase * 3 + i) * s.twinkle;
      if (s.alpha < 0.1) s.alpha = 0.1;
      if (s.alpha > 0.8) s.alpha = 0.8;

      ctx.fillStyle = 'rgba(255, 255, 255, ' + s.alpha + ')';
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  // Draw telemetry markers and pulses
  function drawBeacons() {
    pulsePhase += 0.035;

    for (var i = 0; i < LOCATIONS.length; i++) {
      var loc = LOCATIONS[i];
      var pt = project(loc.lon, loc.lat);
      var isCurrentActive = i === activeLocationIndex;

      // Only draw if facing front hemisphere
      if (pt.z > 0.1) {
        var baseAlpha = Math.min(1, pt.z * 1.5);
        ctx.save();

        // Pulsing radio wave rings
        var pulseRadius = 5 + ((pulsePhase * 8) % 18);
        var ringAlpha = (1 - ((pulsePhase * 8) % 18) / 18) * 0.7 * baseAlpha;

        ctx.strokeStyle = isCurrentActive
          ? 'rgba(245, 158, 11, ' + ringAlpha + ')'
          : 'rgba(16, 185, 129, ' + ringAlpha + ')';
        ctx.lineWidth = isCurrentActive ? 1.6 : 1.2;
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, pulseRadius, 0, Math.PI * 2);
        ctx.stroke();

        // Center dot
        ctx.fillStyle = isCurrentActive
          ? '#F59E0B'
          : 'rgba(56, 189, 248, ' + baseAlpha + ')';
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, isCurrentActive ? 4.2 : 3, 0, Math.PI * 2);
        ctx.fill();

        // White core
        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, 1.5, 0, Math.PI * 2);
        ctx.fill();

        // Target pointer HUD line and label for active or hovered
        if (isCurrentActive) {
          ctx.strokeStyle = 'rgba(245, 158, 11, 0.85)';
          ctx.lineWidth = 1;

          var labelX = pt.x + 24;
          var labelY = pt.y - 18;

          ctx.beginPath();
          ctx.moveTo(pt.x, pt.y);
          ctx.lineTo(labelX - 4, labelY);
          ctx.lineTo(labelX + 80, labelY);
          ctx.stroke();

          // Badge background
          ctx.fillStyle = 'rgba(17, 24, 39, 0.9)';
          ctx.strokeStyle = 'rgba(245, 158, 11, 0.7)';
          ctx.lineWidth = 1;
          ctx.strokeRect(labelX - 2, labelY - 14, 86, 18);
          ctx.fillRect(labelX - 2, labelY - 14, 86, 18);

          // Badge text
          ctx.font = '600 9px "IBM Plex Mono", monospace';
          ctx.fillStyle = '#F59E0B';
          ctx.fillText(loc.id.toUpperCase(), labelX + 4, labelY - 2);
        }

        ctx.restore();
      }
    }
  }

  // Update HUD DOM elements
  function updateHud() {
    var loc = LOCATIONS[activeLocationIndex];
    if (!loc) return;

    if (hudLatLon) {
      hudLatLon.textContent =
        (loc.lat >= 0 ? loc.lat.toFixed(2) + '°N' : Math.abs(loc.lat).toFixed(2) + '°S') +
        ' · ' +
        (loc.lon >= 0 ? loc.lon.toFixed(2) + '°E' : Math.abs(loc.lon).toFixed(2) + '°W') +
        ' (' + loc.elev + ')';
    }

    if (hudTarget) {
      hudTarget.textContent = loc.name + '  -  ' + loc.sub;
    }

    if (hudSensor) {
      hudSensor.textContent = loc.platform + ' | ' + loc.status;
    }

    if (hudAction) {
      hudAction.href = loc.url;
      hudAction.textContent = 'Explore ' + loc.name.split(',')[0] + ' Investigation →';
    }
  }

  // Smooth camera interpolation towards selected location
  function updateTargetInterpolation() {
    if (targetLon !== null) {
      var dLon = targetLon - lonRot;
      // Shortest angle on circle
      while (dLon < -Math.PI) dLon += Math.PI * 2;
      while (dLon > Math.PI) dLon -= Math.PI * 2;

      lonRot += dLon * 0.08;
      if (Math.abs(dLon) < 0.002) {
        lonRot = targetLon;
        targetLon = null;
      }
    }

    if (targetTilt !== null) {
      var dTilt = targetTilt - latTilt;
      latTilt += dTilt * 0.08;
      if (Math.abs(dTilt) < 0.002) {
        latTilt = targetTilt;
        targetTilt = null;
      }
    }
  }

  // Main render loop
  function render() {
    ctx.clearRect(0, 0, width, height);

    drawStars();

    // Auto rotation or inertia
    if (isDragging) {
      lonRot += velX;
      latTilt -= velY;
      // Clamp latTilt to reasonable range [-45 deg, 45 deg]
      latTilt = Math.max(-0.78, Math.min(0.78, latTilt));
    } else if (targetLon !== null || targetTilt !== null) {
      updateTargetInterpolation();
    } else {
      if (Math.abs(velX) > 0.0001) {
        lonRot += velX;
        velX *= 0.94;
      } else if (isAutoRotating) {
        lonRot += rotSpeed;
      }

      if (Math.abs(velY) > 0.0001) {
        latTilt -= velY;
        latTilt = Math.max(-0.78, Math.min(0.78, latTilt));
        velY *= 0.94;
      }
    }

    // Keep lonRot in [-PI, PI] range
    while (lonRot < -Math.PI) lonRot += Math.PI * 2;
    while (lonRot > Math.PI) lonRot -= Math.PI * 2;

    drawAtmosphere();
    drawBeacons();

    requestAnimationFrame(render);
  }

  // Public method to focus a location
  function focusLocation(index) {
    if (index < 0 || index >= LOCATIONS.length) return;
    activeLocationIndex = index;
    var loc = LOCATIONS[index];

    // Target longitude faces center: lonRot should equal lon (radians)
    targetLon = loc.lon * (Math.PI / 180);
    // Target tilt aligns with latitude
    targetTilt = Math.max(-0.5, Math.min(0.5, loc.lat * (Math.PI / 180) * 0.6));

    // Update buttons
    var buttons = document.querySelectorAll('.se-globe-loc-btn');
    buttons.forEach(function (btn, i) {
      if (i === index) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    updateHud();
  }

  // Setup interactions
  function initEvents() {
    canvas.addEventListener('pointerdown', function (e) {
      isDragging = true;
      lastPointerX = e.clientX;
      lastPointerY = e.clientY;
      velX = 0;
      velY = 0;
      targetLon = null;
      targetTilt = null;
      canvas.setPointerCapture(e.pointerId);
    });

    canvas.addEventListener('pointermove', function (e) {
      if (!isDragging) return;
      var dx = e.clientX - lastPointerX;
      var dy = e.clientY - lastPointerY;
      lastPointerX = e.clientX;
      lastPointerY = e.clientY;

      velX = dx * 0.006;
      velY = dy * 0.006;
      lonRot += velX;
      latTilt -= velY;
      latTilt = Math.max(-0.78, Math.min(0.78, latTilt));
    });

    function endDrag(e) {
      if (isDragging) {
        isDragging = false;
        try {
          canvas.releasePointerCapture(e.pointerId);
        } catch (err) {}
      }
    }

    canvas.addEventListener('pointerup', endDrag);
    canvas.addEventListener('pointercancel', endDrag);

    // Location buttons
    var buttons = document.querySelectorAll('.se-globe-loc-btn');
    buttons.forEach(function (btn, i) {
      btn.addEventListener('click', function () {
        focusLocation(i);
      });
    });

    // Toggle rotation
    var toggleBtn = document.getElementById('globe-toggle-spin');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', function () {
        isAutoRotating = !isAutoRotating;
        toggleBtn.textContent = isAutoRotating ? 'Pause Spin' : 'Resume Spin';
        toggleBtn.setAttribute('aria-pressed', isAutoRotating ? 'true' : 'false');
      });
    }

    window.addEventListener('resize', resizeCanvas);
  }

  function init() {
    canvas = document.getElementById('earth-globe-canvas');
    if (!canvas) return;

    container = document.getElementById('earth-globe-container');
    hudLatLon = document.getElementById('globe-hud-latlon');
    hudTarget = document.getElementById('globe-hud-target');
    hudSensor = document.getElementById('globe-hud-sensor');
    hudAction = document.getElementById('globe-hud-action');

    resizeCanvas();
    initEvents();
    updateHud();
    requestAnimationFrame(render);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.SignalEarthGlobe = {
    focusLocation: focusLocation
  };
})();
