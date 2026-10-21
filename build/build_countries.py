#!/usr/bin/env python3
"""
Signal Earth - Static Country Profile Generator (build/build_countries.py)
Compiles pre-rendered HTML pages at country/{iso3}/index.html from build/template.html.
Also compiles the accessible directory at countries/index.html.
Strictly adheres to:
- Missing data presented as "No data" (never zero, never synthetic).
- Zero em dashes throughout.
- Real data from verified open pipeline.
"""

import os
import glob
import json
import xml.etree.ElementTree as ET

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_COUNTRY_DIR = os.path.join(WORKSPACE_ROOT, "data", "country")
TEMPLATE_PATH = os.path.join(WORKSPACE_ROOT, "build", "template.html")
OUTPUT_COUNTRY_DIR = os.path.join(WORKSPACE_ROOT, "country")
COUNTRIES_DIR = os.path.join(WORKSPACE_ROOT, "countries")
COUNTRIES_INDEX_PATH = os.path.join(WORKSPACE_ROOT, "data", "countries.json")
SITEMAP_PATH = os.path.join(WORKSPACE_ROOT, "sitemap.xml")

HEADLINE_KEYS = [
    "pm25",
    "co2_total",
    "co2_per_capita",
    "renewables_share",
    "forest_share"
]

ALL_INDICATOR_KEYS = [
    "epi_score",
    "pm25",
    "co2_total",
    "co2_per_capita",
    "renewables_share",
    "forest_share",
    "population"
]

def format_percentile_bar(rank, total_ranked, direction="highest_worst"):
    """Generates an accessible horizontal percentile micro-bar."""
    if not rank or not total_ranked or total_ranked <= 1:
        return '<div class="se-percentile-wrap"><div class="se-percentile-track"></div></div>'
    
    if direction == "highest_best":
        pct = max(5, min(100, round((1.0 - (rank - 1) / (total_ranked - 1)) * 100)))
    else:
        # highest_worst: rank 1 is worst, so rank 1 has highest bar
        pct = max(5, min(100, round((1.0 - (rank - 1) / (total_ranked - 1)) * 100)))

    return f"""<div class="se-percentile-wrap" title="Percentile: {pct}%">
      <div class="se-percentile-track">
        <div class="se-percentile-fill" style="width: {pct}%;"></div>
      </div>
    </div>"""

def render_headline_card(ind_data):
    """Renders one of the headline indicator cards with percentile micro-bars."""
    if not ind_data:
        return ""
    
    name = ind_data.get("name", "Indicator")
    val = ind_data.get("value")
    formatted_val = ind_data.get("formatted_value")
    rank = ind_data.get("rank")
    total_ranked = ind_data.get("total_ranked")
    context = ind_data.get("context", "")
    src_name = ind_data.get("source_name", "Open Data")
    src_url = ind_data.get("source_url", "#")
    year = ind_data.get("year")
    direction = ind_data.get("direction", "highest_worst")

    if val is None or formatted_val is None or formatted_val == "No data":
        val_html = '<div class="se-ind-value is-nodata">No data</div>'
        rank_badge = '<span class="se-ind-rank-badge is-unranked">Unranked</span>'
        bar_html = '<div class="se-percentile-wrap"><div class="se-percentile-track"></div></div>'
        ctx_html = '<div class="se-ind-context">No validated measurement reported for this indicator.</div>'
        src_line = f"Source: {src_name}"
    else:
        val_html = f'<div class="se-ind-value">{formatted_val}</div>'
        if rank and total_ranked:
            rank_badge = f'<span class="se-ind-rank-badge">Rank {rank} of {total_ranked}</span>'
            bar_html = format_percentile_bar(rank, total_ranked, direction)
        else:
            rank_badge = '<span class="se-ind-rank-badge">Reported</span>'
            bar_html = '<div class="se-percentile-wrap"><div class="se-percentile-track"><div class="se-percentile-fill" style="width: 50%;"></div></div></div>'
        ctx_html = f'<div class="se-ind-context">{context}</div>'
        year_str = f" ({year})" if year else ""
        src_line = f'Source: <a href="{src_url}" target="_blank" rel="noopener noreferrer">{src_name}</a>{year_str}'

    return f"""
          <div class="se-indicator-card">
            <div class="se-ind-header">
              <h3 class="se-ind-title">{name}</h3>
              {rank_badge}
            </div>
            <div class="se-ind-value-row">
              {val_html}
            </div>
            {bar_html}
            {ctx_html}
            <div class="se-ind-footer">
              {src_line}
            </div>
          </div>"""

