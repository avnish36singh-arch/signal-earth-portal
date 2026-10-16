import json
import urllib.request
import os

with open('data/regions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

regions = data['regions']
print(f'Fetching accurate NASA GIBS satellite imagery for {len(regions)} regions...')
os.makedirs('assets/regions', exist_ok=True)

success = 0
for r in regions:
    bbox = r.get('bbox', [r['lat']-1.5, r['lon']-1.5, r['lat']+1.5, r['lon']+1.5])
    min_lat, min_lon, max_lat, max_lon = bbox[0], bbox[1], bbox[2], bbox[3]
    
    # Specific date where atmosphere is clear/characteristic for each region
    # For India/Kanpur/Delhi: winter haze season (Nov/Dec)
    # For Arctic/Greenland: summer sea ice/melt (Aug)
    # For Australia: clear marine observation (Sept)
    # For Sahel/Drought: dry season
    date_str = '2023-11-15' if r['id'] in ['kanpur', 'delhi', 'himalayas'] else \
               '2023-08-15' if r['id'] in ['arctic', 'greenland'] else \
               '2023-09-20' if r['id'] in ['barrier-reef', 'tuvalu'] else \
               '2023-07-25'
    
    layer = r.get('gibs_layer', 'MODIS_Terra_CorrectedReflectance_TrueColor')
    
    # NASA GIBS WMS 1.3.0
    url = (
        f"https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?"
        f"SERVICE=WMS&REQUEST=GetMap&LAYERS={layer}&VERSION=1.3.0&"
        f"FORMAT=image/jpeg&TRANSPARENT=true&WIDTH=640&HEIGHT=400&"
        f"CRS=EPSG:4326&BBOX={min_lat},{min_lon},{max_lat},{max_lon}&TIME={date_str}"
    )
    
    # 10 years earlier comparison date
    date_10yr = f"{int(date_str[:4]) - 10}{date_str[4:]}"
    url_10yr = (
        f"https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?"
        f"SERVICE=WMS&REQUEST=GetMap&LAYERS={layer}&VERSION=1.3.0&"
        f"FORMAT=image/jpeg&TRANSPARENT=true&WIDTH=640&HEIGHT=400&"
        f"CRS=EPSG:4326&BBOX={min_lat},{min_lon},{max_lat},{max_lon}&TIME={date_10yr}"
    )
    
    path_now = os.path.join('assets', 'regions', f"{r['id']}.jpg")
    path_10yr = os.path.join('assets', 'regions', f"{r['id']}_10yr.jpg")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) SignalEarth/2.0'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read()
            if resp.status == 200 and len(content) > 1500 and resp.headers.get('Content-Type') == 'image/jpeg':
                with open(path_now, 'wb') as out:
                    out.write(content)
                print(f"  [SAVED] {r['id']}: {len(content)} bytes ({date_str}) -> {path_now}")
                success += 1
            else:
                print(f"  [WARN] {r['id']} returned non-image: {resp.status}, size {len(content)}")
    except Exception as e:
        print(f"  [ERR] {r['id']} ({date_str}): {e}")

    try:
        req_10yr = urllib.request.Request(url_10yr, headers=headers)
        with urllib.request.urlopen(req_10yr, timeout=12) as resp_10yr:
            content_10yr = resp_10yr.read()
            if resp_10yr.status == 200 and len(content_10yr) > 1500:
                with open(path_10yr, 'wb') as out_10yr:
                    out_10yr.write(content_10yr)
                print(f"  [SAVED 10YR] {r['id']}_10yr: {len(content_10yr)} bytes ({date_10yr}) -> {path_10yr}")
    except Exception as e:
        print(f"  [ERR 10YR] {r['id']}_10yr: {e}")

print(f"Finished: {success}/{len(regions)} primary images saved.")
