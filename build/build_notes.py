#!/usr/bin/env python3
"""
Signal Earth Notes Builder
Generates static HTML pages for empirical notes, the notes index, and notes/feed.xml.
Enforces validation rules: author Avnish Singh, cited sources, date, data link, corrections link,
no em or en dashes, and no institutional affiliation representation.
"""

import os
import re
import glob
import json
from datetime import datetime, timezone
import html

NOTES_SRC_DIR = "notes_src"
NOTES_OUT_DIR = "notes"
FEED_OUT_PATH = os.path.join(NOTES_OUT_DIR, "feed.xml")
NOTES_JSON_PATH = os.path.join("data", "notes.json")

NOTE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | Signal Earth Notes</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="https://avnish36singh-arch.github.io/signal-earth-portal/notes/{slug}.html">
  <link rel="alternate" type="application/rss+xml" title="Signal Earth Notes RSS Feed" href="../notes/feed.xml">
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="../favicon-32.png">
  <link rel="stylesheet" href="../style.css">
  <style>
    .se-note-container {{
      max-width: 780px;
      margin: 0 auto;
      padding: 3rem 1.5rem 5rem;
    }}
    .se-note-header {{
      margin-bottom: 2.5rem;
      border-bottom: 1px solid var(--se-border);
      padding-bottom: 1.5rem;
    }}
    .se-note-kicker {{
      font-family: var(--se-font-mono);
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--se-text-muted);
      margin-bottom: 0.75rem;
      display: inline-block;
    }}
    .se-note-title {{
      font-family: var(--se-font-serif);
      font-size: 2.1rem;
      font-weight: 700;
      line-height: 1.25;
      color: var(--se-text-primary);
      margin: 0 0 1.25rem;
    }}
    .se-note-meta-box {{
      background: var(--se-bg-surface);
      border: 1px solid var(--se-border);
      border-radius: var(--se-radius-sm);
      padding: 1rem 1.25rem;
      font-size: 0.85rem;
      line-height: 1.6;
      color: var(--se-text-secondary);
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem 1.5rem;
    }}
    @media (max-width: 600px) {{
      .se-note-meta-box {{
        grid-template-columns: 1fr;
      }}
    }}
    .se-note-meta-item strong {{
      color: var(--se-text-primary);
      font-weight: 600;
      font-family: var(--se-font-mono);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      display: block;
      margin-bottom: 0.15rem;
    }}
    .se-note-body {{
      font-size: 1.05rem;
      line-height: 1.75;
      color: var(--se-text-primary);
    }}
    .se-note-body h2 {{
      font-family: var(--se-font-serif);
      font-size: 1.45rem;
      margin: 2.25rem 0 1rem;
      border-bottom: 1px solid var(--se-border-subtle);
      padding-bottom: 0.4rem;
    }}
    .se-note-body p {{
      margin: 0 0 1.25rem;
    }}
    .se-note-body ul {{
      margin: 0 0 1.5rem 1.5rem;
      padding: 0;
    }}
    .se-note-body li {{
      margin-bottom: 0.5rem;
    }}
    .se-note-footer-nav {{
      margin-top: 3.5rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--se-border);
      display: flex;
      justify-content: space-between;
      font-size: 0.88rem;
    }}
  </style>
