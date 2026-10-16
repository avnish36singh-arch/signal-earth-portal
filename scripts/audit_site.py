import os
import glob
import re
from urllib.parse import urlparse

def audit_repo():
    html_files = glob.glob('**/*.html', recursive=True)
    broken_links = []
    missing_alt = []
    total_links = 0
    total_imgs = 0

    for hf in html_files:
        if '.git' in hf or 'node_modules' in hf or 'signal-earth-portal' in hf:
            continue
        hf_norm = os.path.normpath(hf)
        with open(hf, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # check links
        links = re.findall(r'href=["\']([^"\']+)["\']', content)
        for link in links:
            if link.startswith(('http://', 'https://', 'mailto:', 'javascript:', '#', 'tel:')):
                continue
            total_links += 1
            path_part = link.split('#')[0].split('?')[0]
            if not path_part:
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(hf), path_part))
            if not os.path.exists(target):
                broken_links.append((hf_norm, link, target))

        # check images
        imgs = re.findall(r'<img\s+([^>]+)>', content, re.IGNORECASE)
        for img_tag in imgs:
            total_imgs += 1
            src_m = re.search(r'src=["\']([^"\']*)["\']', img_tag)
            alt_m = re.search(r'alt=["\']([^"\']*)["\']', img_tag)
            src = src_m.group(1).strip() if src_m else ''
            alt = alt_m.group(1) if alt_m else None
            if alt is None:
                missing_alt.append((hf_norm, src or '<dynamic-src>', "missing alt attribute"))
            elif alt.strip() == "" and 'aria-hidden="true"' not in img_tag and 'role="presentation"' not in img_tag:
                missing_alt.append((hf_norm, src or '<dynamic-src>', "empty alt without aria-hidden"))

            # check if local src exists
            if src and not src.startswith(('http://', 'https://', 'data:')):
                src_path = src.split('?')[0].split('#')[0]
                img_target = os.path.normpath(os.path.join(os.path.dirname(hf), src_path))
                if not os.path.exists(img_target):
                    broken_links.append((hf_norm, src, img_target))

    print(f"Total HTML files checked: {len(html_files)}")
    print(f"Total internal links checked: {total_links}")
    print(f"Broken links found: {len(broken_links)}")
    for src, link, tgt in broken_links:
        print(f"  [BROKEN LINK] In '{src}': href/src '{link}' -> missing target '{tgt}'")

    print(f"\nTotal images checked: {total_imgs}")
    print(f"Images missing alt attribute: {len(missing_alt)}")
    for src, img_src, reason in missing_alt:
        print(f"  [MISSING ALT] In '{src}': img '{img_src}' ({reason})")

if __name__ == '__main__':
    audit_repo()
