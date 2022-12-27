import logging
from datetime import datetime
from shutil import rmtree
from pathlib import Path
from typing import Dict, Iterable, List, Set

from dateutil.parser import isoparse


def retain_monthlies(backups_root_dir: Path, dry_run: bool, keep_latest: int) -> None:
    snapshot_dirs = [
        snapshot_dir
        for snapshot_dir in backups_root_dir.glob("daily-*Z")
        if snapshot_dir.is_dir()
    ]
    dates_2_snapshot_dirs = {
        folder_to_datetime(snapshot_dir): snapshot_dir for snapshot_dir in snapshot_dirs
    }
    all_dates = dates_2_snapshot_dirs.keys()
    dates_to_retain = backups_to_keep(all_dates, keep_latest)
    for date_to_remove in sorted(set(all_dates) - dates_to_retain):
        if dry_run:
            logging.info("Would remove %s", dates_2_snapshot_dirs[date_to_remove])
            continue
        logging.info("Removing %s...", dates_2_snapshot_dirs[date_to_remove])
        rmtree(dates_2_snapshot_dirs[date_to_remove])


def folder_to_datetime(path: Path) -> datetime:
    return isoparse(path.name[6:])


def keep_last(backup_dates: Iterable[datetime], number_to_keep: int) -> List[datetime]:
    return sorted(backup_dates, reverse=True)[:number_to_keep]


def monthlies_to_keep(backup_dates: Iterable[datetime]) -> Set[datetime]:
    month_buckets: Dict[datetime, datetime] = {}
    for cur_backup_date in backup_dates:
        current_month = datetime(
            year=cur_backup_date.year, month=cur_backup_date.month, day=1
        )
        existing_backup_date = month_buckets.get(current_month)
        if existing_backup_date is None or cur_backup_date < existing_backup_date:
            month_buckets[current_month] = cur_backup_date
    return set(month_buckets.values())


def backups_to_keep(
    snapshot_dates: Iterable[datetime], keep_latest: int
) -> Set[datetime]:
    last_dates = set(keep_last(snapshot_dates, keep_latest))
    monthlies = monthlies_to_keep(snapshot_dates)
    return last_dates.union(monthlies)