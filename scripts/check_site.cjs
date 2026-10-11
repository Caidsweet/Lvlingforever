// Run with Playwright available: node scripts/check_site.cjs http://localhost:8080/
const { chromium } = require('playwright');
const assert = require('node:assert/strict');

(async () => {
 const url = process.argv[2] || 'http://127.0.0.1:8083/Lvlingforever/';
 const origin = new URL(url).origin;
 const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',args:['--no-sandbox','--js-flags=--max-old-space-size=64']});
 const page = await browser.newPage({viewport:{width:1450,height:950}});
 const errors=[], missing=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('crash',()=>errors.push('Renderer crash'));
 page.on('response',r=>{if(new URL(r.url()).origin===origin&&r.status()>=400)missing.push(r.url()+' '+r.status())});
 await page.route(/https?:\/\//,route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
 await page.goto(url);assert.equal(await page.evaluate(()=>CRAFTING),null,'Recipe catalogue loaded eagerly');
 await page.getByRole('button',{name:'Professions',exact:true}).click();
 await page.locator('.profession-tab').filter({hasText:'Alchemy'}).click();
 const catalogue=await page.evaluate(()=>CRAFTING);
 assert.equal(catalogue.coverage.recipes,2492);assert.equal(catalogue.professions.length,12);
 const iconFiles=Object.values(catalogue.icons);
 const extra=await page.evaluate(()=>[...Object.values(ITEM_TOOLTIPS).map(i=>i.image),...Object.values(MAPS).map(m=>m.image)]);
 const paths=[...new Set([...iconFiles,...extra])];assert(paths.every(p=>!/^https?:/.test(p)),'Published images use external servers');
 const imageFailures=await page.evaluate(async paths=>{
  const bad=[];
  // Bound decoding work instead of keeping all 1,500 image elements alive.
  for(let i=0;i<paths.length;i+=32)await Promise.all(paths.slice(i,i+32).map(src=>new Promise(resolve=>{
   const image=new Image();image.onload=()=>{if(!image.naturalWidth)bad.push(src);resolve()};image.onerror=()=>{bad.push(src);resolve()};image.src=src;
  })));
  return bad;
 },paths);assert.deepEqual(imageFailures,[],'Broken image assets');console.log('PASS:',paths.length,'local icon/map files fetched and decoded by Chromium.');
 for(const profession of catalogue.professions){
  await page.locator('.profession-tab').filter({hasText:profession.name}).click();assert.equal(await page.locator('.recipe-row').count(),profession.recipes.length);
  assert.deepEqual(await page.locator('.rank-char').allTextContents(),profession.ranks.map(r=>'Character Lv '+r.characterLevel));
 }
 await page.locator('.profession-tab').filter({hasText:'Alchemy'}).click();
 await page.getByRole('searchbox',{name:'Search recipes'}).fill('Swiftness Potion');await page.locator('.recipe-row').first().click();assert.match(await page.locator('.craft-detail').innerText(),/Drop.*Fished.*Pickpocketed/s);
 const quests=await page.locator('#questCount').textContent();await page.getByRole('button',{name:'Mark Learned',exact:true}).click();assert.equal(await page.locator('#questCount').textContent(),quests);
 await page.getByRole('searchbox',{name:'Search recipes'}).fill('');await page.getByRole('combobox',{name:'Recipe source'}).selectOption('drop');assert((await page.locator('.recipe-origin').allTextContents()).every(s=>s.includes('Drop')));
 await page.getByRole('button',{name:'Camping',exact:true}).click();assert.equal(await page.locator('.camp-feature').count(),38);
 const mana=page.locator('[data-item="279956"] .reward').first();await mana.hover();assert.equal(await mana.locator('.tooltip').evaluate(e=>e.hidden),false);await mana.click();await page.mouse.move(2,2);assert.equal(await mana.locator('.tooltip').evaluate(e=>e.hidden),true);
 await page.locator('[data-item="279956"]').getByRole('button',{name:'View Crafting Recipe'}).click();assert.equal(await page.locator('.craft-detail h3').innerText(),'Mana Well');
 await page.getByRole('button',{name:'All Dungeons',exact:true}).click();assert.equal(await page.locator('.dungeon').count(),12);await page.getByRole('button',{name:'Quest Map',exact:true}).click();assert(await page.locator('.quest-marker').count());
 for(const width of [390,768]){await page.setViewportSize({width,height:950});await page.getByRole('button',{name:'Camping',exact:true}).click();assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.getByRole('button',{name:'Professions',exact:true}).click();assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))}
 const mobile=await browser.newPage({viewport:{width:390,height:844},hasTouch:true,isMobile:true});await mobile.route(/https?:\/\//,route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
 await mobile.goto(url);await mobile.getByRole('button',{name:'Camping',exact:true}).tap();await mobile.locator('.camp-feature').first().waitFor();const reward=mobile.locator('[data-item="279956"] .reward').first();await reward.tap();assert.equal(await reward.locator('.tooltip').evaluate(e=>e.hidden),false);await mobile.getByRole('button',{name:'Professions',exact:true}).tap();assert.equal(await mobile.locator('.tooltip-open').count(),0);
 assert.deepEqual(errors,[]);assert.deepEqual(missing,[]);await browser.close();console.log('PASS: recipes, ranks, sources, learned checklist, Camping, tooltip mouse/touch, maps, mobile layout; third-party requests blocked.');
})().catch(error=>{console.error(error);process.exit(1)});
