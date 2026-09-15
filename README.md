# Signal Earth — Public Web Portal & Environmental Observatory

**Independent Environmental Data, Satellite Telemetry, and Atmospheric Analysis Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Web](https://img.shields.io/badge/Platform-Vanilla%20Web%20%2F%20Plotly.js-cyan.svg)](index.html)
[![Standard: CPCB NAQI](https://img.shields.io/badge/Standard-CPCB%20NAQI%202014-green.svg)](https://cpcb.nic.in)

---

## Overview

**Signal Earth** is an independent, open-access public observatory and environmental dashboard delivering interactive visualizations, regulatory evaluations, and scientific dispatches across Indian atmospheric corridors. The portal harmonizes ground-station regulatory telemetry from the Central Pollution Control Board (CPCB) and Uttar Pradesh Pollution Control Board (UPPCB) with NASA POWER satellite thermal datasets.

### Research Suite Repositories
- **Delhi NCR Analysis Pipeline (Python)**: [delhi-air_qaulity_cpcb](https://github.com/avnish36singh-arch/delhi-air_qaulity_cpcb)
- **Kanpur Air Quality Analysis**: [Air-Quality-Analysis-Kanpur](https://github.com/avnish36singh-arch/Air-Quality-Analysis-Kanpur)
- **Kanpur Land Surface Temperature & QGIS Spatial Analysis**: [Kanpur-LST-Thermal-Analysis-GIS](https://github.com/avnish36singh-arch/Kanpur-LST-Thermal-Analysis-GIS)

---

## Platform Features

1. **Multi-Year Delhi NCR Investigation (`investigations/delhi.html`)**
   - 1,825 continuous daily monitoring records (2017–2023) across 24 parameters.
   - Gap-fixed CPCB NAQI time series, sub-index breakdowns, and seasonal dynamics.
   - Interactive Plotly.js charts with full responsive zoom, pan, and hover telemetry.

2. **Kanpur Industrial Particulate Dynamics (`investigations/kanpur.html`)**
   - Multi-station telemetry (Nehru Nagar & Kidwai Nagar).
   - Diurnal traffic and industrial peaks, seasonal shifts, and meteorological scatter regressions.

3. **Kanpur Land Surface Temperature (LST) & Thermal Inversion (`investigations/kanpur-lst.html`)**
   - NASA POWER daily satellite skin temperature ($T_{\text{skin}}$) vs 2-meter air temperature ($T_{\text{2m}}$).
   - Nocturnal surface thermal inversion and particulate trapping diagnostics.
   - Spatial QGIS thermal buffer zones and station overlays.

4. **Cross-Basin Comparative Analysis (`investigations/comparison.html`)**
   - Indo-Gangetic Plain regional air mass dynamics comparing capital megacity vs industrial riverine basin.

5. **Methodology, Citations, & Dispatches**
   - Mathematical formulations of CPCB NAQI piecewise linear sub-indices.
   - Peer-reviewed research citations and analytical briefs.

---

## Directory Structure

```text
signal-earth-portal/
├── index.html                    # Observatory homepage
├── about.html                    # Mission, scope, and principles
├── methodology.html              # CPCB NAQI mathematical formulations
├── citations.html                # Academic literature and data sources
├── dispatches.html               # Analytical research articles
├── contact.html                  # Inquiries and researcher outreach
├── style.css                     # Editorial design system (Dark obsidian theme)
├── investigations/               # City-specific and comparative dashboards
│   ├── delhi.html                # Delhi interactive dashboard
│   ├── delhi.js                  # Delhi telemetry controller & Plotly charts
│   ├── kanpur.html               # Kanpur interactive dashboard
│   ├── kanpur-lst.html           # Kanpur LST & thermal inversion dashboard
│   ├── kanpur-lst.js             # LST controller & Plotly charts
│   └── comparison.html           # Cross-city comparison interface
├── assets/                       # High-resolution satellite imagery & charts
│   ├── delhi/                    # Delhi analytical charts
│   ├── kanpur/                   # Kanpur analytical charts
│   └── lst/                      # LST satellite plots & maps
└── data/                         # Harmonized telemetry feeds (JSON & GeoJSON)
    ├── delhi_daily_gapfixed.json # Cleaned Delhi continuous time series
    ├── kanpur_lst_daily.json     # Kanpur NASA POWER LST telemetry
    ├── kanpur_cpcb_stations.geojson
    ├── kanpur_thermal_zones.geojson
    └── kanpur/                   # Aggregated statistical records
```

---

## Local Development & Deployment

### Run Locally
Since the portal uses modern `fetch()` API calls to load local JSON and GeoJSON data, serve it using any local HTTP server:

```bash
# Using Python 3
python -m http.server 8000

# Or using Node.js
npx serve .
```
Then open `http://localhost:8000` in your web browser.

### Deploying to GitHub Pages
1. Push this repository to GitHub.
2. Go to **Settings** > **Pages**.
3. Under **Source**, select `Deploy from a branch` -> `main` -> `/ (root)`.
4. Click **Save**. Your site will be live at `https://<username>.github.io/<repo-name>/`.

---

## License

This project is open source and available under the [MIT License](LICENSE).
