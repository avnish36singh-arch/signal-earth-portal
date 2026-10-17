"""
Build Credits Page Generator for Signal Earth.
Compiles credits.html from credits.json and software provenance metadata.
Strict typography: ZERO EM DASHES.
"""

import json
import os
import html

def build_credits_page():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    credits_json_path = os.path.join(root, 'credits.json')
    output_html_path = os.path.join(root, 'credits.html')

    with open(credits_json_path, 'r', encoding='utf-8') as f:
        credits_data = json.load(f)

    # Categorize items
    satellite_items = []
    figures_items = []
    photo_items = []

    for item in credits_data:
        sensor = item.get('sensor', '')
        file_path = item.get('file', '')
        if 'MODIS' in sensor or 'Landsat' in sensor or 'Satellite' in sensor or 'TIRS' in sensor:
            satellite_items.append(item)
        elif file_path.endswith('.png') or 'delhi/' in file_path or 'kanpur/' in file_path or 'Figure' in item.get('title', ''):
            figures_items.append(item)
        else:
            photo_items.append(item)

    def render_items(items):
        html_cards = []
        for it in items:
            title = html.escape(it.get('title', 'Untitled Asset'))
            f_path = html.escape(it.get('file', ''))
            date_str = html.escape(it.get('date', 'Unknown'))
            sensor_str = html.escape(it.get('sensor', 'N/A'))
            creator = html.escape(it.get('creator', 'Signal Earth'))
            lic = html.escape(it.get('license', 'Open License'))
            s_url = it.get('source_url', '#')
            credit_txt = html.escape(it.get('credit_text', ''))

            card = f"""
        <article class="se-card-panel" style="background: var(--se-bg-surface); border: 1px solid var(--se-border); border-radius: var(--se-radius-md); padding: 1.25rem; margin-bottom: 1rem;">
          <h3 style="font-family: var(--se-font-serif); font-size: 1.1rem; font-weight: 600; margin: 0 0 0.5rem; color: var(--se-text-primary);">{title}</h3>
          <p style="font-size: 0.85rem; line-height: 1.5; color: var(--se-text-secondary); margin: 0 0 0.75rem;">
            <strong>Asset Path:</strong> <code>{f_path}</code><br>
            <strong>Observation Date:</strong> {date_str}<br>
            <strong>Instrument / Method:</strong> {sensor_str}<br>
            <strong>Custodian:</strong> {creator}<br>
            <strong>License:</strong> {lic}<br>
            <strong>Source Reference:</strong> <a href="{s_url}" target="_blank" rel="noopener noreferrer" class="se-link">Direct Source Link &rarr;</a>
          </p>
          <div style="font-family: var(--se-font-mono); font-size: 0.75rem; color: var(--se-text-muted); background: var(--se-bg-page); padding: 0.4rem 0.6rem; border-radius: var(--se-radius-sm); border: 1px solid var(--se-border);">
            {credit_txt}
          </div>
        </article>"""
            html_cards.append(card)
        return "\n".join(html_cards)

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Credits &amp; Citation | Signal Earth</title>
  <meta name="description" content="Registry of satellite imagery, software libraries, scientific citations, and provenance credits for Signal Earth.">
  <link rel="canonical" href="https://signalearth.netlify.app/credits.html">
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <link rel="manifest" href="site.webmanifest">
  <meta property="og:title" content="Credits &amp; Citation | Signal Earth">
  <meta property="og:description" content="Registry of satellite imagery, software libraries, and academic citation formats.">
  <meta property="og:url" content="https://signalearth.netlify.app/credits.html">
  <meta property="og:type" content="article">
  <link rel="stylesheet" href="style.css">
  <script src="assets/theme.js"></script>
