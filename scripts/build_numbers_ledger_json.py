#!/usr/bin/env python3
"""
Signal Earth - Numbers Ledger JSON Builder
Converts numbers_ledger.csv into structured data/numbers_ledger.json
Zero em dashes or en dashes.
"""

import csv
import json
import os

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_FILE = os.path.join(WORKSPACE_ROOT, "numbers_ledger.csv")
JSON_FILE = os.path.join(WORKSPACE_ROOT, "data", "numbers_ledger.json")

def build_ledger():
    entries = []
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append(row)

    # Structured key mapping for homepage cards and case studies
    structured = {
        "metadata": {
            "title": "Signal Earth Analytical Numbers Ledger",
            "version": "2026.10",
            "total_entries": len(entries),
            "description": "Empirical figures cited across research papers, verified against underlying scripts and data files."
        },
        "case_studies": {
            "kanpur_particulate": {
                "id": "kanpur",
                "title": "Kanpur Particulate Dynamics",
                "headline_number": "2.40x",
                "headline_label": "Winter-to-monsoon PM2.5 ratio",
                "finding": "Winter PM2.5 averaged 2.40x monsoon levels across both observation windows (61.41 vs 25.61 ug/m3).",
                "station_days": 1628,
                "period": "July 2021 to October 2022 and February 2025 to August 2026",
                "source": "CPCB CAAQMS (Kalyanpur and Nehru Nagar)",
                "limitation": "855-day operational monitoring gap between observation windows; spatial coverage restricted to two urban monitors.",
                "url": "analyses/kanpur/"
            },
            "delhi_naqi": {
                "id": "delhi",
                "title": "Delhi Five-Year NAQI Dynamics",
                "headline_number": "95.3%",
                "headline_label": "Valid days governed by particulate matter",
                "finding": "Particulate matter governed official AQI on 95.3% of valid days (PM2.5 on 51.8%, PM10 on 43.4%), with a 5.75x peak haze multiplier.",
                "valid_days": 1137,
                "period": "2017 to 2023 (1,137 days satisfying CPCB minimum reporting quorum)",
                "source": "DPCC / CPCB (Alipur monitoring station)",
                "limitation": "731-day operational hiatus during station refurbishment (2019-2020); single peripheral monitoring station.",
                "url": "analyses/delhi/"
            },
            "kanpur_temperature": {
                "id": "kanpur-lst",
                "title": "Kanpur Skin Temperature & Inversion",
                "headline_number": "r = -0.455",
                "headline_label": "Skin temperature to PM2.5 correlation",
                "finding": "Daily surface skin temperature exhibits a moderate negative seasonal correlation with PM2.5 (r = -0.455, p = 2.47e-16 across 308 concurrent pairs).",
                "concurrent_pairs": 308,
                "total_reanalysis_days": 2556,
                "period": "July 9, 2021 to October 16, 2022 (overlap window; 2017-2023 overall)",
                "source": "NASA POWER (GMAO MERRA-2 daily skin temperature TS)",
                "limitation": "Coarse regional reanalysis grid cell (0.5 deg x 0.625 deg, ~55 x 60 km) cannot resolve intra-urban heat islands.",
                "url": "analyses/kanpur-lst/"
            },
            "kanpur_landsat": {
                "id": "kanpur-uhi",
                "title": "Kanpur Landsat 30 m Thermal Infrared",
                "headline_number": "1.0 to 2.3 K",
                "headline_label": "Urban-rural radiometric thermal delta",
                "finding": "Landsat 8/9 TIRS-2 radiometric snapshot observed an empirical urban-rural thermal delta of 1.0 to 2.3 K across winter clear-sky overpasses.",
                "scenes_analyzed": "January 15 and February 16, 2022 snapshots",
                "period": "Winter 2022 daytime satellite overpasses",
                "source": "USGS Landsat 8/9 TIRS-2 Band 10 (30 m resampled)",
                "limitation": "Instantaneous clear-sky daytime snapshot observation; requires vertical atmospheric soundings to confirm inversion dynamics.",
                "url": "analyses/kanpur-uhi/"
            }
        },
        "raw_entries": entries
    }

    os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2)

    print(f"[+] Wrote data/numbers_ledger.json with {len(entries)} ledger entries.")

if __name__ == "__main__":
    build_ledger()