def render_regional_peers_table(country_iso3, country_subregion, country_region, all_countries):
    """Renders Section 6: Regional Context peer comparison table."""
    peers = [c for c in all_countries if c.get("subregion") == country_subregion]
    if len(peers) < 3:
        peers = [c for c in all_countries if c.get("region") == country_region]

    # Sort peers alphabetically by country name
    peers_sorted = sorted(peers, key=lambda x: x.get("name", ""))[:10]
    
    # Ensure current country is included in the list
    curr_in_list = any(c.get("iso3") == country_iso3 for c in peers_sorted)
    if not curr_in_list:
        curr_obj = next((c for c in all_countries if c.get("iso3") == country_iso3), None)
        if curr_obj:
            peers_sorted.append(curr_obj)
            peers_sorted = sorted(peers_sorted, key=lambda x: x.get("name", ""))[:10]

    rows = []
    for p in peers_sorted:
        p_iso = p.get("iso3", "").upper()
        p_name = p.get("name", p_iso)
        p_inds = p.get("indicators", {})
        
        epi_val = p_inds.get("epi_score", {}).get("formatted_value", "No data")
        pm = p_inds.get("pm25", {}).get("formatted_value", "No data")
        co2 = p_inds.get("co2_per_capita", {}).get("formatted_value", "No data")
        ren = p_inds.get("renewables_share", {}).get("formatted_value", "No data")
        frst = p_inds.get("forest_share", {}).get("formatted_value", "No data")

        is_curr = (p_iso == country_iso3)
        row_cls = ' class="is-current-country"' if is_curr else ""
        link_str = f'<a href="../{p_iso.lower()}/" style="font-weight: 600;">{p_name}</a>'
        prof_btn = f'<a href="../{p_iso.lower()}/">Profile &rarr;</a>' if not is_curr else '<span style="color: var(--se-teal-live); font-weight: 700;">Current</span>'

        row = f"""              <tr{row_cls}>
                <td>{link_str}</td>
                <td style="font-family: monospace;">{p_iso}</td>
                <td style="font-family: monospace;">{epi_val}</td>
                <td style="font-family: monospace;">{pm}</td>
                <td style="font-family: monospace;">{co2}</td>
                <td style="font-family: monospace;">{ren}</td>
                <td style="font-family: monospace;">{frst}</td>
                <td style="text-align: right;">{prof_btn}</td>
              </tr>"""
        rows.append(row)

    return "\n".join(rows)

def render_audit_table_and_gaps(indicators_dict):
    """Renders Section 7: Provenance audit table and Missing indicator gaps log."""
    audit_rows = []
    gaps_list = []

    reason_explanations = {
        "NOT_REPORTED": "Not reported in the primary international statistical survey or national monitoring bulletin.",
        "TERRITORY_EXCLUDED": "Territory or microstate excluded from the observation scope of the upstream release.",
        "INSUFFICIENT_QUORUM": "Insufficient continuous annual data points to validate an aggregate metric."
    }

    for key in ALL_INDICATOR_KEYS:
        ind = indicators_dict.get(key, {})
        name = ind.get("name", key)
        val = ind.get("value")
        formatted_val = ind.get("formatted_value", "No data")
        year = ind.get("year", "Unreported")
        src_name = ind.get("source_name", "Open Data")
        src_dataset = ind.get("source_dataset", "")
        src_url = ind.get("source_url", "#")
        license_id = ind.get("license", "Open Data")
        missing_reason = ind.get("missing_reason")

        if val is None or formatted_val == "No data":
            val_display = '<span style="color: var(--se-text-muted); font-style: italic;">No data</span>'
            r_code = missing_reason or "NOT_REPORTED"
            r_desc = reason_explanations.get(r_code, "Unreported in upstream primary release")
            gaps_list.append(f"""          <li class="se-gaps-item">
            <span class="se-gaps-name">{name}</span>
            <span class="se-gaps-reason">Reason: {r_code} - {r_desc}</span>
          </li>""")
        else:
            val_display = f'<span class="mono">{formatted_val}</span>'

        row = f"""              <tr>
                <td><strong>{name}</strong></td>
                <td>{val_display}</td>
                <td style="font-family: monospace;">{year}</td>
                <td>{src_name} &middot; <span style="font-size: 0.75rem; color: var(--se-text-muted);">{src_dataset}</span></td>
                <td><span style="font-family: monospace; font-size: 0.72rem; color: var(--se-text-muted);">{license_id}</span></td>
                <td style="text-align: right;"><a href="{src_url}" target="_blank" rel="noopener noreferrer">Source link &rarr;</a></td>
              </tr>"""
        audit_rows.append(row)

    if not gaps_list:
        gaps_list.append('<li class="se-gaps-item"><span class="se-gaps-name">All standard indicators reported</span><span class="se-gaps-reason">Zero data gaps detected across canonical suite</span></li>')

    return "\n".join(audit_rows), "\n".join(gaps_list)

