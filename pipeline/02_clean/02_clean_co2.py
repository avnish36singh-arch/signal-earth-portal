#!/usr/bin/env python3
"""
Signal Earth - CO2 & Population Cleaner (pipeline/02_clean/02_clean_co2.py)
Source: Our World in Data (Global Carbon Budget 2025 / ESSD & UN Population Division)
Licence: CC BY 4.0
Zero em dashes or en dashes.
"""

import os
import json
import pandas as pd

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_FILE = os.path.join(WORKSPACE_ROOT, "pipeline", "raw", "owid_co2", "owid-co2-data.csv")
OUT_JSON = os.path.join(WORKSPACE_ROOT, "pipeline", "clean", "co2_cleaned.json")

def clean_co2():
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    df = pd.read_csv(RAW_FILE, low_memory=False)

    # Exclude non-standard ISO entries (OWID_ prefix or null iso_code)
    valid_df = df[df['iso_code'].notna() & (~df['iso_code'].str.startswith('OWID_', na=False))]
    
    cleaned = {}
    grouped = valid_df.groupby('iso_code')

    for iso3, group in grouped:
        iso3 = iso3.strip().upper()
        country_name = group['country'].iloc[0]
        group_sorted = group.sort_values('year')

        co2_ts = {}
        co2_cap_ts = {}
        pop_ts = {}

        latest_co2 = None
        latest_co2_yr = None
        latest_cap = None
        latest_cap_yr = None
        latest_pop = None
        latest_pop_yr = None

        for _, row in group_sorted.iterrows():
            yr = int(row['year'])
            # We focus on modern period (1990 onwards) for timeseries
            if yr >= 1990:
                y_str = str(yr)
                if pd.notna(row.get('co2')):
                    v = round(float(row['co2']), 2)
                    co2_ts[y_str] = v
                    latest_co2 = v
                    latest_co2_yr = yr
                if pd.notna(row.get('co2_per_capita')):
                    v = round(float(row['co2_per_capita']), 3)
                    co2_cap_ts[y_str] = v
                    latest_cap = v
                    latest_cap_yr = yr
                if pd.notna(row.get('population')):
                    v = int(row['population'])
                    pop_ts[y_str] = v
                    latest_pop = v
                    latest_pop_yr = yr

        cleaned[iso3] = {
            "iso3": iso3,
            "country_name": country_name,
            "co2_total": {
                "latest_value": latest_co2,
                "latest_year": latest_co2_yr,
                "unit": "Mt CO2 / year",
                "timeseries": co2_ts,
                "source_name": "Global Carbon Project",
                "source_dataset": "Global Carbon Budget 2025 / ESSD",
                "source_url": "https://globalcarbonbudget.org/",
                "license": "CC BY 4.0"
            },
            "co2_per_capita": {
                "latest_value": latest_cap,
                "latest_year": latest_cap_yr,
                "unit": "tonnes CO2 / person / year",
                "timeseries": co2_cap_ts,
                "source_name": "Global Carbon Project & UN Population Division",
                "source_dataset": "Global Carbon Budget 2025 / UN WPP",
                "source_url": "https://globalcarbonbudget.org/",
                "license": "CC BY 4.0"
            },
            "population": {
                "latest_value": latest_pop,
                "latest_year": latest_pop_yr,
                "unit": "people",
                "timeseries": pop_ts,
                "source_name": "United Nations Population Division",
                "source_dataset": "World Population Prospects (2024 Revision)",
                "source_url": "https://population.un.org/wpp/",
                "license": "CC BY 4.0"
            }
        }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2)

    print(f"[+] Cleaned CO2 & Population data for {len(cleaned)} countries.")
    return cleaned

if __name__ == "__main__":
    clean_co2()
