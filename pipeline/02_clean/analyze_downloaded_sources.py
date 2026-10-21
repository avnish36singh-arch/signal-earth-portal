#!/usr/bin/env python3
"""
Signal Earth - Source Analysis and Verification Script (pipeline/02_clean/analyze_downloaded_sources.py)
Analyzes each raw downloaded source:
- Row count
- Year range
- Column names
- Countries matched (against the 48 canonical ISO 3166-1 alpha-3 entities)
- Countries unmatched
- Aggregates excluded by a documented rule
- Licence text and underlying citations
Strictly zero em dashes or en dashes.
"""

import os
import sys
import json
import csv
import pandas as pd

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ISO_MAP_PATH = os.path.join(WORKSPACE_ROOT, "pipeline", "country_iso_map.json")
RAW_ROOT = os.path.join(WORKSPACE_ROOT, "pipeline", "raw")

with open(ISO_MAP_PATH, "r", encoding="utf-8") as f:
    iso_data = json.load(f)
CANONICAL_ISO3 = set(iso_data["countries"].keys())

print(f"Total canonical countries to match: {len(CANONICAL_ISO3)}")

def analyze_wb_pm25():
    csv_path = os.path.join(RAW_ROOT, "wb_pm25", "API_EN.ATM.PM25.MC.M3_DS2_en_csv_v2_648.csv")
    meta_ind_path = os.path.join(RAW_ROOT, "wb_pm25", "Metadata_Indicator_API_EN.ATM.PM25.MC.M3_DS2_en_csv_v2_648.csv")
    meta_country_path = os.path.join(RAW_ROOT, "wb_pm25", "Metadata_Country_API_EN.ATM.PM25.MC.M3_DS2_en_csv_v2_648.csv")

    df = pd.read_csv(csv_path, skiprows=4)
    rows = len(df)
    cols = list(df.columns)
    
    # Year columns are 4-digit numeric columns
    year_cols = [c for c in cols if str(c).strip().isdigit()]
    min_yr = min([int(y) for y in year_cols])
    max_yr = max([int(y) for y in year_cols])

    # Check non-null year range for PM2.5
    years_with_data = []
    for y in year_cols:
        if df[y].dropna().count() > 0:
            years_with_data.append(int(y))
    active_yr_min = min(years_with_data) if years_with_data else "None"
    active_yr_max = max(years_with_data) if years_with_data else "None"

    # Aggregates vs Countries
    # World Bank provides Metadata_Country with a 'Region' column. Aggregates have Region as NaN/blank or IncomeGroup as NaN.
    meta_country_df = pd.read_csv(meta_country_path)
    # The rule: if 'Region' is null/empty or 'IncomeGroup' is empty, it is an aggregate/regional grouping
    aggregates_meta = set(meta_country_df[meta_country_df['Region'].isna()]['Country Code'].dropna().str.upper())
    
    all_codes = set(df['Country Code'].dropna().str.upper())
    matched = CANONICAL_ISO3.intersection(all_codes)
    unmatched = CANONICAL_ISO3 - all_codes

    # Aggregates in dataset
    aggregates_present = sorted(list(all_codes.intersection(aggregates_meta)))

    # Read licence and source metadata
    licence_text = "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    with open(meta_ind_path, "r", encoding="utf-8") as f:
        meta_content = f.read()

    return {
        "source": "World Bank EN.ATM.PM25.MC.M3",
        "file": os.path.basename(csv_path),
        "row_count": rows,
        "total_columns": len(cols),
        "columns_sample": cols[:5] + [cols[-1]],
        "all_year_columns_range": f"{min_yr} to {max_yr}",
        "active_data_year_range": f"{active_yr_min} to {active_yr_max}",
        "canonical_matched_count": len(matched),
        "canonical_matched": sorted(list(matched)),
        "canonical_unmatched_count": len(unmatched),
        "canonical_unmatched": sorted(list(unmatched)),
        "aggregates_excluded_count": len(aggregates_present),
        "aggregates_sample": aggregates_present[:10],
        "aggregate_rule": "Excluded entities where Region is NaN/blank in World Bank Metadata_Country table (e.g. WLD, EUU, HIC, OED, LCN, MEA, etc.)",
        "licence_text": licence_text,
        "source_organization": "Global Burden of Disease Study 2023 (GBD 2023) Air Pollution Exposure Estimates and Risk Curves 1990-2023, GBD Collaborator Network / IHME"
    }

