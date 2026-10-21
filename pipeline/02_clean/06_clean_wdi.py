#!/usr/bin/env python3
"""
Signal Earth - WDI Context Indicators Cleaner (pipeline/02_clean/06_clean_wdi.py)
Source: World Bank World Development Indicators
- SP.POP.TOTL (Population, total)
- EN.POP.DNST (Population density, people per sq. km)
- SP.URB.TOTL.IN.ZS (Urban population % of total)
- NY.GDP.PCAP.CD (GDP per capita, current US$)
- AG.LND.TOTL.K2 (Land area, sq. km)
Licence: CC BY 4.0
Zero em dashes or en dashes.
"""

import os
import json
import glob
import pandas as pd

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_WDI_DIR = os.path.join(WORKSPACE_ROOT, "pipeline", "raw", "wb_wdi_context")
OUT_JSON = os.path.join(WORKSPACE_ROOT, "pipeline", "clean", "wdi_context_cleaned.json")

INDICATORS = {
    "population": {
        "sub": "sp.pop.totl",
        "pattern": "API_SP.POP.TOTL_DS2_en_csv_v2_",
        "unit": "people"
    },
    "density": {
        "sub": "en.pop.dnst",
        "pattern": "API_EN.POP.DNST_DS2_en_csv_v2_",
        "unit": "people / km²"
    },
    "urban_share": {
        "sub": "sp.urb.totl.in.zs",
        "pattern": "API_SP.URB.TOTL.IN.ZS_DS2_en_csv_v2_",
        "unit": "% of total population"
    },
    "gdp_per_capita": {
        "sub": "ny.gdp.pcap.cd",
        "pattern": "API_NY.GDP.PCAP.CD_DS2_en_csv_v2_",
        "unit": "current US$"
    },
    "land_area": {
        "sub": "ag.lnd.totl.k2",
        "pattern": "API_AG.LND.TOTL.K2_DS2_en_csv_v2_",
        "unit": "km²"
    }
}

def clean_wdi():
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    combined = {}

    for key, cfg in INDICATORS.items():
        sub_dir = os.path.join(RAW_WDI_DIR, cfg["sub"])
        csv_files = glob.glob(os.path.join(sub_dir, f"{cfg['pattern']}*.csv"))
        if not csv_files:
            print(f"[!] Warning: No file matching {cfg['pattern']} in {sub_dir}")
            continue

        fpath = csv_files[0]
        meta_country_files = glob.glob(os.path.join(sub_dir, "Metadata_Country_*.csv"))
        aggregates = set()
        if meta_country_files:
            meta_df = pd.read_csv(meta_country_files[0])
            aggregates = set(meta_df[meta_df['Region'].isna()]['Country Code'].dropna().str.upper())

        df = pd.read_csv(fpath, skiprows=4)
        year_cols = [c for c in df.columns if str(c).strip().isdigit()]
        sorted_years = sorted([int(y) for y in year_cols])

        for _, row in df.iterrows():
            iso3 = str(row['Country Code']).strip().upper()
            if iso3 in aggregates:
                continue

            latest_val = None
            latest_yr = None

            for y in sorted_years:
                val = row.get(str(y))
                if pd.notna(val):
                    latest_val = float(val)
                    latest_yr = y

            if iso3 not in combined:
                combined[iso3] = {
                    "iso3": iso3,
                    "country_name": str(row['Country Name']).strip(),
                    "source": "World Bank World Development Indicators",
                    "license": "CC BY 4.0"
                }

            if latest_val is not None:
                if key in ["population", "land_area"]:
                    formatted = f"{int(round(latest_val)):,}"
                elif key == "density":
                    formatted = f"{latest_val:.1f} people / km²"
                elif key == "urban_share":
                    formatted = f"{latest_val:.1f}%"
                elif key == "gdp_per_capita":
                    formatted = f"${int(round(latest_val)):,}"
                else:
                    formatted = str(latest_val)
            else:
                formatted = "No data"

            combined[iso3][key] = {
                "value": latest_val,
                "formatted_value": formatted,
                "year": latest_yr,
                "unit": cfg["unit"]
            }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)

    print(f"[+] Cleaned WDI contextual indicators for {len(combined)} countries.")
    return combined

if __name__ == "__main__":
    clean_wdi()