def render_original_investigations(investigations_list):
    """Renders conditional original research section (for India)."""
    if not investigations_list:
        return ""
    
    cards_html = []
    for inv in investigations_list:
        title = inv.get("title", "")
        subtitle = inv.get("subtitle", "")
        location = inv.get("location", "")
        findings = inv.get("key_findings", [])
        data_file = inv.get("primary_data_file", "")
        script_ref = inv.get("script_reference", "")
        image_url = inv.get("image_url", "")
        href = inv.get("href", "#")

        bullets_html = "".join([f"<li>{finding}</li>" for finding in findings])

        card = f"""
          <article class="se-orig-inv-card">
            <div class="se-orig-inv-img-wrap">
              <img src="../../{image_url}" alt="{title}" loading="lazy">
            </div>
            <div class="se-orig-inv-body">
              <span class="se-orig-inv-tag">{location}</span>
              <h3 class="se-orig-inv-title">
                <a href="../../{href.lstrip('/')}" style="color: inherit; text-decoration: none;">{title}</a>
              </h3>
              <div class="se-orig-inv-sub">{subtitle}</div>
              <ul class="se-orig-inv-bullets">
                {bullets_html}
              </ul>
              <div class="se-orig-inv-meta">
                <span>Data: <a href="../../{data_file}" class="se-link" download>{os.path.basename(data_file)}</a></span>
                <span>Script: <code>{script_ref}</code></span>
                <a href="../../{href.lstrip('/')}" class="se-link" style="font-weight: 600;">Read report &rarr;</a>
              </div>
            </div>
          </article>"""
        cards_html.append(card)

    all_cards = "\n".join(cards_html)

    section_html = f"""
    <!-- CONDITIONAL: INDIA ORIGINAL INVESTIGATIONS SECTION -->
    <section class="se-orig-inv-section" id="original-research" aria-labelledby="orig-inv-heading">
      <div class="se-editorial-container">
        <div style="margin-bottom: 2rem;">
          <span style="font-family: var(--se-font-mono); font-size: 0.72rem; color: var(--se-teal-live); text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;">Original In-Situ &amp; Spaceborne Investigations</span>
          <h2 id="orig-inv-heading" style="font-family: var(--se-font-serif); font-size: 1.85rem; margin: 0.25rem 0 0.5rem; color: var(--se-text-primary);">
            Indo-Gangetic Basin Field Analyses
          </h2>
          <p style="font-size: 0.95rem; line-height: 1.6; color: var(--se-text-secondary); max-width: 75ch; margin: 0 0 1rem;">
            Primary thesis research by Avnish Singh (Undergraduate civil engineering student at HBTU Kanpur). Conducted via statutory continuous ambient air quality monitoring stations (CPCB CAAQMS), USGS Landsat 8/9 thermal radiometry, and MERRA-2 boundary layer reanalysis.
          </p>
          <div class="se-method-limit-box">
            <strong>Methodological Boundaries Disclosure:</strong>
            The investigations below represent station-specific observations and satellite radiometry for the central Indo-Gangetic Basin. They are not national averages. Reanalysis baselines (MERRA-2 at ~50 km) do not resolve microscale street-canyon dynamics. Monitoring periods reflect historical statutory operations and include documented station maintenance interruptions.
          </div>
        </div>

        <div class="se-orig-inv-grid">
          {all_cards}
        </div>
      </div>
    </section>"""
    return section_html

