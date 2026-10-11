let selectedClass='Warrior';
let selectedClassBuild='';
function showClasses(){view='classes';selected=null;render()}
function renderClassSidebar(side){
 side.dataset.mode='professions';side.replaceChildren(el('div','side-title','Class Tips'),el('div','side-subtitle','Forever · Leveling & group roles'));
 for(const cls of CLASS_TIPS.classes){const b=button('',()=>{selectedClass=cls.name;selectedClassBuild='';main.scrollTop=0;render()},'route profession-tab class-tab'+(selectedClass===cls.name?' active':''));const icon=el('img','class-icon');icon.src=cls.icon;icon.alt='';icon.width=32;icon.height=32;icon.decoding='async';b.append(icon,el('strong','',cls.name));if(selectedClass===cls.name)b.setAttribute('aria-current','page');side.append(b)}
}
function renderClasses(){
 main.dataset.view='classes';const cls=CLASS_TIPS.classes.find(c=>c.name===selectedClass);
 const heading=el('div','stage-heading');heading.append(el('h2','',cls.name+' — Class Tips'),el('span','level','LEVEL 1–30'));main.append(heading);
 main.append(el('p','subtitle','Route-friendly shopping, training reminders and Forever talent suggestions. Compare upgrades with your current gear.'));
 for(const tip of cls.tips){const card=el('article','paper class-tip');card.append(el('h3','',tip.title),el('p','',tip.text),craftLink('View source ↗',tip.url));main.append(card)}
 const talents=el('section','paper class-talents');talents.append(el('h3','','Leveling Talents & Group Roles'),el('p','','Choose a level-20 or level-30 allocation. Leveling, tank and healer suggestions are separate; these are not measured rankings of leveling speed.'));
 const label=el('label','class-build-label','Build ');const select=el('select','class-build-select');select.id='classBuild';label.htmlFor=select.id;
 for(const build of cls.builds){const option=el('option','', 'Level '+build.level+' · '+build.role+' · '+build.title);option.value=build.id;select.append(option)}
 const build=cls.builds.find(b=>b.id===selectedClassBuild)||cls.builds[0];select.value=build.id;select.onchange=()=>{selectedClassBuild=select.value;render()};talents.append(label,select,el('h4','',build.title),el('p','',build.summary));
 talents.append(el('p','class-data-note','Allocation checked against ForeverDB’s current tree data: '+CLASS_TIPS.clientBuild+'. Source recommendation checked against older build '+cls.recommendationBuild+'.'));
 const totals=new Map();for(const point of build.sequence)totals.set(point.talent,point);const list=el('ul','talent-allocation');for(const point of totals.values())list.append(el('li','',point.talent+' '+point.rank+'/'+point.max));talents.append(list);
 const steps=el('details','rank-reference');steps.append(el('summary','','Example point order · levels 10–'+build.level),el('p','','A legal training order generated from this allocation. This order has not been tested as an optimal leveling route.'));
 const table=el('table','class-point-table');const head=el('thead');const hr=el('tr');for(const text of ['Character level','Talent','Rank'])hr.append(el('th','',text));head.append(hr);table.append(head);const body=el('tbody');for(const point of build.sequence){const row=el('tr');for(const text of [String(point.level),point.talent,point.rank+'/'+point.max])row.append(el('td','',text));body.append(row)}table.append(body);steps.append(table);talents.append(steps,craftLink('Forever build source ↗',cls.source));
 if(cls.name==='Warrior')talents.append(el('p','class-data-note','The older Arms level-30 leveling allocation is excluded: it omits the current Deep Wounds prerequisite for Impale.'));
 main.append(talents,el('p','subtitle','Reviewed '+CLASS_TIPS.date+'. Talent allocations are consistent with the cited dataset; class-quest gaps are marked in the tips above.'));
}
