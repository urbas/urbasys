from datetime import datetime, timedelta
from pathlib import Path

import freezegun
import dateutil.tz

from tests.fs_utils import mkdirs
from urbasys.urbackup import retention


@freezegun.freeze_time("2022-12-18 14:00:00")
def test_delete_old_keep_all(tmp_path):
    dir_2022_12_18 = mkdirs(tmp_path / "bak1" / "daily-2022-12-18T01:23:45.123456Z")
    retention.delete_old(tmp_path / "bak1", dry_run=False, max_age=timedelta(days=1))
    assert dir_2022_12_18.is_dir()


@freezegun.freeze_time("2022-12-18 14:00:00")
def test_delete_old_delete_all(tmp_path):
    dir_2022_12_18 = mkdirs(tmp_path / "bak1" / "daily-2022-12-18T01:23:45.123456Z")
    retention.delete_old(tmp_path / "bak1", dry_run=False, max_age=timedelta(hours=1))
    assert not dir_2022_12_18.is_dir()


def test_folder_to_datetime():
    assert retention.folder_to_datetime(
        Path("daily-2019-06-13T02:02:40.603Z")
    ) == datetime(2019, 6, 13, 2, 2, 40, 603000, tzinfo=dateutil.tz.tzutc())
    assert retention.folder_to_datetime(
        Path("/urbackup/mirror/pi1.urbas.si/daily-2022-12-18T04:10:05.849554073Z")
    ) == datetime(2022, 12, 18, 4, 10, 5, 849554, tzinfo=dateutil.tz.tzutc())


def test_keep_last_empty():
    assert retention.keep_last({}, number_to_keep=30) == set()


def test_keep_last_all():
    old_backup = datetime(2019, 5, 13)
    new_backup = datetime(2019, 5, 14)
    assert retention.keep_last(
        {Path("old"): old_backup, Path("new"): new_backup}, number_to_keep=2
    ) == {
        Path("old"),
        Path("new"),
    }


def test_keep_last_some_outdated():
    old_backup = datetime(2019, 5, 13)
    new_backup = datetime(2019, 5, 14)
    assert retention.keep_last(
        {Path("old"): old_backup, Path("new"): new_backup}, number_to_keep=1
    ) == {Path("new")}


def test_oldest_each_month_empty():
    assert retention.oldest_each_month({}) == set()


def test_oldest_each_month_some_keep_oldest():
    assert retention.oldest_each_month(
        snapshots={
            Path("2019_5_1"): datetime(2019, 5, 1),
            Path("2019_5_2"): datetime(2019, 5, 2),
            Path("2019_4_10"): datetime(2019, 4, 10),
            Path("2019_4_22"): datetime(2019, 4, 22),
            Path("2019_1_1"): datetime(2019, 1, 1),
            Path("2019_2_2"): datetime(2019, 2, 2),
        }
    ) == {
        Path("2019_5_1"),
        Path("2019_4_10"),
        Path("2019_1_1"),
        Path("2019_2_2"),
    }
