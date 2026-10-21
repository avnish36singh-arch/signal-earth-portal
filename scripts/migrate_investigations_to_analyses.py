#!/usr/bin/env python3
"""
Migrates investigations/*.html to analyses/<slug>/index.html.
Ensures:
1. Relative asset paths and links are corrected (e.g. ../ -> ../../).
2. Canonical URLs are updated to https://avnish36singh-arch.github.io/signal-earth-portal/analyses/<slug>/.
3. Author line does not imply institutional affiliation with HBTU Kanpur.
4. Zero em dashes (\u2014) or en dashes (\u2013).
5. Old investigation HTML pages are replaced with immediate client-side redirects to /analyses/<slug>/.
6. Creates analyses/index.html.
"""

import os
import re

MIGRATION_MAP = {
    "kanpur": {
        "old_file": "investigations/kanpur.html",
        "slug": "kanpur",
        "title": "Kanpur Particulate Dynamics",
        "aliases": ["kanpur-particulates.html"]
    },
    "delhi": {
        "old_file": "investigations/delhi.html",
        "slug": "delhi",
        "title": "Delhi Five-Year NAQI Dynamics",
        "aliases": ["delhi-naqi.html"]
    },
    "kanpur-lst": {
        "old_file": "investigations/kanpur-lst.html",
        "slug": "kanpur-lst",
        "title": "Kanpur Skin Temperature & Inversion",
        "aliases": ["inversion-dynamics.html"]
    },
    "kanpur-uhi": {
        "old_file": "investigations/kanpur-uhi.html",
        "slug": "kanpur-uhi",
        "title": "Kanpur Landsat 30 m Thermal Infrared",
        "aliases": ["landsat-uhi.html"]
    }
}

REDIRECT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url={target_url}">
  <link rel="canonical" href="{canonical_url}">
  <title>Redirecting to {target_title}...</title>
  <script>window.location.replace("{target_url}");</script>
</head>
<body style="font-family: sans-serif; padding: 2rem; text-align: center;">
  <p>This report has moved to <a href="{target_url}">{target_title}</a>.</p>
</body>
</html>
"""

def clean_dashes(text):
    text = text.replace("\u2014", " - ")
    text = text.replace("\u2013", "-")
    return text

def fix_asset_paths(html_content):
    # Old files used ../style.css etc. Now in analyses/<slug>/, need ../../style.css
    # Replace relative links:
    # href="../ -> href="../../
    # src="../ -> src="../../
    # But do not double replace if already ../../
    html_content = re.sub(r'href="\.\./(?!\.\/)', 'href="../../', html_content)
    html_content = re.sub(r'src="\.\./(?!\.\/)', 'src="../../', html_content)
    return html_content

def fix_affiliation(html_content):
    # Ensure HBTU affiliation is not implied
    # Replace any string that implies university affiliation
    pattern = r'By\s*<strong>Avnish Singh</strong>[,\s\w]*HBTU Kanpur[,\s\w]*'
    replacement = 'By <strong>Avnish Singh</strong>, undergraduate civil engineering student at HBTU Kanpur (personal research project; not affiliated with or endorsed by HBTU Kanpur)'
    html_content = re.sub(pattern, replacement, html_content)
    
    # Also generic mentions
    html_content = html_content.replace(
        "Civil Engineering undergraduate, HBTU Kanpur, focusing on environmental engineering",
        "undergraduate civil engineering student at HBTU Kanpur (independent research project; no institutional affiliation)"
    )
    return html_content

def migrate():
    os.makedirs("analyses", exist_ok=True)

    for slug, meta in MIGRATION_MAP.items():
        out_dir = os.path.join("analyses", slug)
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "index.html")

        with open(meta["old_file"], "r", encoding="utf-8") as f:
            content = f.read()

        content = clean_dashes(content)
        content = fix_asset_paths(content)
        content = fix_affiliation(content)

        # Update canonical URL
        old_canonical = f"https://avnish36singh-arch.github.io/signal-earth-portal/investigations/{slug}.html"
        new_canonical = f"https://avnish36singh-arch.github.io/signal-earth-portal/analyses/{slug}/"
        content = content.replace(old_canonical, new_canonical)

        # Update og:url
        content = content.replace(f'content="{old_canonical}"', f'content="{new_canonical}"')

        # Also copy JS dependencies if needed
        # kanpur-lst.js and delhi.js
        old_js = meta["old_file"].replace(".html", ".js")
        if os.path.exists(old_js):
            js_name = os.path.basename(old_js)
            target_js = os.path.join(out_dir, js_name)
            with open(old_js, "r", encoding="utf-8") as js_f:
                js_content = clean_dashes(js_f.read())
            # In js, check if data paths need adjusting
            js_content = js_content.replace('"../data/', '"../../data/')
            with open(target_js, "w", encoding="utf-8") as js_f:
                js_f.write(js_content)
            print(f"Copied and updated script: {target_js}")

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Migrated {meta['old_file']} -> {out_file}")

        # Now write redirect page into old file
        rel_target = f"../analyses/{slug}/"
        redirect_html = REDIRECT_TEMPLATE.format(
            target_url=rel_target,
            canonical_url=new_canonical,
            target_title=meta["title"]
        )
        with open(meta["old_file"], "w", encoding="utf-8") as f:
            f.write(redirect_html)
        print(f"Created redirect in {meta['old_file']} -> {rel_target}")

        # Also write redirect in alias files
        for alias in meta["aliases"]:
            alias_path = os.path.join("investigations", alias)
            with open(alias_path, "w", encoding="utf-8") as f:
                f.write(redirect_html)
            print(f"Created redirect in {alias_path} -> {rel_target}")

    # Handle comparison.html in investigations
    comp_old = "investigations/comparison.html"
    if os.path.exists(comp_old):
        comp_redirect = REDIRECT_TEMPLATE.format(
            target_url="../compare.html",
            canonical_url="https://avnish36singh-arch.github.io/signal-earth-portal/compare.html",
            target_title="Comparative Analysis"
        )
        with open(comp_old, "w", encoding="utf-8") as f:
            f.write(comp_redirect)
        print(f"Created redirect in {comp_old} -> ../compare.html")

    print("Migration complete!")

if __name__ == "__main__":
    migrate()
