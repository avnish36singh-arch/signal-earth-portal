#!/usr/bin/env python3
"""
Signal Earth - Ember Electricity Cleaner (pipeline/02_clean/03_clean_ember.py)
Source: Ember Global Electricity Review / Yearly Electricity Data
Licence: CC BY 4.0
Zero em dashes or en dashes.
"""

import os
import json
import pandas as pd

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_FILE = os.path.join(WORKSPACE_ROOT, "pipeline", "raw", "ember_electricity", "yearly_full_release_long_format.csv")
OUT_JSON = os.path.join(WORKSPACE_ROOT, "pipeline", "clean", "ember_cleaned.json")

def clean_ember():
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    df = pd.read_csv(RAW_FILE, low_memory=False)

    # Filter strictly for country entities
    country_df = df[df['Area type'] == 'Country or economy']
    
    # Filter for renewables share of generation:
    # Category == 'Electricity generation', Subcategory == 'Aggregate fuel', Variable == 'Renewables', Unit == '%'
    ren_df = country_df[
        (country_df['Category'] == 'Electricity generation') &
        (country_df['Subcategory'] == 'Aggregate fuel') &
        (country_df['Variable'] == 'Renewables') &
        (country_df['Unit'] == '%')
    ]

    cleaned = {}
    grouped = ren_df.groupby('ISO 3 code')

    for iso3, group in grouped:
        iso3 = str(iso3).strip().upper()
        country_name = group['Area'].iloc[0]
        group_sorted = group.sort_values('Year')

        ts = {}
        latest_val = None
        latest_yr = None

        for _, row in group_sorted.iterrows():
            yr = int(row['Year'])
            val = row['Value']
            if pd.notna(val):
                v_flt = round(float(val), 2)
                ts[str(yr)] = v_flt
                latest_val = v_flt
                latest_yr = yr

        cleaned[iso3] = {
            "iso3": iso3,
            "country_name": country_name,
            "latest_value": latest_val,
            "latest_year": latest_yr,
            "timeseries": ts,
            "unit": "% of electricity generation",
            "source_name": "Ember Climate",
            "source_dataset": "Global Electricity Review (Yearly Electricity Data)",
            "source_url": "https://ember-climate.org/data/data-tools/data-explorer/",
            "license": "CC BY 4.0"
        }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2)

    print(f"[+] Cleaned Ember renewable electricity data for {len(cleaned)} countries.")
    return cleaned

if __name__ == "__main__":
    clean_ember()
