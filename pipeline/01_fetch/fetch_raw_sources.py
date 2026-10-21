#!/usr/bin/env python3
"""
Signal Earth - Raw Source Ingestion Script (pipeline/01_fetch/fetch_raw_sources.py)
Downloads and stores unmodified raw data files in pipeline/raw/<source>/
along with download timestamp, exact URL, and SHA-256 checksum.

Enforces:
- Zero em dashes or en dashes.
- Unmodified raw storage.
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
RAW_ROOT = os.path.join(WORKSPACE_ROOT, "pipeline", "raw")

SOURCES_CONFIG = [
    {
        "id": "wb_pm25",
        "name": "World Bank PM2.5 Mean Annual Exposure (EN.ATM.PM25.MC.M3)",
        "url": "https://api.worldbank.org/v2/en/indicator/EN.ATM.PM25.MC.M3?downloadformat=csv",
        "is_zip": True,
        "csv_pattern": "API_EN.ATM.PM25.MC.M3_DS2_en_csv_v2_"
    },
    {
        "id": "owid_co2",
        "name": "Our World in Data CO2 and Greenhouse Gas Dataset",
        "url": "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv",
        "is_zip": False,
        "filename": "owid-co2-data.csv",
        "codebook_url": "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-codebook.csv"
    },
    {
        "id": "ember_electricity",
        "name": "Ember Yearly Electricity Data",
        "url": "https://files.ember-energy.org/public-downloads/yearly_full_release_long_format.csv",
        "is_zip": False,
        "filename": "yearly_full_release_long_format.csv"
    },
    {
        "id": "wb_forest",
        "name": "World Bank Forest Area Share of Land Area (AG.LND.FRST.ZS)",
        "url": "https://api.worldbank.org/v2/en/indicator/AG.LND.FRST.ZS?downloadformat=csv",
        "is_zip": True,
        "csv_pattern": "API_AG.LND.FRST.ZS_DS2_en_csv_v2_"
    }
]

def compute_sha256(data_bytes):
    h = hashlib.sha256()
    h.update(data_bytes)
    return h.hexdigest()

def stream_download_to_file(url, target_path):
    req = urllib.request.Request(url, headers={"User-Agent": "SignalEarthIngest/1.0"})
    h = hashlib.sha256()
    total_bytes = 0
    with urllib.request.urlopen(req, timeout=180) as resp, open(target_path, "wb") as out:
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            out.write(chunk)
            h.update(chunk)
            total_bytes += len(chunk)
    return h.hexdigest(), total_bytes

def fetch_source(cfg):
    src_id = cfg["id"]
    dest_dir = os.path.join(RAW_ROOT, src_id)
    os.makedirs(dest_dir, exist_ok=True)
    
    url = cfg["url"]
    print(f"\n[*] Fetching {cfg['name']} from:\n    {url}")
    
    if cfg.get("is_zip"):
        zip_archive_path = os.path.join(dest_dir, "downloaded_archive.zip")
        archive_sha, total_bytes = stream_download_to_file(url, zip_archive_path)
        now_utc = datetime.now(timezone.utc).isoformat()

        # Unpack
        with zipfile.ZipFile(zip_archive_path) as z:
            z.extractall(dest_dir)
            namelist = z.namelist()

        # Find primary data CSV
        primary_csv = None
        for name in namelist:
            if cfg.get("csv_pattern") and cfg["csv_pattern"] in name:
                primary_csv = name
                break
        if not primary_csv and namelist:
            primary_csv = namelist[0]

        meta = {
            "source_id": src_id,
            "name": cfg["name"],
            "exact_url": url,
            "download_timestamp_utc": now_utc,
            "archive_filename": "downloaded_archive.zip",
            "archive_sha256": archive_sha,
            "archive_size_bytes": total_bytes,
            "unpacked_files": namelist,
            "primary_data_file": primary_csv
        }
    else:
        fn = cfg["filename"]
        target_path = os.path.join(dest_dir, fn)
        sha, total_bytes = stream_download_to_file(url, target_path)
        now_utc = datetime.now(timezone.utc).isoformat()

        codebook_meta = None
        if cfg.get("codebook_url"):
            cb_url = cfg["codebook_url"]
            print(f"[*] Fetching associated codebook from:\n    {cb_url}")
            cb_path = os.path.join(dest_dir, "owid-co2-codebook.csv")
            cb_sha, cb_bytes = stream_download_to_file(cb_url, cb_path)
            codebook_meta = {
                "filename": "owid-co2-codebook.csv",
                "exact_url": cb_url,
                "sha256": cb_sha,
                "size_bytes": cb_bytes
            }

        meta = {
            "source_id": src_id,
            "name": cfg["name"],
            "exact_url": url,
            "download_timestamp_utc": now_utc,
            "primary_data_file": fn,
            "sha256": sha,
            "size_bytes": total_bytes,
            "codebook": codebook_meta
        }

    meta_file = os.path.join(dest_dir, "metadata.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"[+] Stored unmodified in {dest_dir} (SHA256: {meta.get('sha256') or meta.get('archive_sha256')})")
    return meta

def main():
    print("=== Signal Earth Raw Source Downloader ===")
    os.makedirs(RAW_ROOT, exist_ok=True)
    manifest = []
    for cfg in SOURCES_CONFIG:
        m = fetch_source(cfg)
        manifest.append(m)
    
    summary_path = os.path.join(RAW_ROOT, "download_manifest.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\n[+] All 4 raw datasets downloaded and recorded in {summary_path}")

if __name__ == "__main__":
    main()
