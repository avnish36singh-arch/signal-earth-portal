import os
import re

ROOT_DIR = r"b:\movies\signal earth"

TARGET_NUMBERS = [
    # Kanpur winter multipliers
    "2.40", "2.93", "3.25", "3.56", "4.2", "4.99", "5.14",
    # Delhi dominant-pollutant shares
    "88.4", "11.2", "0.4", "51.8", "43.4", "95.3",
    # Landsat urban-rural delta & claims
    "3.60", "7.10", "1.0 to 2.3", "2.3 to 3.8", "3.8 °C", "3.8 K", "+3.8",
    # Delhi haze multiplier
    "5.75"
]

TARGET_FILES = [
    "index.html",
    "about.html",
    "methodology.html",
    "known-problems.html",
    "corrections.html",
    "factsheets.html",
    "compare.html",
    "research.html",
    "data/numbers_ledger.json",
    "numbers_ledger.csv",
    "analyses/kanpur/index.html",
    "analyses/delhi/index.html",
    "analyses/kanpur-lst/index.html",
    "analyses/kanpur-uhi/index.html",
    "notes/kanpur-winter-pm25-ratio-2026.html",
    "notes/delhi-naqi-particulate-dominance.html",
    "notes/kanpur-merra2-skin-temp-inversion.html",
    "notes_src/kanpur-winter-pm25-ratio-2026.md",
    "notes_src/delhi-naqi-particulate-dominance.md",
    "notes_src/kanpur-merra2-skin-temp-inversion.md"
]

results = {num: [] for num in TARGET_NUMBERS}

for rel_path in TARGET_FILES:
    full_path = os.path.join(ROOT_DIR, rel_path)
    if not os.path.exists(full_path):
        continue
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    for idx, line in enumerate(lines, 1):
        for num in TARGET_NUMBERS:
            if num in line:
                # Store match
                results[num].append((rel_path, idx, line.strip()))

for num, matches in results.items():
    print(f"=== Number: {num} (Found {len(matches)} occurrences) ===")
    for m in matches[:10]:
        print(f"  {m[0]}:L{m[1]} -> {m[2][:90]}")
    if len(matches) > 10:
        print(f"  ... and {len(matches) - 10} more.")
    print()
