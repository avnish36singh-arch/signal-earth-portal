#!/usr/bin/env python3
"""
Signal Earth - Forest Area Cleaner (pipeline/02_clean/04_clean_forest.py)
Source: World Bank AG.LND.FRST.ZS (Food and Agriculture Organization FAO FRA)
Licence: CC BY 4.0
Zero em dashes or en dashes.
"""

import os
import json
import pandas as pd

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_FILE = os.path.join(WORKSPACE_ROOT, "pipeline", "raw", "wb_forest", "API_AG.LND.FRST.ZS_DS2_en_csv_v2_811.csv")
META_COUNTRY_FILE = os.path.join(WORKSPACE_ROOT, "pipeline", "raw", "wb_forest", "Metadata_Country_API_AG.LND.FRST.ZS_DS2_en_csv_v2_811.csv")
OUT_JSON = os.path.join(WORKSPACE_ROOT, "pipeline", "clean", "forest_cleaned.json")

def clean_forest():
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    meta_df = pd.read_csv(META_COUNTRY_FILE)
    aggregates = set(meta_df[meta_df['Region'].isna()]['Country Code'].dropna().str.upper())

    df = pd.read_csv(RAW_FILE, skiprows=4)
    year_cols = [c for c in df.columns if str(c).strip().isdigit()]
    sorted_years = sorted([int(y) for y in year_cols])

    cleaned = {}
    excluded_aggregates = []

    for _, row in df.iterrows():
        iso3 = str(row['Country Code']).strip().upper()
        name = str(row['Country Name']).strip()

        if iso3 in aggregates:
            excluded_aggregates.append({"iso3": iso3, "name": name})
            continue

        ts = {}
        latest_val = None
        latest_yr = None

        for y in sorted_years:
            val = row.get(str(y))
            if pd.notna(val):
                v_flt = round(float(val), 2)
                ts[str(y)] = v_flt
                latest_val = v_flt
                latest_yr = y

        cleaned[iso3] = {
            "iso3": iso3,
            "country_name": name,
            "latest_value": latest_val,
            "latest_year": latest_yr,
            "timeseries": ts,
            "unit": "% of land area",
            "source_name": "Food and Agriculture Organization (FAO)",
            "source_dataset": "Global Forest Resources Assessment via World Bank (AG.LND.FRST.ZS)",
            "source_url": "https://data.worldbank.org/indicator/AG.LND.FRST.ZS",
            "license": "CC BY 4.0"
        }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2)

    print(f"[+] Cleaned Forest Area data for {len(cleaned)} countries. Excluded {len(excluded_aggregates)} aggregates.")
    return cleaned

if __name__ == "__main__":
    clean_forest()
