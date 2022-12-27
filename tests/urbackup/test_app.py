import sys

import freezegun
import pytest

from tests.fs_utils import mkdirs
from urbasys.urbackup import app


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


@freezegun.freeze_time("2022-12-18 14:00:00")
def test_delete_old(tmp_path, run):
    dir_2022_11_02 = mkdirs(tmp_path / "bak1" / "daily-2022-11-02T01:23:45.123456Z")
    dir_2022_11_03 = mkdirs(tmp_path / "bak1" / "daily-2022-11-03T01:23:45.123456Z")
    dir_2022_12_16 = mkdirs(tmp_path / "bak1" / "daily-2022-12-16T01:23:45.123456Z")
    dir_2022_12_18 = mkdirs(tmp_path / "bak1" / "daily-2022-12-18T01:23:45.123456Z")

    run(["delete-old", "--max-age=3 days", str(tmp_path / "bak1")])

    assert not dir_2022_11_02.is_dir()
    assert not dir_2022_11_03.is_dir()
    assert dir_2022_12_16.is_dir()
    assert dir_2022_12_18.is_dir()


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
