#!/usr/bin/env python3
"""Terminal inventory audit; writes private detailed evidence under the run only."""
from accounting import classify_status
import collections
import json
from pathlib import Path
import sys
import pandas as pd
run=Path(sys.argv[1])
config=json.loads((run/'config.json').read_text());species=config['species']
states=[classify_status(json.loads((run/sp/'status.json').read_text())) for sp in species]
assert len(states)==len(species)==len(set(s['species'] for s in states))
assert all(s['status'] in ('success','excluded','failed') for s in states)
rows=[]
for state in states:
    if state['status']=='success':
        sp=state['species'];directory=run/sp
        for name in (f'{sp}_model.rds',f'{sp}_evaluation.rds',f'{sp}_SDM.tif',f'{sp}_Plot.png',f'{sp}_all_tunes.csv','metrics.csv','provenance.json','sessionInfo.txt','R-packages.csv'):
            assert (directory/name).stat().st_size>0,(sp,name)
        row=pd.read_csv(directory/'metrics.csv').iloc[0]
        assert int(row.n_final)==int(row.n_occ)
        rows.append(row)
metrics=pd.DataFrame(rows)
metrics.to_csv(run/'all-success-metrics.csv',index=False)
cleaned=[s['occurrence_counts'] for s in states if 'occurrence_counts' in s]
cleaning={key:sum(c[key] for c in cleaned) for key in ('raw','finite','in_boundary','complete_case','unique_cell')}
if len(cleaned)==len(species): assert cleaning['raw']==14180
summary={'cleaning':cleaning,'species_with_cleaning_counts':len(cleaned),'requested':len(species),'counts':dict(collections.Counter(s['status'] for s in states)),
         'classifications':dict(collections.Counter(s['classification'] for s in states)),
         'reasons':dict(collections.Counter(s.get('reason') for s in states if s['status']!='success')),
         'auc_block_cv':{k:float(v) for k,v in metrics['auc.val.avg'].describe().items()},
         'auc_below_half':int((metrics['auc.val.avg']<.5).sum()),
         'settings':dict(collections.Counter(str(r.fc)+'/RM'+str(r.rm) for _,r in metrics.iterrows())),
         'timing_seconds':{'total_job_seconds':sum(s['elapsed_seconds'] for s in states if 'elapsed_seconds' in s),'max_job_seconds':max(s.get('elapsed_seconds',0) for s in states)}}
(run/'final-audit.json').write_text(json.dumps(summary,indent=2))
(run/'accounting.json').write_text(json.dumps(states,indent=2))
print(json.dumps(summary,indent=2))
