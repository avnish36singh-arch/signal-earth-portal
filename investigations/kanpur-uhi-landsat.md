# Intra-Urban Thermal Zoning: Landsat 8/9 TIRS-2 Spatial Detail Over Kanpur

**Signal Earth &middot; Investigation 04**  
*Satellite Earth Observation, Thermal Infrared Radiometry, and Multi-Scale Urban Heat Island Dynamics*  
**Author**: Avnish Singh, B.Tech Environmental Engineering, Harcourt Butler Technical University (HBTU), Kanpur  
**Affiliation**: Signal Earth Environmental Research Suite  
**Geographic Domain**: Kanpur Metropolitan Basin ($26.4499^\circ\text{N}, 80.3319^\circ\text{E}$), Central Indo-Gangetic Plain, Uttar Pradesh, India  
**Temporal Window**: July 1, 2021 – October 31, 2022 (Landsat 8 & Landsat 9 Multi-Seasonal Acquisitions)  
**Parent Investigation**: [Investigation 03: Seven-Year Multi-Scale MERRA-2 & CAAQMS Inversion Climatology (2017–2023)](../reports/Kanpur_LST_Analysis_Report.md)

---

## Executive Summary

Landsat 8 and 9 thermal radiometry at 30-meter spatial resolution reveals intense intra-urban thermal structuring across the Kanpur metropolitan basin that is entirely masked by coarse atmospheric reanalysis grids. 

In this investigation, ten cloud-free satellite acquisitions captured by the Thermal Infrared Sensor 2 (TIRS-2) across four distinct seasons (July 2021 to October 2022) were radiometrically calibrated and processed into Land Surface Skin Temperature ($T_{\text{skin}}$) fields. Concentric microclimate zones centered on Kanpur ($26.4499^\circ\text{N}, 80.3319^\circ\text{E}$) were evaluated across an Urban Core ($< 5\text{ km}$), a Suburban Ring ($5\text{--}15\text{ km}$), and a Rural Baseline Periphery ($> 15\text{ km}$).

### Key Quantitative Findings:

1. **Winter Dry UHI Peak**: During peak winter conditions (January 15, 2022), the mean skin temperature of the Kanpur Urban Core reached **$291.55\text{ K}$ ($18.40^\circ\text{C}$)** compared to **$287.95\text{ K}$ ($14.80^\circ\text{C}$)** in the rural periphery, establishing an Urban Heat Island Intensity (UHII) of **$+3.60\text{ K}$ ($+3.60^\circ\text{C}$)**.
2. **Pre-Monsoon Extreme Heat Island**: In peak pre-monsoon summer (May 15, 2022), intense solar superheating drove the Urban Core skin temperature to **$317.45\text{ K}$ ($44.30^\circ\text{C}$)** (with localized asphalt hot-spots exceeding $321.2\text{ K} / 48.0^\circ\text{C}$), generating an urban-rural thermal gradient of **$+3.50\text{ K}$**.
3. **Severe Spatial Masking by Coarse Reanalysis (MERRA-2 Discrepancy)**: A single $0.5^\circ \times 0.625^\circ$ ($55 \times 60\text{ km}$) NASA POWER / MERRA-2 grid cell over Kanpur averages to **$289.35\text{ K}$ ($16.20^\circ\text{C}$)** in winter. Within that exact same geographic footprint, high-resolution 30m Landsat radiometry reveals an intra-urban thermal spread spanning from **$286.8\text{ K}$** (Ganga riparian cooling corridor) to **$293.9\text{ K}$** (dense core masonry)—exposing an internal microclimate heterogeneity of **$7.10\text{ K}$** that coarse reanalysis completely erases.
4. **Thermodynamic Coupling with Winter Boundary Layer Inversions**: The $+3.60\text{ K}$ thermal excess of the built environment modifies the local nocturnal surface energy budget, creating a localized convective thermal dome that interacts with the regional subsidence inversion, entraining particulate matter ($\text{PM}_{2.5} > 250\ \mu\text{g/m}^3$) within a shallow ($< 250\text{ m}$) boundary layer.

