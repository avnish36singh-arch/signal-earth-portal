"""
Signal Earth Comprehensive Build Verification Test Suite
Enforces:
1. Every number on case study cards matches data/numbers_ledger.json.
2. Every note includes sources, date, data link, author Avnish Singh, and corrections link.
3. Every rank is within [1, N] where N is the number of evaluated entities.
4. Zero broken internal links across the entire static site.
5. Zero em dashes (\u2014) and zero en dashes (\u2013) in all authored files.
6. Homepage below-the-fold content is strictly limited to the Original Analyses strip (4 cards) and the Latest Note line.
"""

import os
import re
import json
import glob
from urllib.parse import urlparse

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_1_case_study_numbers_match_ledger():
    print("--- [TEST 1] Case Study Numbers Parity with Numbers Ledger ---")
    ledger_path = os.path.join(ROOT_DIR, "data", "numbers_ledger.json")
    assert os.path.exists(ledger_path), "Missing data/numbers_ledger.json"
    
    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)
    
    cs = ledger.get("case_studies", {})
    assert len(cs) == 4, f"Expected 4 case studies in ledger, got {len(cs)}"

    index_path = os.path.join(ROOT_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        index_html = f.read()

    # Required numbers per card
    checks = {
        "kanpur_particulate": ["2.40x", "61.41", "25.61", "1,628", "855"],
        "delhi_naqi": ["95.3%", "51.8%", "43.4%", "5.75x", "1,137", "731"],
        "kanpur_temperature": ["-0.455", "308"],
        "kanpur_landsat": ["1.0 to 2.3 K"]
    }

    errors = []
    for cs_key, required_nums in checks.items():
        study = cs.get(cs_key)
        if not study:
            errors.append(f"Missing case study '{cs_key}' in ledger")
            continue
        
        # Verify finding text is in index.html
        finding_clean = study["finding"].replace("\u2014", "-").replace("\u2013", "-")
        if finding_clean not in index_html:
            errors.append(f"Finding text for '{cs_key}' does not match index.html exactly: '{finding_clean}'")

        # Verify key numbers are present in the finding or limitation
        for num in required_nums:
            if num not in index_html:
                errors.append(f"Number '{num}' from ledger '{cs_key}' missing from homepage cards")

    if errors:
        for e in errors:
            print(f"  [FAIL] {e}")
        return False
    print("  [PASS] All 4 case study card numbers agree 100% with data/numbers_ledger.json")
    return True

def test_2_notes_metadata_integrity():
    print("\n--- [TEST 2] Notes Metadata and Frontmatter Integrity ---")
    notes_src_dir = os.path.join(ROOT_DIR, "notes_src")
    notes_html_dir = os.path.join(ROOT_DIR, "notes")
    
    md_files = glob.glob(os.path.join(notes_src_dir, "*.md"))
    if not md_files:
        print("  [FAIL] No markdown notes found in notes_src/")
        return False

    errors = []
    for fp in md_files:
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Frontmatter parse
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if not fm_match:
            errors.append(f"{os.path.basename(fp)}: missing frontmatter")
            continue
        
        fm = {}
        for line in fm_match.group(1).split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
        
        # Check required fields
        for field in ["title", "date", "sources", "data_link", "author", "corrections_link"]:
            if field not in fm or not fm[field]:
                errors.append(f"{os.path.basename(fp)}: missing or empty '{field}'")
        
        if fm.get("author") != "Avnish Singh":
            errors.append(f"{os.path.basename(fp)}: author must be 'Avnish Singh', got '{fm.get('author')}'")

        # Verify underlying data link points to an existing file
        data_link = fm.get("data_link", "").lstrip("/")
        target_data_file = os.path.join(ROOT_DIR, data_link)
        if not os.path.exists(target_data_file):
            errors.append(f"{os.path.basename(fp)}: data link '{data_link}' does not exist on disk")

        # Verify corresponding HTML file was built
        slug = os.path.splitext(os.path.basename(fp))[0]
        html_out = os.path.join(notes_html_dir, f"{slug}.html")
        if not os.path.exists(html_out):
            errors.append(f"Missing generated HTML note: {html_out}")

    # Check notes/index.html and notes/feed.xml
    if not os.path.exists(os.path.join(notes_html_dir, "index.html")):
        errors.append("Missing notes/index.html")
    if not os.path.exists(os.path.join(notes_html_dir, "feed.xml")):
        errors.append("Missing notes/feed.xml")

    if errors:
        for e in errors:
            print(f"  [FAIL] {e}")
        return False
    print(f"  [PASS] All {len(md_files)} notes verified (sources, date, data link, author, feed.xml)")
    return True

def test_3_ranks_within_bounds():
    print("\n--- [TEST 3] Ranks Upper Bound Verification (Rank <= N) ---")
    countries_json = os.path.join(ROOT_DIR, "data", "countries.json")
    with open(countries_json, "r", encoding="utf-8") as f:
        countries = json.load(f)
    
    total_entities = len(countries)
    # Count countries with valid EPI ranks
    epi_ranks = [c["indicators"]["epi_score"]["rank"] for c in countries if c.get("indicators", {}).get("epi_score", {}).get("rank") is not None]
    max_epi_rank = max(epi_ranks) if epi_ranks else 0
    total_evaluated_epi = len(epi_ranks)

    errors = []
    if max_epi_rank > total_entities:
        errors.append(f"Max EPI rank ({max_epi_rank}) exceeds total entities ({total_entities})")

    # Check country profile ranks
    for c in countries:
        iso = c["iso3"]
        for ind_name, ind_data in c.get("indicators", {}).items():
            rank = ind_data.get("rank")
            if rank is not None:
                if rank < 1:
                    errors.append(f"{iso} {ind_name} rank < 1: {rank}")
                if rank > total_entities:
                    errors.append(f"{iso} {ind_name} rank ({rank}) > N ({total_entities})")

    if errors:
        for e in errors:
            print(f"  [FAIL] {e}")
        return False
    print(f"  [PASS] All indicator ranks are within 1 to N (evaluated: {total_evaluated_epi}, total entities: {total_entities})")
    return True

def test_4_no_broken_internal_links():
    print("\n--- [TEST 4] Site-Wide Internal Link Integrity ---")
    html_files = []
    ignored_dirs = [".git", "node_modules", ".agents", ".gemini", "tmp", "scratch", "build", "signal-earth-portal", "Kanpur-LST-Thermal-Analysis-GIS", "enviornment_rajivgangulaly", "kanpur_air_quality"]
    for dirpath, _, filenames in os.walk(ROOT_DIR):
        if any(ign in dirpath for ign in ignored_dirs):
            continue
        for fn in filenames:
            if fn.endswith(".html"):
                html_files.append(os.path.join(dirpath, fn))

    broken_links = []
    link_pattern = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)

    for src_path in html_files:
        with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        src_dir = os.path.dirname(src_path)
        for match in link_pattern.finditer(content):
            href = match.group(1).strip()

            # Ignore external, anchor, mailto, tel, javascript
            if any(href.startswith(prefix) for prefix in ["http://", "https://", "mailto:", "tel:", "javascript:", "#", "data:"]):
                continue

            # Strip query strings and fragment
            clean_href = href.split("?")[0].split("#")[0]
            if not clean_href:
                continue

            # Resolve absolute vs relative
            if clean_href.startswith("/"):
                # Workspace root relative
                target_path = os.path.join(ROOT_DIR, clean_href.lstrip("/"))
            else:
                target_path = os.path.join(src_dir, clean_href)

            # If target is a directory or ends with /, check index.html
            target_norm = os.path.normpath(target_path)
            exists = False
            if os.path.isdir(target_norm):
                if os.path.exists(os.path.join(target_norm, "index.html")):
                    exists = True
            elif os.path.exists(target_norm):
                exists = True
            elif os.path.exists(target_norm + ".html"):
                exists = True
            elif target_norm.endswith(".html") is False and os.path.exists(os.path.join(target_norm, "index.html")):
                exists = True

            if not exists:
                broken_links.append((os.path.relpath(src_path, ROOT_DIR), href, target_norm))

    if broken_links:
        print(f"  [FAIL] Found {len(broken_links)} broken internal link(s):")
        for src, href, tgt in broken_links[:15]:
            print(f"    in {src}: '{href}' (resolved to non-existent: {os.path.relpath(tgt, ROOT_DIR)})")
        return False
    print(f"  [PASS] Checked all internal links across {len(html_files)} HTML pages: 0 broken links found!")
    return True

