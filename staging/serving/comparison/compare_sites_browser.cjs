// Read-only deployed-site comparison; no model/filter/service changes.
const {chromium}=require('/browser/node_modules/playwright');const fs=require('fs');
const DIR=process.env.PLANTWISE_COMPARISON_DIR||'/work/runtime/comparison-20261112-kodagu';
fs.mkdirSync(DIR,{recursive:true});
(async()=>{const browser=await chromium.launch({headless:true,args:['--no-sandbox']});const summary=[];
for(const [name,origin] of [['live','https://plantwise-india.org'],['staging','http://100.82.28.38:8175']]){
 const page=await browser.newPage({viewport:{width:1440,height:1050}});const errors=[],failures=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failures.push({url:r.url(),error:r.failure()?.errorText}));
 await page.goto(`${origin}/#/tool`,{waitUntil:'networkidle',timeout:60000});
 await page.locator('#latitude').fill('12.189703804004086');await page.locator('#longitude').fill('75.94048174979808');
 const threshold=await page.locator('input[type=range]').inputValue();if(threshold!=='50')throw new Error(`Unexpected default threshold ${threshold}`);
 const values={latitude:await page.locator('#latitude').inputValue(),longitude:await page.locator('#longitude').inputValue(),threshold};
 const [r]=await Promise.all([page.waitForResponse(r=>r.url().includes('/api/get-results')&&r.request().method()!=='OPTIONS',{timeout:180000}),page.getByRole('button',{name:'Enter',exact:true}).click()]);
 const raw=await r.text();let data;try{data=JSON.parse(raw)}catch{data=null}
 fs.writeFileSync(`${DIR}/${name}-browser-response-body.json`,raw);
 const request=r.request();const record={name,captured_at:new Date().toISOString(),page_url:page.url(),inputs:values,request:{url:request.url(),method:request.method(),body:request.postData(),headers:await request.allHeaders()},response:{status:r.status(),headers:await r.allHeaders()},count:Array.isArray(data)?data.length:null,errors,failures};
 fs.writeFileSync(`${DIR}/${name}-browser-http.json`,JSON.stringify(record,null,2));
 if(!r.ok()||!Array.isArray(data))throw new Error(`${name} API response ${r.status()}: ${raw.slice(0,300)}`);
 await page.waitForFunction(n=>document.querySelectorAll('tbody tr').length===n,data.length,{timeout:15000});
 record.displayed_rows=await page.locator('tbody tr').allTextContents();
 await page.locator('h5').filter({hasText:'Results'}).scrollIntoViewIfNeeded();
 await page.screenshot({path:`${DIR}/${name}-results-desktop.png`,fullPage:true,animations:'disabled'});
 fs.writeFileSync(`${DIR}/${name}-browser-http.json`,JSON.stringify(record,null,2));summary.push(record);
 console.log(JSON.stringify({site:name,request:record.request,count:data.length,species:data.map(x=>x.species)},null,2));await page.close();
}
fs.writeFileSync(`${DIR}/browser-comparison.json`,JSON.stringify(summary,null,2));await browser.close();})().catch(e=>{console.error(e);process.exit(1)});