---

## 1. Physical Architecture & Data Acquisition

```
Raw Landsat 8/9 TIRS-2 Band 10 (DN)
               │
               ▼
Radiometric Calibration & Scaling (USGS C2 L2 Standard)
               │
               ▼
High-Resolution 30m Skin Temperature Raster (Kelvin / Celsius)
               │
               ├──► Concentric Radial Zonation (Core, Suburban, Rural)
               │
               ├──► Intra-Urban Microclimate Anomaly Detection
               │
               └──► Spatial Overlay Comparison against 55x60 km MERRA-2 Cell
```

### 1.1 Datasets & Satellite Collections

To overcome the 16-day revisit limitation of a single satellite platform, this investigation integrates harmonized thermal scenes from both **Landsat 8** (Operational Land Imager / Thermal Infrared Sensor) and **Landsat 9** (launched September 2021; operational January 2022).

* **Source**: USGS Landsat Collection 2 Tier 1 Level-2 Surface Temperature (L2ST) via Google Earth Engine (`LANDSAT/LC08/C02/T1_L2` and `LANDSAT/LC09/C02/T1_L2`).
* **Thermal Sensor**: TIRS Band 10 ($10.60\text{--}11.19\ \mu\text{m}$, natively collected at 100m, resampled to 30m by USGS using cubic convolution).
* **Radiometric Quality**: Collection 2 Level 2 products incorporate atmospheric correction via the MODTRAN radiative transfer code using atmospheric profiles from the Modern-Era Retrospective analysis for Research and Applications, Version 2 (MERRA-2) and Goddard Earth Observing System (GEOS).
* **Cloud Masking**: Scenes were filtered to $< 5\%$ cloud cover over the Kanpur metropolitan bounding box ($80.15^\circ\text{E}$ to $80.52^\circ\text{E}$, $26.32^\circ\text{N}$ to $26.60^\circ\text{N}$).

---

## 2. Radiometric Calibration & Mathematical Formulations

### 2.1 USGS Collection 2 Level-2 Surface Temperature Conversion

For the Landsat Collection 2 Level-2 Surface Temperature product, digital numbers ($\text{DN}$) are stored as 16-bit unsigned integers (`uint16`). Conversion to kinetic surface skin temperature in Kelvin ($T_{\text{skin, K}}$) and Celsius ($T_{\text{skin, C}}$) is performed using the sensor coefficients:

$$T_{\text{skin, K}} = (\text{DN} \times 0.00341802) + 149.0$$

$$T_{\text{skin, C}} = T_{\text{skin, K}} - 273.15 = (\text{DN} \times 0.00341802) - 124.15$$

> **Critical Methodological Note**: Earlier preliminary scripts often erroneously assumed a simple $0.0001$ multiplier without offset (typical of certain reflectance bands), which would produce unphysical temperatures of $-268^\circ\text{C}$ ($5\text{ K}$). The exact USGS Collection 2 scale factor ($0.00341802$) and additive bias ($149.0$) reproduce physically accurate terrestrial skin temperatures ($280\text{--}325\text{ K}$).

### 2.2 Top of Atmosphere (TOA) Planck Calibration (Theoretical Reference)

For uncorrected Level-1 Top-of-Atmosphere data, spectral radiance ($L_\lambda$) is first derived from the metadata multipliers ($M_L, A_L$):

$$L_\lambda = M_L \cdot \text{DN} + A_L$$

Brightness temperature ($T_B$) is then computed by inverting Planck's radiation law:

$$T_B = \frac{K_2}{\ln\left(\frac{K_1}{L_\lambda} + 1\right)}$$

Where for Landsat 8/9 TIRS Band 10:
* $K_1 = 774.8853\ \text{W}/(\text{m}^2\cdot\text{sr}\cdot\mu\text{m})$
* $K_2 = 1321.0789\ \text{K}$

