import sys
from pathlib import Path

import pytest

from urbasys.urbackup import app


def mkdirs(path: Path) -> Path:
    path.mkdir(exist_ok=True, parents=True)
    return path


@pytest.fixture(name="run")
def fixture_run(monkeypatch):
    def run(args):
        monkeypatch.setattr(sys, "argv", ["urbackup"] + args)
        try:
            app.main()
        except SystemExit as ex:
            if ex.code != 0:
                raise

    return run


def test_retain_monthlies(tmp_path, run):
    dir_2022_11_01 = mkdirs(tmp_path / "bak1" / "daily-2022-11-01T01:23:45.123456Z")
    dir_2022_11_02 = mkdirs(tmp_path / "bak1" / "daily-2022-11-02T01:23:45.123456Z")
    dir_2022_11_03 = mkdirs(tmp_path / "bak1" / "daily-2022-11-03T01:23:45.123456Z")
    dir_2022_12_16 = mkdirs(tmp_path / "bak1" / "daily-2022-12-16T01:23:45.123456Z")
    dir_2022_12_17 = mkdirs(tmp_path / "bak1" / "daily-2022-12-17T01:23:45.123456Z")
    dir_2022_12_18 = mkdirs(tmp_path / "bak1" / "daily-2022-12-18T01:23:45.123456Z")

    run(["retain-monthlies", "--keep-latest=1", str(tmp_path / "bak1")])

    assert dir_2022_11_01.is_dir()
    assert not dir_2022_11_02.is_dir()
    assert not dir_2022_11_03.is_dir()
    assert dir_2022_12_16.is_dir()
    assert not dir_2022_12_17.is_dir()
    assert dir_2022_12_18.is_dir()


def test_retain_monthlies_keep_all(tmp_path, run):
    dir_2022_11_01 = mkdirs(tmp_path / "bak1" / "daily-2022-11-01T01:23:45.123456Z")
    dir_2022_11_02 = mkdirs(tmp_path / "bak1" / "daily-2022-11-02T01:23:45.123456Z")
    dir_2022_11_03 = mkdirs(tmp_path / "bak1" / "daily-2022-11-03T01:23:45.123456Z")
    dir_2022_12_16 = mkdirs(tmp_path / "bak1" / "daily-2022-12-16T01:23:45.123456Z")
    dir_2022_12_17 = mkdirs(tmp_path / "bak1" / "daily-2022-12-17T01:23:45.123456Z")
    dir_2022_12_18 = mkdirs(tmp_path / "bak1" / "daily-2022-12-18T01:23:45.123456Z")

    run(["retain-monthlies", "--keep-latest=6", str(tmp_path / "bak1")])

    assert dir_2022_11_01.is_dir()
    assert dir_2022_11_02.is_dir()
    assert dir_2022_11_03.is_dir()
    assert dir_2022_12_16.is_dir()
    assert dir_2022_12_17.is_dir()
    assert dir_2022_12_18.is_dir()


def test_retain_monthlies_keep_many_years(tmp_path, run):
    dir_2021_11_01 = mkdirs(tmp_path / "bak1" / "daily-2021-11-01T01:23:45.123456Z")
    dir_2022_11_01 = mkdirs(tmp_path / "bak1" / "daily-2022-11-01T01:23:45.123456Z")
    dir_2022_12_18 = mkdirs(tmp_path / "bak1" / "daily-2022-12-18T01:23:45.123456Z")

    run(["retain-monthlies", "--keep-latest=1", str(tmp_path / "bak1")])

    assert dir_2021_11_01.is_dir()
    assert dir_2022_11_01.is_dir()
    assert dir_2022_12_18.is_dir()
