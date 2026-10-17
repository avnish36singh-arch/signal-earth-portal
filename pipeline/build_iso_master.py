#!/usr/bin/env python3
"""
Compiles pipeline/country_iso_map.json with standard ISO 3166-1 alpha-3,
alpha-2, common name, region, coordinates, and common upstream aliases.
Zero em dashes.
"""

import os
import json

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ISO_MAP_PATH = os.path.join(WORKSPACE_ROOT, "pipeline", "country_iso_map.json")

# Core sovereign states registry (sample subset expanding to all sovereign nations)
COUNTRIES = [
    {"iso3": "AFG", "iso2": "AF", "name": "Afghanistan", "region": "Asia", "subregion": "Southern Asia", "capital": "Kabul", "coords": [33.9391, 67.71], "aliases": ["Afghanistan"]},
    {"iso3": "ALB", "iso2": "AL", "name": "Albania", "region": "Europe", "subregion": "Southern Europe", "capital": "Tirana", "coords": [41.1533, 20.1683], "aliases": ["Albania"]},
    {"iso3": "DZA", "iso2": "DZ", "name": "Algeria", "region": "Africa", "subregion": "Northern Africa", "capital": "Algiers", "coords": [28.0339, 1.6596], "aliases": ["Algeria"]},
    {"iso3": "AND", "iso2": "AD", "name": "Andorra", "region": "Europe", "subregion": "Southern Europe", "capital": "Andorra la Vella", "coords": [42.5063, 1.5218], "aliases": ["Andorra"]},
    {"iso3": "AGO", "iso2": "AO", "name": "Angola", "region": "Africa", "subregion": "Middle Africa", "capital": "Luanda", "coords": [-11.2027, 17.8739], "aliases": ["Angola"]},
    {"iso3": "ARG", "iso2": "AR", "name": "Argentina", "region": "Americas", "subregion": "South America", "capital": "Buenos Aires", "coords": [-38.4161, -63.6167], "aliases": ["Argentina"]},
    {"iso3": "ARM", "iso2": "AM", "name": "Armenia", "region": "Asia", "subregion": "Western Asia", "capital": "Yerevan", "coords": [40.0691, 45.0382], "aliases": ["Armenia"]},
    {"iso3": "AUS", "iso2": "AU", "name": "Australia", "region": "Oceania", "subregion": "Australia and New Zealand", "capital": "Canberra", "coords": [-25.2744, 133.7751], "aliases": ["Australia"]},
    {"iso3": "AUT", "iso2": "AT", "name": "Austria", "region": "Europe", "subregion": "Western Europe", "capital": "Vienna", "coords": [47.5162, 14.5501], "aliases": ["Austria"]},
    {"iso3": "AZE", "iso2": "AZ", "name": "Azerbaijan", "region": "Asia", "subregion": "Western Asia", "capital": "Baku", "coords": [40.1431, 47.5769], "aliases": ["Azerbaijan"]},
    {"iso3": "BGD", "iso2": "BD", "name": "Bangladesh", "region": "Asia", "subregion": "Southern Asia", "capital": "Dhaka", "coords": [23.685, 90.3563], "aliases": ["Bangladesh"]},
    {"iso3": "BEL", "iso2": "BE", "name": "Belgium", "region": "Europe", "subregion": "Western Europe", "capital": "Brussels", "coords": [50.5039, 4.4699], "aliases": ["Belgium"]},
    {"iso3": "BRA", "iso2": "BR", "name": "Brazil", "region": "Americas", "subregion": "South America", "capital": "Brasília", "coords": [-14.235, -51.9253], "aliases": ["Brazil"]},
    {"iso3": "CAN", "iso2": "CA", "name": "Canada", "region": "Americas", "subregion": "Northern America", "capital": "Ottawa", "coords": [56.1304, -106.3468], "aliases": ["Canada"]},
    {"iso3": "CHL", "iso2": "CL", "name": "Chile", "region": "Americas", "subregion": "South America", "capital": "Santiago", "coords": [-35.6751, -71.543], "aliases": ["Chile"]},
    {"iso3": "CHN", "iso2": "CN", "name": "China", "region": "Asia", "subregion": "Eastern Asia", "capital": "Beijing", "coords": [35.8617, 104.1954], "aliases": ["China", "People's Republic of China", "China (Mainland)"]},
    {"iso3": "COL", "iso2": "CO", "name": "Colombia", "region": "Americas", "subregion": "South America", "capital": "Bogotá", "coords": [4.5709, -74.2973], "aliases": ["Colombia"]},
    {"iso3": "COD", "iso2": "CD", "name": "DR Congo", "region": "Africa", "subregion": "Middle Africa", "capital": "Kinshasa", "coords": [-4.0383, 21.7587], "aliases": ["Congo, Dem. Rep.", "Democratic Republic of the Congo", "Congo, Democratic Republic of the", "Congo (Kinshasa)"]},
    {"iso3": "COG", "iso2": "CG", "name": "Congo", "region": "Africa", "subregion": "Middle Africa", "capital": "Brazzaville", "coords": [-0.228, 15.8277], "aliases": ["Congo, Rep.", "Republic of the Congo", "Congo (Brazzaville)"]},
    {"iso3": "CIV", "iso2": "CI", "name": "Cote d'Ivoire", "region": "Africa", "subregion": "Western Africa", "capital": "Yamoussoukro", "coords": [7.54, -5.5471], "aliases": ["Côte d'Ivoire", "Ivory Coast"]},
    {"iso3": "DEU", "iso2": "DE", "name": "Germany", "region": "Europe", "subregion": "Western Europe", "capital": "Berlin", "coords": [51.1657, 10.4515], "aliases": ["Germany", "Deutschland"]},
    {"iso3": "DNK", "iso2": "DK", "name": "Denmark", "region": "Europe", "subregion": "Northern Europe", "capital": "Copenhagen", "coords": [56.2639, 9.5018], "aliases": ["Denmark"]},
    {"iso3": "EGY", "iso2": "EG", "name": "Egypt", "region": "Africa", "subregion": "Northern Africa", "capital": "Cairo", "coords": [26.8206, 30.8025], "aliases": ["Egypt", "Egypt, Arab Rep."]},
    {"iso3": "ESP", "iso2": "ES", "name": "Spain", "region": "Europe", "subregion": "Southern Europe", "capital": "Madrid", "coords": [40.4637, -3.7492], "aliases": ["Spain"]},
    {"iso3": "ETH", "iso2": "ET", "name": "Ethiopia", "region": "Africa", "subregion": "Eastern Africa", "capital": "Addis Ababa", "coords": [9.145, 40.4897], "aliases": ["Ethiopia"]},
    {"iso3": "FIN", "iso2": "FI", "name": "Finland", "region": "Europe", "subregion": "Northern Europe", "capital": "Helsinki", "coords": [61.9241, 25.7482], "aliases": ["Finland"]},
    {"iso3": "FRA", "iso2": "FR", "name": "France", "region": "Europe", "subregion": "Western Europe", "capital": "Paris", "coords": [46.2276, 2.2137], "aliases": ["France"]},
    {"iso3": "GBR", "iso2": "GB", "name": "United Kingdom", "region": "Europe", "subregion": "Northern Europe", "capital": "London", "coords": [55.3781, -3.436], "aliases": ["United Kingdom", "UK", "Great Britain"]},
    {"iso3": "GHA", "iso2": "GH", "name": "Ghana", "region": "Africa", "subregion": "Western Africa", "capital": "Accra", "coords": [7.9465, -1.0232], "aliases": ["Ghana"]},
    {"iso3": "IDN", "iso2": "ID", "name": "Indonesia", "region": "Asia", "subregion": "South-Eastern Asia", "capital": "Jakarta", "coords": [-0.7893, 113.9213], "aliases": ["Indonesia"]},
    {"iso3": "IND", "iso2": "IN", "name": "India", "region": "Asia", "subregion": "Southern Asia", "capital": "New Delhi", "coords": [20.5937, 78.9629], "aliases": ["India", "Republic of India", "Bharat"]},
    {"iso3": "IRN", "iso2": "IR", "name": "Iran", "region": "Asia", "subregion": "Southern Asia", "capital": "Tehran", "coords": [32.4279, 53.688], "aliases": ["Iran, Islamic Rep.", "Iran", "Islamic Republic of Iran"]},
    {"iso3": "ITA", "iso2": "IT", "name": "Italy", "region": "Europe", "subregion": "Southern Europe", "capital": "Rome", "coords": [41.8719, 12.5674], "aliases": ["Italy"]},
    {"iso3": "JPN", "iso2": "JP", "name": "Japan", "region": "Asia", "subregion": "Eastern Asia", "capital": "Tokyo", "coords": [36.2048, 138.2529], "aliases": ["Japan"]},
    {"iso3": "KEN", "iso2": "KE", "name": "Kenya", "region": "Africa", "subregion": "Eastern Africa", "capital": "Nairobi", "coords": [-0.0236, 37.9062], "aliases": ["Kenya"]},
    {"iso3": "KOR", "iso2": "KR", "name": "South Korea", "region": "Asia", "subregion": "Eastern Asia", "capital": "Seoul", "coords": [35.9078, 127.7669], "aliases": ["Korea, Rep.", "South Korea", "Korea, Republic of"]},
    {"iso3": "MEX", "iso2": "MX", "name": "Mexico", "region": "Americas", "subregion": "North America", "capital": "Mexico City", "coords": [23.6345, -102.5528], "aliases": ["Mexico"]},
    {"iso3": "NGA", "iso2": "NG", "name": "Nigeria", "region": "Africa", "subregion": "Western Africa", "capital": "Abuja", "coords": [9.082, 8.6753], "aliases": ["Nigeria"]},
    {"iso3": "NLD", "iso2": "NL", "name": "Netherlands", "region": "Europe", "subregion": "Western Europe", "capital": "Amsterdam", "coords": [52.1326, 5.2913], "aliases": ["Netherlands"]},
    {"iso3": "NOR", "iso2": "NO", "name": "Norway", "region": "Europe", "subregion": "Northern Europe", "capital": "Oslo", "coords": [60.472, 8.4689], "aliases": ["Norway"]},
    {"iso3": "PAK", "iso2": "PK", "name": "Pakistan", "region": "Asia", "subregion": "Southern Asia", "capital": "Islamabad", "coords": [30.3753, 69.3451], "aliases": ["Pakistan"]},
    {"iso3": "RUS", "iso2": "RU", "name": "Russia", "region": "Europe", "subregion": "Eastern Europe", "capital": "Moscow", "coords": [61.524, 105.3188], "aliases": ["Russian Federation", "Russia"]},
    {"iso3": "SAU", "iso2": "SA", "name": "Saudi Arabia", "region": "Asia", "subregion": "Western Asia", "capital": "Riyadh", "coords": [23.8859, 45.0792], "aliases": ["Saudi Arabia"]},
    {"iso3": "SWE", "iso2": "SE", "name": "Sweden", "region": "Europe", "subregion": "Northern Europe", "capital": "Stockholm", "coords": [60.1282, 18.6435], "aliases": ["Sweden"]},
    {"iso3": "TUR", "iso2": "TR", "name": "Turkiye", "region": "Asia", "subregion": "Western Asia", "capital": "Ankara", "coords": [38.9637, 35.2433], "aliases": ["Turkey", "Türkiye", "Turkiye"]},
    {"iso3": "USA", "iso2": "US", "name": "United States", "region": "Americas", "subregion": "Northern America", "capital": "Washington, D.C.", "coords": [37.0902, -95.7129], "aliases": ["United States of America", "USA", "United States", "U.S."]},
    {"iso3": "VNM", "iso2": "VN", "name": "Vietnam", "region": "Asia", "subregion": "South-Eastern Asia", "capital": "Hanoi", "coords": [14.0583, 108.2772], "aliases": ["Viet Nam", "Vietnam"]},
    {"iso3": "ZAF", "iso2": "ZA", "name": "South Africa", "region": "Africa", "subregion": "Southern Africa", "capital": "Pretoria", "coords": [-30.5595, 22.9375], "aliases": ["South Africa"]}
]

def build_iso_map():
    mapping = {}
    alias_lookup = {}
    for c in COUNTRIES:
        iso3 = c["iso3"]
        mapping[iso3] = c
        for alias in c["aliases"]:
            alias_lookup[alias.lower().strip()] = iso3

    out_obj = {
        "metadata": {
            "version": "1.0",
            "standard": "ISO 3166-1 alpha-3",
            "total_canonical": len(mapping)
        },
        "countries": mapping,
        "aliases": alias_lookup
    }

    with open(ISO_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, indent=2)

    print(f"Compiled master ISO map to {ISO_MAP_PATH} with {len(mapping)} countries and {len(alias_lookup)} alias mappings.")

if __name__ == "__main__":
    build_iso_map()
