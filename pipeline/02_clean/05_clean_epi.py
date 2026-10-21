#!/usr/bin/env python3
"""
Signal Earth - Yale EPI 2026 Cleaner (pipeline/02_clean/05_clean_epi.py)
Source: Yale Environmental Performance Index 2026 (epi.yale.edu, CIESIN/Yale)
Licence: CC BY-NC-SA 4.0 (Non-commercial, ShareAlike)
Zero em dashes or en dashes.
"""

import os
import json
import pandas as pd

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_FILE = os.path.join(WORKSPACE_ROOT, "pipeline", "raw", "yale_epi", "yale_epi_2026_scorecard.csv")
OUT_JSON = os.path.join(WORKSPACE_ROOT, "pipeline", "clean", "epi_cleaned.json")

def clean_epi():
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    df = pd.read_csv(RAW_FILE)

    cleaned = {}

    for _, row in df.iterrows():
        iso3 = str(row['iso3']).strip().upper()
        country_name = str(row['country']).strip()

        rank_val = row.get('epi_rank')
        score_val = row.get('epi_score')
        change_val = row.get('epi_ten_year_change')
        reg_rank_val = row.get('regional_rank')

        is_ranked = pd.notna(rank_val) and pd.notna(score_val)

        rank_int = int(rank_val) if is_ranked else None
        score_flt = round(float(score_val), 2) if is_ranked else None
        change_flt = round(float(change_val), 2) if pd.notna(change_val) else None
        reg_rank_int = int(reg_rank_val) if pd.notna(reg_rank_val) else None

        cleaned[iso3] = {
            "iso3": iso3,
            "country_name": country_name,
            "epi_score": score_flt,
            "epi_rank": rank_int,
            "epi_total_ranked": 177,
            "ten_year_change": change_flt,
            "regional_rank": reg_rank_int,
            "categories": {
                "environmental_health": round(float(row['environmental_health_score']), 1) if pd.notna(row.get('environmental_health_score')) else None,
                "ecosystem_vitality": round(float(row['ecosystem_vitality_score']), 1) if pd.notna(row.get('ecosystem_vitality_score')) else None,
                "climate_change": round(float(row['climate_change_score']), 1) if pd.notna(row.get('climate_change_score')) else None
            },
            "year": 2026,
            "source_name": "Yale Center for Environmental Law & Policy & CIESIN Columbia University",
            "source_dataset": "2026 Environmental Performance Index (EPI)",
            "source_url": "https://epi.yale.edu/",
            "technical_appendix_url": "https://epi.yale.edu/",
            "license": "CC BY-NC-SA 4.0",
            "disclaimer": "EPI indicator weightings and aggregation methodology are subject to academic debate; see the Yale technical appendix."
        }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2)

    print(f"[+] Cleaned Yale EPI 2026 scorecard for {len(cleaned)} countries.")
    return cleaned

if __name__ == "__main__":
    clean_epi()
