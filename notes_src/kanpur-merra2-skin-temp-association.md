---
title: Seasonal Association of MERRA-2 Skin Temperature with Ground PM2.5 in Kanpur
date: 2026-10-09
author: Avnish Singh
sources: NASA POWER (GMAO MERRA-2 daily skin temperature TS) and CPCB CAAQMS
data_link: /data/numbers_ledger.json
corrections_link: /corrections.html
draft: true
---

> **DRAFT RESEARCH NOTE - PENDING PEER REVIEW**
> This analytical field note is currently undergoing scientific verification. It is withheld from official syndication.

## Summary of Computation

Surface skin temperature measurements derived from the NASA POWER GMAO MERRA-2 assimilation model were paired with daily continuous ground PM2.5 observations from the CPCB monitoring station in Kalyanpur, Kanpur across 308 concurrent calendar dates between July 9, 2021 and October 16, 2022.

The two variables exhibit a moderate negative Pearson correlation coefficient:
r = -0.455 across the 308 concurrent pairs.

Because consecutive daily atmospheric observations exhibit strong temporal autocorrelation, reporting an unadjusted classical p-value would be statistically misleading. The effective sample size is significantly smaller than the nominal count of 308 daily pairs. This negative correlation reflects shared regional seasonal cycles rather than a simple unlagged linear causal relationship.

## Empirical Dataset

- Concurrent paired dates: 308 calendar dates.
- Total MERRA-2 reanalysis days processed: 2,556 days (2017 to 2023).
- Pearson correlation coefficient (r): -0.455.
- Statistical caveat: Autocorrelated time series; classical p-values omitted to avoid pseudoreplication.
- Underlying data: [numbers_ledger.json](/data/numbers_ledger.json).

## Key Observational Limitations

The MERRA-2 reanalysis grid cell is 0.5 degrees latitude by 0.625 degrees longitude (approximately 55 km by 60 km). This coarse regional resolution averages regional boundary layer heat flux and cannot resolve intra-urban microclimate gradients. Nocturnal temperature inversions cannot be proven without vertical atmospheric soundings.

## Corrections and Reproducibility

Signal Earth maintains an open corrections policy. Please report errors or suggestions in our [corrections log](/corrections.html).