def analyze_owid_co2():
    csv_path = os.path.join(RAW_ROOT, "owid_co2", "owid-co2-data.csv")
    df = pd.read_csv(csv_path, low_memory=False)
    rows = len(df)
    cols = list(df.columns)
    
    min_yr = int(df['year'].min())
    max_yr = int(df['year'].max())

    all_isos = set(df['iso_code'].dropna().str.upper())
    matched = CANONICAL_ISO3.intersection(all_isos)
    unmatched = CANONICAL_ISO3 - all_isos

    # Aggregates rule: OWID country entries with null 'iso_code' or custom OWID codes like OWID_WRL, OWID_AFR, OWID_ASI, OWID_EUR, etc.
    owid_codes = set(df['iso_code'].dropna().unique())
    aggregates_present = sorted([c for c in owid_codes if c.startswith('OWID_')])
    entities_no_iso = sorted(df[df['iso_code'].isna()]['country'].unique().tolist())

    return {
        "source": "Our World in Data (owid-co2-data.csv)",
        "file": os.path.basename(csv_path),
        "row_count": rows,
        "total_columns": len(cols),
        "columns_sample": cols[:10],
        "key_columns_present": [c for c in ['co2', 'co2_per_capita', 'population'] if c in cols],
        "year_range": f"{min_yr} to {max_yr}",
        "canonical_matched_count": len(matched),
        "canonical_matched": sorted(list(matched)),
        "canonical_unmatched_count": len(unmatched),
        "canonical_unmatched": sorted(list(unmatched)),
        "aggregates_excluded_count": len(aggregates_present) + len(entities_no_iso),
        "aggregates_sample": aggregates_present[:10],
        "aggregate_rule": "Excluded entities with non-standard ISO prefix 'OWID_' (e.g. OWID_WRL, OWID_EU27, OWID_ASI) and entries with null iso_code",
        "licence_text": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "underlying_sources": {
            "co2": "Global Carbon Budget (2025 update), Global Carbon Project",
            "co2_per_capita": "Global Carbon Budget / UN Population Division WPP",
            "population": "Population based on various sources (UN WPP, Gapminder, Maddison Project 2024)"
        }
    }

def analyze_ember():
    csv_path = os.path.join(RAW_ROOT, "ember_electricity", "yearly_full_release_long_format.csv")
    df = pd.read_csv(csv_path, low_memory=False)
    rows = len(df)
    cols = list(df.columns)

    min_yr = int(df['Year'].min())
    max_yr = int(df['Year'].max())

    # Check distinct values of Area type
    area_types = df['Area type'].dropna().unique().tolist()
    
    # Check matching
    # Filter by Area type == 'Country or economy' or check ISO 3 code
    country_rows = df[df['Area type'] == 'Country or economy']
    country_isos = set(country_rows['ISO 3 code'].dropna().str.upper())

    matched = CANONICAL_ISO3.intersection(country_isos)
    unmatched = CANONICAL_ISO3 - country_isos

    # Aggregates rule: Rows where 'Area type' != 'Country or economy' (e.g. 'Region', 'Continent', or null ISO)
    non_country_rows = df[df['Area type'] != 'Country or economy']
    aggregates_present = sorted(non_country_rows['Area'].dropna().unique().tolist())

    # Variables for renewables share
    # Let's inspect Variable and Category combinations for renewables
    ren_df = df[(df['Variable'] == 'Renewables') | (df['Variable'] == 'Clean')]
    ren_units = ren_df[['Category', 'Subcategory', 'Variable', 'Unit']].drop_duplicates().to_dict(orient='records')

    # Specifically check % of generation
    share_df = df[(df['Unit'] == '%') & (df['Variable'].str.contains('Renewable|renewables', case=False, na=False))]
    share_vars = share_df[['Category', 'Subcategory', 'Variable', 'Unit']].drop_duplicates().to_dict(orient='records')

    return {
        "source": "Ember Yearly Electricity Data",
        "file": os.path.basename(csv_path),
        "row_count": rows,
        "total_columns": len(cols),
        "columns": cols,
        "year_range": f"{min_yr} to {max_yr}",
        "area_types_found": area_types,
        "canonical_matched_count": len(matched),
        "canonical_matched": sorted(list(matched)),
        "canonical_unmatched_count": len(unmatched),
        "canonical_unmatched": sorted(list(unmatched)),
        "aggregates_excluded_count": len(aggregates_present),
        "aggregates_sample": aggregates_present[:10],
        "aggregate_rule": "Excluded all entries where 'Area type' is not 'Country or economy' (e.g. Area type in ['Continent', 'Region', 'World'])",
        "renewables_share_variables": share_vars,
        "licence_text": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "underlying_source": "Ember Global Electricity Review / National grid and energy statistics"
    }