</head>
<body class="se-editorial-page">
  <a href="#main" class="skip-link">Skip to content</a>

  <!-- Standardized 5-Item Editorial Header -->
  <header class="se-editorial-header" id="se-header">
    <div class="se-editorial-container">
      <div class="se-editorial-header-inner">
        <div class="se-editorial-wordmark-wrap">
          <a href="index.html" class="se-editorial-wordmark">Signal Earth</a>
          <span class="se-wordmark-badge">Credits</span>
        </div>
        <div class="se-editorial-header-right">
          <nav class="se-editorial-nav" aria-label="Main Navigation">
            <ul class="se-editorial-nav-list">
              <li><a href="index.html" class="se-editorial-nav-link">Globe</a></li>
              <li><a href="rankings.html" class="se-editorial-nav-link">Rankings</a></li>
              <li><a href="compare.html" class="se-editorial-nav-link">Compare</a></li>
              <li><a href="data.html" class="se-editorial-nav-link">Data</a></li>
              <li><a href="methodology.html" class="se-editorial-nav-link">Methodology</a></li>
              <li><a href="about.html" class="se-editorial-nav-link">About</a></li>
            </ul>
          </nav>
          <button type="button" id="se-theme-toggle" class="se-theme-toggle-btn" aria-label="Toggle theme mode" title="Switch light / dark mode">
            <svg class="se-theme-icon-sun" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="5"></circle>
              <line x1="12" y1="1" x2="12" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="23"></line>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
              <line x1="1" y1="12" x2="3" y2="12"></line>
              <line x1="21" y1="12" x2="23" y2="12"></line>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
            <svg class="se-theme-icon-moon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
            <span class="se-theme-label">Theme</span>
          </button>
        </div>
      </div>
    </div>
  </header>

  <main id="main" class="se-container-narrow se-container-py">
    <header class="se-header-mb">
      <span class="section-kicker">Provenance and Attribution</span>
      <h1 class="editorial-headline se-headline-clamp">
        Credits and Citation
      </h1>
      <p class="se-hero-dek">
        Every photograph, satellite scene, software library, and analytical figure on Signal Earth is credited below with its acquisition date, sensing instrument, custodial organization, and reuse license.
      </p>
    </header>

    <!-- How to Cite Signal Earth -->
    <section class="se-content-section" style="margin-bottom: 3rem;">
      <span class="section-kicker">01 : Academic Citation</span>
      <h2 class="editorial-headline se-content-h2">How to Cite Signal Earth</h2>
      <p class="se-content-p">
        If you use Signal Earth analyses, processed data, or visualizations in academic research, reports, or journalism, please cite the project as follows:
      </p>

      <div style="background: var(--se-bg-surface); border: 1px solid var(--se-border); border-radius: var(--se-radius-md); padding: 1.5rem; margin-bottom: 1.5rem;">
        <h3 style="font-family: var(--se-font-sans); font-size: 0.95rem; font-weight: 700; margin: 0 0 0.5rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--se-teal-live);">
          APA Format (7th Edition)
        </h3>
        <p style="font-family: var(--se-font-serif); font-size: 0.95rem; line-height: 1.6; margin: 0; color: var(--se-text-primary);">
          Singh, A. (2026). <em>Signal Earth: Independent Planetary Environmental Database and Geospatial Analyses</em>. Signal Earth. https://signalearth.netlify.app/
        </p>
      </div>

      <div style="background: var(--se-bg-surface); border: 1px solid var(--se-border); border-radius: var(--se-radius-md); padding: 1.5rem;">
        <h3 style="font-family: var(--se-font-sans); font-size: 0.95rem; font-weight: 700; margin: 0 0 0.5rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--se-teal-live);">
          BibTeX Entry
        </h3>
        <pre style="background: var(--se-bg-page); border: 1px solid var(--se-border); border-radius: var(--se-radius-sm); padding: 1rem; font-family: var(--se-font-mono); font-size: 0.8rem; line-height: 1.5; color: var(--se-text-primary); overflow-x: auto; margin: 0;">@misc{{singh2026signalearth,
  author = {{Singh, Avnish}},
  title = {{Signal Earth: Independent Planetary Environmental Database and Geospatial Analyses}},
  year = {{2026}},
  howpublished = {{\\url{{https://signalearth.netlify.app/}}}},
  note = {{Civil Engineering undergraduate, HBTU Kanpur}}
}}</pre>
      </div>
    </section>

    <!-- Software and Technology Stack Credits -->
    <section class="se-content-section" style="margin-bottom: 3rem;">
      <span class="section-kicker">02 : Software &amp; Frameworks</span>
      <h2 class="editorial-headline se-content-h2">Open Source Software and Frameworks</h2>
      <p class="se-content-p">
        Signal Earth is built entirely with open-source web standards and geospatial rendering libraries:
      </p>

      <div class="se-table-wrap" style="overflow-x: auto; margin: 1.5rem 0;">
        <table class="se-table" style="width: 100%; border-collapse: collapse;">
          <thead>
            <tr style="border-bottom: 2px solid var(--se-border); text-align: left;">
              <th style="padding: 0.75rem;">Component</th>
              <th style="padding: 0.75rem;">Version / Source</th>
              <th style="padding: 0.75rem;">License</th>
              <th style="padding: 0.75rem;">Role in Signal Earth</th>
            </tr>
          </thead>
          <tbody>
            <tr style="border-bottom: 1px solid var(--se-border);">
              <td style="padding: 0.75rem;"><strong>Three.js</strong></td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">r160 (mrdoob)</td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">MIT License</td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">WebGL 3D scene graph, camera projection, and atmospheric glow shader.</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--se-border);">
              <td style="padding: 0.75rem;"><strong>Globe.gl</strong></td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">v2.32.2 (Vasco Asturiano)</td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">MIT License</td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">Country polygon mesh extrusion, hover tooltips, and click-navigation.</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--se-border);">
              <td style="padding: 0.75rem;"><strong>Natural Earth</strong></td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">1:110m Cultural Vectors</td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">Public Domain</td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">Sovereign country boundary geometries and centroid coordinates.</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--se-border);">
              <td style="padding: 0.75rem;"><strong>NASA Blue Marble</strong></td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">Visible Earth / MODIS</td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">Public Domain / NASA Open Data</td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">Planetary surface texture base and night lights radiance maps.</td>
            </tr>
            <tr>
              <td style="padding: 0.75rem;"><strong>Open Typography</strong></td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">Outfit, Inter, JetBrains Mono</td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">SIL Open Font License 1.1</td>
              <td style="padding: 0.75rem; font-size: 0.85rem;">High-legibility editorial headings, body text, and tabular telemetry.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Satellite Imagery Registry -->
    <section class="se-content-section" style="margin-bottom: 3rem;">
      <span class="section-kicker">03 : Satellite Earth Observation</span>
      <h2 class="editorial-headline se-content-h2">Satellite Imagery Registry</h2>
      <div class="se-card-stack">
        {render_items(satellite_items)}
      </div>
    </section>

    <!-- Analytical Figures Registry -->
    <section class="se-content-section" style="margin-bottom: 3rem;">
      <span class="section-kicker">04 : Scientific Figures</span>
      <h2 class="editorial-headline se-content-h2">Analytical Charts and Diagnostic Figures</h2>
      <div class="se-card-stack">
        {render_items(figures_items)}
      </div>
    </section>

    <!-- Photography Registry -->
    <section class="se-content-section" style="margin-bottom: 3rem;">
      <span class="section-kicker">05 : Photographic Perspectives</span>
      <h2 class="editorial-headline se-content-h2">Photographic Assets</h2>
      <div class="se-card-stack">
        {render_items(photo_items)}
      </div>
    </section>

  </main>

  <!-- Standardized Editorial Footer -->
  <footer class="se-editorial-footer">
    <div class="se-editorial-container">
      <div class="se-editorial-footer-grid" style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; margin-bottom: 2rem;">
        <div>
          <div style="font-family: var(--se-font-serif); font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--se-text-primary);">
            Signal Earth
          </div>
          <p style="font-size: 0.9rem; line-height: 1.6; color: var(--se-text-secondary); max-width: 50ch; margin: 0 0 1rem;">
            Avnish Singh &middot; Civil Engineering undergraduate, HBTU Kanpur, focusing on environmental engineering &middot; Contact: <a href="mailto:avnish36singh@gmail.com" class="se-link">avnish36singh@gmail.com</a>
          </p>
          <div style="font-size: 0.85rem;">
            <a href="credits.html" class="se-link">How to cite</a> &middot;
            <a href="methodology.html" class="se-link">Methodology</a> &middot;
            <a href="sources.html" class="se-link">Data Sources</a> &middot;
            <a href="corrections.html" class="se-link">Corrections Log</a> &middot;
            <a href="known-problems.html" class="se-link">Known Problems</a> &middot;
            <a href="numbers_ledger.csv" class="se-link" download>Numbers Ledger (CSV)</a> &middot;
            <a href="https://github.com/avnish36singh-arch/signal-earth-portal" class="se-link" target="_blank" rel="noopener noreferrer">GitHub</a>
          </div>
        </div>
        <div>
          <div style="font-size: 0.8rem; font-family: var(--se-font-mono); text-transform: uppercase; color: var(--se-text-muted); margin-bottom: 0.5rem;">
            Attribution &amp; Hosting
          </div>
          <p style="font-size: 0.82rem; line-height: 1.5; color: var(--se-text-secondary); margin: 0 0 0.5rem;">
            Contains modified Copernicus Climate Change Service information [2026]. Content licensed under CC BY 4.0; code licensed under MIT.
          </p>
          <p style="font-size: 0.82rem; line-height: 1.5; color: var(--se-text-muted); margin: 0;">
            Hosted on Netlify. Static build with zero cookies, zero trackers, and zero server-side state.
          </p>
        </div>
      </div>
      <div class="se-editorial-footer-bottom">
        <div>&copy; 2026 Signal Earth. Open-access empirical environmental telemetry.</div>
        <div><a href="privacy.html" class="se-link">Privacy Policy</a> &middot; <a href="terms.html" class="se-link">Terms of Use</a> &middot; <a href="licenses.html" class="se-link">Licenses</a></div>
      </div>
    </div>
  </footer>
</body>
</html>
"""
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(page_html)

    print(f"Successfully compiled credits.html ({len(page_html)} bytes) with {len(credits_data)} items.")

if __name__ == '__main__':
    build_credits_page()
