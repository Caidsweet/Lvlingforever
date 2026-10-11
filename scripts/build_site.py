"""Build GitHub Pages with same-origin assets and deferred recipe loading."""
import json
import hashlib
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def constant(html, name, following):
    start = html.index('const '+name+'=')
    end = html.index('\n'+following, start)
    value = html[start+len('const '+name+'='):end].rstrip(';')
    return start, end, json.loads(value)


def checked_asset(path):
    if not (ROOT/path).is_file(): raise ValueError('Missing site asset: '+path)
    return path


def build_site(html):
    start, end, recipes = constant(html, 'CRAFTING', 'const PROFESSIONS=')
    recipes['icons'] = {icon: checked_asset(f'assets/professions/{icon}.webp') for icon in recipes['icons'] if icon.isdigit()}
    for record in recipes['items'].values():
        icon = record.get('icon')
        if isinstance(icon, str): recipes['icons'][icon] = checked_asset(f'assets/icons/{icon.lower()}.jpg')
    (ROOT/'data/site-recipes.json').write_text(json.dumps(recipes, ensure_ascii=False, separators=(',', ':'))+'\n')
    declaration = '''let CRAFTING=null;
let craftingLoad=null;
function ensureCraftingData(){
 if(CRAFTING)return Promise.resolve(CRAFTING);
 if(!craftingLoad)craftingLoad=fetch('data/site-recipes.json').then(response=>{
  if(!response.ok)throw Error('Recipe request failed (HTTP '+response.status+').');
  return response.json();
 }).then(data=>{CRAFTING=data;return data}).catch(error=>{craftingLoad=null;throw error});
 return craftingLoad;
}'''
    html = html[:start]+declaration+html[end:]
    for view, name, renderer in [('professions', 'Professions', 'Profession'), ('camping', 'Camping', 'Camping')]:
        entry = "if(view==='"+view+"'){render"+renderer+"Sidebar(side);return}"
        assert entry in html
        html = html.replace(entry, "if(view==='"+view+"'&&!CRAFTING){side.replaceChildren(el('div','side-title','"+name+"'));return}"+entry, 1)
    entry = "if(view==='professions'){renderProfessions();return}"
    assert entry in html
    gate = '''if((view==='professions'||view==='camping')&&!CRAFTING){
 main.append(el('p','subtitle','Loading profession recipes…'));
 ensureCraftingData().then(()=>{if(view==='professions'||view==='camping')render()}).catch(error=>{
  if(view==='professions'||view==='camping')main.replaceChildren(el('p','subtitle','Recipe data could not be loaded: '+error.message),button('Try Again',render));
 });return;
} '''
    html = html.replace(entry, gate+entry, 1)
    start, end, maps = constant(html, 'MAPS', 'const MAP_STATE=')
    for zone, record in maps.items(): record['image'] = checked_asset(f'assets/maps/{zone}.jpg')
    html = html[:start]+'const MAPS='+json.dumps(maps, separators=(',', ':'))+';'+html[end:]
    start, end, tooltips = constant(html, 'ITEM_TOOLTIPS', 'const itemCache=')
    for record in tooltips.values():
        if record.get('icon'): record['image'] = checked_asset('assets/icons/'+record['icon'].lower()+'.jpg')
    html = html[:start]+'const ITEM_TOOLTIPS='+json.dumps(tooltips, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')+';'+html[end:]
    css_path = ROOT/'assets/ui/site-classic.css'
    css = (ROOT/'assets/ui/classic.css').read_text()
    def css_asset(match):
        asset = checked_asset(match.group(1))
        return Path(os.path.relpath(ROOT/asset, css_path.parent)).as_posix()
    css_path.write_text(re.sub(r'asset://([A-Za-z0-9_./-]+)', css_asset, css))
    css_version = hashlib.sha256(css_path.read_bytes()).hexdigest()[:12]
    start = html.index('<!-- CLASSIC_THEME_START -->')
    end = html.index('<!-- CLASSIC_THEME_END -->', start)+len('<!-- CLASSIC_THEME_END -->')
    html = html[:start]+'<!-- CLASSIC_THEME_START -->\n<link rel="stylesheet" href="assets/ui/site-classic.css?v='+css_version+'">\n<!-- CLASSIC_THEME_END -->'+html[end:]
    html = html.replace('</title>', '</title><link rel="icon" href="'+checked_asset('assets/ui/UI-QuestLog-BookIcon.png')+'">', 1)
    assert len(html.encode()) < 600_000, 'Site entry point unexpectedly large'
    (ROOT/'index.html').write_text(html)
    print('Built static site:', len(html.encode()), 'bytes; cached images served locally.')
