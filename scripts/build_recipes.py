"""Compile cached Forever profession facts; no network or inferred trainer sources."""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/recipe-research'
SOURCE_NAMES = {0:'None',1:'Crafted',2:'Drop',3:'PvP',4:'Quest',5:'Vendor',6:'Trainer',7:'Discovery',8:'Redemption',9:'Talent',10:'Starter',11:'Event',12:'Achievement',14:'Black Market',15:'Disenchanted',16:'Fished',17:'Gathered',18:'Milled',19:'Mined',20:'Prospected',21:'Pickpocketed',22:'Salvaged',23:'Skinned'}

def build_recipe_catalogue():
    index = json.loads((RAW / 'foreverdb/index.json').read_text())
    rank_reference = json.loads((ROOT/'data/profession-ranks.json').read_text())
    favor_reference = json.loads((RAW/'wowhead/merchants-favor.json').read_text())
    favor_items = {r['id']:r for r in favor_reference['items']}
    favor_spells = {r['teachesSpellId']:r for r in favor_reference['items'] if r.get('teachesSpellId')}
    professions, items, icon_ids = [], {}, set()
    for summary in index['professions']:
        slug = summary['slug']
        data = json.loads((RAW / f'foreverdb/{slug}.json').read_text())
        wh = json.loads((RAW / f'wowhead/{slug}.json').read_text())
        spells = {r['id']:r for r in wh['spells']}
        assert len(data['recipes']) == summary['count'], f'Incomplete {slug} client catalogue'
        for item_id, item in data['items'].items():
            items[item_id] = {'name':item[0], 'icon':item[1], 'quality':item[2]}
            if item[1]: icon_ids.add(item[1])
        recipes = []
        for raw in data['recipes']:
            live = spells.get(raw['s'], {})
            source = raw.get('src', {})
            client_skill = raw.get('req')
            learned = live.get('learnedat')
            if learned == 9999 or learned is None or learned <= 0: learned = None
            # ForeverDB displays req as the orange skill-up threshold, not learn-at.
            # Do not turn an orange threshold into a learning requirement.
            required = learned
            origins = [SOURCE_NAMES.get(n, f'Source {n}') for n in live.get('source', []) if n]
            if source.get('auto') and 'Automatic' not in origins: origins.append('Automatic')
            if source.get('fv') and 'Trainer' not in origins: origins.append('Trainer')
            if source.get('trainer') and 'Trainer' not in origins: origins.append('Trainer (Classic reference)')
            if source.get('vendors') and not any('Vendor' in s for s in origins): origins.append('Vendor (Classic reference)')
            if source.get('items') and not origins: origins.append('Recipe item · origin not listed')
            if not origins: origins = ['Source not listed']
            favor_plans = [favor_items[i] for i in source.get('items', []) if i in favor_items]
            if raw['s'] in favor_spells and not any(p['id']==favor_spells[raw['s']]['id'] for p in favor_plans):
                favor_plans.append(favor_spells[raw['s']])
            if favor_plans:
                origins = [o for o in origins if o not in ['Source not listed','Recipe item · origin not listed']]
                if not any(o.startswith('Vendor') for o in origins): origins.append('Vendor')
            colours = live.get('colors')
            recipes.append({
                'id':raw['s'], 'name':raw['n'], 'icon':raw.get('ic'), 'skill':required,
                'skillEvidence':'Wowhead Forever learn-at field' if learned is not None else 'Learn-at requirement not published',
                'clientSkill':client_skill,
                'wowheadLearnAt':learned, 'skillDifference':bool(raw.get('req') is not None and learned is not None and raw['req'] != learned),
                'thresholds':colours if colours and len(colours)==4 else None,
                'yellow':raw.get('y'), 'grey':raw.get('g'),
                'reagents':raw.get('r', []), 'creates':raw.get('make'), 'effect':raw.get('fx'),
                'tools':raw.get('tools', []), 'station':raw.get('focus'), 'origins':origins,
                'recipeItems':source.get('items', []), 'hiddenRecipeItems':source.get('hidden', []),
                'merchantFavor':favor_plans,
                'trainerObserved':source.get('fv', []), 'classicTrainer':source.get('trainer'),
                'classicVendors':source.get('vendors'), 'automatic':bool(source.get('auto')),
                'newInForever':bool(raw.get('new')), 'changed':raw.get('chg', []),
                'tier':raw.get('tier'), 'characterLevel':raw.get('rl'), 'specialization':raw.get('sp'),
                'clientOnly':bool(raw.get('missing') or source.get('hidden')),
                'spellUrl':f'https://www.wowhead.com/forever/spell={raw["s"]}',
            })
            if raw.get('ic'): icon_ids.add(raw['ic'])
        recipes.sort(key=lambda r:(r['skill'] is None, r['skill'] or 0, r['name'].lower(), r['id']))
        assert len({r['id'] for r in recipes}) == len(recipes), f'Duplicate {slug} spell'
        profile = next(group for group in rank_reference['groups'].values() if slug in group['professions'])
        ranks = []
        for i, rank in enumerate(summary['ranks']):
            ranks.append({**rank,'characterLevel':profile['characterLevels'][i], 'learnAtSkill':profile['learnAtSkills'][i], 'trainingMethod':profile['methods'][i]})
        professions.append({'id':slug,'name':summary['n'],'kind':summary['kind'],'icon':summary['ic'],'ranks':ranks,'rankNote':profile['note'],'recipes':recipes,'sourceUrl':f'https://foreverdb.net/profession/{slug}'})
        icon_ids.add(summary['ic'])
    item_snapshot_path = ROOT/'data/recipe-item-snapshot.json'
    item_snapshot = json.loads(item_snapshot_path.read_text()) if item_snapshot_path.exists() else {'items':{}}
    for item_id, record in item_snapshot['items'].items():
        if record.get('name') and record.get('icon'):
            items.setdefault(item_id, {'name':record['name'], 'icon':record['icon'].lower(), 'quality':record.get('quality',1), 'available':record['available']})
    item_gaps = {item_id:record for item_id,record in item_snapshot['items'].items() if not record.get('available')}
    for profession in professions:
        for recipe in profession['recipes']:
            recipe['unavailableItems'] = [item_id for item_id in ([recipe['creates'][0]] if recipe['creates'] else [])+[i for i,_ in recipe['reagents']]+recipe['recipeItems']+recipe['hiddenRecipeItems'] if str(item_id) in item_gaps]
            if recipe['creates'] and str(recipe['creates'][0]) in item_gaps: recipe['clientOnly'] = True
    camp_notes = json.loads((ROOT/'data/camping.json').read_text())
    camps = []
    for camp in index['camp']:
        # This guide is Alliance-only: omit the Horde banner variant.
        if camp['id'] == 279973: continue
        entry = dict(camp)
        recipe = next((r for p in professions if p['id']==camp['prof'] for r in p['recipes'] if r['id']==camp['recipe']), None)
        entry['overviewSkill'] = camp.get('skill')
        entry['skill'] = recipe['skill'] if recipe else None
        entry['summary'] = camp_notes['features'].get(str(camp['id']), [])
        camps.append(entry)
        icon_ids.add(camp['ic'])
    catalogue = {'checked':'2026-10-11','professions':professions,'items':items,'itemGaps':item_gaps,'camp':camps,'campNotes':camp_notes,'rankReference':rank_reference,'sources':[
        {'name':'ForeverDB client recipe catalogue','url':'https://foreverdb.net/professions','note':index['about']},
        {'name':'Wowhead Forever','url':'https://www.wowhead.com/forever/spells/professions','note':'Learn-at fields, published skill-up thresholds and acquisition categories. ForeverDB orange skill-up fields are not assumed to be learning requirements.'}
    ]}
    catalogue['coverage'] = {'recipes':sum(len(p['recipes']) for p in professions),'professions':len(professions),'missingSkills':sum(r['skill'] is None for p in professions for r in p['recipes']),'skillDifferences':sum(r['skillDifference'] for p in professions for r in p['recipes'])}
    catalogue['acquisitionReference'] = {'checked':favor_reference['checked'],'source':favor_reference['source'],'currencyId':3402,'publishedItems':len(favor_items),'matchedRecipes':sum(bool(r['merchantFavor']) for p in professions for r in p['recipes']),'icons':{'favor':'racial_dwarf_findtreasure','vendor':'inv_misc_bag_10','trainer':'inv_misc_book_09'}}
    (ROOT/'data/recipe-catalogue.json').write_text(json.dumps(catalogue,ensure_ascii=False,indent=2)+'\n')
    assets = {}
    for icon_id in sorted(icon_ids):
        path = ROOT/f'assets/professions/{icon_id}.webp'
        if path.exists(): assets[str(icon_id)] = 'data:image/webp;base64,'+base64.b64encode(path.read_bytes()).decode()
    for record in items.values():
        if isinstance(record['icon'],str):
            path=ROOT/f'assets/icons/{record["icon"]}.jpg'
            if not path.exists(): raise ValueError('Missing cached item icon: '+record['icon'])
            assets[record['icon']]='data:image/jpeg;base64,'+base64.b64encode(path.read_bytes()).decode()
    for icon in catalogue['acquisitionReference']['icons'].values():
        path=ROOT/f'assets/icons/{icon}.jpg'
        if not path.exists(): raise ValueError('Missing acquisition icon: '+icon)
        assets[icon]='data:image/jpeg;base64,'+base64.b64encode(path.read_bytes()).decode()
    catalogue['icons'] = assets
    return catalogue

if __name__ == '__main__':
    catalogue = build_recipe_catalogue()
    print(json.dumps(catalogue['coverage']))