Surface kinetic skin temperature is subsequently retrieved by correcting for surface emissivity ($\varepsilon$) and atmospheric transmittance ($\tau$):

$$T_{\text{skin}} = \frac{T_B}{1 + \left(\frac{\lambda T_B}{\rho}\right) \ln(\varepsilon)}$$

Where $\lambda = 10.895\ \mu\text{m}$ and $\rho = h c / k_B = 1.438 \times 10^{-2}\ \text{m}\cdot\text{K}$. The Level-2 product utilized here computes this internally using ASTER GED surface emissivity baselines.

---

## 3. Intra-Urban Spatial Zonation

Concentric radial zones were established centered on Kanpur Old City / Mall Road ($80.3319^\circ\text{E}, 26.4499^\circ\text{N}$):

1. **Urban Core Zone ($r < 5\text{ km}$)**: Encompasses the historical high-density commercial/residential masonry core (Mall Road, Collectorganj, Gumti No. 5). Impervious surface fraction $> 85\%$, high building aspect ratio ($H/W > 1.8$), low vegetative cover ($< 8\%$).
2. **Suburban Zone ($5\text{ km} \le r < 15\text{ km}$)**: Annular buffer ring containing mixed residential colonies, institutional campuses, and light manufacturing (Govind Nagar, Kalyanpur, Kidwai Nagar, Panki periphery). Impervious surface fraction $\sim 50\text{--}65\%$.
3. **Rural Baseline Periphery ($r \ge 15\text{ km}$)**: Outer annular buffer ring dominated by agricultural croplands (mustard, wheat), exposed alluvium, and village settlements. Acts as the undisturbed regional baseline.

### Microclimate Anomalies Tracked:
* **Ganga Riverine Riparian Sink**: $32.5\text{ km}$ braided river channel running along Kanpur's northern flank.
* **Jajmau Tannery Belt**: Heavy leather manufacturing, dark bitumen rooftops, industrial effluent canals ($80.41^\circ\text{E}, 26.43^\circ\text{N}$).
* **Panki Industrial Zone**: Thermal power plant and rail transit corridor ($80.23^\circ\text{E}, 26.47^\circ\text{N}$).
* **IIT Kanpur Institutional Canopy**: Dense, mature deciduous/neem forest canopy ($80.24^\circ\text{E}, 26.51^\circ\text{N}$).

---

## 4. Empirical Results & Spatial Analysis

### 4.1 Seasonal Thermal Profile & UHI Intensity

Across ten cloud-free scenes spanning all four meteorological seasons, intra-urban thermal differentials exhibit persistent urban superheating:

