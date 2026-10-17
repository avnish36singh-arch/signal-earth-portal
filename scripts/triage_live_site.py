import urllib.request
import re

base_url = 'https://signalearth.netlify.app/'
print(f"Checking live Netlify deployment at {base_url}...")

req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
    print("Homepage loaded successfully.")
except Exception as e:
    print(f"Failed to load homepage: {e}")
    exit(1)

# Extract scripts, links, images
scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
styles = re.findall(r'<link[^>]+href=["\']([^"\']+)["\']', html)
images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)

all_assets = list(set(scripts + styles + images))
print(f"Total unique referenced assets: {len(all_assets)}")

errors = []
success = 0
for a in sorted(all_assets):
    if a.startswith('data:'):
        continue
    target = a if a.startswith(('http://', 'https://')) else (base_url + a.lstrip('/'))
    try:
        r = urllib.request.urlopen(urllib.request.Request(target, headers={'User-Agent': 'Mozilla/5.0'}), timeout=5)
        print(f"  [{r.status}] {a}")
        success += 1
    except Exception as e:
        print(f"  [FAILED] {a} -> {e}")
        errors.append((a, str(e)))

# Test API endpoint
api_url = base_url + "api/key-numbers"
try:
    r = urllib.request.urlopen(urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=5)
    print(f"\nAPI endpoint {api_url}: STATUS {r.status}")
except Exception as e:
    print(f"\nAPI endpoint {api_url}: FAILED -> {e}")

print(f"\nSummary: {success} OK, {len(errors)} Failed")
