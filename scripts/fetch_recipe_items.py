"""Resolve missing recipe-item facts using current Forever IDs; never substitute Era items."""
import concurrent.futures
import datetime
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT/'data/recipe-item-snapshot.json'


def main():
    catalogue = json.loads((ROOT/'data/recipe-catalogue.json').read_text())
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {'items': {}}
    needed = set()
    for profession in catalogue['professions']:
        for recipe in profession['recipes']:
            ids = ([recipe['creates'][0]] if recipe['creates'] else []) + [i for i, _ in recipe['reagents']] + recipe['recipeItems'] + recipe['hiddenRecipeItems']
            needed.update(str(i) for i in ids if str(i) not in catalogue['items'])
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()

    def download(url):
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15) as response:
            return response.read()

    def fetch(item_id):
        existing = cache['items'].get(item_id)
        try:
            if existing:
                result = existing
            else:
                data = json.loads(download('https://nether.wowhead.com/forever/tooltip/item/'+item_id))
                if not data.get('name') or not re.fullmatch(r'[a-zA-Z0-9_-]+', data.get('icon', '')):
                    raise ValueError('No published item name/icon')
                result = {k: data[k] for k in ['name', 'icon', 'quality'] if k in data}
                result.update(checked=today, source='https://www.wowhead.com/forever/item='+item_id, available=not bool(re.search(r'deprecated|obsolete|unused', data['name'], re.I)))
            icon = result.get('icon')
            if icon:
                icon = icon.lower()
                path = ROOT/'assets/icons'/f'{icon}.jpg'
                if not path.exists():
                    image = download('https://wow.zamimg.com/images/wow/icons/large/'+icon+'.jpg')
                    if not image.startswith(b'\xff\xd8\xff'): raise ValueError('Invalid icon JPEG')
                    path.write_bytes(image)
            return item_id, result
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return item_id, existing or {'available': False, 'checked': today, 'source': 'https://www.wowhead.com/forever/item='+item_id, 'reason': 'No published Forever item record (HTTP 404)'}
            return item_id, existing or {'available': False, 'checked': today, 'reason': 'Fetch failed: HTTP '+str(error.code)}
        except Exception as error:
            return item_id, existing or {'available': False, 'checked': today, 'reason': 'Fetch failed: '+type(error).__name__}

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for count, (item_id, result) in enumerate(pool.map(fetch, sorted(needed)), 1):
            cache['items'][item_id] = result
            if count % 50 == 0: print('Checked', count, '/', len(needed), flush=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2)+'\n')
    print('Resolved', sum(bool(i.get('icon')) for i in cache['items'].values()), 'item icons;', sum(not i.get('available') for i in cache['items'].values()), 'unavailable item records', flush=True)


if __name__ == '__main__': main()
