# Signal Earth : Public Environmental Data Portfolio

The Earth is changing faster than most people realize. Making environmental change visible through maps, data, and science.

Maintained by Avnish Singh, undergraduate student in Civil Engineering at Harcourt Butler Technical University (HBTU), Kanpur.

Portal URL: https://avnish36singh-arch.github.io/signal-earth-portal/

## Overview

Signal Earth is an independent environmental data portfolio that transforms satellite observations, maps, official datasets, and research records into clear visual evidence. The project examines air quality data from the Central Pollution Control Board (CPCB), Uttar Pradesh Pollution Control Board (UPPCB), and Delhi Pollution Control Committee (DPCC), alongside reanalysis skin temperature data from NASA POWER (GMAO MERRA-2).

This site is an independent student portfolio, not an operational monitoring platform, not a government body, and not a commercial product. All analytical code is open source and reproducible.

### Research Pipelines

- Delhi NCR Analysis Pipeline (Python): [delhi-air_qaulity_cpcb](https://github.com/avnish36singh-arch/delhi-air_qaulity_cpcb)
- Kanpur Air Quality Analysis: [Air-Quality-Analysis-Kanpur](https://github.com/avnish36singh-arch/Air-Quality-Analysis-Kanpur)
- Kanpur Skin Temperature and Spatial GIS Analysis: [Kanpur-LST-Thermal-Analysis-GIS](https://github.com/avnish36singh-arch/Kanpur-LST-Thermal-Analysis-GIS)

## Published Analyses

1. Kanpur Particulate Dynamics (`investigations/kanpur.html`)
   - Evaluates particulate levels (PM2.5 and PM10) from two monitoring stations (NSI Kalyanpur and Nehru Nagar) across two discrete observation windows (July 2021 to October 2022 and February 2025 to August 2026; pooled 1,628 station-days).
   - Diurnal traffic and industrial peaks, seasonal variations, and ratio screening (PM2.5 / PM10).

2. Delhi Five-Year NAQI Analysis (`investigations/delhi.html`)
   - Analyzes 1,825 daily records from Alipur, Delhi (2017 to 2023).
   - Documents an operational monitoring gap of 732 days (January 1, 2019 to December 31, 2020) where the station was inactive.
   - Evaluates 1,137 official days meeting the CPCB minimum reporting quorum (3 pollutants including at least one PM parameter).

3. Kanpur Surface Skin Temperature and Boundary Coupling (`investigations/kanpur-lst.html`)
   - Utilizes NASA POWER (GMAO MERRA-2) daily reanalysis skin temperature (TS) and 2-meter air temperature (T2M) over a single 0.5° × 0.625° grid box (~55 × 60 km) covering Kanpur.
   - Examines negative seasonal association with PM2.5 during the true overlap window (July 9, 2021 to October 16, 2022; n = 308, Pearson r = -0.455).
   - Clarifies that coarse reanalysis data cannot resolve intra-urban heat islands; detailed spatial zoning remains planned future work.

4. Regional Airshed Comparison (`investigations/comparison.html`)
   - Compares particulate metrics between Delhi (Alipur) and Kanpur (Kalyanpur and Nehru Nagar).
   - Explicitly notes non-identical monitoring periods, differing station counts (single megacity peripheral station versus pooled industrial/suburban monitors), and differing data density.

## Methodology and Limitations

- CPCB NAQI Formulation: Piecewise linear interpolation based on CPCB 2014 guidelines.
- Ratio Filtering: Observations where PM2.5 > PM10 are physically implausible and flagged or filtered during quality control.
- Reanalysis Resolution: NASA POWER data reflects model reanalysis at regional grid resolution, not high-resolution satellite radiometer land surface temperature.

## Project Structure

```text
signal-earth-portal/
├── index.html                    # Portfolio homepage with NAQI calculator
├── about.html                    # Author background and project scope
├── methodology.html              # CPCB NAQI formula and quality control limits
├── data.html                     # Monitoring station registry, counts, and citations
├── contact.html                  # Contact and inquiry information
├── privacy.html                  # Privacy policy (static hosting, zero tracking)
├── terms.html                    # Terms of use and educational disclaimer
├── licenses.html                 # MIT license and data attribution
├── corrections.html              # Chronological revision and corrections log
├── citations.html                # Redirect to data.html
├── 404.html                      # Not found error page
├── sitemap.xml                   # Site URL index
├── robots.txt                    # Search crawler instructions
├── style.css                     # Editorial journal stylesheet (light theme)
├── investigations/
│   ├── delhi.html                # Delhi investigation
│   ├── delhi.js                  # Delhi Plotly.js charts
│   ├── kanpur.html               # Kanpur particulate investigation
│   ├── kanpur-lst.html           # Kanpur temperature and coupling investigation
│   ├── kanpur-lst.js             # Temperature Plotly.js charts
│   └── comparison.html           # Regional airshed comparative analysis
├── assets/                       # Verified analytical figures and static maps
│   ├── delhi/                    # Delhi charts
│   ├── kanpur/                   # Kanpur charts
│   └── lst/                      # Temperature plots and station location map
└── data/                         # Processed observation data (JSON and GeoJSON)
    ├── delhi_daily_gapfixed.json
    ├── kanpur_lst_daily.json
    ├── kanpur_cpcb_stations.geojson
    ├── kanpur_thermal_zones.geojson
    └── kanpur/
```

## Running Locally

Because the interactive charts use JavaScript fetch requests to load local JSON files, serve the directory with a local HTTP server:

```bash
# Python 3
python -m http.server 8000
```

Then visit `http://localhost:8000` in your web browser.

## License

- Software and markup: MIT License (see [LICENSE](LICENSE)).
- Editorial text and charts: Creative Commons Attribution 4.0 International (CC BY 4.0).
- Data: Central Pollution Control Board (CPCB), Uttar Pradesh Pollution Control Board (UPPCB), Delhi Pollution Control Committee (DPCC), and NASA POWER.
