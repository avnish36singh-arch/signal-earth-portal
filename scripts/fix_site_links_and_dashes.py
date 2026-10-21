#!/usr/bin/env python3
"""
Fixes internal links and removes all unicode em/en dashes in authored files.
"""

import os
import re

ROOT_DIR = r"b:\movies\signal earth"

def clean_dashes_in_file(fpath):
    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    modified = False
    if "\u2014" in content:
        content = content.replace("\u2014", " - ")
        modified = True
    if "\u2013" in content:
        content = content.replace("\u2013", "-")
        modified = True

    if modified:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Cleaned dashes in: {fpath}")

def fix_authored_dashes():
    # Targets: assets/*.js, assets/*.css, *.html
    for dirpath, _, filenames in os.walk(os.path.join(ROOT_DIR, "assets")):
        if "vendor" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith((".js", ".css")):
                clean_dashes_in_file(os.path.join(dirpath, fn))

def fix_analyses_pages():
    analyses_dir = os.path.join(ROOT_DIR, "analyses")
    for slug in ["kanpur", "delhi", "kanpur-lst", "kanpur-uhi"]:
        page = os.path.join(analyses_dir, slug, "index.html")
        if not os.path.exists(page):
            continue
        with open(page, "r", encoding="utf-8") as f:
            c = f.read()

        # Fix relative links inside analyses/<slug>/index.html
        replacements = [
            ('href="kanpur.html"', 'href="../kanpur/index.html"'),
            ('href="delhi.html"', 'href="../delhi/index.html"'),
            ('href="kanpur-lst.html"', 'href="../kanpur-lst/index.html"'),
            ('href="kanpur-uhi.html"', 'href="../kanpur-uhi/index.html"'),
            ('href="kanpur-particulates.html"', 'href="../kanpur/index.html"'),
            ('href="delhi-naqi.html"', 'href="../delhi/index.html"'),
            ('href="inversion-dynamics.html"', 'href="../kanpur-lst/index.html"'),
            ('href="landsat-uhi.html"', 'href="../kanpur-uhi/index.html"'),
            ('href="comparison.html"', 'href="../../compare.html"'),
            ('href="data.html"', 'href="../../data.html"'),
            ('href="rankings.html"', 'href="../../rankings.html"'),
            ('href="sources.html"', 'href="../../sources.html"'),
            ('href="corrections.html"', 'href="../../corrections.html"'),
            ('href="numbers_ledger.csv"', 'href="../../numbers_ledger.csv"'),
            ('href="briefs/', 'href="../../briefs/'),
            ('href="research.html"', 'href="../../research.html"'),
            ('href="index.html"', 'href="../../index.html"'),
            ('href="about.html"', 'href="../../about.html"'),
            ('href="methodology.html"', 'href="../../methodology.html"'),
            ('href="credits.html"', 'href="../../credits.html"'),
            ('href="privacy.html"', 'href="../../privacy.html"'),
            ('href="terms.html"', 'href="../../terms.html"'),
            ('href="licenses.html"', 'href="../../licenses.html"'),
            ('href="../notes/feed.xml"', 'href="../../notes/feed.xml"'),
            ('href="../notes/index.html"', 'href="../../notes/index.html"'),
            ('href="../analyses/index.html"', 'href="../../analyses/index.html"')
        ]
        for old, new in replacements:
            c = c.replace(old, new)

        with open(page, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"Updated links in {page}")

def fix_global_investigation_links():
    # Update links across the site from investigations/*.html to analyses/*/index.html
    map_links = [
        ("investigations/kanpur.html", "analyses/kanpur/index.html"),
        ("investigations/delhi.html", "analyses/delhi/index.html"),
        ("investigations/kanpur-lst.html", "analyses/kanpur-lst/index.html"),
        ("investigations/kanpur-uhi.html", "analyses/kanpur-uhi/index.html"),
        ("investigations/kanpur-particulates.html", "analyses/kanpur/index.html"),
        ("investigations/delhi-naqi.html", "analyses/delhi/index.html"),
        ("investigations/inversion-dynamics.html", "analyses/kanpur-lst/index.html"),
        ("investigations/landsat-uhi.html", "analyses/kanpur-uhi/index.html"),
        ("investigations/comparison.html", "compare.html"),
        ("../investigations/kanpur.html", "../analyses/kanpur/index.html"),
        ("../investigations/delhi.html", "../analyses/delhi/index.html"),
        ("../investigations/kanpur-lst.html", "../analyses/kanpur-lst/index.html"),
        ("../investigations/kanpur-uhi.html", "../analyses/kanpur-uhi/index.html"),
        ("../investigations/comparison.html", "../compare.html"),
    ]

    for dirpath, _, filenames in os.walk(ROOT_DIR):
        if any(ign in dirpath for ign in [".git", "node_modules", ".agents", ".gemini", "tmp", "scratch"]):
            continue
        for fn in filenames:
            if fn.endswith(".html"):
                fp = os.path.join(dirpath, fn)
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    c = f.read()
                modified = False
                for old, new in map_links:
                    if old in c:
                        c = c.replace(old, new)
                        modified = True
                if modified:
                    with open(fp, "w", encoding="utf-8") as f:
                        f.write(c)
                    print(f"Updated investigation links in: {fp}")

def main():
    fix_authored_dashes()
    fix_analyses_pages()
    fix_global_investigation_links()

if __name__ == "__main__":
    main()
