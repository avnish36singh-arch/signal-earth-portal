/**
 * Signal Earth - Modern Interactive Homepage Engine
 * Aceternity-inspired Carousel with 3D parallax tilt & environmental modal
 * Aceternity-inspired Container Scroll 3D Animation (HeroScrollDemo)
 * Interactive Bento Grid, Research Spotlight, and Observation Stream
 */

(function () {
  'use strict';

  // =========================================================================
  // 1. Environmental Slide Dataset (Open Source Aceternity Dataset & Science)
  // =========================================================================
  var SLIDE_DATA = [
    {
      title: "Mystic Mountains",
      button: "Explore Component",
      src: "https://images.unsplash.com/photo-1494806812796-244fe51b774d?q=80&w=3534&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      category: "Orographic Trap · Cryosphere",
      coords: "30.15°N · 78.40°E · Himalayan Front",
      elevation: "3,800m - 8,848m AMSL",
      satellite: "NASA Terra MODIS & Sentinel-2",
      metricName: "AOD Contrast",
      metricVal: "1.45 vs 0.12",
      resolution: "250m Visible / SWIR",
      dek: "Steep topography physically trapping post-monsoon aerosols within northern India.",
      description: "The southern Himalayan mountain front acts as a monumental physical barrier to continental atmospheric transport. As cold, dense winter air settles into the Indo-Gangetic depression, thermal inversions trap regional emissions, preventing vertical convective dissipation and concentrating aerosols along the foothills.",
      linkUrl: "explained/temperature-inversion.html",
      linkText: "Read Inversion Physics Brief →"
    },
    {
      title: "Urban Dreams",
      button: "Explore Component",
      src: "https://images.unsplash.com/photo-1518710843675-2540dd79065c?q=80&w=3387&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      category: "Land Surface Temperature · Radiometry",
      coords: "26.45°N · 80.33°E · Urban Core",
      elevation: "126m AMSL",
      satellite: "USGS Landsat 8/9 TIRS-2 (Band 10)",
      metricName: "Urban Delta",
      metricVal: "+3.60K Delta",
      resolution: "30m Resampled Thermal",
      dek: "High-resolution satellite radiometry exposing extreme intra-urban microclimates.",
      description: "Intra-urban thermal infrared zoning derived from Landsat 8/9 TIRS-2 exposes hyper-localized heat islands across dense industrial and commercial precincts. Impervious concrete infrastructure warms disproportionately, while riparian vegetation along river corridors provides up to 2.15K of localized cooling buffer.",
      linkUrl: "investigations/kanpur-uhi.html",
      linkText: "Read 30m Landsat UHI Investigation →"
    },
    {
      title: "Neon Nights",
      button: "Explore Component",
      src: "https://images.unsplash.com/photo-1590041794748-2d8eb73a571c?q=80&w=3456&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      category: "Nocturnal Radiance · Megacity Emissions",
      coords: "28.61°N · 77.21°E · National Capital Region",
      elevation: "216m AMSL",
      satellite: "ISS Orbital Radiance & VIIRS DNB",
      metricName: "PM Dominance",
      metricVal: "95.3% NAQI",
      resolution: "500m Day-Night Band",
      dek: "Spaceborne night radiance tracing megacity boundaries and statutory NAQI mechanics.",
      description: "Orbital night radiance reveals the continuous nocturnal footprint of the National Capital Region. Regulatory telemetry audits across the airshed demonstrate that particulate components (PM2.5 and PM10) govern statutory NAQI scores on over 95% of monitored days, frequently masking secondary criteria gases.",
      linkUrl: "investigations/delhi.html",
      linkText: "Read Delhi Criteria Dominance Investigation →"
    },
    {
      title: "Desert Whispers",
      button: "Explore Component",
      src: "https://images.unsplash.com/photo-1679420437432-80cfbf88986c?q=80&w=3540&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      category: "Atmospheric Stagnation & Hiatus Audit",
      coords: "26.45°N · 80.33°E · Central Basin",
      elevation: "126m AMSL",
      satellite: "CPCB CAAQMS & NASA Aqua MODIS",
      metricName: "Winter Multiplier",
      metricVal: "4.2× PM2.5",
      resolution: "Continuous Hourly Telemetry",
      dek: "Multi-year particulate evaluations and explicit disclosure of an 855-day station hiatus.",
      description: "Continuous PM2.5 evaluations across multi-year regulatory windows document extreme seasonal ratios, with winter particulates averaging 4.2 times higher than baseline monsoon months. The dataset explicitly discloses an unmonitored 855-day station hiatus with zero synthetic infilling or black-box tampering.",
      linkUrl: "investigations/kanpur.html",
      linkText: "Read Kanpur Multiplier Investigation →"
    }
  ];

  // =========================================================================
  // 2. Aceternity-style 3D Carousel Engine
  // =========================================================================
  function initCarousel() {
    var slides = document.querySelectorAll('.se-carousel-slide');
    var dots = document.querySelectorAll('.se-carousel-dot');
    var prevBtn = document.getElementById('carousel-prev');
    var nextBtn = document.getElementById('carousel-next');
    var counterEl = document.getElementById('carousel-counter');
    var currentIndex = 0;
    var totalSlides = slides.length;
    var autoPlayTimer = null;

    if (!slides.length) return;

    function updateCarousel(newIndex) {
      currentIndex = (newIndex + totalSlides) % totalSlides;

      slides.forEach(function (slide, idx) {
        slide.classList.remove('active', 'prev', 'next', 'hidden-far');

        if (idx === currentIndex) {
          slide.classList.add('active');
        } else if (idx === (currentIndex - 1 + totalSlides) % totalSlides) {
          slide.classList.add('prev');
        } else if (idx === (currentIndex + 1) % totalSlides) {
          slide.classList.add('next');
        } else {
          slide.classList.add('hidden-far');
        }
      });

      dots.forEach(function (dot, idx) {
        if (idx === currentIndex) {
          dot.classList.add('active');
        } else {
          dot.classList.remove('active');
        }
      });

      if (counterEl) {
        var formattedCurr = (currentIndex + 1 < 10 ? '0' : '') + (currentIndex + 1);
        var formattedTotal = (totalSlides < 10 ? '0' : '') + totalSlides;
        counterEl.textContent = formattedCurr + ' / ' + formattedTotal;
      }
    }

    if (prevBtn) {
      prevBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        updateCarousel(currentIndex - 1);
        resetAutoPlay();
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        updateCarousel(currentIndex + 1);
        resetAutoPlay();
      });
    }

    dots.forEach(function (dot) {
      dot.addEventListener('click', function (e) {
        e.stopPropagation();
        var targetIdx = parseInt(dot.getAttribute('data-index'), 10);
        if (!isNaN(targetIdx)) {
          updateCarousel(targetIdx);
          resetAutoPlay();
        }
      });
    });

    // Keyboard navigation
    window.addEventListener('keydown', function (e) {
      if (document.querySelector('.se-env-modal-backdrop.is-open')) return;
      if (e.key === 'ArrowLeft') {
        updateCarousel(currentIndex - 1);
        resetAutoPlay();
      } else if (e.key === 'ArrowRight') {
        updateCarousel(currentIndex + 1);
        resetAutoPlay();
      }
    });

    // Touch swipe support
    var touchStartX = 0;
    var touchEndX = 0;
    var track = document.getElementById('se-carousel-track');
    if (track) {
      track.addEventListener('touchstart', function (e) {
        touchStartX = e.changedTouches[0].screenX;
      }, { passive: true });

      track.addEventListener('touchend', function (e) {
        touchEndX = e.changedTouches[0].screenX;
        var diff = touchStartX - touchEndX;
        if (Math.abs(diff) > 45) {
          if (diff > 0) {
            updateCarousel(currentIndex + 1);
          } else {
            updateCarousel(currentIndex - 1);
          }
          resetAutoPlay();
        }
      }, { passive: true });
    }

    // 3D Parallax Tilt Effect on Active Slide
    slides.forEach(function (slide, idx) {
      slide.addEventListener('mousemove', function (e) {
        if (!slide.classList.contains('active')) return;
        var rect = slide.getBoundingClientRect();
        var x = e.clientX - rect.left;
        var y = e.clientY - rect.top;
        var centerX = rect.width / 2;
        var centerY = rect.height / 2;
        var rotateX = ((centerY - y) / centerY) * 9;
        var rotateY = ((x - centerX) / centerX) * 9;

        slide.style.transform = 'perspective(1000px) rotateX(' + rotateX.toFixed(2) + 'deg) rotateY(' + rotateY.toFixed(2) + 'deg) scale3d(1.02, 1.02, 1.02)';
      });

      slide.addEventListener('mouseleave', function () {
        if (!slide.classList.contains('active')) return;
        slide.style.transform = '';
      });

      // Clicking slide or explore button triggers the Environmental Information Modal
      slide.addEventListener('click', function (e) {
        if (!slide.classList.contains('active')) {
          updateCarousel(idx);
          resetAutoPlay();
          return;
        }
        openEnvModal(idx);
      });
    });

    // Auto-play timer
    function startAutoPlay() {
      autoPlayTimer = setInterval(function () {
        updateCarousel(currentIndex + 1);
      }, 7000);
    }

    function resetAutoPlay() {
      if (autoPlayTimer) clearInterval(autoPlayTimer);
      startAutoPlay();
    }

    var carouselSection = document.getElementById('se-hero-carousel');
    if (carouselSection) {
      carouselSection.addEventListener('mouseenter', function () {
        if (autoPlayTimer) clearInterval(autoPlayTimer);
      });
      carouselSection.addEventListener('mouseleave', function () {
        resetAutoPlay();
      });
    }

    updateCarousel(0);
    startAutoPlay();
  }

  // =========================================================================
  // 3. Environmental Detail Modal System
  // =========================================================================
  function initEnvModal() {
    var modalBackdrop = document.getElementById('se-env-modal-backdrop');
    var closeBtn = document.getElementById('se-env-modal-close');

    if (!modalBackdrop) return;

    function closeModal() {
      modalBackdrop.classList.remove('is-open');
      document.body.style.overflow = '';
    }

    if (closeBtn) {
      closeBtn.addEventListener('click', closeModal);
    }

    modalBackdrop.addEventListener('click', function (e) {
      if (e.target === modalBackdrop) {
        closeModal();
      }
    });

    window.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && modalBackdrop.classList.contains('is-open')) {
        closeModal();
      }
    });
  }

  function openEnvModal(index) {
    var data = SLIDE_DATA[index];
    if (!data) return;

    var modalBackdrop = document.getElementById('se-env-modal-backdrop');
    var imgEl = document.getElementById('modal-img');
    var titleEl = document.getElementById('modal-title');
    var categoryEl = document.getElementById('modal-category');
    var coordsEl = document.getElementById('modal-coords');
    var satelliteEl = document.getElementById('modal-satellite');
    var metricValEl = document.getElementById('modal-metric-val');
    var metricLblEl = document.getElementById('modal-metric-lbl');
    var resolutionEl = document.getElementById('modal-resolution');
    var elevationEl = document.getElementById('modal-elevation');
    var descEl = document.getElementById('modal-desc');
    var actionBtn = document.getElementById('modal-action-btn');

    if (imgEl) imgEl.src = data.src;
    if (titleEl) titleEl.textContent = data.title;
    if (categoryEl) categoryEl.textContent = data.category;
    if (coordsEl) coordsEl.textContent = data.coords;
    if (satelliteEl) satelliteEl.textContent = data.satellite;
    if (metricValEl) metricValEl.textContent = data.metricVal;
    if (metricLblEl) metricLblEl.textContent = data.metricName;
    if (resolutionEl) resolutionEl.textContent = data.resolution;
    if (elevationEl) elevationEl.textContent = data.elevation;
    if (descEl) descEl.textContent = data.description;
    if (actionBtn) {
      actionBtn.href = data.linkUrl;
      actionBtn.textContent = data.linkText;
    }

    if (modalBackdrop) {
      modalBackdrop.classList.add('is-open');
      document.body.style.overflow = 'hidden';
    }
  }

  // =========================================================================
  // 4. Aceternity-style Container Scroll Animation (HeroScrollDemo)
  // =========================================================================
  function initContainerScroll() {
    var section = document.getElementById('se-container-scroll-section');
    var card = document.getElementById('se-container-scroll-card');
    if (!section || !card) return;

    var ticking = false;

    function onScroll() {
      if (!ticking) {
        window.requestAnimationFrame(function () {
          var rect = section.getBoundingClientRect();
          var windowHeight = window.innerHeight;

          // Compute scroll progress through the section (0 to 1)
          var progress = (windowHeight - rect.top) / (windowHeight + rect.height * 0.6);
          progress = Math.min(Math.max(progress, 0), 1);

          // Easing: quadratic ease out for smooth settling
          var easeProgress = 1 - Math.pow(1 - progress, 2);

          // Aceternity 3D formula: starts tilted at 22deg, scales from 0.90 to 1.0, flattens to 0deg
          var rotateX = (22 * (1 - easeProgress)).toFixed(2);
          var scale = (0.90 + 0.10 * easeProgress).toFixed(3);
          var translateY = (35 * (1 - easeProgress)).toFixed(1);

          card.style.transform = 'perspective(1200px) rotateX(' + rotateX + 'deg) scale(' + scale + ') translateY(' + translateY + 'px)';

          ticking = false;
        });
        ticking = true;
      }
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    onScroll();

    // Terminal Screen Interactive Tab Switcher
    var tabs = document.querySelectorAll('.se-terminal-tab');
    var imgLayer = document.getElementById('se-terminal-img');
    var chipSensor = document.getElementById('terminal-hud-sensor');
    var chipCoords = document.getElementById('terminal-hud-coords');
    var statVal1 = document.getElementById('terminal-stat-1');
    var statVal2 = document.getElementById('terminal-stat-2');

    var FEEDS = {
      thermal: {
        src: "assets/kanpur-uhi/kanpur-uhi-30m.png",
        sensor: "Landsat 8/9 TIRS-2 · 30m Infrared",
        coords: "26.45°N · 80.33°E · Kanpur Urban Core",
        s1: "+3.60K",
        s2: "100% Infill-Free"
      },
      plume: {
        src: "assets/hero_indo_gangetic_smoke_20211105.jpg",
        sensor: "NASA Terra MODIS · 250m L1B Radiance",
        coords: "28.30°N · 77.10°E · Ganga Basin",
        s1: "1.45 AOD",
        s2: "Boundary Trapped"
      },
      delhi: {
        src: "assets/delhi_iss_night.jpg",
        sensor: "ISS Spaceborne Radiance · Megacity NCR",
        coords: "28.61°N · 77.21°E · Delhi Airshed",
        s1: "95.3% PM",
        s2: "731-Day Hiatus"
      },
      arctic: {
        src: "assets/nasa_arctic_sea_ice.jpg",
        sensor: "Polar Cryosphere · Albedo Fracture",
        coords: "78.22°N · 15.65°E · Polar Margins",
        s1: "-18.4°C",
        s2: "Margin Fracture"
      }
    };

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        tabs.forEach(function (t) { t.classList.remove('active'); });
        tab.classList.add('active');

        var feedKey = tab.getAttribute('data-feed');
        var feed = FEEDS[feedKey];
        if (feed && imgLayer) {
          imgLayer.style.opacity = '0.3';
          setTimeout(function () {
            imgLayer.src = feed.src;
            imgLayer.style.opacity = '1';
          }, 150);

          if (chipSensor) chipSensor.textContent = feed.sensor;
          if (chipCoords) chipCoords.textContent = feed.coords;
          if (statVal1) statVal1.textContent = feed.s1;
          if (statVal2) statVal2.textContent = feed.s2;
        }
      });
    });

    // Real-time hover coordinates tracking on the screen
    var screen = document.getElementById('se-terminal-screen');
    if (screen && chipCoords) {
      screen.addEventListener('mousemove', function (e) {
        var rect = screen.getBoundingClientRect();
        var xPct = (e.clientX - rect.left) / rect.width;
        var yPct = (e.clientY - rect.top) / rect.height;

        // Compute simulated localized lat/lon jitter for authentic telemetry feel
        var baseLat = 26.45 + (1 - yPct) * 0.18;
        var baseLon = 80.33 + xPct * 0.22;
        chipCoords.textContent = baseLat.toFixed(3) + '°N · ' + baseLon.toFixed(3) + '°E · Grid Lock';
      });
    }
  }

  // =========================================================================
  // 5. Research Spotlight Tab Switcher
  // =========================================================================
  function initResearchTabs() {
    var tabBtns = document.querySelectorAll('.se-res-tab-btn');
    var panes = document.querySelectorAll('.se-research-pane');

    tabBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var targetId = btn.getAttribute('data-target');

        tabBtns.forEach(function (b) { b.classList.remove('active'); });
        panes.forEach(function (p) { p.classList.remove('active'); });

        btn.classList.add('active');
        var targetPane = document.getElementById(targetId);
        if (targetPane) {
          targetPane.classList.add('active');
        }
      });
    });
  }

  // =========================================================================
  // 6. Interactive Python Code Copy Button
  // =========================================================================
  function initCopyCode() {
    var copyBtn = document.getElementById('se-copy-code-btn');
    var codeEl = document.getElementById('se-python-code');

    if (copyBtn && codeEl) {
      copyBtn.addEventListener('click', function () {
        var text = codeEl.innerText || codeEl.textContent;
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () {
            copyBtn.textContent = 'Copied ✓';
            setTimeout(function () {
              copyBtn.textContent = 'Copy Code';
            }, 2000);
          }).catch(function () {
            copyBtn.textContent = 'Copied ✓';
          });
        }
      });
    }
  }

  // =========================================================================
  // DOM Ready Initializer
  // =========================================================================
  document.addEventListener('DOMContentLoaded', function () {
    initCarousel();
    initEnvModal();
    initContainerScroll();
    initResearchTabs();
    initCopyCode();
  });

})();
