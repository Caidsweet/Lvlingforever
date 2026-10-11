"""Cache missing Forever recipe snapshots and original icons; build offline afterwards."""
import concurrent.futures
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'data/recipe-research'
NAMES = ['alchemy','blacksmithing','enchanting','engineering','leatherworking','tailoring','herbalism','mining','skinning','cooking','first-aid','fishing']

def download(url):
    request = urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(request,timeout=25) as response: return response.read()

def parse_wowhead(text):
    match = re.search(r'var listviewspells = (\[.*?\]);',text,re.S)
    if not match: raise ValueError('Spell list not found')
    # Listview data adds unquoted quality/popularity keys; never execute page JavaScript.
    literal = re.sub(r'(?<=[,{])\s*(quality|popularity)\s*:',r'"\1":',match.group(1))
    spells = json.loads(literal)
    return {'spells':spells}

def fetch_profession(name):
    kind = 'secondary-skills' if name in ['cooking','first-aid','fishing'] else 'professions'
    url = f'https://www.wowhead.com/forever/spells/{kind}/{name}'
    path = RAW/f'wowhead/{name}.json'
    cached_html = RAW/f'{name}.html'
    if path.exists():
        data = json.loads(path.read_text())
    else:
        text = cached_html.read_text() if cached_html.exists() else download(url).decode()
        data = parse_wowhead(text)
        data.update(source=url,checked='2026-10-11')
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    fdb = RAW/f'foreverdb/{name}.json'
    if not fdb.exists():
        body = download(f'https://foreverdb.net/data/professions/{name}.json')
        parsed = json.loads(body)
        if not parsed.get('recipes'): raise ValueError(f'No {name} recipes')
        fdb.parent.mkdir(parents=True,exist_ok=True);fdb.write_bytes(body)
    return name,len(data['spells'])

def fetch_icon(icon):
    dest = ROOT/f'assets/professions/{icon}.webp'
    if dest.exists(): return True
    try:
        data = download(f'https://foreverdb.net/icons/{icon}.webp')
        if data[:4]!=b'RIFF' or data[8:12]!=b'WEBP': raise ValueError('Not a WebP icon')
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);return True
    except Exception as exc: print('Icon unavailable:',icon,type(exc).__name__,flush=True);return False

def main():
    index_path = RAW/'foreverdb/index.json'
    if not index_path.exists():
        index_path.parent.mkdir(parents=True,exist_ok=True)
        index_path.write_bytes(download('https://foreverdb.net/data/professions.json'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(fetch_profession,NAMES): print('Snapshot',*result,flush=True)
    index = json.loads(index_path.read_text());icons = set(p['ic'] for p in index['professions'])
    for name in NAMES:
        data = json.loads((RAW/f'foreverdb/{name}.json').read_text())
        icons.update(i[1] for i in data['items'].values() if i[1])
        icons.update(r['ic'] for r in data['recipes'] if r.get('ic'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = pool.map(fetch_icon,sorted(icons))
        success = 0
        for count,result in enumerate(results,1):
            success += result
            if count%100==0 or count==len(icons): print('Icons',count,'/',len(icons),'cached:',success,flush=True)

if __name__=='__main__': main()