</head>
<body>
  <header class="se-editorial-header">
    <div class="se-editorial-header-inner">
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <a href="../index.html" class="se-editorial-wordmark">Signal Earth</a>
        <span style="font-size: 0.75rem; font-family: var(--se-font-mono); color: var(--se-text-muted); text-transform: uppercase;">/ Notes</span>
      </div>
      <nav aria-label="Main Navigation">
        <ul class="se-editorial-nav-list">
          <li><a href="../index.html" class="se-editorial-nav-link">Globe</a></li>
          <li><a href="../analyses/index.html" class="se-editorial-nav-link">Analyses</a></li>
          <li><a href="../notes/index.html" class="se-editorial-nav-link active">Notes</a></li>
          <li><a href="../data.html" class="se-editorial-nav-link">Data</a></li>
          <li><a href="../about.html" class="se-editorial-nav-link">About</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main id="main">
    <article class="se-note-container">
      <header class="se-note-header">
        <span class="se-note-kicker">Empirical Field Note &middot; {date}</span>
        <h1 class="se-note-title">{title}</h1>
        
        <div class="se-note-meta-box">
          <div class="se-note-meta-item">
            <strong>Author</strong>
            <span>{author}</span>
          </div>
          <div class="se-note-meta-item">
            <strong>Published Date</strong>
            <span>{formatted_date}</span>
          </div>
          <div class="se-note-meta-item">
            <strong>Data Source</strong>
            <span>{sources}</span>
          </div>
          <div class="se-note-meta-item">
            <strong>Underlying Dataset</strong>
            <a href="..{data_link}" class="se-link" download>Download Raw Dataset &rarr;</a>
          </div>
        </div>
      </header>

      {draft_banner_html}

      <div class="se-note-body">
{body_html}
      </div>

      <div class="se-note-footer-nav">
        <a href="../notes/index.html" class="se-link">&larr; Back to all notes</a>
        <a href="../corrections.html" class="se-link">Submit a correction</a>
      </div>
    </article>
  </main>

  <footer class="se-editorial-footer" style="background: var(--se-bg-page); border-top: 1px solid var(--se-border); padding: 2.5rem 1.5rem 2rem;">
    <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; color: var(--se-text-muted); flex-wrap: wrap; gap: 1rem;">
      <div>&copy; 2026 Signal Earth. Maintained by Avnish Singh. No institutional affiliation with HBTU Kanpur.</div>
      <div>
        <a href="../notes/feed.xml" class="se-link">RSS Feed</a> &middot;
        <a href="../corrections.html" class="se-link">Corrections</a> &middot;
        <a href="../privacy.html" class="se-link">Privacy</a>
      </div>
    </div>
  </footer>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Analytical Field Notes | Signal Earth</title>
  <meta name="description" content="Technical, empirical, and computational field notes on air quality dynamics, thermal radiometry, and planetary indicators.">
  <link rel="canonical" href="https://avnish36singh-arch.github.io/signal-earth-portal/notes/">
  <link rel="alternate" type="application/rss+xml" title="Signal Earth Notes RSS Feed" href="feed.xml">
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="../favicon-32.png">
  <link rel="stylesheet" href="../style.css">
  <style>
    .se-notes-index-wrap {{
      max-width: 860px;
      margin: 0 auto;
      padding: 3.5rem 1.5rem 5rem;
    }}
    .se-notes-page-header {{
      margin-bottom: 3rem;
      border-bottom: 1px solid var(--se-border);
      padding-bottom: 1.5rem;
    }}
    .se-notes-list {{
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }}
    .se-note-card {{
      background: var(--se-bg-surface);
      border: 1px solid var(--se-border);
      border-radius: var(--se-radius-md);
      padding: 1.75rem 2rem;
      transition: border-color 0.15s ease;
    }}
    .se-note-card:hover {{
      border-color: var(--se-text-primary);
    }}
    .se-note-card-meta {{
      font-family: var(--se-font-mono);
      font-size: 0.78rem;
      color: var(--se-text-muted);
      margin-bottom: 0.65rem;
    }}
    .se-note-card-title {{
      font-family: var(--se-font-serif);
      font-size: 1.45rem;
      font-weight: 700;
      line-height: 1.3;
      margin: 0 0 0.75rem;
    }}
    .se-note-card-title a {{
      color: var(--se-text-primary);
      text-decoration: none;
    }}
    .se-note-card-title a:hover {{
      text-decoration: underline;
    }}
    .se-note-card-excerpt {{
      font-size: 0.95rem;
      line-height: 1.6;
      color: var(--se-text-secondary);
      margin: 0 0 1.25rem;
    }}
    .se-note-card-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.82rem;
      font-family: var(--se-font-mono);
      border-top: 1px solid var(--se-border-subtle);
      padding-top: 0.75rem;
    }}
  </style>
</head>
<body>
  <header class="se-editorial-header">
    <div class="se-editorial-header-inner">
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <a href="../index.html" class="se-editorial-wordmark">Signal Earth</a>
        <span style="font-size: 0.75rem; font-family: var(--se-font-mono); color: var(--se-text-muted); text-transform: uppercase;">/ Notes</span>
      </div>
      <nav aria-label="Main Navigation">
        <ul class="se-editorial-nav-list">
          <li><a href="../index.html" class="se-editorial-nav-link">Globe</a></li>
          <li><a href="../analyses/index.html" class="se-editorial-nav-link">Analyses</a></li>
          <li><a href="../notes/index.html" class="se-editorial-nav-link active">Notes</a></li>
          <li><a href="../data.html" class="se-editorial-nav-link">Data</a></li>
          <li><a href="../about.html" class="se-editorial-nav-link">About</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main id="main">
    <div class="se-notes-index-wrap">
      <div class="se-notes-page-header">
        <h1 style="font-family: var(--se-font-serif); font-size: 2.2rem; margin: 0 0 0.5rem; color: var(--se-text-primary);">Analytical Field Notes</h1>
        <p style="font-size: 0.95rem; color: var(--se-text-secondary); margin: 0; line-height: 1.6;">
          Continuous technical notes, statistical calculations, and empirical audits. Every note requires an underlying site dataset, documented methodology, and open corrections link.
        </p>
      </div>

      <div class="se-notes-list">
{notes_items_html}
      </div>
    </div>
  </main>

  <footer class="se-editorial-footer" style="background: var(--se-bg-page); border-top: 1px solid var(--se-border); padding: 2.5rem 1.5rem 2rem;">
    <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; color: var(--se-text-muted); flex-wrap: wrap; gap: 1rem;">
      <div>&copy; 2026 Signal Earth. Maintained by Avnish Singh. No institutional affiliation with HBTU Kanpur.</div>
      <div>
        <a href="feed.xml" class="se-link">RSS Feed</a> &middot;
        <a href="../corrections.html" class="se-link">Corrections</a> &middot;
        <a href="../privacy.html" class="se-link">Privacy</a>
      </div>
    </div>
  </footer>
