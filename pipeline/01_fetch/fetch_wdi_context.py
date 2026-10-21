#!/usr/bin/env python3
"""
Signal Earth - WDI Context Ingestion Script (pipeline/01_fetch/fetch_wdi_context.py)
Downloads and stores unmodified raw data files in pipeline/raw/wb_wdi_context/
for the 5 World Bank WDI indicators:
- SP.POP.TOTL (Total population)
- EN.POP.DNST (Population density, people per sq. km)
- SP.URB.TOTL.IN.ZS (Urban population % of total)
- NY.GDP.PCAP.CD (GDP per capita, current US$)
- AG.LND.TOTL.K2 (Land area, sq. km)

Strictly enforces:
- Zero em dashes or en dashes.
- Unmodified raw storage with metadata (timestamp, exact URL, SHA256).
"""

import os
import sys
import json
import hashlib
import urllib.request
import zipfile
import io
from datetime import datetime, timezone

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_WDI_DIR = os.path.join(WORKSPACE_ROOT, "pipeline", "raw", "wb_wdi_context")

WDI_INDICATORS = [
    {"code": "SP.POP.TOTL", "name": "Population, total"},
    {"code": "EN.POP.DNST", "name": "Population density (people per sq. km)"},
    {"code": "SP.URB.TOTL.IN.ZS", "name": "Urban population (% of total)"},
    {"code": "NY.GDP.PCAP.CD", "name": "GDP per capita (current US$)"},
    {"code": "AG.LND.TOTL.K2", "name": "Land area (sq. km)"}
]

def stream_download(url, target_path):
    req = urllib.request.Request(url, headers={"User-Agent": "SignalEarthIngest/1.0"})
    h = hashlib.sha256()
    total_bytes = 0
    with urllib.request.urlopen(req, timeout=120) as resp, open(target_path, "wb") as out:
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            out.write(chunk)
            h.update(chunk)
            total_bytes += len(chunk)
    return h.hexdigest(), total_bytes

def fetch_all():
    os.makedirs(RAW_WDI_DIR, exist_ok=True)
    manifest = []

    for ind in WDI_INDICATORS:
        code = ind["code"]
        name = ind["name"]
        url = f"https://api.worldbank.org/v2/en/indicator/{code}?downloadformat=csv"
        print(f"\n[*] Fetching WDI {code} ({name})...")

        sub_dir = os.path.join(RAW_WDI_DIR, code.lower())
        os.makedirs(sub_dir, exist_ok=True)
        zip_path = os.path.join(sub_dir, "archive.zip")

        sha256, size_bytes = stream_download(url, zip_path)
        now_utc = datetime.now(timezone.utc).isoformat()

        # Unpack
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(sub_dir)
            namelist = z.namelist()

        primary_csv = None
        for n in namelist:
            if n.startswith(f"API_{code}_DS2_en_csv_v2_"):
                primary_csv = n
                break

        meta = {
            "indicator_code": code,
            "indicator_name": name,
            "exact_url": url,
            "download_timestamp_utc": now_utc,
            "archive_sha256": sha256,
            "archive_size_bytes": size_bytes,
            "primary_data_file": primary_csv,
            "unpacked_files": namelist,
            "licence": "Creative Commons Attribution 4.0 International (CC BY 4.0)"
        }

        with open(os.path.join(sub_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        manifest.append(meta)
        print(f"  [+] Unpacked {code} ({size_bytes:,} bytes, primary: {primary_csv})")

    manifest_path = os.path.join(RAW_WDI_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\n[+] WDI context ingestion complete. Saved to {manifest_path}")

if __name__ == "__main__":
    fetch_all()
