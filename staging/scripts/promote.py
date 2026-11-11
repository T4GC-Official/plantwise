#!/usr/bin/env python3
"""Atomic local release selection; service restart loads it once."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
release=(ROOT/'releases'/sys.argv[1]).resolve(strict=True)
assert release.parent==ROOT/'releases'
for name,want in json.loads((release/'checksums.json').read_text()).items():
    p=release/name
    assert p.resolve().is_relative_to(release)
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    assert h.hexdigest()==want,name
runtime=ROOT/'runtime';runtime.mkdir(exist_ok=True)
tmp=runtime/'active.next';tmp.symlink_to(release);tmp.replace(runtime/'active')
print(release.name)
