"""Cache current Forever tooltips and icons; retain successful records on errors."""
import argparse
import concurrent.futures
import datetime
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'data/item-tooltip-snapshot.json'
parser = argparse.ArgumentParser()
parser.add_argument('--refresh', action='store_true')
args = parser.parse_args()
snapshot = json.loads(CACHE.read_text()) if CACHE.exists() else {'items': {}}
guide = json.loads((ROOT / 'data/guide.json').read_text())
ids = sorted({str(item['id']) for dungeon in guide['dungeons'] for quest in dungeon['quests'] for item in quest['rewards']})
today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()

def download(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()

def fetch(item_id):
    cached = snapshot['items'].get(item_id)
    try:
        if not cached or args.refresh:
            data = json.loads(download('https://nether.wowhead.com/forever/tooltip/item/' + item_id))
            if not isinstance(data.get('tooltip'), str) or not data['tooltip']:
                raise ValueError('Missing tooltip')
            cached = {key: data[key] for key in ['name', 'quality', 'icon', 'tooltip'] if key in data}
            cached.update(checked=today, source='https://www.wowhead.com/forever/item=' + item_id)
        icon = cached.get('icon', '').lower()
        if re.fullmatch(r'[a-z0-9_-]+', icon):
            path = ROOT / 'assets/icons' / (icon + '.jpg')
            if not path.exists():
                image = download('https://wow.zamimg.com/images/wow/icons/large/' + icon + '.jpg')
                if not image.startswith(b'\xff\xd8\xff'):
                    raise ValueError('Icon response is not a JPEG')
                path.write_bytes(image)
        return item_id, cached, None
    except Exception as error:
        return item_id, cached, str(error)

(ROOT / 'assets/icons').mkdir(parents=True, exist_ok=True)
failures = []
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for item_id, data, error in pool.map(fetch, ids):
        if data:
            snapshot['items'][item_id] = data
        if error:
            failures.append({'id': item_id, 'error': error, 'retained': bool(data)})
snapshot['lastAttempt'] = today
snapshot['failures'] = failures
CACHE.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n')
print('Cached', len(snapshot['items']), 'of', len(ids), 'unique item tooltips;', len(failures), 'fetch errors')
for error in failures:
    print(json.dumps(error))
