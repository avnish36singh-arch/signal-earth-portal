import os
import re
from collections import Counter

ROOT_DIR = r"b:\movies\signal earth"

html_files = []
for dirpath, _, filenames in os.walk(ROOT_DIR):
    if any(ign in dirpath for ign in [".git", "node_modules", ".agents", ".gemini", "tmp", "scratch"]):
        continue
    for fn in filenames:
        if fn.endswith(".html"):
            html_files.append(os.path.join(dirpath, fn))

broken = []
link_pattern = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)

for src in html_files:
    with open(src, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    src_dir = os.path.dirname(src)
    for m in link_pattern.finditer(content):
        href = m.group(1).strip()
        if any(href.startswith(p) for p in ["http://", "https://", "mailto:", "tel:", "javascript:", "#", "data:"]):
            continue
        clean = href.split("?")[0].split("#")[0]
        if not clean:
            continue
        if clean.startswith("/"):
            tgt = os.path.join(ROOT_DIR, clean.lstrip("/"))
        else:
            tgt = os.path.join(src_dir, clean)
        tgt_norm = os.path.normpath(tgt)
        exists = (
            os.path.exists(tgt_norm)
            or os.path.exists(tgt_norm + ".html")
            or (os.path.isdir(tgt_norm) and os.path.exists(os.path.join(tgt_norm, "index.html")))
            or (not tgt_norm.endswith(".html") and os.path.exists(os.path.join(tgt_norm, "index.html")))
        )
        if not exists:
            broken.append((os.path.relpath(src, ROOT_DIR), href, os.path.relpath(tgt_norm, ROOT_DIR)))

print(f"Total broken: {len(broken)}")
counts = Counter([b[1] for b in broken])
for h, c in counts.most_common(25):
    print(f"  {c}x: '{h}'")

print("\nSample sources:")
for src, href, tgt in broken[:15]:
    print(f"  In {src}: '{href}' -> '{tgt}'")
