from datetime import datetime

from urbasys.urbackup.app import (
    folder_to_datetime,
    dailies_to_keep,
    monthlies_to_keep,
    backups_to_keep,
)


def test_folder_to_datetime():
    assert folder_to_datetime("daily-2019-06-13T02:02:40.603Z") == datetime(
        2019, 6, 13, 2, 2, 40, 603000
    )


def test_dailies_to_keep_empty():
    assert dailies_to_keep([], days_to_keep=30, current_date=datetime.now()) == []


def test_dailies_to_keep_some_outdated():
    now = datetime(2019, 6, 13)
    old_backup = datetime(2019, 5, 13)
    new_backup = datetime(2019, 5, 14)
    assert dailies_to_keep(
        [old_backup, new_backup], days_to_keep=30, current_date=now
    ) == [new_backup]


def test_dailies_to_keep_minimum():
    now = datetime(2019, 6, 13)
    oldest_backup = datetime(2019, 5, 12)
    old_backup = datetime(2019, 5, 13)
    new_backup = datetime(2019, 5, 14)
    assert dailies_to_keep(
        [oldest_backup, old_backup, new_backup],
        days_to_keep=30,
        current_date=now,
        minimum_backups=2,
    ) == [new_backup, old_backup]


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
    expected_to_keep = {
        datetime(2019, 5, 1),
        datetime(2019, 5, 2),
        datetime(2019, 4, 10),
        datetime(2019, 4, 22),
        datetime(2019, 1, 1),
        datetime(2018, 12, 16),
    }
    assert (
        backups_to_keep(
            all_backup_dates=backup_dates,
            days_to_keep_dailies=30,
            current_date=datetime(2019, 5, 3),
        )
        == expected_to_keep
    )
    assert (
        backups_to_keep(
            expected_to_keep, days_to_keep_dailies=30, current_date=datetime(2019, 5, 3)
        )
        == expected_to_keep
    )
