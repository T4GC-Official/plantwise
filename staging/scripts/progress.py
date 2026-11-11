#!/usr/bin/env python3
"""Summarize terminal species states without opening private occurrence records."""
import collections
import json
from pathlib import Path
import sys
run=Path(sys.argv[1]);config=json.loads((run/'config.json').read_text())
states=[]
for sp in config['species']:
    file=run/sp/'status.json'
    if file.exists(): states.append(json.loads(file.read_text()))
counts=collections.Counter(x['status'] for x in states)
reasons=collections.Counter(x.get('reason') for x in states if x['status'] in ('failed','excluded'))
print(json.dumps({'requested':len(config['species']),'counts':dict(counts),'not_started':len(config['species'])-len(states),'reasons':dict(reasons)},indent=2))
