#!/usr/bin/env python3
"""
Signal Earth - PM2.5 Exposure Cleaner (pipeline/02_clean/01_clean_pm25.py)
Source: World Bank EN.ATM.PM25.MC.M3 (Global Burden of Disease Study 2023 / IHME)
Licence: CC BY 4.0
Zero em dashes or en dashes.
"""

import os
import json
import pandas as pd

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_FILE = os.path.join(WORKSPACE_ROOT, "pipeline", "raw", "wb_pm25", "API_EN.ATM.PM25.MC.M3_DS2_en_csv_v2_648.csv")
META_COUNTRY_FILE = os.path.join(WORKSPACE_ROOT, "pipeline", "raw", "wb_pm25", "Metadata_Country_API_EN.ATM.PM25.MC.M3_DS2_en_csv_v2_648.csv")
OUT_JSON = os.path.join(WORKSPACE_ROOT, "pipeline", "clean", "pm25_cleaned.json")

def clean_pm25():
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    
    # 1. Read metadata country to get aggregate exclusion set
    meta_df = pd.read_csv(META_COUNTRY_FILE)
    aggregates = set(meta_df[meta_df['Region'].isna()]['Country Code'].dropna().str.upper())

    # 2. Read primary data
    df = pd.read_csv(RAW_FILE, skiprows=4)
    year_cols = [c for c in df.columns if str(c).strip().isdigit()]
    sorted_years = sorted([int(y) for y in year_cols])

    cleaned = {}
    excluded_aggregates = []

    for _, row in df.iterrows():
        iso3 = str(row['Country Code']).strip().upper()
        name = str(row['Country Name']).strip()

        if iso3 in aggregates:
            excluded_aggregates.append({"iso3": iso3, "name": name, "reason": "World Bank Regional/Income Aggregate"})
            continue

        # Extract time series
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

        # Compute ratio against WHO 2021 annual guideline (5 µg/m³)
        who_ratio = round(latest_val / 5.0, 2) if latest_val is not None else None

        cleaned[iso3] = {
            "iso3": iso3,
            "country_name": name,
            "latest_value": latest_val,
            "latest_year": latest_yr,
            "who_2021_multiple": who_ratio,
            "timeseries": ts,
            "unit": "µg/m³",
            "source_name": "World Bank Open Data",
            "source_dataset": "Global Burden of Disease Study 2023 (GBD 2023) / IHME",
            "source_url": "https://data.worldbank.org/indicator/EN.ATM.PM25.MC.M3",
            "license": "CC BY 4.0"
        }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2)

    print(f"[+] Cleaned PM2.5 data for {len(cleaned)} countries. Excluded {len(excluded_aggregates)} aggregates.")
    return cleaned

if __name__ == "__main__":
    clean_pm25()