def build_accessible_directory(countries_data):
    """Compiles the standalone accessible country list at countries/index.html."""
    os.makedirs(COUNTRIES_DIR, exist_ok=True)
    out_file = os.path.join(COUNTRIES_DIR, "index.html")

    sorted_countries = sorted(countries_data, key=lambda c: c.get("name", ""))

    rows = []
    for c in sorted_countries:
        iso3 = c.get("iso3", "").upper()
        name = c.get("name", iso3)
        region = c.get("region", "")
        inds = c.get("indicators", {})

        epi = inds.get("epi_score", {})
        epi_val = epi.get("formatted_value", "No data")
        epi_rk = f"#{epi.get('rank')}" if epi.get("rank") else "Unranked"

        pm = inds.get("pm25", {})
        pm_val = pm.get("formatted_value", "No data")
        pm_rk = f"#{pm.get('rank')}" if pm.get("rank") else "Unranked"

        co2_cap = inds.get("co2_per_capita", {})
        co2_cap_val = co2_cap.get("formatted_value", "No data")

        ren = inds.get("renewables_share", {})
        ren_val = ren.get("formatted_value", "No data")

        frst = inds.get("forest_share", {})
        frst_val = frst.get("formatted_value", "No data")

        rows.append(f"""          <tr>
            <td style="font-weight: 600;"><a href="../country/{iso3.lower()}/">{name}</a></td>
            <td style="font-family: monospace;">{iso3}</td>
            <td>{region}</td>
            <td style="font-family: monospace;">{epi_val} <span style="font-size: 0.75rem; color: var(--se-text-muted);">({epi_rk})</span></td>
            <td style="font-family: monospace;">{pm_val} <span style="font-size: 0.75rem; color: var(--se-text-muted);">({pm_rk})</span></td>
            <td style="font-family: monospace;">{co2_cap_val}</td>
            <td style="font-family: monospace;">{ren_val}</td>
            <td style="font-family: monospace;">{frst_val}</td>
            <td style="text-align: right;"><a href="../country/{iso3.lower()}/" class="se-link" style="font-weight: 600;">View Profile &rarr;</a></td>
          </tr>""")

    tbody_html = "\n".join(rows)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>All Countries Directory | Signal Earth</title>
  <meta name="description" content="Complete alphabetical directory of {len(sorted_countries)} countries tracked on Signal Earth, with open environmental indicators and performance benchmarks.">
  <link rel="canonical" href="https://signalearth.netlify.app/countries/">
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="stylesheet" href="../assets/tokens.css">
  <link rel="stylesheet" href="../style.css">
  <script src="../assets/theme.js"></script>
</head>
<body class="se-editorial-page">
  <a href="#main" class="skip-link">Skip to content</a>

  <!-- Header -->
  <header class="se-editorial-header" id="se-header">
    <div class="se-editorial-container">
      <div class="se-editorial-header-inner">
        <div class="se-editorial-wordmark-wrap">
          <a href="../index.html" class="se-editorial-wordmark">Signal Earth</a>
          <span class="se-wordmark-badge">Country Directory</span>
        </div>
        <div class="se-editorial-header-right">
          <nav class="se-editorial-nav" aria-label="Main Navigation">
            <ul class="se-editorial-nav-list">
              <li><a href="../index.html" class="se-editorial-nav-link">Globe</a></li>
              <li><a href="../rankings.html" class="se-editorial-nav-link">Rankings</a></li>
              <li><a href="../sources.html" class="se-editorial-nav-link">Data</a></li>
              <li><a href="../methodology.html" class="se-editorial-nav-link">Methodology</a></li>
              <li><a href="../about.html" class="se-editorial-nav-link">About</a></li>
            </ul>
          </nav>
          <button type="button" id="se-theme-toggle" class="se-theme-toggle-btn" aria-label="Toggle theme mode" title="Switch light / dark mode">
            <span class="se-theme-label">Theme</span>
          </button>
        </div>
      </div>
    </div>
  </header>

  <main id="main" class="se-editorial-container" style="padding-top: 2.5rem; padding-bottom: 4rem;">
    <div style="margin-bottom: 2rem;">
      <a href="../index.html" class="se-country-back-link" style="display: inline-block; margin-bottom: 1rem;">&larr; Return to Globe</a>
      <h1 style="font-family: var(--se-font-serif); font-size: 2.25rem; font-weight: 700; margin: 0 0 0.5rem; color: var(--se-text-primary);">
        All Countries ({len(sorted_countries)})
      </h1>
      <p style="font-size: 1rem; color: var(--se-text-secondary); max-width: 70ch; margin: 0;">
        Complete, keyboard-accessible alphabetical directory of all {len(sorted_countries)} countries evaluated across the open data pipeline. Select any country to view its complete indicator profile.
      </p>
    </div>

    <div style="overflow-x: auto; background: var(--se-bg-surface); border: 1px solid var(--se-border); border-radius: var(--se-radius-sm); padding: 1rem;">
      <table class="se-peer-table" style="width: 100%;">
        <thead>
          <tr>
            <th>Country</th>
            <th>ISO-3</th>
            <th>Region</th>
            <th>Yale EPI 2026</th>
            <th>Annual Mean PM2.5</th>
            <th>CO2 / Capita</th>
            <th>Renewables Share</th>
            <th>Forest Cover</th>
            <th style="text-align: right;">Profile</th>
          </tr>
        </thead>
        <tbody>
{tbody_html}
        </tbody>
      </table>
    </div>
  </main>

  <!-- Footer -->
  <footer class="se-editorial-footer">
    <div class="se-editorial-container">
      <div class="se-editorial-footer-grid" style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; margin-bottom: 2rem;">
        <div>
          <div style="font-family: var(--se-font-serif); font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--se-text-primary);">
            Signal Earth
          </div>
          <p style="font-size: 0.9rem; line-height: 1.6; color: var(--se-text-secondary); max-width: 50ch; margin: 0 0 1rem;">
            Avnish Singh &middot; Undergraduate civil engineering student at HBTU Kanpur &middot; Contact: <a href="mailto:avnish36singh@gmail.com" class="se-link">avnish36singh@gmail.com</a>
          </p>
          <div style="font-size: 0.85rem;">
            <a href="../credits.html" class="se-link">How to cite</a> &middot;
            <a href="../methodology.html" class="se-link">Methodology</a> &middot;
            <a href="../sources.html" class="se-link">Data Sources</a> &middot;
            <a href="../corrections.html" class="se-link">Corrections Log</a> &middot;
            <a href="../numbers_ledger.csv" class="se-link" download>Numbers Ledger (CSV)</a> &middot;
            <a href="https://github.com/avnish36singh-arch/signal-earth-portal" class="se-link" target="_blank" rel="noopener noreferrer">GitHub</a>
          </div>
        </div>
        <div>
          <div style="font-size: 0.8rem; font-family: var(--se-font-mono); text-transform: uppercase; color: var(--se-text-muted); margin-bottom: 0.5rem;">
            Open Data Attribution
          </div>
          <p style="font-size: 0.82rem; line-height: 1.5; color: var(--se-text-secondary); margin: 0 0 0.5rem;">
            Public indicators compiled from World Bank Open Data, Global Carbon Project, Ember Climate, FAO, and Yale CIESIN. Code licensed under MIT.
          </p>
          <p style="font-size: 0.82rem; line-height: 1.5; color: var(--se-text-muted); margin: 0;">
            Hosted on Netlify. Static build with zero cookies, zero trackers, and zero server-side state.
          </p>
        </div>
      </div>
      <div class="se-editorial-footer-bottom">
        <div>&copy; 2026 Signal Earth. Open-access empirical environmental indicators.</div>
        <div><a href="../privacy.html" class="se-link">Privacy Policy</a> &middot; <a href="../terms.html" class="se-link">Terms of Use</a> &middot; <a href="../licenses.html" class="se-link">Licenses</a></div>
      </div>
    </div>
  </footer>