</body>
</html>
"""

def parse_markdown_note(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Assert no unicode em dash or en dash
    if "\u2014" in content:
        raise ValueError(f"Prohibited em dash (\\u2014) in {filepath}")
    if "\u2013" in content:
        raise ValueError(f"Prohibited en dash (\\u2013) in {filepath}")

    # Extract frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not fm_match:
        raise ValueError(f"Invalid or missing YAML frontmatter in {filepath}")

    fm_raw = fm_match.group(1)
    body_md = fm_match.group(2)

    metadata = {}
    for line in fm_raw.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            metadata[key.strip()] = val.strip()

    # Frontmatter validation
    required_keys = ["title", "date", "author", "sources", "data_link", "corrections_link"]
    for req in required_keys:
        if req not in metadata or not metadata[req]:
            raise ValueError(f"Missing required frontmatter key '{req}' in {filepath}")

    if metadata["author"] != "Avnish Singh":
        raise ValueError(f"Author must be 'Avnish Singh' in {filepath}, got '{metadata['author']}'")

    # Format date
    dt = datetime.strptime(metadata["date"], "%Y-%m-%d")
    metadata["formatted_date"] = dt.strftime("%B %d, %Y")
    metadata["dt"] = dt

    # Convert Markdown to HTML simply and reliably
    body_html = []
    lines = body_md.strip().split("\n")
    in_ul = False

    for line in lines:
        line_s = line.strip()
        if not line_s:
            if in_ul:
                body_html.append("</ul>")
                in_ul = False
            continue

        if line_s.startswith("## "):
            if in_ul:
                body_html.append("</ul>")
                in_ul = False
            heading_text = line_s[3:].strip()
            body_html.append(f"<h2>{html.escape(heading_text)}</h2>")
        elif line_s.startswith("- "):
            if not in_ul:
                body_html.append("<ul>")
                in_ul = True
            item_text = line_s[2:].strip()
            # replace markdown links [text](url)
            item_text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2" class="se-link">\1</a>', item_text)
            body_html.append(f"  <li>{item_text}</li>")
        else:
            if in_ul:
                body_html.append("</ul>")
                in_ul = False
            p_text = line_s
            p_text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2" class="se-link">\1</a>', p_text)
            body_html.append(f"<p>{p_text}</p>")

    if in_ul:
        body_html.append("</ul>")

    metadata["body_html"] = "\n".join(body_html)
    
    # Excerpt (first paragraph)
    for line in lines:
        if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("-"):
            metadata["excerpt"] = line.strip()
            break
    if "excerpt" not in metadata:
        metadata["excerpt"] = metadata["title"]
    is_draft = metadata.get("draft", "false").lower() == "true"
    metadata["is_draft"] = is_draft

    return metadata

def build_rss_feed(notes):
    items_xml = []
    # Do not publish notes marked as draft until user approves
    published_notes = [n for n in notes if not n.get("is_draft")]

    for note in published_notes:
        pub_date = note["dt"].strftime("%a, %d %b %Y 00:00:00 +0000")
        item = f"""    <item>
      <title>{html.escape(note['title'])}</title>
      <link>https://avnish36singh-arch.github.io/signal-earth-portal/notes/{note['slug']}.html</link>
      <guid>https://avnish36singh-arch.github.io/signal-earth-portal/notes/{note['slug']}.html</guid>
      <pubDate>{pub_date}</pubDate>
      <author>avnish36singh@gmail.com (Avnish Singh)</author>
      <description>{html.escape(note['excerpt'])}</description>
    </item>"""
        items_xml.append(item)

    last_build = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    feed_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Signal Earth Notes</title>
    <link>https://avnish36singh-arch.github.io/signal-earth-portal/notes/</link>
    <description>Technical, empirical, and computational field notes on air quality dynamics, thermal radiometry, and planetary indicators.</description>
    <language>en-us</language>
    <lastBuildDate>{last_build}</lastBuildDate>
    <atom:link href="https://avnish36singh-arch.github.io/signal-earth-portal/notes/feed.xml" rel="self" type="application/rss+xml" />
{chr(10).join(items_xml)}
  </channel>
</rss>
"""
    return feed_content

