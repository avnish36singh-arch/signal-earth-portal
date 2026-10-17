#!/usr/bin/env python3
"""
Signal Earth - Static Country Page Generator (build/build_countries.py)
Reads data/country/*.json, compiles data/countries.json, and generates
pre-built HTML pages at country/{iso3}/index.html from build/template.html.
Adheres strictly to zero-em-dash rule, no-data-as-null rule, and canonical source attribution.
"""

import os
import glob
import json
import xml.etree.ElementTree as ET

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_COUNTRY_DIR = os.path.join(WORKSPACE_ROOT, "data", "country")
TEMPLATE_PATH = os.path.join(WORKSPACE_ROOT, "build", "template.html")
OUTPUT_COUNTRY_DIR = os.path.join(WORKSPACE_ROOT, "country")
COUNTRIES_INDEX_PATH = os.path.join(WORKSPACE_ROOT, "data", "countries.json")
SITEMAP_PATH = os.path.join(WORKSPACE_ROOT, "sitemap.xml")

INDICATOR_ORDER = [
    "pm25",
    "temp_anomaly",
    "temp_trend",
    "co2_total",
    "co2_per_capita",
    "forest_share",
    "renewables_share",
    "population"
]

def render_indicator_card(ind_data):
    """Renders a single indicator card with strict 'No data' presentation for null values."""
    if not ind_data:
        return ""
    
    name = ind_data.get("name", "Unknown Indicator")
    val = ind_data.get("value")
    formatted_val = ind_data.get("formatted_value")
    unit = ind_data.get("unit", "")
    rank = ind_data.get("rank")
    total_ranked = ind_data.get("total_ranked")
    context = ind_data.get("context", "")
    src_name = ind_data.get("source_name", "Named Source")
    src_url = ind_data.get("source_url", "#")
    src_dataset = ind_data.get("source_dataset", "")
    year = ind_data.get("year")
    license_id = ind_data.get("license", "Open Data")

    # Strict No Data Rule
    if val is None or formatted_val is None:
        value_html = '<div class="se-ind-value is-nodata">No data</div>'
        rank_badge = '<span class="se-ind-rank-badge" style="background: rgba(148, 163, 184, 0.15); color: var(--se-text-muted); border-color: rgba(148, 163, 184, 0.3);">Unranked</span>'
        context_html = '<div class="se-ind-context">No statutory or peer-reviewed measurement reported for this indicator.</div>'
    else:
        value_html = f'<div class="se-ind-value">{formatted_val}</div>'
        if rank and total_ranked:
            rank_badge = f'<span class="se-ind-rank-badge">Rank {rank} of {total_ranked}</span>'
        else:
            rank_badge = '<span class="se-ind-rank-badge">Reported</span>'
        context_html = f'<div class="se-ind-context">{context}</div>'

    year_str = f" ({year})" if year else ""

    card_html = f"""
          <div class="se-indicator-card">
            <div class="se-ind-header">
              <h3 class="se-ind-title">{name}</h3>
              {rank_badge}
            </div>
            <div class="se-ind-value-row">
              {value_html}
            </div>
            {context_html}
            <div class="se-ind-footer">
              <div class="se-ind-src-line">
                Source: <a href="{src_url}" target="_blank" rel="noopener noreferrer">{src_name}</a>{year_str}
              </div>
              <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 0.35rem;">
                <span style="font-size: 0.7rem; color: var(--se-text-muted);">{src_dataset}</span>
                <span class="se-ind-license-badge">{license_id}</span>
              </div>
            </div>
          </div>"""
    return card_html