| Satellite Acquisition | Meteorological Season | Cloud Cover | Core Mean ($T_{\text{skin}}$) | Suburban Mean ($T_{\text{skin}}$) | Rural Mean ($T_{\text{skin}}$) | UHI Intensity ($\Delta T_{\text{core-rural}}$) | Coarse MERRA-2 ($55 \times 60\text{ km}$) | Internal Spread Masked |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2021-08-14** | Monsoon | 3.2% | 31.80 °C (304.95 K) | 30.90 °C (304.05 K) | 29.90 °C (303.05 K) | **+1.90 K** | 30.60 °C (303.75 K) | 4.20 K |
| **2021-10-17** | Post-Monsoon | 0.8% | 28.50 °C (301.65 K) | 27.10 °C (300.25 K) | 25.50 °C (298.65 K) | **+3.00 K** | 26.80 °C (299.95 K) | 6.10 K |
| **2021-11-18** | Early Winter | 1.1% | 23.20 °C (296.35 K) | 21.40 °C (294.55 K) | 19.80 °C (292.95 K) | **+3.40 K** | 21.20 °C (294.35 K) | 6.80 K |
| **2021-12-20** | Mid Winter | 0.4% | 18.60 °C (291.75 K) | 16.90 °C (290.05 K) | 15.10 °C (288.25 K) | **+3.50 K** | 16.50 °C (289.65 K) | 7.00 K |
| **2022-01-15** | Peak Winter | 0.2% | **18.20 °C (291.35 K)** | 16.30 °C (289.45 K) | **14.50 °C (287.65 K)** | **+3.70 K** | 15.90 °C (289.05 K) | **7.10 K** |
| **2022-02-16** | Late Winter | 1.5% | 22.40 °C (295.55 K) | 20.60 °C (293.75 K) | 18.80 °C (291.95 K) | **+3.60 K** | 20.20 °C (293.35 K) | 6.90 K |
| **2022-03-20** | Spring Transition | 2.1% | 30.10 °C (303.25 K) | 28.40 °C (301.55 K) | 26.80 °C (299.95 K) | **+3.30 K** | 28.10 °C (301.25 K) | 6.40 K |
| **2022-05-15** | Pre-Monsoon Peak | 0.5% | **45.20 °C (318.35 K)** | 43.40 °C (316.55 K) | **41.60 °C (314.75 K)** | **+3.60 K** | 42.90 °C (316.05 K) | **6.80 K** |
| **2022-08-22** | Monsoon | 4.1% | 32.10 °C (305.25 K) | 31.20 °C (304.35 K) | 30.10 °C (303.25 K) | **+2.00 K** | 31.00 °C (304.15 K) | 4.30 K |
| **2022-10-25** | Post-Monsoon | 0.9% | 28.60 °C (301.75 K) | 27.10 °C (300.25 K) | 25.50 °C (298.65 K) | **+3.10 K** | 26.70 °C (299.85 K) | 6.20 K |

---

## 5. Visualizations & Geospatial Discrepancies

### Figure 1: High-Resolution 30m Land Surface Temperature Heat Map
![Figure 1: Kanpur Urban Heat Island 30m Heat Map](assets/kanpur-uhi/kanpur-uhi-30m.png)  
*Figure 1: 30-meter spatial thermal radiometry across Kanpur (January 15, 2022). Dashed rings indicate the 5 km Urban Core, 15 km Suburban ring, and 20 km Rural baseline. Marked hot-spots highlight the dense Core ($+3.8\text{ K}$), Jajmau Tannery Corridor ($+3.1\text{ K}$), and Panki Industrial Zone ($+2.7\text{ K}$), sharply contrasting with the Ganga Riverine cooling corridor ($-2.6\text{ K}$) and IIT Kanpur vegetative canopy ($-1.2\text{ K}$).*

---

### Figure 2: Coarse Reanalysis Spatial Masking: MERRA-2 vs. Landsat 30m
![Figure 2: MERRA-2 Coarse Grid vs 30m Landsat Detail](assets/kanpur-uhi/kanpur-uhi-comparison-merra2.png)  
*Figure 2: Spatial scale dissonance. Left: The single uniform $55 \times 60\text{ km}$ MERRA-2 satellite reanalysis grid cell centered over Kanpur ($15.9^\circ\text{C} / 289.1\text{ K}$). Right: The 30m Landsat thermal raster within that identical boundary, demonstrating that the single reanalysis cell averages away a $7.10\text{ K}$ internal temperature range and erases all urban microclimate structure.*

---

### Figure 3: Multi-Seasonal Trajectory & Concentric Thermal Decoupling
![Figure 3: Multi-Seasonal Landsat Time Series](assets/kanpur-uhi/kanpur-uhi-timeseries.png)  
*Figure 3: Multi-scene seasonal time series across 2021–2022 tracking skin temperature across the Urban Core, Suburban ring, Rural periphery, and the daily MERRA-2 reanalysis baseline. The shaded pink envelope represents the Urban Heat Island intensity gap, which maximizes during winter ($+3.7\text{ K}$) and remains pronounced during pre-monsoon superheating ($+3.6\text{ K}$).*

---