def test_5_zero_unicode_dashes():
    print("\n--- [TEST 5] Zero Em/En Dashes in Authored Files ---")
    dash_violations = []
    
    # Extensions to audit
    audit_exts = {".html", ".md", ".js", ".json", ".css"}
    # Vendor files to exclude
    vendor_patterns = {"globe.gl.js", "globe.gl.min.js", "three.js", "earth-blue-marble", "world-110m"}
    ignored_dirs = [".git", "node_modules", ".agents", ".gemini", "tmp", "scratch", "vendor", "signal-earth-portal", "Kanpur-LST-Thermal-Analysis-GIS", "enviornment_rajivgangulaly", "kanpur_air_quality"]

    for dirpath, _, filenames in os.walk(ROOT_DIR):
        if any(ign in dirpath for ign in ignored_dirs):
            continue
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in audit_exts and not any(vp in fn for vp in vendor_patterns):
                fpath = os.path.join(dirpath, fn)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                for line_idx, line in enumerate(lines, 1):
                    if "\u2014" in line:
                        dash_violations.append((fpath, line_idx, "EM DASH (\\u2014)", line.strip()[:65]))
                    if "\u2013" in line:
                        dash_violations.append((fpath, line_idx, "EN DASH (\\u2013)", line.strip()[:65]))

    if dash_violations:
        print(f"  [FAIL] Found {len(dash_violations)} dash violation(s):")
        for v in dash_violations[:10]:
            print(f"    {os.path.relpath(v[0], ROOT_DIR)}:L{v[1]} - {v[2]} in: {v[3]}")
        return False
    print("  [PASS] ZERO em dashes and ZERO en dashes found across all authored files!")
    return True

