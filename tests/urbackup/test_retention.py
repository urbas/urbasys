from datetime import datetime
from pathlib import Path

import dateutil.tz

from urbasys.urbackup import retention


def test_folder_to_datetime():
    assert retention.folder_to_datetime(
        Path("daily-2019-06-13T02:02:40.603Z")
    ) == datetime(2019, 6, 13, 2, 2, 40, 603000, tzinfo=dateutil.tz.tzutc())
    assert retention.folder_to_datetime(
        Path("/urbackup/mirror/pi1.urbas.si/daily-2022-12-18T04:10:05.849554073Z")
    ) == datetime(2022, 12, 18, 4, 10, 5, 849554, tzinfo=dateutil.tz.tzutc())


def test_keep_last_empty():
    assert retention.keep_last([], number_to_keep=30) == []


def test_keep_last_all():
    old_backup = datetime(2019, 5, 13)
    new_backup = datetime(2019, 5, 14)
    assert retention.keep_last([old_backup, new_backup], number_to_keep=2) == [
        new_backup,
        old_backup,
    ]


def test_keep_last_some_outdated():
    old_backup = datetime(2019, 5, 13)
    new_backup = datetime(2019, 5, 14)
    assert retention.keep_last([old_backup, new_backup], number_to_keep=1) == [
        new_backup
    ]


def test_monthlies_to_keep_empty():
    assert retention.monthlies_to_keep([]) == set()


def test_monthlies_to_keep_some_keep_oldest():
    assert retention.monthlies_to_keep(
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
    assert retention.backups_to_keep(backup_dates, keep_latest=4) == {
        datetime(2019, 5, 1),
        datetime(2019, 5, 2),
        datetime(2019, 4, 10),
        datetime(2019, 4, 22),
        datetime(2019, 1, 1),
        datetime(2018, 12, 16),
    }
    assert retention.backups_to_keep(backup_dates, keep_latest=2) == {
        datetime(2019, 5, 1),
        datetime(2019, 5, 2),
        datetime(2019, 4, 10),
        datetime(2019, 1, 1),
        datetime(2018, 12, 16),
    }
