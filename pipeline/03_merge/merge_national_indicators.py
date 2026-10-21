#!/usr/bin/env python3
"""
Signal Earth - Master Indicator Merge & Synthesis (pipeline/03_merge/merge_national_indicators.py)
Merges cleaned data from:
- pm25_cleaned.json (World Bank / GBD 2023)
- co2_cleaned.json (OWID / Global Carbon Budget 2025)
- ember_cleaned.json (Ember Global Electricity Review 2024)
- forest_cleaned.json (World Bank / FAO FRA 2024)
- epi_cleaned.json (Yale EPI 2026)
- wdi_context_cleaned.json (World Bank WDI: density, urban share, gdp per capita, land area)

Enforces:
- Merge on ISO 3166-1 alpha-3.
- Empirical rank calculation: "X of N" with N dynamically computed and ties handled via competition ranking (1224).
- Multi-year anchor detection and flagging when ranked values span differing observation years.
- Missing values preserved as null with explicit reason code, displayed as "No data" (never zero).
- Temperature and Copernicus attributions excluded.
- Kanpur, Delhi, and Landsat research isolated into india_supplement attached only to ind.json.
- Zero em dashes or en dashes throughout.
"""

import os
import sys
import json
from datetime import datetime, timezone

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CLEAN_DIR = os.path.join(WORKSPACE_ROOT, "pipeline", "clean")
LOGS_DIR = os.path.join(WORKSPACE_ROOT, "pipeline", "logs")
DATA_COUNTRY_DIR = os.path.join(WORKSPACE_ROOT, "data", "country")
ISO_MAP_PATH = os.path.join(WORKSPACE_ROOT, "pipeline", "country_iso_map.json")

def compute_competition_ranks(items, direction="highest_worst"):
    """
    Computes standard competition ranking (1, 2, 2, 4) for non-null items.
    direction:
      - 'highest_worst': highest numerical value gets rank 1 (e.g. PM2.5, CO2 total, CO2 per capita).
      - 'highest_best': highest numerical value gets rank 1 (e.g. EPI score, Renewable electricity share, Forest share).
    Returns dict: iso3 -> {'rank': int, 'total_ranked': int, 'mixed_years': bool, 'year_range': [min_yr, max_yr]}
    """
    valid_items = [it for it in items if it["val"] is not None]
    total_n = len(valid_items)
    if total_n == 0:
        return {}

    reverse_sort = True  # In both highest_worst (worst is #1) and highest_best (best is #1), highest number gets rank 1
    valid_items.sort(key=lambda x: x["val"], reverse=reverse_sort)

    # Check for mixed years
    years = sorted(list(set([it["year"] for it in valid_items if it.get("year")])))
    is_mixed = len(years) > 1
    min_yr = years[0] if years else None
    max_yr = years[-1] if years else None

    ranks_map = {}
    current_rank = 1
    for i, it in enumerate(valid_items):
        if i > 0 and it["val"] < valid_items[i - 1]["val"]:
            current_rank = i + 1
        ranks_map[it["iso3"]] = {
            "rank": current_rank,
            "total_ranked": total_n,
            "mixed_years": is_mixed,
            "years_spanned": years,
            "year_min": min_yr,
            "year_max": max_yr
        }
    return ranks_map

