// Run inside the isolated Playwright container with --network host.
const { chromium } = require('/browser/node_modules/playwright');
const fs = require('fs');
(async () => {
 const evidence = JSON.parse(fs.readFileSync('/work/runtime/live-api-evidence.json'));
 const query = evidence.real_query;
 const browser = await chromium.launch({headless:true,args:['--no-sandbox']});
 const page = await browser.newPage({viewport:{width:1440,height:1050}});
 const requests=[], failures=[], pageErrors=[], consoleErrors=[];
 page.on('request',r=>requests.push(r.url()));
 page.on('response',r=>{if(r.status()>=400)failures.push({url:r.url(),status:r.status()});});
 page.on('pageerror',e=>pageErrors.push(e.message));
 page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});
 await page.goto('http://127.0.0.1:8175/',{waitUntil:'networkidle'});
 await page.screenshot({path:'/work/runtime/homepage.png',fullPage:true});
 await page.goto('http://127.0.0.1:8175/#/tool',{waitUntil:'networkidle'});
 await page.getByLabel('Latitude:',{exact:true}).fill(String(query.latitude));
 await page.getByLabel('Longitude:',{exact:true}).fill(String(query.longitude));
 await page.locator('input[type=range]').fill('0');
 await page.getByRole('button',{name:'Enter',exact:true}).click();
 await page.getByRole('button',{name:query.species,exact:true}).waitFor();
 await page.screenshot({path:'/work/runtime/manual-query.png',fullPage:true});
 await page.getByRole('button',{name:query.species,exact:true}).click();
 await page.getByAltText(`${query.species} map`,{exact:true}).waitFor();
 await page.screenshot({path:'/work/runtime/species-preview.png',fullPage:true});
 await page.getByRole('button',{name:'Close',exact:true}).last().click();
 // Use actual Leaflet drag/zoom controls and screen click, not a fabricated API call.
 // Zoom out until the entire WG is visible, then use measured projection from known
 // center/zoom rendered by Leaflet. Geometry is read from the exact local WG asset.
 const map=page.locator('#map');
 const box=await map.boundingBox();
 // Initial center 15.5/75.5, zoom7; use WebMercator to click a known real query pixel.
 function world(lat,lon,z){const s=256*2**z;const sin=Math.sin(lat*Math.PI/180);return {x:(lon+180)/360*s,y:(.5-Math.log((1+sin)/(1-sin))/(4*Math.PI))*s};}
 // Recenter by dragging the map so the known query is visible at the current zoom.
 const center=world(15.5,75.5,7),target=world(query.latitude,query.longitude,7);
 const dx=target.x-center.x,dy=target.y-center.y;
 if (box.width/2+dx < 0 || box.width/2+dx > box.width || box.height/2+dy < 0 || box.height/2+dy > box.height) throw new Error('Known query outside visible initial map; adjust test viewport');
 await map.click({position:{x:box.width/2+dx,y:box.height/2+dy}});
 const selectedLat=Number(await page.getByLabel('Latitude:',{exact:true}).inputValue());
 const selectedLon=Number(await page.getByLabel('Longitude:',{exact:true}).inputValue());
 if(Math.abs(selectedLat-query.latitude)>.15||Math.abs(selectedLon-query.longitude)>.15)throw new Error('Map click did not update real coordinates');
 await Promise.all([page.waitForResponse(r=>r.url().endsWith('/api/get-results')&&r.request().method()==='POST'), page.getByRole('button',{name:'Enter',exact:true}).click()]);
 await page.screenshot({path:'/work/runtime/map-query.png',fullPage:true});
 // Manual outside-WG input must expose the local API error.
 await page.getByLabel('Latitude:',{exact:true}).fill('0');await page.getByLabel('Longitude:',{exact:true}).fill('0');
 await page.getByRole('button',{name:'Enter',exact:true}).click();
 await page.getByRole('alert').filter({hasText:'outside the Western Ghats'}).waitFor();
 const production=requests.filter(x=>/run\.app|plantwise-india\.org|localhost:8080/.test(x));
 const localFailures=failures.filter(x=>x.url.startsWith('http://127.0.0.1:8175')&&!(x.url.endsWith('/api/get-results')&&x.status===422));
 if(production.length||localFailures.length||pageErrors.length)throw new Error(JSON.stringify({production,localFailures,pageErrors}));
 const result={release:evidence.release,browser_passed:true,manual_query:true,map_query:true,preview:true,outside_wg:true,requests,failures,pageErrors,consoleErrors,production};
 fs.writeFileSync('/work/runtime/browser-evidence.json',JSON.stringify(result,null,2));
 console.log(JSON.stringify({...result,requests:requests.length},null,2));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
