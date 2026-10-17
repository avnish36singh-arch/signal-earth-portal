#!/usr/bin/env python3
"""
Signal Earth - Main Pipeline Orchestrator (pipeline/run_pipeline.py)
Provides a single deterministic command to validate, compile, and build
all static data assets and country pages.
Zero em dashes.
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime, timezone

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VALIDATOR_SCRIPT = os.path.join(WORKSPACE_ROOT, "pipeline", "05_validate", "validator.py")
BUILDER_SCRIPT = os.path.join(WORKSPACE_ROOT, "build", "build_countries.py")
REPORTS_DIR = os.path.join(WORKSPACE_ROOT, "pipeline", "reports")

def run_step(cmd, desc):
    print(f"\n=======================================================")
    print(f"STEP: {desc}")
    print(f"COMMAND: {cmd}")
    print(f"=======================================================")
    res = subprocess.run(cmd, shell=True, cwd=WORKSPACE_ROOT)
    if res.returncode != 0:
        print(f"[!] Step failed with exit code {res.returncode}: {desc}")
        sys.exit(res.returncode)
    print(f"[+] Step succeeded: {desc}")

def main():
    parser = argparse.ArgumentParser(description="Signal Earth Data & Build Pipeline")
    parser.add_argument("--all", action="store_true", help="Run full validation and build pipeline")
    parser.add_argument("--validate", action="store_true", help="Run validation assertions only")
    parser.add_argument("--build", action="store_true", help="Run static country page build only")
    args = parser.parse_args()

    # Default to --all if no arguments provided
    if not (args.validate or args.build or args.all):
        args.all = True

    start_time = datetime.now(timezone.utc)
    print(f"[*] Starting Signal Earth pipeline run at {start_time.isoformat()}...")

    if args.validate or args.all:
        run_step(f"python \"{VALIDATOR_SCRIPT}\"", "Data Model & Plausibility Validation")

    if args.build or args.all:
        run_step(f"python \"{BUILDER_SCRIPT}\"", "Static Country HTML Page Generation")

    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    print(f"\n[+] Pipeline run completed successfully in {duration:.2f} seconds.")

    # Record log
    os.makedirs(REPORTS_DIR, exist_ok=True)
    log_file = os.path.join(REPORTS_DIR, "last_run.log")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Pipeline Run: SUCCESS\nTimestamp (UTC): {datetime.now(timezone.utc).isoformat()}\nDuration: {duration:.2f}s\n")

if __name__ == "__main__":
    main()
