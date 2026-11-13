"""The manager must leave an unrelated installed unit untouched."""
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('plantwise_services', Path(__file__).resolve().parents[1] / 'services/manage.py')
manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)


def test_install_refuses_foreign_unit_without_systemctl(tmp_path, monkeypatch):
    unit = tmp_path / '.config/systemd/user' / manager.UNIT
    unit.parent.mkdir(parents=True)
    unit.write_text('owned by another checkout')
    monkeypatch.setattr(manager.Path, 'home', lambda: tmp_path)
    calls = []
    monkeypatch.setattr(manager, 'ctl', lambda *args, **kwargs: calls.append(args))
    with pytest.raises(SystemExit, match='Refusing to replace'):
        manager.install()
    assert unit.read_text() == 'owned by another checkout'
    assert calls == []
