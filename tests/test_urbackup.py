import sys
from datetime import datetime
from pathlib import Path

import dateutil.tz
import pytest

from urbasys.urbackup.app import (
    backups_to_keep,
    keep_last,
    folder_to_datetime,
    monthlies_to_keep,
    main,
)


def mkdirs(path: Path) -> Path:
    path.mkdir(exist_ok=True, parents=True)
    return path


@pytest.fixture(name="run")
def fixture_run(monkeypatch):
    def run(args):
        monkeypatch.setattr(sys, "argv", ["urbackup"] + args)
        try:
            main()
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


def test_folder_to_datetime():
    assert folder_to_datetime(Path("daily-2019-06-13T02:02:40.603Z")) == datetime(
        2019, 6, 13, 2, 2, 40, 603000, tzinfo=dateutil.tz.tzutc()
    )
    assert folder_to_datetime(
        Path("/urbackup/mirror/pi1.urbas.si/daily-2022-12-18T04:10:05.849554073Z")
    ) == datetime(2022, 12, 18, 4, 10, 5, 849554, tzinfo=dateutil.tz.tzutc())


def test_keep_last_empty():
    assert keep_last([], number_to_keep=30) == []


def test_keep_last_all():
    old_backup = datetime(2019, 5, 13)
    new_backup = datetime(2019, 5, 14)
    assert keep_last([old_backup, new_backup], number_to_keep=2) == [
        new_backup,
        old_backup,
    ]


def test_keep_last_some_outdated():
    old_backup = datetime(2019, 5, 13)
    new_backup = datetime(2019, 5, 14)
    assert keep_last([old_backup, new_backup], number_to_keep=1) == [new_backup]


def test_monthlies_to_keep_empty():
    assert monthlies_to_keep([]) == set()


def test_monthlies_to_keep_some_keep_oldest():
    assert monthlies_to_keep(
        backup_dates=[
            datetime(2019, 5, 1),
            datetime(2019, 5, 2),
            datetime(2019, 4, 10),
            datetime(2019, 4, 22),
            datetime(2019, 1, 1),
            datetime(2019, 2, 2),
        ]
    ) == {
        datetime(2019, 5, 1),
        datetime(2019, 4, 10),
        datetime(2019, 2, 2),
        datetime(2019, 1, 1),
    }


def test_backups_to_keep():
    backup_dates = [
        datetime(2019, 5, 1),
        datetime(2019, 5, 2),
        datetime(2019, 4, 10),
        datetime(2019, 4, 22),
        datetime(2019, 1, 1),
        datetime(2019, 1, 2),
        datetime(2018, 12, 16),
        datetime(2018, 12, 29),
    ]
    assert backups_to_keep(backup_dates, keep_latest=4) == {
        datetime(2019, 5, 1),
        datetime(2019, 5, 2),
        datetime(2019, 4, 10),
        datetime(2019, 4, 22),
        datetime(2019, 1, 1),
        datetime(2018, 12, 16),
    }
    assert backups_to_keep(backup_dates, keep_latest=2) == {
        datetime(2019, 5, 1),
        datetime(2019, 5, 2),
        datetime(2019, 4, 10),
        datetime(2019, 1, 1),
        datetime(2018, 12, 16),
    }