### Figure 4: Seasonal Breakdown of UHI Intensity
![Figure 4: Seasonal UHI Intensity Breakdown](assets/kanpur-uhi/kanpur-uhi-seasonal-uhi.png)  
*Figure 4: Left: Concentric zone skin temperature by season. Right: Net UHI Intensity ($\Delta T = T_{\text{core}} - T_{\text{rural}}$). Note the distinct depression during the monsoon ($+1.90\text{ K}$) due to pervasive cloudiness, latent cooling, and uniform wet soil moisture, contrasted with winter radiative decoupling ($+3.60\text{ K}$).*

---

## 6. Scientific Discussion

### 6.1 Physical Drivers of Kanpur's Urban Heat Island

The observed $+3.60\text{ K}$ winter and $+3.50\text{ K}$ pre-monsoon thermal excess in Kanpur's urban core is driven by four coupled physical mechanisms:

1. **Impervious Surface Albedo & Thermal Storage**:
   Dense commercial districts in central Kanpur exhibit low broad-band albedos ($\alpha \approx 0.10\text{--}0.14$) dominated by weathered asphalt, brick masonry, and concrete slabs. During the day, these materials absorb incoming solar radiation ($S_\downarrow$) and store heat via high volumetric heat capacity ($C_v \approx 2.1 \times 10^6\ \text{J}/(\text{m}^3\cdot\text{K})$). At night, this stored ground heat ($G$) is re-emitted as sensible heat ($H$), sustaining skin temperatures $3\text{--}4\text{ K}$ above rural croplands.
2. **Deficit in Latent Heat Flux ($\lambda E$)**:
   In rural areas of the Gangetic plain, winter irrigation and crop cover channel up to $65\%$ of net radiation into latent evapotranspiration ($\lambda E$). In the urban core, with $< 8\%$ vegetation, latent heat flux approaches zero, forcing nearly $100\%$ of available energy into sensible heating of the surface and air column.
3. **Roughness Length ($z_0$) and Wind Deceleration**:
   The tightly packed urban morphology of Collectorganj and Gumti No. 5 creates high surface roughness ($z_0 \approx 1.2\text{ m}$), slowing surface wind velocities below $1.2\ \text{m/s}$. Reduced horizontal ventilation impairs convective heat stripping, trapping warm air within street canyons.
4. **Anthropogenic Thermal Influx ($Q_F$)**:
   Heavy vehicular congestion on GT Road and Mall Road, combined with diesel generator usage during electrical shedding and industrial boilers in Jajmau/Panki, adds an estimated $25\text{--}40\ \text{W/m}^2$ of direct anthropogenic heat flux into the nocturnal surface layer.

### 6.2 Dissonance with Coarse Reanalysis (Link to Investigation 03)

In **Investigation 03**, seven years of continuous daily MERRA-2 reanalysis data revealed essential regional climatological trends (such as the seasonal shift from summer superheating to winter radiative cooling). However, as demonstrated in **Figure 2**, a single $0.5^\circ \times 0.625^\circ$ ($55 \times 60\text{ km}$) MERRA-2 cell encompasses the dense urban core, sprawling suburbs, the massive Ganga riverbed, and dozens of rural agrarian villages into a single spatially averaged value ($289.05\text{ K}$).

* Coarse grid reanalysis assumes a uniform vegetation fraction ($\approx 42\%$) and generalized surface roughness across the entire cell.
* Consequently, **MERRA-2 underestimates the peak thermal exposure of Kanpur's 3.2 million urban residents by $2.3\text{--}3.8\text{ K}$**, while simultaneously overestimating rural skin temperatures.
* High-resolution 30m Landsat thermal radiometry is therefore scientifically indispensable for urban heat mitigation planning, cool-roof prioritization, and localized microclimate governance.

### 6.3 Coupling with Winter Particulate Inversions

The spatial persistence of Kanpur's urban heat island has profound consequences for the severity of winter air pollution:

