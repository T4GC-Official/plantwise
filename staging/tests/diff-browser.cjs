const {chromium}=require('/browser/node_modules/playwright');const fs=require('fs');
const ORIGIN=process.env.PLANTWISE_DIFF_ORIGIN||'http://127.0.0.1:8184';const OUT='/work/runtime/diff-page-20261112';
const assert=(v,m)=>{if(!v)throw new Error(m)};
(async()=>{const browser=await chromium.launch({headless:true,args:['--no-sandbox']});const evidence=[];let original;
for(const [device,viewport] of [['desktop',{width:1440,height:1100}],['mobile',{width:390,height:844}]]){
 const page=await browser.newPage({viewport});const errors=[],requests=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
 const [response]=await Promise.all([page.waitForResponse(r=>r.url().includes('/api/diff?')&&r.status()===200),page.goto(`${ORIGIN}/diff`,{waitUntil:'networkidle'})]);
 if(!original)original=await response.json();
 await page.getByTestId('staging-count').waitFor({timeout:60000});
 assert(await page.getByTestId('staging-count').textContent()==='23','Staging count');assert(await page.getByTestId('live-count').textContent()==='9','Live count');assert(await page.getByTestId('shared-count').textContent()==='5','Shared count');assert(await page.getByTestId('different-count').textContent()==='22','Difference count');
 assert(await page.locator('tbody tr').count()===265,'Full zero-cutoff union retained');
 const excluded=page.locator('[data-species="Ficus_talbotii"]');assert((await excluded.textContent()).includes('5 usable'),'Exclusion explanation');
 const below=page.locator('[data-species="Clausena_anisata"]');assert(await below.locator('.is-below').count()===1,'Below threshold shading');
 await page.screenshot({path:`${OUT}/${device}-overview.png`,animations:'disabled'});
 await page.getByRole('button',{name:'Only differences (22)',exact:true}).click();assert(await page.locator('tbody tr').count()===22,'Only differences filter');
 if(device==='mobile'){await excluded.locator('summary').click();assert((await excluded.textContent()).includes('No staging model'),'Mobile explanation');}
 await page.locator('.diff-toolbar').scrollIntoViewIfNeeded();await page.screenshot({path:`${OUT}/${device}-differences.png`,animations:'disabled'});
 await page.getByLabel('Search species').fill('Clausena');assert(await page.locator('tbody tr').count()===1,'Search');
 await page.getByLabel('Search species').fill('');await page.getByRole('button',{name:'All scores (265)',exact:true}).click();
 await page.getByLabel('Suitability cutoff',{exact:true}).fill('0');assert(await page.getByTestId('staging-count').textContent()==='231','Zero staging');assert(await page.getByTestId('live-count').textContent()==='264','Zero live');assert(await page.locator('.is-below').count()===0,'Zero cutoff still shaded');
 await page.getByLabel('Suitability cutoff',{exact:true}).fill('50');
 const map=page.locator('.diff-map');const box=await map.boundingBox();
 const [clicked]=await Promise.all([page.waitForResponse(r=>r.url().includes('/api/diff?')),map.click({position:{x:box.width/2-18,y:box.height/2}})]);
 assert(clicked.status()===200,'Map click API');const clickedData=await clicked.json();assert(clickedData.live.status==='available','Map click live result');assert(Math.abs(clickedData.query.longitude-75.94048174979808)>.01,'Map click did not update location');
 await page.getByTestId('staging-count').waitFor();await page.screenshot({path:`${OUT}/${device}-map-click.png`,animations:'disabled'});
 await page.getByRole('navigation').getByRole('link',{name:'What changed?',exact:true}).click();await page.getByRole('heading',{name:'Why can the predictions differ?',exact:true}).waitFor();await page.screenshot({path:`${OUT}/${device}-model.png`,animations:'disabled'});
 assert(new URL(page.url()).pathname==='/model','Clean model route');await page.reload({waitUntil:'networkidle'});await page.getByRole('heading',{name:'Why can the predictions differ?',exact:true}).waitFor();
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),'Horizontal page overflow');
 assert(errors.length===0,JSON.stringify(errors));evidence.push({device,counts:{staging:23,live:9,shared:5,different:22,zeroUnion:265},errors,requests});
 await page.close();
}
// A live outage must never become a false "staging-only" comparison.
const p=await browser.newPage();
const unavailable={...original,live:{status:'unavailable',error:'Live unavailable for test'},rows:original.rows.map(r=>({...r,live:{status:'source_unavailable',score:null,reason:'Live unavailable for test'}}))};
await p.route('**/api/diff?**',r=>r.fulfill({json:unavailable}));await p.goto(`${ORIGIN}/diff`,{waitUntil:'networkidle'});await p.getByRole('alert').waitFor();assert(await p.getByTestId('live-count').textContent()==='—','Outage represented as zero');assert(await p.locator('.badge-staging').count()===0,'Outage false differences');await p.close();
fs.writeFileSync(`${OUT}/browser-verification.json`,JSON.stringify({passed:true,origin:ORIGIN,evidence,live_outage_handled:true},null,2));await browser.close();console.log('Diff desktop/mobile comparison and outage checks passed');})().catch(e=>{console.error(e);process.exit(1)});
