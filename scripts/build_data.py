"""Build offline data from pinned research snapshots; preserve source uncertainty."""
import json, subprocess, sys, re, base64
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
snapshot_path=ROOT/'data/research-snapshot.json'
map_path=ROOT/'data/map-snapshot.json'
map_snapshot=json.loads(map_path.read_text()) if map_path.exists() else {'quests':{},'maps':{}}
item_path=ROOT/'data/item-tooltip-snapshot.json'
item_snapshot=json.loads(item_path.read_text()) if item_path.exists() else {'items':{}}
item_tooltips={}
for item_id, data in sorted(item_snapshot['items'].items()):
 cached=dict(data)
 icon=ROOT/'assets/icons'/(data.get('icon','').lower()+'.jpg')
 if icon.exists():cached['image']='data:image/jpeg;base64,'+base64.b64encode(icon.read_bytes()).decode()
 item_tooltips[item_id]=cached
if len(sys.argv)<3:
    research=json.loads(snapshot_path.read_text())
    cat=research['catalogue'];walk=research['walkthroughs'];items=research['itemStats']
    factions=research.get('questFactions',{});entrances=research.get('entrances',{})
    commits=research['sourceCommits']
else:
    DP=Path(sys.argv[1]);GP=Path(sys.argv[2])
    cat=json.loads((DP/'data/catalogue.json').read_text())
    walk=json.loads((DP/'data/walkthroughs.json').read_text())
    items=json.loads((GP/'pipeline/data/items.json').read_text())
    factions=json.loads((GP/'pipeline/data/quest_faction.json').read_text())
    entrances=json.loads((GP/'pipeline/data/dungeon_entrances.json').read_text())
    commits={'dungeonQuestie':subprocess.check_output(['git','-C',str(DP),'rev-parse','HEAD'],text=True).strip(),'gearQuest':subprocess.check_output(['git','-C',str(GP),'rev-parse','HEAD'],text=True).strip()}

config=[('thanes','The Hall of Thanes','Hall of Thanes',13,20,'Ironforge','#7b5e30'),('lordaeron','Ruins of Lordaeron','Ruins of Lordaeron',15,22,'Tirisfal Glades','#395c58'),('deadmines','Deadmines','The Deadmines',17,26,'Westfall','#386066'),('wailing','Wailing Caverns','Wailing Caverns',15,24,'The Barrens','#305634'),('shadowfang','Shadowfang Keep','Shadowfang Keep',20,30,'Silverpine Forest','#435159'),('blackfathom','Blackfathom Deeps','Blackfathom Deeps',24,32,'Ashenvale','#314c59'),('stockades','Stormwind Stockade','The Stockade',24,32,'Stormwind','#735535'),('excavation','Excavation Site: Wetlands','Excavation Site: Wetlands',26,33,'Wetlands','#6b6743'),('dalaran','City of Dalaran','City of Dalaran',28,35,'Hillsbrad / Dalaran','#55416d'),('razorfen','Razorfen Kraul','Razorfen Kraul',29,35,'The Barrens','#624335'),('gnomeregan','Gnomeregan','Gnomeregan',30,35,'Dun Morogh','#426349'),('scarlet','Scarlet Monastery','Scarlet Monastery',30,35,'Tirisfal Glades','#733e32')]
intro={
 'thanes':'Prepare Underground Map at Gol’Bolar Quarry in Dun Morogh, then head to Old Ironforge. Two quests start inside the dungeon; remember to speak to the NPCs and open the treaty vault.',
 'lordaeron':'Route plan: run this at around level 22, then continue to Shadowfang Keep during the same northern trip. Your screenshot lists four Alliance quests. Several start from items inside the dungeon. The source does not confirm where to pick up Abominable Creatures; check this before travelling.',
 'deadmines':'Complete both the Defias chain and Alba Fairmoon’s Toxic Soil chain in Westfall. After planting the explosives, use the rear exit to meet Alba. A paladin quest also applies if your group includes a paladin.',
 'wailing':'Five neutral quests: pick them up in Ratchet and the cave above the dungeon entrance. The Mutanus event is needed for The Glowing Shard. Include Wailing Caverns in your Kalimdor trip.',
 'shadowfang':'Route plan: follow Ruins of Lordaeron during the same northern trip at levels 22–24. Prepare the relevant class quests before travelling north. The two quests available to Alliance are class quests for paladins and warlocks. Your group can still run the dungeon without these classes.',
 'blackfathom':'Collect quests in Ironforge, Darnassus and Auberdine. Thaelrid offers a quest inside the dungeon. Separate paladin and warlock quests are labelled with their class requirements.',
 'stockades':'Collect quests in Stormwind, Lakeshire and Wetlands. After Deadmines, VanCleef’s letter leads to The Stockade Riots. Complete The Dark Iron War before taking The Fury Runs Deep.',
 'excavation':'Prepare Rethiel’s three outdoor quests, Daily Delivery and the Caitlin chain. Pick up Songblade Search in Lakeshire. Several follow-ups start inside the dungeon and may require a return trip.',
 'dalaran':'Optional late-20s beta planning. The supplied research reports that Dalaran opened for testing on October 8; the official post has not been independently read here. Alliance quests are listed from level 24, but a full run before 30 has not been established. Use nearby outdoor quests if the current build or your group is not ready.',
 'razorfen':'Optional level-29–30 planning if already travelling through Kalimdor; a full run before the cap has not been established. Alliance and neutral quests: prepare Blueleaf Tubers in Ratchet. Willix and Mortality Wanes start inside the dungeon.',
 'gnomeregan':'Saved planning for after the level-30 route. Collect quests in Ironforge and Kharanos when convenient. Turn in Gnogaine to unlock its follow-up, so plan a return trip. Remember Gyrodrillmatic Excavationators, the escort and the ring chain.',
 'scarlet':'Saved planning at the level-30 boundary and beyond. Evaluate Graveyard separately; this catalogue also includes quests for later wings. In the Name of the Light requires Armory and Cathedral, so its completion is outside the 1–30 route. Past Due is a Forever quest with an unconfirmed pickup location.'}