def merge_all():
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(DATA_COUNTRY_DIR, exist_ok=True)
    unmatched_log = os.path.join(LOGS_DIR, "unmatched_entities.log")

    # Load canonical countries
    with open(ISO_MAP_PATH, "r", encoding="utf-8") as f:
        iso_map_data = json.load(f)
    canonical_countries = iso_map_data["countries"]

    # Load cleaned datasets
    with open(os.path.join(CLEAN_DIR, "pm25_cleaned.json"), "r", encoding="utf-8") as f:
        pm25_data = json.load(f)
    with open(os.path.join(CLEAN_DIR, "co2_cleaned.json"), "r", encoding="utf-8") as f:
        co2_data = json.load(f)
    with open(os.path.join(CLEAN_DIR, "ember_cleaned.json"), "r", encoding="utf-8") as f:
        ember_data = json.load(f)
    with open(os.path.join(CLEAN_DIR, "forest_cleaned.json"), "r", encoding="utf-8") as f:
        forest_data = json.load(f)
    with open(os.path.join(CLEAN_DIR, "epi_cleaned.json"), "r", encoding="utf-8") as f:
        epi_data = json.load(f)
    with open(os.path.join(CLEAN_DIR, "wdi_context_cleaned.json"), "r", encoding="utf-8") as f:
        wdi_data = json.load(f)

    # Log unmatched entities from cleaned sources
    unmatched_records = []
    for src_name, dataset in [("pm25", pm25_data), ("co2", co2_data), ("ember", ember_data), ("forest", forest_data), ("wdi", wdi_data)]:
        for iso_code in dataset.keys():
            if iso_code not in canonical_countries:
                unmatched_records.append(f"[{src_name}] ISO {iso_code} not in canonical 48 countries registry.")
    with open(unmatched_log, "w", encoding="utf-8") as f:
        f.write("\n".join(unmatched_records) + "\n")
    print(f"[*] Logged {len(unmatched_records)} non-canonical entities to {unmatched_log}")

    # Prepare lists for empirical rank calculation
    pm25_ranks_in = []
    co2_total_ranks_in = []
    co2_cap_ranks_in = []
    renewables_ranks_in = []
    forest_ranks_in = []
    population_ranks_in = []
    epi_ranks_in = []

    for iso3 in canonical_countries.keys():
        # PM2.5
        pm_obj = pm25_data.get(iso3, {})
        pm25_ranks_in.append({"iso3": iso3, "val": pm_obj.get("latest_value"), "year": pm_obj.get("latest_year")})

        # CO2 & Population
        co2_obj = co2_data.get(iso3, {})
        c_tot = co2_obj.get("co2_total", {})
        c_cap = co2_obj.get("co2_per_capita", {})
        pop_o = co2_obj.get("population", {})
        co2_total_ranks_in.append({"iso3": iso3, "val": c_tot.get("latest_value"), "year": c_tot.get("latest_year")})
        co2_cap_ranks_in.append({"iso3": iso3, "val": c_cap.get("latest_value"), "year": c_cap.get("latest_year")})
        population_ranks_in.append({"iso3": iso3, "val": pop_o.get("latest_value"), "year": pop_o.get("latest_year")})

        # Ember Renewables
        emb_obj = ember_data.get(iso3, {})
        renewables_ranks_in.append({"iso3": iso3, "val": emb_obj.get("latest_value"), "year": emb_obj.get("latest_year")})

        # Forest Share
        fr_obj = forest_data.get(iso3, {})
        forest_ranks_in.append({"iso3": iso3, "val": fr_obj.get("latest_value"), "year": fr_obj.get("latest_year")})

        # Yale EPI 2026
        epi_obj_pre = epi_data.get(iso3, {})
        epi_ranks_in.append({"iso3": iso3, "val": epi_obj_pre.get("epi_score"), "year": 2026})

    # Compute empirical ranks
    pm25_ranks = compute_competition_ranks(pm25_ranks_in, direction="highest_worst")
    co2_tot_ranks = compute_competition_ranks(co2_total_ranks_in, direction="highest_worst")
    co2_cap_ranks = compute_competition_ranks(co2_cap_ranks_in, direction="highest_worst")
    renewables_ranks = compute_competition_ranks(renewables_ranks_in, direction="highest_best")
    forest_ranks = compute_competition_ranks(forest_ranks_in, direction="highest_best")
    population_ranks = compute_competition_ranks(population_ranks_in, direction="highest_worst")
    epi_ranks = compute_competition_ranks(epi_ranks_in, direction="highest_best")

    # Load existing India original research if present to keep thesis work pristine
    india_file = os.path.join(DATA_COUNTRY_DIR, "ind.json")
    india_supplement = []
    if os.path.exists(india_file):
        with open(india_file, "r", encoding="utf-8") as f:
            ind_old = json.load(f)
            india_supplement = ind_old.get("original_investigations", ind_old.get("india_supplement", []))

    # Now construct the comprehensive canonical document for each country
    compiled_count = 0
    for iso3, c_info in canonical_countries.items():
        fname = f"{iso3.lower()}.json"
        fpath = os.path.join(DATA_COUNTRY_DIR, fname)

        # 1. EPI Object
        epi_obj = epi_data.get(iso3, {})
        epi_score = epi_obj.get("epi_score")
        epi_rank = epi_obj.get("epi_rank")
        epi_change = epi_obj.get("ten_year_change")
        epi_reg_rank = epi_obj.get("regional_rank")
        epi_rk_info = epi_ranks.get(iso3, {})

        # 2. PM2.5 Object
        pm = pm25_data.get(iso3, {})
        pm_val = pm.get("latest_value")
        pm_yr = pm.get("latest_year")
        pm_rk_info = pm25_ranks.get(iso3, {})
        pm_ratio = pm.get("who_2021_multiple")

        if pm_val is not None:
            pm_fmt = f"{pm_val:.1f} µg/m³"
            if pm_ratio and pm_ratio > 1.0:
                pm_ctx = f"{pm_ratio:.1f}x the WHO 2021 annual guideline (5 µg/m³); annual population-weighted exposure model."
            else:
                pm_ctx = "Meets the WHO 2021 annual guideline threshold of 5 µg/m³."
            pm_reason = None
        else:
            pm_fmt = "No data"
            pm_ctx = "No validated measurement reported in the primary open database."
            pm_reason = "NOT_REPORTED"

        # 3. CO2 Total Object
        co2_c = co2_data.get(iso3, {})
        c_tot = co2_c.get("co2_total", {})
        ct_val = c_tot.get("latest_value")
        ct_yr = c_tot.get("latest_year")
        ct_rk_info = co2_tot_ranks.get(iso3, {})
        if ct_val is not None:
            ct_fmt = f"{ct_val:,.1f} Mt CO2 / yr"
            ct_ctx = "Annual territorial fossil emissions excluding land-use change."
            ct_reason = None
        else:
            ct_fmt = "No data"
            ct_ctx = "National fossil emissions unrecorded in primary dataset."
            ct_reason = "NOT_REPORTED"

        # 4. CO2 Per Capita Object
        c_cap = co2_c.get("co2_per_capita", {})
        cc_val = c_cap.get("latest_value")
        cc_yr = c_cap.get("latest_year")
        cc_rk_info = co2_cap_ranks.get(iso3, {})
        if cc_val is not None:
            cc_fmt = f"{cc_val:.2f} t CO2 / person / yr"
            cc_ctx = "Per capita fossil CO2 emissions from power, industry, transport, and heating."
            cc_reason = None
        else:
            cc_fmt = "No data"
            cc_ctx = "Per capita fossil emissions uncalculated."
            cc_reason = "NOT_REPORTED"

        # 5. Renewable Share Object
        emb = ember_data.get(iso3, {})
        emb_val = emb.get("latest_value")
        emb_yr = emb.get("latest_year")
        emb_rk_info = renewables_ranks.get(iso3, {})
        if emb_val is not None:
            emb_fmt = f"{emb_val:.1f}% of generation"
            emb_ctx = "Share of electricity generation from solar, wind, hydro, bioenergy, and other renewables."
            emb_reason = None
        else:
            emb_fmt = "No data"
            emb_ctx = "Utility grid generation data not reported in Ember long format."
            emb_reason = "TERRITORY_EXCLUDED"

        # 6. Forest Area Share Object
        frst = forest_data.get(iso3, {})
        frst_val = frst.get("latest_value")
        frst_yr = frst.get("latest_year")
        frst_rk_info = forest_ranks.get(iso3, {})
        if frst_val is not None:
            frst_fmt = f"{frst_val:.1f}% of land area"
            frst_ctx = "Land area covered under natural stands or planted trees."
            frst_reason = None
        else:
            frst_fmt = "No data"
            frst_ctx = "Forest resource assessment data unrecorded."
            frst_reason = "NOT_REPORTED"

        # 7. Population Object
        pop_c = co2_c.get("population", {})
        pop_val = pop_c.get("latest_value")
        pop_yr = pop_c.get("latest_year")
        pop_rk_info = population_ranks.get(iso3, {})
        if pop_val is not None:
            pop_fmt = f"{int(pop_val):,}"
            pop_ctx = "National resident population count."
            pop_reason = None
        else:
            pop_fmt = "No data"
            pop_ctx = "National population unrecorded."
            pop_reason = "NOT_REPORTED"

        # 8. WDI Context Object
        wdi = wdi_data.get(iso3, {})
        wdi_density = wdi.get("density", {})
        wdi_urban = wdi.get("urban_share", {})
        wdi_gdp = wdi.get("gdp_per_capita", {})
        wdi_land = wdi.get("land_area", {})

        # Context summary string (Strictly zero em/en dashes!)
        land_area_km2 = wdi_land.get("value")
        gdp_val = wdi_gdp.get("value")
        gdp_str = f"with a GDP per capita of ${int(round(gdp_val)):,}" if gdp_val else "tracked under international datasets"
        summary_text = f"National profile for {c_info['name']} ({iso3}) {gdp_str}. Evaluates ambient particulate exposure, territorial fossil emissions, renewable electricity generation, and forest cover fractions from public databases."

        country_doc = {
            "iso3": iso3,
            "name": c_info["name"],
            "official_name": c_info.get("aliases", [c_info["name"]])[0] if c_info.get("aliases") else c_info["name"],
            "region": c_info.get("region", "Unassigned"),
            "subregion": c_info.get("subregion", "Unassigned"),
            "capital": c_info.get("capital", "Not specified"),
            "coordinates": c_info.get("coords", [0.0, 0.0]),
            "land_area_km2": land_area_km2,
            "summary": summary_text,
            "data_as_of": max([y for y in [pm_yr, ct_yr, emb_yr, frst_yr, pop_yr] if y is not None], default=2024),
            "yale_epi_2026": {
                "score": epi_score,
                "rank": epi_rank,
                "total_ranked": 177,
                "ten_year_change": epi_change,
                "regional_rank": epi_reg_rank,
                "year": 2026,
                "label": "Yale EPI 2026, not a Signal Earth ranking",
                "categories": epi_obj.get("categories", {}),
                "source_name": "Yale Center for Environmental Law & Policy & CIESIN Columbia University",
                "source_url": "https://epi.yale.edu/",
                "technical_appendix_url": "https://epi.yale.edu/",
                "license": "CC BY-NC-SA 4.0",
                "disclaimer": "EPI indicator weightings and aggregation methodology are subject to academic debate; see the Yale technical appendix."
            },
            "indicators": {
                "epi_score": {
                    "key": "epi_score",
                    "name": "Yale Environmental Performance Index",
                    "value": epi_score,
                    "formatted_value": f"{epi_score:.1f}" if epi_score is not None else "No data",
                    "unit": "score (0-100)",
                    "year": 2026,
                    "rank": epi_rk_info.get("rank"),
                    "total_ranked": epi_rk_info.get("total_ranked"),
                    "global_yale_rank": epi_rank,
                    "global_yale_total": 177,
                    "mixed_years_flag": False,
                    "years_spanned": [2026],
                    "direction": "highest_best",
                    "context": f"Rank {epi_rank} of 177 globally; 10-year change: {epi_change:+.1f}." if epi_score is not None else "Not ranked in Yale EPI 2026.",
                    "missing_reason": None if epi_score is not None else "TERRITORY_EXCLUDED",
                    "timeseries": {},
                    "source_name": "Yale Center for Environmental Law & Policy & CIESIN Columbia University",
                    "source_dataset": "2026 Environmental Performance Index (EPI)",
                    "source_url": "https://epi.yale.edu/",
                    "license": "CC BY-NC-SA 4.0"
                },
                "pm25": {
                    "key": "pm25",
                    "name": "Annual Mean PM2.5 Exposure",
                    "value": pm_val,
                    "formatted_value": pm_fmt,
                    "unit": "µg/m³",
                    "year": pm_yr,
                    "rank": pm_rk_info.get("rank"),
                    "total_ranked": pm_rk_info.get("total_ranked"),
                    "mixed_years_flag": pm_rk_info.get("mixed_years", False),
                    "years_spanned": pm_rk_info.get("years_spanned", []),
                    "direction": "highest_worst",
                    "context": pm_ctx,
                    "missing_reason": pm_reason,
                    "timeseries": pm.get("timeseries", {}),
                    "source_name": "World Bank Open Data",
                    "source_dataset": "State of Global Air (SOGA) 2024 / GBD 2023 (IHME)",
                    "source_url": "https://data.worldbank.org/indicator/EN.ATM.PM25.MC.M3",
                    "license": "CC BY 4.0"
                },
                "co2_total": {
                    "key": "co2_total",
                    "name": "Total Territorial Fossil CO2",
                    "value": ct_val,
                    "formatted_value": ct_fmt,
                    "unit": "Mt CO2 / year",
                    "year": ct_yr,
                    "rank": ct_rk_info.get("rank"),
                    "total_ranked": ct_rk_info.get("total_ranked"),
                    "mixed_years_flag": ct_rk_info.get("mixed_years", False),
                    "years_spanned": ct_rk_info.get("years_spanned", []),
                    "direction": "highest_worst",
                    "context": ct_ctx,
                    "missing_reason": ct_reason,
                    "timeseries": c_tot.get("timeseries", {}),
                    "source_name": "Global Carbon Project",
                    "source_dataset": "Global Carbon Budget 2025 / ESSD",
                    "source_url": "https://globalcarbonbudget.org/",
                    "license": "CC BY 4.0"
                },
                "co2_per_capita": {
                    "key": "co2_per_capita",
                    "name": "Per Capita Fossil CO2",
                    "value": cc_val,
                    "formatted_value": cc_fmt,
                    "unit": "tonnes CO2 / person / year",
                    "year": cc_yr,
                    "rank": cc_rk_info.get("rank"),
                    "total_ranked": cc_rk_info.get("total_ranked"),
                    "mixed_years_flag": cc_rk_info.get("mixed_years", False),
                    "years_spanned": cc_rk_info.get("years_spanned", []),
                    "direction": "highest_worst",
                    "context": cc_ctx,
                    "missing_reason": cc_reason,
                    "timeseries": c_cap.get("timeseries", {}),
                    "source_name": "Global Carbon Project & UN Population Division",
                    "source_dataset": "Global Carbon Budget 2025 / UN WPP",
                    "source_url": "https://globalcarbonbudget.org/",
                    "license": "CC BY 4.0"
                },
                "renewables_share": {
                    "key": "renewables_share",
                    "name": "Renewable Share of Electricity",
                    "value": emb_val,
                    "formatted_value": emb_fmt,
                    "unit": "% of electricity generation",
                    "year": emb_yr,
                    "rank": emb_rk_info.get("rank"),
                    "total_ranked": emb_rk_info.get("total_ranked"),
                    "mixed_years_flag": emb_rk_info.get("mixed_years", False),
                    "years_spanned": emb_rk_info.get("years_spanned", []),
                    "direction": "highest_best",
                    "context": emb_ctx,
                    "missing_reason": emb_reason,
                    "timeseries": emb.get("timeseries", {}),
                    "source_name": "Ember Climate",
                    "source_dataset": "Global Electricity Review (Yearly Electricity Data)",
                    "source_url": "https://ember-climate.org/data/data-tools/data-explorer/",
                    "license": "CC BY 4.0"
                },
                "forest_share": {
                    "key": "forest_share",
                    "name": "Forest Cover Fraction",
                    "value": frst_val,
                    "formatted_value": frst_fmt,
                    "unit": "% of land area",
                    "year": frst_yr,
                    "rank": frst_rk_info.get("rank"),
                    "total_ranked": frst_rk_info.get("total_ranked"),
                    "mixed_years_flag": frst_rk_info.get("mixed_years", False),
                    "years_spanned": frst_rk_info.get("years_spanned", []),
                    "direction": "highest_best",
                    "context": frst_ctx,
                    "missing_reason": frst_reason,
                    "timeseries": frst.get("timeseries", {}),
                    "source_name": "Food and Agriculture Organization (FAO)",
                    "source_dataset": "Global Forest Resources Assessment via World Bank (AG.LND.FRST.ZS)",
                    "source_url": "https://data.worldbank.org/indicator/AG.LND.FRST.ZS",
                    "license": "CC BY 4.0"
                },
                "population": {
                    "key": "population",
                    "name": "Total Population",
                    "value": pop_val,
                    "formatted_value": pop_fmt,
                    "unit": "people",
                    "year": pop_yr,
                    "rank": pop_rk_info.get("rank"),
                    "total_ranked": pop_rk_info.get("total_ranked"),
                    "mixed_years_flag": pop_rk_info.get("mixed_years", False),
                    "years_spanned": pop_rk_info.get("years_spanned", []),
                    "direction": "highest_neutral",
                    "context": pop_ctx,
                    "missing_reason": pop_reason,
                    "timeseries": pop_c.get("timeseries", {}),
                    "source_name": "United Nations Population Division",
                    "source_dataset": "World Population Prospects (2024 Revision)",
                    "source_url": "https://population.un.org/wpp/",
                    "license": "CC BY 4.0"
                }
            },
            "wdi_context": {
                "population_density": wdi_density,
                "urban_population_share": wdi_urban,
                "gdp_per_capita": wdi_gdp,
                "land_area": wdi_land
            },
            "india_supplement": india_supplement if iso3 == "IND" else []
        }

        with open(fpath, "w", encoding="utf-8") as out:
            json.dump(country_doc, out, indent=2, ensure_ascii=False)
        compiled_count += 1

    print(f"\n[+] Master indicator merge complete! Synthesized {compiled_count} country profiles in {DATA_COUNTRY_DIR}")

if __name__ == "__main__":
    merge_all()
