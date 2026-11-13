const {chromium}=require('/browser/node_modules/playwright');const fs=require('fs');
const ORIGIN=process.env.PLANTWISE_DIFF_ORIGIN||'http://127.0.0.1:8184';const OUT=process.env.PLANTWISE_DIFF_EVIDENCE||'/work/runtime/diff-page-20261112';fs.mkdirSync(OUT,{recursive:true});
const assert=(v,m)=>{if(!v)throw new Error(m)};
(async()=>{const browser=await chromium.launch({headless:true,args:['--no-sandbox']});const evidence=[];let original;
for(const [device,viewport] of [['desktop',{width:1440,height:1100}],['mobile',{width:390,height:844}]]){
 const page=await browser.newPage({viewport});const errors=[],requests=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
 await page.goto(`${ORIGIN}/diff`,{waitUntil:'networkidle'});
 assert(requests.filter(url=>url.includes('/api/diff?')).length===0,'Comparison ran on page load');
 const [response]=await Promise.all([page.waitForResponse(r=>r.url().includes('/api/diff?')&&r.status()===200),page.getByRole('button',{name:'Compare both models',exact:true}).click()]);
 if(!original)original=await response.json();
 await page.getByTestId('staging-count').waitFor({timeout:60000});
 assert(await page.getByTestId('staging-count').textContent()==='23','Staging count');assert(await page.getByTestId('live-count').textContent()==='9','Live count');assert(await page.getByTestId('shared-count').textContent()==='5','Shared count');assert(await page.getByTestId('different-count').textContent()==='22','Difference count');
 assert(await page.locator('tbody tr').count()===265,'Full zero-cutoff union retained');
 assert(await page.locator('.diff-table thead th').count()===3,'Three result columns');
 await page.getByRole('heading',{name:'Click the map to compare staging with PlantWise India.',exact:true}).waitFor();
 const excluded=page.locator('[data-species="Ficus_talbotii"]');assert((await excluded.textContent()).includes('5 usable'),'Exclusion explanation');
 const below=page.locator('[data-species="Clausena_anisata"]');assert(await below.locator('.is-below').count()===1,'Below threshold shading');
 assert(!(await page.locator('.pw-diff').innerText()).match(/[·←→↑↓]/),'Decorative dot or arrow');
 assert(await page.locator('summary').first().textContent()==='Why?','Dropdown label');
 await page.screenshot({path:`${OUT}/${device}-overview.png`,animations:'disabled'});
 await page.getByRole('button',{name:'Only differences (22)',exact:true}).click();assert(await page.locator('tbody tr').count()===22,'Only differences filter');
 await excluded.locator('summary').click();assert((await excluded.textContent()).includes('No staging model'),'Dropdown explanation');
 assert((await excluded.textContent()).includes('Staging block-CV AUC: unavailable'),'Excluded AUC status');
 await below.locator('summary').click();assert((await below.textContent()).includes('Staging block-CV AUC: 0.624'),'Staging AUC');assert((await below.textContent()).includes('Live reported AUC:'),'Live AUC');
 await page.locator('.diff-toolbar').scrollIntoViewIfNeeded();await page.screenshot({path:`${OUT}/${device}-differences.png`,animations:'disabled'});
 await page.getByLabel('Search species').fill('Clausena');assert(await page.locator('tbody tr').count()===1,'Search');
 await page.getByLabel('Search species').fill('');await page.getByRole('button',{name:'All scores (265)',exact:true}).click();
 await page.getByLabel('Suitability cutoff',{exact:true}).fill('0');assert(await page.getByTestId('staging-count').textContent()==='231','Zero staging');assert(await page.getByTestId('live-count').textContent()==='264','Zero live');assert(await page.locator('.is-below').count()===0,'Zero cutoff still shaded');
 await page.getByLabel('Suitability cutoff',{exact:true}).fill('50');
 const map=page.locator('.diff-map');const box=await map.boundingBox();
 const beforeClicks=requests.filter(url=>url.includes('/api/diff?')).length;
 for(const offset of [12,18])await map.click({position:{x:box.width/2-offset,y:box.height/2}});
 await page.getByRole('status').filter({hasText:'Location changed.'}).waitFor();
 assert(requests.filter(url=>url.includes('/api/diff?')).length===beforeClicks,'Map selection ran a comparison');
 const selected={latitude:Number(await page.getByLabel('Latitude',{exact:true}).inputValue()),longitude:Number(await page.getByLabel('Longitude',{exact:true}).inputValue())};
 const [clicked]=await Promise.all([page.waitForResponse(r=>r.url().includes('/api/diff?')),page.getByRole('button',{name:'Compare both models',exact:true}).click()]);
 assert(clicked.status()===200,'Compare button API');const clickedData=await clicked.json();assert(clickedData.live.status==='available','Map click live result');assert(Math.abs(clickedData.query.longitude-75.94048174979808)>.01,'Map click did not update location');
 assert(clickedData.query.latitude===selected.latitude&&clickedData.query.longitude===selected.longitude,'Submitted wrong selected coordinates');
 await page.getByTestId('staging-count').waitFor();assert(await page.getByRole('status').filter({hasText:'Location changed.'}).count()===0,'Pending location message remained');await page.screenshot({path:`${OUT}/${device}-map-click.png`,animations:'disabled'});
 await page.getByRole('navigation').getByRole('link',{name:'What changed?',exact:true}).click();await page.getByRole('heading',{name:'Why can the predictions differ?',exact:true}).waitFor();await page.screenshot({path:`${OUT}/${device}-model.png`,animations:'disabled'});
 assert(new URL(page.url()).pathname==='/model','Clean model route');
 for(const [label,path] of [['Old:','/source/old/InitialImplementation.py'],['New:','/source/new/train.R']]){const links=page.locator('.diff-score-changes').getByRole('link',{name:label,exact:true});assert(await links.count()===3,'Source link count');assert(await links.first().getAttribute('href')===path,'Source link target');const source=await page.request.get(`${ORIGIN}${path}`);assert(source.status()===200&&source.headers()['content-type'].startsWith('text/plain'),'Source response');const [sourcePage]=await Promise.all([page.waitForEvent('popup'),links.first().click()]);await sourcePage.waitForLoadState();assert((await sourcePage.locator('body').innerText()).includes(label==='Old:'?'presence_points[0] > 2':'nrow(o$xy)<8'),'Source content');if(device==='desktop')await sourcePage.screenshot({path:`${OUT}/${label==='Old:'?'old':'new'}-source.png`});await sourcePage.close();}

 await page.getByRole('heading',{name:'Summary of model differences',exact:true}).waitFor();
 assert(await page.getByRole('heading',{name:'About the synced TIFF files',exact:true}).count()===0,'Removed TIFF section');await page.reload({waitUntil:'networkidle'});await page.getByRole('heading',{name:'Why can the predictions differ?',exact:true}).waitFor();
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),'Horizontal page overflow');
 assert(errors.length===0,JSON.stringify(errors));evidence.push({device,counts:{staging:23,live:9,shared:5,different:22,zeroUnion:265},errors,requests});
 await page.close();
}
// A live outage must never become a false "staging-only" comparison.
const p=await browser.newPage();
const unavailable={...original,live:{status:'unavailable',error:'Live unavailable for test'},rows:original.rows.map(r=>({...r,live:{status:'source_unavailable',score:null,reason:'Live unavailable for test'}}))};
await p.route('**/api/diff?**',r=>r.fulfill({json:unavailable}));await p.goto(`${ORIGIN}/diff`,{waitUntil:'networkidle'});await p.getByRole('button',{name:'Compare both models',exact:true}).click();await p.getByRole('alert').waitFor();assert(await p.getByTestId('live-count').textContent()==='-','Outage represented as zero');assert(await p.locator('.badge-staging').count()===0,'Outage false differences');await p.close();
fs.writeFileSync(`${OUT}/browser-verification.json`,JSON.stringify({passed:true,origin:ORIGIN,evidence,live_outage_handled:true},null,2));await browser.close();console.log('Diff desktop/mobile comparison and outage checks passed');})().catch(e=>{console.error(e);process.exit(1)});