def main():
    os.makedirs(NOTES_OUT_DIR, exist_ok=True)
    os.makedirs("data", exist_ok=True)

    md_files = glob.glob(os.path.join(NOTES_SRC_DIR, "*.md"))
    if not md_files:
        print("No markdown note files found in", NOTES_SRC_DIR)
        return

    notes = []
    for fp in md_files:
        slug = os.path.splitext(os.path.basename(fp))[0]
        note_data = parse_markdown_note(fp)
        note_data["slug"] = slug
        notes.append(note_data)

    # Sort descending by date
    notes.sort(key=lambda x: x["dt"], reverse=True)

    # Render each note page
    for note in notes:
        draft_banner_html = ""
        if note.get("is_draft"):
            draft_banner_html = """      <aside class="se-draft-banner" style="background: rgba(234, 179, 8, 0.12); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: var(--se-radius-sm); padding: 0.85rem 1.25rem; margin-bottom: 2rem; font-size: 0.88rem; color: #eab308; display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-weight: 700; text-transform: uppercase; font-family: var(--se-font-mono); font-size: 0.75rem; background: #eab308; color: #000; padding: 0.15rem 0.4rem; border-radius: 2px;">Draft</span>
        <span>This analytical field note is currently undergoing verification and review. It is withheld from official RSS syndication.</span>
      </aside>"""

        out_html = NOTE_TEMPLATE.format(
            title=html.escape(note["title"]),
            description=html.escape(note["excerpt"]),
            slug=note["slug"],
            date=note["date"],
            formatted_date=note["formatted_date"],
            author=html.escape(note["author"]),
            sources=html.escape(note["sources"]),
            data_link=note["data_link"],
            draft_banner_html=draft_banner_html,
            body_html=note["body_html"]
        )
        out_path = os.path.join(NOTES_OUT_DIR, f"{note['slug']}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(out_html)
        print(f"Generated note page: {out_path}")

    # Render notes index
    note_cards_html = []
    for note in notes:
        draft_badge = ' <span style="font-size: 0.7rem; font-family: var(--se-font-mono); background: rgba(234, 179, 8, 0.2); color: #eab308; padding: 0.15rem 0.45rem; border-radius: 3px; text-transform: uppercase; font-weight: 600;">Draft</span>' if note.get("is_draft") else ""
        card = f"""        <article class="se-note-card">
          <div class="se-note-card-meta">
            <span>{note['formatted_date']}</span> &middot;
            <span>{html.escape(note['sources'])}</span>{draft_badge}
          </div>
          <h2 class="se-note-card-title">
            <a href="{note['slug']}.html">{html.escape(note['title'])}</a>
          </h2>
          <p class="se-note-card-excerpt">
            {html.escape(note['excerpt'])}
          </p>
          <div class="se-note-card-footer">
            <span>By {html.escape(note['author'])}</span>
            <a href="{note['slug']}.html" class="se-link">Read note &rarr;</a>
          </div>
        </article>"""
        note_cards_html.append(card)

    index_html = INDEX_TEMPLATE.format(notes_items_html="\n".join(note_cards_html))
    index_out = os.path.join(NOTES_OUT_DIR, "index.html")
    with open(index_out, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"Generated notes index: {index_out}")

    # Generate feed.xml
    feed_xml = build_rss_feed(notes)
    with open(FEED_OUT_PATH, "w", encoding="utf-8") as f:
        f.write(feed_xml)
    print(f"Generated RSS feed: {FEED_OUT_PATH}")

    # Export data/notes.json
    export_notes = [
        {
            "slug": n["slug"],
            "title": n["title"],
            "date": n["date"],
            "formatted_date": n["formatted_date"],
            "author": n["author"],
            "sources": n["sources"],
            "data_link": n["data_link"],
            "excerpt": n["excerpt"],
            "url": f"notes/{n['slug']}.html"
        }
        for n in notes
    ]
    with open(NOTES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(export_notes, f, indent=2)
    print(f"Exported notes metadata: {NOTES_JSON_PATH}")

if __name__ == "__main__":
    main()
