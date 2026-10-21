#!/usr/bin/env python3
"""
Signal Earth - Raw Source Files Inspector (pipeline/02_clean/inspect_raw.py)
Inspects placed datasets in pipeline/raw/:
- Row count
- Year range
- Column names
- Validates data integrity, reporting missing or malformed components.
Zero em dashes.
"""

import os
import glob
import pandas as pd

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_DIR = os.path.join(WORKSPACE_ROOT, "pipeline", "raw")

def detect_year_range(df):
    """Detects year range from dataframe columns or a 'year' column."""
    years = []
    # Check if there is a 'year' or 'Year' column
    year_cols = [c for c in df.columns if str(c).strip().lower() in ("year", "years")]
    if year_cols:
        col = year_cols[0]
        numeric_years = pd.to_numeric(df[col], errors='coerce').dropna()
        if not numeric_years.empty:
            years.extend([int(numeric_years.min()), int(numeric_years.max())])
            return f"{int(numeric_years.min())} - {int(numeric_years.max())}"

    # Check if years are in the column headers (common in World Bank CSVs)
    numeric_col_years = []
    for c in df.columns:
        c_str = str(c).strip()
        if c_str.isdigit() and len(c_str) == 4:
            val = int(c_str)
            if 1950 <= val <= 2030:
                numeric_col_years.append(val)
    if numeric_col_years:
        return f"{min(numeric_col_years)} - {max(numeric_col_years)}"

    return "No year column or headers identified"

def read_flexible_csv(fpath):
    """Attempts standard CSV read or skips metadata comment lines (e.g. World Bank 4-row header)."""
    try:
        df = pd.read_csv(fpath)
        # If first column has 'Country Name' or similar, good. If not, check if row 4 is header
        if "Country Name" not in df.columns and "country" not in [c.lower() for c in df.columns]:
            # Try skiprows=4 (typical for World Bank zip/csv downloads)
            try:
                df_wb = pd.read_csv(fpath, skiprows=4)
                if "Country Name" in df_wb.columns or "Country Code" in df_wb.columns:
                    return df_wb, "Skipped 4 metadata header rows (World Bank format)"
            except Exception:
                pass
        return df, "Standard CSV header"
    except Exception as e:
        return None, str(e)

def inspect_all():
    files = glob.glob(os.path.join(RAW_DIR, "*"))
    if not files:
        print("[!] No files found in pipeline/raw/.")
        return []

    results = []
    for fpath in files:
        fname = os.path.basename(fpath)
        if not (fname.endswith(".csv") or fname.endswith(".txt") or fname.endswith(".xlsx")):
            results.append({
                "file": fname,
                "status": "Malformed / Unexpected extension",
                "rows": 0,
                "years": "N/A",
                "columns": []
            })
            continue

        df, note = read_flexible_csv(fpath)
        if df is None:
            results.append({
                "file": fname,
                "status": f"Read Error: {note}",
                "rows": 0,
                "years": "N/A",
                "columns": []
            })
            continue

        rows = len(df)
        cols = list(df.columns)
        yr_range = detect_year_range(df)

        status = "Valid"
        # Check if rows == 0
        if rows == 0:
            status = "Empty (0 rows)"

        results.append({
            "file": fname,
            "status": status,
            "format_note": note,
            "rows": rows,
            "years": yr_range,
            "columns": cols
        })
    return results

if __name__ == "__main__":
    res = inspect_all()
    for r in res:
        print(f"File: {r['file']}")
        print(f"  Status: {r['status']}")
        print(f"  Rows: {r['rows']}")
        print(f"  Year Range: {r['years']}")
        print(f"  Columns ({len(r['columns'])}): {r['columns'][:15]} {'...' if len(r['columns']) > 15 else ''}")
        print()
