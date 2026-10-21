import urllib.request
import json

indicators = [
    'SP.POP.TOTL',
    'EN.POP.DNST',
    'SP.URB.TOTL.IN.ZS',
    'NY.GDP.PCAP.CD',
    'AG.LND.TOTL.K2'
]

for ind in indicators:
    url = f"https://api.worldbank.org/v2/indicator/{ind}?format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "SignalEarthBot/1.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            info = data[1][0]
            print(f"[{ind}] {info['name']}")
            print(f"  Organization: {info.get('sourceOrganization', 'N/A')}")
            print(f"  Source note: {info.get('sourceNote', '')[:120]}...")
    except Exception as e:
        print(f"[{ind}] ERROR: {e}")
