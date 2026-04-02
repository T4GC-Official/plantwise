#!/usr/bin/env bash
set -euo pipefail

cd /app

python3 - <<'PY'
from pathlib import Path
import generate_reports

root = Path('/app')
path, count = generate_reports.build_manifest(root)
print(f"Rebuilt report manifest at {path} with {count} reports")
PY

exec python3 src/backend/app.py
