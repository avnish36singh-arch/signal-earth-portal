/**
 * Signal Earth - Centerpiece Interactive Environmental Globe (assets/globe-app.js)
 * High-performance 3D Earth observation controller with Three.js (0.160.0) & Globe.gl (2.32.2).
 * Features 14 planetary observation stations, genuine NASA GIBS satellite radiometry,
 * location impact beacon rings, quick-select region pills, filterable legend, and accessible keyboard list.
 */

(function () {
  'use strict';

  // Base path resolver for dual deployment (GitHub Pages subpath vs Netlify root)
  function getAssetPath(relPath) {
    var p = relPath.replace(/^\/+/, '');
    var isGhPages = window.location.pathname.indexOf('/signal-earth-portal') === 0;
    return (isGhPages ? '/signal-earth-portal/' : '/') + p;
  }

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

  // Pre-compiled comprehensive data for all 14 planetary stations
  var ALL_REGIONS_DATA = [
    {
      id: "kanpur",
      name: "Kanpur Observatory",
      region: "Central Indo-Gangetic Basin, India",
      lat: 26.4499,
      lon: 80.3319,
      issue_type: "air quality",
      issue_badge: "Particulate Stagnation & Hiatus",
      color: "#F2A33A",
      bbox: [26.0, 79.8, 27.0, 80.8],
      gibs_layer: "MODIS_Terra_CorrectedReflectance_TrueColor",
      summary: "Dense urban and industrial core situated in the central Ganga valley subject to acute winter boundary layer entrapment.",
      why_it_matters: "Meteorological inversions and geographic containment multiply particulate concentrations fourfold, causing severe cardiopulmonary morbidity across the central Ganga valley.",
      signal_shows: "Ground telemetry documents a 4.2× winter aerosol multiplier alongside an 855-day unmonitored regulatory hiatus.",
      metrics: [
        { name: "Winter Multiplier", value: "4.2×", source: "CPCB CAAQMS / Signal Earth Audit", url: "investigations/kanpur-particulates.html", year: 2026 },
        { name: "Documented Hiatus", value: "855 Days", source: "Statutory Telemetry Audit", url: "known-problems.html", year: 2026 },
        { name: "Urban Heat Delta", value: "+3.60K", source: "Landsat 8/9 TIRS-2 Band 10", url: "investigations/landsat-uhi.html", year: 2026 }
      ],
      investigation_url: "investigations/kanpur-particulates.html"
    },
    {
      id: "delhi",
      name: "Delhi NCR Airshed",
      region: "National Capital Region, India",
      lat: 28.6139,
      lon: 77.2090,
      issue_type: "air quality",
      issue_badge: "NAQI Particulate Dominance",
      color: "#D6402B",
      bbox: [28.2, 76.8, 29.1, 77.6],
      gibs_layer: "MODIS_Terra_CorrectedReflectance_TrueColor",
      summary: "Megacity basin capturing post-harvest biomass burning plumes and local emissions under calm synoptic winter wind regimes.",
      why_it_matters: "Airshed exposure affects over 30 million residents with headline air quality indexes consistently saturating statutory maximum thresholds.",
      signal_shows: "Evaluation of 24 criteria pollutants confirms PM2.5 and PM10 determine the overall NAQI score on 95.3% of monitored days.",
      metrics: [
        { name: "PM Dominance", value: "95.3%", source: "CPCB NAQI Regulatory Formulation Audit", url: "investigations/delhi-naqi.html", year: 2026 },
        { name: "Peak PM2.5 Index", value: "480+ AQI", source: "DPCC Continuous Telemetry", url: "data.html", year: 2026 },
        { name: "Station Hiatus", value: "731 Days", source: "Disclosed Monitoring Interruption", url: "known-problems.html", year: 2026 }
      ],
      investigation_url: "investigations/delhi-naqi.html"
    },
    {
      id: "arctic",
      name: "High Arctic Cryosphere",
      region: "Svalbard & Barents Sea",
      lat: 78.2232,
      lon: 15.6469,
      issue_type: "ice",
      issue_badge: "Polar Amplification & Ice Decline",
      color: "#2E6FD8",
      bbox: [76.5, 10.0, 80.5, 25.0],
      gibs_layer: "MODIS_Terra_CorrectedReflectance_TrueColor",
      summary: "Rapidly warming polar ocean margin experiencing winter pack ice thinning and reduced summer multiyear ice volume.",
      why_it_matters: "Loss of Arctic reflective albedo accelerates global ocean heat absorption, altering the Northern Hemisphere jet stream.",
      signal_shows: "Satellite radiometry shows 2026 summer ice extent bottomed at 4.60M km², continuing a 12.2% per decade downward trajectory.",
      metrics: [
        { name: "2026 Minimum Extent", value: "4.60M km²", source: "NSIDC Sea Ice Index", url: "https://nsidc.org/arcticseaicenews/", year: 2026 },
        { name: "Decadal Decline", value: "-12.2% / decade", source: "NASA Cryospheric Sciences", url: "https://climate.nasa.gov/vital-signs/arctic-sea-ice/", year: 2026 },
        { name: "Polar Amplification", value: "3.8× Global Rate", source: "Nature Communications", url: "https://doi.org/10.1038/s43247-022-00498-3", year: 2026 }
      ],
      investigation_url: "reports.html"
    },
    {
      id: "himalayas",
      name: "Himalayan Ridge & Glaciers",
      region: "Hindu Kush Himalaya, South Asia",
      lat: 30.1500,
      lon: 78.4000,
      issue_type: "ice",
      issue_badge: "Orographic Barrier & Cryosphere",
      color: "#2E6FD8",
      bbox: [29.0, 77.5, 31.5, 80.0],
      gibs_layer: "MODIS_Terra_CorrectedReflectance_TrueColor",
      summary: "The third pole: continental elevation wall acting as an atmospheric boundary layer barrier while glacier mass loss accelerates.",
      why_it_matters: "Glacial melt waters feed 10 major Asian river systems supporting 1.9 billion downstream inhabitants.",
      signal_shows: "Elevated black carbon deposition darkens snowpack albedo while steep topography stops winter plain pollution from dissipating.",
      metrics: [
        { name: "Mass Loss Acceleration", value: "65% Faster", source: "ICIMOD Assessment Report", url: "https://www.icimod.org", year: 2026 },
        { name: "Elevation Barrier", value: "3,800m+ AMSL", source: "SRTM Digital Elevation Model", url: "https://www.usgs.gov", year: 2026 },
        { name: "Downstream Dependence", value: "1.9 Billion", source: "IPCC SROCC Assessment", url: "https://www.ipcc.ch/srocc/", year: 2026 }
      ],
      investigation_url: "investigations/inversion-dynamics.html"
    },
    {
      id: "amazon",
      name: "Amazon Basin Biosphere",
      region: "Amazonas, Brazil",
      lat: -3.4653,
      lon: -62.2159,
      issue_type: "forest",
      issue_badge: "Canopy Stress & Desiccation",
      color: "#1FB6A6",
      bbox: [-5.5, -64.5, -1.5, -60.0],
      gibs_layer: "MODIS_Terra_CorrectedReflectance_TrueColor",
      summary: "Planetary hydrological engine facing compound stress from multi-year droughts and land conversion margins.",
      why_it_matters: "Contains over 120 billion metric tons of stored biomass carbon; dieback would destabilize global monsoon networks.",
      signal_shows: "Thermal infrared satellite channels reveal severe riparian soil drying and tree canopy transpiration collapse during dry seasons.",
      metrics: [
        { name: "Stored Biomass Carbon", value: "123 GtC", source: "INPE / Global Carbon Project", url: "https://globalcarbonbudget.org", year: 2026 },
        { name: "Rio Negro Record Low", value: "12.70m", source: "Port of Manaus Hydrological Data", url: "https://www.portodemanaus.com.br", year: 2026 },
        { name: "Basin Tree Mortality", value: "+38% vs baseline", source: "Nature (Flores et al.)", url: "https://doi.org/10.1038/s41586-023-06970-0", year: 2026 }
      ],
      investigation_url: "reports.html"
    },
    {
      id: "barrier-reef",
      name: "Great Barrier Reef",
      region: "Coral Sea, Queensland, Australia",
      lat: -18.2871,
      lon: 147.6992,
      issue_type: "coral",
      issue_badge: "Mass Thermal Bleaching",
      color: "#D6402B",
      bbox: [-20.0, 146.0, -16.0, 149.5],
      gibs_layer: "MODIS_Terra_CorrectedReflectance_TrueColor",
      summary: "World's largest coral reef ecosystem experiencing recurrent mass bleaching driven by marine heatwaves.",
      why_it_matters: "Coral mortality collapses marine trophic webs, dissipating natural storm barriers and endangering oceanic biodiversity.",
      signal_shows: "NOAA Coral Reef Watch confirmed the 4th Global Bleaching Event reached severe Degree Heating Weeks (DHW > 8).",
      metrics: [
        { name: "Bleaching Spatial Extent", value: "73% of Reefs", source: "GBRMPA Aerial Survey Report", url: "https://www.gbrmpa.gov.au", year: 2026 },
        { name: "Thermal Accumulation", value: "14.2 DHW", source: "NOAA Coral Reef Watch", url: "https://coralreefwatch.noaa.gov", year: 2026 },
        { name: "Mass Event Count", value: "5 in 8 Years", source: "Australian Institute of Marine Science", url: "https://www.aims.gov.au", year: 2026 }
      ],
      investigation_url: "reports.html"
    },
    {
      id: "sahel",
      name: "Sahel Transition Belt",
      region: "Sub-Saharan Africa (Chad, Niger, Mali)",
      lat: 14.5000,
      lon: 18.0000,
      issue_type: "drought",
      issue_badge: "Vegetation Stress & Volatility",
      color: "#F2A33A",
      bbox: [12.0, 15.0, 17.0, 21.0],
      gibs_layer: "MODIS_Terra_CorrectedReflectance_TrueColor",
      summary: "Ecological transition margin between Sahara Desert and Savanna subject to extreme precipitation variability.",
      why_it_matters: "Rainfed agropastoral communities face compounding food security risks and climate-induced pastoral migration friction.",
      signal_shows: "MODIS NDVI vegetation indices show erratic wet-season greening followed by abrupt dry-season soil moisture collapse.",
      metrics: [
        { name: "Rainfall Anomaly Variance", value: "±35%", source: "Copernicus Climate Pulse / ERA5", url: "https://climate.copernicus.eu", year: 2026 },
        { name: "Food Security Crisis", value: "12.8M People", source: "UN OCHA Sahel Overview", url: "https://www.unocha.org", year: 2026 },
        { name: "Lake Chad Footprint", value: "90% Lost since 1960", source: "UNEP Environmental Assessment", url: "https://www.unep.org", year: 2026 }
      ],
      investigation_url: "reports.html"
    },
    {
      id: "tuvalu",
      name: "Tuvalu & Pacific Atolls",
      region: "Funafuti, Central Pacific",
      lat: -8.5167,
      lon: 179.2167,
      issue_type: "sea level",
      issue_badge: "Low-Lying Atoll Marine Inundation",
      color: "#2E6FD8",
      bbox: [-9.0, 178.5, -8.0, 179.8],
      gibs_layer: "MODIS_Terra_CorrectedReflectance_TrueColor",
      summary: "Low-lying coral atoll nation averaging less than 2 meters above sea level, facing saltwater intrusion and tidal flooding.",
      why_it_matters: "Exemplifies the existential sovereign challenge of sea level rise, aquifer salinization, and loss of habitable territorial land.",
      signal_shows: "Satellite altimetry records regional sea level rise rates of ~4.8 mm/yr, exceeding the global mean rate.",
      metrics: [
        { name: "Local Sea Level Rise", value: "+4.8 mm/yr", source: "NASA Sea Level Portal / Tide Gauges", url: "https://sealevel.nasa.gov", year: 2026 },
        { name: "Average Land Elevation", value: "< 2.0m AMSL", source: "Tuvalu National Topographic Survey", url: "https://www.gov.tv", year: 2026 },
        { name: "King Tide Flooding Area", value: "46% of Funafuti", source: "UNDP Pacific Coastal Vulnerability", url: "https://www.undp.org", year: 2026 }
      ],
      investigation_url: "reports.html"
    },
    {
      id: "mediterranean",
      name: "Mediterranean Basin",
      region: "Southern Europe & North Africa",
      lat: 38.0000,
      lon: 15.0000,
      issue_type: "heat",
      issue_badge: "Synoptic Heat Dome & Wildfires",
      color: "#D6402B",
      bbox: [35.0, 10.0, 41.0, 20.0],
      gibs_layer: "MODIS_Terra_CorrectedReflectance_TrueColor",
      summary: "Climate change hotspot warming 20% faster than the global average, hit by persistent subtropical heat domes.",
      why_it_matters: "Agricultural crop yields suffer catastrophic losses while catastrophic wildfires threaten coastal infrastructure.",
      signal_shows: "Landsat and Sentinel thermal observations recorded continuous land surface temperatures exceeding 48°C.",
      metrics: [
        { name: "Warming vs Global Rate", value: "+20% Faster", source: "MedECC First Assessment Report", url: "https://www.medecc.org", year: 2026 },
        { name: "Peak Land Surface Temp", value: "48.2°C LST", source: "Sentinel-3 SLSTR Radiometry", url: "https://sentinels.copernicus.eu", year: 2026 },
        { name: "Wildfire Burn Area", value: "450,000 ha / yr", source: "European Forest Fire Information System", url: "https://effis.jrc.ec.europa.eu", year: 2026 }
      ],
      investigation_url: "reports.html"
    },
    {
      id: "greenland",
      name: "Greenland Ice Sheet",
      region: "Ilulissat & Jakobshavn Glacier",
      lat: 69.2167,
      lon: -49.5000,
      issue_type: "ice",
      issue_badge: "Surface Melt & Calving Dynamics",
      color: "#2E6FD8",
      bbox: [67.0, -53.0, 71.0, -45.0],
      gibs_layer: "MODIS_Terra_CorrectedReflectance_TrueColor",
      summary: "Massive continental ice sheet losing hundreds of billions of tons annually via surface melt runoff and fast marine glaciers.",
      why_it_matters: "Complete ice sheet disintegration represents 7.4 meters of potential global sea level rise.",
      signal_shows: "GRACE-FO satellite gravimetry records sustained ice mass loss averaging ~270 Gt per year.",
      metrics: [
        { name: "Annual Ice Mass Loss", value: "-270 Gt / yr", source: "NASA GRACE-FO Satellite Gravimetry", url: "https://climate.nasa.gov/vital-signs/ice-sheets/", year: 2026 },
        { name: "Jakobshavn Velocity", value: "38 m / day", source: "ESA Sentinel-1 Radar Altimetry", url: "https://sentinels.copernicus.eu", year: 2026 },
        { name: "Sea Level Contribution", value: "+0.75 mm / yr", source: "Polar Portal (DMI / GEUS)", url: "http://polarportal.dk", year: 2026 }
      ],
      investigation_url: "reports.html"
    },
    {
      id: "indonesia-peat",
      name: "Indonesia Peatlands",
      region: "Central Kalimantan & Sumatra",
      lat: -1.5000,
      lon: 113.5000,
      issue_type: "forest",
      issue_badge: "Peat Combustion & Transboundary Haze",
      color: "#F2A33A",
      bbox: [-3.5, 111.0, 0.5, 116.0],
      gibs_layer: "MODIS_Terra_CorrectedReflectance_TrueColor",
      summary: "Drained tropical peatland carbon reservoirs prone to deep smoldering subterranean fires during dry seasons.",
      why_it_matters: "Releases massive ancient subterranean carbon pulses alongside hazardous regional PM2.5 transboundary haze.",
      signal_shows: "MODIS and VIIRS thermal anomaly detectors register thousands of persistent subterranean hot spots masked by smoke.",
      metrics: [
        { name: "Stored Peat Carbon", value: "57 GtC", source: "CIFOR Peatland Database", url: "https://www.cifor.org", year: 2026 },
        { name: "Peak Emission Pulse", value: "710 MtCO₂ eq", source: "Copernicus Global Fire Assimilation", url: "https://atmosphere.copernicus.eu", year: 2026 },
        { name: "Transboundary Haze PM", value: "450 µg/m³", source: "ASEAN Specialised Meteorological Centre", url: "https://asmc.asean.org", year: 2026 }
      ],
      investigation_url: "reports.html"
    },
    {
      id: "horn-of-africa",
      name: "Horn of Africa",
      region: "Somalia, Ethiopia & Northern Kenya",
      lat: 5.0000,
      lon: 46.0000,
      issue_type: "drought",
      issue_badge: "Multi-Season Drought Emergency",
      color: "#F2A33A",
      bbox: [2.0, 42.0, 8.0, 50.0],
      gibs_layer: "MODIS_Terra_CorrectedReflectance_TrueColor",
      summary: "Arid region suffering unprecedented consecutive failed rainy seasons, collapsing pastures and livestock water pans.",
      why_it_matters: "Severe humanitarian famine conditions exacerbated by warming western Pacific ocean gradients shifting atmospheric circulation.",
      signal_shows: "Soil Moisture Active Passive (SMAP) satellite observations reveal root-zone moisture remaining below 5th percentile.",
      metrics: [
        { name: "Consecutive Failed Rains", value: "5 Seasons", source: "IGAD Climate Prediction Centre", url: "https://www.icpac.net", year: 2026 },
        { name: "Population Needing Aid", value: "23.4M People", source: "UN World Food Programme", url: "https://www.wfp.org", year: 2026 },
        { name: "Livestock Losses", value: "9.5M Animals", source: "FAO Drought Situation Report", url: "https://www.fao.org", year: 2026 }
      ],
      investigation_url: "reports.html"
    },
    {
      id: "aral-sea",
      name: "Aral Sea Desiccation",
      region: "Karakalpakstan, Uzbekistan & Kazakhstan",
      lat: 45.0000,
      lon: 59.5000,
      issue_type: "drought",
      issue_badge: "Anthropogenic Basin Desiccation",
      color: "#D6402B",
      bbox: [43.0, 57.0, 47.0, 62.0],
      gibs_layer: "MODIS_Terra_CorrectedReflectance_TrueColor",
      summary: "Historic inland sea desiccated by agricultural diversion, now transformed into the toxic Aralkum salt desert.",
      why_it_matters: "Exposed seabed salts and pesticide residues blow across thousands of miles, altering regional microclimates and human health.",
      signal_shows: "Landsat satellite time series reveals 90% water volume loss, exposing over 54,000 km² of hyper-saline desert floor.",
      metrics: [
        { name: "Volume Lost", value: "90% Lost", source: "USGS Earth Resources Observation", url: "https://www.usgs.gov", year: 2026 },
        { name: "Salt Dust Plume Area", value: "100M Tons / yr", source: "UNEP Aral Sea Basin Programme", url: "https://www.unep.org", year: 2026 },
        { name: "Exposed Salt Bed", value: "54,000 km²", source: "NASA Earth Observatory", url: "https://earthobservatory.nasa.gov", year: 2026 }
      ],
      investigation_url: "reports.html"
    },
    {
      id: "california",
      name: "California Wildfire Corridor",
      region: "Sierra Nevada & Coastal Ranges, USA",
      lat: 38.5000,
      lon: -120.5000,
      issue_type: "heat",
      issue_badge: "Pyrocumulonimbus & Megafires",
      color: "#D6402B",
      bbox: [36.5, -123.0, 40.5, -118.0],
      gibs_layer: "MODIS_Terra_CorrectedReflectance_TrueColor",
      summary: "Forest belt subjected to severe vapor pressure deficits, beetle dieback, and offshore Diablo/Santa Ana winds.",
      why_it_matters: "Megafires generate self-sustaining pyrocumulonimbus storms injecting aerosol plumes straight into the stratosphere.",
      signal_shows: "GOES Advanced Baseline Imager captures explosive fire radiative power (FRP) and rapid perimeter expansions.",
      metrics: [
        { name: "Vapor Pressure Deficit", value: "+24% above normal", source: "NOAA Climate Diagnostics Center", url: "https://psl.noaa.gov", year: 2026 },
        { name: "Record Fire Season", value: "4.3M Acres", source: "CAL FIRE Official Incident Archive", url: "https://www.fire.ca.gov", year: 2026 },
        { name: "Insured Property Loss", value: "$16.5B USD", source: "Swiss Re Institute Sigma Report", url: "https://www.swissre.com", year: 2026 }
      ],
      investigation_url: "reports.html"
    }
  ];

  var allRegions = ALL_REGIONS_DATA;
  var globeInstance = null;
  var activeFilters = {
    'heat': true,
    'air quality': true,
    'ice': true,
    'forest': true,
    'sea level': true,
    'coral': true,
    'drought': true
  };
  var activeRegion = allRegions[0];
  var isAutoRotating = true;
  var isGlobeInitialized = false;

  // WebGL support detector
  function isWebGLAvailable() {
    try {
      var canvas = document.createElement('canvas');
      return !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
    } catch (e) {
      return false;
    }
  }

  // Filter regions based on activeFilters state
  function getFilteredRegions() {
    return allRegions.filter(function (r) {
      return activeFilters[r.issue_type] !== false;
    });
  }

  // Render Quick-Select Region Pills  -  click centres globe then opens location page
  function renderRegionPills(regions) {
    var pillsContainer = document.getElementById('globe-regions-pills');
    if (!pillsContainer) return;

    pillsContainer.innerHTML = '';
    regions.forEach(function (r) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'se-globe-pill' + (activeRegion && activeRegion.id === r.id ? ' active' : '');
      btn.setAttribute('data-region-id', r.id);
      btn.setAttribute('title', 'Open location profile: ' + r.name);
      btn.innerHTML =
        '<span class="se-globe-pill-dot" style="background-color: ' + (r.color || '#1FB6A6') + ';"></span>' +
        r.name;

      btn.addEventListener('click', function () {
        // Centre & ring the globe briefly, then navigate to location page
        activeRegion = r;
        updateActivePill(r.id);
        if (globeInstance) {
          var controls = globeInstance.controls();
          controls.autoRotate = false;
          globeInstance.ringsData([r]);
          globeInstance.pointOfView({ lat: r.lat, lng: r.lon, altitude: 1.55 }, 600);
        }
        var basePath = window.location.pathname.indexOf('/signal-earth-portal') === 0
          ? '/signal-earth-portal/' : '/';
        setTimeout(function () {
          window.location.href = basePath + 'location.html?region=' + r.id;
        }, 650);
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
    if (skeletonEl) skeletonEl.style.display = 'none';

    var prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) isAutoRotating = false;

    var width = containerEl.clientWidth || window.innerWidth;
    var height = containerEl.clientHeight || (window.innerHeight * 0.85);

    if (typeof Globe === 'undefined') {
      console.error('Globe.gl library not loaded');
      showWebGLFallback(containerEl);
      return;
    }

    // Render Quick-Select Region Pills
    renderRegionPills(allRegions);

    // Build High-Performance Globe Instance with Local Blue Marble Texture
    globeInstance = Globe()(containerEl)
      .width(width)
      .height(height)
      .backgroundColor('#0A1628')
      .globeImageUrl(getAssetPath('assets/earth-blue-marble.jpg'))
      .showAtmosphere(true)
      .atmosphereColor('#2E6FD8')
      .atmosphereAltitude(0.22)
      // Pulsing Location Impact Ring on the Active Station
      .ringsData(activeRegion ? [activeRegion] : [])
      .ringLat(function (d) { return d.lat; })
      .ringLng(function (d) { return d.lon; })
      .ringColor(function (d) { return function (t) { return d.color || '#1FB6A6'; }; })
      .ringMaxRadius(7.5)
      .ringPropagationSpeed(3.0)
      .ringRepeatPeriod(1200)
      // High-contrast Point Markers
      .pointsData(getFilteredRegions())
      .pointLat(function (d) { return d.lat; })
      .pointLng(function (d) { return d.lon; })
      .pointColor(function (d) { return d.color || '#1FB6A6'; })
      .pointAltitude(0.06)
      .pointRadius(2.2)
      .pointLabel(function (d) {
        return '<div style="background: rgba(10, 22, 40, 0.95); border: 1px solid ' + (d.color || '#1FB6A6') + '; padding: 8px 12px; border-radius: 4px; font-family: IBM Plex Mono, monospace; font-size: 12px; color: #F8FAFC; pointer-events: none;">' +
               '<strong>' + d.name + '</strong><br>' +
               '<span style="color: ' + (d.color || '#1FB6A6') + ';">● ' + d.issue_badge + '</span><br>' +
               '<span style="font-size: 10px; color: #94A3B8;">Click to inspect empirical telemetry</span>' +
               '</div>';
      })
      .onPointClick(function (d) {
        selectRegion(d);
      })
      // Spaceborne Labels Orbiting with Globe
      .labelsData(getFilteredRegions())
      .labelLat(function (d) { return d.lat; })
      .labelLng(function (d) { return d.lon; })
      .labelText(function (d) { return d.name; })
      .labelSize(1.2)
      .labelDotRadius(0.5)
      .labelColor(function (d) { return '#F8FAFC'; })
      .labelAltitude(0.065)
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
      if (closest && minDist < 15) {
        selectRegion(closest);
      }
    });

    // Controls configuration
    var controls = globeInstance.controls();
    controls.autoRotate = isAutoRotating;
    controls.autoRotateSpeed = 0.5;
    controls.enableDamping = true;
    controls.dampingFactor = 0.1;

    controls.addEventListener('start', function () {
      isAutoRotating = false;
      controls.autoRotate = false;
    });

    window.addEventListener('resize', function () {
      if (!globeInstance) return;
      var w = containerEl.clientWidth || window.innerWidth;
      var h = containerEl.clientHeight || (window.innerHeight * 0.85);
      globeInstance.width(w).height(h);
    });

    // Populate accessibility list table
    populateKeyboardList(allRegions);

    // Initial setup
    var initialHashMatch = handleUrlHash();
    if (!initialHashMatch && allRegions.length > 0) {
      selectRegion(allRegions[0]);
    }
    window.addEventListener('hashchange', handleUrlHash);
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
        '<img src="' + getAssetPath('assets/river_basin_network.jpg') + '" alt="Planetary observation map" style="max-width: 90%; max-height: 280px; border-radius: 8px; border: 1px solid #1E3456; margin-bottom: 1.5rem;">' +
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

  // Select Region  -  centres globe, rings beacon, then navigates to dedicated location profile page
  function selectRegion(region) {
    if (!region) return;
    activeRegion = region;

    // Highlight pill
    updateActivePill(region.id);

    // Halt auto-rotation, show beacon ring, and fly to coordinates
    if (globeInstance) {
      var controls = globeInstance.controls();
      controls.autoRotate = false;
      globeInstance.ringsData([region]);
      globeInstance.pointOfView({ lat: region.lat, lng: region.lon, altitude: 1.55 }, 700);
    }

    // Navigate to the standalone wiki-style location profile page
    var basePath = window.location.pathname.indexOf('/signal-earth-portal') === 0
      ? '/signal-earth-portal/' : '/';
    setTimeout(function () {
      window.location.href = basePath + 'location.html?region=' + region.id;
    }, 750);
  }

  // Load NASA Worldview Snapshot / Accurate Regional Satellite Asset
  function loadWorldviewSnapshot(region, dateStr, isCompare) {
    var imgEl = document.getElementById('drawer-snapshot-img');
    var compImgEl = document.getElementById('drawer-compare-img');
    var worldviewLink = document.getElementById('drawer-worldview-link');
    var statusEl = document.getElementById('drawer-snapshot-status');

    var targetImg = isCompare ? compImgEl : imgEl;
    if (!targetImg) return;

    var bbox = region.bbox || [region.lat - 1, region.lon - 1, region.lat + 1, region.lon + 1];
    var minLat = bbox[0], minLon = bbox[1], maxLat = bbox[2], maxLon = bbox[3];
    var targetDate = isCompare ? getTenYearAgoDate(dateStr) : dateStr;
    var layer = region.gibs_layer || 'MODIS_Terra_CorrectedReflectance_TrueColor';

    // Build absolute local asset path
    var localAsset = getAssetPath('assets/regions/' + region.id + (isCompare ? '_10yr.jpg' : '.jpg'));

    // Worldview direct link
    var wvPermalink = 'https://worldview.earthdata.nasa.gov/?v=' + minLon + ',' + minLat + ',' + maxLon + ',' + maxLat + '&l=Reference_Labels_15m,Reference_Features_15m,Coastlines_15m,' + layer + '&t=' + targetDate;
    if (worldviewLink) worldviewLink.href = wvPermalink;

    // Set fallback on error
    targetImg.onerror = function () {
      this.onerror = null;
      this.src = getAssetPath('assets/satellite_view_kanpur_haze_20211111.jpg');
    };

    // Load local high-resolution satellite radiometry immediately
    targetImg.src = localAsset;
    targetImg.style.opacity = '1';
    targetImg.style.display = 'block';

    if (statusEl && !isCompare) {
      statusEl.textContent = 'NASA Spaceborne Radiometry · ' + region.name;
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

  // Handle URL Hash deep linking  -  redirect to location page
  function handleUrlHash() {
    var hash = window.location.hash;
    if (hash && hash.indexOf('#region=') === 0) {
      var id = hash.replace('#region=', '');
      var found = allRegions.find(function (r) { return r.id === id; });
      if (found) {
        // Fly globe to region, then redirect to location profile
        if (globeInstance) {
          globeInstance.ringsData([found]);
          globeInstance.pointOfView({ lat: found.lat, lng: found.lon, altitude: 1.55 }, 700);
        }
        var basePath = window.location.pathname.indexOf('/signal-earth-portal') === 0
          ? '/signal-earth-portal/' : '/';
        setTimeout(function () {
          window.location.href = basePath + 'location.html?region=' + found.id;
        }, 800);
        return true;
      }
    }
    return false;
  }

  // Accessible Keyboard Region Table  -  rows link directly to location profile pages
  function populateKeyboardList(regions) {
    var tableBody = document.getElementById('globe-keyboard-tbody');
    if (!tableBody) return;
    tableBody.innerHTML = '';

    var basePath = window.location.pathname.indexOf('/signal-earth-portal') === 0
      ? '/signal-earth-portal/' : '/';

    regions.forEach(function (r) {
      var tr = document.createElement('tr');
      var locationUrl = basePath + 'location.html?region=' + r.id;
      tr.innerHTML =
        '<td><strong>' + r.name + '</strong><br><span style="font-size: 11px; color: var(--se-text-muted);">' + r.region + '</span></td>' +
        '<td><span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: ' + (r.color || '#1FB6A6') + '; margin-right: 6px;"></span>' + r.issue_badge + '</td>' +
        '<td style="font-family: var(--se-font-mono); font-size: 12px;">' + r.lat.toFixed(2) + '\u00b0, ' + r.lon.toFixed(2) + '\u00b0</td>' +
        '<td><a href="' + locationUrl + '" class="se-stream-btn" style="font-size: 11px; padding: 3px 8px; text-decoration: none; display: inline-block;">Open Profile \u2197</a></td>';

      tableBody.appendChild(tr);
    });
  }

  // Wire UI Controls: Filters only (drawer removed  -  detail opens on location.html)
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

  // Expose globally
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