stat_names={'armor':'Armor','str':'Strength','agi':'Agility','sta':'Stamina','int':'Intellect','spi':'Spirit','ap':'Attack Power','rap':'Ranged Attack Power','heal':'Healing','damageDone':'Spell Damage / Healing','sp':'Spell Power','hp5':'Health per 5 sec','mp5':'Mana per 5 sec','crit':'Critical Strike Rating','hit':'Hit Rating','dodge':'Dodge Rating','def':'Defense','defense':'Defense','resist':'Resistance (type unspecified in source)','block':'Block'}
slot_names={'Held':'Held In Off-hand','TwoHand':'Two-Hand','OneHand':'One-Hand','MainHand':'Main Hand','OffHand':'Off Hand','Back':'Back','Finger':'Finger','Trinket':'Trinket','Ranged':'Ranged'}
kind_names={'Mace2H':'Mace','Sword2H':'Sword','Axe2H':'Axe','Misc':''}
class TooltipText(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_starttag(self,tag,attrs):
  if tag in ['br','div','tr']:self.parts.append('\n')
 def handle_endtag(self,tag):
  if tag in ['div','tr','table']:self.parts.append('\n')
 def handle_data(self,data):self.parts.append(data)
 def lines(self):return [re.sub(r'\s+',' ',line).strip() for line in ''.join(self.parts).splitlines() if line.strip()]
used_nodes={}
def is_horde(x):
 w=walk.get(str(x['id']),{})
 return x.get('faction')=='Horde' or w.get('faction')=='Horde' or factions.get(str(x['id']))=='Horde' or (w.get('raceMask',0) and not(w['raceMask']&77))
def node(id):
 return walk.get(str(id),next((x for x in cat if x['id']==id),{}))
def ancestors(id,seen=None):
 seen=set() if seen is None else seen
 if id in seen: raise ValueError('Cycle in quest chain: '+str(id))
 seen=seen|{id};n=node(id);used_nodes[str(id)]=n
 result=[]
 for parent in n.get('all',n.get('prereqs',[])):
  p=node(parent)
  result+=ancestors(parent,seen)
  text=f"{p.get('name','Quest '+str(parent))} [#{parent}] — {p.get('pickup','Follow your quest log; the source does not list a pickup location.')}"
  if p.get('objectives'):text+=' · '+ '; '.join(p['objectives'])
  if p.get('routeNote'):text+=' · '+p['routeNote']
  if p.get('unverifiedChain'):text+=' · This prerequisite link needs confirmation in game.'
  result.append(text)
 for options in n.get('any',[]):
  choices=options if isinstance(options,list) else [options]
  result.append('Alternative prerequisite: '+ ' OR '.join(node(x).get('name',f'Quest #{x}') for x in choices))
 return list(dict.fromkeys(result))
def reward(x):
 i=items.get(str(x['id']),{});stats=[]
 if i:
  if i.get('ilvl'):stats.append('Item Level '+str(i['ilvl']))
  if i.get('bind')=='BoP' or i.get('bonding')==1:stats.append('Binds when picked up')
  slot=slot_names.get(i.get('slot'),i.get('slot',''));kind=kind_names.get(i.get('kind'),i.get('kind',''))
  stats.append(slot+(' · '+kind if kind else ''))
  if i.get('dmgMax'):stats.extend([f"{i['dmgMin']:g} – {i['dmgMax']:g} Damage    Speed {i.get('speed',0):.2f}",f"({i.get('dps',0):.1f} damage per second)"])
  for k,v in i.get('stats',{}).items():
   # Effect-driven stats and school totals are already represented by Equip lines.
   # Never expose internal keys or add the derived school total to school bonuses.
   if k not in stat_names or (k in ['ap','heal','damageDone'] and i.get('effects')):continue
   stats.append((str(v)+' '+stat_names[k]) if k=='armor' else ('+'+str(v)+' '+stat_names[k]))
  if i.get('tipClasses'):stats.append('Classes: '+', '.join(i['tipClasses']))
  if i.get('rlvl'):stats.append('Requires Level '+str(i['rlvl']))
  stats+=i.get('effects',[])
  for p in i.get('procs',[]):stats.append(str(p))
 cached=item_tooltips.get(str(x['id']))
 if cached:
  text=TooltipText();text.feed(cached['tooltip']);lines=text.lines()
  stats=lines[1:] if lines and lines[0]==cached.get('name') else lines
 return {'id':x['id'],'name':cached.get('name',x['name']) if cached else x['name'],'quality':{0:'poor',1:'common',2:'uncommon',3:'rare',4:'epic'}.get(cached.get('quality',2) if cached else i.get('quality',2),'uncommon'),'stats':stats,'icon':'','kind':i.get('kind','Misc'),'slot':i.get('slot',''),'source':'Wowhead Forever · '+cached['checked'] if cached else 'GearQuest snapshot; current Forever data unavailable.'}
output=[]
for id,key,name,lo,hi,zone,tint in config:
 entries=[x for x in cat if key in x.get('dungeons',[]) and not is_horde(x)]
 # Keep dependency-only quests within the chain rather than duplicate checklist rows.
 skip={96391,92819,6981,95663,95682,95737,95647,95810,2923,2927,2925,2931,2947,1442}
 entries=[x for x in entries if x['id'] not in skip]
 quests=[]
 for x in entries:
  w=node(x['id']);chain=ancestors(x['id']);notes=[]
  for field in ['preparationNote','routeNote','requirementsNote']:
   if x.get(field) or w.get(field):notes.append(x.get(field) or w[field])
  if x.get('restrictionUnknown'):notes.append('The source does not confirm faction restrictions; check in game. Your screenshots confirm Alliance availability for the quests shown.')
  if w.get('unverifiedChain'):notes.append('The source does not fully verify this pickup location or quest chain.')
  if x['id']==98423:notes.append('Your screenshot shows minimum level 9; the database lists 16. Both are noted until the launch version is confirmed.')
  if x['id']==378:notes.append('Your screenshot shows minimum level 25; the beta catalogue lists 22. Plan to pick up the quest at 25.')
  if x['id']==1275:notes.append('Your screenshot marks a prerequisite. The beta source does not confirm the link; check Gershala’s earlier quests in Auberdine before leaving.')
  if x['id']==92753:
   chain.append('After the run: rear exit → Alba Fairmoon → Destruction in Deadmines [#92819] → use the detonator. Do not hearth before completing this step.')
  if x['id']==1053:
   chain=[s.replace('Brother Anton - The Barrens','Brother Anton — Nijel’s Point, Desolace (the source’s Classic reference pin is misplaced)') for s in chain]
  if x['id']==3366:notes.append('Defeat all four Fanglords, start the Disciple of Naralex escort at the entrance and defeat Mutanus. Loot the shard from Mutanus. Continue through Ratchet / Falla Sagewind. Check your quest log for the Alliance follow-up.')
  if x['id']==1740:notes.append('Requires a warlock; collect fragments in both Blackfathom Deeps and Shadowfang Keep.')
  if x['id']==1654:notes.append('Requires a paladin. Gather materials from Deadmines, Shadowfang Keep, Blackfathom Deeps and Loch Modan. In Auberdine, take Seeking the Kor Gem while The Test of Righteousness is active.')
  class_name=x.get('class') or w.get('class') or {2:'PALADIN',128:'MAGE',256:'WARLOCK'}.get(w.get('classMask'))
  pickup=x.get('pickup') or w.get('pickup') or 'The source does not list a pickup location.'
  quests.append({'id':str(x['id']),'name':x['name'],'npc':pickup,'location':'','minLevel':25 if x['id']==378 else (x.get('minLevel') or w.get('minLevel') or 0),'objective':'; '.join(x.get('objectives') or w.get('objectives') or ['Follow the objectives in your in-game quest log. The source does not list them.']),'chain':chain,'notes':notes,'turnin':w.get('turnin') or '; '.join(s for s in x.get('people',[]) if s.startswith('Turned in')) or 'Check your quest log.','rewards':[reward(r) for r in x.get('rewards',[])],'evidence':x.get('evidence','Reference data'),'source':x.get('source',w.get('source','')),'checked':x.get('checked',w.get('checked','')),'class':class_name,'inside':bool(x.get('pickupInside') or w.get('pickupInside')),'uncertain':bool(w.get('unverifiedChain'))})
  if x['id']==78916:
   # The current Forever page references these IDs, but its item records are
   # blank/unattainable and all three Forever item endpoints return 404.
   # Retain the old names as unresolved references, not verified reward cards.
   quests[-1]['unverifiedRewards']=quests[-1]['rewards']
   quests[-1]['rewards']=[]
   quests[-1]['notes'].append('Forever database check on October 10: the three Void Pearl item records have no current names, stats or icons. Older reward names are retained as unresolved references below.')
 for quest in quests:
  quest['mapPoints']=[];quest['mapGaps']=[]
  related=[(quest['id'],'Dungeon Quest',0)]
  for step,ancestor_id in enumerate(dict.fromkeys(re.findall(r'\[#(\d+)\]', ' '.join(quest['chain']))),1):
   if ancestor_id!=quest['id']:related.append((ancestor_id,'Follow-up' if ancestor_id=='92819' else 'Prerequisite',step))
  for related_id,relation,step in related:
   live=map_snapshot['quests'].get(related_id,{})
   quest_name=live.get('name') or node(int(related_id)).get('name') or quest['name']
   for point in live.get('points',[]):
    if point['zoneId'] in ['1637','1638','1497']:continue # Horde class trainers in shared quest records.
    quest['mapPoints'].append(dict(point,questId=related_id,questName=quest_name,relation=relation,step=step,targetQuestId=quest['id']))
   for kind in ['pickup','turnin']:
    if not any(point['kind']==kind for point in live.get('points',[])):
     info=next((p for p in live.get('unmapped',[]) if p['kind']==kind),{})
     source_node=node(int(related_id))
     location=(quest['npc'] if kind=='pickup' else quest['turnin']) if relation=='Dungeon Quest' else source_node.get('pickup' if kind=='pickup' else 'turnin','Check your quest log.')
     quest['mapGaps'].append({'questId':related_id,'questName':quest_name,'relation':relation,'kind':kind,'location':str(location),'npc':info.get('npc'),'zone':info.get('zone'),'reason':'No world-map coordinates published by Wowhead Forever.'})
 plan_scope='after30' if id in ['gnomeregan','scarlet'] else 'boundary' if id in ['dalaran','razorfen'] else 'route'
 output.append({'id':id,'name':name,'min':lo,'max':hi,'zone':zone,'tint':tint,'intro':intro[id],'planScope':plan_scope,'verified':False,'quests':quests,'entrances':entrances.get(name,[])})
research={'catalogue':[x for x in cat if any(d in [a[1] for a in config] for d in x.get('dungeons',[]))],'walkthroughs':used_nodes,'itemStats':{str(r['id']):items.get(str(r['id']),{}) for d in output for q in d['quests'] for r in q['rewards']},'sourceCommits':commits,'questFactions':factions,'entrances':entrances}
(ROOT/'data/research-snapshot.json').write_text(json.dumps(research,ensure_ascii=False,indent=2)+'\n')
(ROOT/'data/guide.json').write_text(json.dumps({'dungeons':output},ensure_ascii=False,indent=2)+'\n')
html=(ROOT/'index.html').read_text();start=html.index('let dungeons=');end=html.index('\nlet stage=',start)
html=html[:start]+'let dungeons='+json.dumps(output,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';'+html[end:];(ROOT/'index.html').write_text(html)
if 'const RESEARCH=' in html:
 research_notes=json.loads((ROOT/'data/leveling-research.json').read_text())
 start=html.index('const RESEARCH=');end=html.index('\nconst LEVEL_CAP=',start)
 html=html[:start]+'const RESEARCH='+json.dumps(research_notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';'+html[end:]
 (ROOT/'index.html').write_text(html)
if 'const ITEM_TOOLTIPS=' in html:
 start=html.index('const ITEM_TOOLTIPS=');end=html.index('\nconst itemCache=',start)
 html=html[:start]+'const ITEM_TOOLTIPS='+json.dumps(item_tooltips,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';'+html[end:]
 (ROOT/'index.html').write_text(html)
used_zones={point['zoneId'] for dungeon in output for quest in dungeon['quests'] for point in quest.get('mapPoints',[])}
map_assets={zone:map_snapshot['maps'][zone] for zone in sorted(used_zones) if zone in map_snapshot['maps'] and map_snapshot['maps'][zone].get('image')}
html=(ROOT/'index.html').read_text()
if 'const MAPS=' in html:
 start=html.index('const MAPS=');end=html.index('\nconst MAP_STATE=',start)
 html=html[:start]+'const MAPS='+json.dumps(map_assets,ensure_ascii=False,separators=(',',':'))+';'+html[end:]
 (ROOT/'index.html').write_text(html)
theme_path=ROOT/'assets/ui/classic.css'
if 'const PROFESSIONS=' in html:
 professions=json.loads((ROOT/'data/professions.json').read_text())
 start=html.index('const PROFESSIONS=');end=html.index('\nlet professionSection=',start)
 html=html[:start]+'const PROFESSIONS='+json.dumps(professions,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';'+html[end:]
 (ROOT/'index.html').write_text(html)
if theme_path.exists():
 css=theme_path.read_text()
 def embed_asset(match):
  path=ROOT/match.group(1)
  mime='font/ttf' if path.suffix=='.ttf' else 'image/png'
  return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()
 css=re.sub(r'asset://([A-Za-z0-9_./-]+)',embed_asset,css)
 block='<!-- CLASSIC_THEME_START -->\n<style id="classic-theme">'+css+'</style>\n<!-- CLASSIC_THEME_END -->'
 if '<!-- CLASSIC_THEME_START -->' in html:
  start=html.index('<!-- CLASSIC_THEME_START -->');end=html.index('<!-- CLASSIC_THEME_END -->',start)+len('<!-- CLASSIC_THEME_END -->')
  html=html[:start]+block+html[end:]
 else:html=html.replace('</head>',block+'</head>',1)
 (ROOT/'index.html').write_text(html)
print('Built',len(output),'dungeons,',sum(len(d['quests']) for d in output),'quests,',sum(len(q['rewards']) for d in output for q in d['quests']),'rewards')
