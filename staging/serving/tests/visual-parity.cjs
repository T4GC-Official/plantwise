// Visual/interaction regression against the deployed original. Evidence stays ignored.
const {chromium}=require('/browser/node_modules/playwright');const fs=require('fs');
const DIR='/work/runtime/visual-parity-20261111';
function check(value,message){if(!value)throw new Error(message);}
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});const report=[];

 for(const [size,viewport] of [['desktop',{width:1440,height:1050}],['mobile',{width:390,height:844}]]) {
  const reference=await browser.newPage({viewport});
  await reference.goto('https://plantwise-india.org/#/tool',{waitUntil:'networkidle'});
  await reference.locator('.leaflet-overlay-pane path').first().waitFor();
  await reference.waitForFunction(()=>Array.from(document.images).every(i=>i.complete),{timeout:20000});
  const before=await reference.locator('#latitude').boundingBox();
  await reference.screenshot({path:`${DIR}/reference-${size}-current.png`,fullPage:true,animations:'disabled'});
  await reference.close();
  const page=await browser.newPage({viewport});const requests=[],failures=[],errors=[];
  page.on('request',r=>requests.push({url:r.url(),method:r.method()}));page.on('pageerror',e=>errors.push(e.message));
  page.on('response',r=>{if(r.status()>=400)failures.push({url:r.url(),status:r.status()});});
  // Reproduce the read-only forwarding constraint under which the old client failed.
  await page.route('**/api/get-results**',r=>r.request().method()==='POST'?r.fulfill({status:405,body:''}):r.continue());
  for(const route of ['','about','model','tool']) {
   await page.goto(`http://127.0.0.1:8175/#/${route}`,{waitUntil:'networkidle'});
   await page.screenshot({path:`${DIR}/after-${size}-${route||'home'}.png`,fullPage:true,animations:'disabled'});
  }
  const text=await page.locator('body').innerText();
  for(const extra of ['Release:','ENMeval Java Maxent','cloglog suitability','planting success probability','Block-CV AUC']) check(!text.includes(extra),`Extra UI remains: ${extra}`);

  const now=await page.locator('#latitude').boundingBox();
  for(const dimension of ['x','y','width','height'])check(Math.abs(before[dimension]-now[dimension])<1,`${size} coordinate layout differs: ${dimension} ${before[dimension]} vs ${now[dimension]}`);
  await page.locator('#latitude').fill('17.519216206515345');await page.locator('#longitude').fill('73.60814321375223');
  const [response]=await Promise.all([page.waitForResponse(r=>r.url().includes('/api/get-results')),page.getByRole('button',{name:'Enter',exact:true}).click()]);
  check(response.request().method()==='GET'&&response.status()===200,'Recommendation request failed');
  const data=await response.json();check(data.length>0,'Screenshot coordinates returned no results');
  await page.getByRole('button',{name:data[0].species,exact:true}).waitFor();
  check(await page.locator('thead th').allTextContents().then(x=>JSON.stringify(x)===JSON.stringify(['#','Species Name','Suitability (%)'])),'Added result columns remain');
  await page.screenshot({path:`${DIR}/after-${size}-screenshot-coordinates.png`,fullPage:true,animations:'disabled'});
  await page.getByRole('button',{name:data[0].species,exact:true}).click();
  await page.getByAltText(`${data[0].species} map`,{exact:true}).waitFor();
  await page.screenshot({path:`${DIR}/after-${size}-preview.png`,fullPage:true,animations:'disabled'});
  await page.getByRole('button',{name:'Close',exact:true}).last().click();
  if(size==='desktop') {
   const map=page.locator('#map');const box=await map.boundingBox();
   function world(lat,lon){const s=256*2**7;const sin=Math.sin(lat*Math.PI/180);return {x:(lon+180)/360*s,y:(.5-Math.log((1+sin)/(1-sin))/(4*Math.PI))*s};}
   const center=world(15.5,75.5),target=world(17.519216206515345,73.60814321375223);
   await map.click({position:{x:box.width/2+target.x-center.x,y:box.height/2+target.y-center.y}});
   const lat=Number(await page.locator('#latitude').inputValue());check(Math.abs(lat-17.519216206515345)<.02,'Map click did not populate coordinates');
   const [clicked]=await Promise.all([page.waitForResponse(r=>r.url().includes('/api/get-results')),page.getByRole('button',{name:'Enter',exact:true}).click()]);
   check(clicked.status()===200&&(await clicked.json()).length>0,'Map query failed');
   await page.screenshot({path:`${DIR}/after-desktop-map-query.png`,fullPage:true,animations:'disabled'});
  }
  // Empty error responses must not produce a raw JSON exception or false no-results.
  await page.route('**/api/get-results**',r=>r.fulfill({status:502,body:''}));
  await page.getByRole('button',{name:'Enter',exact:true}).click();
  await page.getByRole('alert').filter({hasText:'Unable to load results. Please try again.'}).waitFor();
  const failedText=await page.locator('body').innerText();check(!failedText.includes('Unexpected end')&&!failedText.includes('No results found'),'Misleading failure UI');
  check(errors.length===0,'JavaScript exceptions');
  check(!requests.some(x=>/run\.app|plantwise-india\.org/.test(x.url)),'Production fallback request');
  check(!failures.some(x=>x.url.startsWith('http://127.0.0.1:8175')&&!x.url.includes('/api/get-results')),'Missing local asset');
  report.push({size,referenceBounds:before,actualBounds:now,queryCount:data.length,firstSpecies:data[0].species,requestMethod:response.request().method(),preview:true,mapClick:size==='desktop',emptyErrorHandled:true,errors,requests,failures});
  await page.close();
 }
 fs.writeFileSync(`${DIR}/after-verification.json`,JSON.stringify({passed:true,report},null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
