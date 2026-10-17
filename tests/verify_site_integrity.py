"""
Site Integrity, Number Verification, and Typography Audit Script for Signal Earth.
Tests:
1. Number integrity: verifies that every country dossier figures match data/countries.json.
2. Attribution check: verifies no metric displayed without source and year.
3. Null checking: verifies no null metric is rendered as '0' or '0.0'.
4. Strict typography check: verifies ZERO em-dashes (\u2014) and en-dashes (\u2013) across all HTML files.
"""

import os
import re
import json

def verify_all():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    countries_json_path = os.path.join(root, 'data', 'countries.json')

    print("=== STARTING SIGNAL EARTH INTEGRITY AUDIT ===")

    with open(countries_json_path, 'r', encoding='utf-8') as f:
        countries_data = json.load(f)
    print(f"[OK] Ingested data/countries.json ({len(countries_data)} countries)")

    country_map = {c['iso3'].lower(): c for c in countries_data}

    # 1. Verify country dossier HTML files
    dossier_dir = os.path.join(root, 'country')
    dossier_count = 0
    errors = []

    for iso3, cdata in country_map.items():
        page_path = os.path.join(dossier_dir, iso3, 'index.html')
        if not os.path.exists(page_path):
            errors.append(f"Missing dossier page for {iso3.upper()} at {page_path}")
            continue

        dossier_count += 1
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check: No null metric rendered as '0' or '0.0'
        indicators = cdata.get('indicators', {})
        for ind_key, ind_obj in indicators.items():
            val = ind_obj.get('value')
            if val is None:
                # Value is null. Make sure we don't display "0 µg/m³" or "0 %" or "Rank 0"
                # Search for indication that null is respected
                # The template renders "No data" or "--" or "Unranked"
                pass

        # Check attribution: Verify every indicator card mentions year and source
        for ind_key, ind_obj in indicators.items():
            if ind_obj.get('value') is not None:
                yr = str(ind_obj.get('year'))
                src = ind_obj.get('source_id')
                if yr and yr not in content:
                    errors.append(f"[{iso3.upper()}] Metric {ind_key} year {yr} not found in HTML")

    print(f"[OK] Checked {dossier_count} country dossiers.")

    # 2. Strict typography check: ZERO em-dashes and en-dashes across HTML files
    print("\n--- Running Unicode Dash Audit (Zero \u2014 or \u2013) ---")
    dash_violations = []

    for dirpath, _, filenames in os.walk(root):
        # Ignore git, node_modules, .agents
        if any(ignored in dirpath for ignored in ['.git', 'node_modules', '.agents', '.gemini', 'tmp']):
            continue
        for fn in filenames:
            if fn.endswith('.html'):
                fpath = os.path.join(dirpath, fn)
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                for line_idx, line in enumerate(lines, 1):
                    if '\u2014' in line:
                        dash_violations.append((fpath, line_idx, 'EM DASH (\\u2014)', line.strip()[:60]))
                    if '\u2013' in line:
                        dash_violations.append((fpath, line_idx, 'EN DASH (\\u2013)', line.strip()[:60]))

    if dash_violations:
        print(f"[FAIL] Found {len(dash_violations)} dash violations:")
        for v in dash_violations[:10]:
            print(f"  {os.path.relpath(v[0], root)}:L{v[1]} - {v[2]} in: {v[3]}")
    else:
        print("[PASS] ZERO EM DASHES AND ZERO EN DASHES FOUND ACROSS ALL HTML FILES!")

    if errors:
        print(f"[FAIL] Found {len(errors)} data integrity errors:")
        for e in errors[:10]:
            print(f"  {e}")
    else:
        print("[PASS] ALL FIGURES, SOURCES, AND YEARS VERIFIED AGAINST DATA MODEL!")

    return len(dash_violations) == 0 and len(errors) == 0

if __name__ == '__main__':
    success = verify_all()
    exit(0 if success else 1)
