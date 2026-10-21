#!/usr/bin/env python3
"""
Signal Earth - Pipeline Validation Suite (pipeline/05_validate/validator.py)
Enforces physical plausibility bounds, staleness checks, null reason codes,
and typography assertions (zero em-dashes).
"""

import os
import glob
import json
import sys

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_COUNTRY_DIR = os.path.join(WORKSPACE_ROOT, "data", "country")

# Physical plausibility bounds
BOUNDS = {
    "pm25": {"min": 0.0, "max": 250.0, "unit": "µg/m³"},
    "co2_total": {"min": 0.0, "max": 15000.0, "unit": "Mt CO2 / year"},
    "co2_per_capita": {"min": 0.0, "max": 80.0, "unit": "tonnes CO2 / person / year"},
    "forest_share": {"min": 0.0, "max": 100.0, "unit": "% of land area"},
    "renewables_share": {"min": 0.0, "max": 100.0, "unit": "% of electricity generation"},
}

VALID_MISSING_REASONS = {"NOT_REPORTED", "TERRITORY_EXCLUDED", "INSUFFICIENT_QUORUM"}

def validate_all():
    print("[*] Running Signal Earth automated validation suite...")
    errors = []
    warnings = []
    
    country_files = glob.glob(os.path.join(DATA_COUNTRY_DIR, "*.json"))
    if not country_files:
        errors.append("Fatal: No country JSON profiles found in data/country/")
        print_report(errors, warnings)
        sys.exit(1)

    seen_iso3 = set()

    for cpath in country_files:
        with open(cpath, "r", encoding="utf-8") as f:
            raw_text = f.read()
            cdata = json.loads(raw_text)

        iso3 = cdata.get("iso3")
        name = cdata.get("name", "Unknown")

        # Typography check: Zero em dashes or en dashes
        for char, code in [("\u2014", "em-dash"), ("\u2013", "en-dash")]:
            if char in raw_text:
                errors.append(f"Typography violation ({code}) found in {cpath}")

        # Unique ISO check
        if not iso3 or len(iso3) != 3:
            errors.append(f"Invalid ISO3 code in {cpath}: {iso3}")
        elif iso3 in seen_iso3:
            errors.append(f"Duplicate country detected: {iso3}")
        else:
            seen_iso3.add(iso3)

        # Yale EPI 2026 check
        epi = cdata.get("yale_epi_2026", {})
        if epi:
            epi_score = epi.get("score")
            if epi_score is not None:
                if not (0.0 <= epi_score <= 100.0):
                    errors.append(f"EPI score out of bounds in {iso3}: {epi_score}")
                epi_rank = epi.get("rank")
                if epi_rank is not None and not (1 <= epi_rank <= 177):
                    errors.append(f"EPI rank out of bounds in {iso3}: {epi_rank}")

        # Indicator checks
        indicators = cdata.get("indicators", {})
        for ind_key, bound in BOUNDS.items():
            ind = indicators.get(ind_key)
            if not ind:
                warnings.append(f"Missing indicator key '{ind_key}' in {iso3} ({name})")
                continue

            val = ind.get("value")
            missing_reason = ind.get("missing_reason")

            # Null check: If null, must have missing_reason or be valid null
            if val is None:
                if missing_reason and missing_reason not in VALID_MISSING_REASONS:
                    errors.append(f"Invalid missing_reason '{missing_reason}' in {iso3} for {ind_key}")
                continue

            # Physical plausibility
            try:
                numeric_val = float(val)
                if numeric_val < bound["min"] or numeric_val > bound["max"]:
                    errors.append(
                        f"Plausibility failure in {iso3} ({name}) for {ind_key}: {numeric_val} outside [{bound['min']}, {bound['max']}]"
                    )
            except (ValueError, TypeError):
                errors.append(f"Non-numeric value in {iso3} for {ind_key}: {val}")

            # Staleness check
            year = ind.get("year")
            if year and year < 2018:
                warnings.append(f"Stale indicator {ind_key} in {iso3} ({name}): year {year}")

    print_report(errors, warnings)

    if errors:
        print(f"[!] Validation FAILED with {len(errors)} error(s). Build aborted.")
        sys.exit(1)
    else:
        print(f"[+] Validation PASSED for {len(country_files)} country profile(s).")
        sys.exit(0)

def print_report(errors, warnings):
    if warnings:
        print(f"\n--- WARNINGS ({len(warnings)}) ---")
        for w in warnings[:10]:
            print(f"  [WARN] {w}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more warnings.")

    if errors:
        print(f"\n--- ERRORS ({len(errors)}) ---")
        for e in errors:
            print(f"  [ERROR] {e}")

if __name__ == "__main__":
    validate_all()
