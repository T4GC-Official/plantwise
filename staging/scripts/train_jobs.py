#!/usr/bin/env python3
"""Sequential resumable jobs. A changed code/image/input fingerprint needs a new run."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
IMAGE = 'plantwise-training:20261111'

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024), b''): h.update(c)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('--species');p.add_argument('--gate');p.add_argument('--workers',type=int,default=1,choices=(1,2,3));a=p.parse_args()
    data=pd.read_csv(ROOT/'data/occurrences/filtered_species_output.csv')
    species=[a.species] if a.species else sorted(data.Species.unique())
    assert len(data)==14180 and data.Species.nunique()==448 and set(species)<=set(data.Species)
    if not a.species:
        if not a.gate: p.error('Full training requires --gate pointing to real pass-1 acceptance evidence')
        gate=json.loads(Path(a.gate).read_text())
        assert gate['passed'] and gate['browser_passed'] and gate['api_passed']
    run=ROOT/'runs'/a.run;run.mkdir(parents=True,exist_ok=True)
    files=[ROOT/'models/enmeval/train.R',ROOT/'scripts/train_jobs.py',ROOT/'data/occurrences/filtered_species_output.csv',ROOT/'data/derived/bias_layer/biasBg.csv',ROOT/'models/maxent/maxent.jar']
    files+=sorted((ROOT/'data/attributes').glob('*.tif'))+sorted((ROOT/'data/boundary').glob('*'))
    image_id=subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',IMAGE],text=True).strip()
    config={'species':species,'image':image_id,'inputs_and_code':{str(x.relative_to(ROOT)):digest(x) for x in files if x.is_file()},'seed':123,'fc':['L','LQ'],'rm':[1,2],'partitions':'block','threads':1,'job_cpus':2,'job_memory':'8g','workers':a.workers}
    manifest=run/'config.json'
    if manifest.exists(): assert json.loads(manifest.read_text())==config, 'Immutable config changed: use a NEW run ID'
    else: manifest.write_text(json.dumps(config,indent=2))
    def train_one(item):
        i,sp=item
        job=run/sp;state=job/'status.json'
        if state.exists() and json.loads(state.read_text())['status'] in ('success','excluded','failed'):
            print(f'{i}/{len(species)} {sp}: retained terminal status',flush=True);return
        # Interrupted attempts are retained and moved aside rather than overwritten.
        if job.exists(): job.rename(run/f'{sp}.interrupted-{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")}')
        job.mkdir()
        container=f'plantwise-{a.run}-{sp}-{datetime.now(timezone.utc).strftime("%H%M%S%f")}'.lower().replace('_','-')
        cmd=['docker','run','--name',container,'--cpus','2','--memory','8g','--network','none',
             '-e','OMP_NUM_THREADS=1','-e','OPENBLAS_NUM_THREADS=1','-e','MKL_NUM_THREADS=1',
             '-v',f'{ROOT}:/work',IMAGE,'Rscript','models/enmeval/train.R',f'--species={sp}',f'--output_dir=/work/runs/{a.run}/{sp}']
        print(f'{i}/{len(species)} {sp}: starting',flush=True)
        samples=[]
        with (job/'training.log').open('w') as log:
            process=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
            while process.poll() is None:
                stats=subprocess.run(['docker','stats','--no-stream','--format','{{json .}}',container],capture_output=True,text=True)
                if stats.returncode==0 and stats.stdout.strip():
                    samples.append(json.loads(stats.stdout))
                try: process.wait(timeout=3)
                except subprocess.TimeoutExpired: pass
            result=process
        (job/'resources.json').write_text(json.dumps(samples,indent=2))
        if not state.exists() or json.loads(state.read_text()).get('status')=='running':
            temp=state.with_suffix('.tmp');temp.write_text(json.dumps({'species':sp,'status':'failed','reason':f'container_exit_{result.returncode}_without_terminal_status'}));temp.replace(state)
        print(state.read_text(),flush=True)
    # Start full work serially, then ramp to 2 jobs and only then the configured
    # ceiling (max 3 = six CPUs/24 GiB caps on this shared 20-core host).
    items=list(enumerate(species,1))
    warmup=min(2,len(items))
    for item in items[:warmup]: train_one(item)
    ramp_end=min(warmup+4,len(items))
    with ThreadPoolExecutor(max_workers=min(2,a.workers)) as pool:
        list(pool.map(train_one,items[warmup:ramp_end]))
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        list(pool.map(train_one,items[ramp_end:]))
    states=[json.loads((run/sp/'status.json').read_text()) for sp in species]
    (run/'accounting.json').write_text(json.dumps(states,indent=2))
    print(json.dumps({k:sum(x['status']==k for x in states) for k in ('success','excluded','failed')}),flush=True)
    return 1 if any(x['status']=='failed' for x in states) else 0

if __name__=='__main__': sys.exit(main())
