#!/usr/bin/env python3
"""
Signal Earth - Country ISO Map Expander
Expands pipeline/country_iso_map.json to cover all 177 countries in world-110m.geojson.
Zero em dashes or en dashes.
"""

import json
import os

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ISO_MAP_PATH = os.path.join(WORKSPACE_ROOT, "pipeline", "country_iso_map.json")
GEOJSON_PATH = os.path.join(WORKSPACE_ROOT, "data", "world-110m.geojson")

def expand_iso_map():
    with open(ISO_MAP_PATH, "r", encoding="utf-8") as f:
        iso_map_data = json.load(f)

    countries = iso_map_data.get("countries", {})

    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geo = json.load(f)

    for feature in geo["features"]:
        props = feature["properties"]
        iso = props.get("ISO_A3")
        if not iso or iso == "-99":
            iso = props.get("ADM0_A3") or props.get("SOV_A3")
        iso = str(iso).strip().upper()

        name = props.get("NAME") or props.get("ADMIN") or iso
        region = props.get("REGION_UN") or props.get("CONTINENT") or "Global"
        subregion = props.get("SUBREGION") or region

        # Compute centroid from bbox or geometry if not already present
        if iso not in countries:
            geom = feature.get("geometry", {})
            coords = geom.get("coordinates", [])

            # Simple centroid calculation from first outer ring
            lat, lon = 0.0, 0.0
            pts = []
            def extract_pts(c_list):
                if not c_list: return
                if isinstance(c_list[0], (int, float)):
                    pts.append(c_list)
                else:
                    for sub in c_list:
                        extract_pts(sub)
            extract_pts(coords)
            if pts:
                avg_lon = sum(p[0] for p in pts) / len(pts)
                avg_lat = sum(p[1] for p in pts) / len(pts)
                lat = round(avg_lat, 2)
                lon = round(avg_lon, 2)

            countries[iso] = {
                "iso3": iso,
                "iso2": iso[:2],
                "name": name,
                "region": region,
                "subregion": subregion,
                "capital": name,
                "coords": [lat, lon],
                "aliases": [name]
            }

    iso_map_data["metadata"]["total_canonical"] = len(countries)
    iso_map_data["countries"] = countries

    with open(ISO_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(iso_map_data, f, indent=2)

    print(f"[+] Expanded pipeline/country_iso_map.json to {len(countries)} countries.")

if __name__ == "__main__":
    expand_iso_map()
