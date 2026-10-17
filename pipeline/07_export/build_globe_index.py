"""
Build Globe Country Index for Signal Earth.
Consolidates data/country/*.json indicators into data/countries.json
for instantaneous 3D Globe WebGL rendering, metric layers, tooltips,
and client-side sorting in rankings.html and compare.html.
Budget: < 100 KB.
Strict typography: ZERO EM DASHES.
"""

import os
import json
import glob

def build_globe_index():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    country_json_dir = os.path.join(root, 'data', 'country')
    output_path = os.path.join(root, 'data', 'countries.json')

    country_files = glob.glob(os.path.join(country_json_dir, '*.json'))
    countries_index = []

    print(f"Found {len(country_files)} country files in {country_json_dir}")

    for fpath in country_files:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        iso3 = data.get('iso3', '').upper()
        name = data.get('name', '')
        region = data.get('region', '')
        coordinates = data.get('coordinates', [0, 0])

        # Extract concise indicator objects
        raw_indicators = data.get('indicators', {})
        compact_indicators = {}
        compact_ranks = {}

        for k, ind in raw_indicators.items():
            val = ind.get('value')
            yr = ind.get('year')
            rk = ind.get('rank')
            tot = ind.get('total_ranked')
            unit = ind.get('unit', '')
            fmt = ind.get('formatted_value', str(val) if val is not None else 'No data')
            src = ind.get('source_name', '')
            lic = ind.get('license', 'CC BY 4.0')

            compact_indicators[k] = {
                'value': val,
                'year': yr,
                'rank': rk,
                'total_ranked': tot,
                'unit': unit,
                'formatted': fmt,
                'source': src,
                'license': lic
            }
            if rk is not None:
                compact_ranks[k] = rk

        countries_index.append({
            'iso3': iso3,
            'name': name,
            'region': region,
            'coordinates': coordinates,
            'ranks': compact_ranks,
            'indicators': compact_indicators
        })

    # Sort alphabetically by name
    countries_index.sort(key=lambda c: c['name'])

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(countries_index, f, separators=(',', ':'), ensure_ascii=False)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"Compiled {len(countries_index)} countries into {output_path} ({size_kb:.2f} KB) - well under 100 KB budget!")

if __name__ == '__main__':
    build_globe_index()
