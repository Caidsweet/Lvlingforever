"""Build a small standalone review page; leave the site entry point untouched.

Large recipe facts are compressed data, not a giant JavaScript object literal.
Original game maps and icons load from their source only when displayed.
"""
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'forever-guide-classic-v12.html'


def read_constant(html, name, following):
    start = html.index('const ' + name + '=')
    end = html.index('\n' + following, start)
    value = html[start + len('const ' + name + '='):end].rstrip(';')
    return start, end, json.loads(value)


def main():
    html = (ROOT / '.pages-build/standalone.html').read_text()
    start, end, crafting = read_constant(html, 'CRAFTING', 'const PROFESSIONS=')
    crafting['icons'] = {icon: f'https://foreverdb.net/icons/{icon}.webp' if icon.isdigit() else f'https://wow.zamimg.com/images/wow/icons/large/{icon}.jpg' for icon in crafting['icons']}
    packed = base64.b64encode(gzip.compress(json.dumps(crafting, ensure_ascii=False, separators=(',', ':')).encode(), mtime=0)).decode()
    # Keep the expensive catalogue out of both the JS parser and initial rendering.
    declaration = 'let CRAFTING=null;\nconst craftingPacked="' + packed + '";\n' + '''let craftingLoad=null;
function ensureCraftingData(){
 if(CRAFTING)return Promise.resolve(CRAFTING);
 if(!craftingLoad)craftingLoad=(async()=>{
  if(typeof DecompressionStream!=='function')throw Error('This preview requires a current browser.');
  const encoded=atob(craftingPacked),bytes=new Uint8Array(encoded.length);
  for(let i=0;i<encoded.length;i++)bytes[i]=encoded.charCodeAt(i);
  const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
  CRAFTING=JSON.parse(await new Response(stream).text());return CRAFTING;
 })().catch(error=>{craftingLoad=null;throw error});
 return craftingLoad;
}
'''
    html = html[:start] + declaration.rstrip() + html[end:]
    start, end, maps = read_constant(html, 'MAPS', 'const MAP_STATE=')
    for zone, record in maps.items():
        record['image'] = f'https://wow.zamimg.com/images/wow/classicplus/maps/enus/original/{zone}.jpg'
    html = html[:start] + 'const MAPS=' + json.dumps(maps, separators=(',', ':')) + ';' + html[end:]
    start, end, items = read_constant(html, 'ITEM_TOOLTIPS', 'const itemCache=')
    for item in items.values():
        if item.get('icon'):
            item['image'] = 'https://wow.zamimg.com/images/wow/icons/large/' + item['icon'].lower() + '.jpg'
    html = html[:start] + 'const ITEM_TOOLTIPS=' + json.dumps(items, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';' + html[end:]
    # Recipe views are the only entry points that need the compressed catalogue.
    sidebar = "if(view==='professions'){renderProfessionSidebar(side);return}"
    html = html.replace(sidebar, "if(view==='professions'&&!CRAFTING){side.replaceChildren(el('div','side-title','Professions'));return}" + sidebar, 1)
    sidebar = "if(view==='camping'){renderCampingSidebar(side);return}"
    html = html.replace(sidebar, "if(view==='camping'&&!CRAFTING){side.replaceChildren(el('div','side-title','Camping'));return}" + sidebar, 1)
    entry = "if(view==='professions'){renderProfessions();return}"
    gate = """if((view==='professions'||view==='camping')&&!CRAFTING){
 main.append(el('p','subtitle','Loading profession recipes…'));
 ensureCraftingData().then(()=>{if(view==='professions'||view==='camping')render()}).catch(error=>{
  if(view==='professions'||view==='camping'){main.replaceChildren(el('p','subtitle','Recipe data could not be loaded: '+error.message),button('Try Again',render))}
 });return;
} """
    assert entry in html
    html = html.replace(entry, gate + entry, 1)
    # Native lazy images avoid eagerly decoding hundreds of off-screen icons.
    html = html.replace("const image=el('img',cls);image.src=", "const image=el('img',cls);image.loading='lazy';image.decoding='async';image.src=", 1)
    html = html.replace("const icon=el('img','reward-icon');icon.src=image", "const icon=el('img','reward-icon');icon.loading='lazy';icon.decoding='async';icon.src=image", 1)
    assert len(html.encode()) < 1_200_000, 'Preview unexpectedly large'
    OUTPUT.write_text(html)
    print(f'Built {OUTPUT.name}: {OUTPUT.stat().st_size:,} bytes; original icons/maps load on demand.')


if __name__ == '__main__':
    main()