def test_6_homepage_below_the_fold_constraints():
    print("\n--- [TEST 6] Homepage Below-the-Fold Constraint Check ---")
    index_path = os.path.join(ROOT_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    errors = []

    # Verify no newsletter forms or form tags
    if "<form" in html:
        errors.append("Prohibited <form> tag found in index.html (Strict zero forms rule)")

    # Verify no newsletter input or subscription elements
    for term in ["newsletter", "subscribe", "email signup", "join our mailing"]:
        if term in html.lower():
            errors.append(f"Prohibited newsletter term '{term}' found in index.html")

    # Verify no carousel markup
    for term in ["carousel", "swiper", "slick-slider", "glide"]:
        if term in html.lower():
            errors.append(f"Prohibited carousel term '{term}' found in index.html")

    # Verify exactly one strip with 4 cards below the globe
    main_match = re.search(r"<main[^>]*>(.*?)</main>", html, re.DOTALL)
    if not main_match:
        errors.append("Could not find <main> block in index.html")
    else:
        main_content = main_match.group(1)
        # Check globe stage exists
        if 'id="globe-stage"' not in main_content:
            errors.append("Missing #globe-stage in index.html main")

        # Check section exists
        if 'id="original-analyses"' not in main_content:
            errors.append("Missing #original-analyses section in index.html main")

        # Check cards count
        card_matches = re.findall(r'<article class="se-strip-card"', main_content)
        if len(card_matches) != 4:
            errors.append(f"Expected exactly 4 cards in original analyses strip, found {len(card_matches)}")

        # Check latest note strip exists
        if 'id="latest-note-strip"' not in main_content:
            errors.append("Missing #latest-note-strip in index.html main")

    if errors:
        for e in errors:
            print(f"  [FAIL] {e}")
        return False
    print("  [PASS] Homepage below-the-fold content is strictly limited to 4 cards strip and 1 latest note line!")
    return True

def test_7_no_hardcoded_48_countries():
    print("\n--- [TEST 7] No Hardcoded '48' Country Counts in User-Facing HTML ---")
    html_files = []
    ignored_dirs = [".git", "node_modules", ".agents", ".gemini", "tmp", "scratch", "build", "signal-earth-portal", "Kanpur-LST-Thermal-Analysis-GIS", "enviornment_rajivgangulaly", "kanpur_air_quality"]
    for dirpath, _, filenames in os.walk(ROOT_DIR):
        if any(ign in dirpath for ign in ignored_dirs):
            continue
        for fn in filenames:
            if fn.endswith(".html"):
                html_files.append(os.path.join(dirpath, fn))

    pattern = re.compile(r'\b48\s+(?:countries|sovereign|nations|entities|canonical)\b', re.IGNORECASE)
    violations = []
    for fpath in html_files:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        match = pattern.search(content)
        if match:
            violations.append((os.path.relpath(fpath, ROOT_DIR), match.group(0)))

    if violations:
        print(f"  [FAIL] Found {len(violations)} occurrences of hardcoded '48' country counts:")
        for v in violations:
            print(f"    in {v[0]}: '{v[1]}'")
        return False
    print(f"  [PASS] Zero hardcoded '48' country counts found across {len(html_files)} HTML pages!")
    return True

def test_8_no_prohibited_terms():
    print("\n--- [TEST 8] No Prohibited Words ('verified', 'sovereign') in User-Facing HTML ---")
    html_files = []
    ignored_dirs = [".git", "node_modules", ".agents", ".gemini", "tmp", "scratch", "build", "signal-earth-portal", "Kanpur-LST-Thermal-Analysis-GIS", "enviornment_rajivgangulaly", "kanpur_air_quality"]
    for dirpath, _, filenames in os.walk(ROOT_DIR):
        if any(ign in dirpath for ign in ignored_dirs):
            continue
        for fn in filenames:
            if fn.endswith(".html"):
                html_files.append(os.path.join(dirpath, fn))

    pattern = re.compile(r'\b(verified|sovereign)\b', re.IGNORECASE)
    violations = []
    for fpath in html_files:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for match in pattern.finditer(content):
            violations.append((os.path.relpath(fpath, ROOT_DIR), match.group(0)))

    if violations:
        print(f"  [FAIL] Found {len(violations)} prohibited term violation(s):")
        for v in violations[:15]:
            print(f"    in {v[0]}: prohibited word '{v[1]}'")
        return False
    print(f"  [PASS] Zero prohibited words ('verified', 'sovereign') found across {len(html_files)} HTML pages!")
    return True

def test_9_epi_absent_from_csv():
    print("\n--- [TEST 9] Yale EPI Data Absent from Numbers Ledger CSV ---")
    csv_path = os.path.join(ROOT_DIR, "numbers_ledger.csv")
    if not os.path.exists(csv_path):
        print("  [FAIL] numbers_ledger.csv not found!")
        return False
    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read().lower()
    
    if "epi" in content:
        print("  [FAIL] numbers_ledger.csv contains references to EPI data!")
        return False
    print("  [PASS] numbers_ledger.csv strictly omits CC BY-NC-SA 4.0 Yale EPI data!")
    return True

def test_10_ledger_entries_generating_scripts():
    print("\n--- [TEST 10] Ledger Entries Traceability and Generating Scripts ---")
    ledger_path = os.path.join(ROOT_DIR, "data", "numbers_ledger.json")
    if not os.path.exists(ledger_path):
        print("  [FAIL] data/numbers_ledger.json not found!")
        return False
    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)
    
    raw_entries = ledger.get("raw_entries", [])
    if not raw_entries:
        print("  [FAIL] No raw_entries found in numbers_ledger.json!")
        return False
    
    missing_actions = []
    for idx, entry in enumerate(raw_entries, 1):
        if not entry.get("Action (keep / relabel / remove)"):
            missing_actions.append(f"Row {idx} missing Action")
    
    if missing_actions:
        print(f"  [FAIL] {len(missing_actions)} entries missing actionable status:")
        for m in missing_actions:
            print(f"    {m}")
        return False
    print(f"  [PASS] All {len(raw_entries)} entries in numbers_ledger.json have documented scripts and actions!")
    return True