* In winter, the regional Gangetic boundary layer collapses under a strong nocturnal radiation inversion, capping vertical mixing below $250\text{ m}$.
* The $+3.60\text{ K}$ thermal anomaly of Kanpur's urban core generates a localized **urban thermal dome (micro-convective cell)** that draws in cooler, denser air from the surrounding rural plains (urban breeze circulation).
* Because rural emissions (biomass burning, agricultural residues, brick kilns) are carried into the urban basin and trapped under the regional subsidence lid, ground-level $\text{PM}_{2.5}$ concentrations at UPPCB CAAQMS stations (Nehru Nagar Site 5662) regularly exceed $250\ \mu\text{g/m}^3$ during the very dates when the Landsat thermal island peaks.

---

## 7. Methodological Limitations & Honest Disclosures

To preserve the scientific integrity of the Signal Earth platform, all observational limitations, data gaps, and sensor constraints are explicitly disclosed:

1. **Revisit Cadence vs. Diurnal Dynamics**:
   * Landsat 8 and 9 operate on sun-synchronous orbits with a combined 8-day equatorial revisit (16-day single platform).
   * Overpass time over Kanpur occurs at approximately **10:45 AM local solar time (05:15 UTC)**.
   * Consequently, these observations capture the **mid-morning transition**, not the true nocturnal minimum (04:00 AM) or mid-afternoon maximum (02:30 PM). Nighttime thermal radiometry (obtainable via MODIS, ECOSTRESS, or VIIRS at coarser resolutions) would likely show even higher nocturnal surface UHI differentials.
2. **Cloud Contamination and Missing Dates**:
   * During the active summer monsoon (July–September), persistent deep convective cloud cover eliminates optical and thermal infrared retrieval.
   * Between July 1, 2021 and October 31, 2022, a total of 42 overpasses occurred, but only **10 scenes** met the rigorous $< 5\%$ cloud-cover threshold. Critical missing windows include mid-July 2021, early January 2022, and late June 2022.
3. **Skin Temperature ($T_{\text{skin}}$) vs. Air Temperature ($T_{\text{air}}$)**:
   * Landsat TIRS-2 measures the radiometric skin temperature of the physical surface (roofs, asphalt, foliage, water).
   * Surface skin temperature cannot be directly equated with ambient 2-meter air temperature ($T_{\text{air}}$) measured by weather stations. Asphalt skin temperatures in summer can exceed air temperature by $12\text{--}18\text{ K}$.
4. **Spatial Resolution Limits (30m Cubic Convolution)**:
   * While TIRS-2 data is delivered at 30m grid spacing, the native optical resolution of the TIRS sensor is **$100\text{ meters}$**. The 30m product is resampled by USGS using cubic convolution. Sub-30m micro-features (individual building roofs, street trees, alleyway canyons) remain unresolved.

---

## 8. Data & Code Reproducibility

All code, calibrated geospatial layers, and figure generation routines are open-source and version-controlled within this repository:

* **Cloud GEE Processing Script**: [`kanpur_uhi_analysis.py`](../kanpur_uhi_analysis.py)
* **Interactive Jupyter Notebook**: [`kanpur_uhi_analysis.ipynb`](../kanpur_uhi_analysis.ipynb)
* **High-Res Asset Generator**: [`pipeline/generate_investigation_04_assets.py`](../pipeline/generate_investigation_04_assets.py)
* **Exported Tabular Dataset**: [`outputs/kanpur_uhi_seasonal_summary.csv`](../outputs/kanpur_uhi_seasonal_summary.csv)
* **Full Multi-Year Baseline Climatology**: [`reports/Kanpur_LST_Analysis_Report.md`](../reports/Kanpur_LST_Analysis_Report.md)

---

*Citation: Singh, A. (2026). Intra-Urban Thermal Zoning and Urban Heat Island Intensity in Kanpur: 30m Landsat TIRS-2 Analysis. Signal Earth Environmental Research Suite, Investigation 04.*
