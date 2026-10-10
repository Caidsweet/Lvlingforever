"""Refresh quest map coordinates from Wowhead Forever and cache original WoW maps."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64,json,re,urllib.request,urllib.error,html,datetime,sys
ROOT=Path(__file__).resolve().parents[1]
source=json.loads((ROOT/'data/research-snapshot.json').read_text())
CACHE=ROOT/'data/wowhead';CACHE.mkdir(exist_ok=True)
TODAY=datetime.datetime.now(datetime.timezone.utc).date().isoformat()
def download(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
 with urllib.request.urlopen(req,timeout=25) as response:return response.read()
def decode_after(text,marker):
 start=text.find(marker)
 if start<0:return {}
 return json.JSONDecoder().raw_decode(text[start+len(marker):].lstrip())[0]
def quest_info(qid):
 url=f'https://www.wowhead.com/forever/quest={qid}'
 cached=CACHE/f'quest-{qid}.json'
 if cached.exists() and '--refresh' not in sys.argv:return str(qid),json.loads(cached.read_text())
 try:
  page=download(url).decode('utf-8')
  mapper=decode_after(page,'new Mapper(')
  points=[];unmapped=[]
  for zone_id,area in mapper.get('objectives',{}).items():
   for level_index,level in enumerate(area.get('levels',[])):
    for point in level:
     kind={'start':'pickup','end':'turnin'}.get(point.get('point'))
     if not kind or point.get('reactalliance',0)<0:continue
     entry={'kind':kind,'npc':point.get('name','Unknown quest giver'),'entityId':point.get('id'),'entityType':point.get('type'),'zone':area.get('zone'),'zoneId':str(zone_id),'floor':level_index,'source':url,'checked':TODAY}
     coords=point.get('coords') or [point.get('coord',[])]
     coordinate=next((c for c in coords if len(c)>=2 and all(isinstance(v,(int,float)) and 0<=v<=100 for v in c[:2])),None)
     if coordinate and area.get('mappable') and level_index==0:
      entry.update(x=coordinate[0],y=coordinate[1]);points.append(entry)
     else:unmapped.append(entry)
  details=decode_after(page,f'$.extend(g_quests[{qid}], ')
  name=details.get('name') or source['walkthroughs'].get(str(qid),{}).get('name')
  info={'id':str(qid),'name':name,'points':points,'unmapped':unmapped,'source':url,'checked':TODAY,'status':'fetched'}
  (CACHE/f'quest-{qid}.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
  return str(qid),info
 except Exception as error:
  if cached.exists():return str(qid),json.loads(cached.read_text())
  return str(qid),{'id':str(qid),'points':[],'unmapped':[],'source':url,'status':'unavailable','error':str(error)}
ids=set(source['walkthroughs'])|{str(q['id']) for q in source['catalogue']}
quests={}
with ThreadPoolExecutor(max_workers=6) as pool:
 for future in as_completed([pool.submit(quest_info,qid) for qid in sorted(ids)]):
  qid,info=future.result();quests[qid]=info
zones={p['zoneId']:p['zone'] for q in quests.values() for p in q['points']}
def map_image(entry):
 zone_id,name=entry;url=f'https://wow.zamimg.com/images/wow/classicplus/maps/enus/original/{zone_id}.jpg'
 try:
  data=download(url)
  if not data.startswith(b'\xff\xd8'):raise ValueError('Not a JPEG map')
  (ROOT/f'assets/maps/{zone_id}.jpg').write_bytes(data)
  return zone_id,{'id':zone_id,'name':name,'image':'data:image/jpeg;base64,'+base64.b64encode(data).decode('ascii'),'source':url}
 except Exception as e:return zone_id,{'id':zone_id,'name':name,'source':url,'error':str(e)}
maps={}
with ThreadPoolExecutor(max_workers=4) as pool:
 for future in as_completed([pool.submit(map_image,entry) for entry in zones.items()]):
  zone_id,info=future.result();maps[zone_id]=info
output={'quests':quests,'maps':maps,'checked':TODAY}
(ROOT/'data/map-snapshot.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print('Quests fetched:',sum(q['status']=='fetched' for q in quests.values()),'/',len(quests))
print('World-map points:',sum(len(q['points']) for q in quests.values()))
print('Original WoW maps downloaded:',sum('image' in m for m in maps.values()),'/',len(maps))
print('Quest failures:',sum(q['status']!='fetched' for q in quests.values()))
print('Map failures:',{z:m.get('error') for z,m in maps.items() if 'image' not in m})
