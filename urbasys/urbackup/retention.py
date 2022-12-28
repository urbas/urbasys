import logging
from datetime import datetime, timedelta
from shutil import rmtree
from pathlib import Path
from typing import Dict, List, Set, Tuple

import dateutil.tz
from dateutil.parser import isoparse


def delete_old(
    backups_root_dir: Path, dry_run: bool, max_age: timedelta, min_keep: int = 0
) -> None:
    now = datetime.now(tz=dateutil.tz.tzutc())
    snapshots = get_parsed_snapshot_dirs(backups_root_dir)
    to_retain = keep_last(snapshots, min_keep)
    for snapshot_dir, timestamp in sorted(
        snapshots.items(),
        key=lambda path_and_timestamp: path_and_timestamp[1],
    ):
        if timestamp >= now - max_age or snapshot_dir in to_retain:
            continue
        if dry_run:
            logging.info("Would remove %s", snapshot_dir)
            continue
        logging.info("Removing %s...", snapshot_dir)
        rmtree(snapshot_dir)


def retain_monthlies(backups_root_dir: Path, dry_run: bool, keep_latest: int) -> None:
    snapshots = get_parsed_snapshot_dirs(backups_root_dir)
    monthlies = oldest_each_month(snapshots)
    dailies = keep_last(snapshots, number_to_keep=keep_latest)
    snapshots_to_remove = snapshots.keys() - monthlies - dailies
    for snapshot_to_remove in sorted(snapshots_to_remove):
        if dry_run:
            logging.info("Would remove %s", snapshot_to_remove)
            continue
        logging.info("Removing %s...", snapshot_to_remove)
        rmtree(snapshot_to_remove)


def get_parsed_snapshot_dirs(backups_root_dir: Path) -> Dict[Path, datetime]:
    snapshot_dirs = get_snaphot_dirs(backups_root_dir)
    return {
        snapshot_dir: folder_to_datetime(snapshot_dir) for snapshot_dir in snapshot_dirs
    }


def get_snaphot_dirs(backups_root_dir: Path) -> List[Path]:
    return [
        snapshot_dir
        for snapshot_dir in backups_root_dir.glob("daily-*Z")
        if snapshot_dir.is_dir()
    ]


def folder_to_datetime(path: Path) -> datetime:
    return isoparse(path.name[6:])


def keep_last(snapshots: Dict[Path, datetime], number_to_keep: int) -> Set[Path]:
    return {
        snapshot_dir
        for snapshot_dir, _ in sorted(
            snapshots.items(),
            reverse=True,
            key=lambda path_and_timestamp: path_and_timestamp[1],
        )[:number_to_keep]
    }


def oldest_each_month(snapshots: Dict[Path, datetime]) -> Set[Path]:
    month_buckets: Dict[datetime, Tuple[Path, datetime]] = {}
    for snapshot_dir, timestamp in snapshots.items():
        current_month = datetime(year=timestamp.year, month=timestamp.month, day=1)
        month_bucket = month_buckets.get(current_month)
        if month_bucket is None or timestamp < month_bucket[1]:
            month_buckets[current_month] = (snapshot_dir, timestamp)
    return set(snapshot_dir for snapshot_dir, _ in month_buckets.values())