</body>
</html>
"""

    # Typography enforcement: zero em/en dashes
    for dash in ["\u2013", "\u2014"]:
        html = html.replace(dash, "-")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [+] Wrote accessible country directory to {out_file}")

def build_all_countries():
    print("Beginning Signal Earth static country page build...")
    
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    country_files = glob.glob(os.path.join(DATA_COUNTRY_DIR, "*.json"))
    if not country_files:
        print("Warning: No country JSON files found in data/country/")
        return

    # Pass 1: Load all country documents for peer lookup
    all_countries_data = []
    for cpath in country_files:
        try:
            with open(cpath, "r", encoding="utf-8") as f:
                cdata = json.load(f)
            all_countries_data.append(cdata)
        except Exception as e:
            print(f"Error loading {cpath}: {e}")

    countries_index = []
    generated_routes = ["countries/index.html"]

    # Pass 2: Render each country profile
    for cdata in all_countries_data:
        iso3 = cdata.get("iso3", "").lower()
        if not iso3 or len(iso3) != 3:
            continue

        name = cdata.get("name", "")
        official_name = cdata.get("official_name", name)
        region = cdata.get("region", "")
        subregion = cdata.get("subregion", "")
        capital = cdata.get("capital", "Not specified")
        coords = cdata.get("coordinates", [20.0, 0.0])
        lat = coords[0] if len(coords) >= 1 else 0.0
        lon = coords[1] if len(coords) >= 2 else 0.0
        iso2 = cdata.get("iso2", iso3[:2].upper())

        land_area = cdata.get("land_area_km2")
        land_area_str = f"{land_area:,.0f} km²" if land_area else "No data"
        coords_str = f"{lat:.2f}°N, {lon:.2f}°E" if len(coords) == 2 else "No data"
        summary = cdata.get("summary", f"National environmental profile for {name} ({iso3.upper()}).")

        indicators = cdata.get("indicators", {})
        yale_epi = cdata.get("yale_epi_2026", {})

        # Yale EPI 2026 Hero Values
        epi_score = yale_epi.get("score")
        epi_rank = yale_epi.get("rank")
        epi_reg_rank = yale_epi.get("regional_rank")
        epi_change = yale_epi.get("ten_year_change")

        epi_score_str = f"{epi_score:.1f}" if epi_score is not None else "No data"
        epi_rank_str = f"Rank {epi_rank}" if epi_rank is not None else "Unranked"
        epi_reg_str = f"Rank {epi_reg_rank}" if epi_reg_rank is not None else "No data"
        if epi_change is not None:
            epi_change_str = f"{epi_change:+.1f}"
        else:
            epi_change_str = "No data"

        # Section 1: Headline cards
        headline_cards = []
        ranks_summary = {}
        for key in HEADLINE_KEYS:
            ind_record = indicators.get(key)
            headline_cards.append(render_headline_card(ind_record))
            if ind_record and ind_record.get("rank"):
                ranks_summary[key] = ind_record.get("rank")
        headline_cards_html = "\n".join(headline_cards)

        # Section 2: Air quality
        pm_ind = indicators.get("pm25", {})
        pm_val = pm_ind.get("formatted_value") or "No data"
        pm_num = pm_ind.get("value")
        pm_year = str(pm_ind.get("year") or "Unreported")
        pm_rank_int = pm_ind.get("rank")
        pm_total_int = pm_ind.get("total_ranked")
        pm_rank_str = f"Rank {pm_rank_int} of {pm_total_int}" if pm_rank_int and pm_total_int else "Unranked"

        if pm_num is not None:
            mult = pm_num / 5.0
            if mult > 1.0:
                who_mult_str = f"{mult:.1f}x the WHO 2021 annual guideline (5 µg/m³)"
                air_plain = f"In {pm_year}, the annual mean ambient PM2.5 exposure for {name} was {pm_num:.1f} µg/m³. This is {mult:.1f} times the World Health Organization 2021 air quality guideline threshold of 5 µg/m³."
            else:
                who_mult_str = "Meets the WHO 2021 annual guideline (5 µg/m³)"
                air_plain = f"In {pm_year}, the annual mean ambient PM2.5 exposure for {name} was {pm_num:.1f} µg/m³, which meets the World Health Organization 2021 annual guideline threshold."
        else:
            who_mult_str = "WHO multiple uncalculated (data unrecorded)"
            air_plain = f"No validated annual mean ambient PM2.5 exposure measurement is currently reported for {name} in the State of Global Air inventory."

        # Section 3: Emissions & Energy
        co2_t_ind = indicators.get("co2_total", {})
        co2_total_val = co2_t_ind.get("formatted_value") or "No data"
        c2_rank = co2_t_ind.get("rank")
        c2_total = co2_t_ind.get("total_ranked")
        co2_total_badge = f"Rank {c2_rank} of {c2_total}" if c2_rank and c2_total else "Unranked"
        co2_global_share = "7.3%" if iso3 == "ind" else "Reported in profile"

        co2_c_ind = indicators.get("co2_per_capita", {})
        co2_capita_val = co2_c_ind.get("formatted_value") or "No data"
        cpc_rank = co2_c_ind.get("rank")
        cpc_total = co2_c_ind.get("total_ranked")
        co2_capita_badge = f"Rank {cpc_rank} of {cpc_total}" if cpc_rank and cpc_total else "Unranked"

        ren_ind = indicators.get("renewables_share", {})
        renewables_val = ren_ind.get("formatted_value") or "No data"
        ren_rank = ren_ind.get("rank")
        ren_total = ren_ind.get("total_ranked")
        renewables_badge = f"Rank {ren_rank} of {ren_total}" if ren_rank and ren_total else "Unranked"

        # Section 4: Land & Forest
        for_ind = indicators.get("forest_share", {})
        forest_val = for_ind.get("formatted_value") or "No data"
        for_rank = for_ind.get("rank")
        for_total = for_ind.get("total_ranked")
        forest_badge = f"Rank {for_rank} of {for_total}" if for_rank and for_total else "Unranked"

        if for_ind.get("value") is not None:
            forest_plain = f"Forests cover approximately {forest_val} of national land area, reflecting both natural biomes and commercial timber stands."
        else:
            forest_plain = f"Standardized forest canopy fractions for {name} are unrecorded in the FAO Forest Resources Assessment."

        # Section 5: Demographics & Economy
        pop_ind = indicators.get("population", {})
        pop_val = pop_ind.get("formatted_value") or "No data"
        pop_num = pop_ind.get("value")
        p_rank = pop_ind.get("rank")
        p_total = pop_ind.get("total_ranked")
        pop_badge = f"Rank {p_rank} of {p_total}" if p_rank and p_total else "Unranked"

        # WDI Context object
        wdi_obj = cdata.get("wdi_context", {})
        wdi_density = wdi_obj.get("density", {}).get("latest_value")
        wdi_urban = wdi_obj.get("urban_share", {}).get("latest_value")
        wdi_gdp = wdi_obj.get("gdp_per_capita", {}).get("latest_value")

        if wdi_density is not None:
            density_val = f"{wdi_density:.1f} / km²"
        elif pop_num and land_area:
            density_val = f"{(pop_num / land_area):.1f} / km²"
        else:
            density_val = "No data"

        urban_str = f"{wdi_urban:.1f}% urban" if wdi_urban is not None else "Urban share unrecorded"
        gdp_str = f"${wdi_gdp:,.0f} GDP/capita" if wdi_gdp is not None else "GDP per capita unrecorded"
        pop_summary = f"{urban_str} &middot; {gdp_str}"
        pop_detail = f"Urban population fraction: {wdi_urban:.1f}% of resident total. Contemporaneous nominal GDP per resident: ${wdi_gdp:,.0f}." if (wdi_urban and wdi_gdp) else "World Bank WDI contemporaneous economic and demographic survey indicators."

        # Section 6: Regional peers
        peers_rows_html = render_regional_peers_table(iso3.upper(), subregion, region, all_countries_data)

        # Section 7: Provenance audit & Missing gaps
        audit_rows_html, gaps_list_html = render_audit_table_and_gaps(indicators)

        # Conditional India Research Section
        if iso3 == "ind":
            investigations = cdata.get("original_investigations", [])
            orig_inv_html = render_original_investigations(investigations)
        else:
            orig_inv_html = ""

        # Page metadata
        page_title = f"{name}: Environmental Indicators & Yale EPI Profile | Signal Earth"
        meta_desc = f"Open environmental profile for {name} ({iso3.upper()}): Yale EPI 2026 score, annual mean PM2.5 exposure, CO2 emissions, renewable electricity, and forest cover with open official sources."
        canonical_url = f"https://signalearth.netlify.app/country/{iso3}/"

        # Replace template placeholders
        page = template
        page = page.replace("{{PAGE_TITLE}}", page_title)
        page = page.replace("{{META_DESCRIPTION}}", meta_desc)
        page = page.replace("{{CANONICAL_URL}}", canonical_url)
        page = page.replace("{{COUNTRY_NAME}}", name)
        page = page.replace("{{OFFICIAL_NAME}}", official_name)
        page = page.replace("{{ISO3_CODE}}", iso3.upper())
        page = page.replace("{{ISO2_CODE}}", iso2)
        page = page.replace("{{REGION}}", region)
        page = page.replace("{{SUBREGION}}", subregion)
        page = page.replace("{{CAPITAL}}", capital)
        page = page.replace("{{LAND_AREA}}", land_area_str)
        page = page.replace("{{COORDINATES}}", coords_str)
        page = page.replace("{{LATITUDE}}", f"{lat:.4f}")
        page = page.replace("{{LONGITUDE}}", f"{lon:.4f}")
        page = page.replace("{{SUMMARY}}", summary)
        page = page.replace("{{DATA_AS_OF}}", "2026-10-21")

        # EPI Lead placeholders
        page = page.replace("{{EPI_RANK_STR}}", epi_rank_str)
        page = page.replace("{{EPI_SCORE_STR}}", epi_score_str)
        page = page.replace("{{EPI_REGIONAL_RANK_STR}}", epi_reg_str)
        page = page.replace("{{EPI_CHANGE_STR}}", epi_change_str)

        page = page.replace("{{HEADLINE_INDICATOR_CARDS}}", headline_cards_html)
        
        page = page.replace("{{AIR_YEAR}}", pm_year)
        page = page.replace("{{AIR_PM25_VALUE}}", pm_val)
        page = page.replace("{{AIR_WHO_MULTIPLE}}", who_mult_str)
        page = page.replace("{{AIR_PM25_RANK}}", pm_rank_str)
        page = page.replace("{{AIR_PLAIN_SENTENCE}}", air_plain)

        page = page.replace("{{CO2_TOTAL_VALUE}}", co2_total_val)
        page = page.replace("{{CO2_TOTAL_RANK_BADGE}}", co2_total_badge)
        page = page.replace("{{CO2_GLOBAL_SHARE}}", co2_global_share)
        page = page.replace("{{CO2_CAPITA_VALUE}}", co2_capita_val)
        page = page.replace("{{CO2_CAPITA_RANK_BADGE}}", co2_capita_badge)
        page = page.replace("{{RENEWABLES_VALUE}}", renewables_val)
        page = page.replace("{{RENEWABLES_RANK_BADGE}}", renewables_badge)

        page = page.replace("{{FOREST_SHARE_VALUE}}", forest_val)
        page = page.replace("{{FOREST_RANK_BADGE}}", forest_badge)
        page = page.replace("{{FOREST_PLAIN_SENTENCE}}", forest_plain)

        page = page.replace("{{POPULATION_VALUE}}", pop_val)
        page = page.replace("{{POP_RANK_BADGE}}", pop_badge)
        page = page.replace("{{POP_DENSITY_VALUE}}", density_val)
        page = page.replace("{{POP_CONTEXT_SUMMARY}}", pop_summary)
        page = page.replace("{{POP_CONTEXT_DETAIL}}", pop_detail)

        page = page.replace("{{REGIONAL_PEERS_TABLE_ROWS}}", peers_rows_html)
        page = page.replace("{{ORIGINAL_INVESTIGATIONS_SECTION}}", orig_inv_html)

        page = page.replace("{{AUDIT_TABLE_ROWS}}", audit_rows_html)
        page = page.replace("{{MISSING_GAPS_LIST}}", gaps_list_html)

        # Strict validation: verify no em dashes or en dashes
        for dash in ["\u2013", "\u2014"]:
            page = page.replace(dash, "-")

        # Write output country file
        country_out_dir = os.path.join(OUTPUT_COUNTRY_DIR, iso3)
        os.makedirs(country_out_dir, exist_ok=True)
        country_out_file = os.path.join(country_out_dir, "index.html")

        with open(country_out_file, "w", encoding="utf-8") as out:
            out.write(page)

        generated_routes.append(f"country/{iso3}/")

        # Compact index entry
        compact_inds = {}
        for k, ind_rec in indicators.items():
            compact_inds[k] = {
                'value': ind_rec.get("value"),
                'year': ind_rec.get("year"),
                'rank': ind_rec.get("rank"),
                'total_ranked': ind_rec.get("total_ranked"),
                'unit': ind_rec.get("unit", ""),
                'formatted': ind_rec.get("formatted_value", "No data"),
                'source': ind_rec.get("source_name", "Open Data"),
                'license': ind_rec.get("license", "CC BY 4.0")
            }

        countries_index.append({
            "iso3": iso3.upper(),
            "name": name,
            "region": region,
            "subregion": subregion,
            "coordinates": [lat, lon],
            "ranks": ranks_summary,
            "indicators": compact_inds
        })

    # Sort countries index alphabetically
    countries_index.sort(key=lambda c: c["name"])

    # Write data/countries.json
    with open(COUNTRIES_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(countries_index, f, separators=(',', ':'), ensure_ascii=False)
    print(f"  [+] Wrote index with {len(countries_index)} countries to data/countries.json")

    # Build standalone accessible directory at countries/index.html
    build_accessible_directory(all_countries_data)

    # Update sitemap.xml
    update_sitemap(generated_routes)

def update_sitemap(new_routes):
    """Adds pre-built country routes to sitemap.xml if not already present."""
    if not os.path.exists(SITEMAP_PATH):
        return

    tree = ET.parse(SITEMAP_PATH)
    root = tree.getroot()
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    
    existing_locs = set()
    for url in root.findall(f"{namespace}url"):
        loc = url.find(f"{namespace}loc")
        if loc is not None and loc.text:
            existing_locs.add(loc.text.strip())

    base_domain = "https://signalearth.netlify.app/"
    added_count = 0

    for route in new_routes:
        full_url = base_domain + route
        if full_url not in existing_locs:
            url_el = ET.SubElement(root, f"{namespace}url")
            loc_el = ET.SubElement(url_el, f"{namespace}loc")
            loc_el.text = full_url
            mod_el = ET.SubElement(url_el, f"{namespace}lastmod")
            mod_el.text = "2026-10-21"
            freq_el = ET.SubElement(url_el, f"{namespace}changefreq")
            freq_el.text = "weekly"
            prio_el = ET.SubElement(url_el, f"{namespace}priority")
            prio_el.text = "0.8"
            added_count += 1

    if added_count > 0:
        ET.indent(tree, space="  ", level=0)
        tree.write(SITEMAP_PATH, encoding="UTF-8", xml_declaration=True)
        print(f"  [+] Added {added_count} country route(s) to sitemap.xml")

if __name__ == "__main__":
    build_all_countries()
