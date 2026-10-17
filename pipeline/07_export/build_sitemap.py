"""
Sitemap XML Generator for Signal Earth.
Builds canonical XML sitemap on https://signalearth.netlify.app/
including core hubs and all 48 sovereign country dossiers.
"""

import os
import json
from datetime import datetime

def generate_sitemap():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sitemap_path = os.path.join(root, 'sitemap.xml')
    countries_json_path = os.path.join(root, 'data', 'countries.json')

    base_url = "https://signalearth.netlify.app"
    today = datetime.now().strftime("%Y-%m-%d")

    # Core Hubs
    core_pages = [
        {"loc": f"{base_url}/", "changefreq": "daily", "priority": "1.0"},
        {"loc": f"{base_url}/rankings.html", "changefreq": "daily", "priority": "0.95"},
        {"loc": f"{base_url}/compare.html", "changefreq": "daily", "priority": "0.95"},
        {"loc": f"{base_url}/sources.html", "changefreq": "weekly", "priority": "0.9"},
        {"loc": f"{base_url}/methodology.html", "changefreq": "weekly", "priority": "0.9"},
        {"loc": f"{base_url}/data.html", "changefreq": "weekly", "priority": "0.85"},
        {"loc": f"{base_url}/known-problems.html", "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{base_url}/corrections.html", "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{base_url}/credits.html", "changefreq": "monthly", "priority": "0.75"},
        {"loc": f"{base_url}/about.html", "changefreq": "monthly", "priority": "0.75"},
        {"loc": f"{base_url}/licenses.html", "changefreq": "monthly", "priority": "0.7"},
        {"loc": f"{base_url}/privacy.html", "changefreq": "monthly", "priority": "0.7"},
        {"loc": f"{base_url}/terms.html", "changefreq": "monthly", "priority": "0.7"},
        {"loc": f"{base_url}/numbers_ledger.csv", "changefreq": "weekly", "priority": "0.7"},
        {"loc": f"{base_url}/data/countries.json", "changefreq": "daily", "priority": "0.8"},
    ]

    # Sovereign country dossiers
    country_pages = []
    if os.path.exists(countries_json_path):
        with open(countries_json_path, 'r', encoding='utf-8') as f:
            countries = json.load(f)
        for c in countries:
            iso3 = c.get('iso3', '').lower()
            if iso3:
                country_pages.append({
                    "loc": f"{base_url}/country/{iso3}/",
                    "changefreq": "weekly",
                    "priority": "0.85"
                })

    urls = core_pages + country_pages

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    for u in urls:
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{u["loc"]}</loc>')
        xml_lines.append(f'    <lastmod>{today}</lastmod>')
        xml_lines.append(f'    <changefreq>{u["changefreq"]}</changefreq>')
        xml_lines.append(f'    <priority>{u["priority"]}</priority>')
        xml_lines.append('  </url>')

    xml_lines.append('</urlset>\n')

    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(xml_lines))

    print(f"Generated sitemap.xml with {len(urls)} URLs at {sitemap_path}")

if __name__ == '__main__':
    generate_sitemap()
