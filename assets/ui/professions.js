const craftStates = {};
let campProfession = 'all';
function craftIcon(icon, cls='craft-icon') {
 const image=el('img',cls);image.loading='lazy';image.decoding='async';image.src=CRAFTING.icons[String(icon)]||'';image.alt='';image.width=32;image.height=32;return image;
}
function craftLink(text, url) {
 const link=el('a','source-link',text);link.href=url;link.target='_blank';link.rel='noopener noreferrer';return link;
}
function recipeKey(profession, recipe) {return 'recipe:'+profession.id+':'+recipe.id}
function recipeSkill(recipe) {return recipe.skill===null?'Not listed':String(recipe.skill)}
function openCrafting(id, recipeId) {
 view='professions';professionSection=id;selected=null;
 if(recipeId){craftStates[id]={...(craftStates[id]||{}),search:'',source:'all',selected:recipeId}}
 render();
}
function renderProfessionSidebar(side) {
 side.dataset.mode='professions';side.replaceChildren(el('div','side-title','Professions'));
 const progress=el('div','side-subtitle','Starting setup · '+professionCompleted()+'/'+PROFESSIONS.checklist.length);progress.id='professionProgress';side.append(progress);
 const setup=button('Starting-Zone Setup',()=>openCrafting('setup'),'route profession-tab'+(professionSection==='setup'?' active':''));side.append(setup);
 let group='';
 for(const profession of CRAFTING.professions){
  const kind=['herbalism','mining','skinning'].includes(profession.id)?'Gathering':profession.kind==='primary'?'Crafting':'Secondary';
  if(kind!==group){side.append(el('div','profession-group',kind));group=kind}
  const b=button('',()=>openCrafting(profession.id),'route profession-tab'+(professionSection===profession.id?' active':''));
  if(professionSection===profession.id)b.setAttribute('aria-current','page');
  const text=el('span');text.append(el('strong','',profession.name));
  b.append(craftIcon(profession.icon),text);side.append(b);
 }
}
function renderProfessions() {
 const profession=CRAFTING.professions.find(p=>p.id===professionSection);
 if(profession){renderCraftingProfession(profession);return}
 const heading=el('div','stage-heading');heading.append(el('h2','','Starting-Zone Professions'),el('span','level','STARTING SETUP'));main.append(heading);
 const paper=el('article','paper profession-guide');
 paper.append(el('p','',PROFESSIONS.recommendation),el('h4','','Before Leaving Your Starting Zone'),professionChecklist(),el('h4','','Buy from the Local Trainers'),professionPrices(),el('h4','','Gather While You Level'),el('p','','Follow RestedXP to level 10. Skin looted beasts and collect nearby herbs or ore as you quest, then keep gathering along the dungeon route.'),el('h4','','Recipe Catalogue'),el('p','',CRAFTING.coverage.recipes.toLocaleString('en-US')+' client recipe records across all '+CRAFTING.professions.length+' professions. Select a profession on the left for skill requirements, recipe sources and materials.'),button('Browse Alchemy Recipes',()=>openCrafting('alchemy')));
 main.append(paper);
}
function craftItem(itemId, count, label) {
 const record=CRAFTING.items[String(itemId)];
 if(!record?.icon){const unavailable=el('span','craft-item-unavailable','Item #'+itemId+(count?' ×'+count:'')+' · Item data unavailable');unavailable.title=CRAFTING.itemGaps?.[String(itemId)]?.reason||'No verified Forever item icon or name is published.';return unavailable}
 const item={id:itemId,name:label||record?.name||'Item #'+itemId,stats:[]};
 const b=button('',()=>{},'reward craft-item');b.dataset.quality=['poor','common','uncommon','rare','epic','legendary'][record?.quality]||'common';
 if(record?.icon)b.append(craftIcon(record.icon,'reward-icon'));
 b.append(el('span','',item.name+(count?' ×'+count:'')));
 const tip=el('span','tooltip');tip.setAttribute('role','tooltip');tip.id='craft-tip-'+itemId+'-'+(++craftTipId);b.setAttribute('aria-describedby',tip.id);b.append(tip);
 renderRewardTooltip(item,b,tip,ITEM_TOOLTIPS[String(itemId)]);bindRewardTooltip(item,b,tip);return b;
}
let craftTipId=0;
function recipeOriginMatches(recipe, source) {
 if(source==='all')return true;
 if(source==='recipe')return !!(recipe.recipeItems.length||recipe.hiddenRecipeItems.length);
 if(source==='client')return recipe.clientOnly;
 if(source==='unknown')return recipe.origins.some(o=>o.includes('not listed'));
 return recipe.origins.some(o=>o.toLowerCase().startsWith(source));
}
function renderCraftingProfession(profession) {
 main.dataset.view='crafting';
 const state=craftStates[profession.id]||(craftStates[profession.id]={search:'',source:'all',selected:null});
 const heading=el('div','craft-heading');heading.append(craftIcon(profession.icon,'profession-emblem'),el('h2','',profession.name),el('span','craft-total',profession.recipes.length+' recipes'));main.append(heading);
 const ranks=el('div','craft-ranks');ranks.setAttribute('aria-label',profession.name+' rank requirements — Classic reference');
 for(const rank of profession.ranks){const cell=el('div','craft-rank');cell.dataset.rank=rank.rank;cell.append(el('strong','',rank.rank+' · Cap '+rank.max),el('span','rank-char','Character Lv '+rank.characterLevel),el('span','rank-skill',rank.learnAtSkill?'Learn at skill '+rank.learnAtSkill:'No prior skill needed'));ranks.append(cell)}
 main.append(ranks);
 const reference=el('details','rank-reference');reference.append(el('summary','',CRAFTING.rankReference.status),el('p','',profession.rankNote),el('p','','You can learn the next rank before reaching your current cap when both the character-level and skill requirements are met. Visit the appropriate trainer; Classic secondary professions can also require a book or quest.'));
 const methods=el('ul');profession.ranks.forEach(rank=>methods.append(el('li','',rank.rank+' — '+rank.trainingMethod)));reference.append(methods);
 CRAFTING.rankReference.sources.forEach(source=>reference.append(craftLink(source.name,source.url)));main.append(reference);
 const controls=el('div','craft-controls'),searchLabel=el('label','craft-field','Search'),search=el('input','search');search.type='search';search.placeholder='Recipe or material…';search.value=state.search;search.setAttribute('aria-label','Search recipes');searchLabel.append(search);
 const sourceLabel=el('label','craft-field','Recipe source'),sources=el('select');sources.setAttribute('aria-label','Recipe source');
 for(const [value,name] of [['all','All sources'],['trainer','Trainer'],['drop','Drop'],['vendor','Vendor'],['quest','Quest'],['automatic','Automatic'],['recipe','Recipe item'],['discovery','Discovery'],['fished','Fished'],['pickpocketed','Pickpocketed'],['unknown','Source not listed'],['client','Client records']]){const option=el('option','',name);option.value=value;sources.append(option)}sources.value=state.source;sourceLabel.append(sources);controls.append(searchLabel,sourceLabel);main.append(controls);
 const workbench=el('div','craft-workbench'),catalogue=el('section','craft-catalogue'),countLabel=el('div','craft-count'),list=el('div','recipe-list'),detail=el('section','craft-detail');list.setAttribute('aria-label',profession.name+' recipes');
 const header=el('div','recipe-columns');header.append(el('span','','Recipe'),el('span','','Skill'),el('span','','Learn from'));catalogue.append(countLabel,header,list);workbench.append(catalogue,detail);main.append(workbench);
 function select(recipe){state.selected=recipe.id;for(const row of list.children){row.classList.toggle('active',row.dataset.recipe===String(recipe.id));row.setAttribute('aria-pressed',String(row.dataset.recipe===String(recipe.id)))}renderCraftingDetail(profession,recipe,detail,fill)}
 function fill(resetScroll=false){
  const top=resetScroll?0:list.scrollTop,term=state.search.trim().toLowerCase();
  const filtered=profession.recipes.filter(r=>recipeOriginMatches(r,state.source)&&(!term||(r.name+' '+r.reagents.map(([id])=>CRAFTING.items[String(id)]?.name||'').join(' ')+' '+r.recipeItems.map(id=>CRAFTING.items[String(id)]?.name||'').join(' ')).toLowerCase().includes(term)));
  const learned=profession.recipes.filter(r=>done.has(recipeKey(profession,r))).length;countLabel.textContent=filtered.length+' / '+profession.recipes.length+' recipes · '+learned+' marked learned';list.replaceChildren();
  for(const recipe of filtered){const row=button('',()=>select(recipe),'recipe-row');row.dataset.recipe=recipe.id;const title=el('span','recipe-name');title.append(craftIcon(recipe.icon),el('span','',recipe.name+(done.has(recipeKey(profession,recipe))?' ✓':'')));row.append(title,el('span','recipe-skill',recipeSkill(recipe)),el('span','recipe-origin',recipe.origins.join(' / ')+(recipe.clientOnly?' · Client record':'')));list.append(row)}
  list.scrollTop=top;
  if(!filtered.length){list.append(el('p','craft-empty','No matching recipes.'));detail.replaceChildren(el('p','craft-empty','Try another search or source.'));return}
  select(filtered.find(r=>r.id===state.selected)||filtered[0]);
 }
 search.oninput=()=>{state.search=search.value;fill(true)};sources.onchange=()=>{state.source=sources.value;fill(true)};fill();
 const gathering=PROFESSIONS.professions.find(p=>p.id===profession.id);if(gathering){const setup=el('details','craft-reference');setup.append(el('summary','','Starting-zone gathering setup'),el('p','',gathering.description));const steps=el('ol');gathering.steps.forEach(s=>steps.append(el('li','',s)));setup.append(steps);main.append(setup)}
 const catalogueReference=el('details','craft-reference');catalogueReference.append(el('summary','','Catalogue sources & skill requirements'),el('p','','The catalogue includes client records beyond the level 1–30 route. Required skill uses the Wowhead Forever learn-at field. Skill-up colours are separate from the skill needed to learn a recipe.'),el('p','',CRAFTING.coverage.missingSkills+' records have no published learn-at requirement. '+CRAFTING.coverage.skillDifferences+' records have a client skill-up start that differs from Wowhead learn-at; both fields are shown in their details. Classic trainer and vendor references are labelled. A recipe item without an origin is not assumed to drop.'),craftLink('ForeverDB — '+profession.name,profession.sourceUrl),craftLink('Wowhead Forever','https://www.wowhead.com/forever/'),el('p','','Snapshot checked '+CRAFTING.checked));main.append(catalogueReference);
}
function renderCraftingDetail(profession, recipe, target, refresh) {
 closeRewardTooltips();target.replaceChildren();
 const title=el('div','craft-detail-title');title.append(craftIcon(recipe.icon,'profession-emblem'),el('h3','',recipe.name));target.append(title);
 target.append(el('p','craft-requirement','Requires '+profession.name+': '+recipeSkill(recipe)),el('p','craft-provenance',recipe.skillEvidence));
 if(recipe.skillDifference)target.append(el('p','craft-data-note','Different fields: client skill-up start '+recipe.clientSkill+' · Wowhead learn-at '+recipe.wowheadLearnAt+'. The learning requirement uses Wowhead.'));
 if(recipe.skill===null&&recipe.clientSkill!==null)target.append(el('p','craft-data-note','Client skill-up start: '+recipe.clientSkill+'. A learning requirement is not published.'));
 if(recipe.clientOnly)target.append(el('p','craft-data-note','Client record · current availability is not confirmed.'));
 if(recipe.unavailableItems?.length)target.append(el('p','craft-data-note','This record references items with no current Forever data, or deprecated items. Missing names, icons and stats are not substituted from another game version.'));
 if(recipe.creates){target.append(el('h4','','Creates'));const output=el('div','craft-materials');output.append(craftItem(recipe.creates[0],recipe.creates[1]));target.append(output)}
 if(recipe.effect)target.append(el('p','craft-effect',readableItemText(recipe.effect)));
 target.append(el('h4','','Reagents'));const materials=el('div','craft-materials');for(const [id,count] of recipe.reagents)materials.append(craftItem(id,count));target.append(materials);if(!recipe.reagents.length)target.append(el('p','','No reagents listed.'));
 if(recipe.tools.length)target.append(el('p','','Tools: '+recipe.tools.join(', ')));
 if(recipe.station)target.append(el('p','','Crafting station: '+recipe.station));
 if(recipe.specialization)target.append(el('p','','Specialization: '+recipe.specialization));
 if(recipe.tier)target.append(el('p','','Camp feature · Client tier '+recipe.tier));
 target.append(el('h4','','Learn This Recipe'),el('p','',recipe.origins.join(' · ')));
 if(recipe.trainerObserved.length)target.append(el('p','','Forever trainer observations: '+recipe.trainerObserved.join(', ')));
 if(recipe.classicTrainer)target.append(el('p','craft-provenance','Classic trainer reference: '+recipe.classicTrainer.n+' trainers'+(recipe.classicTrainer.cost!==undefined?' · Training cost '+recipe.classicTrainer.cost+' copper':'')));
 if(recipe.classicVendors)target.append(el('p','craft-provenance','Classic vendor reference: '+recipe.classicVendors+' vendors.'));
 const scrolls=el('div','recipe-scrolls');for(const id of [...recipe.recipeItems,...recipe.hiddenRecipeItems]){const wrapper=el('div');wrapper.append(craftItem(id),craftLink(recipe.hiddenRecipeItems.includes(id)?'Unavailable recipe record ↗':'Recipe item source ↗','https://www.wowhead.com/forever/item='+id));scrolls.append(wrapper)}target.append(scrolls);
 if(recipe.thresholds){const colors=el('div','skill-colours');['Orange','Yellow','Green','Gray'].forEach((name,i)=>colors.append(el('span','skill-'+name.toLowerCase(),name+' '+recipe.thresholds[i])));target.append(el('h4','','Skill-Up Thresholds'),colors,el('p','craft-provenance','Published Wowhead Forever thresholds; these are not all learn-at requirements.'))}
 const actions=el('div','craft-actions'),key=recipeKey(profession,recipe);actions.append(button(done.has(key)?'Learned — Undo':'Mark Learned',()=>{done.has(key)?done.delete(key):done.add(key);save();refresh()}),craftLink('Recipe details ↗',recipe.spellUrl));target.append(actions);
}
function showCamping(){view='camping';selected=null;render()}
function renderCampingSidebar(side) {
 side.dataset.mode='professions';side.replaceChildren(el('div','side-title','Camping'),el('div','side-subtitle','Camp features & group benefits'));
 for(const profession of [{id:'all',name:'All Camp Features'},...CRAFTING.professions]){const b=button('',()=>{campProfession=profession.id;render()},'route profession-tab'+(campProfession===profession.id?' active':''));if(campProfession===profession.id)b.setAttribute('aria-current','page');if(profession.icon)b.append(craftIcon(profession.icon));b.append(el('strong','',profession.name));side.append(b)}
}
function renderCamping() {
 main.dataset.view='camping';const heading=el('div','stage-heading');heading.append(el('h2','','Camping'),el('span','level','ALL PROFESSIONS'));main.append(heading);
 const intro=el('article','camp-intro');intro.append(el('h3','','Build a Camp. Share the Benefits.'),el('p','','Start with a Cooking campfire kit: Basic supports 3 additional features, Journeyman 5 and Expert 10. Sit or craft nearby for 1 minute to receive camp benefits. Camp features share a 1-hour cooldown. Effects can replace equivalent class buffs; open the details for exclusions and level scaling.'),el('p','','The Camp Tent raises rested XP to 5% of a level; it has no effect when your rested XP already exceeds that amount.'));main.append(intro);
 for(const profession of CRAFTING.professions.filter(p=>campProfession==='all'||p.id===campProfession)){
  const section=el('section','camp-profession'),title=el('div','craft-heading');title.append(craftIcon(profession.icon),el('h3','',profession.name),button('Recipes',()=>openCrafting(profession.id)));section.append(title);const grid=el('div','camp-grid');
  for(const feature of CRAFTING.camp.filter(c=>c.prof===profession.id)){
   const card=el('article','camp-feature');card.dataset.item=feature.id;card.append(el('div','camp-tier','Client tier '+feature.tier+' · '+profession.name+' '+(feature.skill??'Not listed')),craftItem(feature.id,0,feature.n));const buffs=el('ul','camp-buffs');feature.summary.forEach(s=>buffs.append(el('li','',s)));card.append(buffs);
   const details=el('details','camp-details');details.append(el('summary','','Effects & materials'));for(const fx of feature.fx||[])details.append(el('p','',readableItemText(fx)));if(feature.overviewSkill!==feature.skill)details.append(el('p','','ForeverDB camp overview lists skill '+feature.overviewSkill+'; recipe learn-at '+(feature.skill??'not published')+' is shown above.'));const mats=el('div','craft-materials');for(const [id,count] of feature.r||[])mats.append(craftItem(id,count));details.append(mats,craftLink('Wowhead item ↗','https://www.wowhead.com/forever/item='+feature.id));card.append(details,button('View Crafting Recipe',()=>openCrafting(profession.id,feature.recipe)));grid.append(card);
  }
  section.append(grid);main.append(section);
 }
 const sources=el('details','craft-reference');sources.append(el('summary','','Camping sources'),el('p','',CRAFTING.campNotes.summarySource),el('p','','Tier numbers follow the client catalogue. Iron Oven is included as an additional client feature. The banner shown is the Alliance version.'),craftLink('ForeverDB camp features','https://foreverdb.net/professions'),craftLink('Wowhead Forever','https://www.wowhead.com/forever/'));main.append(sources);
}
