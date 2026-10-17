#!/usr/bin/env python3
"""
Seeds canonical country profiles in data/country/ based on pipeline/country_iso_map.json.
Leaves existing files (e.g. ind.json) completely unmodified.
Strictly adheres to:
- Missing data presented as null / "No data", never zero or synthetic.
- Zero em dashes.
"""

import os
import json

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ISO_MAP_PATH = os.path.join(WORKSPACE_ROOT, "pipeline", "country_iso_map.json")
DATA_COUNTRY_DIR = os.path.join(WORKSPACE_ROOT, "data", "country")

INDICATOR_DEFAULTS = [
    {
        "key": "pm25",
        "name": "Annual Mean PM2.5 Exposure",
        "unit": "µg/m³",
        "direction": "highest_worst",
        "source_name": "Health Effects Institute & IHME",
        "source_dataset": "State of Global Air (SOGA) 2024 / Global Burden of Disease",
        "source_url": "https://www.stateofglobalair.org/",
        "license": "CC BY 4.0"
    },
    {
        "key": "temp_anomaly",
        "name": "Surface Temperature Anomaly",
        "unit": "°C",
        "direction": "highest_worst",
        "source_name": "Berkeley Earth",
        "source_dataset": "BEST Country Temperature Series (2024 update)",
        "source_url": "https://berkeleyearth.org/data/",
        "license": "CC BY 4.0"
    },
    {
        "key": "temp_trend",
        "name": "30-Year Warming Trend Rate",
        "unit": "°C / decade",
        "direction": "highest_worst",
        "source_name": "Berkeley Earth",
        "source_dataset": "BEST Regional Linear Climatology",
        "source_url": "https://berkeleyearth.org/data/",
        "license": "CC BY 4.0"
    },
    {
        "key": "co2_total",
        "name": "Total Territorial CO2 Emissions",
        "unit": "MtCO2",
        "direction": "highest_worst",
        "source_name": "Global Carbon Project",
        "source_dataset": "Global Carbon Budget 2024",
        "source_url": "https://globalcarbonbudget.org/",
        "license": "CC BY 4.0"
    },
    {
        "key": "co2_per_capita",
        "name": "Per Capita CO2 Emissions",
        "unit": "tCO2 / person",
        "direction": "highest_worst",
        "source_name": "Global Carbon Project & UN WPP",
        "source_dataset": "Global Carbon Budget 2024 / UN Population Division",
        "source_url": "https://globalcarbonbudget.org/",
        "license": "CC BY 4.0"
    },
    {
        "key": "forest_share",
        "name": "Forest Cover Share of Land Area",
        "unit": "%",
        "direction": "highest_best",
        "source_name": "FAO & World Bank",
        "source_dataset": "Global Forest Resources Assessment / WDI (AG.LND.FRST.ZS)",
        "source_url": "https://www.fao.org/forest-resources-assessment/",
        "license": "CC BY 4.0"
    },
    {
        "key": "renewables_share",
        "name": "Renewable Electricity Share",
        "unit": "%",
        "direction": "highest_best",
        "source_name": "Ember",
        "source_dataset": "Yearly Electricity Data (May 2024)",
        "source_url": "https://ember-climate.org/data/data-tools/data-explorer/",
        "license": "CC BY 4.0"
    },
    {
        "key": "population",
        "name": "National Population",
        "unit": "people",
        "direction": "contextual",
        "source_name": "United Nations Population Division",
        "source_dataset": "World Population Prospects 2024 Revision",
        "source_url": "https://population.un.org/wpp/",
        "license": "CC BY 3.0 IGO"
    }
]

def seed_countries():
    if not os.path.exists(ISO_MAP_PATH):
        print(f"ISO map not found at {ISO_MAP_PATH}")
        return

    with open(ISO_MAP_PATH, "r", encoding="utf-8") as f:
        iso_data = json.load(f)

    countries = iso_data.get("countries", {})
    created_count = 0

    for iso3, info in countries.items():
        fname = f"{iso3.lower()}.json"
        fpath = os.path.join(DATA_COUNTRY_DIR, fname)
        if os.path.exists(fpath):
            # Already exists (e.g. ind.json)
            continue

        name = info.get("name", iso3)
        region = info.get("region", "")
        subregion = info.get("subregion", "")
        capital = info.get("capital", "")
        coords = info.get("coords", [0.0, 0.0])

        indicators_obj = {}
        for item in INDICATOR_DEFAULTS:
            k = item["key"]
            indicators_obj[k] = {
                "key": k,
                "name": item["name"],
                "value": None,
                "formatted_value": None,
                "unit": item["unit"],
                "year": None,
                "rank": None,
                "total_ranked": None,
                "direction": item["direction"],
                "context": "Awaiting raw dataset pipeline ingestion.",
                "source_name": item["source_name"],
                "source_dataset": item["source_dataset"],
                "source_url": item["source_url"],
                "license": item["license"]
            }

        country_doc = {
            "iso3": iso3.upper(),
            "name": name,
            "official_name": name,
            "region": region,
            "subregion": subregion,
            "capital": capital,
            "coordinates": coords,
            "land_area_km2": None,
            "summary": f"National profile for {name} ({iso3.upper()}) tracking comparative environmental indicators, atmospheric particulates, surface warming anomalies, and energy transition data.",
            "indicators": indicators_obj,
            "original_investigations": []
        }

        with open(fpath, "w", encoding="utf-8") as out:
            json.dump(country_doc, out, indent=2)
        created_count += 1

    print(f"Seeded {created_count} canonical country profile documents in {DATA_COUNTRY_DIR}")

if __name__ == "__main__":
    seed_countries()