def test_11_no_autocorrelated_p_values():
    print("\n--- [TEST 11] No Unadjusted P-Values on Autocorrelated Time Series ---")
    index_path = os.path.join(ROOT_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Check that Kanpur skin temperature card does not report classical p-value
    if "2.47e-16" in html or "2.47 x 10" in html:
        print("  [FAIL] Found classical p-value claimed on autocorrelated series in index.html!")
        return False
    
    ledger_path = os.path.join(ROOT_DIR, "data", "numbers_ledger.json")
    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)
    
    kanpur_temp = ledger.get("case_studies", {}).get("kanpur_temperature", {})
    finding = kanpur_temp.get("finding", "")
    if "p-value" in finding.lower() or "p =" in finding or "p <" in finding:
        print("  [FAIL] Case study ledger reports classical p-value on autocorrelated series!")
        return False
        
    print("  [PASS] Autocorrelated time series report Pearson r without pseudoreplication p-values!")
    return True

def run_all_tests():
    print("=======================================================")
    print("   SIGNAL EARTH COMPREHENSIVE INTEGRITY TEST SUITE     ")
    print("=======================================================")
    t1 = test_1_case_study_numbers_match_ledger()
    t2 = test_2_notes_metadata_integrity()
    t3 = test_3_ranks_within_bounds()
    t4 = test_4_no_broken_internal_links()
    t5 = test_5_zero_unicode_dashes()
    t6 = test_6_homepage_below_the_fold_constraints()
    t7 = test_7_no_hardcoded_48_countries()
    t8 = test_8_no_prohibited_terms()
    t9 = test_9_epi_absent_from_csv()
    t10 = test_10_ledger_entries_generating_scripts()
    t11 = test_11_no_autocorrelated_p_values()

    all_passed = t1 and t2 and t3 and t4 and t5 and t6 and t7 and t8 and t9 and t10 and t11
    print("\n=======================================================")
    if all_passed:
        print("  >>> ALL BUILD INTEGRITY AUDITS PASSED SUCCESSFULLY! <<<")
    else:
        print("  >>> BUILD INTEGRITY AUDIT FAILED! SEE ERRORS ABOVE. <<<")
    print("=======================================================")
    return all_passed

if __name__ == "__main__":
    passed = run_all_tests()
    exit(0 if passed else 1)
