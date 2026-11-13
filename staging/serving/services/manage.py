#!/usr/bin/env python3
"""Manage only the repository-owned PlantWise service on fixed port 8175."""
import argparse
import json
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
STAGING = HERE.parents[1]
UNIT = 'plantwise-staging.service'


def ctl(*args, check=True):
    return subprocess.run(['systemctl', '--user', *args], check=check)


def ready():
    expected = json.loads((STAGING / 'runtime/active/catalog.json').read_text())['release']
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen('http://127.0.0.1:8175/api/health', timeout=2) as response:
                health = json.load(response)
            if health.get('status') == 'ok' and health.get('release') == expected:
                with urllib.request.urlopen('http://127.0.0.1:8175/', timeout=2) as response:
                    if response.status == 200:
                        print(f'Ready: http://127.0.0.1:8175/ ({expected})')
                        return
        except (OSError, ValueError, urllib.error.URLError):
            pass
        time.sleep(.25)
    raise SystemExit('Readiness failed. Run: python3 staging/serving/services/manage.py logs')


def install():
    directory = Path.home() / '.config/systemd/user'
    directory.mkdir(parents=True, exist_ok=True)
    link = directory / UNIT
    source = HERE / UNIT
    if (link.exists() or link.is_symlink()) and (not link.is_symlink() or link.resolve() != source):
        raise SystemExit(f'Refusing to replace a unit not linked to this checkout: {link}')
    # Unit paths match the standard checkout location; avoid installing a broken unit elsewhere.
    expanded_unit = source.read_text().replace('%h', str(Path.home())).splitlines()
    if f'WorkingDirectory={STAGING / "serving"}' not in expanded_unit:
        raise SystemExit('Update the repository unit paths for this checkout before installing.')
    if not link.is_symlink():
        link.symlink_to(source)
    ctl('daemon-reload')
    ctl('enable', UNIT)
    print('Installed repository unit link and enabled startup. Use start to run on 8175.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['install', 'start', 'stop', 'restart', 'status', 'logs', 'disable'])
    action = parser.parse_args().action
    if action == 'install':
        install()
    elif action == 'status':
        raise SystemExit(ctl('status', UNIT, '--no-pager', check=False).returncode)
    elif action == 'logs':
        subprocess.run(['journalctl', '--user', '-u', UNIT, '-n', '60', '--no-pager'], check=True)
    elif action == 'disable':
        ctl('disable', '--now', UNIT)
    else:
        if action == 'restart':
            ctl('daemon-reload')
        ctl(action, UNIT)
        if action in {'start', 'restart'}:
            ready()


if __name__ == '__main__':
    main()