def render_original_investigations(investigations_list):
    """Renders regional original research section (e.g. for India)."""
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
    <!-- Original Field Research Section -->
    <section class="se-orig-inv-section" aria-labelledby="orig-inv-heading">
      <div class="se-editorial-container">
        <div style="margin-bottom: 2rem;">
          <span style="font-family: var(--se-font-mono); font-size: 0.72rem; color: var(--se-teal-live); text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;">Original In-Situ &amp; Spaceborne Investigations</span>
          <h2 id="orig-inv-heading" style="font-family: var(--se-font-serif); font-size: 1.85rem; margin: 0.25rem 0 0.5rem; color: var(--se-text-primary);">
            Indo-Gangetic Basin Field Analyses
          </h2>
          <p style="font-size: 1rem; line-height: 1.6; color: var(--se-text-secondary); max-width: 70ch; margin: 0;">
            Primary research conducted by Avnish Singh (HBTU Kanpur) combining statutory continuous ambient monitoring stations, Landsat 8/9 thermal radiometry, and MERRA-2 boundary layer reanalysis.
          </p>
        </div>

        <div class="se-orig-inv-grid">
          {all_cards}
        </div>
      </div>
    </section>"""
    return section_html

def build_all_countries():
    print("Beginning Signal Earth static country page build...")
    
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    country_files = glob.glob(os.path.join(DATA_COUNTRY_DIR, "*.json"))
    if not country_files:
        print("Warning: No country JSON files found in data/country/")
        return

    countries_index = []
    generated_routes = []

    for cpath in country_files:
        with open(cpath, "r", encoding="utf-8") as f:
            cdata = json.load(f)

        iso3 = cdata.get("iso3", "").lower()
        if not iso3 or len(iso3) != 3:
            print(f"Skipping invalid file: {cpath}")
            continue

        name = cdata.get("name", "")
        official_name = cdata.get("official_name", name)
        region = cdata.get("region", "")
        subregion = cdata.get("subregion", "")
        capital = cdata.get("capital", "N/A")
        coords = cdata.get("coordinates", [0.0, 0.0])
        land_area = cdata.get("land_area_km2")
        land_area_str = f"{land_area:,.0f} km²" if land_area else "No data"
        coords_str = f"{coords[0]:.2f}°N, {coords[1]:.2f}°E" if len(coords) == 2 else "No data"
        summary = cdata.get("summary", "")

        # Format 8 indicator cards
        indicators_map = cdata.get("indicators", {})
        cards_html_list = []
        ranks_summary = {}

        for key in INDICATOR_ORDER:
            ind_record = indicators_map.get(key)
            cards_html_list.append(render_indicator_card(ind_record))
            if ind_record and ind_record.get("rank"):
                ranks_summary[key] = ind_record.get("rank")

        indicator_cards_html = "\n".join(cards_html_list)

        # Format original investigations if present
        investigations = cdata.get("original_investigations", [])
        orig_inv_html = render_original_investigations(investigations)

        # Replace template placeholders
        page_title = f"{name}: Environmental Data, Air Quality & Rankings | Signal Earth"
        meta_desc = f"Verified environmental profile for {name} ({iso3.upper()}): annual PM2.5, surface temperature anomaly, CO2 emissions, and forest cover with named sources and reproducible data."
        canonical_url = f"https://signalearth.netlify.app/country/{iso3}/"

        page_content = template
        page_content = page_content.replace("{{PAGE_TITLE}}", page_title)
        page_content = page_content.replace("{{META_DESCRIPTION}}", meta_desc)
        page_content = page_content.replace("{{CANONICAL_URL}}", canonical_url)
        page_content = page_content.replace("{{COUNTRY_NAME}}", name)
        page_content = page_content.replace("{{OFFICIAL_NAME}}", official_name)
        page_content = page_content.replace("{{ISO3_CODE}}", iso3.upper())
        page_content = page_content.replace("{{REGION}}", region)
        page_content = page_content.replace("{{SUBREGION}}", subregion)
        page_content = page_content.replace("{{CAPITAL}}", capital)
        page_content = page_content.replace("{{LAND_AREA}}", land_area_str)
        page_content = page_content.replace("{{COORDINATES}}", coords_str)
        page_content = page_content.replace("{{SUMMARY}}", summary)
        page_content = page_content.replace("{{INDICATOR_CARDS}}", indicator_cards_html)
        page_content = page_content.replace("{{ORIGINAL_INVESTIGATIONS_SECTION}}", orig_inv_html)

        # Strict validation: verify no em dashes
        for dash in ["\u2013", "\u2014"]:
            if dash in page_content:
                page_content = page_content.replace(dash, "-")

        # Write country/{iso3}/index.html
        country_out_dir = os.path.join(OUTPUT_COUNTRY_DIR, iso3)
        os.makedirs(country_out_dir, exist_ok=True)
        country_out_file = os.path.join(country_out_dir, "index.html")

        with open(country_out_file, "w", encoding="utf-8") as out:
            out.write(page_content)

        print(f"  [+] Generated /country/{iso3}/index.html ({name})")
        generated_routes.append(f"country/{iso3}/")

        # Record in lightweight index
        countries_index.append({
            "iso3": iso3.upper(),
            "name": name,
            "region": region,
            "coordinates": coords,
            "ranks": ranks_summary
        })

    # Write data/countries.json
    with open(COUNTRIES_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(countries_index, f, indent=2)
    print(f"  [+] Wrote lightweight index with {len(countries_index)} countries to data/countries.json")

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
            mod_el.text = "2026-10-17"
            freq_el = ET.SubElement(url_el, f"{namespace}changefreq")
            freq_el.text = "monthly"
            prio_el = ET.SubElement(url_el, f"{namespace}priority")
            prio_el.text = "0.8"
            added_count += 1

    if added_count > 0:
        ET.indent(tree, space="  ", level=0)
        tree.write(SITEMAP_PATH, encoding="UTF-8", xml_declaration=True)
        print(f"  [+] Added {added_count} country route(s) to sitemap.xml")

if __name__ == "__main__":
    build_all_countries()
