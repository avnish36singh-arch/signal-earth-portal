---
title: Particulate Governance Frequency Across 1,137 Days of Delhi NAQI
date: 2026-10-14
author: Avnish Singh
sources: DPCC / CPCB (Alipur monitoring station)
data_link: /data/cleaned.json
corrections_link: /corrections.html
draft: true
---

> **DRAFT RESEARCH NOTE - PENDING PEER REVIEW**
> This analytical field note is currently undergoing scientific verification. It is withheld from official syndication.

## Summary of Computation

We analyzed 1,137 valid daily National Air Quality Index (NAQI) records from the Delhi Pollution Control Committee (DPCC) / CPCB monitoring station at Alipur between 2017 and 2023. Each day satisfies the official CPCB minimum reporting quorum (at least 16 hours of continuous measurements for three or more criteria pollutants including either PM2.5 or PM10).

On 95.3% of all valid monitoring days (1,083 of 1,137 days), particulate matter determined the primary sub-index driving the official daily NAQI score:
- PM2.5 was the governing pollutant on 51.8% of valid days (589 days).
- PM10 was the governing pollutant on 43.4% of valid days (494 days).
- Gaseous pollutants governed on only 4.7% of valid days (CO on 50 days = 4.4%, Ozone on 4 days = 0.4%).

Furthermore, the seasonal peak haze multiplier reached 5.75x when comparing peak winter AQI (Nov-Jan mean = 197.51 ug/m3) to core monsoon baseline (Jul-Sep mean = 34.32 ug/m3). Standard meteorological winter (Dec-Feb, 166.61 ug/m3) vs monsoon (Jun-Sep, 39.17 ug/m3) yields a 4.25x ratio.

## Empirical Dataset

- Total valid observation days: 1,137 days satisfying CPCB reporting quorum.
- Governing particulate frequency: 95.3% (1,083 days).
- PM2.5 dominance: 51.8% of valid days (589 days).
- PM10 dominance: 43.4% of valid days (494 days).
- Underlying data: [cleaned.json](/data/cleaned.json).

## Key Observational Limitations

The dataset includes a 731-day operational hiatus during station sensor refurbishment and recalibration between 2019 and 2020. Measurements represent a single peripheral ambient station situated in northwest Delhi.

## Corrections and Reproducibility

Signal Earth maintains an open corrections policy. If you detect any discrepancy, refer to the [corrections log](/corrections.html).