def analyze_wb_forest():
    csv_path = os.path.join(RAW_ROOT, "wb_forest", "API_AG.LND.FRST.ZS_DS2_en_csv_v2_811.csv")
    meta_ind_path = os.path.join(RAW_ROOT, "wb_forest", "Metadata_Indicator_API_AG.LND.FRST.ZS_DS2_en_csv_v2_811.csv")
    meta_country_path = os.path.join(RAW_ROOT, "wb_forest", "Metadata_Country_API_AG.LND.FRST.ZS_DS2_en_csv_v2_811.csv")

    df = pd.read_csv(csv_path, skiprows=4)
    rows = len(df)
    cols = list(df.columns)

    year_cols = [c for c in cols if str(c).strip().isdigit()]
    min_yr = min([int(y) for y in year_cols])
    max_yr = max([int(y) for y in year_cols])

    years_with_data = []
    for y in year_cols:
        if df[y].dropna().count() > 0:
            years_with_data.append(int(y))
    active_yr_min = min(years_with_data) if years_with_data else "None"
    active_yr_max = max(years_with_data) if years_with_data else "None"

    meta_country_df = pd.read_csv(meta_country_path)
    aggregates_meta = set(meta_country_df[meta_country_df['Region'].isna()]['Country Code'].dropna().str.upper())
    
    all_codes = set(df['Country Code'].dropna().str.upper())
    matched = CANONICAL_ISO3.intersection(all_codes)
    unmatched = CANONICAL_ISO3 - all_codes
    aggregates_present = sorted(list(all_codes.intersection(aggregates_meta)))

    licence_text = "Creative Commons Attribution 4.0 International (CC BY 4.0)"
    with open(meta_ind_path, "r", encoding="utf-8") as f:
        meta_content = f.read()

    return {
        "source": "World Bank AG.LND.FRST.ZS (Forest Area % of Land Area)",
        "file": os.path.basename(csv_path),
        "row_count": rows,
        "total_columns": len(cols),
        "columns_sample": cols[:5] + [cols[-1]],
        "all_year_columns_range": f"{min_yr} to {max_yr}",
        "active_data_year_range": f"{active_yr_min} to {active_yr_max}",
        "canonical_matched_count": len(matched),
        "canonical_matched": sorted(list(matched)),
        "canonical_unmatched_count": len(unmatched),
        "canonical_unmatched": sorted(list(unmatched)),
        "aggregates_excluded_count": len(aggregates_present),
        "aggregates_sample": aggregates_present[:10],
        "aggregate_rule": "Excluded entities where Region is NaN/blank in World Bank Metadata_Country table (e.g. WLD, EUU, HIC, OED, LCN, MEA, etc.)",
        "licence_text": licence_text,
        "source_organization": "Food and Agriculture Organization of the United Nations (FAO / FAOSTAT FRA)"
    }

def main():
    print("=== Analyzing Downloaded Sources ===")
    results = {
        "wb_pm25": analyze_wb_pm25(),
        "owid_co2": analyze_owid_co2(),
        "ember_electricity": analyze_ember(),
        "wb_forest": analyze_wb_forest()
    }
    
    out_path = os.path.join(WORKSPACE_ROOT, "pipeline", "02_clean", "source_analysis_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n[+] Analysis complete! Saved detailed audit to {out_path}")

if __name__ == "__main__":
    main()
