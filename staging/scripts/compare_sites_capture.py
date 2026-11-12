"""Capture read-only numeric POST comparisons; browser requests are captured separately."""
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import httpx

OUT=Path(os.environ.get('PLANTWISE_COMPARISON_DIR',Path(__file__).resolve().parents[1]/'runtime/comparison-20261112-kodagu'))
OUT.mkdir(parents=True,exist_ok=True)
COORD={'latitude':12.189703804004086,'longitude':75.94048174979808}
ENDPOINTS={'live':'https://species-api-452165326340.asia-south1.run.app/api/get-results','staging':'http://100.82.28.38:8175/api/get-results'}
with httpx.Client(timeout=180) as client:
 for threshold in (50,0):
  for name,url in ENDPOINTS.items():
   body={**COORD,'minProbability':threshold}
   response=client.post(url,json=body,headers={'Origin':'https://plantwise-india.org'} if name=='live' else {})
   evidence={'captured_at':datetime.now(timezone.utc).isoformat(),'request':{'url':url,'method':'POST','json':body},'response':{'status':response.status_code,'headers':dict(response.headers),'body':response.text}}
   (OUT/f'{name}-threshold-{threshold}-http.json').write_text(json.dumps(evidence,indent=2))
   response.raise_for_status();data=response.json();assert isinstance(data,list)
   (OUT/f'{name}-threshold-{threshold}.json').write_text(json.dumps(data,indent=2))
   print(name,threshold,len(data),flush=True)
   if threshold==50:
    browser=json.loads((OUT/f'{name}-browser-response-body.json').read_text())
    assert {r['species']:r for r in browser}=={r['species']:r for r in data},f'{name} UI/direct response mismatch'
 for path in ('openapi.json',''):
  url='https://species-api-452165326340.asia-south1.run.app/'+path
  response=client.get(url)
  (OUT/('live-openapi.json' if path else 'live-api-root.html')).write_text(response.text)
  print('live',path or 'root',response.status_code,flush=True)
